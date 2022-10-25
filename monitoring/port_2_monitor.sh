#!/bin/bash

case $1 in
  start)
     /usr/bin/python3 /home/solar/versa_upgrade/port_2.py 1>/tmp/port_2_output.out &
     echo $! > /var/run/port_2_monitor.pid ;
     ;;
   stop)
     kill `cat /var/run/port_2_monitor.pid` ;;
   *)
     echo "usage: port_2_monitor {start|stop}" ;;
esac
exit 0

