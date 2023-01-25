from cryptography.fernet import Fernet

# Key for encrypting and decrypting passwords
f_key: bytes = b"-mMdnutdSi2gfGM0lio-jugM-OlwOazVNufKIBZUGq0="


class Hash:
    # Encrypt a plaintext password
    def encrypt_password(password: str):
        fernet = Fernet(f_key)
        return fernet.encrypt(password.encode())

    # Verify if the plaintext password matches the hashed password
    def verify_password(hashed_password: bytes, plain_password):
        fernet = Fernet(f_key)
        if fernet.decrypt(hashed_password).decode() == plain_password:
            return True
        else:
            return False

    # Decrypt a hashed password
    def decrypt_password(hashed_password: bytes):
        fernet = Fernet(f_key)
        return fernet.decrypt(hashed_password).decode()