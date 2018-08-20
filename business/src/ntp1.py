#!/usr/bin/env python3
import ntplib
import os
import mod_log

from time import ctime
c = ntplib.NTPClient()
response = c.request('it.pool.ntp.org')
print (response.offset)
print (response.version)
print (ctime(response.tx_time))
print (ntplib.leap_to_text(response.leap))
print (response.root_delay)
print (ntplib.ref_id_to_text(response.ref_id))

print(ctime(response.tx_time))
print(ntplib.system_to_ntp_time)

#print (os.system)

current_time = ctime(response.tx_time)
print (current_time)
os.system("service ntp stop")
os.system("sudo date -s '{0}'".format(current_time))
os.system("sudo service ntp start")