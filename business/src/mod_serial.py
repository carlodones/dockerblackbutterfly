import serial
import minimalmodbus

minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True

class SerialPortException(Exception):
    ''' Exception for configuration error '''
    pass

# Creates and manager a minimalmodbus "instruments" dictionary
class SerialManager(object):
    def __init__(self, log_mgr):

        self.dict_serial_ports = {}
        self.sp_baudrates = [9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
        self.log_mgr = log_mgr

    # Creates a new instrument
    def add_instrument(self, s_port_idx, s_port_name, s_modbus_adr, s_baudrate_set, s_parity_set, s_bytesize_set, s_stopbits_set):

        self.modbus_addr = int(s_modbus_adr)
        self.port_name = s_port_name
        self.port_idx = int(s_port_idx)

        # Modbus Baudrate
        minimalmodbus.BAUDRATE = self.set_baudrate(s_baudrate_set)
        """Default value for the baudrate in Baud (int)."""
        minimalmodbus.PARITY   = self.set_parity(s_parity_set)
        """Default value for the parity. See the pySerial module for documentation. Defaults to serial.PARITY_NONE"""
        minimalmodbus.BYTESIZE = int(s_bytesize_set)
        """Default value for the bytesize (int)."""
        minimalmodbus.STOPBITS = int(s_stopbits_set)
        """Default value for the number of stopbits (int)."""

        # Create new instrument instance
        instrument = minimalmodbus.Instrument(self.port_name, self.modbus_addr)

        # Add serial port to internal dictionary
        self.dict_serial_ports.update({self.port_idx: instrument})

    # Retrieves a specific instrument given its index
    def get_instrument(self, idx):
        if(idx == -1):
            return None
        if(self.dict_serial_ports.has_key(idx) == False):
            raise SerialPortException( \
                "Serial Port Error - No instruments found at index:<" + str(idx) + ">")
        return self.dict_serial_ports.get(idx)

    # Sets serial port parity
    def set_parity(self, s_parity_set):
        s_parity_set = s_parity_set.capitalize
        if (s_parity_set == "None") :
            parity_set = serial.PARITY_NONE
        elif (s_parity_set == "Even") :
            parity_set = serial.PARITY_EVEN
        elif (s_parity_set == "Odd") :
            parity_set = serial.PARITY_ODD
        else:
            raise SerialPortException( \
                "Serial Port Error - Invalid parity:<" + str(s_parity_set) + ">")
        return parity_set

    # Sets serial port baudrate
    def set_baudrate(self, s_baudrate_set):
        baudrate_set = int(s_baudrate_set)
        for br in self.sp_baudrates:
            if (baudrate_set == br):
                return baudrate_set

        raise SerialPortException( \
            "Serial Port Error - Invalid baudrate:<" + str(s_baudrate_set)+ ">")
        
        