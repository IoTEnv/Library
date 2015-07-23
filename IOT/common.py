__author__ = 'Jackie'

import sys
import paho.mqtt.client as mqtt

DEBUG = False
appID = None
serverAddr = "epiwork.hcii.cs.cmu.edu"
serverPort = 1883
clientID = None
mqttClient = mqtt.Client()
mqttSubscribedFunctions = {}


IMPROMPTO_APP_ID = "12345"
IMPROMPTO_PROTOCOL_VERSION = 1
IMPROMPTO_DEVICE_ID = "IOT Scripting"
IMPROMPTO_IOT_CONTEXT = "IOT"
IMPROMPTO_COMMAND_CONTEXT = "IOT_TABLET_LIGHT"


def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def debug(*objs):
    if DEBUG == True:
        print(*objs)