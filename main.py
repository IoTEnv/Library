import json
import copy
import types
import time
import threading
import paho.mqtt.client as mqtt
import bluetooth
import urllib
import urllib.parse
import urllib.request
from operator import attrgetter

EXPIRE_TIME = 1000
DEVICE_ID = "IOT Scripting"
IOT_CONTEXT = "IOT"
IMPROMPTO_APP_ID = "12345"
IMPROMPTO_PROTOCOL_VERSION = 1

scanAndRecordDeamon = None
client = mqtt.Client()

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def sendRequest(url, obj, request):
    print("sendRequest BEGIN")
    print(url)
    print( obj)
    print( request)
    """send the request"""
    # try:
    #     client.publish(url, payload=obj, qos=0, retain=False)
    # except (Exception e):
    #     raise e
    client.publish("cmu/gcf_framework", request, qos=0, retain=False)
    print("sendRequest END")
    return {"result" : "finished", }

# scan nearby things, this will be automatically called in certain interval
def scanThings():
    """scan the things"""
    f = open("./Schema/vibrate.cleaned.json")
    # scanResult = json.loads(f.read())
    deviceList = bluetooth.discover_devices(lookup_names=True)
    deviceProfiles = [];
    for MACaddress, deviceName in deviceList:
        splittedName = deviceName.split('::')
        # print(splittedName)
        if len(splittedName) == 4:
            deviceName = splittedName[1]
            deviceProfURL = splittedName[2]
            deviceKey = splittedName[3]
            requestPayload = {
                "deviceID": deviceName,
                "appID" : IMPROMPTO_APP_ID,
                "key" : deviceKey,
                "context[]" : IOT_CONTEXT
            }
            encodedRequestPayload = urllib.parse.urlencode(requestPayload)
            full_url = deviceProfURL + "?" + encodedRequestPayload
            data = urllib.request.urlopen(full_url)
            deviceProfile = json.loads(data.read().decode('UTF-8'))
            if "IOT" in deviceProfile.keys():
                deviceProfile = deviceProfile["IOT"]
                deviceProfile["rssi"] = "-22" # temp workaround
                deviceProfile["uuid"] = deviceName
                deviceProfile["name"] = deviceName
                deviceProfiles.append(deviceProfile)
    scanResult = deviceProfiles
    print(scanResult)
    return scanResult

class ThingList(list):
    """docstring for ThingList"""

    # dispatch the method to the list
    def __getattr__(self, name):
        def method(*args):
            for obj in self:
                getattr(obj, name)(*args)
        return method

    # override the append method
    # things with the same uuid will be automatically merged.
    def append(self, obj):
        for idx, thing in enumerate(self):
            if thing._uuid == obj._uuid:
                self[idx] = obj
                return
        super(ThingList, self).append(obj)
        return

    # clean ThingList
    # items that are older than expire_time are cleared
    def cleanList(self):
        for thing in self:
            if thing._timestamp - time.time() > EXPIRE_TIME:
                self.remove(thing)

thingsList = ThingList([]);

class Thing(object):
    """docstring for Thing"""
    def __init__(self, JSONthing, parent = None):
        super(Thing, self).__init__()
        self._uuid = JSONthing["uuid"]
        self._type = JSONthing["type"]
        self._timestamp = time.time()
        if "rssi" in JSONthing:
            self._rssi = int(JSONthing["rssi"])
        else:
            self._rssi = parent._rssi
        if "name" in JSONthing:
            self._name = JSONthing["name"]
        else:
            self._name = parent._name + "." + self._type
        self._nested = [];
        for capName, capDes in JSONthing["capability"].items():
            def function(self, *request):
                JSONrequest = copy.deepcopy(capDes["input"])
                for x in range(0, len(request)):
                    JSONrequest.values()[x] = request[x]
                MQTTpayload = {
                    "contextType":"IOT",
                    "command": capDes["command"],
                    "messageType": capDes["messageType"],
                    "version" : IMPROMPTO_PROTOCOL_VERSION,
                    "deviceID" : DEVICE_ID,
                    "destination":[
                        self._uuid
                    ],
                    "payload": [
                        "PARAMETERS=" + json.dumps(JSONrequest)
                    ]
                }
                print("payload is ", type(json.dumps(MQTTpayload)))
                response = sendRequest(capDes["channel"], self, json.dumps(MQTTpayload));
                return response
            setattr(self, capName, types.MethodType(function, self))
        if "@nested" in JSONthing:
            for JSONnested in JSONthing["@nested"]:
                nestedThing = Thing(JSONnested, self)
                self._nested.append(nestedThing)
        thingsList.append(self)

    """a short description for Thing"""
    def short_description(self):
        return "{ name: " + self._name + ", uuid" + self._uuid + "}"

    def __str__(self):
        return self.short_description();

    # prevent Thing from throwing exception
    def __getattr__(self, name):
        def method(*args):
            warning(self, "does not support ")
        return method

class IOT(object):
    """docstring for IOT"""
    def __init__(self, arg):
        super(IOT, self).__init__()
        self.arg = arg
    @staticmethod
    def find(rule, types = None):
        if types == None:
            return ThingList(rule(thingsList))
        elif isinstance(types, list):
            filteredThingsList = filter(lambda x: any(x._type == s for s in types), thingsList)
            return ThingList(rule(filteredThingsList))
        elif isinstance(types, str):
            filteredThingsList = filter(lambda x: x._type == types, thingsList)
            return ThingList(rule(filteredThingsList))
    @staticmethod
    def findAll():
        return thingsList
    @staticmethod
    def findNearest():
        def Nearest(things):
            return ThingList([max(things, key=attrgetter("rssi"))])
        return IOT.find(Nearest)

def All(things):
    return things

def scanAndRecord():
    print("scanning")
    JSONthingList = scanThings()
    for JSONthing in JSONthingList:
        thingsList.append(Thing(JSONthing))
    thingsList.cleanList()
    print("wait...")
    return

class ScanAndRecordDeamon(object):
    """docstring for scanAndRecordDeamon"""
    def __init__(self):
        super(ScanAndRecordDeamon, self).__init__()
        thread = threading.Thread(target=self.run, args=())
        thread.deamon = True
        thread.start()

    def run(self):
        while True:
            scanAndRecord()
            time.sleep(30)

def initializeMQTT():
    def on_connect(client, userdata, rc):
        print("Connected with result code" + str(rc))
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
    client.subscribe("cmu/gcf_framework")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("epiwork.hcii.cs.cmu.edu", 1883)
    client.publish("cmu/gcf_framework", payload="start", qos=0, retain=False)
    print("mqtt client initialized")
    pass

def initialize():
    initializeMQTT();
    ScanAndRecordDeamon()

if __name__ == '__main__':
    # initialize()
    # scanAndRecord()
    # aThing.identify()
    # print("### test thing list")
    # thingsList.identify()
    # print("### test find all")
    # IOT.find(All).identify()
    # print("### test find phone")
    # IOT.find(All, "phone").identify()
    pass