#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_10.py 1>/tmp/port_10_output.out &
     echo $! > /var/run/port_10_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_10_monitor.pid` ;;
   *)
     echo "usage: port_10_monitor {start|stop}" ;;
esac
exit 0

