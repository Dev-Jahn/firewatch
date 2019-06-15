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

class Drone:
    
    MIN_COMMAND = 1000
    MIN_THROTTLE = 1100
    BTN_PRESSED = 1
    BTN_RELEASED = 0
    TOGGLE_ON = 1
    TOGGLE_OFF = 0
    
    def __init__(self, serPort = '/dev/ttyUSB0'):


        self.serialPort = serPort
        self.board = MultiWii(self.serialPort)
        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = Drone.MIN_COMMAND
        self.arm_condition = False
        self.disarm_condition = False
        self.stop_condition = False
        self.fail_condition = False
        self.last_comm_time = 0
        self.curAux2 = 1000 # init for angle mode
        self.curAux3 = 1000 # init for baro mode
        
        self.aux2_toggle = 0
        self.aux3_toggle = 0

        data = [self.curRoll, self.curPitch, self.curYaw, Drone.MIN_COMMAND, 0, self.curAux2, self.curAux3, 0] # roll, pitch, yaw, throttle
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
        print('o/O : send aux2 hi')
        print('p/P : send aux3 hi')
        print('[/{ : send aux2 mid')
        print(']/} : send aux3 mid')
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
                    self.arm()
                    print('Drone Arming completed')
                elif keyboard.is_pressed('x'):
                    # disarming
                    print('Drone Disarming started')
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
                elif keyboard.is_pressed('o'):
                    self.send_aux2_hi()
                    print('angle mode on')
                elif keyboard.is_pressed('p'):
                    self.send_aux3_hi()
                    print('baro mode on')
                elif keyboard.is_pressed('['):
                    self.send_aux2_mid()
                    print('angle mode off')
                elif keyboard.is_pressed(']'):
                    self.send_aux3_mid()
                    print('angle mode off')
                elif keyboard.is_pressed('h'):
                    self.print_command()
                elif keyboard.is_pressed('r'):
                    print('Drone reset [1500, 1500, 1500, 1500, 1000, 1500, 1500, 1000]')
                    self.reset()
                #else:
                    #print('Wrong Command. h or H is help')
                else:
                    data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, self.curAux2, self.curAux3, 0]
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
            data = [1500, 1500, 2000, 1000, 0, 1000, 1000, 0] # roll, pitch, yaw, throttle
            data_len = len(data) * 2 # use as short data type
            self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
            time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

        data = [1500, 1500, 1500, Drone.MIN_THROTTLE, 0, 0, 0, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = Drone.MIN_THROTTLE
        self.last_comm_time = time.time()
        self.arm_condition = False
        self.disarm_condition = False
        self.stop_condition = False
        self.fail_condition = False
        self.aux2_toggle = Drone.TOGGLE_OFF
        self.aux3_toggle = Drone.TOGGLE_OFF


    def disarm(self):
        timer = 0
        start = time.time()
        while timer < 0.5:
            data = [1500, 1500, 1000, 1000, 1000, 1000, 1000, 1000] # roll, pitch, yaw, throttle
            data_len = len(data) * 2 # use as short data type
            self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
            time.sleep(0.05)
            timer = timer + (time.time() - start)
            start = time.time()

        data = [1500, 1500, 1500, Drone.MIN_COMMAND, 0, 1500, 1500, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = Drone.MIN_COMMAND
        self.last_comm_time = 0
        self.arm_condition = False
        self.disarm_condition = False
        self.stop_condition = False
        self.fail_condition = False
        self.aux2_toggle = Drone.TOGGLE_OFF
        self.aux3_toggle = Drone.TOGGLE_OFF


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
        data = [1500, 1500, 1500, min_command, 0, 1500, 1500, 0] # roll, pitch, yaw, throttle
        data_len = len(data) * 2 # use as short data type
        
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

        self.curRoll = 1500
        self.curPitch = 1500
        self.curYaw = 1500
        self.curThrottle = Drone.MIN_COMMAND

    def getData(self, cmd = MultiWii.RC):
        return self.board.getData(cmd)

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
        if power < Drone.MIN_THROTTLE:
            power = Drone.MIN_THROTTLE
        elif power > 2000:
            power = 2000

        data = [self.curRoll, self.curPitch, self.curYaw, power]
        data_len = len(data) * 2 # use as short data type
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curThrottle = power
        
    def send_aux2(self, mode):
        if mode == 'lo':
            self.send_aux2_lo()
        elif mode == 'mid':
            self.send_aux2_mid()
        elif mode == 'hi':
            self.send_aux2_hi()
    
    def send_aux2_lo(self):
        data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, 1000, self.curAux3, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curAux2 = 1000
        self.aux2_toggle = Drone.TOGGLE_OFF
        
    def send_aux2_mid(self):
        data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, 1500, self.curAux3, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curAux2 = 1500
        self.aux2_toggle = Drone.TOGGLE_OFF
    
    def send_aux2_hi(self):
        data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, 2000, self.curAux3, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curAux2 = 2000
        self.aux2_toggle = Drone.TOGGLE_ON
        
    def send_aux3(self, mode):
        if mode == 'lo':
            self.send_aux3_lo()
        elif mode == 'mid':
            self.send_aux3_mid()
        elif mode == 'hi':
            self.send_aux3_hi()
    
    def send_aux3_lo(self):
        data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, self.curAux2, 1000, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curAux3 = 1000
        self.aux3_toggle = Drone.TOGGLE_OFF
        
    def send_aux3_mid(self):
        data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, self.curAux2, 1500, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curAux3 = 1500
        self.aux3_toggle = Drone.TOGGLE_OFF
    
    def send_aux3_hi(self):
        data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, self.curAux3, 2000, 0]
        data_len = len(data) * 2
        self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)
        self.curAux3 = 2000
        self.aux3_toggle = Drone.TOGGLE_ON


    # In[ ]:


    def comm_wait(self, sock):
        while True:
            data, addr = sock.recvfrom(200)
            content = data.decode()
            
            if content == 'OK':
                self.fail_condition = False
                self.last_comm_time = time.time()
            elif not content == 'OK' and self.fail_condition == False:
                content = content.split(':')

                operator = content[0]
                value = int(content[1])

                if operator == 'ABS_X':
                    # YAW - Left controller x
                    self.change_yaw(value)
                    print('yaw changed to ', value)
                elif operator == 'ABS_Y':
                    # THROTTLE - Left controller y
                    self.change_throttle(value)
                    print('throttle changed to ', value)
                elif operator == 'ABS_RX':
                    # ROLL - Right controller x
                    self.change_roll(value)
                    print('roll changed to ', value)
                elif operator == 'ABS_RY':
                    # PITCH - Right contorller y
                    self.change_pitch(value)
                    print('pitch changed to ', value)
                elif operator == 'BTN_SOUTH':
                    # ARM - button A
                    if value == Drone.BTN_PRESSED:
                        self.arm_condition = True
                        self.arm()
                        print('arm signal start')
                    elif value == Drone.BTN_RELEASED:
                        self.arm_condition = False
                        print('arm end')
                elif operator == 'BTN_WEST':
                    # DISARM - button X
                    if value == Drone.BTN_PRESSED:
                        self.disarm_condition = True
                        self.disarm()
                        print('disarm signal start')
                    elif value == Drone.BTN_RELEASED:
                        self.disarm_condition = False
                        print('disarm end')
                elif operator == 'BTN_SELECT':
                    # Force fail safe - button Select (right)
                    if value == Drone.BTN_PRESSED:
                        self.stop_condition = True
                        print('stop signal start')
                    elif value == Drone.BTN_RELEASED:
                        self.stop_condition = False
                        print('stop signal end')
                elif operator == 'BTN_EAST':
                    # Aux2 - angle mode toggle
                    if value == Drone.BTN_PRESSED:
                        if self.aux2_toggle == Drone.TOGGLE_OFF:
                            self.send_aux2_hi()
                            print('Aux2 is set to hi (Angle mode is on)')
                        elif self.aux2_toggle == Drone.TOGGLE_ON:
                            self.send_aux2_lo()
                            print('Aux2 is set to lo (Angle mode is off)')
                elif operator == 'BTN_NORTH':
                    # Aux3 - baro mode toggle
                    if value == Drone.BTN_PRESSED:
                        if self.aux3_toggle == Drone.TOGGLE_OFF:
                            self.send_aux3_hi()
                            print('Aux3 is set to hi (Baro mode is on)')
                        elif self.aux3_toggle == Drone.TOGGLE_ON:
                            self.send_aux3_lo()
                            print('Aux3 is set to lo (Baro mode is off)')

    def comm_controlling(self, IP = '192.168.43.143', port = 6666):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if IP == 'LOOP_BACK':
            IP = '127.0.0.1'
            
        sock.bind((IP, port))

        t = Thread(target=self.comm_wait, args=(sock,))
        t.daemon = True
        t.start()

        while True:
            time.sleep(0.05)
            
            cur_time = time.time()
            if (cur_time - self.last_comm_time) < 0.1 or self.stop_condition == True:
                self.fail_condition = True
                self.do_failsafe()
            
            if self.arm_condition or self.disarm_condition or self.stop_condition:
                pass
            
            else:
                data = [self.curRoll, self.curPitch, self.curYaw, self.curThrottle, 0, self.curAux2, self.curAux3, 0]
                data_len = len(data) * 2
                self.board.sendCMD(data_len, MultiWii.SET_RAW_RC, data)

                
    def do_failsafe(self, accel = 0.98):
        if self.fail_condition == False:
            return None
        
        print('failsafe mode is on')
        print('current accel : ', accel)
        
        hovering_throttle = 1600
        step = 1
        self.send_aux3_lo() # turn off the baro mode by force
        
        if accel >= 1:
            accel = 0.98
        elif accel <= 0.96:
            accel = 0.96
        
        timer = 0

        while True:
            time.sleep(0.05)
            newThrottle = int(self.curThrottle * accel)
            print('failsafe mode step ', step, ' : throttle down to ', newThrottle)
            start = time.time()
            while timer < 3:
                self.changeThrottle(newThrottle)
            timer = 0
            step += 1
            if self.curThrottle <= Drone.MIN_THROTTLE:
                break

        print('failsafe mode last step ', step, ' : throttle is min throttle now')
        print('failsafe last step ----- disarm start')
        self.disarm()
        print('failsafe completed ----- disarm completed')