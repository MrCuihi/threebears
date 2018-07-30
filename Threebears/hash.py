# hash
# Author: ZY
import hashlib
import os
import sys

import hashlib


# SHA256计算散列值的函数
def sha256(filename):  # filename：文件路径
    f = open(filename, 'rb')
    sh = hashlib.sha256()
    sh.update(f.read())
    fr = open(filename + '_sha256.txt', 'w')  # 将散列值输出到“文件名_sha256.txt”中
    fr.write(sh.hexdigest())
    f.close()
    return



