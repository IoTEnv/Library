from datetime import time, datetime
import json
import types
import time

from .common import *
from .Communication import *


class BaseThing(object):
    def __init__(self, uuid):
        super(BaseThing, self).__init__()
        self.mqttHandler = MQTTHandler(uuid)
        self._uuid = uuid
        self._func = {}
        self._type = []
        self._subscriable = {}
        self._nesting = []
        self._nested = []

    def _createType(self, type):
        self.mqttHandler.registerTypes(type)

    def _createMethod(self, funcName, funcMethod, funcParameters, funcDoc=""):
        self.mqttHandler.registerMethod(funcName, funcMethod, funcParameters, False, funcDoc)
        self._addMethod(funcName, funcMethod, funcParameters, funcDoc)

    def _createSubscriable(self, name, value, doc=""):
        self._subscriable[name] = value
        self.mqttHandler.registerMethod(name, lambda: self._getSubscriable(name), {}, doc)
        self._addSubscriable(name, lambda: self._getSubscriable(name), doc)

    def _addMethod(self, name, method, parameters, doc=""):
        self._func[name] = parameters
        method.__doc__ = doc
        setattr(self, name, types.MethodType(method, self))

    def _addType(self, type):
        if not (type in self._type):
            self._type.append(type)

    def _addSubscriable(self, name, callMethod, subscribeMethod, doc=""):
        self._func[name] = {}
        getattr(self, name, types.MethodType(callMethod, self))
        getattr(self, name).__doc__ = doc

    def _setSubscriable(self, name, value):
        self._subscriable[name] = value
        self.mqttHandler.updateSubscription(name, value)

    def _getSubscriable(self, name):
        return self._subscriable[name]

    def _updateSubscriable(self, name):
        self.mqttHandler.updateSubscription(name, self._getSubscriable(name))

    def _subscribe(self, name, callback):
        return self.mqttHandler.subscribeVariable(name, callback)

    def __str__(self):
        return "{ name: " + self._uuid + ", type: " + json.dumps(self._type) + "}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __dir__(self):
        return self._func.keys()

        # prevent Thing from throwing exception
        # def __getattr__(self, name):
        # def method(*args):
        #         warning(self, "does not support ", name)
        #     return method


class Thing(BaseThing):
    def __init__(self, uuid):
        super(Thing, self).__init__(uuid)

        def capCallback(types, funcList):
            for type in types:
                self._addType(type)
            for func in funcList:
                subscribable = func["subscribable"]
                name = func["name"]
                parameters = func["parameters"]
                doc = func["doc"]
                if subscribable:
                    def funcMethod(obj, *objs, name=name):
                        return self.mqttHandler.callFunction(name, objs)

                    self._addSubscriable(name, funcMethod, doc)
                else:
                    def funcMethod(obj, *objs, name=name):
                        return self.mqttHandler.callFunction(name, objs)

                    self._addMethod(name, funcMethod, parameters, doc)

        self.mqttHandler.gatherCapibilities(capCallback)

        self._nestingCallback = lambda x : None
        self._nestedCallback = lambda y : None

        def nestingCallback(uuid):
            self._nesting.append(ContextualThing(uuid, 0, time.time()))

        def nestedCallback(uuid):
            self._nested.append(ContextualThing(uuid, 0, time.time()))

        self.mqttHandler.gatherNestingDevices(nestingCallback)
        self.mqttHandler.gatherNestedDevices(nestedCallback)


class ContextualThing(Thing):
    def __init__(self, uuid, rssi, timestamp):
        super(ContextualThing, self).__init__(uuid)
        self._rssi = rssi
        self._timestamp = timestamp

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{ name: " + self._uuid + ", rssi: " + str(self._rssi) + ", type: " + json.dumps(
            self._type) + ", last seen: " + time.ctime(self._timestamp) + "}"

class ListedThing(ContextualThing):
    def __init__(self, uuid, rssi, timestamp, resident):
        super(ListedThing, self).__init__(uuid, rssi, timestamp)
        def nestCallback(thing):
            if isinstance(resident, set):
                resident.add(thing)
            if isinstance(resident, list):
                resident.add(thing)
        self._nestedCallback = nestCallback
        self._nestingCallback = nestCallback

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
