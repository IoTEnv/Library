import types

from .common import *
from .mqtt import *

class Thing(object):
    def __init__(self, obj):
        super(Thing, self).__init__()
        self._func = {}
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
                    JSONrequest[list(JSONrequest.keys())[x]] = request[x]
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
                debug("payload is ", jsonEncode(MQTTpayload))
                response = send(capDes["channel"], jsonEncode(MQTTpayload));
                return response
            self._func[capName] = afunc
            setattr(self, capName, types.MethodType(afunc, self))

    def __str__(self):
        if(isinstance(self, ContextualThing)):
            return "{ name: " + self._name + ", rssi: " + str(self._rssi) + ", type: " + jsonEncode(self._type) + ", lastseen: " + time.ctime(self._timestamp) + "}"
        else:
            return "{ name: " + self._name + ", type: " + jsonEncode(self._type) + "}"

    def __repr__(self):
        return "<" + str(self) + ">"

    # prevent Thing from throwing exception
    # def __getattr__(self, name):
    #     def method(*args):
    #         warning(self, "does not support ", name)
    #     return method

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __dir__(self):
        return self._func.keys()

class ThingsList(object):
    """docstring for ThingList"""

    def __init__(self, *objs):
        super(ThingsList, self).__init__()
        self.l = list(*objs)

    # dispatch the method to the list
    def __getattr__(self, name):
        def method(*args):
            for obj in self.l:
                getattr(obj, name)(*args)
        return method

    def __dir__(self):
        funclist = (set(device.__dir__()) for device in self.l)
        return set.intersection(*funclist)

    def __str__(self):
        return self.l.__str__()

    def __repr__(self):
        return self.l.__str__()

    def __iter__(self):
        return self.l.__iter__()

    def __getitem__(self, key):
        return self.l.__getitem__(key)

    def __len__(self):
        return self.l.__len__()

class ContextualThing(Thing):
    """docstring for ContextualThing"""
    def __init__(self, JSONthing, timestamp, rssi):
        super(ContextualThing, self).__init__(JSONthing)
        self._timestamp = timestamp
        self._rssi = rssi
