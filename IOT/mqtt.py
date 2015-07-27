import sys
import json
import copy
import time
import threading
import paho.mqtt.client as mqtt
import bluetooth
import urllib
import urllib.parse
import urllib.request
from operator import attrgetter

from .common import *

def initializeMQTT():
    def on_connect(client, userdata, rc):
        debug("client connected with result code" + str(rc))
        pass
    def on_message(client, userdata, msg):
        debug(msg.topic + " " + str(msg.payload))
        for function in mqttSubscribedFunctions[msg.topic]:
            function(msg)
    def on_disconnect(client, userdata, rc):
        debug("client disconnected!")
        client.connect(serverAddr, serverPort)
        debug("client reconnecting...")
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    mqttClient.connect(serverAddr, serverPort)
    mqttClient.publish("IOT/debug", payload = str(clientID) + " connected", qos = 0, retain = False)
    debug("mqtt client initialized")


class mqttChannelList(list):
    """docstring for mqttChannelList"""
    def __init__(self, channel):
        super(mqttChannelList, self).__init__()
        self.channel = channel
        mqttSubscribedFunctions[channel] = self
        mqttClient.subscribe(channel)

    def remove(self, obj):
        super(mqttChannelList, self)
        if len(super(mqttChannelList, self)) == 0:
            mqttClient.unsubscribe(self.channel)
            del mqttSubscribedFunctions[self.channel]

def getMqttChannel(channel):
    if channel in mqttSubscribedFunctions.dict():
        return mqttSubscribedFunctions[channel]
    else:
        mqttSubscribedFunctions[channel] = mqttChannelList(channel)
        return mqttSubscribedFunctions[channel]

class mqttSubscriber(object):
    """docstring for mqttSubscriber"""
    mqttChannel = None
    mqttFunction = None
    def __init__(self, channel, function):
        super(mqttSubscriber, self).__init__()
        self.mqttChannel = getMqttChannel(channel)
        self.mqttFunction = function
        self.mqttChannel.append(self.mqttFunction)

    def __del__(self):
        self.mqttChannel.remove(self.mqttFunction)

def subscribe(channel, function):
    return mqttSubscriber(channel, function)

def send(channel, message):
    mqttClient.publish(channel, payload = message, qos = 0, retain = False)

