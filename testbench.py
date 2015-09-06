__author__ = 'Jackie'
import IOT
IOT.init()
thing = IOT.Thing("thing")
thing._createMethod("identify", lambda: print("hello world"), {})
thing._createMethod("print", lambda x: print(x), {"text":"string"})
anotherThing = IOT.Thing("thing")