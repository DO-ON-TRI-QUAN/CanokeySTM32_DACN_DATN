#!/usr/bin/env python3
"""
Windows replacement for the scriptor-based provisioning in
canokey-stm32/utils/device-config-init.sh  (TEST DEVICE version)

What it does:
  1. select the admin applet
  2. show the admin PIN retry counter, then verify the admin PIN
  3. (only with --nfc) send the NFC chip config lines
  4. set the device serial number - skipped if the device already has one
  5. write the attestation private key
  6. write the attestation certificate
  7. read back the serial number

Before it touches the device, it checks that the private key and the
certificate belong together (same public key). A mismatched pair makes every
attestation signature fail, so the script refuses it.

Modes:
  demo   (default) use the demo key/cert found inside device-config-init.sh
         (the file must sit in the same folder as this script)
  files  use your own key/cert: --key dev.key (PEM) --cert dev.der (DER)

Examples (run from the utils folder with the venv active):
  python provision_attestation.py --list
  python provision_attestation.py --dry-run          # checks only, no device
  python provision_attestation.py
  python provision_attestation.py --reader canokey --pin 123456
  python provision_attestation.py --mode files --key dev.key --cert dev.der

Changes from the original version:
  - serial already set (SW 6985) no longer stops the run; the script reads the
    serial first and skips the write when one exists
  - key/cert pair is checked before anything is written
  - --serial option; in files mode the default serial comes from the cert CN
  - --pin option; the retry counter is shown before the PIN is tried
  - NFC config lines are skipped unless --nfc is given (NUCLEO has no NFC chip)
"""

import argparse
import re
import sys
import time
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
except ImportError:
    sys.exit("cryptography is not installed. Run: pip install -r requirements.txt")

SELECT_ADMIN = "00A4040005F000000000"
VERIFY_STATUS = "00200000"            # VERIFY with no data -> retry counter
READ_SN = "0032000004"
NFC_CONFIG = [
    "00FF01010903B005720300B39900",
    "00FF010103039100",
    "00FF01010603A044000420",
]
AAGUID_OID = x509.ObjectIdentifier("1.3.6.1.4.1.45724.1.1.4")
SW_TEXT = {
    0x9000: "OK",
    0x6700: "wrong length",
    0x6900: "unable to process (firmware/filesystem error)",
    0x6982: "PIN not verified",
    0x6983: "PIN blocked",
    0x6985: "conditions not satisfied",
    0x6A80: "wrong data",
    0x6A86: "wrong P1/P2",
    0x6D00: "instruction not supported",
    0x6F00: "checking error",
}


# ---------------------------------------------------------------- APDU helpers

def sw_text(sw):
    if sw & 0xFFF0 == 0x63C0:
        return f"wrong PIN, {sw & 0xF} tries left"
    return SW_TEXT.get(sw, "unknown status")


def transmit(conn, apdu_hex):
    """Send one APDU. Return (data_bytes, sw) or exit on a transport error."""
    from smartcard.Exceptions import CardConnectionException
    apdu = list(bytes.fromhex(apdu_hex.replace(" ", "")))
    try:
        data, sw1, sw2 = conn.transmit(apdu)
    except CardConnectionException as e:
        print(f"[FAIL] transmit error: {e}")
        print("Hint: long APDUs (the certificate write) can fail through the "
              "Windows CCID driver. Note the exact error.")
        sys.exit(1)
    return bytes(data), (sw1 << 8) | sw2


def send(conn, apdu_hex, label, required=True):
    """Send one APDU and print the result. Exit on failure if required."""
    data, sw = transmit(conn, apdu_hex)
    ok = sw == 0x9000
    tag = "OK  " if ok else ("FAIL" if required else "WARN")
    print(f"[{tag}] {label}: SW={sw:04X} ({sw_text(sw)})")
    if not ok and required:
        sys.exit(1)
    return data, sw


# ------------------------------------------------------- key / cert handling

def load_demo(sh_path):
    """Read the demo key and cert out of device-config-init.sh.
    Returns (priv 32 bytes, cert DER bytes)."""
    if not sh_path.exists():
        sys.exit(f"Cannot find {sh_path}. Keep this script in the utils folder.")
    text = sh_path.read_text(errors="ignore")
    key = re.search(r'DEMO_ATTEST_KEY="([0-9a-fA-F ]+)"', text)
    cert = re.search(r'DEMO_ATTEST_CERT="([0-9a-fA-F ]+)"', text)
    if not key or not cert:
        sys.exit(f"Could not find DEMO_ATTEST_KEY / DEMO_ATTEST_CERT in {sh_path.name}.")
    key_apdu = bytes.fromhex(key.group(1).replace(" ", ""))
    cert_apdu = bytes.fromhex(cert.group(1).replace(" ", ""))
    # key APDU  = 00 01 00 00 20 | 32-byte key
    # cert APDU = 00 02 00 00 00 LL LL | DER cert   (extended length)
    if key_apdu[:5] != bytes.fromhex("0001000020") or len(key_apdu) != 37:
        sys.exit("Demo key APDU has an unexpected format.")
    if cert_apdu[:5] != bytes.fromhex("0002000000"):
        sys.exit("Demo cert APDU has an unexpected format.")
    cert_len = int.from_bytes(cert_apdu[5:7], "big")
    cert_der = cert_apdu[7:]
    if len(cert_der) != cert_len:
        sys.exit(f"Demo cert length field says {cert_len} bytes, found {len(cert_der)}.")
    return key_apdu[5:], cert_der


def load_files(key_path, cert_path):
    """Read a PEM private key and a DER cert. Returns (priv 32 bytes, cert DER)."""
    key = serialization.load_pem_private_key(Path(key_path).read_bytes(), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey) or key.curve.name != "secp256r1":
        sys.exit("The key must be an EC key on curve secp256r1 (P-256).")
    priv = key.private_numbers().private_value.to_bytes(32, "big")
    cert = Path(cert_path).read_bytes()
    if not cert or cert[0] != 0x30:
        sys.exit("The cert does not look like DER (expected first byte 0x30). "
                 "Convert it with: openssl x509 -outform der -in dev.pem -out dev.der")
    return priv, cert


def check_pair(priv, cert_der):
    """Check that the key and cert belong together. Return the parsed cert."""
    cert = x509.load_der_x509_certificate(cert_der)
    cert_pub = cert.public_key()
    if not isinstance(cert_pub, ec.EllipticCurvePublicKey) or cert_pub.curve.name != "secp256r1":
        sys.exit("The certificate public key is not EC P-256.")
    key = ec.derive_private_key(int.from_bytes(priv, "big"), ec.SECP256R1())
    raw = serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    if key.public_key().public_bytes(*raw) != cert_pub.public_bytes(*raw):
        sys.exit("[FAIL] The private key does NOT match the certificate public key.\n"
                 "       They come from different runs. Regenerate them together.")
    print("[OK  ] key matches certificate public key")
    return cert


def cert_aaguid(cert):
    """Return the 16-byte AAGUID from the cert extension, or None."""
    try:
        ext = cert.extensions.get_extension_for_oid(AAGUID_OID)
    except x509.ExtensionNotFound:
        return None
    der = ext.value.value          # OCTET STRING: 04 10 <16 bytes>
    if len(der) == 18 and der[:2] == b"\x04\x10":
        return der[2:]
    return None


def fmt_uuid(b):
    h = b.hex()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def serial_from_cert(cert):
    cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    if cn:
        m = re.search(r"Serial\s+([0-9a-fA-F]{8})\b", cn[0].value)
        if m:
            return m.group(1).lower()
    return None


# ------------------------------------------------------------------- readers

def pick_reader(all_readers, wanted):
    if not all_readers:
        sys.exit("No smart card readers found. Check that the token's USB side "
                 "is plugged in, the firmware is flashed, and the Windows "
                 "'Smart Card' service is running.")
    if wanted is not None:
        if wanted.isdigit() and int(wanted) < len(all_readers):
            return all_readers[int(wanted)]
        for r in all_readers:
            if wanted.lower() in str(r).lower():
                return r
        sys.exit(f"No reader matches '{wanted}'. Use --list to see readers.")
    for r in all_readers:
        if "canokey" in str(r).lower():
            return r
    if len(all_readers) == 1:
        return all_readers[0]
    print("Several readers found and none looks like a CanoKey:")
    for i, r in enumerate(all_readers):
        print(f"  [{i}] {r}")
    sys.exit("Pick one with --reader <index or name part>.")


def connect(reader):
    from smartcard.CardConnection import CardConnection
    conn = reader.createConnection()
    try:
        conn.connect(CardConnection.T1_protocol)
    except Exception:
        conn.connect()
    print("ATR:", bytes(conn.getATR()).hex(" ").upper())
    return conn


# ---------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list readers and exit")
    ap.add_argument("--reader", help="reader index or part of its name")
    ap.add_argument("--mode", choices=["demo", "files"], default="demo")
    ap.add_argument("--key", help="PEM private key (files mode)")
    ap.add_argument("--cert", help="DER certificate (files mode)")
    ap.add_argument("--pin", default="123456", help="admin PIN (default 123456)")
    ap.add_argument("--serial", help="8 hex digits. Default: from cert CN in files "
                                     "mode, current Unix time in demo mode")
    ap.add_argument("--nfc", action="store_true",
                    help="also send the NFC chip config lines (boards with FM11 NFC chip only)")
    ap.add_argument("--dry-run", action="store_true",
                    help="run all checks and print the APDUs, but do not touch the device")
    args = ap.parse_args()

    if args.list:
        from smartcard.System import readers
        all_readers = readers()
        if not all_readers:
            print("No readers found.")
        for i, r in enumerate(all_readers):
            print(f"[{i}] {r}")
        return

    # 1. load and check key + cert (no device needed)
    if args.mode == "demo":
        priv, cert_der = load_demo(Path(__file__).resolve().with_name("device-config-init.sh"))
    else:
        if not args.key or not args.cert:
            sys.exit("--mode files needs both --key and --cert")
        priv, cert_der = load_files(args.key, args.cert)
    cert = check_pair(priv, cert_der)
    aaguid = cert_aaguid(cert)
    print(f"       subject : {cert.subject.rfc4514_string()}")
    print(f"       issuer  : {cert.issuer.rfc4514_string()}")
    print(f"       AAGUID  : {fmt_uuid(aaguid) if aaguid else 'MISSING - cert has no AAGUID extension'}")
    print(f"       size    : {len(cert_der)} bytes")
    if len(cert_der) > 0xFFFF:
        sys.exit("Certificate too large for one APDU.")

    # 2. choose the serial
    if args.serial:
        serial = args.serial.lower()
    elif args.mode == "files" and serial_from_cert(cert):
        serial = serial_from_cert(cert)
    else:
        serial = f"{int(time.time()):08x}"
    if not re.fullmatch(r"[0-9a-f]{8}", serial):
        sys.exit(f"Serial must be exactly 8 hex digits, got '{serial}'.")

    pin = args.pin.encode("ascii")
    if not 1 <= len(pin) <= 255:
        sys.exit("Admin PIN must be 1 to 255 characters.")
    verify_apdu = f"00200000{len(pin):02X}{pin.hex()}"
    key_apdu = "0001000020" + priv.hex()
    cert_apdu = "0002000000" + f"{len(cert_der):04X}" + cert_der.hex()

    if args.dry_run:
        print("\n--dry-run: these APDUs would be sent (key and PIN hidden):")
        print(" ", SELECT_ADMIN)
        print(f"  00200000{len(pin):02X}<PIN>")
        if args.nfc:
            for line in NFC_CONFIG:
                print(" ", line)
        print(f"  0030000004{serial}   (only if the device has no serial yet)")
        print("  0001000020<32-byte private key>")
        print(f"  0002000000{len(cert_der):04X}<{len(cert_der)}-byte certificate>")
        return

    # 3. talk to the device
    from smartcard.System import readers
    reader = pick_reader(readers(), args.reader)
    print("Using reader:", reader)
    conn = connect(reader)

    send(conn, SELECT_ADMIN, "select admin applet")

    _, sw = transmit(conn, VERIFY_STATUS)
    if sw & 0xFFF0 == 0x63C0:
        print(f"[INFO] admin PIN tries left: {sw & 0xF}")
        if sw & 0xF == 0:
            sys.exit("[FAIL] admin PIN is blocked. Only a full flash erase recovers it.")
    send(conn, verify_apdu, "verify admin PIN")

    if args.nfc:
        for i, line in enumerate(NFC_CONFIG, 1):
            send(conn, line, f"NFC config {i}", required=False)
    else:
        print("[SKIP] NFC config (use --nfc on boards with the NFC chip)")

    data, sw = send(conn, READ_SN, "read current serial", required=False)
    current = data.hex() if sw == 0x9000 and len(data) == 4 else None
    if current and current != "00000000":
        print(f"[SKIP] serial already set to {current}; the firmware allows it only once")
        if current != serial and args.mode == "files":
            print(f"[WARN] cert CN serial {serial} differs from device serial {current}")
    else:
        _, sw = send(conn, "0030000004" + serial, f"set serial {serial}", required=False)
        if sw not in (0x9000, 0x6985):
            sys.exit(1)

    send(conn, key_apdu, "write attestation key")
    send(conn, cert_apdu, "write attestation certificate")

    data, sw = send(conn, READ_SN, "read back serial", required=False)
    if sw == 0x9000:
        print(f"       device serial: {data.hex()}")
    try:
        conn.disconnect()
    except Exception:
        pass
    print("Done. Next: run verify_attestation.py to check the result over FIDO2.")


if __name__ == "__main__":
    main()
