

IMPORTANT: EVERYTHING IS EXPECTED TO BE DONE AS ROOT USE.

run the following command: 
sudo su 

then proceed. 

How to use:
Store .bin file in same storage as this script /home/solar/versa_upgrade/*.bin
Modify value in "/home/solar/versa_upgrade/versa_variables.py" to the name of the file.

If you're making changes to the image or any other variable you will need to restart the script.
run the following command:

        python3 /home/solar/versa_upgrade/other/stop_all.py

This will reset all the running processes.

I'm using monit to restart services if they stop, this is checked every 2 minutes.
You can check log in /var/log/monit.log

Config is under /etc/monit/monitrc

You can check if all services are running by running:

python3 /home/solar/versa_upgrade/other/show_running_services.py 

This will show it like this if they are running:
root      123147       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_1.py
root      123151       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_2.py
root      123155       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_3.py
root      123159       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_4.py
root      123163       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_5.py
root      123167       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_6.py
root      123171       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_7.py
root      123175       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_8.py
root      123179       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_9.py
root      123183       1  0 21:49 ?        00:00:00 /usr/bin/python3 /home/solar/versa_upgrade/port_10.py

If they are not showing, then just wait 2-3 minutes or check /var/log/monitrc. 
Also verify that monit is running.

Can check by doing:
systemctl show status 

You can check log for each port under /home/solar/versa_upgrade/log/port_*.log




Additional information:


We're using a VEP1445, i was not able to get the normal LTE module to work with normal network manager / modem manager / netplan .

So had to use MBIM.

I used this guide:

https://gist.github.com/Juul/e42c5b6ec71ce11923526b36d3f1cb2c


However, mbim does not have a "auto-start" function.

So this means that i had to include a script on boot and a running script (soon to be fixed.)
That does the following:


filename: /etc/.rclocal

##Start of file

#!/bin/sh -e



sleep 30
mbimcli --device=/dev/cdc-wdm0 --query-device-caps
mbim-network /dev/cdc-wdm0 start
mbimcli -d /dev/cdc-wdm0 -p --query-ip-configuration





ip link set dev wwan0 up
ip addr add 212.27.2.243/29 dev wwan0
sudo ip route add default via 212.27.2.244 dev wwan0
sudo ip route add 172.16.0.0/12 via 172.16.100.1
exit 0

#End of file

This starts the modem with mbim and adds required routes 30 seconds after boot.

Will also need to do the same if it fails.
Can be done with:

Script that pings 8.8.8.8, if it fails for 5-10-20? consecutive times, run script to restart the mbim-network and re-add routes if required. 

