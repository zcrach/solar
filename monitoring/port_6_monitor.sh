#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_6.py 1>/tmp/port_6_output.out &
     echo $! > /var/run/port_6_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_6_monitor.pid` ;;
   *)
     echo "usage: port_6_monitor {start|stop}" ;;
esac
exit 0

