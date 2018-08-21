import mod_config


# Single measure storage
class Measure(object):
    def __init__(self, channel, value, qos, timestamp, count=1):
        self.channel = channel          # Measure channel
        self.value = value              # Measure value
        self.timestamp = timestamp      # Measure timestamp
        self.read = False               # Flag: measure read
        self.average = False            # Flag: measure used to calculate average
        self.json = False               # Flag: measure used to generate JSON string
        self.count = count              # Number of measure used to calculate the average
        self.qos = qos

# Measure list management class
class MeasureList(object):
    def __init__(self):
        pass

    plist = []

    # Creates a new measure and adds it to the list
    def add_details(self, channel, value, qos, timestamp):
        meas = Measure(channel, value, qos, timestamp)
        self.plist.append(meas)

    # Adds a new measure to the list
    def add_measure(self, meas):
        self.plist.append(meas)

    # Returns complete measures list for one channel
    def list_by_channel(self, channel):
        part_list = []
        for meas in self.plist:
            if ((meas.channel == channel) & (meas.read == False)):
                part_list.append(meas)
                meas.read = True
        return part_list

    # Returns dictionary for single measure
    def json_dictionary(self, channel, cfg_mgr):
        dic_list = []
        #key_dict = cfg_mgr.get_config_item_list("MQTT_keys")[0] 
        key_dict = cfg_mgr.get_config_item_list("MQTT_keys") 
        for meas in self.plist:
            elem_dic = {}
            if ((meas.channel == channel) & (meas.json == False)):
#                elem_dic[key_dict.get('payload')] = meas.value
#                elem_dic[key_dict.get('address')] = meas.channel
#                elem_dic[key_dict.get('timestamp')] = meas.timestamp
#                elem_dic[key_dict.get('qos')] = meas.qos

                elem_dic['payload'] = meas.value
                elem_dic['address'] = meas.channel
                elem_dic['timestamp'] = meas.timestamp
                elem_dic['qos'] = meas.qos

                dic_list.append(elem_dic)
                meas.json = True
        return dic_list

    # Returns measure average for single channel
    def avg_by_channel(self, channel, source_channel):

        # Initialization
        val_count = 0
        val_tot = 0
        val_ts = 0
        val_avg = 0

        # Get measure list
        for meas in self.plist:
            if ((meas.channel == source_channel) and (meas.average == False)):
                if (val_ts == 0):
                    val_ts = meas.timestamp
                val_count = val_count + 1
                val_tot = val_tot + meas.value
                meas.average = True

        # Calculate average
        if (val_count > 0):
            val_avg = float(val_tot / val_count)
        else:
            val_avg = 0

        meas_avg = Measure(channel, val_avg, val_ts, val_count)

        return meas_avg

    # Delete processed measures
    def clear_list_by_channel(self, channel):
        for meas in self.plist:
            if (meas.channel == channel):
                self.plist.remove(meas)

    # Clear list
    def clear_list(self):
        for meas in self.plist:
            if (meas.json == True):
                self.plist.remove(meas)

    # Returns complete list
    def list(self):
        return self.plist
