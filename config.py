# coding:utf-8
__author__ = 'chenghao'

import logging
import logging.handlers
import os


# 访问该项目的前缀, 如http://ip:port/websetup/XX
url_prefix = "/websetup"

# 字体类型
font_type = os.path.abspath("../web_setup/static/fonts/calibri.ttf")

# 按每天生成日志文件 linux (win是存放在该项目的所在盘下)
# logHandler = logging.handlers.TimedRotatingFileHandler("/data/logs/hao", "D", 1)  # 服务器
logHandler = logging.handlers.TimedRotatingFileHandler("/home/chenghao/logs/websetup", "D", 1)
# 格式化日志内容
logFormatter = logging.Formatter('%(asctime)s %(name)-5s %(levelname)-5s %(message)s')
logHandler.setFormatter(logFormatter)
# 设置记录器名字
logger = logging.getLogger('websetup')
logger.addHandler(logHandler)
# 设置日志等级
logger.setLevel(logging.INFO)


# mysql
mysql_param = {
    "host": "127.0.0.1",
    "port": 3306,
    "charset": "utf8",
    "db": "test",
    "user": "root",
    "password": "123456",
    "use_unicode": True
}
# redis
redis_param = {
    "host": "127.0.0.1",
    "port": 6379
}