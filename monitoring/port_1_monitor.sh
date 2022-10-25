#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_1.py 1>/tmp/port_1_output.out &
     echo $! > /var/run/port_1_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_1_monitor.pid` ;;
   *)
     echo "usage: port_1_monitor {start|stop}" ;;
esac
exit 0

