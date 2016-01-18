from .Discovery import *
from .thing import *
from .Communication import *
import time

nearbyDevices = set()


def init():
    initializeMQTT()
    def deviceCallback(uuid, rssi):
        # print(uuid + "discovered")
        newThing = ContextualThing(uuid, rssi, time.time())
        # print(newThing)
        if newThing in nearbyDevices:
            # print("update")
            nearbyDevices
        else:
            # print("add")
            nearbyDevices.add(newThing)
        # print(newThing)
        # filter(lambda contextualThing:
        #        True if time.time() - contextualThing._timestamp > 60 else False,
        #        nearbyDevices)

    Bluewave.getDefaultManager().setDeviceCallback(deviceCallback)


def select(rule, types=None):
    if types == None:
        return ThingsList(rule(nearbyDevices))
    elif isinstance(types, str):
        devices = []
        for device in nearbyDevices:
            if types in device._type:
                devices.append(device)
        return ThingsList(rule(devices))
    elif isinstance(types, list):
        devices = []
        for deviceType in types:
            for device in nearbyDevices:
                if deviceType in device._type:
                    devices.append(device)
        return ThingsList(rule(devices))
    else:
        warning("select error")


def selectAll(types=None):
    def all(list):
        return list

    return select(all, types)


def selectNearest(types=None):
    def nearest(list):
        contextualThings = filter(lambda thing: isinstance(thing, ContextualThing), nearbyDevices)
        return [max(contextualThings, key=lambda thing: int(thing._rssi))]

    return select(nearest, types)


def selectWithName(name, types=None):
    def withName(list):
        return filter(lambda device: device._name == name, list)

    return select(withName, types)


def selectWithUUID(uuid, types=None):
    def withUUID(list):
        return filter(lambda device: device._uuid == uuid, list)

    return select(withUUID, types)


def list():
    for device in nearbyDevices:
        print(str(device))
