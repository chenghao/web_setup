# coding:utf-8
__author__ = 'chenghao'

from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def get(self, *args, **kwargs):
        pass