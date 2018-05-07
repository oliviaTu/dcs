#!/bin/sh

ps -ef | grep /opt/powercloud/dcs/dcs_server/software/dcs/dcs | grep -v grep | awk '{print $2}' | xargs kill -9