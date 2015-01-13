# coding:utf-8
__author__ = 'chenghao'

from datetime import datetime, date
import re
import uuid
import config
from config import logger
import smtplib
from email.mime.text import MIMEText
import time


# 格式化日期
def get_current_date(pattern="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(pattern)


# 验证手机号
def ver_mobile(data):
    p = re.compile(r"((13|14|15|17|18)\d{9}$)")
    return p.match(data)


# 验证邮箱
def ver_email(data):
    p = re.compile(r"(\w+[@]\w+[.]\w+)")
    return p.match(data)


# 获取随机数
def random_num():
    return uuid.uuid4()


# 发送邮箱
def send_email(to_emails, user_name, link):
    from_email = config.email_name
    # HOST & PORT
    host = 'smtp.163.com'
    port = 25
    # Create SMTP Object
    smtp = smtplib.SMTP()
    # show the debug log
    # smtp.set_debuglevel(1)
    # connect
    try:
        smtp.connect(host, port)
    except Exception, e:
        logger.error("连接163邮箱失败: " + str(e), exc_info=True)
    # login
    try:
        smtp.login(from_email, config.email_pwd)
    except Exception, e:
        logger.error("登录163邮箱失败: " + str(e), exc_info=True)

    content = """<div>
                    <p>HI, %s  您找回密码的连接地址如下</p>
                    <p>提示：如果您点击验证按钮无效，请把粘贴下面链接，复制到浏览器地址栏中，手动验证.</p>
                    <a href='%s'>%s</a>
                 </div>""" % (user_name, link, link)
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = u'取回密码 -- 一通江 - 通江第一门户网'
    msg['from'] = u"一通江 -通江第一门户网<%s>" % from_email
    try:
        smtp.sendmail(from_email, to_emails, msg.as_string())
    except Exception, e:
        logger.error("发送邮箱失败: " + str(e), exc_info=True)
    finally:
        smtp.quit()


# 计算星座
def compute_star(date_str):
    # 将str转换为time
    d = time.strptime(date_str, "%Y-%m-%d")
    # 格式化, 只获取月日
    mon_day = date(d.tm_year, d.tm_mon, d.tm_mday).strftime("%m-%d")

    if mon_day >= "01-21" and mon_day <= "02-19":
        star = u"水瓶座"
    elif mon_day >= "02-20" and mon_day <= "03-20":
        star = u"双鱼座"
    elif mon_day >= "03-21" and mon_day <= "04-20":
        star = u"白羊座"
    elif mon_day >= "04-21" and mon_day <= "05-21":
        star = u"金牛座"
    elif mon_day >= "05-22" and mon_day <= "06-21":
        star = u"双子座"
    elif mon_day >= "06-22" and mon_day <= "07-22":
        star = u"巨蟹座"
    elif mon_day >= "07-23" and mon_day <= "08-23":
        star = u"狮子座"
    elif mon_day >= "08-24" and mon_day <= "09-23":
        star = u"处女座"
    elif mon_day >= "09-24" and mon_day <= "10-23":
        star = u"天秤座"
    elif mon_day >= "10-24" and mon_day <= "11-22":
        star = u"天蝎座"
    elif mon_day >= "11-23" and mon_day <= "12-21":
        star = u"射手座"
    else:
        star = u"魔羯座"

    return star


# 计算年龄
def compute_age(date_str):
    d = datetime.now().strftime("%Y-%m-%d")
    date_end = time.strptime(d, '%Y-%m-%d')
    year_end = date_end.tm_year
    mon_end = date_end.tm_mon
    day_end = date_end.tm_mday

    date_begin = time.strptime(date_str, "%Y-%m-%d")
    year_begin = date_begin.tm_year
    mon_begin = date_begin.tm_mon
    day_begin = date_begin.tm_mday

    year = year_end - year_begin
    mon = mon_end - mon_begin
    day = day_end - day_begin
    if year > 0 and mon >= 0 and day >= 0:
        age = year
    elif year > 0 and year_end != year_begin and mon >= 0 and mon_end != mon_begin:
        age = year
    elif year <= 0:
        age = 0
    else:
        age = year - 1

    return age


class Dict(dict):
    '''
    Simple dict but support access as x.y style.
    > d1 = Dict()
    > d1['x'] = 100
    > d1.x
    100
    > d1.y = 200
    > d1['y']
    200
    > d2 = Dict(a=1, b=2, c='3')
    > d2.c
    '3'
    > d2['empty']
    Traceback (most recent call last):
        ...
    KeyError: 'empty'
    > d2.empty
    Traceback (most recent call last):
        ...
    AttributeError: 'Dict' object has no attribute 'empty'
    > d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
    > d3.a
    1
    > d3.b
    2
    > d3.c
    3
    '''

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
