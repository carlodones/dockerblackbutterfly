#!/usr/bin/env python3
import ntplib
from time import ctime
c = ntplib.NTPClient()
response = c.request('it.pool.ntp.org')
print(ctime(response.tx_time))


