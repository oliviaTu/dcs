#!/usr/bin/env bash

CURRENT_DIR="/opt/wisecloud/cdn/live/sysmanage/sysmanage_server"
CURRENT_VERSION=$(grep "Version" /opt/wisecloud/cdn/live/sysmanage/sysmanage_server/version | awk -F '=' '{print $2}')  
LAST_VERSION=$(grep "Version" /opt/wisecloud/cdn/live/sysmanage/sysmanage_server_bak/version | awk -F '=' '{print $2}')
# 读取数据库配置，备份数据库
DBNAME=$(grep 'postgres_database' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
DBTYPE=$(grep 'database_type' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
USERNAME=$(grep 'db_username' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
PASSWORD=$(grep 'db_password' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
HOST=$(grep 'db_host' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
PORT=$(grep 'db_port' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)

SYSMANAGESERVERPATH="/opt/wisecloud/cdn/live/sysmanage/sysmanage_server"
SAVEBACKPATH="/opt/wisecloud/cdn/live/sysmanage/sysmanage_server_bak"
INSTALL_LOG="/tmp/SYSMANAGESERVER_install.log"
DATAPATH="/opt/wisecloud/cdn/live/sysmanage/data"
SAVEBAKSQL="/opt/wisecloud/cdn/live/sysmanage_server_bak/data/sysmanage_database.sql"


export INSTALL_LOG

if [ -d ${SAVEBACKPATH} ];then
    # 还原程序
    rm -rf ${SYSMANAGESERVERPATH};mv ${SAVEBACKPATH} ${SYSMANAGESERVERPATH}

    # 还原数据库
    if [ -f ${SAVEBAKSQL} ];then
        # 备份数据库
        PGPASSWORD=${PASSWORD} pg_dump -h ${HOST} -p ${PORT} -U ${USERNAME} ${DBNAME} >${DATAPATH}/sysmanage_database.sql >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo -e "\033[31;49;1m [----------无法导出sql，备份数据库失败--------] \033[39;49;0m"
            exit 1
        fi
        PGPASSWORD=${PASSWORD} psql -U ${USERNAME} -h ${HOST} -p ${PORT} <${SAVEBAKSQL} >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo -e "\033[31;49;1m [----------回滚数据库失败--------] \033[39;49;0m"
            echo "-----------`date` 回退数据库失败--------------" >> ${INSTALL_LOG} 2>&1
            exit 1
        else
            echo -e "\033[32;49;1m [-----------回滚数据库成功-------] \033[39;49;0m"
            echo "-----------`date` 回退数据库成功--------------" >> ${INSTALL_LOG} 2>&1
        fi
    fi
    echo -e "\033[32;49;1m [-----------------Current Version:${CURRENT_VERSION}  Last Version:${LAST_VERSION}---------------] \033[39;49;0m"
    echo "-----------`date` Current Version:${CURRENT_VERSION} Last Version:${LAST_VERSION}--------------" >> ${INSTALL_LOG} 2>&1
    exit 0
else
    echo -e "\033[31;49;1m [----------没发现回滚版本，回滚失败--------] \033[39;49;0m"
    exit 1
fi
