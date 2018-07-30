#Encrypt and decrypt (AES)
# Author: ZY
# Stitching modificate: CL
# coding: utf-8
import os
from Crypto.Cipher import AES
import binascii
from pubencrypt_pridecrypt import *

#处理文件路径及名称
def dealfilesname(name):
    namestr = name
    namelist = name.split('/')
    name_length = len(namelist)
    name = namelist[name_length - 1]
    path = namestr.strip(name)
    return name,path

class prpcrypt():
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv
        self.mode = AES.MODE_CBC
        self.pad = 0

    def __len__(self):
        return 32


    # 加密函数，如果text不是32的倍数【加密文本text必须为32的倍数！】，那就补足为32的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.这里使用AES-256确保安全
        length = 32
        count = len(text)
        extra = count % length
        if extra != 0:
            self.pad = length - (count % length)
            text = text + ('\0' * self.pad)

        ciphertext = cryptor.encrypt(text)
        return ciphertext

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(text)
        plain_text = plain_text.decode('utf-8').rstrip('\0')
        return plain_text


# 文件加密函数，加密后得到名为“encrypt_原文件名”的加密文件
def encrypt_file(content, cipher):

    text=content
    print(type(text))
    cipher_text = cipher.encrypt(binascii.hexlify(text).decode('utf-8'))

    return cipher_text


# 文件解密函数，解密后得到名为“decrypt_encrypt_原文件名”的解密后文件
def decrypt_file(name, cipher):
    fs = open(name, 'rb')
    text = fs.read()
    cipher_text = cipher.decrypt(text)
    fs.close()

    name,path=dealfilesname(name)

    fc = open(path+'decrypt_' + name, 'wb')
    fc.write(binascii.unhexlify(cipher_text))
    fc.close()
    return binascii.unhexlify(cipher_text)



