"""Password hashing helpers (bcrypt + legacy pbkdf2_sha256)."""

from __future__ import annotations

import hashlib
import hmac

import bcrypt


def hash_password(plain_password: str) -> str:
    pw = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    # Legacy dump (phpMyAdmin) uses Django-like pbkdf2_sha256 hashes:
    # pbkdf2_sha256$<iterations>$<salt>$<hex_digest>
    if password_hash.startswith("pbkdf2_sha256$"):
        try:
            _algo, iterations_str, salt, digest_hex = password_hash.split("$", 3)
            iterations = int(iterations_str)
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            ).hex()
            return hmac.compare_digest(derived, digest_hex)
        except Exception:
            return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False
