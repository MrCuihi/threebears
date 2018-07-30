##### config upload ######
# Author: CL
import os

#设置允许上传的文件类型,office文档、常见图片类型
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'JPG','jpeg','JPEG', 'PNG', 'bmp',
                          'BMP', 'xls','xlsx', 'gif', 'GIF','doc','docx','dot',
                          'dotx','PPT','ppt','pptx','PPTX','pdf'])

# 设置允许上传的文件最大为10M
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
#  获取当前项目的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 判断文件是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
