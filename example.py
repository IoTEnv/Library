import IOT
import time

IOT.initService()

notifiableThings = IOT.find(IOT.All, ["light", "speaker", "sign"])

def notify(self):
	if "speaker" in self.type:
		self.speak("You have a notification!")
	elif "light" in self.type:
		onoff, red, green, blue = self.light()
		self.light() = True, 255, 0, 0
		time.sleep(1)
		self.light() = onoff, red, green, blue
		time.sleep(1)
		self.light() = True, 255, 0, 0
		time.sleep(1)
		self.light() = onoff, red, green, blue
	elif "sign" in self.type:
		sign = self.sign()
		self.sign() = "http://notify.gif"
		time.sleep(1)
		self.sign() = sign

notifiableThings._reg("notify", notify)

