# coding:utf-8
__author__ = 'chenghao'

from base import BaseHandler
import config
from db import dbutil
import json


class Login(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("user/login.html")

    def post(self, *args, **kwargs):
        args = self.request.arguments
        print args


class Register(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("user/register.html")

    def post(self, *args, **kwargs):
        args = self.request.arguments
        params = {}
        for i in args:
            params[i] = self.get_argument(i)

        item = dbutil.select_one("select loginName from user where loginName=?", params["loginName"])
        if item is None:
            row = dbutil.insert("user", **params)
            if row:
                re = {"status": 0}
            else:
                re = {"status": -1}
        else:
            re = {"status": -2}

        self.finish(json.dumps(re))


urls = [
    (config.url_prefix + "/user/login", Login),
    (config.url_prefix + "/user/register", Register),
]