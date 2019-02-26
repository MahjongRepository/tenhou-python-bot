#!/bin/sh -e

# the cron job will be executed each 5 minutes
# and it will try to find bot process
# if there is no process, it will run it
# example of usage
# */5 * * * * bash /root/bot/bin/run.sh bot_settings_name

SETTINGS_NAME="$1"

PID=`ps -eaf | grep "project/main.py -s ${SETTINGS_NAME}" | grep -v grep | awk '{print $2}'`

if [[ "" = "$PID" ]]; then
  /root/bot/env/bin/python /root/bot/project/main.py -s ${SETTINGS_NAME}
else
  WORKED_SECONDS=`ps -p "$PID" -o etimes=`
  # if process run > 60 minutes, probably it hangs and we need to kill it
  if [[ ${WORKED_SECONDS} -gt "3600" ]]; then
    kill ${PID}
  fi
fi