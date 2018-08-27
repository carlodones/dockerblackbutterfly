import os
import sys
import time
import ntplib
import mod_log
from time import ctime

class NTPManager(object):
    def __init__(self, log_mgr, service_url):
        self.service_url = service_url
        self.log_mgr = log_mgr

        self.ntp_client = ntplib.NTPClient()
        self.log_mgr.info(self.__class__.__name__, "NTPManager initialized: service_url=<" + str(self.service_url) + ">", 2)
        pass

    # Calculate single average measure from single channel
    def ntp_sync(self):

        try:
            response = None
            self.log_mgr.info(self.__class__.__name__, "NTP Sync", 2)
            response = self.ntp_client.request(self.service_url)
            current_time = ctime(response.tx_time)

            self.log_mgr.info(self.__class__.__name__, "Updating system clock:<" + str(current_time) + ">", 2)
            #os.system("sudo service ntp stop")
            os.system("sudo date -s '{0}'".format(current_time))
            #os.system("sudo service ntp start")
        except Exception as ex:
            self.log_mgr.info(self.__class__.__name__, "NTP Sync error:<" + str(ex) + ">", 1)

        pass

    def close(self):
        self.log_mgr = None
        self.service_url = None
        self.ntp_client

# #!/usr/bin/env python3
# import time
# import ntplib
# import mod_log
# from time import ctime
# import os

# c = ntplib.NTPClient()
# class NTPManager(object):
#     def __init__(self, log_mgr, service_url):
#         self.service_url = service_url
#         self.log_mgr = log_mgr
#         self.log_mgr.info(self.__class__.__name__, "NTPManager initialized", 2)
#         pass

#     def ntp_sync(self):              
#         try:
#             response = c.request(self.service_url)
#             current_time = ctime(response.tx_time)           
#             os.system("sudo service ntp stop")
#             os.system("sudo date -s '{0}'".format(current_time))
#             os.system("sudo service ntp start")
#         except:
#             self.log_mgr.info(self.__class__.__name__, "server error", 1)     
# pass 
