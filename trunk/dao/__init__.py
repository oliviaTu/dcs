#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# ----------------------------------------------------------
#  Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
#  FileName: dao.__init__.py
#  Author: vod_team
#  Email: info@sowell-tech.com
#  Version: 0.0.1
#  LastChange: 2016-12-12
#  History: modified by HeYong  in December 12, 2016.
#  Desc:
# ----------------------------------------------------------

# --------------------------------------------------------------------------------
    连接池算法选用方案为:
        1.连接内存中的sqlite, 默认的连接池算法为 SingletonThreadPool 类, 即每个线程允许一个连接
        2.连接基于文件的sqlite, 默认的连接池算法为 NullPool 类, 即没有连接池
        3.对于其他情况, 默认的连接池算法为 QueuePool类, session不能手动关闭
        4.当然, 我们也可以实现自己的连接池算法: eg. db = create_engine('sqlite:///file.db', poolclass=YourPoolClass)

    max_overflow: 超出pool_size后可允许的最大连接数，默认为10, 这10个连接在使用过后, 不放在pool中, 而是被真正关闭的.
    pool_timeout: 获取连接的超时阈值, 默认为30秒
    pool_recycle:  默认为-1, 设置为3600, 即如果connection空闲了3600秒, 自动重新获取, 以防止connection被db server关闭.
    pool_size: 连接数大小，默认为5，正式环境该数值太小，需根据实际情况调大
#----------------------------------------------------------------------------------
"""
import sys
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

from utils import DATABASE_TYPE, USERNAME, PASSWORD, \
    POOL_SIZE, HOST, PORT, DATABASE

# 创建数据库会话

try:
    CONNECTOR = 'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (USERNAME, PASSWORD, HOST, PORT, DATABASE)
    print CONNECTOR
    ENGINE = create_engine(
        CONNECTOR,
        encoding='utf-8',
        pool_size=POOL_SIZE,
        pool_recycle=60,
        echo=False
    )
except BaseException:
    print traceback.format_exc()
    print "数据库初始化失败"
    sys.exit()

SESSION = sessionmaker(bind=ENGINE)

BASE = declarative_base()
# SESSION = scoped_session(sessionmaker(bind=ENGINE))
METADATA = BASE.metadata

__all__ = [ENGINE, BASE, SESSION, METADATA]
