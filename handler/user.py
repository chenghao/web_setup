# coding:utf-8
__author__ = 'chenghao'

from base import BaseHandler
import config


class Login(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("user/login.html")

    def post(self, *args, **kwargs):
        pass


class Register(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("user/register.html")

    def post(self, *args, **kwargs):
        pass


urls = [
    (config.url_prefix + "/user/login", Login),
    (config.url_prefix + "/user/register", Register),
]