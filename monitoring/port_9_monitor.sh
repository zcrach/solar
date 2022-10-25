#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_9.py 1>/tmp/port_9_output.out &
     echo $! > /var/run/port_9_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_9_monitor.pid` ;;
   *)
     echo "usage: port_9_monitor {start|stop}" ;;
esac
exit 0

