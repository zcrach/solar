#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_7.py 1>/tmp/port_7_output.out &
     echo $! > /var/run/port_7_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_7_monitor.pid` ;;
   *)
     echo "usage: port_7_monitor {start|stop}" ;;
esac
exit 0

