"""Encryption support for profile values using Fernet symmetric encryption."""

import json
from pathlib import Path
from typing import Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None
    InvalidToken = Exception


class EncryptionError(Exception):
    pass


def get_key_path() -> Path:
    from envswitch.storage import get_profiles_path
    return get_profiles_path().parent / "encrypt.key"


def generate_key() -> bytes:
    if Fernet is None:
        raise EncryptionError("cryptography package is required: pip install cryptography")
    return Fernet.generate_key()


def save_key(key: bytes, path: Optional[Path] = None) -> None:
    path = path or get_key_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)
    path.chmod(0o600)


def load_key(path: Optional[Path] = None) -> bytes:
    path = path or get_key_path()
    if not path.exists():
        raise EncryptionError(f"No encryption key found at {path}. Run 'envswitch encrypt init' first.")
    return path.read_bytes()


def encrypt_value(value: str, key: bytes) -> str:
    if Fernet is None:
        raise EncryptionError("cryptography package is required")
    f = Fernet(key)
    return "enc:" + f.encrypt(value.encode()).decode()


def decrypt_value(value: str, key: bytes) -> str:
    if Fernet is None:
        raise EncryptionError("cryptography package is required")
    if not value.startswith("enc:"):
        return value
    f = Fernet(key)
    try:
        return f.decrypt(value[4:].encode()).decode()
    except Exception:
        raise EncryptionError(f"Failed to decrypt value. Check your encryption key.")


def is_encrypted(value: str) -> bool:
    return value.startswith("enc:")


def encrypt_profile(profile: dict, key: bytes, vars_to_encrypt: Optional[list] = None) -> dict:
    result = {}
    for k, v in profile.items():
        if vars_to_encrypt is None or k in vars_to_encrypt:
            result[k] = encrypt_value(v, key) if not is_encrypted(v) else v
        else:
            result[k] = v
    return result


def decrypt_profile(profile: dict, key: bytes) -> dict:
    return {k: decrypt_value(v, key) for k, v in profile.items()}
