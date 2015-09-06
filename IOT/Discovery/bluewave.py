from os import environ
from .common import *

ANDROID = 'ANDROID_STORAGE' in environ

if ANDROID:
    from .android import Bluetooth
else:
    from .linux import Bluetooth

defaultManager = None

class Bluewave(object):
    """docstring for Bluewave"""

    @staticmethod
    def getDefaultManager():
        global defaultManager
        if defaultManager == None:
            defaultManager = BluewaveManager()
        return defaultManager


class BluewaveManager(object):
    """docstring for BluewaveManager"""

    def __init__(self):
        super(BluewaveManager, self).__init__()
        debug("BluewaveManager initialized!")
        self.adapter = Bluetooth.getDefaultAdapter()
        self.deviceCallback = lambda x, y: None

        def scanningCompleteCallback():
            debug("scanning complete")
            self.adapter.startScanning()

        def deviceDiscoveredCallback(name, rssi):
            nameParts = name.split("::")
            if nameParts[0] == "IOT" and len(nameParts) == 2:
                uuid = nameParts[1]
                debug("device found: ", uuid, " ", rssi)
                self.deviceCallback(uuid, rssi)

        self.adapter.setScanningCompleteCallback(scanningCompleteCallback)
        self.adapter.setDeviceDiscoveredCallback(deviceDiscoveredCallback)
        self.adapter.startScanning()

    def setDeviceCallback(self, callback):
        self.deviceCallback = callback

