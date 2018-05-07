#!/usr/bin/env python2.7
#-*- encoding:UTF-8 -*-

"""
版权所有 (C)2016, 深圳市视维科技有限公司。
作者  : 贺勇
日期    : 2016-07-19
版本 : logsuite 0.0.1
"""

"""
说明：操作日志记录表
字段：
id	自增长id
user_name	登录用户名
operation	请求的操作行为;
            枚举值,可扩展，1:新增、2:修改、3:删除 4:导入 5：导出 6、登录 99:其他
operation_ip	请求操作的客户端IP
operation_service	操作业务,请求接口
request_body	body请求参数
requset_args	URI中的请求参数
operation_result	1:操作成功
                    0:操作失败
operation_message	失败描述
execute_time	操作耗时ms
operation_time	操作时间		
"""
toperationlogtables = {
    't_operation_log': "create table t_operation_log(id serial PRIMARY KEY,\
                             user_name varchar(32) not null,\
                             operation char(2) not null,\
                             operation_ip varchar(32) not null,\
                             operation_service varchar(256) not null,\
                             request_body text,\
                             request_args varchar(1024),\
                             operation_result char(1) not null,\
                             operation_message varchar(256) default(' '),\
                             execute_time int4 not null,\
                             operation_time timestamp not null)",
    'idx_usr_name' : "create index idx_usr_name on t_operation_log(user_name)",
    'idx_operation_time' : "create index idx_operation_time on t_operation_log(operation_time)"
}
