#!/usr/bin/env python3
# coding=utf-8
import time
import mod_log
import mod_serial
import minimalmodbus
import mod_measure_list
#import numpy as np
import sys

# port name, slave address (in decimal)
#instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

# Array dei canali 
channels = []
exit_flag = False
calib_temp = None

modbus = None

class SenecaManager(object):
    def __init__(self, log_mgr, channel, source_channel, send, modbus_addr, instrument):

        self.log_mgr = log_mgr
        self.channel = channel
        self.source_channel = source_channel
        self.modbus_addr = int(modbus_addr)
        self.send = send
        self.name = "seneca"
        self.qos = mod_measure_list.QOS()
        self.instrument = instrument

        # self.instrument = minimalmodbus.Instrument(self.serial_settings.port_id, self.modbus_addr)
        self.log_mgr.info(self.__class__.__name__, "SenecaManager initialized", 2)

    # Acquire single measure from single channel
    def read_channel(self):

        val = None
        qos = None

        # Get timestamp
        ts = time.time()

        try: 
            ## "Open serial port if not open": disabled
            # https://minimalmodbus.readthedocs.io/en/master/troubleshooting.html
            
            # if(self.instrument.serial.isOpen() == False):
            #     self.instrument.serial.open()            

            # Acquiring from Seneca channels sensors: 
            val = float(self.instrument.read_register(self.source_channel, 0, 3, True))
            qos = self.qos.ONLINE
        
        except Exception as exc:
            self.log_mgr.info(self.__class__.__name__, "ERROR getting data from device <" + str(self.modbus_addr) + ">; exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) +">", 1)
            val = -999
            qos = self.qos.ANOMALY

        meas_sh = mod_measure_list.Measure(self.channel, val, ts, qos, self.send)

        return meas_sh

    # # Get status register
    # def read_status(self):

    #     status = None
    #     gE_signal = False
    #     cE_signal = False
    #     mE_signal = False

    #     # Get timestamp
    #     ts = time.time()

    #     try:
    #         # Acquiring from Seneca device: 
    #         status = float(self.instrument.read_register(2, 0, 3, False))
            
    #     except Exception as exc:
    #         self.log_mgr.info(self.__class__.__name__, "ERROR getting data from device <" + self.modbus_addr + ">; exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) +">", 1)
    #         return 0

    #     #"MQTT_channel_qos": [
    #     #    { "1": "DIAGN_STATUS_ONLINE", "0": "DIAGN_STATUS_OFFLINE", "-1": "DIAGN_STATUS_ONLINE_ANOMALY" }
    #     #],

    #     if (status & 57344) :
    #         return -1
    #     else :
    #         return 1

    def close(self):
        self.log_mgr.info(self.__class__.__name__, "SenecaManager closed", 2)
        try:
            self.instrument = None
            if(self.instrument.serial.isOpen()):
                self.instrument.serial.close()           
        except Exception as exc:
            self.log_mgr.fatal("Error closing minimalmodbus; exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) +">", 1)
        self.channel = None

    #    Status : 40002
    #        Generic error: Bit 15
    #            0=there isnt; 1=there is
    #        Configuration error: Bit 14
    #            0=there isnt; 1=there is
    #        Memory error (EEPROM): Bit 13
    #            0=there isnt; 1=there is

        return 

    def get_name(self):
        return self.name


