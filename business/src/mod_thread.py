import threading
import time
import mod_log
import mod_measure_list
import mod_json

class ThreadException(Exception):
    ''' Exception for configuration error '''
    pass

# Threads management class
class ThreadManager(object):

    def __init__(self, log_mgr, thread_type):
        self.log_mgr = log_mgr              # Logger module
        self.thread_type = thread_type      # Thread type: ACQ = acquisition, CFG = config update, MQTT = mqtt
        self.thread_configured = False      # True when right configuration method has been called
        self.thread_id = None               # Thread unique identifier

        self.exit_flag = False              # Thread termination flag
        self.stopped_flag = False           # Thread stopped flag

        self.exit_check_delay = 5           # Check thread exit each 5 seconds
        self.exit_check_count = 1

    # Start thread configuration
    def thread_start_config(self, thread_type=None, thread_id=None):

        self.log_mgr.info(self.__class__.__name__, "Initializing thread type:<" + str(self.thread_type) + ">; <" + str(thread_id) + ">", 1)

        if (self.thread_type != thread_type):
            raise ThreadException("Mis-configured thread type:<" + str (self.thread_type) + ">", 1)

    # End thread configuration
    def thread_end_config(self, thread_id=None):

        self.thread_id = thread_id
        self.thread_configured = True

        if (self.delay >= self.exit_check_delay):
            self.exit_check_count = int(self.delay / self.exit_check_delay)
            self.exit_check_delay = float(self.delay / self.exit_check_count)

        self.log_mgr.info(self.__class__.__name__, "Check delay:<" + str(self.exit_check_delay) + ">; count:<" + str(self.exit_check_count) + ">", 2)
        self.log_mgr.info(self.__class__.__name__, "Initialized thread type:<" + str(self.thread_type) + ">; <" + str(thread_id) + ">", 1)

    # Set values for acquisition thread params
    def acq_thread_params(self, channel, delay, source_mgr, measure_list):

        self.thread_id = str(source_mgr.get_name()) + "-" + str(channel)
        self.thread_start_config("ACQ", self.thread_id)

        self.channel = channel              # Acquisition channel
        self.delay = delay                  # Sampling time (sec.)
        self.source_mgr = source_mgr        # source_mgr: board (sense_hat, seneca) / calc (average, etc.)
        self.measure_list = measure_list    # Measure internal list

        self.thread_end_config(self.thread_id)

    # Set values for configuration update check thread params
    def cfg_thread_params(self, mod_cfg, delay):

        self.thread_id = "config"
        self.thread_start_config("CFG", self.thread_id)

        self.mod_cfg = mod_cfg              # Configuration management module
        self.delay = delay                  # Sampling time (sec.)
        
        self.thread_end_config(self.thread_id)

    # Set values for configuration update check thread params
    def json_thread_params(self, delay, json_manager):

        self.thread_id = "json"
        self.thread_start_config("JSON", self.thread_id)

        self.delay = delay                  # Send / Receive time (sec.)
        self.json_manager = json_manager    # JSON manager
        
        self.thread_end_config(self.thread_id)

    # Set values for configuration update check thread params
    def mqtt_thread_params(self, delay, mqtt_manager):

        self.thread_id = "mqtt"
        self.thread_start_config("MQTT", self.thread_id)

        self.delay = delay                  # Send / Receive time (sec.)
        self.mqtt_manager = mqtt_manager    # MQTT manager
        
        self.thread_end_config(self.thread_id)

    # Set values for configuration update check thread params
    def ntp_thread_params(self, delay, ntp_manager):

        self.thread_id = "ntp"
        self.thread_start_config("NTP", self.thread_id)

        self.delay = delay                  # Send / Receive time (sec.)
        self.ntp_manager = ntp_manager      # NTP manager
        
        self.thread_end_config(self.thread_id)


    # Start thread
    def start_thread(self):
        if (self.thread_configured == False):
            raise ThreadException("Mis-configured thread type:<" + str(self.thread_type) + ">; <" + str(self.thread_id) + ">", 1)

        self.mgmt_thread = threading.Thread(target = self.thread_core)
        self.mgmt_thread.start()

    # Thread definition
    def thread_core(self):
        self.log_mgr.info(self.__class__.__name__, "Started thread type:<" + str(self.thread_type) + ">; id:<" + str(self.thread_id) + ">", 1)
        self.stopped_flag = False

        counter = 0
        action = False
        while (self.exit_flag == False):

            # Check every second if exit_flag was set to True
            if (self.delay >= self.exit_check_delay):
                if(counter == self.exit_check_count):
                    counter = 0
                    action = True
                else:
                    counter = counter + 1
                    action = False
            else:
                action = True

            if (action == True):
                # Perform cyclical action
                if (self.thread_type == "MQTT"):
                    self.mqtt_manager.manage_message()
                elif (self.thread_type == "CFG"):
                    self.mod_cfg.load_config()
                elif (self.thread_type == "ACQ"):
                    self.measure_list.add_measure(self.source_mgr.read_channel())
                elif (self.thread_type == "JSON"):
                    self.json_manager.create_collection()
                elif (self.thread_type == "NTP"):
                    self.ntp_manager.ntp_sync()
                else:
                    self.exit_flag = True

            if (self.delay >= self.exit_check_delay):
                time.sleep(self.exit_check_delay)
            else:
                time.sleep(self.delay)

        self.log_mgr.info(self.__class__.__name__, "Stopped thread type:<" + str(self.thread_type) + ">; id:<" + str(self.thread_id) + ">", 1)
        self.stopped_flag = True

    # Stop thread
    def stop_thread (self):
        self.log_mgr.info(self.__class__.__name__, "Stopping thread type:<" + str(self.thread_type) + ">; id:<" + str(self.thread_id) + ">", 1)
        self.exit_flag = True

    def close(self):
        self.delay = None

        # Perform cyclical action
        if (self.thread_type == "MQTT"):
            self.mqtt_manager.close()

        elif (self.thread_type == "CFG"):
            self.mod_cfg = None

        elif (self.thread_type == "JSON"):
            self.json_manager = None

        elif (self.thread_type == "ACQ"):
            self.channel = None
            self.measure_list = None
            self.source_mgr.close()

        elif (self.thread_type == "NTP"):
            self.ntp_manager.close()

        else:
            self.exit_flag = True

    def stopped_thread(self):
        return self.stopped_flag

    def get_id(self):
        return self.thread_id

    def get_type(self):
        return self.thread_type

    