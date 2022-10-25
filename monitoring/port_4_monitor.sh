#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_4.py 1>/tmp/port_4_output.out &
     echo $! > /var/run/port_4_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_4_monitor.pid` ;;
   *)
     echo "usage: port_4_monitor {start|stop}" ;;
esac
exit 0

