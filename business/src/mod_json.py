import mod_config
import mod_measure_list
import json
import time

# Measure list management class
class Collection(object):
    def __init__(self, log_mgr, cfg_mgr, measure_list, direction, jf_topic, jf_path):
        self.log_mgr = log_mgr
        self.cfg_mgr = cfg_mgr
        self.measure_list = measure_list

        self.direction = direction
        self.jf_path = jf_path+jf_topic.replace("/", "_")+"_%Y%m%d-%H%M%S.json"

        self.exit_flag = False              # Flag per la terminazione del thread
        self.flag = mod_measure_list.FLAG()

        pass

    # Adds a new measure to the list
    def create_collection(self):

        # Create dictionary with all measures with:
        #  - "send" flag set to "true"
        #  - "average" flag set to any value
        #  - "json" flag set to "false"
        json_list = self.measure_list.to_json_by_status(self.cfg_mgr, self.flag.TRUE, self.flag.ALL, self.flag.FALSE)

        # {
        #   "qos": string('good'|'bad'), optional, default('good')
        #   "timestampDevice": number(epoch ms), optional (required if not specified in values array)
        #   "values": array, required
        #   [{
        #     "address": string, required
        #     "payload": string|number|boolean, required
        #     "qos": string('good'|'bad'), optional, default(main "qos")
        #     "timestampDevice": number(epoch ms), optional (required if main "timestampDevice" not specified)
        #   }, {
        #     ...
        #   }]
        # }

        # Set new file name with date and time
        json_file_full_path = time.strftime(self.jf_path)

        with open(json_file_full_path, "w") as f:
            json.dump(json_list, f)
