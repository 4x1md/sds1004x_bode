'''
Created on May 4, 2018

@author: 4x1md

@note: Tests the command_parser.py module.
'''

from sds1004x_bode.command_parser import CommandParser
from sds1004x_bode.awgdrivers.dummy_awg import DummyAWG


if __name__ == '__main__':
    with open("awg_commands_log.txt") as f:
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
    