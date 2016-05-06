#!/bin/sh -e

# kill old process (just in case)
# usually old process will be already ended
PID=`ps -eaf | grep project/main.py | grep -v grep | awk '{print $2}'`
if [[ "" !=  "$PID" ]]; then
  echo "killing $PID"
  kill -9 $PID
fi

/home/bot/env/bin/python /home/bot/app/project/main.py