'''
Created on November 20, 2019

@author: Dundarave

Driver for FeelTech FY6600 AWG.
'''

import serial
import time
from base_awg import BaseAWG
import constants
from exceptions import UnknownChannelError

# Port settings constants
BAUD_RATE = 115200
BITS = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
TIMEOUT = 5

# FY6600 Data packet ends with just a single LF (\n) character
EOL = '\x0A'
# Channels validation tuple
CHANNELS = (0, 1, 2)
CHANNELS_ERROR = "Channel can be 1 or 2."
# FY6600 requires some delay between commands. 0.5 seconds seems to work, .25 seconds is iffy. Your unit might need more.
SLEEP_TIME = 0.5

# Output impedance of the AWG
R_IN = 50.0

class FY6600(BaseAWG):
    '''
    FY6600 function generator driver.
    '''    
    SHORT_NAME = "fy6600"

    def __init__(self, port, baud_rate=BAUD_RATE, timeout=TIMEOUT):
        """baud_rate parameter is ignored."""
        self.port = port
        self.ser = None
        self.timeout = timeout
        self.channel_on = [False, False]
        self.r_load = [50, 50]
        self.v_out_coeff = [1, 1]
    
    def connect(self):
        self.ser = serial.Serial(self.port, BAUD_RATE, BITS, PARITY, STOP_BITS, timeout=self.timeout)
    
    def disconnect(self):
        self.ser.close()
        
    def send_command(self, cmd):
        self.ser.write(cmd)
        self.ser.write(EOL)
        time.sleep(SLEEP_TIME)
        
    def initialize(self):
        self.channel_on = [False, False]
        self.connect()
        self.enable_output()
    
    def get_id(self):
        self.send_command("UID")
        ans = self.ser.read_until(terminator="\r\n", size=None)
        return ans

    def enable_output(self, channel=None, on=False):
        """
        Turns channels output on or off.
        The channel is defined by channel variable. If channel is None, both channels are set.
        
        Commands:        
            WMN1 means main wave output set to on
            WMN0 means main wave output set to off
            WFN1 means second channel wave output set to on
            WFN0 means second channel wave output set to off

        Separate commands are thus needed to set the channels for the FY6600.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        if channel is not None and channel != 0:
            self.channel_on[channel-1] = on
        else:
            self.channel_on = [on, on]
        
        ch1 = "1" if self.channel_on[0] == True else "0"
        ch2 = "1" if self.channel_on[1] == True else "0"
        
        # The fy6600 uses separate commands to enable each channel.
        cmd = "WMN%s" % (ch1)
        self.send_command(cmd)
        cmd = "WFN%s" % (ch2)
        self.send_command(cmd)

    def set_frequency(self, channel, freq):
        """
        Sets frequency on the selected channel.
        
        Command examples:        
            WMF00000000000001 equals 1 uHz on channel 1
            WMF00000001000000 equals 1 Hz on channel 1
            WMF00001000000000 equals 1 kHz on channel 1
            WFF00000000000001 equals 1 uHz on channel 2
            and so on.
        """
        
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        freq_str = "%.2f" % freq
        freq_str = freq_str.replace(".", "")
        freq_str = freq_str + "0000"
       
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = "WMF%s" % freq_str
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) :
            cmd = "WFF%s" % freq_str
            self.send_command(cmd)
        
        
    def set_phase(self, phase):
        """
        Sends the phase setting command to the generator.
        The phase is set on channel 2 only.
        
        Commands:
            WMP100.0 is 100.0 degrees on Channel 1
            WFP4.9 is 4.9 degrees on Channel 2. We are only setting phase on channel 2 here.
        """
        if phase < 0:
            phase += 360

        cmd = "WFP%s" % (phase)
        self.send_command(cmd)

    def set_wave_type(self, channel, wave_type):
        """
        Sets wave type of the selected channel.
        
        Commands:
            WMW00 for Sine wave channel 1
            WFW00 for Sine wave channel 2
        Both commands are "hard-coded".
       """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        if not wave_type in constants.WAVE_TYPES:
            raise ValueError("Incorrect wave type.")
        
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = "WMW00"
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = "WFW00"
            self.send_command(cmd)
        
    def set_amplitue(self, channel, amplitude):
        """
        Sets amplitude of the selected channel.
        
        Commands:
            WMA0.44 for 0.44 volts Channel 1
            WFA9.87 for 9.87 volts Channel 2
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        """
        Adjust the output amplitude to obtain the requested amplitude
        on the defined load impedance.
        """
        amplitude = amplitude / self.v_out_coeff[channel-1] 
        amp_str = "%.3f" % amplitude
        
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = "WMA%s" % amp_str
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = "WFA%s" % amp_str
            self.send_command(cmd)
    
    def set_offset(self, channel, offset):
        """
        Sets DC offset of the selected channel.
        
        Command examples:
        WMO0.33 sets channel 1 offset to 0.33 volts
        WFO-3.33sets channel 2 offset to -3.33 volts
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        # Adjust the offset to the defined load impedance
        offset = offset / self.v_out_coeff[channel-1] 
        
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = "WMO%s" % offset
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = "WFO%s" % offset
            self.send_command(cmd)
        
    def set_load_impedance(self, channel, z):
        """
        Sets load impedance connected to each channel. Default value is 50 Ohm.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        self.r_load[channel-1] = z
        
        """
        Vout coefficient defines how the requestd amplitude must be increased
        in order to obtain the requested amplitude on the defined load.
        If the load is Hi-Z, the amplitude must not be increased.
        If the load is 50 Ohm, the amplitude has to be double of the requested
        value, because of the voltage divider between the output impedance
        and the load impedance.
        """
        if z == constants.HI_Z:
            v_out_coeff = 1
        else:
            v_out_coeff = z / (z + R_IN)
        self.v_out_coeff[channel-1] = v_out_coeff
    
if __name__ == '__main__':
    print "This module shouldn't be run. Run awg_tests.py instead."
