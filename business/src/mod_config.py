import sys
import os
import json
import time
import mod_log
import mod_config_validation
from pprint import pprint

config_file = "/usr/src/app/cfg/config.json"
config_check = "/usr/src/app/log/dict_%Y%m%d-%H%M%S.json"

class ConfigManager(object):
    def __init__(self, log_mgr):
        self.log_mgr = log_mgr
        self.config = None
        self.command_path = None
        self.action = None
        self.stopping = False
        self.cv = mod_config_validation.ConfigValidation(self.log_mgr)

    def load_config(self):

        global config_file
        config_new_sorted = None

        if(self.stopping == True):
            self.log_mgr.info(self.__class__.__name__, "Service is stopping ... nothing to do!", 1)
            return True

        # Check config file existence
        self.log_mgr.info(self.__class__.__name__, "Loading Config file <" + str(config_file) + ">", 1)
        if not os.path.isfile(config_file):
            self.log_mgr.fatal(self.__class__.__name__, "Config file <" + str(config_file) + "> does not exist!", 1)
            return False

        try: # Open configuration file
            with open(config_file, 'r') as f:
                config_new_sorted = self.ordered(json.load(f))

            # Validate configuration
            self.cv.validate_config(config_new_sorted)
            self.log_mgr.info(self.__class__.__name__, "Configuration validated", 1)

        except Exception as exc: # Validation error
            self.log_mgr.fatal(self.__class__.__name__, "Configuration load error:<" + str(exc.message) + ">", 1)
            return False if self.config is None else True

        # If confguration is empty, ok
        if self.config is None:
            self.config = config_new_sorted
            return True

        # If nothing change, ok
        if (config_new_sorted == self.config):
            self.log_mgr.info(self.__class__.__name__, "Config unchanged", 2)
            return True

        # Log configuration changes and restart service
        self.to_json(self.config, "config_back_up")
        self.check_diffs(config_new_sorted, self.config)

        if (self.action is None or self.command_path is None):
            raise mod_config_validation.ConfigurationException( \
                "Configuration Error - " + \
                "update action not set:<"+ str(self.command_path) +">")

        self.log_mgr.info(self.__class__.__name__, "Config update - FORCING SERVICE RESTART", 1)
        self.stopping = True

        with open(str(self.command_path) + "/" + str(self.action) , 'w') as f:
            f.write(str(self.action))

        return False

    def close(self):
        self.log_mgr = None
        self.cv.close()

    # Sets the folder where to write the command file
    def configure_action(self, command_path, action):
        self.command_path = command_path
        self.action = action

    # Save configuration dictionary to a new file
    def to_json(self, cfg=None, cfg_name=None):
        global config_check
        if (cfg == None):
            cfg = self.config
        if (cfg_name == None):
            cfg_name = "inner"
        config_check_f = time.strftime(config_check)
        self.log_mgr.info(self.__class__.__name__, "Saving config:<" + str(cfg_name) + "> to JSON:<" + str(config_check_f) + ">", 2)
        with open(config_check_f, 'w') as f:
            f.write(json.dumps(cfg))

    # Sorting configurtion dictionary elements
    # https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa
    def ordered(self, obj):
        try:
            if isinstance(obj, dict):
                return dict(sorted((k, self.ordered(v)) for k, v in obj.items()))
            if isinstance(obj, list):
                return list(sorted(self.ordered(x) for x in obj))
            else:
                return obj
        except:
            self.log_mgr.fatal("Error processing object:<" + str(obj) + ">", 2)

    # Compare old and new configuration dictionaries and log differences
    def check_diffs(self, old_item, new_item):
        diff = False
        try:
            if (isinstance(old_item, dict)):
                if(isinstance(new_item, dict) == False):
                    diff = diff or True
                    self.log_mgr.warning(self.__class__.__name__, "old is dict, new not", 2)
                else:
                    for old_key in old_item.keys():
                        if (new_item.has_key(old_key) == False):
                            diff = diff or True
                            self.log_mgr.warning(self.__class__.__name__, \
                                "key:<" + str(old_key) + "> missing", 2)
                        elif (isinstance(old_item.get(old_key), list) or \
                              isinstance(new_item.get(old_key), list) or \
                              isinstance(old_item.get(old_key), dict) or \
                              isinstance(new_item.get(old_key), dict)):
                                self.log_mgr.warning(self.__class__.__name__, "processing key:<" + str(old_key) + ">", 3)
                                diff = self.check_diffs(old_item.get(old_key), new_item.get(old_key))
                        elif (old_item.get(old_key) != new_item.get(old_key)):
                            diff = diff or True
                            self.log_mgr.warning(self.__class__.__name__, \
                                "key:<" + str(old_key) + "> " + \
                                "old:<" + str(old_item.get(old_key)) + ">; " + \
                                "new:<" + str(new_item.get(old_key)) + ">", 2)

            elif (isinstance(old_item, list)):
                if(isinstance(new_item, list) == False):
                    diff = diff or True
                    self.log_mgr.warning(self.__class__.__name__, "old is list, new not", 2)
                elif (len(new_item) != len(old_item)):
                    diff = diff or True
                    self.log_mgr.warning(self.__class__.__name__, \
                        "Lists have different items number - " + \
                        "old:<" + str(len(old_item)) + ">; " + \
                        "new:<" + str(len(new_item)) + ">", 2)
                else:
                    for i in range(len(old_item)):
                        if (isinstance(old_item[i], dict) or \
                            isinstance(new_item[i], dict) or \
                            isinstance(old_item[i], list) or \
                            isinstance(new_item[i], list)):
                                diff = diff or self.check_diffs(old_item[i], new_item[i])
                        elif (old_item[i] != new_item[i]):
                            diff = diff or True
                            self.log_mgr.warning(self.__class__.__name__, \
                                "key:<" + str(old_key) + "> " + \
                                "old:<" + str(old_item[i]) + ">; " + \
                                "new:<" + str(new_item[i]) + ">", 2)
            else:
                diff = diff or True
                self.log_mgr.warning(self.__class__.__name__, "Dicts have different structure", 2)

            return diff

        except:
            self.log_mgr.fatal("Error processing objects - old_item:<" + str(old_item) + ">; new_item:<" + str(new_item) + ">", 1)

    def get_config_item_list(self, config_key):
        if (self.config.has_key(config_key) == False):
            raise mod_config_validation.ConfigurationException( \
                "Configuration Error - " + \
                "missing key:<"+ str(config_key) +">")

        # Each dict key refers to a dict list
        elem_list = self.config.get(config_key)
    
        if (isinstance(elem_list, list) == False):
            raise mod_config_validation.ConfigurationException( \
                "Configuration Error - " + \
                "configuration <"+ str(config_key) +"> is not a lists")

        if (elem_list is None):
            raise mod_config_validation.ConfigurationException( \
                "Configuration Error - " + \
                "configuration " + str(config_key)+ " list is null!")

        if (elem_list.count == 0):
            raise mod_config_validation.ConfigurationException( \
                "Configuration Error - " + \
                "configuration " + str(config_key)+ " list is empty!")

        return elem_list
