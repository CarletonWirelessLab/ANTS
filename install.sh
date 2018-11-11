#!/usr/bin/bash

# This file creates a symbolic link in /usr/local/bin, allowing ANTS to be run
# from anywhere on the system. It may need to be run as root or with "sudo"

dir=`pwd`
chmod +x ./ants/ants.py
echo "made ants executable"
cd /usr/local/bin
echo "changed directory to /usr/local/bin"
ln -s ${dir}/ants/ants .
echo "made symbolic link"
