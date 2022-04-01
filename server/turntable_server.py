from socket import *
import signal
import sys
from datetime import datetime
import subprocess
import os

PORT = 3000
BUFFER_SIZE = 2048

udp_listen_sock = socket(AF_INET,SOCK_DGRAM, IPPROTO_UDP)

def turn():
	return 0

def begin_turn():
	return 0

def end_turn():
	return 0

def send_message(address, message):
	sock.sendto(message.encode('utf-8'), addr)

def main():
	udp_listen_sock.bind(("", PORT))
	while True:
		data,addr = udp_listen_sock.recvfrom(BUFFER_SIZE)
		print('received: ', data, addr)
		data = data.decode('UTF-8')
		splits = data.split(' ')
		if splits[0] == 'turn':
			turn(splits[1])
			send_message(addr, 'success')
		elif splits[0] == 'begin_turn':
			begin_turn()
		elif splits[0] == 'end_turn':
			end_turn()

if __name__ == "__main__":
	main()
