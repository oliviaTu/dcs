#!/usr/bin/env python2.7
# -*- encoding:UTF-8 -*-

"""
版权所有 (C)2016, 深圳市视维科技有限公司。
作者  : 贺勇
日期    : 2016-07-06
版本 : logsuite_conf 0.0.1
修改版本	： logsuite_conf 0.0.2
       修改将配置文件改为由调用者传入，不使用获取py文件所在路径
"""

import os
import sys
import string
import hashlib
import traceback
import time

# 配置信息--全局变量
global g_conf

# 配置文件修改时间--全局变量
global g_file_mtime
g_file_mtime = '2000-01-01 00:00:00'


# 配置文件路径--全局变量
# global g_confFile
# g_confFile = os.path.split(os.path.realpath(__file__))[0] + '/LogSuite.conf'

# 配置信息类
class cLogSuiteConf:
    def __init__(conf):
        conf.level = ''
        conf.nor_log_path = ''
        conf.nor_filename = ''
        conf.biz_log_path = ''
        conf.biz_filename = ''
        conf.keep_count = 50
        conf.max_size = 100
        conf.day_mode = 1


g_conf = cLogSuiteConf()


def init_LogSuite_conf(conf_file):
    """配置文件加载

    返回值：
        0:加载成功
        1：文件未改动无法加载
        -1：加载失败
    异常抛出:
        IOError:配置文件打开异常"""
    if not os.path.exists(conf_file):
        print 'Not Find LogSuite Conf File!'
        return -1
    else:  # 判断配置文件修改时间，如果未被修改返回1
        timeFormat = '%Y-%m-%d %X'
        statinfo = os.stat(conf_file)
        timestr = time.strftime(timeFormat, time.localtime(statinfo.st_ctime))
        global g_file_mtime
        if g_file_mtime != timestr:
            g_file_mtime = timestr
        else:
            return 1

    # 打开配置文件
    try:
        fp = open(conf_file, 'r')
    except:
        print traceback.format_exc()
        return -2

    # 读取配置文件并赋值
    while True:
        line = fp.readline()
        if 'level' in line:
            g_conf.level = line[6:-1]
        elif 'nor_log_path' in line:
            g_conf.nor_log_path = line[13:-1]
        elif 'nor_filename' in line:
            g_conf.nor_filename = line[13:-1]
        elif 'biz_log_path' in line:
            g_conf.biz_log_path = line[13:-1]
        elif 'biz_filename' in line:
            g_conf.biz_filename = line[13:-1]
        elif 'keep_count' in line:
            countstr = line[11:-1]
            g_conf.keep_count = int(countstr)
        elif 'max_size' in line:
            maxsizestr = line[9:-1]
            g_conf.max_size = int(maxsizestr)
        elif 'day_mode' in line:
            daymodestr = line[9:-1]
            g_conf.day_mode = int(daymodestr)
        else:
            break

    fp.close()
    return 0

