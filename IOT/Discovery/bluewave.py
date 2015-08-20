from os import environ

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
		if defaultManager == None:
			defaultManager = BluewaveManager()
		return defaultManager

class BluewaveManager(object):
	"""docstring for BluewaveManager"""
	def __init__(self):
		super(BluewaveManager, self).__init__()
		self.adapter = Bluetooth.getDefaultAdapter()
		self.deviceCallback = lambda x, y: None
		def scanningCompleteCallback():
			self.adapter.startScanning()
		def deviceDiscoveredCallback(name, rssi):
			nameParts = name.split("")
			if nameParts[0] == "IOT" and len(nameParts) == 2:
				uuid = nameParts[1]
				self.deviceCallback(uuid, rssi)
		self.adapter.setScanningCompleteCallback(scanningCompleteCallback)
		self.adapter.setDeviceDiscoveredCallback(deviceDiscoveredCallback)

	def setDeviceCallback(callback):
		self.deviceCallback = callback

