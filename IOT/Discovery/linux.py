import bluetooth
import urllib
import urllib.parse
import urllib.request
import json
import time
import threading
import select

from .common import *

bluewaveDevices = set()


class DeviceDiscoverer(bluetooth.DeviceDiscoverer):
    """docstring for DeviceDiscoverer"""
    done = False

    def __init__(self, manager):
        super(DeviceDiscoverer, self).__init__()
        self.manager = manager

    def pre_inquiry(self):
        self.done = False
        self.manager.thread = threading.Thread(target=self.manager.run)
        self.manager.thread.start()
        debug("scan started")

    def device_discovered(self, address, device_class, rssi, name):
        self.manager.deviceDiscovereredCallback(name.decode(), rssi)

    def inquiry_compelete(self):
        debug("inquiry_complete")
        self.done = True
        self.manager.scanningCompleteCallback()
        self.manager.thread.join()


class DeviceDiscovererManager(object):
    """docstring for DeviceDiscovererManager"""

    def __init__(self):
        super(DeviceDiscovererManager, self).__init__()
        self.deviceDiscovereredCallback = lambda x, y: None
        self.scanningCompleteCallback = lambda: None
        self.discoverer = DeviceDiscoverer(self)

    def run(self):
        while self.discoverer.done == False:
            debug("processing event")
            try:
                rfds = select.select([self.discoverer], [], [], 3)[0]
                debug("rfds get: ", rfds)
                if self.discoverer in rfds:
                    # try:
                    #     self.discoverer.process_event()
                    # except:
                    #     e = sys.exc_info()[0]
                    #     debug("process_event exception: ", e)
                    #     self.discoverer = DeviceDiscoverer(self)
                    #     self.scanningCompleteCallback()
                    self.discoverer.process_event()
                else:
                    self.discoverer.inquiry_compelete()
            except:
                e = sys.exc_info()[0]
                debug("select exception: ", e)

        debug("thread end")


class BluetoothAdapter(object):
    """docstring for BluetoothAdapter"""

    def __init__(self):
        super(BluetoothAdapter, self).__init__()
        self.manager = DeviceDiscovererManager()

    def setDeviceDiscoveredCallback(self, callback):
        self.manager.deviceDiscovereredCallback = callback

    def setScanningCompleteCallback(self, callback):
        self.manager.scanningCompleteCallback = callback

    def startScanning(self):
        debug("start scanning")
        self.manager.discoverer.find_devices()


defaultAdapter = None


class Bluetooth(object):
    """docstring for Bluetooth"""

    @staticmethod
    def getDefaultAdapter():
        global defaultAdapter
        if defaultAdapter == None:
            defaultAdapter = BluetoothAdapter()
        return defaultAdapter
