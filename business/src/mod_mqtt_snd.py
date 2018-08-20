#!/usr/bin/env python3
import sys
import os
import json
import mod_log
import time
import paho.mqtt.client as mqtt
import threading

# Threads management class
class MqttSend(object):
    def __init__(self,delay,log_mgr,topic,ip_add,file_msg):
        self.log_mgr = log_mgr
        self.topic = topic
        self.ip_add = ip_add
        self.file_msg = file_msg
        self.f_send_msg = None

        self.exit_flag = False              # Flag for terminating thread
        self.delay = delay                  # Time loop (s)
        #init client
        self.client = mqtt.Client("P1")
        pass
    
    def send_msg(self):
        self.log_mgr.info(self.__class__.__name__, "MQTT snd sending <" + self.file_msg + "> to <" + self.ip_add + ">", 3)
        try:
            #open loop for sending message
            self.client.loop_start()
            #send json message
            self.client.publish(self.topic, payload=json.dumps(self.f_send_msg), qos=2, retain=False)
            #close loop for sending message
            self.client.loop_stop()
            return True
            
        except:
            self.log_mgr.info(self.__class__.__name__, "MQTT snd ERROR sending <" + self.f_send_msg + "> to <" + self.ip_add + "> " + str(sys.exc_info()[0]), 1)
            raise
        
    def connect(self):
        self.log_mgr.info(self.__class__.__name__, "MQTT snd connecting to <" + self.ip_add + ">", 1)
        try:
            #connect to server identified by IP_ADDR
            self.client.connect(self.ip_add)
            #compile message topic
            self.client.subscribe(self.topic)
            return True
            
        except:
            self.log_mgr.info(self.__class__.__name__, "MQTT snd connecting to <" + self.ip_add + "> " + sys.exc_info()[0], 1)
            raise
    
    def disconnect(self):
        try:
            self.client.disconnect()
            return True
            
        except:
            raise

    # Stop thread
    def stop_function (self):
        self.log_mgr.info(self.__class__.__name__, "MQTT snd exit", 1)
        self.exit_flag = True

    def manage_message(self):
        # [TODO] : potrei avere una lista di file JSON ...
        if (os.path.exists(self.file_msg)):
            with open(self.file_msg) as data_file:
                self.f_send_msg = json.load(data_file)
                self.connect()
                self.send_msg()

    # # Start thread definition
    # def MqttSend_thread(self):
    #     self.log_mgr.info(self.__class__.__name__, "MQTT snd starting")

    #     while (self.exit_flag == False):
    #         try:
    #             with open(self.file_msg) as data_file:
    #                 self.f_send_msg = json.load(data_file)
    #                 self.connect()
    #                 self.send_msg()
                    
    #         except:
    #             self.log_mgr.info(self.__class__.__name__, "MQTT snd nothing to send")
    #             raise

    #         time.sleep(self.delay)

    # # Start main thread
    # def start_Thread(self):
    #     self.snd_thread = threading.Thread(target = self.MqttSend_thread)
    #     self.snd_thread.start()



######################################################################################################

'''

with open('./src/message.json') as data_file:
#with open ('/usr/src/app/src/MQTT/message.json') as data_file:
    send_msg = json.load(data_file)

client = mqtt.Client("P1") #create new instance
client.connect("127.0.0.1") #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic")
client.publish('de/DAB_0001/@DATA', payload=json.dumps(send_msg), qos=2, retain=False)
time.sleep(4) # wait
client.loop_stop() #stop the loop


############
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
########################################
broker_address="192.168.1.184"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","house/bulbs/bulb1")
client.subscribe("house/bulbs/bulb1")
print("Publishing message to topic","house/bulbs/bulb1")
client.publish("house/bulbs/bulb1","OFF")
time.sleep(4) # wait
client.loop_stop() #stop the loop
'''