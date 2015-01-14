# coding:utf-8
__author__ = 'chenghao'

import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
from urls import handlers_urls
from db import dbutil
from config import mysql_param

define("port", default=7777, help="run on the given port", type=int)

# 禁用tornado的日志
tornado.options.options.logging = "none"
tornado.options.parse_command_line()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = handlers_urls

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        dbutil.init("mysql", mysql_param["db"], mysql_param["host"], mysql_param["port"], mysql_param["user"],
                    mysql_param["password"], mysql_param["password"])


http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(options.port)
tornado.ioloop.IOLoop.instance().start()