'''
Created on Apr 24, 2018

@author: 4x1md
'''

class BaseAWG(object):
    '''
    Base class defining arbitrary waveform generator and its functionality.
    '''
    SHORT_NAME = "base_awg"

    def __init__(self, *args):
        pass
    
    def connect(self):
        raise NotImplementedError()
    
    def disconnect(self):
        raise NotImplementedError()
    
    def initialize(self):
        raise NotImplementedError()
    
    def get_id(self):
        raise NotImplementedError()
    
    def enable_output(self, channel, on):
        raise NotImplementedError()
    
    def set_frequency(self, channel, freq):
        raise NotImplementedError()
        
    def set_phase(self, phase):
        raise NotImplementedError()

    def set_wave_type(self, channel, wave_type):
        raise NotImplementedError()
    
    def set_amplitue(self, channel, amplitude):
        raise NotImplementedError()
    
    def set_offset(self, channel, offset):
        raise NotImplementedError()
    
    def set_load_impedance(self, channel, z):
        raise NotImplementedError()

