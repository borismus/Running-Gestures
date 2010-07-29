"""A library to pair with the wiimote and extract accelerometer data from it"""

from hexbyte import *
from time import sleep
import lightblue

WIIMOTE_DEVICE_NAME = 'Nintendo RVL-CNT-01'
# hardcoded wiimote address...
DEFAULT_WIIMOTE_ADDRESS = '00:26:59:65:D3:A6'

class Wiimote:
    
    def __init__(self, button_callback):
        self.button_callback = button_callback
        self.button_down = False
    
    def discover_and_pair(self):
        """Discovers nearby wiimotes"""
        wiimote = None
        devs = lightblue.finddevices(getnames=True, length=5)
        for dev in devs:
            if dev[1] == WIIMOTE_DEVICE_NAME:
                wiimote = dev
                
        self.pair(wiimote[0])
    
    def pair(self, addr=DEFAULT_WIIMOTE_ADDRESS):
        """Pairs to wiimotes"""
        # create a socket for reading data
        self.read_socket = lightblue.socket(lightblue.L2CAP)
        self.read_socket.connect((addr, 0x13))
        
        # create a socket for writing data
        write_socket = lightblue.socket(lightblue.L2CAP)
        write_socket.connect((addr, 0x11))
        
        sleep(0.5)
        # tell wiimote to go into mode 0x33
        write_socket.send(HexToByte('52 12 00 33'))
    
    def read_accelerometer(self):
        """Reads a data point from the accelerometer"""
        byte = self.read_socket.recv(256 * 7)
        data = [int(val, 16) for val in ByteToHex(byte).split()]
        # print data

        # parse the data into accelerometer values
        accelerometer_data = data[4:7]
        
        if not data[2] & 2 and self.button_down:
            self.button_callback()
            
        self.button_down = bool(data[2] & 2)
            
        return accelerometer_data
        
    
