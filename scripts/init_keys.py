#!/usr/bin/env python3
"""Create or re-protect the dashboard's encryption keys.

First-time setup (creates a new RSA key pair; any already-encrypted editions
would become unreadable, so only do this once):

    python3 scripts/init_keys.py --user joearmitage --passphrase 'SECRET'

Change the sign-in credentials (keeps the key pair, so every edition stays
readable):

    python3 scripts/init_keys.py --rotate --user OLDUSER --passphrase 'OLD' \
        --new-user NEWUSER --new-passphrase 'NEW'

Outputs:
    site/keys/public.spki   public key (safe to commit; the routine encrypts with it)
    site/keys/private.enc   private key, encrypted with the sign-in credentials

There is no recovery if the credentials are lost: the private key only exists
inside private.enc.
"""
import argparse
import getpass

import pdb_crypto as pc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", required=True, help="sign-in user ID (case-insensitive)")
    ap.add_argument("--passphrase", help="sign-in passphrase (prompted if omitted)")
    ap.add_argument("--rotate", action="store_true", help="re-protect the existing private key with new credentials")
    ap.add_argument("--new-user", help="with --rotate: the new user ID (defaults to --user)")
    ap.add_argument("--new-passphrase", help="with --rotate: the new passphrase (prompted if omitted)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing key pair (editions encrypted to it become unreadable)")
    args = ap.parse_args()

    passphrase = args.passphrase if args.passphrase is not None else getpass.getpass("Passphrase: ")

    if args.rotate:
        private_key = pc.read_private_key(args.user, passphrase)
        new_user = args.new_user or args.user
        new_pass = args.new_passphrase if args.new_passphrase is not None else getpass.getpass("New passphrase: ")
        pc.write_private_key(private_key, new_user, new_pass)
        print(f"Re-protected {pc.PRIVATE} for user '{new_user}'. Key pair unchanged.")
        return

    if pc.PRIVATE.exists() and not args.force:
        raise SystemExit(f"{pc.PRIVATE} already exists. Use --rotate to change credentials, or --force to start over.")
    pc.generate_keypair(args.user, passphrase)
    print(f"Wrote {pc.PUBLIC} and {pc.PRIVATE} for user '{args.user}'.")


if __name__ == "__main__":
    main()
