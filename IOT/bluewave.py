import bluetooth
import urllib
import urllib.parse
import urllib.request
import json
import time
import threading
import select

from .common import *
from .thing import *

bluewaveDevices = set()

class BluewaveDiscoverer(bluetooth.DeviceDiscoverer):
    """docstring for BluewaveDiscoverer"""

    # def __init__(self, completeCallback):
    #     super(BluewaveDiscoverer, self).__init__()
    #     self.completeCallback = completeCallback
    done = False
    def pre_inquiry(self):
        self.done = False
        # debug("scan started")

    def device_discovered (self, address, device_class, rssi, name):
        try:
            debug("device found: ", name, rssi)
            name = name.decode("ISO-8859-1")
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
                    bluewaveDevices.add(ContextualThing(deviceProfile, time.time(), rssi))
        except:
            e = sys.exc_info()[0]
            debug("device_discovered exception: ", e)


    def inquiry_complete(self):
        self.done = True
        # debug("scan completed")

class BluewaveDiscoveryDeamon(threading.Thread):
    """docstring for BlueWaveDiscoveryDeamon"""
    def __init__(self):
        super(BluewaveDiscoveryDeamon, self).__init__()
        self.discoverer = BluewaveDiscoverer()
        debug("deamon started")
        self.discoverer.find_devices()
        self.start()

    def run(self):
        while True:
            rfds = select.select([self.discoverer], [], [])[0]
            if self.discoverer in rfds:
                try:
                    self.discoverer.process_event()
                except:
                    e = sys.exc_info()[0]
                    debug("process_event exception: ", e)
                    deamon = BluewaveDiscoveryDeamon()

            if self.discoverer.done:
                self.discoverer.find_devices()


deamon = None

def initializeBluewave():
    deamon = BluewaveDiscoveryDeamon()