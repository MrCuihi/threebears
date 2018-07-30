# Encrypt by publickey ,decrypt by privatekey
# Author: CL

# 导入cryptography库的相关模块和函数
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import padding
import os
import binascii

# 加密函数
def encrypt(src, dst_file, public_key_file):

    data=src

    # 读取公钥数据
    key_file = open(public_key_file, 'rb')
    key_data = key_file.read()
    key_file.close()

    # 从公钥数据中加载公钥
    public_key = serialization.load_pem_public_key(
        key_data,
        backend=default_backend()
        )

    # 使用公钥对原始数据进行加密，使用PKCS#1 v1.5的填充方式
    out_data = public_key.encrypt(
        data,
        padding.PKCS1v15()
    )

    # 将加密结果输出到目标文件中
    # write encrypted data
    out_data_file = open(dst_file, 'wb')
    out_data_file.write(out_data)
    out_data_file.close()

    # 返回加密结果
    return out_data


# 解密函数
def decrypt(src_file, dst_file, private_key_file):

    # 读取原始数据
    data_file = open(src_file, 'rb')
    data = data_file.read()
    data_file.close()

    # 读取私钥数据
    key_file = open(private_key_file, 'rb')
    key_data = key_file.read()
    key_file.close()

    # 从私钥数据中加载私钥
    private_key = serialization.load_pem_private_key(
        key_data,
        password=None,
        backend=default_backend()
    )

    # 使用私钥对数据进行解密，使用PKCS#1 v1.5的填充方式
    out_data = private_key.decrypt(
        data,
        padding.PKCS1v15()
    )

    # 将解密结果输出到目标文件中
    out_data_file = open(dst_file, 'wb')
    out_data_file.write(binascii.hexlify(out_data))
    out_data_file.close()

    # 返回解密结果
    return out_data

