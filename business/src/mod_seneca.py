#!/usr/bin/env python3
# coding=utf-8
import time
import mod_log
import mod_measure_list
import minimalmodbus
import numpy as np
import sys

# port name, slave address (in decimal)
#instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

# Array dei canali 
channels = []
exit_flag = False
calib_temp = None

modbus = None

class SenecaManager(object):
    def __init__(self, log_mgr, channel, source_channel, modbus_addr, port_id, baudrate_set, parity_set, bytesize_set, stopbits_set):
        # Modbus Baudrate
        minimalmodbus.BAUDRATE = baudrate_set
        """Default value for the baudrate in Baud (int)."""
        minimalmodbus.PARITY   = parity_set
        """Default value for the parity. See the pySerial module for documentation. Defaults to serial.PARITY_NONE"""
        minimalmodbus.BYTESIZE = bytesize_set
        """Default value for the bytesize (int)."""
        minimalmodbus.STOPBITS = stopbits_set
        """Default value for the number of stopbits (int)."""

        self.log_mgr = log_mgr
        self.channel = channel
        self.source_channel = source_channel
        #self.seneca = Seneca
        self.name = "seneca"
        self.port_id = port_id
        self.modbus_addr = modbus_addr
        self.instrument = minimalmodbus.Instrument(self.port_id, self.modbus_addr)
        self.log_mgr.info(self.__class__.__name__, "SenecaManager initialized", 2)

    # Acquire single measure from single channel
    def read_channel(self):

        val = None
        qos = ""

        # Get timestamp
        ts = time.time()

        #"MQTT_measure_qos": [
        #    { "1": "good", "-1": "bad" }
        #],
        try:
            # Acquiring from Seneca channels sensors: 
            val = float(self.instrument.read_register(self.source_channel, 0, 3, True))
            qos = "good"
        
        except:
            self.log_mgr.info(self.__class__.__name__, "ERROR getting data from device <" + self.modbus_addr + ">" + str(sys.exc_info()[0]), 1)
            val = -999
            qos = "bad"

        print (val)
        meas_sh = mod_measure_list.Measure(self.channel, val, qos, ts)

        return meas_sh

    # Get status register
    def read_status(self):

        status = None
        gE_signal = False
        cE_signal = False
        mE_signal = False

        # Get timestamp
        ts = time.time()

        try:
            # Acquiring from Seneca device: 
            status = float(self.instrument.read_register(2, 0, 3, False))
            
        except:
            self.log_mgr.info(self.__class__.__name__, "ERROR getting data from device <" + self.modbus_addr + ">" + str(sys.exc_info()[0]), 1)
            return 0

        #"MQTT_channel_qos": [
        #    { "1": "DIAGN_STATUS_ONLINE", "0": "DIAGN_STATUS_OFFLINE", "-1": "DIAGN_STATUS_ONLINE_ANOMALY" }
        #],

        if (status & 57344) :
            return -1
        else :
            return 1
        


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


