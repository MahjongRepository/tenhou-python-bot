#!/bin/sh -e

# cron will run each 5 minutes
# and will search the run process
# if there is no process, it will run it

# */5 * * * * bash /home/bot/app/bin/run.sh

PID=`ps -eaf | grep project/main.py | grep -v grep | awk '{print $2}'`
if [[ "" =  "$PID" ]]; then
  /home/bot/env/bin/python /home/bot/app/project/main.py
fi