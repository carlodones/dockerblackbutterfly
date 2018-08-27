# coding=utf-8
import sys
import time
import threading
import mod_config
import mod_log
import mod_commands
import mod_measure_list
import mod_json
import mod_thread
import mod_ntp_manager
import mod_mqtt_rcv
import mod_mqtt_snd
import mod_sense_hat
import mod_average
import mod_seneca
import mod_serial

class ServiceClass(object):
    def __init__(self, evn_stop, evn_restart):

        self.evn_restart = evn_restart
        self.evn_stop = evn_stop

        self.thread_list = []
        self.channels = []

        # Instantiate log manager
        self.log_mgr = mod_log.LogManager()
        self.log_mgr.info(self.__class__.__name__, "Initialization", 1)

        # Instantiate measure and channel status lists
        self.measure_list = mod_measure_list.MeasureList()
        self.chstst_list = mod_measure_list.ChannelStatusList()

        # Leggo la configurazione
        self.cfg_mgr = mod_config.ConfigManager(self.log_mgr)
        if (self.cfg_mgr.load_config() == False):
            exit(0)

        self.config_update = self.cfg_mgr.get_config_item_list("config_update")
        self.serial_ports = self.cfg_mgr.get_config_item_list("serial_ports")
        self.channels = self.cfg_mgr.get_config_item_list("channels")
        self.MQTT_flows = self.cfg_mgr.get_config_item_list("MQTT_flows")
        self.ntp_service = self.cfg_mgr.get_config_item_list("ntp_service")
        self.commands = self.cfg_mgr.get_config_item_list("commands")
        self.log = self.cfg_mgr.get_config_item_list("log")

        # Initialize serial ports dictionary
        self.serial_manager = mod_serial.SerialManager(self.log_mgr)

        for lg in self.log:
            backup_log_path = lg.get("backup_log_path")
            log_level = int(lg.get("log_level"))
            self.log_mgr.set_log_config(log_level, backup_log_path)

    def setup_threads(self):

        source_mgr = None
        mqtt_mgr = None
        thd_mgr = None

        self.log_mgr.info(self.__class__.__name__, "Setting-up serial ports", 1)

        for sp in self.serial_ports:

            enabled = True if (sp.get("enabled") == "true") else False
            if (enabled == False):
                continue

            port_idx = sp.get("idx")
            port_name = sp.get("name")
            modbus_addr = sp.get("addr")
            baudrate_set = sp.get("baudrate")                        
            bytesize_set = sp.get("bytesize")
            parity_set = sp.get("parity")
            stopbits_set = sp.get("stopbits")

            self.log_mgr.info(self.__class__.__name__, \
                "Serial Port definition - " + \
                "port_idx:<" + str(port_idx) + ">; " + \
                "port_name:<" + str(port_name) + ">; " + \
                "modbus_addr:<" + str(modbus_addr) + ">; " + \
                "baudrate_set:<" + str(baudrate_set) + ">; " + \
                "bytesize_set:<" + str(bytesize_set) + ">; " + \
                "parity_set:<" + str(parity_set) + ">; " + \
                "stopbits_set:<" + str(stopbits_set) + ">", 1)

            try: # Create serial port manager
                self.serial_manager.add_instrument(port_idx, port_name, modbus_addr, baudrate_set, parity_set, bytesize_set, stopbits_set)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1) 
                continue

        self.log_mgr.info(self.__class__.__name__, "Setting-up acquisition threads", 1)

        for ch in self.channels:

            enabled = True if (ch.get("enabled") == "true") else False
            if (enabled == False):
                continue

            send = True if (ch.get("send") == "true") else False
            channel_type = ch.get("channel_type")
            thread_id = ch.get("channel_id")
            port_idx = int(ch.get("port_idx"))
            channel = int(ch.get("channel"))
            source_channel = int(ch.get("source_channel"))
            delay = float(ch.get("delay_ms")) / 1000
            
            try: # Create serial port manager
                instrument = self.serial_manager.get_instrument(port_idx)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1) 
                continue

            self.log_mgr.info(self.__class__.__name__, \
                "Source definition - " + \
                "send:<" + str(send) + ">; " + \
                "thread_id:<" + str(thread_id) + ">; " + \
                "channel:<" + str(channel) + ">; " + \
                "channel_type:<" + str(channel_type) + ">; " + \
                "delay:<" + str(delay) + ">; " + \
                "source_channel:<" + str(source_channel) + ">", 1)

            # Create an instance of the acquisition manager
            if (channel_type == "sense_hat"):
                source_mgr = mod_sense_hat.SenseManager(self.log_mgr, channel, send)
            if (channel_type == "average"):
                source_mgr = mod_average.AverageManager(self.log_mgr, self.measure_list, channel, source_channel, send)
            if (channel_type == "seneca"):
                source_mgr = mod_seneca.SenecaManager(self.log_mgr, channel, source_channel, send, modbus_addr, instrument)

            try: # Create an instance of the acquisition management thread
                thd_mgr = mod_thread.ThreadManager(self.log_mgr, "ACQ")
                thd_mgr.acq_thread_params(channel, delay, source_mgr, self.measure_list, self.chstst_list)
                self.thread_list.append(thd_mgr)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1) 
                continue

        self.log_mgr.info(self.__class__.__name__, "Setting-up JSON management threads", 1)

        for jc in self.MQTT_flows:

            enabled = True if (jc.get("enabled") == "true") else False
            if (enabled == False):
                continue

            subscription_topic = jc.get("subscription_topic")
            direction = jc.get("direction")
            json_file_path = jc.get("json_file_path")
            delay = float(jc.get("delay_ms")) / 1000

            self.log_mgr.info(self.__class__.__name__, \
                "JSON flow definition - " + \
                "subscription_topic:<" + str(subscription_topic) + ">; " + \
                "direction:<" + str(direction) + ">; " + \
                "json_file_path:<" + str(json_file_path) + ">; " + \
                "delay:<" + str(delay) + ">")

            json_mgr = mod_json.Collection(self.log_mgr, self.cfg_mgr, self.measure_list, direction, subscription_topic, json_file_path)

            try: # Create an instance of the MQTT management thread
                thd_mgr = mod_thread.ThreadManager(self.log_mgr, "JSON")
                thd_mgr.json_thread_params(delay, json_mgr)
                self.thread_list.append(thd_mgr)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1)
                continue

        self.log_mgr.info(self.__class__.__name__, "Setting-up MQTT management threads", 1)

        for fl in self.MQTT_flows:

            enabled = True if (fl.get("enabled") == "true") else False
            if (enabled == False):
                continue

            subscription_topic = fl.get("subscription_topic")
            broker_ip_address = fl.get("broker_ip_address")
            json_file_path = fl.get("json_file_path")
            broker_ip_port = int(fl.get("broker_ip_port"))
            direction = fl.get("direction")
            delay = float(fl.get("delay_ms")) / 1000

            self.log_mgr.info(self.__class__.__name__, \
                "MQTT flow definition - " + \
                "broker_ip_address:<" + str(broker_ip_address) + ">; " + \
                "json_file_path:<" + str(json_file_path) + ">; " + \
                "broker_ip_port:<" + str(broker_ip_port) + ">; " + \
                "subscription_topic:<" + str(subscription_topic) + ">; " + \
                "delay:<" + str(delay) + ">; " + \
                "direction:<" + str(direction) + ">", 1)

            # Create an instance of the mqtt message manager
            if (direction == "in"):
                mqtt_mgr = mod_mqtt_rcv.MqttReceive(delay, self.log_mgr, subscription_topic, broker_ip_address, json_file_path)
            if (direction == "out"):
                mqtt_mgr = mod_mqtt_snd.MqttSend(delay, self.log_mgr, subscription_topic, broker_ip_address, json_file_path)

            try: # Create an instance of the MQTT management thread
                thd_mgr = mod_thread.ThreadManager(self.log_mgr, "MQTT")
                thd_mgr.mqtt_thread_params(delay, mqtt_mgr)
                self.thread_list.append(thd_mgr)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1)
                continue

        self.log_mgr.info(self.__class__.__name__, "Setting-up NTP sync management threads", 1)

        for ntp in self.ntp_service:

            enabled = True if (ntp.get("enabled") == "true") else False
            if (enabled == False):
                continue

            service_url = ntp.get("service_url")
            delay = float(ntp.get("delay_ms")) / 1000

            self.log_mgr.info(self.__class__.__name__, \
                "NTP sync definition - " + \
                "service_url:<" + str(service_url) + ">; " + \
                "delay:<" + str(delay) + ">", 1)

            # Create an instance of the ntp sync manager
            ntp_mgr = mod_ntp_manager.NTPManager(self.log_mgr, service_url)

            try: # Create an instance of the NTP sync thread
                thd_mgr = mod_thread.ThreadManager(self.log_mgr, "NTP")
                thd_mgr.ntp_thread_params(delay, ntp_mgr)
                self.thread_list.append(thd_mgr)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1)
                continue

        self.log_mgr.info(self.__class__.__name__, "Setting-up config update management thread", 1)

        for cup in self.config_update:

            enabled = True if (cup.get("enabled") == "true") else False
            if (enabled == False):
                continue

            commands_path = cup.get("commands_path")
            action = cup.get("action")
            delay = float(cup.get("delay_ms")) / 1000

            self.log_mgr.info(self.__class__.__name__, \
                "Configuration update check - " + \
                "commands_path:<" + str(commands_path) + ">; " + \
                "action:<" + str(action) + ">; " + \
                "delay:<" + str(delay) + ">", 1)

            self.cfg_mgr.configure_action(commands_path, action)

            try: # Create an instance of the Config Update thread
                thd_mgr = mod_thread.ThreadManager(self.log_mgr, "CFG")
                thd_mgr.cfg_thread_params(self.cfg_mgr, delay)
                self.thread_list.append(thd_mgr)
            except Exception as exc: # Thread error
                self.log_mgr.fatal(self.__class__.__name__, "Thread creation exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) + ">", 1)
                continue

    def start_threads(self):

        # Start threads
        for th in self.thread_list:
            self.log_mgr.info(self.__class__.__name__, "Activating thread type:<" + str(th.get_type()) + ">; id:<" + str(th.get_id()) + ">", 1)
            th.start_thread()

        for cmd in self.commands:

            commands_path = cmd.get("commands_path")
            expire_count = int(cmd.get("expire_count"))
            expire_timeout = float(cmd.get("expire_timeout_ms")) / 1000
            delay = float(cmd.get("delay_ms")) / 1000

            self.log_mgr.info(self.__class__.__name__, \
                "CMD check definition - " + \
                "commands_path:<" + str(commands_path) + ">; " + \
                "expire_count:<" + str(expire_count) + ">; " + \
                "expire_timeout:<" + str(expire_timeout) + ">; " + \
                "delay:<" + str(delay) + ">", 1)

        self.log_mgr.info(self.__class__.__name__, "Starting commands mgr", 1)

        # Instantiate and activate the exit manager
        self.exit_mgr = mod_commands.CommandsManager(\
                        self.log_mgr, \
                        self.thread_list, \
                        delay, \
                        expire_timeout, \
                        expire_count, \
                        commands_path, \
                        self.evn_restart, \
                        self.evn_stop)

        self.exit_mgr.start_commands_mgmt()

        self.log_mgr.info(self.__class__.__name__, "Service end", 1)

    def close(self):
        self.log_mgr.info(self.__class__.__name__, "Closing service manager", 1)

        self.evn_restart = None
        self.evn_stop = None

        self.thread_list = None
        self.channels = None

        self.log_mgr.close()
        self.cfg_mgr.close()
        self.measure_list.clear_list()

        self.config_update = None
        self.MQTT_flows = None
        self.ntp_service = None
        self.commands = None
        self.log = None

class MainClass(object):
    def __init__(self):
        self.evn_restart = threading.Event()
        self.evn_stop = threading.Event()

    def service_start(self):

        startup = True
        while (startup == True):
            
            startup = False
            event_set = False

            print("Starting service ...")
            self.service = ServiceClass(self.evn_restart, self.evn_stop)
            self.service.setup_threads()
            self.service.start_threads()
            print("Service Started")

            while(event_set == False):
                if(self.evn_stop.isSet()):
                    event_set = True
                    print("Service Restart")
                elif(self.evn_restart.isSet()):
                    event_set = True
                    startup = True
                    print("Service End")
                
                time.sleep(5)

            self.service.close()
            
            time.sleep(10)

        print("Program End")
                
main = MainClass()
main.service_start()
exit()