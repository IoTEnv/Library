__author__ = 'Jackie'

from .Discovery import initializeBluewave
from .Communication import initializeMQTT
from .IOT import *
from .thing import Thing, ThingsList

def initialize():
    initializeMQTT()
    initializeBluewave()