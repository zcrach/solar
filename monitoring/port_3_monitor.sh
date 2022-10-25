#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_3.py 1>/tmp/port_3_output.out &
     echo $! > /var/run/port_3_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_3_monitor.pid` ;;
   *)
     echo "usage: port_3_monitor {start|stop}" ;;
esac
exit 0

