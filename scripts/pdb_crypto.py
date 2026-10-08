#!/usr/bin/env python3
"""Encryption for the dashboard archive.

Design
------
* Each published file (PDF, brief JSON, the archive index) is encrypted with a
  fresh random AES-256-GCM key.
* That file key is wrapped with the site's RSA-OAEP(SHA-256) public key,
  which lives in plaintext at site/keys/public.spki. Anyone (the daily routine
  included) can publish with only the public key.
* The RSA private key lives at site/keys/private.enc, encrypted with
  AES-256-GCM under a key derived from the user ID + passphrase with
  PBKDF2-SHA256. Only a correct sign-in in the browser can open it.

Container format for an encrypted file (binary):
    magic   b"PDBE1"               5 bytes
    klen    big-endian uint16      length of the wrapped key
    wrapped                        RSA-OAEP wrapped AES key
    iv      12 bytes               AES-GCM nonce
    ct      rest                   AES-GCM ciphertext + 16-byte tag

Everything here mirrors what site/index.html does with WebCrypto.
"""
import base64
import json
import os
import pathlib
import struct

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
KEYS = SITE / "keys"
PUBLIC = KEYS / "public.spki"
PRIVATE = KEYS / "private.enc"
MAGIC = b"PDBE1"
PBKDF2_ITERATIONS = 600_000


def _b64(b):
    return base64.b64encode(b).decode("ascii")


def _unb64(s):
    return base64.b64decode(s)


def credential_key(user_id, passphrase, salt, iterations=PBKDF2_ITERATIONS):
    """Derive the 256-bit key that protects the private key. User ID is case-insensitive."""
    material = (user_id.strip().lower() + ":" + passphrase).encode("utf-8")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(material)


def load_public_key():
    if not PUBLIC.exists():
        raise SystemExit(f"no public key at {PUBLIC}; run scripts/init_keys.py first")
    der = _unb64(PUBLIC.read_text().strip())
    return serialization.load_der_public_key(der)


def encrypt_bytes(data, public_key):
    file_key = AESGCM.generate_key(bit_length=256)
    iv = os.urandom(12)
    ct = AESGCM(file_key).encrypt(iv, data, None)
    wrapped = public_key.encrypt(
        file_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    return MAGIC + struct.pack(">H", len(wrapped)) + wrapped + iv + ct


def encrypt_file(src, dst, public_key):
    dst = pathlib.Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(encrypt_bytes(pathlib.Path(src).read_bytes(), public_key))
    return dst


def decrypt_bytes(blob, private_key):
    """Used only for local verification; the browser does this with WebCrypto."""
    if not blob.startswith(MAGIC):
        raise ValueError("not a PDBE1 container")
    (klen,) = struct.unpack(">H", blob[5:7])
    wrapped = blob[7:7 + klen]
    iv = blob[7 + klen:7 + klen + 12]
    ct = blob[7 + klen + 12:]
    file_key = private_key.decrypt(
        wrapped,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    return AESGCM(file_key).decrypt(iv, ct, None)


def write_private_key(private_key, user_id, passphrase):
    pkcs8 = private_key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = credential_key(user_id, passphrase, salt)
    ct = AESGCM(key).encrypt(iv, pkcs8, None)
    KEYS.mkdir(parents=True, exist_ok=True)
    PRIVATE.write_text(json.dumps({
        "v": 1,
        "kdf": "PBKDF2-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": _b64(salt),
        "iv": _b64(iv),
        "ct": _b64(ct),
    }, indent=1))


def read_private_key(user_id, passphrase):
    if not PRIVATE.exists():
        raise SystemExit(f"no private key at {PRIVATE}")
    blob = json.loads(PRIVATE.read_text())
    key = credential_key(user_id, passphrase, _unb64(blob["salt"]), int(blob["iterations"]))
    try:
        pkcs8 = AESGCM(key).decrypt(_unb64(blob["iv"]), _unb64(blob["ct"]), None)
    except Exception:
        raise SystemExit("wrong user ID or passphrase")
    return serialization.load_der_private_key(pkcs8, password=None)


def generate_keypair(user_id, passphrase):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    KEYS.mkdir(parents=True, exist_ok=True)
    spki = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    PUBLIC.write_text(_b64(spki) + "\n")
    write_private_key(private_key, user_id, passphrase)
    return private_key
