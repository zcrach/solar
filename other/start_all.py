import os

for index, i in enumerate(range(10), 1):
    os.system(f'/home/solar/versa_upgrade/monitoring/port_{index}_monitor.sh start')
    