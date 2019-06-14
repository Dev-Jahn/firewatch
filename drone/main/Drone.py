#!/usr/bin/env python
# coding: utf-8

# In[26]:


from MultiWii import MultiWii
from threading import Thread
import serial
import time
import struct
import keyboard
import socket


# In[21]:


min_command = 1000
min_throttle = 1100
BTN_PRESSED = 1
BTN_RELEASED = 0

# In[18]:


class Drone:
    def __init__(self, serPort = '/dev/ttyUSB0'):
        self.serialPort = serPort
        self.board = MultiWii(self.serialPort)
        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = min_command
        self.arm_condition = False
        self.disarm_condition = False
        self.stop_condition = False

        data = [1500, 1500, 1500, min_command, 0, 0, 0, 0] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)


    # Serial Port example
    # /dev/ttyUSB0 ; raspberry pi
    # COM7 ; windows
    
    # windows : devmgmt.msc
    # rasbian : ls /dev/tty*
    def print_command(self):
        print('q/Q : quit')
        print('z/Z : arming')
        print('x/X : disarming')
        print('w/W : throttle up')
        print('s/S : throttle down')
        print('a/A : yaw down (turn left)')
        print('d/D : yaw up (turn right)')
        print('i/I : pitch up (go_forward)')
        print('k/K : pitch down (go_backward)')
        print('j/J : roll down (left side rotate)')
        print('l/L : roll up (right side rotate)')
        print('h/H : command reprint')

    def keyboard_controlling(self):
        self.print_command()

        while True:
            try:
                time.sleep(0.05)
                if keyboard.is_pressed('q'):
                    break
                elif keyboard.is_pressed('z'):
                    # arming
                    print('Drone Arming started')
                    print('Drone channel state = [1500, 1500, 2000, 1]')
                    self.arm()
                    print('Drone Arming completed')
                elif keyboard.is_pressed('x'):
                    # disarming
                    print('Drone Disarming started')
                    print('Drone channel state = [1500, 1500, 1000, 1]')
                    self.disarm()
                    print('Drone Disarming completed')
                elif keyboard.is_pressed('w'):
                    #throttle up
                    print('Drone Throttle up')
                    self.up_key()
                    print('cur Throttle is : ', self.curThrottle)
                elif keyboard.is_pressed('s'):
                    #throttle down
                    print('Drone Throttle down')
                    self.down_key()
                    print('cur Throttle is : ', self.curThrottle)
                elif keyboard.is_pressed('a'):
                    #yaw down
                    print('Drone Yaw down (turn left)')
                    self.turn_left_key()
                    print('cur Yaw is : ', self.curYaw)
                elif keyboard.is_pressed('d'):
                    #yaw up
                    print('Drone Yaw up (turn right)')
                    self.turn_right_key()
                    print('cur Yaw is : ', self.curYaw)
                elif keyboard.is_pressed('i'):
                    #pitch up
                    print('Drone pitch up (go forward)')
                    self.go_forward_key()
                    print('cur Pitch is : ', self.curPitch)
                elif keyboard.is_pressed('k'):
                    #pitch down
                    print('Drone pitch down (go backward)')
                    self.go_backward_key()
                    print('cur Pitch is : ', self.curPitch)
                elif keyboard.is_pressed('j'):
                    #roll down
                    print('Drone roll down (left rotate)')
                    self.rotate_left_key()
                    print('cur Roll is : ', self.curRoll)
                elif keyboard.is_pressed('l'):
                    #roll up
                    print('Drone roll up (right rotate)')
                    self.rotate_right_key()
                    print('cur Roll is : ', self.curRoll)
                elif keyboard.is_pressed('h'):
                    self.print_command()
                elif keyboard.is_pressed('r'):
                    print('Drone reset [1500, 1500, 1500, 1]')
                    self.reset()
                #else:
                    #print('Wrong Command. h or H is help')
                else:
                    data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, 0, 0, 0]
                    data_len = len(data) * 2
                    self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
            except Exception as error:
                print('key error : ', str(error))
                break
        
    def setSerialPort(self, serPort):
        self.serialPort = serPort

    def reopenBoard(self):
        self.board = MultiWii(self.serialPort)

    def printInfo(self):
        print('Data order : Roll Pitch Yaw Throttle Aux1 2 3 4')

    def arm(self):
        timer = 0
        start = time.time()
        while timer < 0.5:
            data = [1500, 1500, 2000, 1000] # roll, pitch, yaw, throttle
            data_len = len(data) * 2 # use as short data type
            self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
            time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

        data = [1500, 1500, 2000, min_throttle]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = min_throttle

    def disarm(self):
        timer = 0
        start = time.time()
        while timer < 0.5:
            data = [1500, 1500, 1000, 1000] # roll, pitch, yaw, throttle
            data_len = len(data) * 2 # use as short data type
            self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
            time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

        data = [1500, 1500, 1000, min_command]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = min_command

    def go_forward(self,power = 300):
        if power > 500:
            power = 500
        elif power < 0:
            power = 0
        
        data = [1500, 1500 - power, 1500, 1500] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500 - power
        self.curYaw = 1500
        self.curThrottle = 1500

    def go_forward_key(self, power = 10):
        newPitch = self.curPitch - power
        if newPitch < 1000:
            newPitch = 1000

        data = [self.curRoll, newPitch, self.curYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curPitch = newPitch
            
    def go_backward(self,power = 300):
        if power > 500:
            power = 500
        elif power < 0:
            power = 0
            
        data = [1500, 1500 + power, 1500, 1500] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500 + power
        self.curYaw = 1500
        self.curThrottle = 1500

    def go_backward_key(self, power = 10):
        newPitch = self.curPitch + power
        if newPitch > 2000:
            newPitch = 2000

        data = [self.curRoll, newPitch, self.curYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curPitch = newPitch
    
    def rotate_left_key(self, power = 10):
        newRoll = self.curRoll - power
        if newRoll < 1000:
            newRoll = 1000
        data = [newRoll, self.curPitch, self.curYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = newRoll

    def rotate_right_key(self, power = 10):
        newRoll = self.curRoll + power
        if newRoll > 2000:
            newRoll = 2000
        data = [newRoll, self.curPitch, self.curYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = newRoll

    def turn_left(self,power = 300) :
        if power > 500:
            power = 500
        elif power < 0:
            power = 0
            
        data = [1500, 1500, 1500 - power, 1500] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500 - power
        self.curThrottle = 1500

    def turn_left_key(self, power = 10) :
        newYaw = self.curYaw - power
        if newYaw < 1000:
            newYaw = 1000
        data = [self.curRoll, self.curPitch, newYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curYaw = newYaw

    def turn_right(self,power = 300):
        if power > 500:
            power = 500
        elif power < 0:
            power = 0
            
        data = [1500, 1500, 1500 + power, 1500] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500 + power
        self.curThrottle = 1500

    def turn_right_key(self, power = 10) :
        newYaw = self.curYaw + power
        if newYaw > 2000:
            newYaw = 2000
        data = [self.curRoll, self.curPitch, newYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curYaw = newYaw

    def up(self,power = 300):
        if power > 500:
            power = 500
        elif power < 0:
            power = 0
        data = [1500, 1500, 1500, 1500 + power] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = 1500 + power

    def up_key(self, power = 10):
        newThrottle = self.curThrottle + power
        if newThrottle > 2000:
            newThrottle = 2000
        data = [self.curRoll, self.curPitch, self.curYaw, newThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curThrottle = newThrottle

    def down(self,power = 300):
        if power > 500:
            power = 500
        elif power < min_command:
            power = min_command
            
        data = [1500, 1500, 1500, 1500-power] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = 1500 - power

    def down_key(self, power = 10):
        newThrottle = self.curThrottle - power
        if newThrottle < 1:
            newThrottle = 1
        data = [self.curRoll, self.curPitch, self.curYaw, newThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curThrottle = newThrottle

    def reset(self):
            
        data = [1500, 1500, 1500, min_command] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = min_command

    def getData(self, cmd = MultiWii.RC):
        return self.board.getData(cmd)

    def getRC(self):
        self.board.getData(MultiWii.RC)
        roll = self.board.rcChannels['roll']
        pitch = self.board.rcChannels['pitch']
        yaw = self.board.rcChannels['yaw']
        throttle = self.board.rcChannels['throttle']

        print('type of roll = ', type(roll))
        print('type of pitch = ', type(pitch))
        print('type of yaw = ', type(yaw))
        print('type of throttle = ', type(throttle))

        self.curRoll = roll
        self.curPtich = pitch
        self.curYaw = yaw
        self.throttle = throttle

        return roll, pitch, yaw, throttle


    def droneTest(self, msgFlag=True):

    	print('Drone arming started')
    	self.arm()
    	print('Drone arming completed')

    	print('Drone Up during 3seconds')
    	timer = 0
    	start = time.time()
    	while timer < 3:
            self.up()
            if msgFlag == True:
                print(self.getData())
       	    time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

    	print('Drone Go forward during 3seconds')
    	timer = 0
    	start = time.time()
    	while timer < 3:
            self.go_forward()
            if msgFlag == True:
                print(self.getData())
       	    time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

    	print('Drone Go backward during 3seconds')
    	timer = 0
    	start = time.time()
    	while timer < 3:
            self.go_backward()
            if msgFlag == True:
                print(self.getData())
       	    time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

    	print('Drone Turn Left during 3seconds')
    	timer = 0
    	start = time.time()
    	while timer < 3:
            self.turn_left()
            if msgFlag == True:
                print(self.getData())
       	    time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

    	print('Drone Turn right during 3seconds')
    	timer = 0
    	start = time.time()
    	while timer < 3:
            self.turn_right()
            if msgFlag == True:
                print(self.getData())
       	    time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

    	print('Drone Down during 3seconds')
    	timer = 0
    	start = time.time()
    	while timer < 3:
            self.down()
            if msgFlag == True:
                print(self.getData())
       	    time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

    	print('After 3seconds, drone disarming will be started')
    	time.sleep(3)

    	print('Drone disarming started')
    	self.disarm()
    	print('Drone disarming completed')


# In[24]:


    def change_pitch(self, power):
        if power < 1000:
            power = 1000
        elif power > 2000:
            power = 2000

        data = [self.curRoll, power, self.curYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curPitch = power

    def change_yaw(self, power):
        if power < 1000:
            power = 1000
        elif power > 2000:
            power = 2000

        data = [self.curRoll, self.curPitch, power, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curYaw = power

    def change_roll(self, power):
        if power < 1000:
            power = 1000
        elif power > 2000:
            power = 2000

        data = [power, self.curPitch, self.curYaw, self.curThrottle]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = power

    def change_throttle(self, power):
        if power < min_throttle:
            power = min_throttle
        elif power > 2000:
            power = 2000

        data = [self.curRoll, self.curPitch, self.curYaw, power]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curThrottle = power


    # In[ ]:


    def comm_wait(self, sock):
        while True:
            data, addr = sock.recvfrom(200)
            content = data.decode().split(':')

            operator = content[0]
            value = int(content[1])

            if operator == 'ABS_X':
                # YAW
                self.change_yaw(value)
                print('yaw changed to ', value)
            elif operator == 'ABS_Y':
                # THROTTLE
                self.change_throttle(value)
                print('throttle changed to ', value)
            elif operator == 'ABS_RX':
                # ROLL
                self.change_roll(value)
                print('roll changed to ', value)
            elif operator == 'ABS_RY':
                # PITCH
                self.change_pitch(value)
                print('pitch changed to ', value)
            elif operator == 'BTN_SOUTH':
                # ARM
                if value == BTN_PRESSED:
                    self.arm_condition = True
                    self.arm()
                    print('arm signal start')
                elif value == BTN_RELEASED:
                    self.arm_condition = False
                    print('arm end')
            elif operator == 'BTN_WEST':
                # DISARM
                if value == BTN_PRESSED:
                    self.disarm_condition = True
                    self.disarm()
                    print('disarm signal start')
                elif value == BTN_RELEASED:
                    self.disarm_condition = False
                    print('disarm end')
            elif operator == 'BTN_NORTH':
                if value == BTN_PRESSED:
                    self.stop_condition = True
                    print('stop signal start')
                elif value == BTN_RELEASED:
                    self.stop_condition = False
                    print('stop signal end')
    # In[27]:


    def comm_controlling(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('192.168.43.143', 6666))

        t = Thread(target=self.comm_wait, args=(sock,))
        t.daemon = True
        t.start()

        while True:
            time.sleep(0.05)
            if self.arm_condition or self.disarm_condition or self.stop_condition:
                pass
            else:
                data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, 0, 0, 0]
                data_len = len(data) * 2
                self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

