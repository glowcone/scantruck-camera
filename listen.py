# Server program
from socket import *
import time
import sys
import imageCapture
from datetime import datetime
import subprocess
import os

def main(*args):
	captureEnable = 1
	# Set the socket parameters
	port = 5764
	host = ""
	send_port = 5765
		
	if len(args) > 0:
		if len(args[0]):
			port = int(args[0][0])
		
			if len(args[0]) > 1:
				host = args[0][1]
				
	print('port:', port)
	print('host:', host)
	
	buf = 2048
	addr = (host,port)
	send_addr = ("192.168.27.222",send_port)
	# Create socket and bind to address
	udp_listen_sock = socket(AF_INET,SOCK_DGRAM, IPPROTO_UDP)
	udp_listen_sock.bind(addr)

	udp_send_sock = socket(AF_INET,SOCK_DGRAM, IPPROTO_UDP)

	try:
		imageCapture.killgphoto2process()
	except:
		print('unable to kill process')

	# Receive messages
	while 1:
		data,addr = udp_listen_sock.recvfrom(buf)
		print('received: ', data, addr)
		data = data.decode('UTF-8')
		splits = data.split(' ')
		if splits[0] in ['capture']:
			if captureEnable == 1:
				try:
					#print('calling captureImage()')
					imageCapture.captureImage(str(time.time()))
					udp_listen_sock.sendto("1".encode('utf-8'), addr)
				except Exception as e:
					print(e)
		elif splits[0] in ['getBatch']:
				imageCapture.getImageBatch()
				udp_listen_sock.sendto("1".encode("utf-8"),addr)
		if splits[0] in ['enable']:
			print('Capture Enabled')
			captureEnable = 1
		if splits[0] in ['disable']:
			print('Capture Disabled')
			captureEnable = 0				
		if splits[0] in ['sync']:
			p = subprocess.Popen(['sudo', 'sntp', '-s', '192.168.27.222'], stdout=subprocess.PIPE)
			out, err = p.communicate()
			print(out)
			if err:
				print(err)
			print(p)
		elif splits[0] in ['rsync']:
			try:
				print('Focusing camera')
				imageCapture.rsync()
				print("images synced")
			except:
				print('unable to sync images')
		elif splits[0] in ['setsharemountpath']:
			try:
				print('setting share mount path to: ', splits[1])
				imageCapture.setShareMountPath(splits[1])
				print("share mount path set")
			except:
				print('unable to set share mount path')
		elif splits[0] in ['--set-config']:
			try:
				print('Splits', splits[0], splits[1])
				imageCapture.setconfig(splits[1])
			except:
				print('unable to set configuration')
			print("configuration set")
		elif splits[0] in ['delpiimages']:
			try:
				imageCapture.delPiImages()
			except:
				print('unable to delete files')
			print("files deleted")
		elif splits[0] in ['focusCamera']:
			try:
				print('Focusing camera')
				imageCapture.focusCamera()
				print("camera focused")
			except:
				print('unable focus camera')
		elif splits[0] in ['clientstop']:
			print("Client has exited!")
			break
		elif splits[0] in ['clearimages']:
			try:
				imageCapture.clearImages()
			except:
				print('unable to kill process')
			print("image clear finished")
		elif splits[0] in ['killgphoto', 'gphoto', 'kg']:
			try:
				imageCapture.killgphoto2process()
			except:
				print('unable to kill process')
			print('kill gphoto')
		elif splits[0] in ['status']:
			try:
				cmd = "sudo gphoto2 --auto-detect"
				ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				output = ps.communicate()[0]
				camera_status = str('usb' in output.decode('utf-8'))
				#print(camera_status)

				cmd = "pgrep -af python"
				ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				output = ps.communicate()[0]
				proc_status = str('listen.py' in output.decode('utf-8')) + ':' +  str('clientExecute.py' in output.decode('utf-8'))
				#print(proc_status)

				cmd = "mount | cut -f 1,3 -d ' '"
				ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				output = ps.communicate()[0]
				mount_status = str('//192.168.27.223/share /home/pi/Desktop/gphoto/imageshare' in output.decode('utf-8'))
				#print(mount_status)

				image_count = str(len([name for name in os.listdir('.') if os.path.isfile(name)]))
				#print(image_count)
				
				status = camera_status + ':' + proc_status + ':' + mount_status + ':' + image_count
				udp_send_sock.sendto(status.encode(), send_addr)
				#print(status)
			except:
				print('unable to get status')

		else:
			print('Unrecognized command')
			try:
				print('Unrecognized command')
			except Exception as e:
				print(e)
	
	# Close socket
	udp_listen_sock.close()
	udp_send_sock.close()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		main(sys.argv[1:])
	else:
		main()

