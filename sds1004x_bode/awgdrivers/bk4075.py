'''
Created on Apr 24, 2018

@author: 4x1md

Driver for BK Precision BK4075 AWG.
'''

import serial
import time
from base_awg import BaseAWG
import constants
from exceptions import UnknownChannelError

# Port settings
BAUD_RATES = (2400, 4800, 9600, 19200)
DEFAULT_BAUD_RATE = 19200
BITS = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
TIMEOUT = 2

# Data packet ends with CR LF (\r \n) characters
EOL = '\x0D\x0A'

# Channels validation tuple
CHANNELS = (0, 1)
CHANNELS_ERROR = "BK4075 has only one channel."
WAVEFORM_COMMANDS = {
    constants.SINE: ":SOUR:FUNC SIN",
    constants.SQUARE: ":SOUR:FUNC SQU",
    constants.PULSE: ":SOUR:FUNC PUL",
    constants.TRIANGLE: ":SOUR:FUNC TRI"
    }
# Delay between commands. BK4075 doesn't seem to need it.
SLEEP_TIME = 0.005

# Default AWG settings
DEFAULT_LOAD = 50
DEFAULT_OUTPUT_ON = False

# Output impedance of the AWG
R_IN = 50.0

class BK4075(BaseAWG):
    '''
    BK Precision 4075 generator driver.
    https://www.bkprecision.com/products/discontinued/4075-25-mhz-arbitrary-waveform-function-generator.html
    '''
    SHORT_NAME = "bk4075"

    def __init__(self, port, baud_rate=DEFAULT_BAUD_RATE, timeout=TIMEOUT):
        if not baud_rate in BAUD_RATES:
            raise ValueError("Baud rate must be 2400, 4800, 9600 or 19200 bps.")
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
    
    def connect(self):
        self.ser = serial.Serial(self.port, self.baud_rate, BITS, PARITY, STOP_BITS, timeout=self.timeout)
    
    def disconnect(self):
        self.ser.close()
        
    def send_command(self, cmd):
        self.ser.write(cmd)
        self.ser.write(EOL)
        time.sleep(SLEEP_TIME)
        
    def initialize(self):
        self.connect()
        self.send_command("SYST:SCR ON")
        self.r_load = DEFAULT_LOAD
        self.v_out_coeff = 1.0
        self.output_on = DEFAULT_OUTPUT_ON
        self.enable_output(1, self.output_on)
        
    def get_id(self):
        self.ser.reset_input_buffer()
        self.send_command("*IDN?")
        time.sleep(SLEEP_TIME)
        ans = self.ser.read_until(terminator=EOL, size=None)
        return ans.strip()
        
    def enable_output(self, channel=None, on=False):
        """
        Turns the output on or off.

        Syntax: :OUTPut[:STATe]<ws>ON|1|OFF|0
        Examples:
            :OUTP:STAT ON
            :OUTP OFF
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        self.output_on = on
        
        if self.output_on:
            self.send_command(":OUTP:STAT ON")
        else:
            self.send_command(":OUTP:STAT OFF")
            
    def set_frequency(self, channel, freq):
        """
        Sets output frequency.
        
        Syntax:
            [:SOURce]:FREQuency[:CW]<ws><frequency>[units]
            [:SOURce]:FREQuency<ws>MINimum|MAXimum
        Examples: :FREQ 5KHZ
            :FREQ 5E3
            :FREQ MAXIMUM
            :FREQ MIN
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        freq_str = "%.10f" % freq
        cmd = ":FREQ %s" % (freq_str)
        self.send_command(cmd)
        
    def set_phase(self, phase):
        """
        BK4075 does not require setting phase.
        """
        pass

    def set_wave_type(self, channel, wave_type):
        """
        Sets the output wave type.
        
        Syntax:
            [:SOURce]:FUNCtion[:SHAPe]<WS><OPTION>
        Available functions:
            SINusoid, Square, TRIangle, ARBitrary, PULse
            SIN|TRI|SQU|ARB|PUL
        Examples: 
            :FUNC SIN
            :FUNC ARB
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        if not wave_type in constants.WAVE_TYPES:
            raise ValueError("Incorrect wave type.")
        
        cmd = WAVEFORM_COMMANDS[wave_type]
        self.send_command(cmd)
    
    def set_amplitue(self, channel, amplitude):
        """
        Sets output amplitude.
        
        Syntax:
            [:SOURce]:VOLTage:AMPLitude<ws><amplitude>[units]
            [:SOURce]:VOLTage:AMPLitude<ws>MINimum|MAXimum
        Examples:
            :VOLT:AMPL 2.5
            :VOLT:AMPL 2.5V
            :VOLT:AMPL MAX
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        # Adjust the amplitude to the defined load impedance
        amplitude = amplitude * self.v_out_coeff
        
        amp_str = "%.3f" % amplitude
        cmd = ":VOLT:AMPL %s" % (amp_str)
        self.send_command(cmd)
    
    def set_offset(self, channel, offset):
        """
        Sets DC offset of the output.
        
        Syntax:
            [:SOURce]:VOLTage:OFFSet<ws><offset>[units]
            [:SOURce]:VOLTage:OFFSet<ws>MINimum|MAXimum
        Examples:
            :VOLT:OFFS 2.5
            :VOLT:OFFS 2.5V
            :VOLT:OFFS MAX
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        # Adjust the offset voltage to match the defined load impedance 
        offset = offset * self.v_out_coeff
        
        cmd = ":VOLT:OFFS %s" % (offset)
        self.send_command(cmd)
        
    def set_load_impedance(self, channel, z):
        """
        Sets load impedance connected to each channel. Default value is 50 Ohms.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        self.r_load = z
        
        """
        The voltage amplitude which is requestd from the AWG by the
        oscilloscope is the actual peak-to-peak amplitude.
        The actual output of BK4075 is twice the defined value because it
        supposes that it is loaded with 50 Ohm and half of the output voltage
        will fall on the internal impedance which is also 50 Ohm.
        If the connected load has other impedance, the output amplitude must
        be adjusted.
        For example, in order to obtain 1Vp-p on a Hi-Z load, the amplitude
        defined on BK405 must be 0.5Vp-p. For other load impedances it must
        be adjusted accordingly. 
        v_out_coeff variable stores the coefficient by which the amplitude
        defined by the oscilloscope will be multiplied before sending it
        to the AWG. 
        """
        if self.r_load == constants.HI_Z:
            self.v_out_coeff = 0.5
        else:        
            self.v_out_coeff = 0.5 * (self.r_load + R_IN) / self.r_load 

if __name__ == '__main__':
    print "This module shouldn't be run. Run awg_tests.py instead."
