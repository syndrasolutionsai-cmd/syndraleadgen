import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from leadforge.config import settings


def _get_key() -> bytes:
    """Decode the base64-encoded 32-byte AES key from settings."""
    # Pad to ensure valid base64 length
    key_str = settings.encryption_key
    padding = 4 - len(key_str) % 4
    if padding != 4:
        key_str += "=" * padding
    return base64.b64decode(key_str)


def encrypt(plaintext: str) -> str:
    """Encrypt plaintext with AES-256-GCM. Returns base64-encoded nonce+ciphertext."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(token: str) -> str:
    """Decrypt a base64-encoded nonce+ciphertext string."""
    key = _get_key()
    aesgcm = AESGCM(key)
    data = base64.b64decode(token)
    nonce, ciphertext = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
