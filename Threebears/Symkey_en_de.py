# Encrypt,dectypt and save the symmetric key #
# Author: CL#
import os
from pubencrypt_pridecrypt import *
import binascii

def keyencrption(key,username):

    basedir = os.path.abspath(os.path.dirname(__file__))
    # 文件夹不存在就创建
    if not os.path.exists(basedir + '/userfiles/' + username + '/keys'):
        os.makedirs(basedir + '/userfiles/' + username + '/keys')

    key_file = basedir + '/userfiles/' + username + '/keys/symkey.txt'
    fr = open(key_file, 'w')
    fr.write(binascii.hexlify(key).decode('utf-8'))
    fr.close()

    encrypted_file_name = basedir + '/userfiles/' + username + '/keys/' + username + '_encryptsymkey.txt'
    public_key_file=basedir+ '/userfiles/' + username + '/keys/pub.pem'
    key = encrypt(key, encrypted_file_name, public_key_file)

def keydecrption(username):
    basedir = os.path.abspath(os.path.dirname(__file__))
    # 文件夹不存在就创建
    if not os.path.exists(basedir + '/userfiles/' + username + '/keys'):
        os.makedirs(basedir + '/userfiles/' + username + '/keys')

    encrypted_file_name = basedir + '/userfiles/' + username + '/keys/' + username + '_encryptsymkey.txt'
    decrypted_file_name = basedir + '/userfiles/' + username + '/keys/' + username + '_decryptsymkey.txt'
    private_key_file = basedir + '/userfiles/' + username + '/keys/key.pem'
    key = decrypt(encrypted_file_name, decrypted_file_name, private_key_file)
    return key
