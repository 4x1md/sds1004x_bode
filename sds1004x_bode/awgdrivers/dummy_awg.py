'''
Created on Apr 24, 2018

@author: 4x1md
'''

from base_awg import BaseAWG

AWG_ID = "Dummy AWG"

class DummyAWG(BaseAWG):
    '''
    Dummy waveform generator driver.
    '''
    
    SHORT_NAME = "dummy"

    def __init__(self, *args):
        pass
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def initialize(self):
        pass
    
    def get_id(self):
        return AWG_ID
    
    def enable_output(self, channel, on):
        pass
    
    def set_channel(self, chn):
        pass
    
    def set_output(self, on=False):
        pass
    
    def set_frequency(self, channel, freq):
        pass
        
    def set_phase(self, phase):
        pass

    def set_wave_type(self, channel, wvtp):
        pass
    
    def set_amplitue(self, channel, amp):
        pass
    
    def set_offset(self, channel, offset):
        pass
    
    def set_load_impedance(self, channel, z):
        pass
    
