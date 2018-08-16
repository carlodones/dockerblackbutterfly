#!/bin/bash

# Start sshd if we don't use the init system
if [ "$INITSYSTEM" != "on" ]; then
  /usr/sbin/sshd -p 22 &
fi

# Set timezone to Europe/Rome
#timedatectl set-timezone Europe/Rome

# Start python script
python /usr/src/app/src/ntp1.py


