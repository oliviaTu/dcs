#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (python) ,Sowell Tech. Co,Ltd
"""

import tornado.web
import datetime
import json
import traceback
from json import dumps
from service.operator_service import *
from utils.globals import RUNLOG
from utils.globals import record_operation_log, cas


class OperatorHandler(tornado.web.RequestHandler):
    """
    manange disk handler
    """
    def get(self):
        """
        user_group调用cas接口组装返回数据
        """
        start_time = datetime.datetime.now()
        returnCode = 0
        errorMessage = "操作成功"
        operator_list = []
        total_size = 0
        values = {}
        try:
            username = self.cookies.get("tokenUserName").value
            username = username[3:-3] if username[:3] == "%22" else username  # 去除%22 双引号
            auth_result = cas(self.cookies, self.request.path, self.request.method.lower())
            if auth_result['result'] == 'CAS_SUCCESS':
                url = self.request.uri
                if "start_num" not in url:
                    returnCode = 406400
                    errorMessage = "参数错误"
                    return
                if "operator_type" not in url:
                    returnCode = 406400
                    errorMessage = "参数错误"
                    return
                else:
                    start_num = self.get_argument("start_num")
                    start_num = int(start_num)
                    values['start_num'] = start_num
                    values['operator_type'] = self.get_argument("operator_type")
                    if "size" in url:
                        size = self.get_argument("size")
                        values["size"] = int(size)
                    else:
                        values["size"] = 10
                    if 'operator_name' in url:
                        operator_name = self.get_argument("operator_name")
                        values["operator_name"] = operator_name
                    returnCode, errorMessage, operator_list, total_size = select(values)
            else:
                returnCode = -2
                errorMessage = auth_result['result']
        except Exception:
            returnCode = 506000
            errorMessage = "系统内部错误"
            RUNLOG.error(traceback.format_exc())

        finally:
            self.request.body = dumps(values)
            end_time = datetime.datetime.now()            # 操作日志记录
            execute_time = (end_time - start_time).microseconds / 1000  # 业务操作耗时
            record_operation_log(self.request, '1', username, returnCode, errorMessage, execute_time)   # 操作日志记录
            self.write(dumps({"returnCode": returnCode, "errorMessage": errorMessage,\
                "operator_list": operator_list, "total_size": total_size}))
