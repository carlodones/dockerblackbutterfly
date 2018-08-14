#!/bin/bash

# Start sshd if we don't use the init system
if [ "$INITSYSTEM" != "on" ]; then
  /usr/sbin/sshd -p 22 &
fi

echo "This is where your application would start..."

python /usr/src/app/src/hello.py

#while : ; do
#  echo "waiting"
#  sleep 60
#done
