#!/usr/bin/env python3
# coding=utf-8
import time
import mod_log
import mod_measure_list
import minimalmodbus
import numpy as np

# port name, slave address (in decimal)
#instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

# Array dei canali 
channels = []
exit_flag = False
calib_temp = None

modbus = None

class SenecaManager(object):
    def __init__(self, log_mgr, channel, source_channel, port_id, baudrate_set, parity_set, bytesize_set, stopbits_set):
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
        self.instrument = minimalmodbus.Instrument(port_id, 1)
        self.log_mgr.info(self.__class__.__name__, "SenecaManager initialized", 2)

    # Acquire single measure from single channel
    def read_channel(self):

        val = None

        # Get timestamp
        ts = time.time()
        
        # Acquiring from Seneca channels sensors: 
        #if(self.channel == 7):
        val = float(self.instrument.read_register(self.channel, self.source_channel, 3, True))
        #elif(self.channel == 8):
        #    val = float(self.instrument.read_register(self.channel, 4, 3, True))
        #else:
        #    val = float(self.instrument.read_register(self.channel, 5, 3, True))
#
        meas_sh = mod_measure_list.Measure(self.channel, val, ts)

        return meas_sh

    def get_name(self):
        return self.name


