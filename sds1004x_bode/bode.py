'''
Created on May 5, 2018

@author: dima
'''

import sys
from awg_server import AwgServer
from awg_factory import awg_factory

if __name__ == '__main__':
    # Extract AWG name from parameters
    if len(sys.argv) >= 2:
        awg_name = sys.argv[1]
    else:
        awg_name = "dummy"
        
    # Extract port name from parameters
    if len(sys.argv) >= 3:
        awg_port = sys.argv[2]
    else:
        awg_port = None
        
    # Extract AWG port baud rate from parameters
    if len(sys.argv) == 4:
        awg_baud_rate = int(sys.argv[3])
    else:
        awg_baud_rate = None  
    
    # Initialize AWG
    print "Initializing AWG..."
    print "AWG: %s" % awg_name
    print "Port: %s" % awg_port
    awg_class = awg_factory.get_class_by_name(awg_name)
    awg = awg_class(awg_port, awg_baud_rate)
    awg.initialize()
    
    # Run AWG server
    server = None
    try:
        server = AwgServer(awg)
        server.start()
    
    except KeyboardInterrupt:
        print('Ctrl+C pressed. Exiting...')
    
    finally:
        if server is not None:
            server.close_sockets()
    
    print "Bye."
    