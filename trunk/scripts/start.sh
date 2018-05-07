#!/bin/sh
num=$(ps -ef |grep /opt/powercloud/dcs/dcs_server/software/dcs/dcs | grep -v grep)
if [ "$num" ]; then
	echo "sysmanage is running"
	exit 0
fi

prog_path=/opt/powercloud/dcs/dcs_server/software/dcs/dcs
nohup ${prog_path} > /opt/powercloud/dcs/dcs_server/run/dcs.file 2>&1 &
if [ $? -ne 0 ]
then
	echo "start dcs failed"
	exit 1
else
	echo "start dcs success"
fi