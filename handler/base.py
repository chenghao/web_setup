# coding:utf-8
__author__ = 'chenghao'

from tornado.web import RequestHandler


class Base(RequestHandler):
    def get(self, *args, **kwargs):
        pass