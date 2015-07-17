import json
import copy
import types
import time
import threading
import paho.mqtt.client as mqtt

EXPIRE_TIME = 1000
DEVICE_ID = "IOT Scripting"

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
    print( "scanThings CALLED")
    """scan the things"""
    f = open("./Schema/vibrate.cleaned.json")
    scanResult = json.loads(f.read())
    print( "scanThings ENDED")
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
        self._uuid = JSONthing["@uuid"]
        self._type = JSONthing["@type"]
        self._timestamp = time.time()
        if "@rssi" in JSONthing:
            self._rssi = int(JSONthing["@rssi"])
        else:
            self._rssi = parent._rssi
        if "@name" in JSONthing:
            self._name = JSONthing["@name"]
        else:
            self._name = parent._name + "." + self._type
        self._nested = [];
        for capName, capDes in JSONthing["@cap"].items():
            def function(self, *request):
                JSONrequest = copy.deepcopy(capDes["input"])
                for x in range(0, len(request)):
                    JSONrequest.values()[x] = request[x]
                MQTTpayload = {
                    "contextType":"IOT",
                    "command": capDes["command"],
                    "messageType": capDes["messageType"],
                    "version" : capDes["version"],
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

class Please(object):
    """docstring for Please"""
    def __init__(self, arg):
        super(Please, self).__init__()
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

def All(things):
    return things

def Nearest(things):
    return ThingList([max(things, lambda x: x._rssi)])

def scanAndRecord():
    JSONthingList = scanThings()
    for JSONthing in JSONthingList:
        thingsList.append(Thing(JSONthing))
    thingsList.cleanList()
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
        client.subscribe("cmu/gcf_framework")
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
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
    initialize()
    scanAndRecord()
    # aThing.identify()
    print("### test thing list")
    thingsList.identify()
    print("### test find all")
    Please.find(All).identify()
    print("### test find phone")
    Please.find(All, "phone").identify()
    pass