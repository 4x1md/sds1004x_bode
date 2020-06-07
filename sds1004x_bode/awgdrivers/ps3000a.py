'''
Created on Jun 7, 2020

@author: Mark Watson

Driver for Picoscope 3205MSO (3000a series)
'''

import ctypes
from picosdk.ps3000a import ps3000a as ps
import time
from picosdk.functions import assert_pico_ok

from base_awg import BaseAWG
import constants
from exceptions import UnknownChannelError

CHANNELS = (0, 1)
CHANNELS_ERROR = "ps3000a has only one channel."
WAVEFORM_COMMANDS = {
    constants.SINE: ctypes.c_int16(0),
    constants.SQUARE: ctypes.c_int16(1),
    constants.PULSE: ctypes.c_int16(8), #TODO: what should this be?
    constants.TRIANGLE: ctypes.c_int16(2)
    }
# Output impedance of the AWG
R_IN = 600.0
#typedef enum enPS3000AWaveType
#{
#  PS3000A_SINE,
#  PS3000A_SQUARE,
#  PS3000A_TRIANGLE,
#  PS3000A_RAMP_UP,
#  PS3000A_RAMP_DOWN,
#  PS3000A_SINC,
#  PS3000A_GAUSSIAN,
#  PS3000A_HALF_SINE,
#  PS3000A_DC_VOLTAGE,
#  PS3000A_MAX_WAVE_TYPES
#} PS3000A_WAVE_TYPE;

class ps3000a(BaseAWG):
    '''
    Picoscope 3205MSO AWG driver
    '''
    SHORT_NAME = "ps3000a"

    def __init__(self, *args):
        self.connect()
        self.initialize()
    
    def connect(self):
        # Gives the device a handle
        self.chandle = ctypes.c_int16()
        
        # Opens the device/s
        status = {}
        status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(self.chandle), None)
        
        try:
            assert_pico_ok(status["openunit"])
        except:
        
            # powerstate becomes the status number of openunit
            powerstate = status["openunit"]
        
            # If powerstate is the same as 282 then it will run this if statement
            if powerstate == 282:
                # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
                status["ChangePowerSource"] = ps.ps3000aChangePowerSource(self.chandle, 282)
            # If the powerstate is the same as 286 then it will run this if statement
            elif powerstate == 286:
                # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
                status["ChangePowerSource"] = ps.ps3000aChangePowerSource(self.chandle, 286)
            else:
                raise
        
            assert_pico_ok(status["ChangePowerSource"])
        print ("Connected")
    
    def disconnect(self):
        status = {}
        status["close"] = ps.ps3000aCloseUnit(self.chandle)
        assert_pico_ok(status["close"])
    
    def initialize(self):
        self.wavetype = ctypes.c_int16(0) #sine
        self.frequency = 1; #1Hz
        self.amplitude = 0.001; #0.001v
        self.offsetVoltage = 0;
        z = 50
        self.v_out_coeff = z / (z + R_IN)
        self.v_out_coeff = 1.0
        self.onoff = False
    
    def get_id(self):
        return "ps3000a"
    
    def enable_output(self, channel, on):
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
# handle = chandle
# offsetVoltage = 0
# pkToPk = 2000000
# waveType = ctypes.c_int16(0) = PS3000A_SINE
# startFrequency = 10000 Hz
# stopFrequency = 10000 Hz
# increment = 0
# dwellTime = 1
# sweepType = ctypes.c_int16(1) = PS3000A_UP
# operation = 0
# shots = 0
# sweeps = 0
# triggerType = ctypes.c_int16(0) = PS3000A_SIGGEN_RISING
# triggerSource = ctypes.c_int16(0) = P3000A_SIGGEN_NONE
# extInThreshold = 1
        sweepType = ctypes.c_int32(0)
        triggertype = ctypes.c_int32(0)
        triggerSource = ctypes.c_int32(0)
        status = {}

#        print("offset,amplitude,wavetype,frequency\n")
#        print(self.offsetVoltage)
#        print(self.amplitude)
#        print(self.wavetype)
#        print(self.frequency)
        print("amplitude:" + str(self.amplitude))
        print("offset:" + str(self.offsetVoltage))
        print("v_out_coeff:" + str(self.v_out_coeff))
        amplitude = ctypes.c_uint32(int(round(self.amplitude*1000000/self.v_out_coeff)))
        offsetVoltage = ctypes.c_int32(int(round(self.offsetVoltage*1000000/self.v_out_coeff)))
        if on:
            status["SetSigGenBuiltIn"] = ps.ps3000aSetSigGenBuiltIn(self.chandle, offsetVoltage, amplitude, self.wavetype, self.frequency, self.frequency, 0, 1, sweepType, 0, 0, 0, triggertype, triggerSource, 1)
            assert_pico_ok(status["SetSigGenBuiltIn"])
            self.onoff = True
        else:
            status["SetSigGenBuiltIn"] = ps.ps3000aSetSigGenBuiltIn(self.chandle, ctypes.c_int32(0), ctypes.c_uint32(0), self.wavetype, self.frequency, self.frequency, 0, 1, sweepType, 0, 0, 0, triggertype, triggerSource, 1)
            assert_pico_ok(status["SetSigGenBuiltIn"])
            self.onoff = False
    
    def set_frequency(self, channel, freq):
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        self.frequency = ctypes.c_float(freq)
        self.enable_output(channel,self.onoff)
        
    def set_phase(self, phase):
 #       if channel is not None and channel not in CHANNELS:
 #           raise UnknownChannelError(CHANNELS_ERROR)
        pass

    def set_wave_type(self, channel, wave_type):
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        self.wavetype = WAVEFORM_COMMANDS[wave_type]
        self.enable_output(channel,self.onoff)

    def set_amplitue(self, channel, amplitude): #BSWV specifies this in pk-pk
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        self.amplitude = amplitude
        self.enable_output(channel,self.onoff)
    
    def set_offset(self, channel, offset):
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        self.offsetVoltage = offset
        self.enable_output(channel,self.onoff)
    
    def set_load_impedance(self, channel, z):
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        if z == constants.HI_Z:
            v_out_coeff = 1
        else:
            v_out_coeff = z / (z + R_IN)
        print ("Z:" + str(z))
        self.v_out_coeff = v_out_coeff
        self.enable_output(channel,self.onoff)
        pass

