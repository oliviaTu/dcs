#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
#——————————————————————————
# Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
# FileName: dcs.py
# Version: 0.0.1
# Author : tm,
# LastChange: 2018-03-09
# Desc:
# History:
#———————————————————————————
"""

import os
import sys
import socket
import platform
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define
from tornado.options import options
import traceback

from utils.globals import RUNLOG
from utils import LOG_CONF_PATH
from utils import LOG_DB_PATH
from utils.logsuite.logsuite_handler import QueryLogHandler

from api.operator_handler import OperatorHandler
from api.query_state_sales import QueryStateSalesHandler
from api.query_sales_trend import QuerySalesTrendHandler
from api.file_handler import TrendFileHandler
from api.state_file_handler import StateFileHandler
# from api.up_eq_handler import UpEqHandler

define("port", default=9095, help="run on the given port", type=int)


APP = tornado.web.Application([
    (r'/api/dcs/querySales', QueryStateSalesHandler),
    (r'/api/dcs/querySalesTrend', QuerySalesTrendHandler),
    (r'/api/dcs/file', TrendFileHandler),
    (r'/api/dcs/statefile', StateFileHandler),
], debug=False)


def windows_main():
    """程序入口main函数"""

    options.parse_command_line()
    port = options.port
    APP.listen(int(port))
    tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.instance().close()


def linux_main():
    """程序入口main函数"""
    try:
        options.parse_command_line()
        port = options.port
        APP.listen(int(port))
        tornado.ioloop.IOLoop.instance().start()
        tornado.ioloop.IOLoop.instance().close()
    except Exception:
        print traceback.format_exc()

    #create_daemon()
    options.parse_command_line()
    APP.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    RUNLOG.loginit(LOG_CONF_PATH, LOG_DB_PATH, 30)
    if "Windows" in platform.system():
        windows_main()

    elif "Linux" in platform.system():
        linux_main()

    else:
        print platform.system()
