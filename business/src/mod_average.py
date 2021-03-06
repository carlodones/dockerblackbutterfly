import time
import mod_log
import mod_measure_list

class AverageManager(object):
    def __init__(self, log_mgr, measure_list, channel, source_channel, send):
        self.log_mgr = log_mgr                  # Log manager
        self.measure_list = measure_list        # Measures list
        self.source_channel = source_channel    # Source channel, generating measures for the average
        self.channel = channel                  # Channel
        self.name = "average"                   # Source name
        self.send = send                        # True when measure must be sent by MQTT

        self.flag = mod_measure_list.FLAG()
        
        self.log_mgr.info(self.__class__.__name__, "AverageManager initialized", 2)

    # Calculate single average measure from single channel
    def read_channel(self):

        # Get timestamp
        ts = time.time()
        
        # Calculate average value
        meas_avg = self.measure_list.avg_by_channel(self.channel, self.source_channel, self.send)

        # Erase all source channel measures already used for average calculations and not to be sent
        self.measure_list.clear_by_channel_and_status(self.source_channel, self.flag.FALSE, self.flag.TRUE, self.flag.ALL )

        # Set timestamp
        meas_avg.timestamp = ts

        return meas_avg

    def get_name(self):
        return self.name

    def close(self):
        self.log_mgr = None
        self.measure_list = None
        self.source_channel = None
        self.channel = None

    # For compliancy with abstract class
    def check_exit(self):
        return False