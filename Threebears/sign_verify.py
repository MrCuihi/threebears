# Verify signature
# Author: CL

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography.exceptions import InvalidSignature

# 验证签名函数
def verify(data_file, signature_file, public_key_file):

    # 读取原始数据
    data_file = open(data_file, 'rb')
    data = data_file.read()
    data_file.close()

    # 读取待验证的签名数据
    signature_file = open(signature_file, 'rb')
    signature = signature_file.read()
    signature_file.close()

    # 从PEM文件中读取公钥数据
    key_file = open(public_key_file, 'rb')
    key_data = key_file.read()
    key_file.close()

    # 从PEM文件数据中加载公钥
    public_key = serialization.load_pem_public_key(
        key_data,
        backend=default_backend()
    )

    # 验证结果，默认为False
    verify_ok = False

    try:
        # 使用公钥对签名数据进行验证
        # 指定填充方式为PKCS1v15
        # 指定hash方式为sha256
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    # 签名验证失败会触发名为InvalidSignature的exception
    except InvalidSignature:
        # 打印失败消息
        print('invalid signature!')
    else:
        # 验证通过，设置True
        verify_ok = True

    # 返回验证结果
    return verify_ok

