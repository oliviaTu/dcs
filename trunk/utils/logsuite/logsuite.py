#!/usr/bin/env python2.7
# -*- encoding:UTF-8 -*-

"""
版权所有 (C)2016, 深圳市视维科技有限公司。
作者  : 贺勇
日期    : 2016-07-06
版本 : logsuite 0.0.1
修改版本： 日志配置文件由调用者传入，在loginit方法中加入配置文件参数
"""
import os
import sys
import time
import logging
import threading
import traceback

import logsql
import logsuite_conf
import logsuite_handler


def deleteLog(type):
    """删除创建时间最早的日志
        参数：
            param1:  日志类型('biz'为特殊日志，其它默认为普通日志)
        返回值：
            0：删除成功
            -1：删除失败
        异常抛出：
            OSError: 文件删除异常
    """

    createtime = time.time()
    firstfile = ''

    # 获取文件列表
    if type == 'biz':
        filepath = logsuite_conf.g_conf.biz_log_path
        filelist = os.listdir(logsuite_conf.g_conf.biz_log_path)
        filename = logsuite_conf.g_conf.biz_filename
    else:
        filepath = logsuite_conf.g_conf.nor_log_path
        filelist = os.listdir(logsuite_conf.g_conf.nor_log_path)
        filename = logsuite_conf.g_conf.nor_filename

    # 查找最早创建的日志文件
    for str in filelist:
        if filename in str:
            statinfo = os.stat(filepath + os.sep + str)
            if createtime > statinfo.st_ctime:
                createtime = statinfo.st_ctime
                firstfile = filepath + os.sep + str

    # 删除最早创建的日志文件
    try:
        os.remove(firstfile)
    except:
        logging.error(traceback.format_exc())
        return -1
    return 0


def getLogFileNum(type):
    """获取日志文件序号和文件个数

    参数：
        param1:  日志类型('biz'为特殊日志，其它默认为普通日志)
    返回值：
        fileno(日志文件最大序号)和filecount(日志文件个数)"""

    fileno = 0
    filecount = 0

    # 获取文件列表
    if type == 'biz':  # 特殊等级日志
        filelist = os.listdir(logsuite_conf.g_conf.biz_log_path)
        filename = logsuite_conf.g_conf.biz_filename
    else:  # 普通等级日志
        filelist = os.listdir(logsuite_conf.g_conf.nor_log_path)
        filename = logsuite_conf.g_conf.nor_filename

    ilen = len(filename) + 1  # 文件名长度

    # 获取日志文件个数和非日期保存模式下日志文件最大序号数
    if logsuite_conf.g_conf.day_mode != 1:
        for str in filelist:
            if filename in str:
                filecount += 1
                num = str[ilen:]
                if num.isdigit():
                    if int(num) > fileno:
                        fileno = int(num)
    else:
        for str in filelist:
            if filename in str:
                filecount += 1

    return fileno, filecount


def mkLogDir():
    """	初始化创建日志目录
        异常抛出：
        OSError：目录创建失败
    """

    # 初始化创建普通日志存放目录
    try:
        if not os.path.isdir(logsuite_conf.g_conf.nor_log_path):
            os.makedirs(logsuite_conf.g_conf.nor_log_path)

            # 初始化创建特殊日志存放目录
        if not os.path.isdir(logsuite_conf.g_conf.biz_log_path):
            os.makedirs(logsuite_conf.g_conf.biz_log_path)
    except:
        logging.error(traceback.format_exc())
        return -1

    return 0


def log_backup_judge(type, file, bufsize):
    """判断日志文件个数，超过配置文件中设置个数则删除创建时间最早的日志文件
       判断日志文件大小，超过配置文件中设置大小则进行备份

    参数：
        param1:  日志类型('biz'为特殊日志，其它默认为普通日志)
        param2:  日志文件名(文件为全路径)
        param3:  需要记录日志内容字节长度
    返回值：
        0：成功
        -1：删除最早的日志文件失败
        -2：文件备份失败
    异常抛出："""

    TIMEFORMAT = '%Y-%m-%d %X'

    # 初始化日志目录
    if mkLogDir() != 0:
        return -1

    # 判断日志文件是否存在
    try:
        if not os.path.exists(file):
            os.mknod(file)
            return 0

        # 获取文件大小
        filesize = os.path.getsize(file)
        # 判断文件大小，超过配置文件设置大小则进行备份
        fileMaxSize = logsuite_conf.g_conf.max_size * 1024 * 1024
        if fileMaxSize < filesize + bufsize:
            filenum = getLogFileNum(type)

            # 判断文件个数是否已经达到配置文件中设置的个数
            if filenum[1] >= logsuite_conf.g_conf.keep_count:
                if deleteLog(type) != 0:
                    return -1
                    # 日志备份
            if logsuite_conf.g_conf.day_mode == 1:  # 按日期存储
                timestr = time.strftime(TIMEFORMAT, time.localtime())
                backupfile = file + '_' + timestr[0:10]
                os.rename(file, backupfile)
                os.mknod(file)
            else:  # 按序号存储
                backupfile = file + '_' + str(filenum[0] + 1)
                os.rename(file, backupfile)
                os.mknod(file)
    except:
        logging.error(traceback.format_exc())
        print -2

    return 0


class updateThread(threading.Thread):
    def __init__(self, conf_file, updateTime):
        threading.Thread.__init__(self)
        self.updateTime = updateTime
        self.conf_file = conf_file
        self.setDaemon(True)

    def run(self):
        while True:
            # 加载配置文件
            logsuite_conf.init_LogSuite_conf(self.conf_file)

            time.sleep(self.updateTime)


class runlogapi(object):
    """运行日志调用api接口"""

    def loginit(self, log_conf_path, log_db_path, updatetime):
        """初始化配置文件，并派生线程定时扫描配置文件"""
        logsuite_conf.init_LogSuite_conf(log_conf_path)
        logsuite_handler.log_db_path = log_db_path
        logthread = updateThread(log_conf_path, updatetime)
        logthread.start()

        return logthread

    def debug(self, message, executeTime=-1):
        """运行日志debug级别调用api
            参数:
                param1:  日志内容
                param2:  业务执行耗时(单位ms)，运行日志可默认为-1
            返回值:
                0：成功
                500：文件备份失败
        """
        TIMEFORMAT = '%Y-%m-%d %X'

        filename = logsuite_conf.g_conf.nor_log_path + os.sep + logsuite_conf.g_conf.nor_filename
        if log_backup_judge('nor', filename, len(message)) != 0:
            return 500

        # 日志打印
        if logsuite_conf.g_conf.level == 'DEBUG':
            printlevel = logging.DEBUG
        elif logsuite_conf.g_conf.level == 'INFO':
            printlevel = logging.INFO
        elif logsuite_conf.g_conf.level == 'WARN':
            printlevel = logging.WARNING
        elif logsuite_conf.g_conf.level == 'ERROR':
            printlevel = logging.ERROR
        else:
            printlevel = logging.CRITICAL

        # 设置日志打印等级、输出格式、日志文件写入文件名
        filestr = logsuite_conf.g_conf.nor_log_path + os.path.sep + logsuite_conf.g_conf.nor_filename
        logging.basicConfig(level=printlevel,
                            format='[%(asctime)s][%(levelname)s]%(message)s',
                            datefmt=TIMEFORMAT,
                            filename=filestr,
                            filemode='a')

        console = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        console.setFormatter(formatter)
        console_logger = logging.getLogger('')
        console_logger.addHandler(console)
        console_logger.setLevel(printlevel)

        filelog = logging.FileHandler(filestr)
        filelog.setFormatter(formatter)
        logger = logging.getLogger('')
        logger.addHandler(filelog)
        logger.setLevel(printlevel)

        lineno = sys._getframe().f_back.f_lineno
        funcname = sys._getframe().f_back.f_code.co_name
        filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
        if executeTime > -1:
            logstr = '[%s][%s][line:%d][executeTime:%d]%s' % (filename, funcname, lineno, executeTime, message)
        else:
            logstr = '[%s][%s][line:%d]%s' % (filename, funcname, lineno, message)

        logging.debug(logstr)
        logger.removeHandler(filelog)
        console_logger.removeHandler(console)
        return 0

    def info(self, message, executeTime=-1):
        """运行日志info级别调用api
            参数:
                param1:  日志内容
                param2:  业务执行耗时(单位ms)，运行日志可默认为-1
            返回值:
                0：成功
                500：文件备份失败
        """
        TIMEFORMAT = '%Y-%m-%d %X'

        filename = logsuite_conf.g_conf.nor_log_path + os.sep + logsuite_conf.g_conf.nor_filename
        if log_backup_judge('nor', filename, len(message)) != 0:
            return 500

        # 日志打印
        if logsuite_conf.g_conf.level == 'DEBUG':
            printlevel = logging.DEBUG
        elif logsuite_conf.g_conf.level == 'INFO':
            printlevel = logging.INFO
        elif logsuite_conf.g_conf.level == 'WARN':
            printlevel = logging.WARNING
        elif logsuite_conf.g_conf.level == 'ERROR':
            printlevel = logging.ERROR
        else:
            printlevel = logging.CRITICAL

        # 设置日志打印等级、输出格式、日志文件写入文件名
        filestr = logsuite_conf.g_conf.nor_log_path + os.path.sep + logsuite_conf.g_conf.nor_filename
        logging.basicConfig(level=printlevel,
                            format='[%(asctime)s][%(levelname)s]%(message)s',
                            datefmt=TIMEFORMAT,
                            filename=filestr,
                            filemode='a')

        console = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        console.setFormatter(formatter)
        console_logger = logging.getLogger('')
        console_logger.addHandler(console)
        console_logger.setLevel(printlevel)

        filelog = logging.FileHandler(filestr)
        filelog.setFormatter(formatter)
        logger = logging.getLogger('')
        logger.addHandler(filelog)
        logger.setLevel(printlevel)

        lineno = sys._getframe().f_back.f_lineno
        funcname = sys._getframe().f_back.f_code.co_name
        filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
        if executeTime > -1:
            logstr = '[%s][%s][line:%d][executeTime:%d]%s' % (filename, funcname, lineno, executeTime, message)
        else:
            logstr = '[%s][%s][line:%d]%s' % (filename, funcname, lineno, message)

        logging.info(logstr)
        logger.removeHandler(filelog)
        console_logger.removeHandler(console)
        return 0

    def warn(self, message, executeTime=-1):
        """运行日志warn级别调用api
            参数：
                param1:  日志内容
                param2:  业务执行耗时(单位ms)，运行日志可默认为-1
            返回值:
                0：成功
                500：文件备份失败
        """
        TIMEFORMAT = '%Y-%m-%d %X'

        filename = logsuite_conf.g_conf.nor_log_path + os.sep + logsuite_conf.g_conf.nor_filename
        if log_backup_judge('nor', filename, len(message)) != 0:
            return 500

        # 日志打印
        if logsuite_conf.g_conf.level == 'DEBUG':
            printlevel = logging.DEBUG
        elif logsuite_conf.g_conf.level == 'INFO':
            printlevel = logging.INFO
        elif logsuite_conf.g_conf.level == 'WARN':
            printlevel = logging.WARNING
        elif logsuite_conf.g_conf.level == 'ERROR':
            printlevel = logging.ERROR
        else:
            printlevel = logging.CRITICAL

        # 设置日志打印等级、输出格式、日志文件写入文件名
        filestr = logsuite_conf.g_conf.nor_log_path + os.path.sep + logsuite_conf.g_conf.nor_filename
        logging.basicConfig(level=printlevel,
                            format='[%(asctime)s][%(levelname)s]%(message)s',
                            datefmt=TIMEFORMAT,
                            filename=filestr,
                            filemode='a')

        console = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        console.setFormatter(formatter)
        console_logger = logging.getLogger('')
        console_logger.addHandler(console)
        console_logger.setLevel(printlevel)

        filelog = logging.FileHandler(filestr)
        filelog.setFormatter(formatter)
        logger = logging.getLogger('')
        logger.addHandler(filelog)
        logger.setLevel(printlevel)

        lineno = sys._getframe().f_back.f_lineno
        funcname = sys._getframe().f_back.f_code.co_name
        filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
        if executeTime > -1:
            logstr = '[%s][%s][line:%d][executeTime:%d]%s' % (filename, funcname, lineno, executeTime, message)
        else:
            logstr = '[%s][%s][line:%d]%s' % (filename, funcname, lineno, message)

        logging.warning(logstr)
        logger.removeHandler(filelog)
        console_logger.removeHandler(console)
        return 0

    def error(self, message, executeTime=-1):
        """运行日志error级别调用api
            参数：
                param1:  日志内容
                param2:  业务执行耗时(单位ms)，运行日志可默认为-1
            返回值:
                0：成功
                500：文件备份失败
        """
        TIMEFORMAT = '%Y-%m-%d %X'

        filename = logsuite_conf.g_conf.nor_log_path + os.sep + logsuite_conf.g_conf.nor_filename
        if log_backup_judge('nor', filename, len(message)) != 0:
            return 500

        # 日志打印
        if logsuite_conf.g_conf.level == 'DEBUG':
            printlevel = logging.DEBUG
        elif logsuite_conf.g_conf.level == 'INFO':
            printlevel = logging.INFO
        elif logsuite_conf.g_conf.level == 'WARN':
            printlevel = logging.WARNING
        elif logsuite_conf.g_conf.level == 'ERROR':
            printlevel = logging.ERROR
        else:
            printlevel = logging.CRITICAL

        # 设置日志打印等级、输出格式、日志文件写入文件名
        filestr = logsuite_conf.g_conf.nor_log_path + os.path.sep + logsuite_conf.g_conf.nor_filename
        logging.basicConfig(level=printlevel,
                            format='[%(asctime)s][%(levelname)s]%(message)s',
                            datefmt=TIMEFORMAT,
                            filename=filestr,
                            filemode='a')

        console = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        console.setFormatter(formatter)
        console_logger = logging.getLogger('')
        console_logger.addHandler(console)
        console_logger.setLevel(printlevel)

        filelog = logging.FileHandler(filestr)
        filelog.setFormatter(formatter)
        logger = logging.getLogger('')
        logger.addHandler(filelog)
        logger.setLevel(printlevel)

        lineno = sys._getframe().f_back.f_lineno
        funcname = sys._getframe().f_back.f_code.co_name
        filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
        if executeTime > -1:
            logstr = '[%s][%s][line:%d][executeTime:%d]%s' % (filename, funcname, lineno, executeTime, message)
        else:
            logstr = '[%s][%s][line:%d]%s' % (filename, funcname, lineno, message)

        logging.error(logstr)
        logger.removeHandler(filelog)
        console_logger.removeHandler(console)
        return 0

    def biz(self, message, executeTime):
        """业务日志调用api
            参数：
                param1:  日志内容
                param2:  操作耗时ms(int)
            返回值:
                0：成功
                500：文件备份失败
        """
        TIMEFORMAT = '%Y-%m-%d %X'

        filename = logsuite_conf.g_conf.biz_log_path + os.sep + logsuite_conf.g_conf.biz_filename
        if log_backup_judge('biz', filename, len(message)) != 0:
            return 500

        # 日志打印级别
        printlevel = logging.DEBUG

        # 设置日志打印等级、输出格式、日志文件写入文件名
        filestr = logsuite_conf.g_conf.biz_log_path + os.path.sep + logsuite_conf.g_conf.biz_filename
        logging.basicConfig(level=printlevel,
                            format='%(message)s',
                            datefmt=TIMEFORMAT,
                            filename=filestr,
                            filemode='a')

        lineno = sys._getframe().f_back.f_lineno
        funcname = sys._getframe().f_back.f_code.co_name
        filename = os.path.basename(sys._getframe().f_back.f_code.co_filename)
        logstr = '[%s][%s][line:%d][executeTime:%d]%s' % (filename, funcname, lineno, executeTime, message)

        console = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        console.setFormatter(formatter)
        console_logger = logging.getLogger('')
        console_logger.addHandler(console)
        console_logger.setLevel(printlevel)

        filelog = logging.FileHandler(filestr)
        filelog.setFormatter(formatter)
        logger = logging.getLogger('')
        logger.addHandler(filelog)
        logger.setLevel(printlevel)

        logging.info(logstr)
        logger.removeHandler(filelog)
        console_logger.removeHandler(console)
        return 0


class operationlogapi(object):
    """操作日志记录api"""

    def record_operation(self, session, user_name, operation, operation_ip, operation_service, request_body,
                         request_args, operation_result,
                         operation_message, execute_time):
        """操作日志调用api
            参数：
                param1:  登录用户名
                param2:  请求的操作行为枚举值,可扩展，1:新增、2:修改、3:删除 4:导入 5：导出 99:其他
                param3:  请求操作的客户端IP
                param4:  操作业务,请求接口
                param5:  body请求参数
                param6:  URI中的请求参数
                param7:  操作结果(int)
                param8:  操作耗时ms(int)
            返回值：
                True：执行成功
                False：数据库操作失败
            抛出异常：
                expression：数据库异常
        """

        # 检测日志表，不存在则创建
        try:
            # row = session.execute("select count(*) from pg_class where relname = 't_operation_log'").fetchone()
            # if row[0] == 0:
            #     sql = logsql.toperationlogtables['t_operation_log']
            #     session.execute(sql)
            #     session.commit()
            #     sql = logsql.toperationlogtables['idx_usr_name']
            #     session.execute(sql)
            #     session.commit()
            #     sql = logsql.toperationlogtables['idx_operation_time']
            #     session.execute(sql)
            #     session.commit()

            # 日志信息插入数据库
            # print "日志信息插入数据库"
            # print user_name, operation, operation_ip, operation_service, request_body, request_args, operation_result, operation_message, execute_time
            operation_message = unicode("operation_message", "utf-8")
            if operation_result == 0:
                sql = "insert into t_operation_log(" \
                      "user_name, operation, operation_ip, operation_service,request_body, request_args, " \
                      "operation_result, operation_message, execute_time, operation_time)" \
                      "values('%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', %d, current_timestamp)" % \
                      (user_name, operation, operation_ip, operation_service, request_body,
                       request_args, operation_result, operation_message, execute_time)
            else:
                sql = "insert into t_operation_log(" \
                      "user_name, operation, operation_ip, operation_service, request_body, request_args, " \
                      "operation_result, execute_time, operation_time)" \
                      "values('%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', current_timestamp)" % \
                      (user_name, operation, operation_ip, operation_service, request_body,
                       request_args, operation_result, execute_time)
            session.execute(sql)
            session.commit()
        except:
            logging.error(traceback.format_exc())
            return 1000

        return 0
