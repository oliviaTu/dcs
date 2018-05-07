#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
#——————————————————————————
# Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
# FileName: run.py
# Version: 0.0.1
# Author : tumin
# LastChange: 2018-02-03
# Desc:
# History:
#———————————————————————————
"""

import datetime

from sqlalchemy import Index
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import VARCHAR
from sqlalchemy import DateTime

from dao import BASE
from dao.base import BaseWrapper


class OrderHistory(BASE, BaseWrapper):
    "订单记录表"
    __tablename__ = 't_order_history'

    table_id = Column("id", Integer, primary_key=True)                # 主键，自增长
    order_number = Column(VARCHAR(32), unique=True, nullable=False)  # 订单号
    pay_history_id = Column(Integer)                                   # 支付历史记录id
    user_tel = Column(VARCHAR(32))                       # 用户手机号
    user_id = Column(VARCHAR(36))                           # 用户id
    payment = Column(Integer)                                         # 支付方式
    sn = Column(VARCHAR(255))                                         # 设备sn号
    sales_user_name = Column(VARCHAR(255))                           # 业务员登录账户
    equ_type = Column(Integer)                                        # 设备型号
    active_code = Column(VARCHAR(32))                                 # 激活码
    # distributed = Column(Integer, default=0)                          # 是否发放设备，0：未发放，1：已发放
    status = Column(Integer)                                          # 账单状态,1：正常,0：不正常,2:未支付
    # pay_status = Column(Integer)                                      # 支付状态，0：未支付，1：已支付
    remaining_date = Column(Integer)                                  # 剩余支付天数
    # grant_operator = Column(VARCHAR(255))                             # 发放设备操作人
    check_operator = Column(VARCHAR(255))                             # 对账操作人
    isBind = Column(Integer, default=0)                               # 订单是否绑定设备，0：未绑定，1：已绑定
    delivery_addr = Column(VARCHAR(255))                            # 收货地址
    created_time = Column(DateTime, default=datetime.datetime.now())  # 创建时间, 无索引
    updated_time = Column(DateTime, default=datetime.datetime.now(),
                         onupdate=datetime.datetime.now())            # 最后更新时间, 无索引

    Index("idx_order_history_order_number", order_number)
    Index("idx_order_history_created_time", created_time)

    def __init__(self):
        BaseWrapper.__init__(self, self.__class__)

