import IOT
import random
import time

IOT.initialize()

def isAdrianAround():
    return len(IOT.selectWithName("Nexus 5-A")) == 1

def adrianDis():
    return int(IOT.selectWithName("Nexus 5-A")[0]._rssi)

def notify(devices):
    for device in devices:
        if "speaker" in device._type:
            device.speak("Adrian is around you!!!")
        if "lights" in device._type:
            device.setLights("true", str(random.randint(0, 255)), str(random.randint(0, 255)), str(random.randint(0, 255)))

def notifyMe(urgent):
    if urgent:
        notify(IOT.selectAll())
    else:
        notify(IOT.selectNearest())

while True:
    if isAdrianAround():
        print("Adrian is around " + adrianDis())
    if isAdrianAround() and adrianDis() > -75:
        if adrianDis() > -65:
            notifyMe(True)
        else:
            notifyMe(False)
    time.sleep(2)
# while True:
#     notifyMe(True)
#     # IOT.selectAll().notify()
#     IOT.initializeMQTT()
#     time.sleep(5)