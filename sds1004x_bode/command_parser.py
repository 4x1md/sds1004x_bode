'''
Created on May 4, 2018

@author: 4x1md
'''

from awgdrivers import constants

class CommandParser(object):
    """
    Parses the commands sent by the oscilloscope and sends them to the AWG.
    """
    
    def __init__(self, awg):
        """
        Initializes the command parses.
        Gets an instance of the initialized AWG as argument.
        """
        self.awg = awg

    def parse_scpi_command(self, line):
        """
        Parses the commands send by the oscilloscope and sends them to the AWG.
        
        Command examples:
            1. IDN-SGLT-PRI? - requests the id of the AWG.
            2. C1:OUTP LOAD,50;BSWV WVTP,SINE,PHSE,0,FRQ,50000,AMP,2,OFST,0;OUTP ON - sets
            the parameters of the AWG before performing the frequency sweep.
            3. C1:BSWV? - queries the AWG settings defined by the previous command.
            Actual implementation of the bode plot doesn't require any reply from the AWG. 
            4. C1:BSWV FRQ,10 - sets AWG frequency during the frequency sweep.
        
        If the command is a query to the AWG, it is ignored.
        """
        if line.endswith("?"):
            return

        channel = int(line[1])
        
        commands = line[3:].split(';')
        
        for command in commands:
            token = command[0:4]
            args = command[5:].split(',')
            
            if token == "BSWV":
                self.parse_bswv(args, channel)
            
            elif token == "OUTP":
                self.parse_outp(args, channel)
    
    def parse_bswv(self, args, channel):
        """
        Parses and executes the basic wave (BSWV) command which is used
        to set the wave form, frequency, amplitude, offset and phase.
        
        Examples:
            BSWV WVTP,SINE,PHSE,0,FRQ,50000,AMP,2,OFST,0
            BSWV FRQ,10.8890427
        """
        n = 0
        while n < len(args):
            if args[n] == "WVTP":
                """
                The argument of the WVTP command is not checked because
                the oscilloscope will set sine waveform only.
                """
                self.awg.set_wave_type(channel, constants.SINE)
                n += 2

            elif args[n] == "FRQ":
                freq = float(args[n+1])
                self.awg.set_frequency(channel, freq)
                n += 2

            elif args[n] == "AMP":
                ampl = float(args[n+1])
                self.awg.set_amplitue(channel, ampl)
                n += 2
            
            elif args[n] == "OFST":
                offset = float(args[n+1])
                self.awg.set_offset(channel, offset)
                n += 2
            
            elif args[n] == "PHSE":
                phase = float(args[n+1])
                self.awg.set_phase(phase)
                n += 2
            
            else:
                n += 1
    
    def parse_outp(self, args, channel):
        """
        Parses and executes the OUTP command which is used to turn the AWG output on and
        to set the load impedance of the AWG to 50 Ohm, 75 Ohm or Hi-Z.
        
        Examples:
            OUTP LOAD,50
            OUTP LOAD,75
            OUTP LOAD,HZ
            OUTP ON
            
        It seems that the oscilloscope doesn't turn the AWG output off after
        completing the plot. Even thought, the OUTP OFF command was added for
        the case it will be used in future.
        """
        n = 0
        while n < len(args):
            if args[n] == "ON":
                self.awg.enable_output(channel, True)
                n += 1

            elif args[n] == "LOAD":
                if args[n+1] == "HZ":
                    z = constants.HI_Z
                else:
                    z = int(args[n+1]) 
                self.awg.set_load_impedance(channel, z)
                n += 2
            
            elif args[n] == "OFF":
                self.awg.enable_output(channel, False)
                n += 1
            
            else:
                n += 1
