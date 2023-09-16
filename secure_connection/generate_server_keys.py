#!/usr/bin/env python3
"""generate_server_keys.py
----------------

This module contains utilities for generating and storing server keys and
certificates for the Pylandia Secure Email Initiative. It utilizes the
`cryptography` library to create a private key and a self-signed certificate,
which are then saved to specified paths.

Functions:
    - parse_args() -> Namespace: Parses the command line arguments.
    - generate_key_pair(storage_path: Path): Generates a key pair and a
      certificate and writes them to the specified storage path.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def parse_args() -> Namespace:
    """Parses the command line arguments for the script.

    Returns:
        Namespace: A namespace object that holds the command line arguments as
                   attributes.
    """
    parser = ArgumentParser(description="Pylandia Server Key Generator")

    parser.add_argument(
        "-p",
        "--path",
        default="server_keys",
        help="Path to save private and public keys",
    )

    return parser.parse_args()


def generate_key_pair(storage_path: Path):
    """Generates a private key and a self-signed certificate and saves them to
    the specified storage path.

    Args:
        storage_path (Path): The directory where the private key and certificate
                             files should be saved.

    Returns:
        None
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend()
    )

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "PY"),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, "Central Province"
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Pylandia City"),
            x509.NameAttribute(
                NameOID.ORGANIZATION_NAME, "Pylandia Secure Email Initiative"
            ),
            x509.NameAttribute(NameOID.COMMON_NAME, "securemail.pylandia"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    if not storage_path.exists():
        storage_path.mkdir(parents=True)

    publickey_path = storage_path / "cert.pem"
    with publickey_path.open("wb") as file:
        file.write(cert.public_bytes(serialization.Encoding.PEM))

    privatekey_path = storage_path / "key.pem"
    with privatekey_path.open("wb") as file:
        file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


if __name__ == "__main__":
    args = parse_args()
    storage = args.path
    full_storage_path = Path(storage)
    generate_key_pair(full_storage_path)
