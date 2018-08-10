import os
import json
import mod_log

#config_file = '/usr/src/app/cfg/config.json'
config_file = './cfg/config.json'
log_mgr = mod_log.LogManager()

class ConfigManager(object):
    def __init__(self):
        self.config = None
        pass

    def load_config(self):
        global config_file
        if not os.path.isfile(config_file):
            log_mgr.fatal("Config file <%s> does not exist!" % config_file)
            return False

        # Apro la lista dei parametri di configurazione
        with open(config_file, 'r') as f:
            if self.config is None:
                config = self.ordered(json.load(f))
                return True

            config_new = json.load(f)
            #config_new = self.ordered(config_new)
            print (config_new)

        if (config == config_new):
            return True
        
        self.check_diffs(config, config_new)

        return True

    # Stampa gli elementi della lista
    #def print_config(self):
    #    for item in self.config:
    #        lvINDEX=0
    #        for params in self.config[item]:
    #            for key, value in params.iteritems():
    #                print (item +'/'+str(lvINDEX)+'/'+key, value)
    #            lvINDEX+=1

    # Ordinamento degli elementi della lista
    def ordered(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj

    # Confronto dei valori della configurazione nuova con quella vecchia
    def check_diffs(self, old, new):
        diff = False
        for old_key in old:
            if old_key not in new:
                diff = True
                log_mgr.warning("key:<%s> missing" %old_key)
            elif old[old_key] != new[old_key]:
                diff = True
                log_mgr.warning("key:<" + old_key + "> value updated: old:<" + old[old_key] + ">; new:<" + new[old_key] + ">")
        return diff

    def get_channel_list(self):
        return self.config.get('channels', {})

    def get_MQTT_keys_dict(self):
        return self.config.get('MQTT_keys', {})

ConfigManager.load_config(0)
    