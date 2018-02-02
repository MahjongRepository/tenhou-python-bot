#!/bin/sh -e

# cron will run each 5 minutes
# and will search the run process
# if there is no process, it will run it

# */5 * * * * bash /root/bot/bin/run.sh

PID=`ps -eaf | grep project/main.py | grep -v grep | awk '{print $2}'`

if [[ "" =  "$PID" ]]; then
  /root/bot/env/bin/python /root/bot/project/main.py
else
  WORKED_SECONDS=`ps -p "$PID" -o etimes=`
  # if process run > 60 minutes, probably it hang and we need to kill it
  if [ ${WORKED_SECONDS} -gt "3600" ]; then
    kill ${PID}
  fi
fi