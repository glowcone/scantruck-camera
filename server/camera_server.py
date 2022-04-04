from socket import *
import signal
import sys
from datetime import datetime
import subprocess
import os

IMAGES_DIR = '/home/pi/server/images/'
PORT = 3000
BUFFER_SIZE = 2048

udp_listen_sock = socket(AF_INET,SOCK_DGRAM, IPPROTO_UDP)

def capture():
        now = datetime.now()
        p = subprocess.Popen(['gphoto2', '--capture-image-and-download', '--filename', IMAGES_DIR+now.strftime("%d-%m-%Y_%H-%M-%S")+ '.jpg'], stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        return out

def delete_camera_all():
        p = subprocess.Popen(['sudo', 'gphoto2', '-R', '-D'], stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        return out

def copy_camera_all():
        p = subprocess.Popen(['sudo', 'gphoto2', '-R', '-P'], stdout=subprocess.PIPE, cwd=IMAGES_DIR)
        p.wait()
        out, err = p.communicate()
        return out

def count_camera_images():
        p = subprocess.Popen(['sudo', 'gphoto2', '--num-files'], stdout=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        return out

def count_local_images():
        files = next(os.walk(IMAGES_DIR))[2]
        return len(files)

def delete_local_all():
        for filename in os.listdir(IMAGES_DIR):
                file_path = os.path.join(IMAGES_DIR, filename)
                try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                except:
                        pass

def send_message(address, message):
        udp_listen_sock.sendto(str(message).encode(), address)

def main():
	udp_listen_sock.bind(("", PORT))
	while True:
		data,addr = udp_listen_sock.recvfrom(BUFFER_SIZE)
		print('received: ', data, addr)
		data = data.decode()
		splits = data.split(' ')
		if splits[0] == 'capture':
			send_message(addr, capture())
		elif splits[0] == 'delete_camera_all':
			send_message(addr, delete_camera_all())
		elif splits[0] == 'copy_camera_all':
			send_message(addr, copy_camera_all())
		elif splits[0] == 'delete_all':
			delete_local_all()
                        send_message('Deleted')
		elif splits[0] == 'count_camera_images':
			send_message(addr, count_camera_images())
		elif splits[0] == 'count_local_images':
			send_message(addr, count_local_images())

if __name__ == "__main__":
	main()
