from MultiWii import MultiWii
from Drone import Drone

import serial
import time
import struct

drone = Drone('/dev/ttyUSB0')
#drone = Drone('COM1')

#drone.comm_controlling()
drone.comm_controlling(IP='192.168.0.148')
#drone.keyboard_controlling()
