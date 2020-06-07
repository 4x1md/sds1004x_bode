# Siglent SDS1004X-E Bode Plot
Bode plot with Siglent SDS1004X-E oscilloscopes and a non-siglent AWG.

## Overview
At a certain point after getting the SDG1204X-E oscilloscope I started to wonder if it might be possible to use the Bode plot function with a non-Siglent waveform generator. After some hours of researching and reverse engineering I wrote this Python program which is a small server which emulates Siglent arbitrary waveform generator.

The oscilloscope connects using LAN to a PC running this program. The program makes the oscilloscope think that it communicates with a genuine Siglent signal generator. The program extracts the commands sent to the generator, parses them and translates to the command set, which can be understood by the connected to the PC non-Siglent generator.

The program is written in Python and uses ```sockets``` library to connect to the oscilloscope and ```serial``` library for connecting to AWG.

Current version of the program was tested under Linux only. Later, I'll test it under Windows too.

## Supported AWG Models

As of June 7, 2020 the program supports the following models:

* **BK Precision BK4075** One channel 25MHz AWG. Requires a RS-232 serial port for the connection to a PC. It is compatible with the SCPI 1992.0 standard.

* **RD JDS6600** Chinese generator which is widely sold on eBay and AliExpress. It connects to the PC as a USB serial port.

* **Feeltech FY6600** Another Chinese generator which is widely sold on eBay and AliExpress. It also connects to the PC as a USB serial port.

* **Picoscope 3000a series** It connects to the PC usb support and their is an API that needs downloading from Picotech. Tested with Picoscope 3205 MSO only.

## Program Structure
TBD

## Oscilloscope Configuration
Before starting the program you have to tell the oscilloscope how to connect to the waveform generator. Connect your oscilloscope to the same network where your PC is connected. Then go to ```Configure => AWG I/O``` in the Bode plot settings. Define LAN connection and the IP addres of your PC as the AWG IP. After starting the program you can press ```Test Connection``` button to test the communication between the oscilloscope and the PC.

## Running The Program
To run this program you must have Python 2.7 installed.

The source code is located in the [```sds1004x_bode```](https://github.com/4x1md/sds1004x_bode/tree/master/sds1004x_bode) directory of this repository.

Python ```sockets``` requires elevated privileges in Linux, therefore the program has to be run with ```su``` or ```sudo``` command.

The program must be run in Linux terminal. The file to be run is ```bode.py```. In order to run it, change current path to the directory where you downloaded the source code. Then write the following command:

```sudo python bode.py <awg_name> <serial_port> <baud_rate>```

where

* ```<awg_name>``` is the name of the AWG connected to your PC: ```bk4075```, ```jds6600```, ```fy6600``` or ```dummy```.

* ```<serial_port>``` is the serial port to which your AWG is connected. Usually it will be something like ```/dev/ttyUSB0```. If you use the ```dummy``` generator, you don't have to specify the port.

* ```<baud_rate>``` is the serial baud rate as defined in the AWG settings. Currently only ```bk4075``` supports it. If you don't provide this parameter, ```bk4075``` will use the default baud rate of 19200 bps. Two other AWGs don't require it: ```jds6600``` and ```fy6600``` run always at 115200 bps and the ```dummy``` generator doesn't use a serial port.

The ```dummy``` generator was added for running this program without connecting a signal generator. The program will emulate a Siglent AWG and the oscilloscope will generate a Bode plot but no commands will be sent to the AWG.

If the program starts successfully, you'll see the following output:

```
Initializing AWG...
AWG: jds6600
Port: /dev/ttyUSB0
Starting AWG server...
Listening on 0.0.0.0
RPCBIND on port 111
VXI-11 on port 703
Creating sockets...

Waiting for connection request...
```

After starting the program, follow the usual procedure of creating Bode plot. After starting the plotting, the program output will be similar to the following:

```
Incoming connection from 192.168.14.27:55916.
VXI-11 CREATE_LINK, SCPI command: inst0
VXI-11 DEVICE_WRITE, SCPI command: IDN-SGLT-PRI?
VXI-11 DEVICE_READ, SCPI command: None
VXI-11 DESTROY_LINK, SCPI command: None

Waiting for connection request...

Incoming connection from 192.168.14.27:48446.
VXI-11 CREATE_LINK, SCPI command: inst0
VXI-11 DEVICE_WRITE, SCPI command: C1:OUTP LOAD,50;BSWV WVTP,SINE,PHSE,0,FRQ,510,AMP,1,OFST,0;OUTP ON
VXI-11 DESTROY_LINK, SCPI command: None

Waiting for connection request...

Incoming connection from 192.168.14.27:50264.
VXI-11 CREATE_LINK, SCPI command: inst0
VXI-11 DEVICE_WRITE, SCPI command: C1:BSWV?
VXI-11 DEVICE_READ, SCPI command: None
VXI-11 DESTROY_LINK, SCPI command: None

Waiting for connection request...

Incoming connection from 192.168.14.27:55976.
VXI-11 CREATE_LINK, SCPI command: inst0
VXI-11 DEVICE_WRITE, SCPI command: C1:BSWV FRQ,10
VXI-11 DESTROY_LINK, SCPI command: None

Waiting for connection request...

Incoming connection from 192.168.14.27:48088.
VXI-11 CREATE_LINK, SCPI command: inst0
VXI-11 DEVICE_WRITE, SCPI command: C1:BSWV FRQ,10
VXI-11 DESTROY_LINK, SCPI command: None
```

## Changelog

### 2019-01-30

* The program supports Feeltech FY6600 AWG.

### 2018-07-18

* The first version of the program was uploaded to GitHub.

## Follow-up Projects

* [espBode](https://github.com/PanKaczka/espBode) by [Jakub Stępniewicz SQ6SFO](https://github.com/PanKaczka) - an interface between a Siglent SDS1004X-E oscilloscope and FY6800 AWG implemented on ESP-01 module.

## Contributing

I'd like to add here more AWGs but it's impossible to have them all at the home lab. If you'd like to write a driver for an AWG which isn't listed here, please contact me.

## Authors

* **Dmitry Melnichansky [@4x1md](https://github.com/4x1md)** - Project idea and implementation.

* **Nick Bryant (Dundarave on EEVblog Forum)** - Driver for Feeltech FY6600 AWG.

## Links

1. [Siglent SDS1104X-E and SDS1204X-E: Bode plot with non-Siglent AWG](http://www.eevblog.com/forum/testgear/siglent-sds1104x-e-and-sds1204x-e-bode-plot-with-non-siglent-awg/) on EEVblog Forum.
2. [Running the script with SDS1204X-E and JDS6600 AWG](https://www.youtube.com/watch?v=7PvueUHAJ78) on YouTube (best viewed in 1080p quality).

## Questions? Suggestions?
You are more than welcome to contact me with any questions, suggestions or propositions regarding this project. You can:

1. Visit [my QRZ.COM page](https://www.qrz.com/db/4X1MD)
2. Visit [my Facebook profile](https://www.facebook.com/Dima.Meln)
3. :email: Write me an email to iosaaris =at= gmail dot com

73 de 4X1MD
