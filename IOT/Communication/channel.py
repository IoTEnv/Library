import paho.mqtt.client as mqtt
from .common import *

import threading

mqttClient = mqtt.Client()
mqttSubscribedChannels = {}
mqttThread = None

def initializeMQTT():
    def on_connect(client, userdata, rc):
        debug("client connected with result code" + str(rc))
        pass
    def on_message(client, userdata, msg):
        debug(msg.topic + " " + str(msg.payload))
        for function in mqttSubscribedChannels[msg.topic]:
            # threading.Thread(target=function, args=(msg))
            function(msg)
    def on_disconnect(client, userdata, rc):
        debug("client disconnected!")
        client.connect(serverAddress, serverPort)
        debug("client reconnecting...")
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    mqttClient.on_disconnect = on_disconnect
    mqttClient.connect(serverAddress, serverPort)
    mqttClient.publish("IOT/debug", payload = str(clientID) + " connected", qos = 0, retain = False)
    debug("mqtt client initialized")
    mqttClient.loop_start()

class MqttChannelList(list):
    """docstring for MqttChannelList"""
    def __init__(self, channel):
        super(MqttChannelList, self).__init__()
        self.channel = channel
        mqttSubscribedChannels[channel] = self
        mqttClient.subscribe(channel)

    def remove(self, obj):
        super(MqttChannelList, self)
        if len(self) == 0:
            mqttClient.unsubscribe(self.channel)
            del mqttSubscribedChannels[self.channel]

def getMqttChannel(channel):
    if channel in mqttSubscribedChannels:
        return mqttSubscribedChannels[channel]
    else:
        mqttSubscribedChannels[channel] = MqttChannelList(channel)
        return mqttSubscribedChannels[channel]

class MqttSubscriber(object):
    """docstring for MqttSubscriber"""
    mqttChannel = None
    mqttFunction = None
    def __init__(self, channel, function):
        super(MqttSubscriber, self).__init__()
        self.mqttChannel = getMqttChannel(channel)
        self.mqttFunction = function
        self.mqttChannel.append(self.mqttFunction)

    def __del__(self):
        self.mqttChannel.remove(self.mqttFunction)

def subscribe(channel, function):
    return MqttSubscriber(channel, function)

def send(channel, message):
    mqttClient.publish(channel, payload = message, qos = 0, retain = False)

