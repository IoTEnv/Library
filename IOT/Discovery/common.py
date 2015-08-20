__author__ = 'Jackie'

import sys

DEBUG = False
NAME = "Discovery"

def warning(*objs):
    print(NAME + ": WARNING: ", *objs, file=sys.stderr)

def debug(*objs):
    if DEBUG == True:
        print(NAME + ": DEBUG: ", *objs)