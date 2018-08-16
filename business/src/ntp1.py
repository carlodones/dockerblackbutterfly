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
#os.system('/etc/init.d/ntpd stop, /usr/sbin/ntpdate -b -s it.pool.ntp.org, /etc/init.d/ntpd start')
current_time = ctime(response.tx_time)
os.system("sudo date -s '{0}'".format(current_time))
#self.logger.info('Raptor rozpoczal prace: {0}'.format(current_time))

'''

def set(self):
        try:
            c = ntplib.NTPClient()
            response = c.request('europe.pool.ntp.org', version=3)
            current_time = ctime(response.tx_time)
            # current_time = 'Sun Apr 09 21:15:06 2017'
            os.system("sudo date -s '{0}'".format(current_time))
            self.logger.info('Raptor rozpoczal prace: {0}'.format(current_time))

        except Exception as ex:
            self.logger.error('OsTime: {0}'.format(ex))
            pass 

'''