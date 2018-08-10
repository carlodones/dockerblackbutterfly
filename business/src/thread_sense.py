import math
import json
import mod_config
import mod_measure_list
import mod_thread
import mod_sense_hat
import mod_average
from random import randint

thread_list = []
thd_mgr = mod_thread.ThreadManager
max_cycles = 1000

class start(object):
    def __init__(self):
        self.cfg_mgr = cfg_mgr
        self.channel_list = []
        cfg_mgr.load_config()
        self.channel_list = self.cfg_mgr.get_channel_list
        pass

    def setup_threads(self):
        global thread_list
        global measure_list

        source = None
        thread = None

        for ch in self.channel_list:

            # Istanzio l'oggetto che gestisce il canale di acquisizione (fisico o calcolato)
            if (ch.get("type") == "analogue"):
                source = mod_sense_hat.SenseManager(ch.get("channel"))
            if (ch.get("type") == "average"):
                source = mod_average.AverageManager(measure_list, ch.get("channel"))

            # Istanzio il thread, fornendogli il riferimento del canale di acquisizione
            thread = thd_mgr(ch.get("channel"), ch.get("id"), ch.get("name"), ch.get("samp_time_ms"), source, measure_list)
            thread_list.append(thread)

    def start_threads(self):
        for th in thread_list:
            th.start()
            th.join()
            th.read_channel()


# Leggo la configurazione
cfg_mgr = mod_config.ConfigManager()

# Istanzio la lista misure
measure_list = mod_measure_list.MeasureList()

# sns_mgr.show_green_sign()
print("Termine programma")
