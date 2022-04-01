from socket import *
import signal
import sys
from datetime import datetime
import subprocess
import os

IMAGES_DIR = '/home/pi/Desktop/gphoto/images/'
PORT = 3000
BUFFER_SIZE = 2048

udp_listen_sock = socket(AF_INET,SOCK_DGRAM, IPPROTO_UDP)

def capture():
	p = subprocess.Popen(['gphoto2', '--capture-image'], stdout=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()

def delete_camera_all():
	p = subprocess.Popen(['sudo', 'gphoto2', '-R', '-D'], stdout=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()

def copy_camera_all():
	p = subprocess.Popen(['sudo', 'gphoto2', '-R', '-P'], stdout=subprocess.PIPE, cwd=IMAGES_DIR)
	p.wait()
	out, err = p.communicate()

def count_camera_images():
	p = subprocess.Popen(['sudo', 'gphoto2', '--num-files'], stdout=subprocess.PIPE)
	p.wait()
	out, err = p.communicate()
	return out

def count_local_images():
	files = next(os.walk(IMAGES_DIR))[2]
	return len(files)

def delete_local_all():
	p = subprocess.Popen(['rm', '-rf', '*'], stdout=subprocess.PIPE, cwd=IMAGES_DIR)
	p.wait()
	out, err = p.communicate()

def send_message(address, message):
	sock.sendto(message.encode('utf-8'), addr)

def main():
	udp_listen_sock.bind(("", PORT))
	while True:
		data,addr = udp_listen_sock.recvfrom(BUFFER_SIZE)
		print('received: ', data, addr)
		data = data.decode('UTF-8')
		splits = data.split(' ')
		if splits[0] == 'capture':
			capture()
			send_message(addr, 'success')
		elif splits[0] == 'delete_camera_all':
			delete_camera_all()
		elif splits[0] == 'copy_camera_all':
			copy_camera_all()
		elif splits[0] == 'delete_all':
			delete_local_all()
		elif splits[0] == 'count_camera_images':
			send_message(addr, count_camera_images())
		elif splits[0] == 'count_local_images':
			send_message(addr, count_local_images())

if __name__ == "__main__":
	main()
