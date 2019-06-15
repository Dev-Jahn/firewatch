from MultiWii import MultiWii
from Drone import Drone

import serial
import time
import struct

drone = Drone('/dev/ttyUSB0')
#drone = Drone('COM5')

#drone.comm_controlling()
#drone.comm_controlling(IP='LOOP_BACK')
drone.comm_controlling(IP='192.168.0.148')
#drone.comm_controlling(IP='192.168.43.143')
#drone.keyboard_controlling()
