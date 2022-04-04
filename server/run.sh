#!/bin/sh
cd /home/pi/server/images
while true ; do
	sudo python3 /home/pi/server/scantruck-camera/server/camera_server.py
done
