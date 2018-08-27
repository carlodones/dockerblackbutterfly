#!/usr/bin/env python3
import sys
import os
import json
import mod_log
import time
import paho.mqtt.client as mqtt
import threading

# Threads management class
class MqttReceive(object):
    def __init__(self,delay,log_mgr,topic,ip_add,file_msg):
        self.log_mgr = log_mgr
        self.topic = topic
        self.ip_add = ip_add
        self.file_msg = file_msg
        self.f_send_msg = None

        self.exit_flag = False              # Flag per la terminazione del thread
        self.delay = delay                  # Tempo di loop in s.
        #init client
        self.client = mqtt.Client()
        pass

    #waiting for messages
    def on_message(self, client, userdata, msg):
        self.log_mgr.info(self.__class__.__name__, "MQTT rcv received <" + msg.payload.decode() + ">", 2)
  
        #decode message
        if msg.payload.decode() == "Test":
          self.client.disconnect()
          self.stop_function()

    #define topic
    def on_connect(self, client, userdata, flags, rc):
        self.log_mgr.info(self.__class__.__name__, "MQTT rcv connected with result code "+str(rc), 2)
        self.client.subscribe(self.topic)
    
    #connect to server defined by IP_ADDR
    def connect(self):
        self.log_mgr.info(self.__class__.__name__, "MQTT rcv connecting to <" + self.ip_add + ">", 2)
        try:
            self.client.connect(self.ip_add,1883,60)
            self.client.on_connect = self.on_connect
            return True
            
        except Exception as exc:
            self.log_mgr.info(self.__class__.__name__, "MQTT rcv ERROR connecting to <" + self.ip_add + ">; exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) +">", 2)
    
    def disconnect(self):
        self.log_mgr.info(self.__class__.__name__, "MQTT rcv disconnecting", 1)
        try:
            self.client.disconnect()
            return True
            
        except:
            raise

    # Stop thread
    def stop_function (self):
        self.log_mgr.info(self.__class__.__name__, "MQTT rcv exit", 1)
        self.exit_flag = True

    def manage_message(self):
        try:
            self.connect()
            self.client.on_message = self.on_message
            self.client.loop_read()
        except Exception as exc:
            self.log_mgr.info(self.__class__.__name__, "MQTT rcv ERROR; exception:<" + str(exc) + ">; exc_info:<" + str(sys.exc_info()[0]) +">", 2)
            raise

    # # Start thread definition
    # def MqttReceive_thread(self):
    #     self.log_mgr.info(self.__class__.__name__, "MQTT rcv starting")
    #     self.connect()
    #     self.client.on_message = self.on_message
    #     self.client.loop_forever()

    # # Start main thread
    # def start_Thread(self):
    #     self.rcv_thread = threading.Thread(target = self.MqttReceive_thread)
    #     self.rcv_thread.start()
#
#
#'-------------------------------------------------------------------------------------------------------------'
#
#import paho.mqtt.client as mqtt
#
## This is the Subscriber
#
#def on_connect(client, userdata, flags, rc):
#  print("Connected with result code "+str(rc))
#  client.subscribe("de/DAB_0001/@DATA")
#
#def on_message(client, userdata, msg):
#  print ("messaggio arrivato: " + msg.payload.decode())
#  
#  if msg.payload.decode() == "Test":
#     print("Yes!")
#     client.disconnect()
#    
#client = mqtt.Client()
#client.connect("localhost",1883,60)
#client.on_connect = on_connect
#client.on_message = on_message
#
#client.loop_forever()
#