from time import time, sleep
from threading import Thread
from tkinter import *

# Read Config
queue = open('config', 'r').read().split('\n')

# Countdown timer object
class Countdown:
    def __init__(self):
        self.returned = False
        self.returnval = 0

    def begin(self, t):
        self.returned = False
        start = time()
        while time() - start < t:
            sleep(0.001)
        self.returned = True

    def gen_thread(self, t):
        return Thread(target=self.begin, args=t)


# Countup timer object
class Countup:
    def __init__(self):
        self.returned = False
        self.returnval = 0

    def begin(self):
        self.returned = False
        self.returnval = 0
        start = time()
        while not self.returned:
            sleep(0.001)
        self.returnval = time() - start

    def stop(self):
        self.returned = True

    def gen_thread(self):
        return Thread(target=self.begin)
