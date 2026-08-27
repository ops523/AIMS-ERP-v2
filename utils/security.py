from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)


_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Securely hash a plaintext password using Argon2id.

    Returns:
        str: Argon2 password hash.
    """

    if not isinstance(password, str):
        raise TypeError("Password must be a string.")

    if not password:
        raise ValueError("Password cannot be empty.")

    return _password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plaintext password against an Argon2 password hash.

    Returns:
        bool: True when the password matches, otherwise False.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(password_hash, str):
        return False

    if not password_hash:
        return False

    try:
        return _password_hasher.verify(
            password_hash,
            password,
        )

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False
