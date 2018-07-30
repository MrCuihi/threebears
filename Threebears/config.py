#config base
# Author: CL
import os
DEBUG = True
SECRET_KEY = os.urandom(24)
#配置数据库，连接demo
SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:cl090325@127.0.0.1:3306/threebears"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True

