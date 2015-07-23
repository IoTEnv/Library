__author__ = 'Jackie'

from .bluewave import initializeBluewave
from .communication import initializeMQTT
from .IOT import *
from .thing import Thing, ThingsList

def initialize():
    initializeMQTT()
    initializeBluewave()