import pytest
from leadforge.crypto import encrypt, decrypt


def test_encrypt_decrypt_roundtrip():
    plaintext = "sk-instantly-secret-key-12345"
    ciphertext = encrypt(plaintext)
    assert ciphertext != plaintext
    assert decrypt(ciphertext) == plaintext


def test_encrypt_produces_different_outputs():
    # AES-GCM with random IV so same input produces different ciphertext
    plaintext = "same-key"
    assert encrypt(plaintext) != encrypt(plaintext)


def test_decrypt_wrong_key_raises():
    ciphertext = encrypt("secret")
    # Tamper with ciphertext
    tampered = ciphertext[:-4] + "xxxx"
    with pytest.raises(Exception):
        decrypt(tampered)
