#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# ----------------------------------------------------------
#     FileName: handler.py
#       Author: cn
#        Email:
#      Version: 0.0.1
#   LastChange: 2018-02-28 14:11
#      History:
# ----------------------------------------------------------
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import xlwt
import StringIO
import datetime
import traceback
from service.query_sales_trend_service import query
from utils.globals import RUNLOG, cas

from tornado import web, gen
from utils.globals import thread_pool
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import json
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
sys.setdefaultencoding('utf8')


class TrendFileHandler(web.RequestHandler):
    """
    页面下载表格，后台导出文件流
    """
    # self 对象是继承了tornado.web.RequestHandler的派生类
    executor = ThreadPoolExecutor(thread_pool.THREAD_POOL)  # 建立线程池，参数为线程池大小

    @web.asynchronous
    @gen.coroutine
    def get(self):
        username = None
        values = {}
        try:
            username = self.cookies.get("tokenUserName").value
            username = username[3:-3] if username[:3] == "%22" else username  # 去除%22 双引号

            auth_result = cas(self.cookies, self.request.path, self.request.method.lower())
            if auth_result['result'] == 'CAS_SUCCESS':
                self.set_header('Content-Type', 'application/octet-stream')
                self.set_header('Content-Disposition', 'attachment; filename=sales_trend.xls')
                arguments = self.request.arguments
                RUNLOG.info("receive request arguments = %s" % arguments)
                for key, value in arguments.items():
                    values[key] = value[0]
                # # 参数合法性校验
                for item in ["startTime", "endTime"]:
                    if item not in values.keys():
                        returnCode = 406400
                        errorMessage = "参数错误"
                        result = {"returnCode": returnCode, "errorMessage": errorMessage}
                        RUNLOG.info(str(result))
                        return
                returnCode, errorMessage, list_info = query(values)
                self.file_exits()
                # 将表格存入文件流
                sio = yield self.write_xls(list_info)

        except BaseException:
            returnCode = 506000
            errorMessage = "系统内部错误"
            result = {"returnCode": returnCode, "errorMessage": errorMessage}
            RUNLOG.info(str(result))
            RUNLOG.error(traceback.format_exc())
        finally:
            self.write(sio.getvalue())
            self.finish()

    def file_exits(self):
        """
        判断表格文件是否存在，有责
        :return:
        """
        my_file = '/opt/powercloud/dcs.xls'
        if os.path.exists(my_file):
            # 删除文件，可使用以下两种方法。
            os.remove(my_file)
        else:
            print 'no such file:%s' % my_file

    @run_on_executor
    def write_xls(self, data_array):
        """
        将数据写进表格
        """
        sio = StringIO.StringIO()
        try:
            wbk = xlwt.Workbook()
            sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
            sheet.write(0, 0, 'Date', xlwt.easyxf('font: height 250'))
            sheet.write(0, 1, 'New   sales', xlwt.easyxf('font: height 250'))
            sheet.write(0, 2, 'Accumulated sales', xlwt.easyxf('font: height 250'))
            hang = 1
            first_col = sheet.col(0)  # xlwt中是行和列都是从0开始计算的
            sec_col = sheet.col(1)
            thrd_col = sheet.col(2)
            first_col.width = 150 * 30
            sec_col.width = 150 * 30
            thrd_col.width = 250 * 30

            # 对字典按日期降序排列
            data_array = sorted(data_array, key=lambda data_array: data_array['date'], reverse=True)
            for data in data_array:
                for lie in range(len(data.keys())):
                    if lie == 0:
                        content = data['date']
                    elif lie == 1:
                        content = data['newSales']
                    elif lie == 2:
                        content = data['accumulatedSales']
                    sheet.write(hang, lie, content, xlwt.easyxf('font: height 250, name Arial, colour_index black, '
                                                                'bold off, italic off; align: wrap on, vert centre, horiz left;'))
                hang = hang + 1
            sio = StringIO.StringIO()
            wbk.save(sio)
            # wbk.save('/opt/powercloud/dcs.xls')
            # ## raise gen.Return(sio)
        except BaseException:
            RUNLOG.error(traceback.format_exc())
        finally:
            return sio
