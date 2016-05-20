#!/bin/sh -e

# kill old process if it hang
# usually old process will be already ended
PID=`ps -eaf | grep project/main.py | grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  kill -9 ${PID}
fi

sleep 20
/home/bot/env/bin/python /home/bot/app/project/main.py