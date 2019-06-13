#Event specification
#event.ev_type:
#    Key:      좌우 범퍼, ABXY, 기타버튼
#    Absolute: 좌우트리거, 십자패드, 좌우 아날로그스틱
#    Sync:     이벤트발생후 싱크
#event.code                      event.state
#    ABS_Z:     L트리거             0~255
#    ABS_RZ:    R트리거             0~255
#    ABS_X:     L아날로그스틱 X축    -32768~32767
#    ABS_Y:     L아날로그스틱 Y축    -32768~32767
#    ABS_RX:    R아날로그스틱 X축    -32768~32767
#    ABS_RY:    R아날로그스틱 Y축    -32768~32767
#    ABS_HAT0X: LR십자버튼          L -1, R 1
#    ABS_HAT0Y: UD십자버튼          U -1, D 1
#    BTN_TL:    L범퍼              누를때 1, 뗄때 0
#    BTN_TR:    L범퍼
#    BTN_SOUTH: A
#    BTN_EAST:  B 
#    BTN_WEST:  X
#    BTN_NORTH: Y
#    BTN_THUMBL:L썸버튼
#    BTN_THUMBR:R썸버튼
#    BTN_START: 좌측메뉴버튼
#    BTN_SELECT:우측메뉴버튼


# In[2]:


import inputs
from inputs import devices
from inputs import UnpluggedError
analog_sticks = ['ABS_X','ABS_Y','ABS_RX','ABS_RY']


# In[3]:


class XboxPad:
    def __init__(self, deadzone=8000, a_mid=1500, a_range=1000):
        self.deadzone = deadzone
        self.a_mid = a_mid 
        self.a_range = a_range
        self.raw_max = 32767
        self.raw_min = -32768
        self.latest_st = {'ABS_X':a_mid,
                          'ABS_Y':a_mid,
                          'ABS_RX':a_mid,
                          'ABS_RY':a_mid}
        if len(devices.gamepads) != 0:
            print('Gamepad connected.')
        else:
            print('Cannot find gamepad.')
    #이벤트 리스너
    def get_event(self):
        try:
            events = inputs.get_gamepad()
            for event in events:
                if event.ev_type != 'Sync':
                    # 아날로그스틱 데드존 이하 미세동작 무시
                    if event.code in analog_sticks:
                        st = self._convert(event.state)
                        if self.latest_st[event.code] == self.a_mid and st == self.a_mid:
                            return
                        else:
                            self.latest_st[event.code] = st
                            return event.code, st
                    # 일반키입력
                    else:
                        return event.code, event.state
                # Sync 이벤트
                else:
                    return 
        except UnpluggedError as e:
            print(e)
            return
    # 데드존 컷오프 후 리스케일
    def _rescale(self, n):
        if abs(n) <= self.deadzone:
            return 0
        elif n > 0:
            return int((n-self.deadzone)*self.raw_max/(self.raw_max-self.deadzone))
        elif n < 0:
            return int((n+self.deadzone)*self.raw_min/(self.raw_min+self.deadzone))
        else:
            return n
    # 전송신호규격에 맞추어 변환 
    def _convert(self, n):
        return int((self._rescale(n)-self.raw_min)/(self.raw_max-self.raw_min)*self.a_range+(self.a_mid-self.a_range/2))