from MultiWii import MultiWii
from Drone import Drone

import serial
import time
import struct

drone = Drone('/dev/ttyUSB0')
#drone = Drone('COM3')

drone.comm_controlling()