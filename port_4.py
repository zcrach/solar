import os, logging, pexpect, re, time, subprocess, sys
from datetime import date
from versa_variables import *
#File used to hold hosts file and image file variable. Same directory, named versa_variables.py


#Variable to change ports.1
#If going above port 9, modify hostname. 
port_number = 4
hostname = f"172.16.10{port_number}.1"
username = "admin"
password = "versa123"
prompt = "\$"


def versa_login():
    #Creates the initial SSH session used to gather variables. 
    ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
    #Calls back information based on expect response. 
    session_callback = ch.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'assword:', 'Connection refused', prompt] )
    if session_callback == 0:
        #SSH Timeout
        versa_terminate(ch, 'SSH timed out.' )
        return False
    elif session_callback == 1:
        #SSH Errors (Alternative)
        versa_terminate(ch, 'SSH had an EOF error.' )
        return False
    elif session_callback == 2:
        #SSH with yes/no response, Example: Do you want to accept the hostkey etc...
        send_and_expect(ch, 'yes', 'assword:')
        send_and_expect(ch, password, prompt)
        return True

    elif session_callback == 3:
        #SSH Normal login
        send_and_expect(ch, password, prompt)
        try:
            global versa_sn, versa_release, versa_details, versa_ls, versa_status, versa_interfaces, versa_hwclock
            versa_sn = versa_parse_output(ch, "vsh details", "Serial number")
            versa_release = versa_parse_output(ch, "vsh details", "Release")
            versa_details = send_and_expect(ch, 'vsh details', prompt)
            versa_ls = send_and_expect(ch, 'ls -al /home/versa/packages', prompt)
            send_and_expect(ch, 'vsh status', "admin:")
            versa_status = send_and_expect(ch, password, prompt)
            versa_hwclock = send_and_expect(ch, 'timedatectl', prompt)
            versa_interfaces = cli_send_and_expect(ch, 'show interfaces brief | tab | nomore')
            
            return True
        except:
            return False
    elif session_callback == 4:
        #SSH Connection refused
        time.sleep(0.5)
        return False
    else:
        #Incase anything else is returned. 
        time.sleep(0.5)
        return False


def logging_function(port_number):
    #Function to enable logging in file and terminal. 
    global logger
    logger = logging.getLogger(f'port_{port_number}_logger')
    logger.setLevel(logging.DEBUG)
    level = logging.DEBUG
    fh = logging.FileHandler(f"/home/solar/versa_upgrade/log/port_{port_number}.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] [%(asctime)s]: %(message)s ')
    #Format for logfile
    fh.setFormatter(formatter)
    fmt = '[%(levelname)s] [%(asctime)s]: %(message)s '
    #Format for terminal 
    logging.basicConfig(level=level, format=fmt)
    logger.addHandler(fh)    

def cli_send_and_expect(ch, send):
    #Function used for cli commands, can be re-used for any other cli commands. 
    send_and_expect(ch, "cli", "cli>")
    output = send_and_expect(ch, send, "cli>")
    send_and_expect(ch, "exit", prompt)
    return output

def versa_terminate(child, errstr):
    #Function used to terminate session and print errors received. 
    logger.error(errstr)
    logger.info(child.before)
    logger.info(child.after)
    child.terminate()


def versa_parse_output(ch, command, matching_string):
    #Function used to parse output from vsh details, works for most of the data. 
    output = send_and_expect(ch, command, prompt)
    variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", output)
    try:
        return variable_get[0]
    except:
        return variable_get


def send_and_expect(ch, send, expect):
    #Function to reduce text from send/expect function in pexpect. Send data, wait for expected response or timeout. Return output. 
    ch.sendline(send)
    ch.expect([expect, pexpect.EOF, pexpect.TIMEOUT])
    output = ch.before.decode()
    return output


def versa_ping(response=None):
    #Function to ping the IP address for the port, and return True when reply is received. 
    while response != 0:
        response = os.system("ping -c 1 " + hostname)
    else:
        global versa_sn, versa_release, versa_details, versa_ls, versa_status, versa_interfaces, versa_hwclock
        versa_sn = None
        versa_release = None
        versa_details = None
        versa_ls = None
        versa_status = None
        versa_interfaces = None
        versa_hwclock = None
        return True


def versa_upgrade():
    #Had scenario's where it failed entering cli even with services running, and gave errors. Using Try to just repeat until it works. 
    #Would also break if unplugged during upgrade. 
    try:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.logfile = sys.stdout.buffer
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, "cli", "cli>")
        send_and_expect(ch, f"request system package upgrade {image_filename}", "[no,yes]")
        send_and_expect(ch, "yes", "cli>")
        return True
    except:
        return False
    
    
def versa_reset():
    #Had scenario's where it failed entering cli even with services running, and gave errors. Using Try to just repeat until it works. 
    #Would also break if unplugged during upgrade. 
    try:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.logfile = sys.stdout.buffer
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, "cli", "cli>")
        send_and_expect(ch, f"request system reset", "[no,yes]")
        send_and_expect(ch, "yes", "cli>")
        return True
    except:
        return False


def versa_update_clock():
    #Had scenario's where it failed entering cli even with services running, and gave errors. Using Try to just repeat until it works. 
    #Would also break if unplugged during upgrade. 
    try:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.logfile = sys.stdout.buffer
        today = date.today()
        date_today = today.strftime("%Y-%m-%d")
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, f"sudo timedatectl set-time {date_today}", "admin: ")
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, f"sudo hwclock --systohc", "admin: ")
        send_and_expect(ch, password, prompt)        
        send_and_expect(ch, f"vsh start", "admin: ")
        send_and_expect(ch, password, prompt)   
        return True
    except:
        return False


def versa_failed_upgrade():
    #Had scenario's where it failed entering cli even with services running, and gave errors. Using Try to just repeat until it works. 
    #Would also break if unplugged during upgrade. 
    try:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.logfile = sys.stdout.buffer
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        logger.info(f"Attempting to install image with sudo ./home/versa/packages/{image_filename}")
        send_and_expect(ch, f"sudo /home/versa/packages/{image_filename}", "admin: ")
        send_and_expect(ch, password, prompt)
        logger.info(f"Installation started, Will stop script for 10 minutes, then reboot device.")
        time.sleep(600)
        send_and_expect(ch, f"sudo reboot", "admin: ")
        send_and_expect(ch, password, prompt)        
        return True
    except:
        return False

def versa_upload():
    #Using Try incase upload fails midway or someone unplugs the ethernet cable. Would break if unplugged during upload. 
    try:
        cmd = f'sshpass -p {password} scp -o StrictHostKeyChecking=no /home/solar/versa_upgrade/{image_filename} {username}@{hostname}:/home/versa/packages/'
        output = subprocess.check_output(cmd, shell=True)
        logger.info(output.decode()) #ISSUES#Need to add decode
        return True
    except:
        return False

def versa_hosts_file():
    #When switching device, the hosts file will contain the hostkey <-> IP binding, this will change when changing device.
    #Can either never use SSH key check, or just delete it. I went for deleting it, incase someone are testing something manually.
    #And end up storing a key on the device for one of the IP addresses used. 
    try:
        os.remove(hosts_path)
    except:
        logging.info(f"No file in {hosts_path} to remove")

def versa_shutdown():
    #Engineering DK wanted the function to shutdown the device when it's completed.
    #Had issues here where even if i checked that all services are running, cli would sometimes fail.
    #Just did Try/Expect again to repeat until it works. 
    try:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, "cli", "cli>")
        send_and_expect(ch, f"request system shutdown", "[no,yes]")
        send_and_expect(ch, "yes", "cli>")
        return True
    except:
        return False


def main():
    #Enable logging for the port number used. 
    logging_function(port_number)

    
    try:

        #Note INCLUDING ALOT OF TIME.SLEEP(X) as if it attempts to write the commands too fast, or one check fails it breaks.
        #Tested with the time delay, the upgrade process is a few minutes slower but it's stable. 
        #Alternative is to include alot more checks, but for now this will do. 
        #A check that should be implemented is probably to check /var/log/versa/upgrade.log
        #For image_filanem succeeded. 
        #But i'm not comfortable enough with it working properly, so instead i used a 5 minute timer.
        #Average wait upgrade time when image is uploaded seems to be 2-4 minutes, so i set a 5 minute timer. 

        while True:
            #Ping the device until it gives a reply, then proceed. 
            if not versa_ping():
                logger.info("Ping check failed")
            else:
                logger.info("Ping: Successful")
                #Try to login to the device and collect variables, then proceed. 
                if not versa_login():
                    logger.info("Login failed, will try again in 30 seconds.")
                    versa_hosts_file()
                    time.sleep(30)
                else:
                    logger.info("Login: Successful")
                    try: 
                        #Check if all services are running, then proceed. 
                        for i in range(10):
                            if "Stopped" in versa_status: #Loop here - 10 Attempts over 10 minutes
                                logger.info("Some services have stopped, will try again in 1 minute.")
                                if not versa_update_clock():
                                    logger.info(f"Failed to update clock.")
                                    time.sleep(60)
                                else:
                                    logger.info(f"Successfully updated clock ")
                                    time.sleep(60)
                                break

                            elif "Running" in versa_status:
                                logger.info("All services are running")
                                if versa_release in image_filename:
                                    logger.info(f"SERIAL NUMBER: {versa_sn}")
                                    logger.info(f"{versa_sn} has the right version: {versa_release}")
                                    time.sleep(30)
                                    #Checks if the interfaces have the correct name, if they dont it's either an issue or is not default config. 
                                    for x in range(10):
                                        if "WAN1-Transport-VR" in versa_interfaces:
                                            logger.info(f"Device has WAN interface in correct VRF.")
                                            logger.info(f"Will stop script for 1 minutes, then shutdown device.")
                                            time.sleep(60)
                                            #Shutdown the device when all checks are completed. 
                                            #It saves a file with the serial number of the device to completed_devices/
                                            #I want to seperate these in models, so 350, 730, 750, 770 folders. Can get from parse code.
                                            #For now this will do.
                                            #In the file it's stored:
                                            # vsh details
                                            # vsh status
                                            # cli> show interfaces brief | tab | nomore 
                                            #This will show most of what's necessary.
                                            if not versa_shutdown():
                                                logger.error(f"Unable to shutdown device, will wait 1 minutes.")
                                                time.sleep(60)
                                            else:
                                                logger.info(f"COMPLETED {versa_sn} COMPLETED")
                                                logger.info(f"Device is shutting down, will wait 2 minutes.")
                                                #File creation with vsh details, vsh status and show interfaces under completed/devices. 
                                                with open(f"/home/solar/versa_upgrade/completed_devices/{versa_sn}.log", "w") as f:
                                                    f.write(f"Start of file\n {versa_sn} \n {versa_details} \n {versa_status} \n {versa_interfaces}\n end of file\n")
                                                    logger.info(f"Created file: completed_devices/{versa_sn}.log")
                                                time.sleep(120)
                                            break
                                        else:
                                            #Mostly either delayed start or non-default configuration. Could be "resolved" doing the following:
                                            # Check 2-3 more times, to verify it's not a slow start or read error.
                                            # If process is repeated 3 times and gives same error:
                                            # - Evaluate device model and run appropriate reset function.
                                            # CSG7XX works with cli> request system reset
                                            # CSG350 might require versa factory default script. 
                                            logger.info(f"Device does not have WAN interface in correct VRF.")
                                            logger.info(f"Current loop {i}, waiting 10 seconds and trying again")
                                            time.sleep(10)
                                            
                                            if x == 9:
                                                if not versa_reset():
                                                    logger.info(f"Failed to Reset device to solve WAN interface.")
                                                    time.sleep(10)
                                                else:
                                                    logger.info(f"Successfully Reset device to solve WAN interface, waiting 2 minutes.")
                                                    time.sleep(120)
                                                break
                                
                                else:
                                    #If it's the wrong version, and image is uploaded, start upgrade. 
                                    logger.info(f"{versa_sn} has the wrong version: {versa_release}")

                                    #If it's the wrong version, and image is not uploaded, upload then start upgrade. 
                                    logger.info(f"starting upload of image")
                                    if not versa_upload():
                                        logger.info(f"{versa_sn} Failed to upload {image_filename} to /home/versa/packages")
                                        time.sleep(30)
                                    else:
                                        logger.info(f"{versa_sn} Successfully uploaded {image_filename} to /home/versa/packages")
                                        time.sleep(10)
                                        if not versa_upgrade():
                                            logger.info(f"{versa_sn} Failed to upgrade device with {image_filename}.")
                                            time.sleep(10)
                                        else:
                                            logger.info(f"{versa_sn} Successfully started upgrade of device with {image_filename}.")
                                            logger.info(f"{versa_sn} Waiting 5 minutes for the device to complete upgrade.")
                                            time.sleep(300)
                                        break
                                break
                            else:
                                #vsh not avaiable, usually from trying too fast after reboot / upgrade. Just try again.
                                logger.info("Status is not stopped or running")  
                                logger.info(f"Current loop {i}, waiting 10 seconds and trying again")
                                time.sleep(10)
                                if i == 9:
                                    if not versa_failed_upgrade():
                                        logger.info(f"Upgrade failed.")
                                        time.sleep(10)
                                    else:
                                        logger.info(f"Upgrade successful, rebooting device.")
                                        time.sleep(10)
                                    break
                                
                                


                    except: #Want this to loop 10 minutes - Then force manual upgrade of CPE 
                        #Mostly when trying too fast, when vsh is not avaiable. 
                        logger.info("Unable to get variables, trying again.")
                        if not versa_update_clock():
                            logger.info(f"Failed to update clock.")
                            time.sleep(10)
                        else:
                            logger.info(f"Successfully updated clock ")
                            time.sleep(10)
                        time.sleep(10)
    except KeyboardInterrupt:
        logger.warning(f"Session has been stopped with Ctrl+C.")
if __name__ == '__main__':
    main()
