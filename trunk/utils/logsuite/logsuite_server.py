#!/usr/bin/env python2.7
#-*- encoding:UTF-8 -*-

"""
版权所有 (C)2016, 深圳市视维科技有限公司。
作者  : 贺勇
日期    : 2016-07-06
版本 : logsuite_server 0.0.1
"""

import os
import json
import time
import ConfigParser

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import psycopg2


from tornado.options import define, options
define("port", default=8500, help="run on the given port", type=int)


import database
from logsuite_handler import QueryLogHandler

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
          handlers=[(r"/api/log/operation", QueryLogHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8500)
    tornado.ioloop.IOLoop.instance().start()

