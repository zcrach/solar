#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_8.py 1>/tmp/port_8_output.out &
     echo $! > /var/run/port_8_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_8_monitor.pid` ;;
   *)
     echo "usage: port_8_monitor {start|stop}" ;;
esac
exit 0

