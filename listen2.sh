#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python scrip$

cd /home/pi/Desktop/gphoto/images
sudo python3 /home/pi/Desktop/gphoto/listen.py &
