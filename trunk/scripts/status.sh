#!/bin/sh

ver_conf=/opt/powercloud/dcs/dcs_server/version
INSTALL_DIR=/opt/powercloud/dcs/dcs_server

#function readCONF() {
#    INIFILE=$1; SECTION=$2; ITEM=$3
#    readIni=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2;exit}' $INIFILE`
#    echo $readIni
#}

#db_ip=( $( readCONF ${prog_conf} DB host ) )
#db_port=( $( readCONF ${prog_conf} DB port ) )
#db_user=( $( readCONF ${prog_conf} DB user ) )
#db_pass=( $( readCONF ${prog_conf} DB pass ) )
#db_name=( $( readCONF ${prog_conf} DB name ) )

#psql -h ${db_ip} -p ${db_port} "user=${db_user} password=${db_pass} dbname=${db_name}" << EOF > status.scripts
#    SELECT value FROM t_authcenter_conf WHERE key='pid' ;
#EOF

#sed -i 's/^[ \t]*//g' status.scripts

#pid_file=$(sed -n '3p' status.scripts)
#rm -f status.scripts
#echo "$pid_file"


RED_COLOR='\E[31m'
GREEN_COLOR='\E[32m'
RES='\E[0m'

log_info() {
    echo -e "${GREEN_COLOR}$1${RES}"
}

log_warning() {
    echo -e "${RED_COLOR}$1${RES}"
}

log_info "[-----ProductName:$(head -n1 ${ver_conf} | tail -n1 | cut -d'=' -f2)-----]"
log_info "[-----ProductVersion:$(head -n2 ${ver_conf} | tail -n1 | cut -d'=' -f2)-----]"
log_info "[-----ProductProvider:$(head -n3 ${ver_conf} | tail -n1 | cut -d'=' -f2)-----]"
log_info "[-----CreateTime:$(head -n4 ${ver_conf} | tail -n1 | cut -d'=' -f2)-----]"

process=`ps -ef |grep /opt/powercloud/dcs/dcs_server/software/dcs/dcs |grep -v "grep" |grep -v "status" |grep -v "stop" |grep -v "start"  |grep -v "restart"  |wc -l`

if [ ${process} -eq 2 ]; then
    log_info "[-----Server status:started-----]"
else
    log_warning "[-----Server status:stopped-----]"
fi
