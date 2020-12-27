'''
Created on June 1, 2018

@author: 4x1md

@summary: Tester module which tests AWG drivers.
'''

from sds1004x_bode.awgdrivers.exceptions import UnknownChannelError
from sds1004x_bode.awgdrivers import constants
from sds1004x_bode.awg_factory import awg_factory

# Port settings constants
PORT = "/dev/ttyUSB0"
TIMEOUT = 5

if __name__ == '__main__':
    
    #awg_name = "dummy"
    #baud = None
    
    #awg_name = "jds6600"
    #baud = 115200
    
    awg_name = "fy"
    baud = 115200

    #awg_name = "fy6600"
    #baud = 19200
    
    #awg_name = "bk4075"
    #baud = 19200
    
    awg_class = awg_factory.get_class_by_name(awg_name)
    
    awg = awg_class(PORT, baud, TIMEOUT)
    awg.initialize()
    
    # Get AWG id
    awg_id = awg.get_id()
    print "AWG id: %s" % (awg_id)
    
    # Output off
    print "Setting output to off."
    awg.enable_output(0, False)
    
    # Channel 1: 257.86Hz, 1Vpp, offset 0.5V
    awg.set_wave_type(1, constants.SINE)
    awg.set_frequency(1, 7257.865243)
    awg.set_load_impedance(1, 50)
    awg.set_amplitue(1, 0.722)
    awg.set_offset(1, 0.041)
    
    try:
        # Channel 2: 35564.0493Hz, 1.5Vpp, offset -0.35V
        awg.set_wave_type(2, constants.SINE)
        awg.set_frequency(2, 35564.0493)
        awg.set_load_impedance(2, constants.HI_Z)
        awg.set_amplitue(2, 1.5)
        awg.set_offset(2, -0.35)
    except UnknownChannelError:
        print "This AWG doesn't have second channel."

    # Output on
    print "Setting output to on."
    awg.enable_output(0, True)
    
    # Disconnect
    print "Disconnecting from the AWG."
    awg.disconnect()
    
