import mod_log
import os
import mod_measure_list

class ConfigurationException(Exception):
    ''' Exception for configuration error '''
    pass

# List of managed configuration dictionaries
class ConfigValidation():
    def __init__(self, log_mgr):

        self.log_mgr = log_mgr
        self.qos = mod_measure_list.QOS()

        self.config_keys = { \
        "config_update": { \
            "enabled": "boolean", \
            "delay_ms": "number", \
            "commands_path": "path", \
            "action": "string" },
        "device": { \
            "device_name": "string", \
            "device_ip": "ip_address" },
        "channels": { \
            "enabled": "boolean", \
            "channel_type": "board", \
            "send": "boolean", \
            "channel_id": "string", \
            "name": "string", \
            "channel": "number", \
            "source_channel": "number", \
            "port_idx": "number", \
            "delay_ms": "number", \
            "upper_limit": "number", \
            "lower_limit": "number" },
        "serial_ports": { \
            "enabled": "boolean", \
            "idx": "number", \
            "addr": "number", \
            "name": "string", \
            "baudrate": "number", \
            "parity": "string", \
            "bytesize": "number", \
            "stopbits": "number" },
        "MQTT_flows": { \
            "enabled": "boolean", \
            "broker_ip_port": "number", \
            "broker_ip_address": "string", \
            "subscription_topic": "string", \
            "delay_ms": "number", \
            "direction": "string", \
            "json_file_path": "path" },
        "MQTT_keys": { \
            "payload": "string", \
            "address": "string", \
            "qos": "string", \
            "values": "string", \
            "timestamp": "string" },
        "MQTT_measure_qos": { \
            str(self.qos.ANOMALY): "string", \
            str(self.qos.ONLINE): "string" },
        "MQTT_channel_qos": { \
            str(self.qos.OFFLINE): "string", \
            str(self.qos.ONLINE): "string", \
            str(self.qos.ANOMALY): "string" },
        "log": { \
            "backup_log_path": "path", \
            "log_level": "number" }, \
        "ntp_service": { \
            "enabled": "boolean", \
            "service_url": "string", \
            "delay_ms": "number" },
        "commands": { \
            "delay_ms": "number", \
            "expire_timeout_ms": "number", \
            "expire_count": "number", \
            "commands_path": "path" }
        }
        pass

    # Validate single key
    def validate_key(self, key_name, param_value, param_type):

        self.log_mgr.info(self.__class__.__name__, "Validating key:<" + str(key_name) + ">; value:<" + str(param_value) + ">", 3)

        result = False
        if (param_type == "boolean"):
            result = self.is_boolean(param_value)
        elif (param_type == "number"):
            result = self.is_number(param_value)
        elif (param_type == "ip_address"):
            result = self.is_ip_address(param_value)
        elif (param_type == "board"):
            result = self.is_board(param_value)
        elif (param_type == "path"):
            result = self.is_path(param_value)
        elif (param_type == "string"):
            result = True
        else:
            raise ConfigurationException("Function Error - " \
                                         "Unknown type:<"+ str(param_type) +">")
        if (result == False):
            raise ConfigurationException("Configuration Error - " \
                                         "key:<"+ str(key_name) +">; " \
                                         "value:<" + str(param_value) + ">")

    # Validate single dictionary
    def validate_dict(self, dict_name, test_dict):

        self.log_mgr.info(self.__class__.__name__, "Validating dict:<" + str(dict_name) + ">", 3)

        # Get list of valid keys
        self.ck = self.get_keys(dict_name)
        if (self.ck is None):
            raise ConfigurationException("Function Error - " \
                                        "missing dict:<"+ str(dict_name) +">")

        # Check if test configuration includes unknown keys
        for c_key in test_dict.keys():
            if (self.ck.has_key(c_key) == False):
                raise ConfigurationException("Configuration Error - unknown key:<"+ str(c_key) +">")

        # Iterate over dictionary configuration keys
        for c_key in self.ck.iterkeys():

            # Perform key configuration check
            if (test_dict.has_key(c_key) == False):
                raise ConfigurationException("Configuration Error - " \
                                            "missing key:<"+ str(c_key) +">")

            try: # Perform data congruity check
                self.validate_key(c_key, test_dict.get(c_key), self.ck.get(c_key))
            except ConfigurationException as ce:
                raise ce

    # Validate entire configuration
    def validate_config(self, test_config):

        self.log_mgr.info(self.__class__.__name__, "Starting Validation", 2)

        if (test_config is None):
            raise ConfigurationException("Configuration Error - empty configuration")
        
        if (isinstance(test_config, dict) == False):
            raise ConfigurationException("Configuration Error - configuration must be a dictionary")

        # Check if all keys in configuration files are valid
        for c_dict in self.config_keys.keys():
            if (test_config.has_key(c_dict) == False):
                raise ConfigurationException("Configuration Error - missing dict:<"+ str(c_dict) +">")

            # Each dict key refers to a dict list
            dics_list = test_config.get(c_dict)
        
            if (isinstance(dics_list, list) == False):
                raise ConfigurationException("Configuration Error - configuration items must be lists")

            for dic in dics_list:
                if (isinstance(dic, dict) == False):
                    raise ConfigurationException("Configuration Error - configuration list must include dictionaries")

                try: # Perform data congruity check
                    self.validate_dict(c_dict, dic)
                except ConfigurationException as ce:
                    raise ce

        # Check if configuration file includes unknown dict lists
        for c_dict in test_config.keys():
            if (self.config_keys.has_key(c_dict) == False):
                raise ConfigurationException("Configuration Error - unknown dict:<"+ str(c_dict) +">")


    def close(self):
        self.log_mgr = None

    # Service methods
    def is_number(self, check_string):
        try:
            float(check_string)
            return True
        except ValueError:
            return False

    def is_boolean(self, check_string):
        if ((check_string == "true") or (check_string == "false")):
            return True
        else:
            return False

    def is_board(self, check_string):
        return ((check_string == "sense_hat") or \
                (check_string == "average") or \
                (check_string == "seneca") )

    def is_ip_address(self, check_string):
        a = check_string.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def is_path(self, check_string):
        if not os.path.exists(os.path.dirname(check_string)):
            raise ConfigurationException("Configuration Error - " \
                                        "Unexisting path:<"+ str(check_string) +">")

    # Get internal variables
    def get_dicts(self):
        return self.config_keys.keys()

    def get_keys(self, dict_type):
        for dict_name in self.config_keys.keys():
            if (dict_name == dict_type):
                return self.config_keys.get(dict_name)

        raise ConfigurationException("Function Error - " \
                                        "Unknown dict:<"+ str(dict_type) +">")
