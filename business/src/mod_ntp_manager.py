#!/usr/bin/env python3
import time
import ntplib
import mod_log
from time import ctime
import os

c = ntplib.NTPClient()
class NTPManager(object):
    def __init__(self, log_mgr, service_url):
        self.service_url = service_url
        self.log_mgr = log_mgr
        self.log_mgr.info(self.__class__.__name__, "NTPManager initialized", 2)
        pass

    def ntp_sync(self):              
        try:
            response = c.request(self.service_url)
            current_time = ctime(response.tx_time)           
            os.system("sudo service ntp stop")
            os.system("sudo date -s '{0}'".format(current_time))
            #os.system("sudo service ntp start")
        except:
            self.log_mgr.info(self.__class__.__name__, "server error", 1)     
            pass  
