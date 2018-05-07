#!/usr/bin/env python2.7
#-*- encoding:UTF-8 -*-

"""
版权所有 (C)2016, 深圳市视维科技有限公司。
作者  : 贺勇
日期    : 2016-07-21
版本 : logsuite_handler 0.0.1
"""
import MySQLdb
import os
import json
import time
import ConfigParser
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import psycopg2

import database

#数据库配置文件
global dbconf
dbconf = {}

# confname = os.path.split(os.path.realpath(__file__))[0] + '/logdb.conf'
log_db_path = ""

def getDbConf():
    """获取配置文件中数据库配置信息

    返回值：
        0：成功
        -1：失败
    抛出异常：
        exception：读取配置文件异常"""

    global dbconf
    try:
        conf = ConfigParser.RawConfigParser()
        conf.read(log_db_path)
        dbconf['dbip'] = conf.get("logdbinfo", "dbip")
        dbconf['usrid'] = conf.get("logdbinfo", "usrid")
        dbconf['passwd'] = conf.get("logdbinfo", "passwd")
        dbconf['dbport'] = conf.get("logdbinfo", "dbport")
        dbconf['logdbname'] = conf.get("logdbinfo", "logdbname")
    except Exception, e:
        print e
        return -1
    return 0


def getSelectSql(querylist, table):
    """根据查询条件，获取查询语句字符串
    参数：
        param1:  查询条件列表
        param2:  日志表名
    返回值：
        sql：查询的sql语句"""
        
    sql = "select user_name, operation, operation_ip, operation_service, request_body, request_args,\
           operation_result, operation_message, execute_time, FORMAT(operation_time, 'yyyy-mm-dd hh24:mi:ss') from %s" % (table)
    countsql = "select count(*) from %s" % (table)      
    iI = 0    
    pageNum = int(querylist['pageNum'])

    #每页展示条数
    if 'pageSize' not in querylist:
        pageSize = 10
    else:
        if int(querylist['pageSize']) > 1000:
            pageSize = 1000
        else:
            pageSize = int(querylist['pageSize'])
        
    #登录用户名
    if 'userName' in querylist:
        tmpstr = " where user_name = '%s'" % (querylist['userName'])
        sql = sql + tmpstr
        countsql = countsql + tmpstr
        iI = iI + 1

    #请求的操作行为
    if 'operation' in querylist and iI > 0:
        tmpstr = " and operation = '%s'" % (querylist['operation'])
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
    elif 'operation' in querylist and iI == 0:
        tmpstr = " where operation = '%s'" % (querylist['operation'])
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
    """
    #操作业务(模糊查询) 
    if 'operationService' in querylist and iI > 0:
        likestr = '%' + querylist['operationService'] + '%'
        tmpstr = " and operation_service like '%s'" % (likestr)
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
    elif 'operationService' in querylist and iI == 0:
        likestr = '%' + querylist['operationService'] + '%'		
        tmpstr = " where operation_service like '%s'" % (likestr)
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
    """
    #操作结果
    if 'operationResult' in querylist and iI > 0:
        tmpstr = " and operation_result = '%s'" % (querylist['operationResult'])
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
    elif 'operationResult' in querylist and iI == 0:
        tmpstr = " where operation_result = '%s'" % (querylist['operationResult'])
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1    
        
    #操作业务
    if 'operationService' in querylist and iI > 0:
        str = querylist['operationService']
        str = str.replace('%', '[%')
        str = str.replace('_', '[_')
        likestr = '%' + str + '%'
        tmpstr = " and operation_service like '%s' escape '['" % (likestr)
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
    elif 'operationService' in querylist and iI == 0:
        str = querylist['operationService']
        str = str.replace('%', '[%')
        str = str.replace('_', '[_')
        likestr = '%' + str + '%'
        tmpstr = " where operation_service like '%s' escape '['" % (likestr)
        sql = sql + tmpstr
        countsql = countsql + tmpstr        
        iI = iI + 1
   
    #查询时间
    if iI > 0:
        tmpstr = " and operation_time between '%s' and '%s';" % (querylist['startTime'], querylist['endTime'])
        countsql = countsql + tmpstr
    elif iI == 0:
        tmpstr = " where operation_time between '%s' and '%s';" % (querylist['startTime'], querylist['endTime'])
        countsql = countsql + tmpstr        

    #查询时间
    if iI > 0:
        tmpstr = " and operation_time between '%s' and '%s' order by operation_time desc limit %d offset %d;" % \
        (querylist['startTime'], querylist['endTime'], pageSize, (pageNum - 1)*pageSize)
        sql = sql + tmpstr
    elif iI == 0:
        tmpstr = " where operation_time between '%s' and '%s' order by operation_time desc limit %d offset %d;" % \
        (querylist['startTime'], querylist['endTime'], pageSize, (pageNum - 1)*pageSize)
        sql = sql + tmpstr
            
    return sql, countsql


def getReturnData(totalsize, datalist, querylist):
    """获取返回给前端的数据
    参数：
        param1:  日志库中查询的数据列表
        param2:  查询条件列表
    返回值：
        返回json格式的查询结果"""

    retData = {}
    operationLogList = []

    #获取返回数据
    retData['returnCode'] = '0'
    retData['errorMessage'] = '操作成功!'
    namelist = ['userName','operation','operationIp','operationService','requestBody','requsetArgs','operationResult',
                'operationMessage', 'executeTime', 'operationTime']    

    retData['totalSize'] = totalsize

    #获取operationLog对象
    for iI in range(len(datalist)):
        datadict = dict(zip(namelist, datalist[iI]))
        operationLogList.append(datadict)  
    retData['operationLogList'] = operationLogList    

    return json.dumps(retData)


def QueryLog(jRecvData):
    """查询日志信息
    参数:
        param1:  前端发送查询条件(json格式)
    抛出异常：
        Exception：数据库异常
    """	
    queryData = {}
    decodejson = json.loads(jRecvData)  
    if getDbConf() != 0:
        print 'read dbconf error'
        return -4, queryData

    url = 'mysql+mysqldb://%s:%s@%s:%s/%s' % (dbconf['usrid'], dbconf['passwd'], dbconf['dbip'], dbconf['dbport'], dbconf['logdbname'])

    try:
        #检测日志数据库是否存在
        if not database.database_exists(url):
            return -1, queryData

        #连接数据库
        dbconf['dbport']=int(dbconf['dbport'])
        conn = MySQLdb.connect(db=dbconf['logdbname'], user=dbconf['usrid'],
                               passwd=dbconf['passwd'], host=dbconf['dbip'], port=int(dbconf['dbport']))
        print "===========217"
        print conn

    except Exception, e:
        print e
        return -2, queryData 
    try:
        cur = conn.cursor()
    except Exception, e:
        conn.close()
        print e
        return -2, queryData

    #查询数据
    selectsql = getSelectSql(decodejson, 't_operation_log')
    try:
        #获取返回数据
        cur.execute(selectsql[0])
        rows = cur.fetchall()

        cur.execute(selectsql[1])
        totalsize = cur.fetchone()[0]          

        queryData = getReturnData(totalsize, rows, decodejson)          
    except Exception, e:
        cur.close()
        conn.close()
        print e
        return -3, queryData; 
            
    #关闭连接
    cur.close()
    conn.close()
    
    return 0, queryData


class QueryLogHandler(tornado.web.RequestHandler):
    def get(self):
        TIMEFORMAT = '%Y-%m-%d %X'
        recvData = {}
        retData = {}
        errData = {}

        arguments = self.request.arguments
        for key, value in arguments.items():
            recvData[key] = value[0]

        if ("pageNum" not in recvData.keys()) or ("startTime" not in recvData.keys()) \
            or ("endTime" not in recvData.keys()):
            errData["returnCode"] = 400
            errData["errorMessage"] = "参数错误!"
            errData["totalSize"] = 0
            errData["operationLogList"] = []
            retData = json.dumps(errData)
        else:
            print recvData
            ret = QueryLog(json.dumps(recvData))
            print "ret---------:", ret
            if ret[0] == 0:
                retData = ret[1]
            else:
                errData["returnCode"] = 1000
                print "log_handler_275--line"
                errData["errorMessage"] = "数据库错误!"
                errData["totalSize"] = 0
                errData["operationLogList"] = []
                retData = json.dumps(errData)
                print traceback.format_exc()
                traceback.print_exc()

        self.write(str(retData))


    def post(self, *args, **kwargs):
        retData = {}
        errData = {}
        ret = QueryLog(self.request.body)
        if ret[0] == 0:
            retData = ret[1]
        else:
            errData["returnCode:"] = 1000
            errData["errorMessage"] = "数据库错误!"
            errData["totalSize"] = 0
            retData = json.dumps(errData)
        print retData
        self.write(str(retData))
