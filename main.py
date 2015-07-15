import json
import copy

def sendRequest(url, obj, request):
	print "sendRequest BEGIN"
	print url
	print obj
	print request
	"""send the request"""
	print "sendRequest END"
	return {"result" : "finished", }

def scanThings():
	print "scanThings CALLED"
	"""scan the things"""
	f.open("./Schema/example.json")
	print f
	scanResult = f.read()
	print "scanThings ENDED"
	return scanResult

class Thing(object):
	"""docstring for Thing"""
	def __init__(self, json):
		super(Thing, self).__init__()
		self._uuid = json["@uuid"]
		self._type = json["@type"]
		self._name = json["@name"]
		for capName, capDes in json["@cap"].iternames():
			def function(*request):
				JSONrequest = capDes["input"].deepcopy()
				for x in xrange(0, len(args) - 1):
					JSONrequest.values()[x] = args[x]
					JSONresponse = sendRequest(capDes["url"], self, json.dumps(JSONrequest));
					response = json.loads(JSONresponse)
					return response

class That(object):
	"""docstring for That"""
	def __init__(self, arg):
		super(That, self).__init__()
		self.arg = arg
	@staticmethod
	def find(rule):
		pass

def main():
	print scanThings();
	pass