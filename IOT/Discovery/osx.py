import threading
import select

from .common import *

bluewaveDevices = set()


class BluetoothAdapter(object):
    """docstring for BluetoothAdapter"""

    def __init__(self):
        super(BluetoothAdapter, self).__init__()

    def setDeviceDiscoveredCallback(self, callback):
        pass

    def setScanningCompleteCallback(self, callback):
        pass

    def startScanning(self):
        debug("start scanning")


defaultAdapter = None


class Bluetooth(object):
    """docstring for Bluetooth"""

    @staticmethod
    def getDefaultAdapter():
        global defaultAdapter
        if defaultAdapter == None:
            defaultAdapter = BluetoothAdapter()
        return defaultAdapter
