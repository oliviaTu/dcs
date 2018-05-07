#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------------------------
#  Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
#  FileName: globals.py
#  Author: dcmp_team
#  Email: info@sowell-tech.com
#  Version: 0.0.1
#  LastChange: 2016-12-13
#  History: modified by HeYong  in December 13, 2016.
#  Desc: Defines all the global objects that are proxies to the current active context.
# -------------------------------------------------------------------------------------
"""
import json
import time
import hashlib
import traceback
from json import dumps
from json import loads
from datetime import datetime,timedelta

from dao import SESSION

from utils import CAS_LOG_path
from utils import CAS_CONF_PATH
from utils.casclient.cas import casClient
from utils.logsuite.logsuite import runlogapi
from utils.logsuite.logsuite import operationlogapi

# 日志对象
RUNLOG = runlogapi()
CASCLIENT = casClient(CAS_LOG_path, CAS_CONF_PATH)


class MessageError(Exception):
    """自定义异常抛出类"""
    def __init__(self, error_code, error_message):
        Exception.__init__(self)
        self.error_code = error_code
        self.error_message = error_message


def converter(obj_list):
    """
        对象转化器，将sqlalchemy查询结果对象转化为字典类型，并放在列表中返回。
    """
    result = []
    for obj_dict in obj_list:
        obj_dict = obj_dict.__dict__
        result.append(dict((key, obj_dict[key]) for key in obj_dict if
                           not key.startswith("_") and key not in ["instance", "model", "session"]))
    return result


def get_now_time():
    """
        获取当前时间
    """
    now_time = datetime.now()
    return now_time


def get_md5_value(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest


def utc2local(utc_st):
    """UTC时间转本地时间（+8:00）"""
    now_stamp = time.time()
    local_time = datetime.fromtimestamp(now_stamp)
    utc_time = datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            obj = utc2local(obj)
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            obj = utc2local(obj)
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def record_operation_log(request, req_type, req_user, return_code, error_message, execute_time):
    """
        解析request中信息，进行操作日志记录
        参数：
             request:                 http请求中request对象
             req_type:         字符   操作行为(1:新增、2:修改、3:删除 4:导入 5：导出 99:其他)
             req_user:         字符   从cookies中获取到的登录用户名
             return_code:      字符   执行结果
             error_message:    字符   错误信息
             execute_time:     整型   业务操作耗时
    """
    try:
        # 操作日志记录
        if return_code == '0':
            operation_result = 1
        else:
            operation_result = 0

        operation_log = operationlogapi()
        session = SESSION()
        # 请求中body数据
        req_body = loads(request.body)
        # 请求操作的客户端ip
        client_ip = request.headers.get('X-Real-Ip', request.remote_ip)
        # 操作业务，请求接口
        req_path = request.path
        # 请求uri中参数
        req_args = request.uri[len(req_path) + 1:]
        operation_log.record_operation(session, req_user, req_type, client_ip, req_path, dumps(req_body),
                                       req_args, operation_result, error_message, execute_time)
    except Exception, e:
        RUNLOG.error(traceback.format_exc())
    finally:
        session.close()


def cas(cookies, request_path, request_method):
    """
        包装cas认证，解析cookies
    """
    auth_result = {"result": "cas认证异常"}
    try:
        token = cookies.get("token").value
        if token[:3] == "%22":      # 去除%22 双引号
            token = token[3:-3]

        username = cookies.get("tokenUserName").value
        if username[:3] == "%22":   # 去除%22 双引号
            username = username[3:-3]

        auth_result = CASCLIENT.authentication(token, username, request_path, request_method)

        if auth_result is not None:
            auth_result = eval(auth_result)
        if auth_result["result"] != "CAS_SUCCESS":
            RUNLOG.warn(auth_result)

    except Exception:
        RUNLOG.error(traceback.format_exc())

    finally:
        return auth_result


# 插入时数据转换
def _insert(session, table_instance, data):
    if data.has_key("create_time") is False and hasattr(table_instance, "create_time"):
        setattr(table_instance, "create_time", datetime.now())
        setattr(table_instance, "update_time", datetime.now())
    for key, value in data.items():
        if hasattr(table_instance, key):
            setattr(table_instance, key, value)
    session.add(table_instance)

class thread_pool():
    """线程池配置类"""
    THREAD_POOL = 10

