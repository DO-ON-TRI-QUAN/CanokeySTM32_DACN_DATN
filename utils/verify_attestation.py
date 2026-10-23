#!/usr/bin/env python3
"""
Check the attestation of a CanoKey over FIDO2 (CTAP2), end to end.

It does what a website does when it asks for "direct" attestation:
  1. getInfo            -> read the AAGUID the firmware reports
  2. makeCredential     -> register a throw-away credential (needs a TOUCH)
  3. check the answer:
       a. format is "packed" and has a certificate (x5c)
       b. the attestation signature verifies with the certificate public key
       c. AAGUID in getInfo == AAGUID in authData == AAGUID in the certificate
       d. (optional, --ca) the certificate is signed by the given CA cert

Transport:
  --transport hid   USB FIDO HID. On Windows this needs an ADMINISTRATOR
                    terminal (Windows blocks raw FIDO access otherwise).
  --transport pcsc  CTAP over the CCID smart-card interface. No admin needed.
  --transport auto  (default) try hid, then pcsc.

Touch: makeCredential waits for user presence. On a NUCLEO board without a
touch sensor, send 'T' on the ST-LINK serial port (UART touch emulator), or use
a DUMB_DONGLE build.

Examples:
  python verify_attestation.py
  python verify_attestation.py --transport pcsc
  python verify_attestation.py --ca "CanoKey ... Attest CA.pem"
  python verify_attestation.py --fido-pin 1234    # only if a FIDO PIN is set

Needs: pip install fido2 cryptography pyscard
"""

import argparse
import hashlib
import os
import sys

try:
    from cryptography import x509
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
    from fido2.ctap import CtapError
    from fido2.ctap2 import Ctap2
except ImportError:
    sys.exit("Missing packages. Run: pip install fido2 cryptography pyscard")

AAGUID_OID = x509.ObjectIdentifier("1.3.6.1.4.1.45724.1.1.4")
results = []


def check(ok, label, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return ok


def fmt_uuid(b):
    h = bytes(b).hex()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def open_device(transport):
    errors = []
    if transport in ("auto", "hid"):
        try:
            from fido2.hid import CtapHidDevice
            dev = next(CtapHidDevice.list_devices(), None)
            if dev:
                print(f"Transport: HID ({dev})")
                return dev
            errors.append("hid: no FIDO HID device found (on Windows: run as Administrator)")
        except Exception as e:
            errors.append(f"hid: {e}")
    if transport in ("auto", "pcsc"):
        try:
            from fido2.pcsc import CtapPcscDevice
            dev = next(iter(CtapPcscDevice.list_devices()), None)
            if dev:
                print(f"Transport: PC/SC ({dev})")
                return dev
            errors.append("pcsc: no reader with a FIDO applet found")
        except Exception as e:
            errors.append(f"pcsc: {e}")
    sys.exit("No authenticator found.\n  " + "\n  ".join(errors))


def get_pin_param(ctap, pin, client_data_hash, rp_id):
    from fido2.ctap2.pin import ClientPin
    cp = ClientPin(ctap)
    token = cp.get_pin_token(pin, ClientPin.PERMISSION.MAKE_CREDENTIAL, rp_id)
    return cp.protocol.authenticate(token, client_data_hash), cp.protocol.VERSION


def verify_with(pub, sig, data):
    if isinstance(pub, ec.EllipticCurvePublicKey):
        pub.verify(sig, data, ec.ECDSA(hashes.SHA256()))
    elif isinstance(pub, rsa.RSAPublicKey):
        pub.verify(sig, data, padding.PKCS1v15(), hashes.SHA256())
    else:
        raise TypeError("unsupported key type")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transport", choices=["auto", "hid", "pcsc"], default="auto")
    ap.add_argument("--ca", help="CA certificate (PEM) to check the chain against")
    ap.add_argument("--fido-pin", help="FIDO2 PIN, only if one is set on the device")
    ap.add_argument("--save-cert", help="write the attestation cert (PEM) to this file")
    args = ap.parse_args()

    ctap = Ctap2(open_device(args.transport))

    # 1. getInfo
    info = ctap.get_info()
    info_aaguid = bytes(info.aaguid)
    print(f"getInfo versions : {info.versions}")
    print(f"getInfo AAGUID   : {fmt_uuid(info_aaguid)}")
    print(f"clientPin set    : {info.options.get('clientPin')}")

    # 2. makeCredential
    rp = {"id": "attestation-test.local", "name": "Attestation test"}
    user = {"id": os.urandom(16), "name": "tester"}
    cdh = hashlib.sha256(os.urandom(32)).digest()      # stands in for clientDataHash
    pin_param = pin_proto = None
    if args.fido_pin:
        pin_param, pin_proto = get_pin_param(ctap, args.fido_pin, cdh, rp["id"])
    print("\n>>> TOUCH the key now (or send 'T' on the ST-LINK serial port) <<<\n")
    try:
        att = ctap.make_credential(cdh, rp, user, [{"type": "public-key", "alg": -7}],
                                   pin_uv_param=pin_param, pin_uv_protocol=pin_proto)
    except CtapError as e:
        hint = ""
        if e.code == CtapError.ERR.PIN_REQUIRED:
            hint = " -> a FIDO PIN is set: re-run with --fido-pin <PIN>"
        elif e.code in (CtapError.ERR.USER_ACTION_TIMEOUT, CtapError.ERR.KEEPALIVE_CANCEL):
            hint = " -> no touch within the timeout"
        sys.exit(f"makeCredential failed: {e}{hint}")

    auth_data = att.auth_data
    stmt = att.att_stmt
    print(f"attestation fmt  : {att.fmt}")

    # 3a. packed + x5c
    if not check(att.fmt == "packed", "format is packed", att.fmt):
        sys.exit(1)
    if not check("x5c" in stmt and len(stmt["x5c"]) > 0, "attestation has a certificate (x5c)",
                 "self attestation - no attestation key/cert installed?" if "x5c" not in stmt else ""):
        sys.exit(1)
    cert = x509.load_der_x509_certificate(bytes(stmt["x5c"][0]))
    print(f"       subject : {cert.subject.rfc4514_string()}")
    print(f"       issuer  : {cert.issuer.rfc4514_string()}")
    print(f"       valid   : {cert.not_valid_before_utc:%Y-%m-%d} to {cert.not_valid_after_utc:%Y-%m-%d}")
    if args.save_cert:
        with open(args.save_cert, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        print(f"       saved   : {args.save_cert}")

    # 3b. signature
    check(stmt.get("alg") == -7, "alg is ES256 (-7)", str(stmt.get("alg")))
    try:
        verify_with(cert.public_key(), bytes(stmt["sig"]), bytes(auth_data) + cdh)
        check(True, "attestation signature verifies with the cert public key")
    except InvalidSignature:
        check(False, "attestation signature verifies with the cert public key",
              "private key on the device does not match the certificate")

    # 3c. AAGUID in three places
    ad_aaguid = bytes(auth_data.credential_data.aaguid)
    try:
        der = cert.extensions.get_extension_for_oid(AAGUID_OID).value.value
        cert_aaguid = der[2:] if der[:2] == b"\x04\x10" and len(der) == 18 else None
    except x509.ExtensionNotFound:
        cert_aaguid = None
    print(f"AAGUID authData  : {fmt_uuid(ad_aaguid)}")
    print(f"AAGUID cert      : {fmt_uuid(cert_aaguid) if cert_aaguid else 'MISSING'}")
    check(ad_aaguid == info_aaguid, "AAGUID authData == getInfo")
    check(cert_aaguid == ad_aaguid, "AAGUID certificate == authData",
          "" if cert_aaguid == ad_aaguid else "firmware ctap.c and cert .cnf disagree")
    try:
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
        check(not bc.ca, "certificate is not a CA (basicConstraints CA:FALSE)")
    except x509.ExtensionNotFound:
        check(False, "certificate has basicConstraints")
    check(cert.version == x509.Version.v3, "certificate is X.509 v3")

    # 3d. chain
    if args.ca:
        ca = x509.load_pem_x509_certificate(open(args.ca, "rb").read())
        try:
            verify_with(ca.public_key(), cert.signature, cert.tbs_certificate_bytes)
            check(cert.issuer == ca.subject, "certificate is signed by the given CA",
                  ca.subject.rfc4514_string())
        except (InvalidSignature, TypeError):
            check(False, "certificate is signed by the given CA", "signature does not verify")

    print(f"\n{sum(results)}/{len(results)} checks passed.")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
