#!/usr/bin/env bash

INSTALL_LOG="/tmp/dcs_install.log"
export INSTALL_LOG

CURRENT_DIR=$(pwd)
DATAPATH="/opt/powercloud/dcs/dcs_server/data"
dcsSERVERPATH="/opt/powercloud/dcs/dcs_server"
SAVEBACKPATH="/opt/powercloud/dcs/dcs_server_bak"

PARAMNUM=$#

# 读取数据库配置，备份数据库
USERNAME=$(grep 'db_username' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
PASSWORD=$(grep 'db_password' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
DATABASE=$(grep 'postgres_database =' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)

DATABASE_TYPE=$(grep 'database_type =' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
POOL_SIZE=$(grep 'pool_size' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
HOST=$(grep 'db_host' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
PORT=$(grep 'db_port =' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)

CDNGateWay_redis_ip=$(grep 'CDNGateWay_redis_ip =' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
CDNGateWay_redis_port=$(grep 'CDNGateWay_redis_port' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
redis_password=$(grep 'redis_password =' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)

log_conf_path=$(grep 'log_conf_path' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
log_db_path=$(grep 'log_db_path' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
PID_PATH=$(grep 'PID_PATH' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)

service_id=$(grep 'service_id' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
etcd_host=$(grep 'etcd_host' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
etcd_port=$(grep 'etcd_port' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)

CAS_LOG_PATH=$(grep 'cas_log_path' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
CAS_CONF_PATH=$(grep 'cas_conf_path' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
CAS_LIB_PATH=$(grep 'cas_lib_path' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
CAS_OPERATOR_SEARCH=$(grep 'cas_operator_search' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
cas_host=$(grep 'cas_host' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
cas_port=$(grep 'cas_port' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)
cas_password=$(grep 'cas_password' ${CURRENT_DIR}/param.properties | cut -d'=' -f2)


modify_config()
{
    # 修改dcs配置文件
    sed -i "s/db_username_v/$USERNAME/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/db_password_v/$PASSWORD/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/postgres_database_v/$DATABASE/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/database_type_v/$DATABASE_TYPE/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/pool_size_v/$POOL_SIZE/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/db_host_v/$HOST/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/db_port_v/$PORT/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini

    sed -i "s/CDNGateWay_redis_ip_v/$CDNGateWay_redis_ip/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/CDNGateWay_redis_port_v/$CDNGateWay_redis_port/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/redis_password_v/$redis_password/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini

    sed -i "s%log_conf_path_v%$log_conf_path%g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s%log_db_path_v%$log_db_path%g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s%PID_PATH_v%$PID_PATH%g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/service_id_v/$service_id/g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini

    sed -i "s%cas_log_path_v%$CAS_LOG_PATH%g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s%cas_conf_path_v%$CAS_CONF_PATH%g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s%cas_lib_path_v%$CAS_LIB_PATH%g" ${dcsSERVERPATH}/software/dcs/utils/conf.ini
    sed -i "s/192.168.10.123/$cas_host/g" ${dcsSERVERPATH}/software/dcs/utils/casclient/casclient.ini
    sed -i "s/6379/$cas_port/g" ${dcsSERVERPATH}/software/dcs/utils/casclient/casclient.ini
    sed -i "s/123567/$cas_password/g" ${dcsSERVERPATH}/software/dcs/utils/casclient/casclient.ini

}


# 检查环境
check_env()
{
	# 删除安装日志文件
	rm -rf ${INSTALL_LOG} >/dev/null 2>&1

	echo -e "\033[32;49;1m [----------------check env begin--------------] \033[39;49;0m"
	echo "`date` check env begin--------------" >> ${INSTALL_LOG} 2>&1

    # 检查是否已经安装dcsServer,如果存在,先执行shop.sh脚本
    if [ -d ${dcsSERVERPATH} ]; then
		echo "`date` Start to stop dcsServer service." >> ${INSTALL_LOG} 2>&1

		# 检查dcs_server服务是否已经启动
		process=`ps -ef |grep /opt/powercloud/dcs/dcs_server/software/dcs/dcs |grep -v "grep" |grep -v "status" |grep -v "stop" |grep -v "start"  |grep -v "restart"  |wc -l`
		if [ ${process} == 2 ]; then
			stop_dcsServer >> ${INSTALL_LOG} 2>&1
		fi

    fi
    echo -e "\033[32;49;1m [-----------------check env end---------------] \033[39;49;0m"
    echo "`date` check env end--------------" >> ${INSTALL_LOG} 2>&1
}


# 注册命令
register_cmd()
{
    #注册restart命令
    yes|cp ${CURRENT_DIR}/scripts/restart.sh /bin/restart_dcs_server
    chmod 755 /bin/restart_dcs_server

    #注册查看状态命令status
	yes|cp ${CURRENT_DIR}/scripts/status.sh /bin/status_dcs_server
    chmod 755 /bin/status_dcs_server

	#注册start命令
	yes|cp ${CURRENT_DIR}/scripts/start.sh /bin/start_dcs_server
    chmod 755 /bin/start_dcs_server

    #注册stop命令
	yes|cp ${CURRENT_DIR}/scripts/stop.sh /bin/stop_dcs_server
    chmod 755 /bin/stop_dcs_server

    #注册rollback命令
    yes|cp ${CURRENT_DIR}/scripts/rollback.sh /bin/rollback_dcs_server
    chmod 755 /bin/rollback_dcs_server
}

# 备份数据
backup()
{
    echo -e "\033[32;49;1m [----------------#backup database begin--------------] \033[39;49;0m"
    echo "`date` #backup database begin--------------" >> ${INSTALL_LOG} 2>&1

    if [ -d ${DATAPATH} ];then
        # 备份数据库
        touch ${DATAPATH}/dcs_database.sql
        chmod 777 ${DATAPATH}/dcs_database.sql
        su postgres -c "PGPASSWORD=${PASSWORD} pg_dump -h ${HOST} -p ${PORT} -U ${USERNAME} ${DATABASE} > ${DATAPATH}/dcs_database.sql " >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo -e "\033[31;49;1m [----------无法导出sql，备份数据库失败--------] \033[39;49;0m"
            exit 1
        fi
    else
        echo -e "\033[31;49;1m [----------data目录不存在，备份数据库失败--------] \033[39;49;0m"
        exit 1
    fi

    echo -e "\033[32;49;1m [----------------#backup database end--------------] \033[39;49;0m"
    echo "`date` #backup database end--------------" >> ${INSTALL_LOG} 2>&1
}

# 检查组件安装环境
check_components_env()
{
    echo -e "\033[32;49;1m [----------------check components environment begin--------------] \033[39;49;0m"
    echo "`date` check components environment begin--------------" >> ${INSTALL_LOG} 2>&1
    lib_path=${CURRENT_DIR}/lib
    cp -f ${CURRENT_DIR}/lib/* /usr/lib
    if [ -d ${lib_path} ];then
        chmod -R 755 ${lib_path}
        yes|cp ${lib_path}/libhiredis.so /usr/lib/libhiredis
        ln -s /usr/lib/libjson.so /usr/lib/libjson
        ln -s /usr/lib/liblogsuite.so.1.1.6 /usr/lib/liblogsuite.so
        ln -s /usr/lib/libcas.so.1.1.4 /usr/lib/libcas.so
        ln -s /usr/lib/libhiredis.so.0.13 /usr/lib/libhiredis.so
        ldconfig
    fi
    echo -e "\033[32;49;1m [----------------check components environment end--------------] \033[39;49;0m"
    echo "`date` check components environment end--------------" >> ${INSTALL_LOG} 2>&1
}

# 全量安装
all_install()
{
    echo "-----------`date` install dcs begin--------------" >> ${INSTALL_LOG} 2>&1
    echo -e "\033[32;49;1m [-----------install dcs begin------------] \033[39;49;0m"
    # 检查安装环境
    check_components_env
    check_env

    # 注册命令
    register_cmd

    mkdir -p /opt/powercloud/dcs/dcs_server/run
    # 备份目录
    if [ -d ${dcsSERVERPATH} ];then
        if [ ! -d ${DATAPATH} ];then
            mkdir -p ${DATAPATH}
        fi
        rm -rf ${SAVEBACKPATH};mv ${dcsSERVERPATH} ${SAVEBACKPATH}
    else
        rm -rf ${SAVEBACKPATH}>/dev/null 2>&1
    fi

	cp -rf ${CURRENT_DIR} /opt/powercloud/dcs/dcs_server
    if [ ! -d ${DATAPATH} ];then
        mkdir -p ${DATAPATH}
    fi
    #备份数据
    # backup

    # # 删除旧的数据库
    # su postgres -c "PGPASSWORD=${PASSWORD} psql -h ${HOST} -p ${PORT} -c ' DROP DATABASE ${DATABASE}'" >/dev/null 2>&1

    # echo "`date` Initialization database--------------" >> ${INSTALL_LOG} 2>&1;
    # echo -e "\033[32;49;1m [-----------Initialization database-------] \033[39;49;0m"
    # # 创建新数据库
    # su postgres -c "PGPASSWORD=${PASSWORD} psql -h ${HOST} -p ${PORT} -c 'CREATE DATABASE ${DATABASE}'">/dev/null 2>&1

    # if [ $? -ne 0 ]; then
    #     echo -e "\033[31;49;1m [----------创建数据库失败--------] \033[39;49;0m"
    #     exit 1
    # fi

    # # 初始化数据库
    # if [ ! -f ${CURRENT_DIR}/sql/cdn.sql ];then
    #     echo -e "\033[31;49;1m [----------setup.sql不存在，初始化数据库失败--------] \033[39;49;0m"
    #     exit 1
    # fi
    # PGPASSWORD=${PASSWORD} psql -U ${USERNAME} -d ${DATABASE} -h ${HOST} -p ${PORT} -f ${CURRENT_DIR}/sql/cdn.sql >/dev/null 2>&1
    # if [ $? -ne 0 ]; then
    #     echo -e "\033[31;49;1m [----------倒入数据错误，初始化数据库失败--------] \033[39;49;0m"
    #     exit 1
    # fi



    # 修改dcsServer配置文件
    #modify_config
    #yes|cp param.properties /opt/powercloud/dcs/dcs_server/software/dcs/utils/conf.ini
    #yes|cp licenseclient.conf /opt/powercloud/dcs/dcs_server/software/dcs/utils/authclient
    #yes|cp logdb.conf /opt/powercloud/dcs/dcs_server/software/dcs/utils/logsuite
    chmod 755 ${dcsSERVERPATH}/software/dcs
    mkdir -p /opt/powercloud/dcs/dcs_server/run

    echo "-----------install software end--------------" >> ${INSTALL_LOG} 2>&1
    echo -e "\033[32;49;1m [-----------install software finished---------] \033[39;49;0m"
}

pip install sqlalchemy
all_install
start_dcs_server

status_dcs_server
