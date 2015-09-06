# mqttCommand.py
#
# look up mqtt commands
#
# command list
# "CAP": get capabilities
# "RUN": run a specific method
# "SUB": subscribe a specific method result
# "NES": get nest info
#
# command type
# "REQ": request
# "RES": response
import json

from .channel import send, subscribe
from threading import Semaphore
from .common import *
from random import randint

DEV_CHANNEL = "dev/"
MSG_VERSION = 1
PAYLOAD_VERSION = 1
TRANS_MIN = 0
TRANS_MAX = 1000000


class VersionError(Exception):
    pass


class FuncCallTimeOutError(Exception):
    pass


def getMessage(command, commandType, payload):
    message = {
        "command": command,
        "type": commandType,
        "payload": payload,
        "version": MSG_VERSION
    }
    return message


def sendCapReq(channel):
    payload = {
        "version": PAYLOAD_VERSION
    }
    message = getMessage("CAP", "REQ", payload)
    send(channel, json.dumps(message))


def sendCapRes(channel, types, funcList):
    payload = {
        "types": types,
        "methods": funcList,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("CAP", "RES", payload)
    send(channel, json.dumps(message))


def sendRunReq(channel, methodName, methodParameters, transID):
    payload = {
        "name": methodName,
        "parameters": methodParameters,
        "transID": transID,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("RUN", "REQ", payload)
    send(channel, json.dumps(message))


def sendRunRes(channel, methodName, methodReturn, transID):
    payload = {
        "name": methodName,
        "return": methodReturn,
        "transID": transID,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("RUN", "RES", payload)
    send(channel, json.dumps(message))


def sendSubReq(channel, methodName, methodParameters):
    payload = {
        "name": methodName,
        "parameters": methodParameters,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("SUB", "REQ", payload)
    send(channel, json.dumps(message))


def sendSubRes(channel, methodName, methodReturn):
    payload = {
        "name": methodName,
        "return": methodReturn,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("SUB", "RES", payload)
    send(channel, json.dumps(message))


def sendNesReq(channel, nestType):
    payload = {
        "type": nestType,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("NES", "REQ", payload)
    send(channel, json.dumps(message))


def sendNesRes(channel, nestType, array):
    payload = {
        "type": nestType,
        "array": array,
        "version": PAYLOAD_VERSION
    }
    message = getMessage("NES", "RES", payload)
    send(channel, json.dumps(message))


def getCallback(msgCommand, msgType, callback):
    def msgCallback(msg):
        msg = json.loads(msg.payload.decode())
        if msg["version"] == MSG_VERSION:
            if msg["command"] != msgCommand or msg["type"] != msgType:
                return
            payload = msg["payload"]
            callback(payload)
        else:
            raise VersionError
    return msgCallback


def getCapReqCallback(channel, types, funcList):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            sendCapRes(channel, types, funcList)
        else:
            raise VersionError

    return getCallback("CAP", "REQ", payloadCallback)


def getCapResCallback(callback):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            types = payload["types"]
            funcList = payload["methods"]
            callback(types, funcList)
        else:
            raise VersionError

    return getCallback("CAP", "RES", payloadCallback)


def getRunReqCallback(channel, methodName, method):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            if payload["name"] == methodName:
                parameters = payload["parameters"]
                transID = payload["transID"]
                result = method(*parameters)
                sendRunRes(channel, methodName, result, transID)
        else:
            raise VersionError

    return getCallback("RUN", "REQ", payloadCallback)


def getRunResCallback(methodName, transID, callback):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            if payload["name"] == methodName and payload["transID"] == transID:
                result = payload["return"]
                callback(result)
        else:
            raise VersionError

    return getCallback("RUN", "RES", payloadCallback)


def getSubReqCallback(channel, methodName, method):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            if payload["name"] == methodName:
                parameters = payload["parameters"]
                result = method(*parameters)
                sendSubRes(channel, methodName, result)
        else:
            raise VersionError

    return getCallback("SUB", "REQ", payloadCallback)


def getSubResCallback(methodName, callback):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            if payload["name"] == methodName:
                result = payload["return"]
                callback(result)
        else:
            raise VersionError

    return getCallback("SUB", "RES", payloadCallback)


def getNesReqCallback(channel, nestType, array):
    def payloadCallback(payload):
        if payload == PAYLOAD_VERSION:
            if payload["type"] == nestType:
                sendNesRes(channel, nestType, array)
        else:
            raise VersionError

    return getCallback("NES", "REQ", payloadCallback)


def getNesResCallback(nestType, callback):
    def payloadCallback(payload):
        if payload["version"] == PAYLOAD_VERSION:
            if payload["type"] == nestType:
                array = payload["array"]
                callback(array)
        else:
            raise VersionError

    return getCallback("NES", "RES", payloadCallback)


class MQTTHandler(object):
    """docstring for MQTTHandler"""

    def __init__(self, uuid):
        super(MQTTHandler, self).__init__()
        self.uuid = uuid
        self.channel = DEV_CHANNEL + uuid
        self.msgCallbacks = []

        # cap
        self.registeredCapabiblity = False
        self.types = []
        self.funcList = []
        self.capCallback = lambda x: None

        # nes
        self.nesting = []
        self.nested = []
        self.registeredNesting = False
        self.registeredNested = False
        self.nestingCallback = lambda x: None
        self.nestedCallback = lambda x: None

        def mqttCallback(msg):
            debug("mqtt msg received: ", msg)
            if self.registeredCapabiblity:
                self.capCallback(msg)
            if self.registeredNesting:
                self.nestingCallback(msg)
            if self.registeredNested:
                self.nestedCallback(msg)
            for msgCallback in self.msgCallbacks:
                msgCallback(msg)

        debug("subscribe to: ", self.channel)
        self.subscriber = subscribe(self.channel, mqttCallback)

    def callFunction(self, methodName, methodParameters):
        debug("callFunction: ", methodParameters)
        transID = randint(TRANS_MIN, TRANS_MAX)
        lock = Semaphore(0)
        lock.result = None

        def functionReturnCallback(returnValue):
            lock.result = returnValue
            self.msgCallbacks.remove(runResCallback)
            lock.release()

        runResCallback = getRunResCallback(methodName, transID, functionReturnCallback)
        self.msgCallbacks.append(runResCallback)
        sendRunReq(self.channel, methodName, methodParameters, transID)
        if lock.acquire(True, timeout=10):
            return lock.result
        else:
            raise FuncCallTimeOutError

    def subscribeVariable(self, name, callback):
        class subscriber(object):
            def __init__(self, handler):
                self.handler = handler
                self.subResCallback = getSubResCallback(name, callback)
                self.handler.msgCallback.append(self.subResCallback)
                sendSubReq(self.handler.channel, name, {})
            def __del__(self):
                self.handler.msgCallback.remove(self.subResCallback)
        return subscriber(self)

    def refreshCapCallback(self):
        self.capCallback = getCapReqCallback(self.channel, self.types, self.funcList)
        self.registeredCapabiblity = True
        sendCapRes(self.channel, self.types, self.funcList)

    def registerMethod(self, funcName, funcMethod, funcParameters, subscribable=False, funcDoc=""):
        runReqCallback = getRunReqCallback(self.channel, funcName, funcMethod)
        self.msgCallbacks.append(runReqCallback)
        if subscribable:
            subReqCallback = getSubReqCallback(self.channel, funcName, funcMethod)
            self.msgCallbacks.append(subReqCallback)
        funcCap = {
            "name": funcName,
            "parameters": funcParameters,
            "doc": funcDoc,
            "subscribable": subscribable
        }
        self.funcList.append(funcCap)
        self.refreshCapCallback()

    def updateSubscription(self, name, value):
        sendSubRes(self.channel, name, value)

    def registerTypes(self, types):
        if isinstance(types, str):
            self.types.append(types)
        elif isinstance(types, list):
            self.types.extend(types)
        else:
            debug("types is not str or list")
        self.refreshCapCallback()

    def gatherCapibilities(self, callback):
        capResCallback = getCapResCallback(callback)
        self.msgCallbacks.append(capResCallback)
        sendCapReq(self.channel)

    def refreshNestingCallback(self):
        self.nestingCallback = getNesReqCallback(self.channel, "nesting", self.nesting)
        self.registeredNesting = True

    def registerNestingDevice(self, uuid):
        self.nesting.append(uuid)
        self.refreshNestingCallback()

    def gatherNestingDevices(self, callback):
        nesResCallback = getNesResCallback("nesting", callback)
        self.msgCallbacks.append(nesResCallback)
        sendNesReq(self.channel, "nesting")

    def refreshNestedCallback(self):
        self.nestedCallback = getNesReqCallback(self.channel, "nested", self.nested)
        self.registeredNested = True

    def registerNestedDevice(self, uuid):
        self.nesting.append(uuid)
        self.refreshNestedCallback()

    def gatherNestedDevices(self, callback):
        nesResCallback = getNesResCallback("nested", callback)
        self.msgCallbacks.append(nesResCallback)
        sendNesReq(self.channel, "nested")