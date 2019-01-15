from time import time, sleep
from threading import Thread
from tkinter import *

# Read Config
queue = open('config', 'r').read().split('\n')
log = open('log', 'a')

def parse_hms(st):
    h = st.find('h')
    m = st.find('m')
    s = st.find('s')
    hours = minutes = seconds = 0
    if h != -1:
        hours = int(st[:h])
    if m != -1:
        minutes = int(st[h+1:m])
    if s != -1:
        seconds = int(st[max(m,h)+1:s])

    return hours*3600 + minutes*60 + seconds

# Countdown timer object
class Countdown:
    def __init__(self, t):
        self.returned = False
        self.returnval = 0
        self.t = t
        self.start = -1

    def tick(self):
        if self.returnval:
            return
        if self.start == -1:
            self.start = time()
        if time() - self.start >= self.t:
            self.returned = True
            self.returnval = 1
            return True
        return False


# Countup timer object
class Countup:
    def __init__(self):
        self.returned = False
        self.returnval = 0
        self.start = -1

    def tick(self):
        if self.returnval:
            return
        if self.start == -1:
            self.start = time()
        if self.returned:
            self.returnval = time() - self.start
            return True
        return False

    def stop(self):
        self.returned = True
