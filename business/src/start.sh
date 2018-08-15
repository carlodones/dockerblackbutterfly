#!/bin/bash

# Start sshd if we don't use the init system
if [ "$INITSYSTEM" != "on" ]; then
  /usr/sbin/sshd -p 22 &
fi

# Default to UTC if no TIMEZONE env variable is set

echo "Setting time zone to ${TIMEZONE=CEST}"

# This only works on Debian-based images

echo "${Europe/Paris}" > /etc/timezone
dpkg-reconfigure tzdata


echo "This is where your application would start..."

python /usr/src/app/src/hello.py

#while : ; do
#  echo "waiting"
#  sleep 60
#done
