import base64
from cryptography.fernet import Fernet
import api.globals as g

config = g.config

SECRET = config.get("chatgpt_user_secret")
recovered_key = base64.urlsafe_b64decode(SECRET.encode())
cipher_suite = Fernet(recovered_key)


def encrypt(password: str) -> str:
    # 加密一个密码
    encrypted_password = cipher_suite.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted_password).decode()


def decrypt(encrypted_password: str) -> str:
    # 解密密码
    encrypted_password = base64.urlsafe_b64decode(encrypted_password.encode())
    return cipher_suite.decrypt(encrypted_password).decode()
