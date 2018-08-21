import mod_config
import mod_measure_list
import json

# Measure list management class
class Collection(object):
    def __init__(self,log_mgr,delay,channel, jf_topic,jf_path):
        self.log_mgr = log_mgr
        self.jf_topic = jf_topic
        self.jf_path = jf_path
        self.channel = channel
        self.jl_measure_list = None

        self.exit_flag = False              # Flag per la terminazione del thread
        self.delay = delay                  # Tempo di loop in s.
        pass

    # Adds a new measure to the list
    def create_collection(self):
        jl_measure_list=mod_measure_list.MeasureList()
        
        cfg_mgr = mod_config.ConfigManager(self.log_mgr)
        json_list = jl_measure_list.json_dictionary(self.channel,cfg_mgr)
        
        #json_list = jl_measure_list.list_by_channel(self.channel)
        #print (json_list)

        with open(self.jf_path+self.jf_topic+'.json',"w") as f:
            json.dump(json_list, f)
