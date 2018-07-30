# Verify login
# Author: ZY
# Stitching modificate: CL
# 参考：https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/
# 用户口令：passphrase，存储密钥：password
# 口令加密函数：derivePassphrase，口令认证函数：verifyPassphrase
# 用到的库：passlib、cryptography
import os
import binascii
from passlib.crypto.digest import pbkdf1
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# 全局变量设置

# 随机产生盐值，并不需要持久化存储以用于
# 1. 加密算法秘钥的再次延展生成
# 2. 口令散列存储的验证算法
salt = os.urandom(16)
# 返回二进制盐的16进制表示形式

backend = default_backend()
rounds = 10000
outlen = 32

#加密函数
def derivePassphrase(passphrase):
    algo = 'sha256'
    # 从人类可记忆「口令」生成面向加密算法用途的「密钥」
    password = pbkdf1(algo, passphrase.decode('latin1'), salt, rounds, keylen=outlen)
    # 扩展秘钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=outlen,
        salt=salt,
        iterations=rounds,
        backend=backend
    )
    password = kdf.derive(passphrase)
    return password
    #return binascii.hexlify(password)
    #return password
#用户输入密码加密
#解密函数
def verifyPassphrase(passphrase, password):
    # 验证密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=outlen,
        salt=salt,
        iterations=rounds,
        backend=backend
    )
    try:
        kdf.verify(passphrase, password)
        # 测试输出，相同则认证成功
        print('Key Verification OK!')
        return True
    except Exception as e:
        # 否则输出错误信息
        return False
