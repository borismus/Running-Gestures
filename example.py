#!/usr/bin/python
import sys, lightblue, hexbyte

WIIMOTE_DEVICE_NAME = 'Nintendo RVL-CNT-01'

# auto-discover nearby bluetooth devices
devs = lightblue.finddevices(getnames=True, length=5)
# find the one with the correct name
wiimote = [d for d in devs if d[1] == WIIMOTE_DEVICE_NAME] and d[0] or None
if not wiimote:
    print "No wiimotes found!"
    sys.exit(1)
    
# create a socket for writing control data
write_socket = lightblue.socket(lightblue.L2CAP)
write_socket.connect((wiimote, 0x11))

# create a socket for reading accelerometer data
read_socket = lightblue.socket(lightblue.L2CAP)
read_socket.connect((wiimote, 0x13))

# initialize the socket to the right mode
write_socket.send(hexbyte.HexToByte('52 12 00 33'))

# start reading data from it
while 1:
    byte = read_socket.recv(256 * 7)
    data = hexbyte.ByteToHex(byte)
    # do something interesting with the data
    print data
