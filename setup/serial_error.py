import logging, pexpect, time, re, sys, subprocess, os
from versa_variables import *
global device_completed, hosts_path, timestr



####################################################################################
############################# Variables you can change #############################
####################################################################################


#hosts_path = "/root/.ssh/known_hosts"
#image_filename = "versa-flexvnf-20220420-131241-eca39c5-21.1.4-wsm.bin"


####################################################################################
#################################### DONT TOUCH ####################################
####################################################################################

device_completed = False
hostname = "172.16.101.1"
username = "admin"
password = "versa123"
prompt = "\$"

logger = logging.getLogger('port_1_logger')
logger.setLevel(logging.DEBUG)
level = logging.DEBUG
fh = logging.FileHandler(f"/home/solar/versa_upgrade/log/{hostname}.log")
fh.setLevel(logging.DEBUG)
fmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=level, format=fmt)
logger.addHandler(fh)

class Versa:
    def __init__(self, serial_number, release, package_id, release_date, vsh_details, package_folder, vsh_status, show_interfaces):
        self.serial_number = serial_number
        self.release = release
        self.package_id = package_id
        self.release_date = release_date
        self.vsh_details = vsh_details
        self.package_folder = package_folder
        self.vsh_status = vsh_status
        self.show_interfaces = show_interfaces

class VersaAttributes:
    def __init__(self, ch):
        self.ch = ch

    def versa_parse_output(self, ch, command, matching_string):
        output = VersaConnect.send_and_expect(self, ch, command, prompt)
        variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", output)
        return variable_get[0]

    
class VersaConnect:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

    def send_and_expect(self, ch, send, expect):
        ch.sendline(send)
        ch.expect([expect, pexpect.EOF, pexpect.TIMEOUT])
        output = ch.before.decode()
        return output

    def cli_send_and_expect(self, ch, send):
        VersaConnect.send_and_expect(self, ch, "cli", "cli>")
        output = VersaConnect.send_and_expect(self, ch, send, "cli>")
        VersaConnect.send_and_expect(self, ch, "exit", prompt)
        return output

    def upgrade(self):
        try:
            ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
            ch.logfile = sys.stdout.buffer
            ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
            VersaConnect.send_and_expect(self, ch, password, prompt)
            VersaConnect.send_and_expect(self, ch, "cli", "cli>")
            VersaConnect.send_and_expect(self, ch, f"request system package upgrade {image_filename}", "[no,yes]")
            VersaConnect.send_and_expect(self, ch, "yes", "cli>")
            return True
        except:
            return False

    def login(self):
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        session_callback = ch.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'assword:', 'Connection refused', prompt] )
        if session_callback == 0:
            VersaConnect.die(self, ch, 'ERROR!\nSSH timed out. Here is what SSH said:' )
            return False
        elif session_callback == 1:
            VersaConnect.die(self, ch, 'ERROR!\nSSH had an EOF error, here is what it said:' )
            return False
        elif session_callback == 2:
            VersaConnect.send_and_expect(self, ch, 'yes', 'assword:')
            VersaConnect.send_and_expect(self, ch, password, prompt)
            return True
        elif session_callback == 3:
            VersaConnect.send_and_expect(self, ch, password, prompt)
            try:
                VersaConnect.login.serial_number = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Serial number")
                VersaConnect.login.release = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Release")
                VersaConnect.login.package_id = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Package id")
                VersaConnect.login.release_date = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Release date")
                VersaConnect.login.vsh_details = VersaConnect.send_and_expect(self, ch, 'vsh details', prompt)
                VersaConnect.login.package_folder = VersaConnect.send_and_expect(self, ch, 'ls /home/versa/packages', prompt)
                VersaConnect.send_and_expect(self, ch, 'vsh status', "admin:")
                VersaConnect.login.vsh_status = VersaConnect.send_and_expect(self, ch, password, prompt)
                VersaConnect.login.show_interfaces = VersaConnect.cli_send_and_expect(self, ch, 'show interfaces brief | tab | nomore')
                return True
            except:
                VersaConnect.die(self, ch, 'ERROR! Unable to get any readable output from vsh details/status:' )
                    
                
                return False
        elif session_callback == 4:
            time.sleep(0.5)
            return False
        else:
            time.sleep(0.5)
            return False

    def upload(self):
        try:
            cmd = f'sshpass -p {password} scp -o StrictHostKeyChecking=no /home/solar/versa_upgrade/{image_filename} {username}@{hostname}:/home/versa/packages/'
            output = subprocess.check_output(cmd, shell=True)
            logger.info(output)
            return True
        except:
            return False

    def die(self, child, errstr):
        logger.error("Started DIE function")
        #logger.error(child)
        with open("port_1.output", 'a') as f:
            logger.error(errstr)
            logger.info(child.before)
            logger.info(child.after)
        child.terminate()


def main():

    device_completed = False
    try:
        os.remove(hosts_path)
    except:
        logger.info(f"Unable to delete hosts file, it either does not exist, has the wrong privileges or path: {hosts_path}")

    try:
        while True:
            versa_login = VersaConnect(hostname, username, password)
            if not versa_login.login():
                logger.info("Unable to login, will try again in one minute.")
                time.sleep(60)
            else:
                versa_login.login()
                try:
                    Versa_CPE = Versa(versa_login.login.serial_number, versa_login.login.release, versa_login.login.package_id, versa_login.login.release_date, versa_login.login.vsh_details, versa_login.login.package_folder, versa_login.login.vsh_status, versa_login.login.show_interfaces)
                    
                    if "Stopped" in Versa_CPE.vsh_status:
                        logger.info("Some services have stopped, will try again in 2 minutes.")
                        time.sleep(120)
                    elif "Running" in Versa_CPE.vsh_status:
                        print("started running")
                        logger.info("All services are running")
                        if all(k in image_filename for k in (Versa_CPE.release, Versa_CPE.package_id, Versa_CPE.release_date)):
                            logger.info(f"Device has the correct Version {Versa_CPE.release}")
                            if "WAN1-Transport-VR" in Versa_CPE.show_interfaces:
                                logger.info(f"Device has WAN interface in correct VRF.")
                                logger.info(f"Device with Serial Number {Versa_CPE.serial_number} is completed, will stop script for 10 minutes.")
                                with open(f"/home/solar/versa_upgrade/completed_devices/{Versa_CPE.serial_number}.txt", "w") as f:
                                    f.write(f"Start of file\n {Versa_CPE.serial_number} \n {Versa_CPE.vsh_details} \n {Versa_CPE.vsh_status} \n {Versa_CPE.show_interfaces}\n end of file\n")
                                device_completed = True
                                time.sleep(600)
                            else:
                                logger.error(f"No WAN interface with the WAN1-Transport-VR VRF, will try again after 2 minutes.")
                                time.sleep(120)
                        else:
                            logger.info(f"Device has the wrong version installed: {Versa_CPE.release}")
                            if image_filename in Versa_CPE.package_folder:
                                logger.info(f"Image found in /home/versa/packages/")
                                if not versa_login.upgrade():
                                    logger.error(f"Unable to complete upgrade, will try again in 2 minutes.")
                                    time.sleep(120)
                                else:
                                    logger.info(f"Starting upgrade, waiting 10 minutes.")
                                    time.sleep(600)
                            else:
                                logger.info(f"Image not found in /home/versa/packages, proceeding with upload")
                                if not versa_login.upload():
                                    logger.error(f"Unable to upload image, will try again in 2 minutes.")
                                    time.sleep(120)
                                else:
                                    logger.info(f"{image_filename} uploaded to /home/versa/packages")
                                    time.sleep(5)
                    else:
                        logger.info("Status is not stopped or running")    
                except:
                    logger.info("Variables failed on Versa_CPE")

    except KeyboardInterrupt:
        logger.warning(f"Session has been stopped with Ctrl+C.")
if __name__ == '__main__':
    main()
