#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# ----------------------------------------------------------
#  Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
#  FileName: service.__init__.py
#  Author: UserGroup
#  Email: info@sowell-tech.com
#  Version: 0.0.1
#  LastChange: 2017-06-14
#  History: modified by  YouShaoPing
#  Desc:
# ----------------------------------------------------------
"""
import requests
import traceback
from json import loads

from utils.globals import RUNLOG
from utils import CAS_OPERATOR_SEARCH


def select(values):
    """门户关联管理操作员查询接口调用函数，service层查询逻辑处理。

    参数：
        values  字典
    """
    returnCode = 0
    errorMessage = "操作成功"
    result = {}
    child_list = []
    operator_info_list = []
    total_size = 0
    try:
        # 分页查询条目和起点计算
        # page_num = int(values.get("pageNum"))
        # 每页展示条数默认为10，当大于1000时，取1000
        # page_size = 1000 if int(values.get("pageSize", 10)) > 1000 else int(values.get("pageSize", 10))
        key = "ertjmFRGyriRFogjCDf38978"
        page_num = values['start_num']
        page_size = values['size']
        offset = int(page_num) * int(page_size)  # 分页起点
        limit = offset + int(page_size)  # 每页展示条数

        params = {
            "key": key,
            "page": 1,
            "results_per_page": 9999,
            "operatorType": "2"
        }

        portal_id = values.get("portalId")
        status = values.get("status")
        operator_name = values.get("operatorName")
        auth_status = values.get("authStatus")

        # 设置查询条件
        if operator_name:
            params["operatorName"] = operator_name

        url = CAS_OPERATOR_SEARCH + '/api/cas/operator'
        # 循环请求3次
        for i in range(3):

            response = requests.get(
                url=url,
                params=params,
                headers={"Connection": "close", 'content-type': 'application/json'}
            )

            if response.status_code is not 200:
                logstr = "portalRefAuth release get cas error: status_code %d in %d release" \
                         % (response.status_code, i+1)
                RUNLOG.error(logstr)

            elif response.content:
                result = loads(response.content)

    except Exception:
        returnCode = 500
        errorMessage = "系统内部错误"
        RUNLOG.error(traceback.format_exc())

    finally:
        total_size = result['num_results']
        operator_list = result['objects']
        return returnCode, errorMessage, operator_list, total_size
