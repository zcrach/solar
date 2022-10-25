#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_5.py 1>/tmp/port_5_output.out &
     echo $! > /var/run/port_5_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_5_monitor.pid` ;;
   *)
     echo "usage: port_5_monitor {start|stop}" ;;
esac
exit 0

