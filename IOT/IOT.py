from .bluewave import *
from .thing import *
from .communication import *

def select(rule, types = None):
    if types == None:
        return ThingsList(rule(bluewaveDevices))
    elif isinstance(types, str):
        devices = []
        for device in bluewaveDevices:
            if types in device.type:
                devices.append(device)
        return ThingsList(rule(devices))
    elif isinstance(types, list):
        devices = []
        for deviceType in types:
            for device in bluewaveDevices:
                if deviceType in device.type:
                    devices.append(device)
        return ThingsList(rule(devices))
    else:
        warning("select error")

def selectAll(types = None):
    def all(list):
        return list
    return select(all, types)

def selectNearest(types = None):
    def nearest(list):
        contextualThings = filter(lambda thing: isinstance(thing, ContextualThing), bluewaveDevices)
        return [max(contextualThings, key = lambda thing: int(thing._rssi))]
    return select(nearest, types)

def list():
    for device in bluewaveDevices:
        print(str(device))