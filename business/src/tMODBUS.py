# #!/usr/bin/env python3
# import time
# import minimalmodbus
# import numpy as np

# minimalmodbus.BAUDRATE = 57600

# # port name, slave address (in decimal)
# instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

# #counter = 5
# def modbus(self, counter):
#     while counter:
#         #global counter 
#         # Register number, number of decimals, function code
#         temperature = instrument.read_registers(2, 8, 3) 
#         # Registeraddress, numberOfDecimals=0, functioncode=3, signed=False
#         pressure = instrument.read_register(self.channel, 3, 3, True)       
#         #NumPy int 16 su lista
#         temperature = np.int16(temperature)
#         #pressure = np.int16(pressure)
#         #print (temperature)
#         #print (pressure)
#         time.sleep(1)
#         counter -= 1
#     return pressure

# #if __name__ == '__main__':
# #
# #    Modbus.modbus(0, 5)
