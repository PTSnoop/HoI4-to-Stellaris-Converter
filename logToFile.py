#!/usr/bin/python

import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("output.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        pass    

sys.stdout = Logger()
sys.stderr = sys.stdout
