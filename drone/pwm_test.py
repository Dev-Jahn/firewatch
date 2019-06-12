import cv2
import numpy as np
#from RPi.GPIO as GPIO
from RPIO import PWM
import time

#GPIO.setmode(GPIO.BCM)

#roll_pin = 5
#pitch_pin = 6
#throttle_pin = 13
#yaw_pin = 19
#aux_pin = 26

#GPIO.setup(roll_pin, GPIO.OUT)
#GPIO.setup(pitch_pin, GPIO.OUT)
#GPIO.setup(throttle_pin, GPIO.OUT)
#GPIO.setup(yaw_pin, GPIO.OUT)
#GPIO.setup(aux_pin, GPIO.OUT)

#roll = GPIO.PWM(roll_pin, 500)             # Aileron
#pitch = GPIO.PWM(pitch_pin, 500)           # Elevator
#throttle = GPIO.PWM(throttle_pin, 600)     # Throttle
#yaw = GPIO.PWM(yaw_pin, 1520)               # Rudder
#aux = GPIO.PWM(aux_pin, 1010)               # Control Mode


# Servo 객체 초기화
roll = PWM.Servo()      # Aileron
pitch = PWM.Servo()     # Elevator
throttle = PWM.Servo()  # Throttle
yaw = PWM.Servo()       # Rudder
aux = PWM.Servo()       # Control Mode

# 각각의 GPIO번호에 PWM 세팅(핀번호 아님)
roll.set_servo(5,1520)      # pin 29
pitch.set_servo(6,1520)     # pin 31
throttle.set_servo(13,1100) # pin 33
yaw.set_servo(19,1520)      # pin 35
aux.set_servo(26,1010)      # pin 37, pin 39 is Ground

# 최대최소값 지정
th_min = 1100
th_max = 2400
r_min = 1100
r_max = 1900
p_min = 1100
p_max = 1900
y_min = 1100
y_max = 1900
a_min = 980
a_max = 2300
th = 1100
r = 1520
p = 1520
y = 1520
a = False
th1 = 0

try:
    while True:
        string = input ('Enter Command: ')
        word = string.split()
        word1 = word[0]
        
        if word1 == 'ready':
            th = 1100
            throttle.set_servo(13,th)
            time.sleep(1)
            
            yaw.set_servo(19,1100)
            time.sleep(1)
            yaw.set_servo(19,1520)
            time.sleep(1)
            print('System is ready')
            continue

        elif word1 == 'fly':

            # 매뉴얼 모드
            if word[1] == 'manual':
                print('Flight control: Manual')
                try:
                    while True:
                        cv2.imshow('i',np.zeros((1,1,1), dtype=np.int8))# dummy
                        k = cv2.waitKey(1)

                        # mapping THR = UP
                        if (k & 0xFF) == ord('w'):
                            th = th + 10
                            if (th < th_min):
                                throttle.set_servo(13,1100)
                                th = 1100
                            elif (th > th_max):
                                throttle.set_servo(13,2400)
                                th = 2400
                            elif (th > th_min & th < th_max):
                                throttle.set_servo(13,th)
                            print('THR: ' + str(th))
                            continue

                        # mapping THR = DOWN
                        if (k & 0xFF) == ord('s'):
                            th = th - 10
                            if (th < th_min):
                                throttle.set_servo(13,1100)
                                th = 1100
                            elif (th > th_max):
                                throttle.set_servo(13,2400)
                                th = 2400
                            elif (th > th_min & th < th_max):
                                throttle.set_servo(13,th)
                            print('THR: ' + str(th))
                            continue

                        # mapping YAW = LEFT
                        if (k & 0xFF) == ord('a'):
                            y = y - 10
                            if (y < y_min):
                                yaw.set_servo(19,1100)
                                y = 1100
                            elif (y > y_max):
                                yaw.set_servo(19,1900)
                                y = 1900
                            elif (y > y_min & y < y_max):
                                yaw.set_servo(19,y)
                            print('YAW: ' + str(y))
                            continue

                        # mapping YAW = RIGHT
                        if (k & 0xFF) == ord('d'):
                            y = y + 10
                            if (y < y_min):
                                yaw.set_servo(19,1100)
                                y = 1100
                            elif (y > y_max):
                                yaw.set_servo(19,1900)
                                y = 1900
                            elif (y > y_min & y < y_max):
                                yaw.set_servo(19,y)
                            print('YAW: ' + str(y))
                            continue

                        # mapping PIT = UP
                        elif (k & 0xFF) == ord('i'):
                            p = p + 10
                            if (p < p_min):
                                pitch.set_servo(6,1100)
                                p = 1100
                            elif (p > p_max):
                                pitch.set_servo(6,1900)
                                p = 1900
                            elif (p > p_min & p < p_max):
                                pitch.set_servo(6,p)
                            print('PIT: ' + str(p))
                            continue
            
                        # mapping PIT = DOWN
                        if (k & 0xFF) == ord('k'):
                            p = p - 10
                            if (p < p_min):
                                pitch.set_servo(6,1100)
                                p = 1100
                            elif (p > p_max):
                                pitch.set_servo(6,1900)
                                p = 1900
                            elif (p > p_min & p < p_max):
                                pitch.set_servo(6,p)
                            print('PIT: ' + str(p))
                            continue

                        # mapping ROL = LEFT
                        if (k & 0xFF) == ord('j'):
                            r = r - 10
                            if (r < r_min):
                                roll.set_servo(5,1100)
                                r = 1100
                            elif (r > r_max):
                                roll.set_servo(5,1900)
                                r = 1900
                            elif (r > r_min & r < r_max):
                                roll.set_servo(5,r)
                            print('ROL: ' + str(r))
                            continue

                        # mapping ROL = RIGHT
                        if (k & 0xFF) == ord('l'):
                            r = r + 10
                            if (r < r_min):
                                roll.set_servo(5,1100)
                                r = 1100
                            elif (r > r_max):
                                roll.set_servo(5,1900)
                                r = 1900
                            elif (r > r_min & r < r_max):
                                roll.set_servo(5,r)
                            print('ROL: ' + str(r))
                            continue

                        # mapping for NO KEY
                        if k == -1:
                            if th1 != th:
                                throttle.set_servo(13,th)
                            else:
                                pass
                            if r != 1520:
                                roll.set_servo(5,1520)
                            else:
                                pass
                            if p !=1520:
                                pitch.set_servo(6,1520)
                            else:
                                pass
                            if y != 1520:
                                yaw.set_servo(19,1520)
                            else:
                                pass
                            th1 = th
                            print('STABLE')
                            continue

                        # mapping for AUX
                        if (k & 0xFF) == ord(' '):
                            a = not(a)
                            if a == True:
                                aux.set_servo(26,2300)
                                print('Turn on')
                            elif a == False:
                                aux.set_servo(26,980)
                                print('Turn off')
                                continue

                        # mapping for BREAK CONDITION
                        if (k & 0xFF) == ord('q'):
                            aux.set_servo(26,2300)
                            throttle.set_servo(13,th)
                            roll.set_servo(5,1520)
                            pitch.set_servo(6,1520)
                            yaw.set_servo(19,1520)
                            break
                        
                        else:
                            continue
                                
                except KeyboardInterrupt:
                    pass

        elif word1 == 'land':
            while (th > 1000):
                throttle.set_servo(13,th-10)
                time.sleep(10)
            print('drone has landed')
            break
        else:
            print('Wrong Input')
        
        time.sleep(0.1)
            
except KeyboardInterrupt:
	pass

roll.stop_servo(5)
pitch.stop_servo(6)
throttle.stop_servo(13)
yaw.stop_servo(19)
aux.stop_servo(26)

cv2.destroyAllWindows()
