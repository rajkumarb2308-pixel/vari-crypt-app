import os
from argon2.low_level import hash_secret_raw, Type
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class CryptoEngine:
    def __init__(self):
        self.key_length = 32  # AES-256

    def derive_key(self, password: str, salt: bytes) -> bytes:
        return hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=self.key_length,
            type=Type.ID
        )

    def encrypt_data(self, plaintext: str, password: str):
        salt = get_random_bytes(16)
        key = self.derive_key(password, salt)

        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())

        return salt, cipher.nonce, tag, ciphertext

    def decrypt_data(self, salt, nonce, tag, ciphertext, password: str):
        try:
            key = self.derive_key(password, salt)
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted.decode()
        except ValueError:
            return "ERROR: Integrity Check Failed or Wrong Password."