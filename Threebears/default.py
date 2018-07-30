#config login#
# Author: CL#

#配置登录状态信息
from flask_login import LoginManager,UserMixin


login_manager = LoginManager()
login_manager.session_protection = "strong"

# 可设置为None，basic，strong已提供不同的安全等级
login_manager.login_view = "login"  # 设置登录页
