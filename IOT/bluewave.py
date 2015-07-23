import bluetooth
import urllib
import urllib.parse
import urllib.request
import json
import time

from .common import *
from .thing import *

bluewaveDevices = set()
BluewaveDiscoverDeamonEnabled = False

class BluewaveDiscoverer(bluetooth.DeviceDiscoverer):
    """docstring for BluewaveDiscoverer"""

    def __init__(self, completeCallback):
        super(BluewaveDiscoverer, self).__init__()
        self.completeCallback = completeCallback

    def device_discovered (self, address, device_class, psrm, pspm, clockoff, rssi, name):
        splittedName = name.split('::')
        if len(splittedName) == 4 and splittedName[0] == "GCF":
            deviceName = splittedName[1]
            deviceURL = splittedName[2]
            deviceKey = splittedName[3]
            requestPayload = {
                "deviceID": deviceName,
                "appID": IMPROMPTO_APP_ID,
                "key": deviceKey,
                "context[]": IMPROMPTO_IOT_CONTEXT
            }
            encodedPayload = urllib.parse.urlencode(requestPayload)
            fullURL = deviceURL + "?" + encodedPayload
            data = urllib.request.urlopen(fullURL)
            deviceProfile = json.loads(data.read().decode("UTF-8"))
            if "IOT" in deviceProfile.keys():
                deviceProfile = deviceProfile["IOT"]
                deviceProfile["uuid"] = deviceName
                deviceProfile["name"] = deviceName
                if "nested" in deviceProfile.keys():
                    warning("nested is not yet implemented!")
                bluewaveDevices.add(ContextualThing(deviceProfile, time.time()))

    def inquiry_complete(self):
        self.completeCallback()

class BluewaveDiscoveryDeamon(object):
    """docstring for BlueWaveDiscoveryDeamon"""
    def __init__(self):
        super(BluewaveDiscoveryDeamon, self).__init__()
        self.discoverer = BluewaveDiscoverer(lambda: self.discoverer.find_devices())
        self.discoverer.find_devices()

deamon = None

def initializeBluewave():
    deamon = BluewaveDiscoveryDeamon()