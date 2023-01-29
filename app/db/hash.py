from cryptography.fernet import Fernet
from app.config import SECRET_KEY_HASH

secret_key = SECRET_KEY_HASH


class Hash:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.fernet = Fernet(secret_key)

    def encrypt_password(self, plain_password: str) -> bytes:
        if not plain_password:
            raise ValueError("plain_password can not be empty or None")
        return self.fernet.encrypt(plain_password.encode())

    def verify_password(self, hashed_password: bytes, plain_password: str) -> bool:
        if not (hashed_password and plain_password):
            raise ValueError("encrypted_password and plain_password can not be empty or None")
        try:
            decrypted_password = self.decrypt_password(hashed_password)
            if decrypted_password == plain_password:
                return True
            else:
                return False
        except Exception as e:
            raise e

    def decrypt_password(self, hashed_password: bytes) -> str:
        if not hashed_password:
            raise ValueError("encrypted_password can not be empty or None")
        try:
            return self.fernet.decrypt(hashed_password).decode()
        except Exception as e:
            raise e
