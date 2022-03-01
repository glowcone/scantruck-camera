import sys
from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import shutil
import socket
import fcntl
import struct
import os
from datetime import datetime
from datetime import timedelta

IP_DELAY_TIME = 1000

picID = socket.gethostname()

currentpath = os.path.dirname(os.path.realpath(__file__))
camconfigs = [os.path.join(currentpath, f) for f in os.listdir(currentpath) if f.endswith('.camconfig')]
if not camconfigs:
	campath = "/store_00010001/DCIM/101D3400"
else:
	with open(camconfigs[0], 'r') as conf:
		for line in conf:
			campath = line.strip()
			break
print(picID, campath)
clearCommand = ["--folder", campath, "-R", "--delete-all-files"]
downloadCommand = ["--get-all-files"]

def get_ip_address():
	print('Finding IP address')
	f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
	return f.read()

def captureImage(*args):
    #gp(["--capture-image-and-download", "--filename", args[0] + "." + picID + ".jpg"])
        p = subprocess.Popen(['gphoto2', '--capture-image', '--filename', args[0] + '.' + picID + '.jpg'], stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()

def getImageBatch():
    cmd = ['sudo', 'gphoto2', '--folder', campath, '-R', '-P']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    if p.returncode == 0:
        cmd = ['sudo', 'gphoto2', '--folder', campath, '-R', '-D']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()

def rsync():
	cmd = "mount | cut -f 1,3 -d ' '"
	ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	output = ps.communicate()[0]
	mount_status = str('//192.168.27.223/share /home/pi/Desktop/gphoto/imageshare' in output.decode('utf-8'))
	if mount_status == 'True':
		print('rsync starting...')
		p = subprocess.Popen(['sudo', 'rsync', '-rlptDv', '/home/pi/Desktop/gphoto/images/', '/home/pi/Desktop/gphoto/imageshare', '--log-file=/home/pi/Desktop/gphoto/logs/rsync_log.txt'], stdout=subprocess.PIPE)
		out, err = p.communicate()
		print('rsync complete')

def setShareMountPath(*args):
	print('Creating Directory')
	if not os.path.exists('/home/pi/Desktop/gphoto/imageshare'):
		os.makedirs('/home/pi/Desktop/gphoto/imageshare')
		with open('/etc/fstab', 'a') as myfile:
			myfile.write('//192.168.27.222/images ' + args[0] + ' cifs user=imageshare,password=i2mage#shR,x-systemd.automount 0 0')
			myfile.close()

def delPiImages():
	print('Deleting images on Pi')
	p = subprocess.Popen(['rm -rf *'], shell=True, stdout=subprocess.PIPE)
	out, err = p.communicate()

def ipDelay ():
	print('Calculating delay based on IP address')
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ip_address = get_ip_address()
	print('IP address is:', ip_address)
	octets = ip_address.split('.')
	delay_time = int(octets[3]) * IP_DELAY_TIME
	print('Delay time is:', delay_time, 'ms')
	return delay_time

def focusCamera ():
	ip_delay = ipDelay()
	print('Setting camera to auto focus mode')
	gp(["--set-config", "/main/capturesettings/focusmode2=2"])
	run_at = datetime.now() + timedelta(milliseconds=ip_delay)
	camera_focused = False
	print('Waiting', ip_delay, 'ms')
	while camera_focused == False:
		if datetime.now() >= run_at:
			print('Focusing camera...')
			gp(["--set-config", "/main/actions/autofocusdrive=1"])
			print('Camera focused, now setting the camera back to manual focus')
			gp(["--set-config", "/main/capturesettings/focusmode2=4"])
			camera_focused = True
	print('Done focusing camera')		

def setconfig(setting):
	print('setting ', setting)
	gp("--set-config", setting)

def killgphoto2process ():
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if b'gphoto2' in line:
			#Kill the process!
			pid = int(line.split(None,1)[0])
			os.kill(pid, signal.SIGKILL)

def clearImages():
	gp(clearCommand)

def main(*args):
	print('hello')

if __name__ == "__main__":
	if len(sys.argv) > 1:
		main(sys.argv[:])
	else:
		main()

