import types

from .common import *
from .communication import *

class Thing(object):
    _func = []
    def __init__(self, obj):
        super(Thing, self).__init__()
        if isinstance(obj, str):
            self._uuid = obj
            self._type = []
            self._name = ""
        elif isinstance(obj, dict):
            JSONthing = obj
            self._uuid = JSONthing["uuid"]
            self._type = []
            self._appendFeature(JSONthing)
        else:
            warning("obj is in unsupported type")

    def _appendFeature(self, JSONthing):
        self._type.extend([JSONthing["type"]])
        self._name = JSONthing["name"]
        for capName, capDes in JSONthing["capability"].items():
            def afunc(self, *request, capName = capName, capDes = capDes):
                debug(capName, capDes["command"])
                JSONrequest = copy.deepcopy(capDes["input"])
                for x in range(0, len(request)):
                    JSONrequest["TEXT"] = request[x]
                payload  = []
                debug(JSONrequest)
                if isinstance(JSONrequest, dict):
                    for key, value in JSONrequest.items():
                        payload.append(key + "=" + value)
                MQTTpayload = {
                    "contextType":IMPROMPTO_COMMAND_CONTEXT,
                    "command": capDes["command"],
                    "messageType": capDes["messageType"],
                    "version" : IMPROMPTO_PROTOCOL_VERSION,
                    "deviceID" : IMPROMPTO_DEVICE_ID,
                    "destination":[
                        self._uuid
                    ],
                    "payload": payload
                }
                debug("payload is ", json.dumps(MQTTpayload))
                response = send(capDes["channel"], json.dumps(MQTTpayload));
                return response
            setattr(self, capName, types.MethodType(afunc, self))

    def __str__(self):
        if(isinstance(self, ContextualThing)):
            return "{ name: " + self._name + ", type: " + json.dumps(self._type) + ", rssi: " + str(self._rssi) + "}"
        else:
            return "{ name: " + self._name + ", type: " + json.dumps(self._type) + "}"


    # prevent Thing from throwing exception
    def __getattr__(self, name):
        def method(*args):
            warning(self, "does not support ", name)
        return method

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return hash(self) == hash(other)

class ThingsList(list):
    """docstring for ThingList"""

    # dispatch the method to the list
    def __getattr__(self, name):
        def method(*args):
            for obj in self:
                getattr(obj, name)(*args)
        return method

class ContextualThing(Thing):
    """docstring for ContextualThing"""
    def __init__(self, JSONthing, timestamp, rssi):
        super(ContextualThing, self).__init__(JSONthing)
        self._timestamp = timestamp
        self._rssi = rssi