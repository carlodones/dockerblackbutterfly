import sys
import os
import time
import logging

class LogManager(object):

    def __init__(self):

        # Setting default log level and log path:
        self.log_path = '/usr/src/app/log/main_log.log'
        self.log_level = 3 

        self.log = logging.getLogger(__name__)

        try:

            self.log.setLevel(logging.INFO)

            # create a file handler
            handler = logging.FileHandler(self.log_path)
            handler.setLevel(logging.INFO)

            # create a logging format
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            # add the handlers to the log
            self.log.addHandler(handler)
            self.info(self.__class__.__name__, "logger open", 1)

        except:
            print ("Log set-up error:", sys.exc_info()[0])
            raise

    # Set log path and log level
    def set_log_config(self, log_level, backup_log_path):
        self.log_level = log_level
        self.backup_log_path = backup_log_path

    # Define logging level
    def set_log_level(self, log_level):
        self.log_level = log_level

    # Info message
    def info(self, caller, message, level=1):
        if (level <= self.log_level):
            self.log.info(caller + " - "  + message)

    # Fatal message
    def fatal(self, caller, message, level=1):
        if (level <= self.log_level):
            self.log.fatal(caller + " - "  + message)

    # Warning message
    def warning(self, caller, message, level=1):
        if (level <= self.log_level):
            self.log.warning(caller + " - "  + message)

    def close(self):
        # Notify log close-up
        self.info(self.__class__.__name__, "logger closed", 1)

        # Backup actual log file
        self.backup_log_path = time.strftime(self.backup_log_path)
        if(os.path.exists(self.log_path)):
            if(os.path.exists(self.backup_log_path) == False):
                os.rename(self.log_path, self.backup_log_path)

        # Close log handlers
        for h in list(self.log.handlers):
            self.log.removeHandler(h)
        self.log_path = None
        self.log_level = None

