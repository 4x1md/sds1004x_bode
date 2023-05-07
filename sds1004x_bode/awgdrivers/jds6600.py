'''
Created on Apr 24, 2018

@author: 4x1md

Driver for JDS6600 AWG.
'''

import serial
import time
from .base_awg import BaseAWG
from . import constants
from .exceptions import UnknownChannelError

# Port settings constants
BAUD_RATE = 115200
BITS = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
TIMEOUT = 5

# Data packet ends with CR LF (\r\n) characters
EOL = b'\x0D\x0A'
# Channels validation tuple
CHANNELS = (0, 1, 2)
CHANNELS_ERROR = "Channel can be 1 or 2."
# JDS6600 requires some delay between commands. 15msec seem to be enough.
SLEEP_TIME = 0.015

# Output impedance of the AWG
R_IN = 50.0

class JDS6600(BaseAWG):
    '''
    JDS6600 function generator driver.
    '''    
    SHORT_NAME = "jds6600"

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
        self.send_command(":r01=0.")
        ans = self.ser.read_until(terminator=".\r\n", size=None)
        ans = ans.replace(":ok", "")
        ans = ans.strip()
        return ans.strip()
    
    def enable_output(self, channel=None, on=False):
        """
        Turns channels output on or off.
        The channel is defined by channel variable. If channel is None, both channels are set.
        
        Commands
            :w20=0,0.
            :w20=0,1.
            :w20=1,1.
        enable outputs of channels 1, 2 and of both accordingly.
        
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        if channel is not None and channel != 0:
            self.channel_on[channel-1] = on
        else:
            self.channel_on = [on, on]
        
        ch1 = "1" if self.channel_on[0] == True else "0"
        ch2 = "1" if self.channel_on[1] == True else "0"
        cmd = ":w20=%s,%s." % (ch1, ch2)
        self.send_command(cmd)
    
    def set_frequency(self, channel, freq):
        """
        Sets frequency on the selected channel.
        
        Command examples:
            :w23=25786,0.
                sets the output frequency of channel 1 to 2578.6Hz.
            :w23=25786,1.
                sets the output frequency of channel 1 to 2578.6kHz.
            :w24=25786,3.
                sets the output frequency of channel 2 to 25.786mHz.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        freq_str = "%.2f" % freq
        freq_str = freq_str.replace(".", "")

        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = ":w23=%s,0." % freq_str
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = ":w24=%s,0." % freq_str
            self.send_command(cmd)
        
    def set_phase(self, phase):
        """
        Sends the phase setting command to the generator.
        The phase is set on channel 2 only.
        
        Commands
            :w31=100. 
            :w31=360.
        sets the phase to 10 and 0 degrees accordingly.
        For negative values 360 degrees are considered zero point.
        """
        if phase < 0:
            phase += 360
        phase = int(round(phase * 10))
        cmd = ":w31=%s." % (phase)
        self.send_command(cmd)

    def set_wave_type(self, channel, wave_type):
        """
        Sets wave type of the selected channel.
        
        Commands
            :w21=0.
            :w22=0.
        set wave forms of channels 1 and 2 accordingly to sine wave.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        if not wave_type in constants.WAVE_TYPES:
            raise ValueError("Incorrect wave type.")
        
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = ":w21=%s." % wave_type
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = ":w22=%s." % wave_type
            self.send_command(cmd)
        
    def set_amplitue(self, channel, amplitude):
        """
        Sets amplitude of the selected channel.
        
        Commands
            :w25=30.
            :w26=30.
        set amplitudes of channel 1 and channel 2 accordingly to 0.03V.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        """
        Adjust the output amplitude to obtain the requested amplitude
        on the defined load impedance.
        """
        amplitude = amplitude / self.v_out_coeff[channel-1] 
        
        amp_str = "%.3f" % amplitude
        amp_str = amp_str.replace(".", "")
        
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = ":w25=%s." % amp_str
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = ":w26=%s." % amp_str
            self.send_command(cmd)
    
    def set_offset(self, channel, offset):
        """
        Sets DC offset of the selected channel.
        
        Command examples:
            :w27=9999.    
                sets the offset of channel 1 to 9.99V.
            :w27=1000. 
                sets the offset of channel 1 to 0V.
            :w28=1. 
                sets the offset of channel 2 to -9.99V.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)
        
        # Adjust the offset to the defined load impedance
        offset = offset / self.v_out_coeff[channel-1] 
        
        offset_val = 1000 + int(offset * 100)
        
        # Channel 1
        if channel in (0, 1) or channel is None:
            cmd = ":w27=%s." % offset_val
            self.send_command(cmd)
        
        # Channel 2
        if channel in (0, 2) or channel is None:
            cmd = ":w28=%s." % offset_val
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
    print("This module shouldn't be run. Run awg_tests.py instead.")
