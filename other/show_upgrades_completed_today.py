import os

print(os.system('ls /home/solar/versa_upgrade/completed_devices/ -altrh --time-style=+%D | grep $(date +%D) | wc -l'))  
