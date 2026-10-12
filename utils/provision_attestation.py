#!/usr/bin/env python3
"""
Windows replacement for the scriptor-based provisioning in
canokey-stm32/utils/device-config-init.sh

What it does (same order as the shell script):
  1. select the admin applet
  2. verify the default admin PIN (123456)
  3. send the NFC config lines (tolerated to fail on boards without the NFC chip)
  4. set the device serial number (current Unix time)
  5. write the attestation private key
  6. write the attestation certificate

Modes:
  demo   (default) use the demo key/cert found inside device-config-init.sh
         (the file must sit in the same folder as this script)
  files  use your own key/cert: --key dev.key (PEM) --cert dev.der (DER)

Examples (run from the utils folder with the venv active):
  python provision_attestation.py --list
  python provision_attestation.py
  python provision_attestation.py --mode files --key dev.key --cert dev.der
  python provision_attestation.py --reader canokey
"""

import argparse
import re
import sys
import time
from pathlib import Path

try:
    from smartcard.System import readers
    from smartcard.CardConnection import CardConnection
    from smartcard.Exceptions import CardConnectionException
except ImportError:
    sys.exit("pyscard is not installed. Activate the venv, then run: "
             "pip install -r requirements.txt")

SELECT_ADMIN = "00A4040005F000000000"
VERIFY_PIN = "0020000006313233343536"  # default admin PIN 123456
NFC_CONFIG = [
    "00FF01010903B005720300B39900",
    "00FF010103039100",
    "00FF01010603A044000420",
]


def send(conn, apdu_hex, label, required=True):
    """Send one APDU given as a hex string. Exit on failure if required."""
    apdu = list(bytes.fromhex(apdu_hex.replace(" ", "")))
    try:
        _, sw1, sw2 = conn.transmit(apdu)
    except CardConnectionException as e:
        print(f"[FAIL] {label}: transmit error: {e}")
        if required:
            print("Hint: long APDUs (the certificate write) can fail through "
                  "the Windows CCID driver. Note the exact error and ask the "
                  "instructor or the master's student.")
            sys.exit(1)
        return None
    sw = (sw1 << 8) | sw2
    ok = sw == 0x9000
    tag = "OK  " if ok else ("FAIL" if required else "WARN")
    print(f"[{tag}] {label}: SW={sw:04X}")
    if not ok and required:
        sys.exit(1)
    return sw


def load_demo(sh_path):
    """Read the demo key and cert APDUs out of device-config-init.sh."""
    if not sh_path.exists():
        sys.exit(f"Cannot find {sh_path}. Keep this script in the utils folder.")
    text = sh_path.read_text(errors="ignore")
    key = re.search(r'DEMO_ATTEST_KEY="([0-9a-fA-F ]+)"', text)
    cert = re.search(r'DEMO_ATTEST_CERT="([0-9a-fA-F ]+)"', text)
    if not key or not cert:
        sys.exit("Could not find DEMO_ATTEST_KEY / DEMO_ATTEST_CERT in "
                 f"{sh_path.name}.")
    return key.group(1), cert.group(1)


def load_files(key_path, cert_path):
    """Build the key and cert APDUs from a PEM private key and a DER cert."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec
    except ImportError:
        sys.exit("cryptography is not installed. Run: pip install -r requirements.txt")

    key = serialization.load_pem_private_key(Path(key_path).read_bytes(),
                                             password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey) or \
            key.curve.name != "secp256r1":
        sys.exit("The key must be an EC key on curve secp256r1 (P-256).")
    priv = key.private_numbers().private_value.to_bytes(32, "big")

    cert = Path(cert_path).read_bytes()
    if not cert or cert[0] != 0x30:
        sys.exit("The cert does not look like DER (expected first byte 0x30). "
                 "Convert it with: openssl x509 -outform der -in dev.pem -out dev.der")

    key_apdu = "0001000020" + priv.hex()
    cert_apdu = "0002000000" + f"{len(cert):04x}" + cert.hex()
    return key_apdu, cert_apdu


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
    conn = reader.createConnection()
    try:
        conn.connect(CardConnection.T1_protocol)
    except Exception:
        conn.connect()
    print("ATR:", bytes(conn.getATR()).hex(" ").upper())
    return conn


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list readers and exit")
    ap.add_argument("--reader", help="reader index or part of its name")
    ap.add_argument("--mode", choices=["demo", "files"], default="demo")
    ap.add_argument("--key", help="PEM private key (files mode)")
    ap.add_argument("--cert", help="DER certificate (files mode)")
    args = ap.parse_args()

    all_readers = readers()
    if args.list:
        if not all_readers:
            print("No readers found.")
        for i, r in enumerate(all_readers):
            print(f"[{i}] {r}")
        return

    if args.mode == "demo":
        key_apdu, cert_apdu = load_demo(Path(__file__).with_name("device-config-init.sh"))
    else:
        if not args.key or not args.cert:
            sys.exit("--mode files needs both --key and --cert")
        key_apdu, cert_apdu = load_files(args.key, args.cert)

    reader = pick_reader(all_readers, args.reader)
    print("Using reader:", reader)
    conn = connect(reader)

    serial = f"{int(time.time()):08x}"

    send(conn, SELECT_ADMIN, "select admin applet")
    send(conn, VERIFY_PIN, "verify admin PIN")
    for i, line in enumerate(NFC_CONFIG, 1):
        send(conn, line, f"NFC config {i} (ok to fail without NFC chip)", required=False)
    send(conn, "0030000004" + serial, f"set serial {serial}")
    send(conn, key_apdu, "write attestation key")
    send(conn, cert_apdu, "write attestation certificate")
    print("Done.")


if __name__ == "__main__":
    main()
