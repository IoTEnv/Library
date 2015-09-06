import sys

serverAddress = "epiwork.hcii.cs.cmu.edu"
# serverAddress = "bluetest.yangjunrui.com"
serverPort = 1883
DEBUG = False
clientID = None
NAME = "MQTT"

def warning(*objs):
    print(NAME + ": WARNING: ", *objs, file=sys.stderr)

def debug(*objs):
    if DEBUG == True:
        print(NAME + ": DEBUG: ", *objs)