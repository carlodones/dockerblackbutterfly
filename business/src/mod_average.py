import time
import mod_measure_list

class AverageManager(object):
    def __init__(self, measure_list, source_channel):
        self.measure_list = measure_list
        self.source_channel = source_channel

    def read_channel(self, channel):
        
        # Calcolo la media
        val = self.measure_list.avg_by_channel(self.source_channel)

        # Arrotondamento ad una cifra decimale
        val = round(val, 2)

        return val
