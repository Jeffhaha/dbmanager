import os
from cryptography.fernet import Fernet

# 生成一个有效的 Fernet 密钥
SECRET_KEY = Fernet.generate_key().decode()

print(SECRET_KEY)