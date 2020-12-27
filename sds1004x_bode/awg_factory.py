'''
Created on May 15, 2018

@author: 4x1md

Update of original file on Nov. 17 2018 by Dundarave to add entries needed for FY6600 support.
'''

from awgdrivers.dummy_awg import DummyAWG
from awgdrivers.jds6600 import JDS6600
from awgdrivers.bk4075 import BK4075
from awgdrivers.fy6600 import FY6600
from awgdrivers.fy import FygenAWG

class AwgFactory(object):
    
    def __init__(self):
        self.awgs = {}
    
    def add_awg(self, short_name, awg_class):
        self.awgs[short_name] = awg_class
        
    def get_class_by_name(self, short_name):
        return self.awgs[short_name]

# Initialize factory
awg_factory = AwgFactory()
drivers = (
    DummyAWG,
    JDS6600,
    BK4075,
    FY6600,
    FygenAWG,
)
for driver in drivers:
    awg_factory.add_awg(driver.SHORT_NAME, driver)

