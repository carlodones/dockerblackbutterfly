import logging

log_path = '/usr/src/app/log/main_log.log'
log = logging.getLogger(__name__)

class LogManager(object):

    def __init__(self):
        global log
        global log_path

        log = logging.getLogger(__name__)
        log.setLevel(logging.INFO)

        # create a file handler
        handler = logging.FileHandler(log_path)
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the log
        log.addHandler(handler)
        pass
    
    # Aggiunge alla lista una misura dati i valori
    def info(self, message):
        global log
        log.info(message)

    # Aggiunge alla lista una misura dati i valori
    def fatal(self, message):
        global log
        log.fatal(message)

    # Aggiunge alla lista una misura dati i valori
    def warning(self, message):
        global log
        log.warning(message)