###app run
## Author: CL、HFf
import os
import time
from flask import Flask
from flask import render_template, redirect, url_for, request, session,send_from_directory,jsonify
from flask import app, safe_join, send_from_directory
from functools import wraps
from datetime import datetime
from sqlalchemy import or_, and_
from werkzeug.security import generate_password_hash, check_password_hash  # 密码保护，使用hash方法
from flask_sqlalchemy import SQLAlchemy

#python.3# use mysqldb
import pymysql
pymysql.install_as_MySQLdb()
import shutil
import config
from verify import *
#files upload
from uploadconfig import  *
from default import *
#sign
from keygenerate_and_sign import *
#encrypt and decrypt files
from En_Decryption_AES  import *
#encrypt and decrypt key
from Symkey_en_de import *
#verify sign
from sign_verify import *
#hash
from hash import  *
from zip import *

app = Flask(__name__,static_folder="/home/parallels/Desktop/Therebears/templates",static_url_path="//home/parallels/Desktop/Therebears/templates")
app.config.from_object(config)


# 创建数据库的操作对象
db = SQLAlchemy(app)

#创建数据库的share表，记录下载url的下载次数
class Share(db.Model):
    __tablename__ = 'Share'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(100), nullable=True)  # 文件保存的名字
    count = db.Column(db.Integer, nullable=True)  # 下载次数
    temp = db.Column(db.Integer, nullable=True)  # 已经下载的次数

# 创建数据库的user表
class User(UserMixin,db.Model):
    __tablename__ = 'User3'
    id = db.Column(db.Integer,primary_key = True,autoincrement = True,nullable=False)
    username = db.Column(db.String(20),unique=True,nullable = False)
    _password = db.Column(db.String(200),nullable = False)
    pubkey=db.Column(db.Text,nullable=False)
    privatekey=db.Column(db.Text,nullable=False)
    userfilepath=db.Column(db.String(100),unique=True)


    def __init__(self,username,password):
        self.username=username
        self.password=password
        print ('_init',self.username,self.password,username)

     #使用指定的标识符加载用户
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # 定义一个外部使用的密码
    @property
    def password(self):
        return self._password

    #用户公私钥生成
    def generatekey(self,row_password):
        self.privatekey,self.pubkey = generate_pub_and_key(row_password,self.username)


   #创建用户目录文件夹
    def setfile(self):
        self.userfilepath=os.path.join(app.root_path+'/userfiles',self.username)
        if not os.path.exists(self.userfilepath):
            os.makedirs(self.userfilepath)
            #用于存储用户公私钥
            os.makedirs(self.userfilepath+'/keys')
            #存储用户文件
            os.makedirs(self.userfilepath+'/files')


    # 设置密码加密
    @password.setter
    def password(self,row_password):

        self.generatekey(row_password)
        row_password=bytes(row_password,'utf-8')
        self._password=derivePassphrase(row_password)
        # bytes类型解码为str类型
        self._password = binascii.hexlify(self._password).decode('utf-8')

    #密码验证
    def check_password(self,row_password):
        row_password=bytes(row_password,'utf-8')
        #str类型编码为bytes类型
        self._password=self._password.encode('utf-8')
        self._password=binascii.unhexlify(self._password)
        #用户输入密码加密
        # 把此时的password传入验证函数
        result=verifyPassphrase(row_password,self._password)
        return result


db.create_all()

@app.route('/<any(css, images, js,jpg, sound):folder>/<path:filename>')
def toplevel_static(folder, filename):
    filename = safe_join(folder, filename)
    cache_timeout = app.get_send_file_max_age(filename)
    return send_from_directory(app.static_folder, filename,
                               cache_timeout=cache_timeout)


@app.route('/')
def index():
       return render_template('WelcomeHa.html')


#注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('Register.html')
    else:
           usern = request.form.get('username')
           passw = request.form.get('password')
           user = User.query.filter(User.username==usern).first()
           # 判断用户名是否已经存在与数据库中
           if user:
               return u'username exitsted'
           else:
               #递交用户存储到数据库
               user = User(username=usern,password=passw)
               db.session.add(user)
               db.session.commit()
               # 重新向到登陆页面
               return redirect(url_for('login'))

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('Login.html')
    else:
       usern = request.form.get('username')
       passw = request.form.get('password')
       user = User.query.filter(User.username==usern).first()
       if user:
           if user.check_password(passw):
               # 登录的信息记录到session
               session['user']=usern
               session['id'] = user.id
               session['password']=passw
               session.permanent = True
               #匿名用户登录成功具有上传文件权限,跳转到上传文件界面
               return redirect(url_for('upload'))
           else:
               return u'password error'
       else:
           return u'username is no existed'


# 设置上传的目标文件夹

app.config['UPLOAD_FOLDER'] ='userfiles'

# 上传文件页面
@app.route('/upload')
def upload():
    #匿名用户访问上传文件页面必须先登录
    if session.get('user')== None:
        return redirect(url_for('login'))
    else:
        return render_template('Upload.html')


@app.route('/upload/result', methods=['POST'], strict_slashes=False)
def api_upload():
    # 拼接成合法文件夹地址
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    file_dir=os.path.join(file_dir,session['user'])
    file_dir=os.path.join(file_dir,'files')
    # 文件夹不存在就创建
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 从表单的file字段获取文件，file为该表单的name值
    f=request.files['file']
    text=f.read()
    size=len(text)
    # 判断是否是允许上传的文件类型,是否超过限制的文件大小10M
    if f and allowed_file(f.filename) and size <10*1024*1024:

        fname=f.filename
        # 获取文件后缀
        ext = fname.rsplit('.', 1)[1]
        unix_time = int(time.time())
        # 修改文件名
        new_filename = session['user']+'_encrypt_'+str(unix_time)+'.'+ext

        ###对文件进行加密###
        #  生成32位随机数
        key = os.urandom(32)
        #加密对称秘钥并保存
        keyencrption(key,session['user'])
        if os.path.exists(app.root_path+'/userfiles/'+session.get('user')+'/keys/symkey.pem'):
           os.remove(app.root_path+'/userfiles/'+session.get('user')+'/keys/symkey.pem')
        # 初始化密钥
        cipher = prpcrypt(key, key)
        filepath=file_dir+'/'+new_filename
        #cipher加密文件
        c=encrypt_file(text,cipher)
        fc=open(filepath,'wb')
        fc.write(c)
        fc.close()

        # 签名文件
        signf(filepath, session.get('user'))

        #计算散列值，供匿名用户下载
        shapath=file_dir+'/'+new_filename+'.signature'
        sha256(shapath)

        #同时保存到可供用户下载的目录,可供用户下载的目录还有对应的公钥
        fc=open(basedir+'/download/'+new_filename,'wb')
        fc.write(c)
        fc.close()

        # 限制下载url的下载次数 counts是从前端接收的参数，
        count = request.form.get('count')
        temp = 0
        share = Share(filename=new_filename, count=count, temp=temp)
        db.session.add(share)
        db.session.commit()


        return jsonify({"errno": 0, "errmsg": "上传成功"})
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})


#文件下载
@app.route("/download/<path:filename>")
def downloader(filename):
    #这里在下载的时候：# 对于匿名用户，下载按钮下载的内容包括未
    # 解密文件和签名文件，对于登陆的用户下载的内容为解密文件
    keep=filename
    keepuser=keep.split('_') [0]
    #匿名用户下载设置
    if session.get('user')==None:
        counts = db.session.query(Share.count).filter(filename==filename).all()
        temp = db.session.query(Share.temp).filter(filename==filename).all()
        if temp[len(temp)-1][0] < counts[len(counts)-1][0]:
            #已经下载的次数+1
            db.session.query(Share).filter(filename==filename).update({Share.temp:Share.temp+1})
            #生成本地路径
            dirpath = os.path.join(app.root_path, 'userfiles')
            dirpath = os.path.join(dirpath, keepuser)
            pubkeypath=os.path.join(dirpath,'keys')
            dirpath = os.path.join(dirpath, 'files')
            signfilename=filename+'.signature'
            pubkeyname='pub.pem'
            if not os.path.exists(dirpath+'/download'):
               os.mkdir(dirpath+'/download')
            #匿名用户需要被加密的文件
            shutil.copyfile(dirpath+'/'+filename,dirpath+'/download/'+filename)
            #匿名用户需要被加密的文件的相应签名文件
            shutil.copyfile(dirpath + '/' + signfilename, dirpath + '/download/' + signfilename)
            #匿名用户需要用于验证被加密的文件的相应签名的文件
            shutil.copyfile(pubkeypath + '/' + pubkeyname, dirpath + '/download/' + pubkeyname)

            #用户用于解密文件的对称秘钥
            #解密对称秘钥
            key = keydecrption(keepuser)
            fr = open(pubkeypath+'/symkey.txt', 'w')
            fr.write(binascii.hexlify(key).decode('utf-8'))
            fr.close()
            shutil.copyfile(pubkeypath+'/symkey.txt', dirpath + '/download/symkey.txt')
            #压缩打包已登录用户所需的文件
            zip_dir(dirpath+'/download',dirpath+'/download.zip')
            return send_from_directory(dirpath, 'download.zip', as_attachment=True)
        else:
            return u"下载次数已经超过限定次数"

    # 非匿名用户（已登陆用户）下载设置，不用判断下载的次数直接下载
    else:
        #对文件进行解密
        dirpath = os.path.join(app.root_path, 'userfiles')
        dirpath = os.path.join(dirpath,keepuser)
        dirpath = os.path.join(dirpath, 'files')
        filepath=os.path.join(dirpath,filename)
        # 解密文件
        keya = keydecrption(keepuser)
        cipher = prpcrypt(keya, keya)
        defile = decrypt_file(filepath, cipher)
        decryptfilename='decrypt_'+filename
        shapath=os.path.join(dirpath, decryptfilename)
        #生成散列值，供登录用户下载
        sha256(shapath)
        #已登录用户提供解密文件下载
        return  send_from_directory(dirpath, decryptfilename, as_attachment=True)

#静态文件散列值下载
@app.route("/downloadhash/<path:filename>")
def downloadhash(filename):
    keep = filename
    #匿名用户下载加密文件的散列值
    if session.get('user')==None:
        keepuser = keep.split('_')[0]
        downloadpath=os.path.join(app.root_path,'userfiles')
        downloadpath=os.path.join(downloadpath,keepuser)
        downloadpath=os.path.join(downloadpath,'files')
        downloadname=filename+'.signature'+'_sha256.txt'
        print (downloadname)
        return send_from_directory(downloadpath,downloadname,as_attachment=True)
    #登陆用户下载原文件散列值
    else:
        keepuser=keep.split('_')[1]
        downloadpath=os.path.join(app.root_path,'userfiles')
        downloadpath=os.path.join(downloadpath,keepuser)
        downloadpath=os.path.join(downloadpath,'files')
        downloadname=filename+'_sha256.txt'
        if os.path.exists(downloadpath+'/'+filename):
          os.remove(downloadpath+'/'+filename)
        return send_from_directory(downloadpath,downloadname,as_attachment=True)



if __name__ == '__main__':

     app.run(host='0.0.0.0', port=5001, debug=True)
             #ssl_context=('/home/parallels/Documents/server/server.cert','/home/parallels/Documents/server/server.key'))
            # ssl_context=('/home/parallels/Documents/ca/server-cert.pem',
            #  '/home/parallels/Documents/ca/server-key.pem'))
