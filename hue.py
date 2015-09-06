__author__ = 'Jackie'
from phue import Bridge
import IOT

IOT.initializeMQTT()

SERVER_ADDRESS = "192.168.1.100"

b = Bridge(SERVER_ADDRESS)
b.connect()

def setBrightness(obj, x):
    obj.brightness = x

hue_light1 = b.lights[0]
light1 = IOT.Thing("light1")

light1._createType("light")

light1._createMethod("turn", lambda x: setBrightness(hue_light1, 255 if x else 0),{}, "turn on or off light")
light1._createMethod("light", lambda: hue_light1.brightness,{}, "get the brightness")
light1._createMethod("brightness", lambda x: setBrightness(hue_light1, x), {}, "set the brightness of the light")

hue_light2 = b.lights[1]
light2 = IOT.Thing("light2")

light2._createType("light")

light2._createMethod("turn", lambda x: setBrightness(hue_light2, 255 if x else 0),{}, "turn on or off light")
light2._createMethod("light", lambda: hue_light2.brightness,{}, "get the brightness")
light2._createMethod("brightness", lambda x: setBrightness(hue_light2, x), {}, "set the brightness of the light")

while True:
    pass