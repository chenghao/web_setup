# coding:utf-8
__author__ = 'chenghao'
import random
import string
import StringIO
from PIL import Image, ImageDraw, ImageFont
from base import BaseHandler
import config
import cache

"""随机验证码"""


class VerCode(BaseHandler):
    def get(self, *args, **kwargs):
        imei = self.get_argument("imei")  # 手机设备的唯一标识

        img_size = (90, 40)  # 图片大小
        width, height = img_size  # 长，宽
        # 颜色值，图片大小，背景颜色
        im = Image.new('RGBA', img_size, (255, 255, 255))
        # 随机获取4位数
        rule = string.letters + string.digits
        texts = random.sample(rule, 4)

        charset = "".join(texts)
        try:
            cache.redis_cache.set(cache.ver_code_prefix + imei, charset)
        except:
            pass
        # 创建画布
        draw = ImageDraw.Draw(im)
        # 设置字体大小
        font_type = config.font_type
        font_type = font_type.replace("\\", "/")
        font = ImageFont.truetype(font_type, 40)

        # 增加干扰线
        for i in xrange(200):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            # 干扰线颜色
            fill = (random.randint(130, 250), random.randint(130, 250), random.randint(130, 250))
            draw.line(((x1, y1), (x2, y2)), fill=fill)

        x = 5
        y = 2
        for word in texts:
            # 字体颜色
            fill = (random.randint(0, 130), random.randint(0, 130), random.randint(0, 130))
            draw.text((x, y), word, font=font, fill=fill)
            x += 20

        # 增加像素点
        for i in xrange(1000):
            x1 = random.randint(0, width - 1)
            y1 = random.randint(0, height - 1)
            # 像素点颜色
            fill = (random.randint(20, 250), random.randint(20, 250), random.randint(20, 250))
            im.putpixel((x1, y1), fill)

        mem = StringIO.StringIO()
        im.save(mem, "JPEG")
        img_data = mem.getvalue()
        mem.close()

        self.set_header('Content-Type', 'image/jpeg; charset=utf-8')
        self.finish(img_data)


urls = [
    (config.url_prefix + "/verCode", VerCode),  # 验证码
]
