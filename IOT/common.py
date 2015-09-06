__author__ = 'Jackie'

import sys

DEBUG = False
NAME = "IOT"
EXPIRE_TIME=60


def warning(*objs):
    print(NAME + ": WARNING: ", *objs, file=sys.stderr)


def debug(*objs):
    if DEBUG:
        print(NAME + ": DEBUG: ", *objs)