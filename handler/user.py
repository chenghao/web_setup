# coding:utf-8
__author__ = 'chenghao'

from base import Base
import config


class Login(Base):
    def get(self, *args, **kwargs):
        print ".................."
        self.render("user/login.html")

    def post(self, *args, **kwargs):
        pass


urls = [
    (config.url_prefix + "/user/login", Login),
]