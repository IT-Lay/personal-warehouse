import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# 加密函数
def func_encrypt_config(_key, plain_text):
    cipher = AES.new(_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    encrypted_text = base64.b64encode(ciphertext).decode()
    return iv + encrypted_text

# 解密函数
def func_decrypt_config(_key, encrypted_text):
    iv = base64.b64decode(encrypted_text[:24])
    ciphertext = base64.b64decode(encrypted_text[24:])
    cipher = AES.new(_key, AES.MODE_CBC, iv)
    decrypted_text = unpad(cipher.decrypt(ciphertext), AES.block_size).decode()
    return decrypted_text

key = b'quectel@gnss1234'  # 密钥
if not os.path.exists('en_mac.ini'):
    # 读取文件明文内容
    with open('mac.ini', 'r') as f:
        r_config=f.read()
    # 加密配置文件内容
    encrypted_content = func_encrypt_config(key, r_config)
    print("加密后的配置文件内容：")
    print(encrypted_content)
    with open('en_mac.ini', 'w') as fa:
        fa.write(encrypted_content)
else:
    # 读取文件密文内容
    with open('en_mac.ini', 'r') as f:
        r_config = f.read()
    # 解密配置文件内容
    decrypted_content = func_decrypt_config(key, r_config)
    print("解密后的配置文件内容：")
    print(decrypted_content)
    with open('mac.ini', 'w') as fa:
        fa.write(decrypted_content)