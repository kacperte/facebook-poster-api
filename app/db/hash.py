from cryptography.fernet import Fernet


f_key: bytes = b"-mMdnutdSi2gfGM0lio-jugM-OlwOazVNufKIBZUGq0="


class Hash:
    def bcrypt(password: str):
        fernet = Fernet(f_key)
        return fernet.encrypt(password.encode())

    def verify(hashed_passwrod: bytes, plain_password):
        fernet = Fernet(f_key)
        if fernet.decrypt(hashed_passwrod).decode() == plain_password:
            return True
        else:
            return False

    def uncrypt(hashed_passwrod: bytes):
        fernet = Fernet(f_key)
        return fernet.decrypt(hashed_passwrod).decode()
