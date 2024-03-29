import serial
import struct
import time

class MultiWii:

    # MultiWii Serial Protocols
    
    # SET_RAW_RC / SET_PID
    
    IDENT = 100
    STATUS = 101
    RAW_IMU = 102
    SERVO = 103
    MOTOR = 104
    RC = 105
    RAW_GPS = 106
    COMP_GPS = 107
    ATTITUDE = 108
    ALTITUDE = 109
    ANALOG = 110
    RC_TUNING = 111
    PID = 112
    BOX = 113
    MISC = 114
    MOTOR_PINS = 115
    BOXNAMES = 116
    PIDNAMES = 117
    WP = 118
    BOXIDS = 119
    RC_RAW_IMU = 121
    SET_RAW_RC = 200
    SET_RAW_GPS = 201
    SET_PID = 202
    SET_BOX = 203
    SET_RC_TUNING = 204
    ACC_CALIBRATION = 205
    MAG_CALIBRATION = 206
    SET_MISC = 207
    RESET_CONF = 208
    SET_WP = 209
    SWITCH_RC_SERIAL = 210
    IS_SERIAL = 211
    DEBUG = 254
    VTX_CONFIG = 88
    VTX_SET_CONFIG = 89
    EEPROM_WRITE = 250
    REBOOT = 68

    def __init__(self, serPort, wakeupTime = 2):
        
        self.PIDcoef = {'rp':0,'ri':0,'rd':0,'pp':0,'pi':0,'pd':0,'yp':0,'yi':0,'yd':0}
        
        self.rcChannels = {'roll':0,'pitch':0,'yaw':0,'throttle':0,'elapsed':0,'timestamp':0}
        self.rawIMU = {'ax':0,'ay':0,'az':0,'gx':0,'gy':0,'gz':0,'mx':0,'my':0,'mz':0,'elapsed':0,'timestamp':0}
        self.motor = {'m1':0,'m2':0,'m3':0,'m4':0,'elapsed':0,'timestamp':0}
        self.attitude = {'angx':0,'angy':0,'heading':0,'elapsed':0,'timestamp':0}
        self.altitude = {'estalt':0,'vario':0,'elapsed':0,'timestamp':0}
        self.message = {'angx':0,'angy':0,'heading':0,'roll':0,'pitch':0,'yaw':0,'throttle':0,'elapsed':0,'timestamp':0}
        self.vtxConfig = {'device':0, 'band':0, 'channel':0, 'power':0, 'pit':0, 'unknown':0}
        self.temp = ();
        self.temp2 = ();
        self.elapsed = 0
        self.PRINT = 1

        self.ser = serial.Serial()
        self.ser.port = serPort
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2

        # set board wake up time
        wakeup = wakeupTime
        try:
            self.ser.open()
            if self.PRINT:
                print ("Waking up board on "+self.ser.port+"...")
            for i in range(1,wakeup):
                if self.PRINT:
                    print (wakeup-i)
                    time.sleep(1)
                else:
                    time.sleep(1)
        except Exception as error:
            print ("\n\nError opening "+self.ser.port+" port.\n"+str(error)+"\n\n")
    
    def sendCMD(self, data_length, code, data):
        checksum = 0
        # MSP : Command = ['$' 'M' '<' 'size N' 'type T' 'payload N-bytes' 'crc' ]
        # Type : [ Roll Pitch Yaw Throttle Aux1 Aux2 Aux3 Aux4 ]
        total_data = ['$'.encode('utf-8'), 'M'.encode('utf-8'), '<'.encode('utf-8'), data_length, code] + data
        for i in struct.pack('<2B%dH' % len(data), *total_data[3:len(total_data)]):
            checksum = checksum ^ i
        total_data.append(checksum)
        try:
            b = None
            b = self.ser.write(struct.pack('<3c2B%dHB'% len(data), *total_data))
        except Exception as error:
            print ("\n\nError in sendCMD.")
            print ("("+str(error)+")\n\n")
            pass


    # sendCMD + receive Attitude
    def sendCMDreceiveATT(self, data_length, code, data):
        checksum = 0
        # MSP : Command = ['$' 'M' '<' 'size N' 'type T' 'payload N-bytes' 'crc' ]
        # Type : [ Roll Pitch Yaw Throttle Aux1 Aux2 Aux3 Aux4 ]
        total_data = ['$'.encode('utf-8'), 'M'.encode('utf-8'), '<'.encode('utf-8'), data_length, code] + data
        for i in struct.pack('<2B%dH' % len(data), *total_data[3:len(total_data)]):
            checksum = checksum ^ i
        total_data.append(checksum)
        try:
            start = time.time()
            b = None
            b = self.ser.write(struct.pack('<3c2B%dHB' % len(data), *total_data))
            
            while True:
                header = self.ser.read().decode('utf-8')
                if header == '$':
                    header = header+self.ser.read(2).decode('utf-8')
                    break
            datalength = struct.unpack('<b', self.ser.read())[0]
            code = struct.unpack('<b', self.ser.read())
            data = self.ser.read(datalength)
            temp = struct.unpack('<'+'h'*int(datalength/2),data)
            self.ser.flushInput()
            self.ser.flushOutput()
            elapsed = time.time() - start
            self.attitude['angx']=float(temp[0]/10.0)
            self.attitude['angy']=float(temp[1]/10.0)
            self.attitude['heading']=float(temp[2])
            self.attitude['elapsed']=round(elapsed,3)
            self.attitude['timestamp']="%0.2f" % (time.time(),) 
            return self.attitude
        except Exception as error:
            print ("\n\nError in sendCMDreceiveATT.")
            print ("("+str(error)+")\n\n")
            pass
    
    def setPID(self,pd):
        print ("PID sending:", pd)
        self.sendCMD(30,MultiWii.SET_PID,data)
        self.sendCMD(0,MultiWii.EEPROM_WRITE,[])

    # data packet
    def getData(self, cmd):
        try:
            start = time.time()
            self.sendCMD(0,cmd,[])
            while True:
                header = self.ser.read().decode('utf-8')
                if header == '$':
                    header = header+self.ser.read(2).decode('utf-8')
                    break
            datalength = struct.unpack('<b', self.ser.read())[0]
            code = struct.unpack('<b', self.ser.read())
            data = self.ser.read(datalength)
            
            self.ser.flushInput()
            self.ser.flushOutput()
            elapsed = time.time() - start
            if cmd == MultiWii.ATTITUDE:
                temp = struct.unpack('<'+'h'*int(datalength/2),data)                
                self.attitude['angx']=float(temp[0]/10.0)
                self.attitude['angy']=float(temp[1]/10.0)
                self.attitude['heading']=float(temp[2])
                self.attitude['elapsed']=round(elapsed,3)
                self.attitude['timestamp']="%0.2f" % (time.time(),) 
                return self.attitude
            elif cmd == MultiWii.ALTITUDE:
                temp = struct.unpack('<'+'h'*int(datalength/2),data)
                self.altitude['estalt']=float(temp[0])
                self.altitude['vario']=float(temp[1])
                self.altitude['elapsed']=round(elapsed,3)
                self.altitude['timestamp']="%0.2f" % (time.time(),) 
                return self.altitude
            elif cmd == MultiWii.RC:
                temp = struct.unpack('<'+'h'*int(datalength/2),data)
                self.rcChannels['roll']=temp[0]
                self.rcChannels['pitch']=temp[1]
                self.rcChannels['yaw']=temp[2]
                self.rcChannels['throttle']=temp[3]
                self.rcChannels['elapsed']=round(elapsed,3)
                self.rcChannels['timestamp']="%0.2f" % (time.time(),)
                return self.rcChannels
            elif cmd == MultiWii.RAW_IMU:
                temp = struct.unpack('<'+'h'*int(datalength/2),data)
                self.rawIMU['ax']=float(temp[0])
                self.rawIMU['ay']=float(temp[1])
                self.rawIMU['az']=float(temp[2])
                self.rawIMU['gx']=float(temp[3])
                self.rawIMU['gy']=float(temp[4])
                self.rawIMU['gz']=float(temp[5])
                self.rawIMU['mx']=float(temp[6])
                self.rawIMU['my']=float(temp[7])
                self.rawIMU['mz']=float(temp[8])
                self.rawIMU['elapsed']=round(elapsed,3)
                self.rawIMU['timestamp']="%0.2f" % (time.time(),)
                return self.rawIMU
            elif cmd == MultiWii.MOTOR:
                temp = struct.unpack('<'+'h'*int(datalength/2),data)
                self.motor['m1']=float(temp[0])
                self.motor['m2']=float(temp[1])
                self.motor['m3']=float(temp[2])
                self.motor['m4']=float(temp[3])
                self.motor['elapsed']="%0.3f" % (elapsed,)
                self.motor['timestamp']="%0.2f" % (time.time(),)
                return self.motor
            elif cmd == MultiWii.PID:
                temp = struct.unpack('<'+'h'*int(datalength/2),data)
                dataPID=[]
                if len(temp)>1:
                    d=0
                    for t in temp:
                        dataPID.append(t%256)
                        dataPID.append(t/256)
                    for p in [0,3,6,9]:
                        dataPID[p]=dataPID[p]/10.0
                        dataPID[p+1]=dataPID[p+1]/1000.0
                    self.PIDcoef['rp']= dataPID=[0]
                    self.PIDcoef['ri']= dataPID=[1]
                    self.PIDcoef['rd']= dataPID=[2]
                    self.PIDcoef['pp']= dataPID=[3]
                    self.PIDcoef['pi']= dataPID=[4]
                    self.PIDcoef['pd']= dataPID=[5]
                    self.PIDcoef['yp']= dataPID=[6]
                    self.PIDcoef['yi']= dataPID=[7]
                    self.PIDcoef['yd']= dataPID=[8]
                return self.PIDcoef
            elif cmd == MultiWii.VTX_CONFIG:
                if datalength > 1:
                    temp = struct.unpack('<bbbbb',data)
                    self.vtxConfig['device'] = temp[0]
                    self.vtxConfig['band'] = temp[1]
                    self.vtxConfig['channel'] = temp[2]
                    self.vtxConfig['power'] = temp[3]       
                    self.vtxConfig['pit'] = temp[4]
                    self.vtxConfig['unknown'] = 0
                    return self.vtxConfig
                else:
                    temp = struct.unpack('<b',data)
                    self.vtxConfig['unknown'] = temp[0]
                    return self.vtxConfig
            else:
                return "No return error!"
        except Exception as error:
            print (error)
            pass
