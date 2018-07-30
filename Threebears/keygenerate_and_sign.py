# Generate key and sign #
# Author: CL#
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from math import *
import os
#素数判断
def juge(n):
    if n == 1:
        return False
    for i in range(2, int(sqrt(n) + 1)):
        if n % i == 0:
            return False
    return True

#以用户密码为参数生成public_exponent
def generate_exponent(password):
    base=65537

    increase=0
    for i in password:
        increase=increase+ord(i)
    print(increase)
    exponent=base+increase
    while juge(exponent)!=True:
        exponent = exponent + 1
    return exponent

# 生成2048比特公私钥对
def generate_pub_and_key(password,username):
    # 生成用户私钥
    exponent=generate_exponent(password)
    key = rsa.generate_private_key(
        public_exponent=exponent,
        key_size=2048,
        backend=default_backend(),
    )
    #生成用户公钥
    pub = key.public_key()
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pub_pem=pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format = serialization.PublicFormat.SubjectPublicKeyInfo,
        #format=serialization.PublicFormat,
    )
    basedir = os.path.abspath(os.path.dirname(__file__))

    newfile= os.path.join(basedir+"/userfiles",username)
    downloadpath=os.path.join(basedir,'download')
    downloadpath=os.path.join(downloadpath,'pubkeys')
    newfile=os.path.join(newfile,'keys')
    if not os.path.exists(newfile):
        os.makedirs(newfile)
    if not os.path.exists(downloadpath):
        os.makedirs(downloadpath)
    with open(newfile+'/key.pem', 'wb') as f:
        f.write(key_pem)
    with open(newfile+'/pub.pem', 'wb') as f:
        f.write(pub_pem)
    #用户公钥保存在用户可下载目录
    with open(downloadpath+'/'+username+'_pub.pem','wb') as f:
        f.write(pub_pem)

    return key_pem,pub_pem

#进行签名
def sign(data_file, private_key):

    # 读取待签名数据
    data_file = open(data_file, 'rb')
    data = data_file.read()
    data_file.close()

    # 从PEM文件数据中加载私钥
    private_key = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
    )
    # 使用私钥对数据进行签名
    # 指定填充方式为PKCS1v15
    # 指定hash方式为sha256
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    # 将签名数据写入结果文件中
    with open(data_file.name+'.signature', 'wb') as signature_file:
        signature_file.write(signature)
    signature_file.close()

    # 返回签名数据
    return signature

def signfile(data_file,password,username):
    key_pem,pub_pem=generate_pub_and_key(password,username)
    sign(data_file, key_pem)

def signf(data_file,username):
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath=os.path.join(basedir,'userfiles')
    filepath=os.path.join(filepath,username)
    filepath=os.path.join(filepath,'keys')
    filepath=os.path.join(filepath,'key.pem')

    fc=open(filepath,'rb')
    key_pem=fc.read()
    fc.close()
    sign(data_file,key_pem)
