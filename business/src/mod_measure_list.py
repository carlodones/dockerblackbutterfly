import mod_config
import datetime
import time

class QOS(object):
    def __init__(self):
        self.ONLINE = 1
        self.OFFLINE = 0
        self.ANOMALY = -1

class FLAG(object):
    def __init__(self):
        self.ALL = 2
        self.TRUE = 1
        self.FALSE = 0

# Single measure storage
class Measure(object):
    def __init__(self, channel, value, timestamp, qos, send, count=1):
        self.channel = channel          # Measure channel
        self.value = value              # Measure value
        self.timestamp = timestamp      # Measure timestamp
        self.qos = qos                  # Quality of service: (1=ONLINE/GOOD; 0=OFFLINE; -1=ANOMALY/BAD)
        self.send = send                # Flag: true if measure must be sent by MQTT message
        self.average = False            # Flag: measure used to calculate average
        self.json = False               # Flag: measure used to generate JSON string
        self.count = count              # Number of measure used to calculate the average
        self.qos = qos

# Single channel status storage
class ChannelStatus(object):
    def __init__(self, channel, qos, timestamp):
        self.channel = channel          # Measure channel
        self.qos = qos                  # Quality of service: (1=ONLINE; 0=OFFLINE; -1=ANOMALY)
        self.timestamp = timestamp      # Measure timestamp
        self.json = False               # Flag: measure used to generate JSON string

# Measure list management class
class MeasureList(object):
    def __init__(self):
        self.qos = QOS()
        self.flag = FLAG()
        self.flag_dict = { self.flag.TRUE: True, self.flag.FALSE: False }
        pass

    plist = []

    # Creates a new measure and adds it to the list
    def add_details(self, channel, value, timestamp, qos, send):
        meas = Measure(channel, value, timestamp, qos, send)
        self.plist.append(meas)

    # Adds a new measure to the list
    def add_measure(self, meas):
        self.plist.append(meas)

    # Returns dictionary of all non-json-ed measures list
    def to_json_by_status(self, cfg_mgr, flag_send, flag_average, flag_json):

        dic_list = []
        key_dict = cfg_mgr.get_config_item_dict("MQTT_keys", 0)
        qos_dict = cfg_mgr.get_config_item_dict("MQTT_measure_qos", 0)


        send = self.flag_dict.get(flag_send, False)
        average = self.flag_dict.get(flag_average, False)
        json = self.flag_dict.get(flag_json, False)
        for meas in self.plist:
            elem_dic = {}
            if(flag_send != self.flag.ALL):
                if(send != meas.send):
                    continue
            if(flag_average != self.flag.ALL):
                if (average != meas.average):
                    continue
            if(flag_json != self.flag.ALL): 
                if(json != meas.json):
                    continue
            elem_dic[key_dict.get("payload")] = meas.value
            elem_dic[key_dict.get("address")] = meas.channel
            elem_dic[key_dict.get("timestamp")] = meas.timestamp
            elem_dic[key_dict.get("qos")] = qos_dict.get(meas.qos)
            dic_list.append(elem_dic)
            meas.json = True
        return dic_list


    # Returns dictionary of all non-json-ed measures list
    def to_json(self, cfg_mgr):
        dic_list = []
        key_dict = cfg_mgr.get_config_item_dict("MQTT_keys", 0)
        qos_dict = cfg_mgr.get_config_item_dict("MQTT_measure_qos", 0)
        for meas in self.plist:
            elem_dic = {}
            if (meas.json == False):
                elem_dic[key_dict.get('payload')] = meas.value
                elem_dic[key_dict.get('address')] = meas.channel
                elem_dic[key_dict.get('timestamp')] = meas.timestamp
                elem_dic[key_dict.get('qos')] = qos_dict.get(meas.qos)
                dic_list.append(elem_dic)
                meas.json = True
        return dic_list

    # Returns measure average for single channel
    def avg_by_channel(self, channel, source_channel, send):

        # Initialization
        val_count = 0
        val_tot = 0
        val_qos = self.qos.ONLINE
        val_ts = 0
        val_avg = 0

        # Get measure list
        for meas in self.plist:
            if ((meas.channel == source_channel) and \
                (meas.average == False)):
                if (val_ts == 0):
                    val_ts = meas.timestamp
                val_count = val_count + 1
                if (meas.qos == self.qos.ONLINE):
                    val_tot = val_tot + meas.value
                    meas.average = True
                else:
                    val_qos = meas.qos

        # Calculate average
        if (val_count > 0):
            val_avg = float(val_tot / val_count)
        else:
            val_avg = 0

        meas_avg = Measure(channel, val_avg, val_ts, val_qos, send, val_count)

        return meas_avg

    # Delete processed measures
    def clear_by_channel(self, channel):
        for meas in self.plist:
            if (meas.channel == channel):
                self.plist.remove(meas)

    # Delete processed measures
    def clear_by_channel_and_status(self, channel, flag_send, flag_average, flag_json):

        send = self.flag_dict.get(flag_send, False)
        average = self.flag_dict.get(flag_average, False)
        json = self.flag_dict.get(flag_json, False)

        for meas in self.plist:
            if (meas.channel == channel):
                if(flag_send != self.flag.ALL):
                    if(send != meas.send):
                        continue
                if(flag_average != self.flag.ALL):
                    if (average != meas.average):
                        continue
                if(flag_json != self.flag.ALL): 
                    if(json != meas.json):
                        continue
                self.plist.remove(meas)

    # Clear list
    def clear_list(self):
        for meas in self.plist:
            self.plist.remove(meas)

    # Returns complete list
    def list(self):
        return self.plist


# Channel status list management class
class ChannelStatusList(object):
    def __init__(self):
        pass

    plist = []

    # Creates a new channel status and adds it to the list
    def add_details(self, channel, qos, timestamp):
        chsts = ChannelStatus(channel, qos, timestamp)
        self.plist.append(chsts)

    # Adds a new channel status to the list
    def add_channel_status(self, chsts):
        self.plist.append(chsts)

    # Updates channel status with a measure status
    def upd_channel_status(self, meas):
        last_chsts = self.get_last_status_by_channel(meas.channel)
        if(last_chsts is None):
            self.add_details(meas.channel, meas.qos, meas.timestamp)
        elif(last_chsts.qos != meas.qos):
            self.add_details(meas.channel, meas.qos, meas.timestamp)

    # Returns last recorded channel_status for a specific channel
    def get_last_status_by_channel(self, channel):
        ts_start = time.mktime(datetime.datetime(2000, 1, 1, 0, 0, 0).timetuple())
        ret_chsts = None
        for chsts in self.plist:
            if (chsts.channel == channel):
                if (chsts.timestamp >= ts_start):
                    ret_chsts = chsts
        return ret_chsts

    # Returns dictionary for all channel statuses
    def to_json(self, cfg_mgr):
        dic_list = []
        key_dict = cfg_mgr.get_config_item_dict("MQTT_keys", 0)
        qos_dict = cfg_mgr.get_config_item_dict("MQTT_channel_qos", 0)
        for chsts in self.plist:
            elem_dic = {}
            if (chsts.json == False):
                elem_dic[key_dict.get('address')] = chsts.channel
                elem_dic[key_dict.get('timestamp')] = chsts.timestamp
                elem_dic[key_dict.get('qos')] = qos_dict.get(chsts.qos)
                dic_list.append(elem_dic)
                chsts.json = True
        return dic_list

    # Delete processed channel statuss
    def clear_list_by_channel(self, channel):
        for chsts in self.plist:
            if (chsts.channel == channel):
                self.plist.remove(chsts)

    # Clear list
    def clear_list(self):
        for chsts in self.plist:
            if (chsts.json == True):
                self.plist.remove(chsts)

    # Returns complete list
    def list(self):
        return self.plist
