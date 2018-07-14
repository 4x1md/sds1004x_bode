'''
Created on May 4, 2018

@author: 4x1md
'''

from awgdrivers import constants
import sds1004x_bode
from sds1004x_bode import awgdrivers

class CommandParser(object):
    """
    Parses the commands sent by the oscilloscope and sends them to the AWG.
    """
    
    def __init__(self, awg):
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
        Parses and executes basic wave (BSWV) command.
        
        BSWV WVTP,SINE,PHSE,0,FRQ,50000,AMP,2,OFST,0
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
        n = 0
        while n < len(args):
            if args[n] == "ON":
                self.awg.enable_output(channel, True)
                n += 1

            elif args[n] == "LOAD":
                if args[n+1] == "HZ":
                    z = float("inf")
                else:
                    z = int(args[n+1]) 
                self.awg.set_load_impedance(channel, z)
                n += 2
            
            else:
                n += 1


if __name__ == '__main__':
    """This code is intended for testing command_parser.py module only."""
    
    from awgdrivers.dummy_awg import DummyAWG
    
    with open("../awg_commands_log.txt") as f:
        lines = f.readlines()
    
    port = "/dev/ttyUSB0"
    awg = DummyAWG()
    awg.initialize()
    
    parser = CommandParser(awg)
    
    for line in lines:
        line = line.strip()
        print line
        if line == "":
            continue
        parser.parse_scpi_command(line)
    
    pass