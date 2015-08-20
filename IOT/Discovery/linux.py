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

class DeviceDiscoverer(bluetooth.DeviceDiscoverer):
    """docstring for DeviceDiscoverer"""
    done = False

    def __init__(self, manager):
        super(DeviceDiscoverer, self).__init__()
        self.manager = manager

    def pre_inquiry(self):
        done = False
        manager.start()
        debug("scan started")

    def device_discovered(self, address, device_class, rssi, name):
        self.manager.deviceDiscovereredCallback(name, rssi)

    def inquiry_compelete(self):
        self.manager.scanningCompleteCallback()
        self.done = True

class DeviceDiscovererManager(threading.Thread):
    """docstring for DeviceDiscovererManager"""
    def __init__(self):
        super(DeviceDiscovererManager, self).__init__()
        self.deviceDiscovereredCallback = lambda x, y: None
        self.scanningCompleteCallback = lambda : None
        self.discoverer = DeviceDiscoverer(self)

    def run(self):
        while self.discoverer.done == False:
            tfds = select.select([self.discoverer], [], [])[0]
            if self.discoverer in rfds:
                try:
                    self.discoverer.process_event()
                except:
                    e = sys.exc_info()[0]
                    debug("process_event exception: ", e)
                    self.scanningCompleteCallback()
                    self.discoverer = DeviceDiscoverer(self)


class BluetoothAdapter(object):
    """docstring for BluetoothAdapter"""
    def __init__(self):
        super(BluetoothAdapter, self).__init__()
        manager = DeviceDiscovererManager()

    def setDeviceDiscoveredCallback(callback):
        manager.deviceDiscovereredCallback = callback

    def setScanningCompleteCallback(callback):
        manager.scanningCompleteCallback = callback

    def startScanning():
        manager.discoverer.find_devices()


defaultAdapter = None

class Bluetooth(object):
    """docstring for Bluetooth"""
    @staticmethod
    def getDefaultAdapter():
        if defaultAdapter == None:
            defaultAdapter = BluetoothAdapter()
        return defaultAdapter