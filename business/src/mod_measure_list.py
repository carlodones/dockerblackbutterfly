import mod_config


# Classe per la memorizzazione di una singola misura
class Measure(object):
    def __init__(self, channel, value, timestamp, count=1):
        self.channel = channel
        self.value = value
        self.timestamp = timestamp
        self.read = 0
        self.average = 0
        self.json = 0
        self.count = count

# Classe per la gestione delle liste misura
class MeasureList(object):
    def __init__(self):
        pass

    plist = []

    # Aggiunge alla lista una misura dati i valori
    def add_details(self, channel, value, timestamp):
        meas = Measure(channel, value, timestamp)
        self.plist.append(meas)

    # Aggiunge alla lista una misura
    def add_measure(self, meas):
        self.plist.append(meas)

    # Ritorna lista delle misure per singolo canale
    def list_by_channel(self, channel):
        part_list = []
        for meas in self.plist:
            if ((meas.channel == channel) & (meas.read == 0)):
                part_list.append(meas)
                meas.read = 1
        return part_list

    # Ritorna lista delle misure per singolo canale e stato
    def json_dictionary(self, cfg_mgr):
        dic_list = []
        key_dict = cfg_mgr.get_MQTT_keys_dict()
        for meas in self.plist:
            elem_dic = {}
            if (meas.json == 0):
                elem_dic[key_dict.get('payload')] = meas.value
                elem_dic[key_dict.get('address')] = meas.channel
                elem_dic[key_dict.get('timestamp')] = meas.timestamp
                elem_dic[key_dict.get('qos')] = "good"
                dic_list.append(elem_dic)
                meas.json = 1
        return dic_list

    # Ritorna media delle misure per singolo canale e stato
    def avg_by_channel(self, channel):

        # Numero misure contate
        val_count = 0
        val_tot = 0
        val_ts = 0
        val_avg = 0

        # Estraggo le misure e calcolo la media
        for meas in self.plist:
            if ((meas.channel == channel) & (meas.average == 0)):
                if (val_ts == 0):
                    val_ts = meas.timestamp
                val_count = val_count + 1
                val_tot = val_tot + meas.value
                meas.average = 1

        # Calcolo la media delle ultime misure
        if (val_count > 0):
            val_avg = val_tot / val_count
        else:
            val_avg = 0

        meas_avg = Measure(channel, val_avg, val_ts, val_count)

        return meas_avg

    # Elimina gli elementi processati
    def clear_list(self):
        for meas in self.plist:
            if (meas.json == 1):
                self.plist.remove(meas)

    # Ritorna la lista completa
    def list(self):
        return self.plist
