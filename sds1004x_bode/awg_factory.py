'''
Created on May 15, 2018

@author: 4x1md
'''

from awgdrivers.dummy_awg import DummyAWG
from awgdrivers.jds6600 import JDS6600
from awgdrivers.bk4075 import BK4075

# from dummy_awg import DummyAWG
# from jds6600 import JDS6600
# from bk4075 import BK4075

class AwgFactory(object):
    
    def __init__(self):
        self.awgs = {}
    
    def add_awg(self, short_name, awg_class):
        self.awgs[short_name] = awg_class
        
    def get_class_by_name(self, short_name):
        return self.awgs[short_name]

# Initialize factory
awg_factory = AwgFactory()
awg_factory.add_awg(DummyAWG.SHORT_NAME, DummyAWG)
awg_factory.add_awg(JDS6600.SHORT_NAME, JDS6600)
awg_factory.add_awg(BK4075.SHORT_NAME, BK4075)
