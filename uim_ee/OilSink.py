# -*- encoding: utf-8 -*-
'''
@File    :   OilSink.py
@Time    :   2024/05/05 16:03:15
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''

# here put the import lib


import serial
import time


DEBUG = 1
def debugPrint(msg):
    if DEBUG:
        print(msg)



class ZCTB_400L():
    def __init__(self, comport) -> None:
        self.session = serial.Serial(comport,9600,timeout=0.5)

    def getID(self):
        self.session.write(b'*ver\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt)
        debugPrint(ret)

    def set_temp(self,temp):
        self.session.write(b's=%d\r\n'%temp)

    def set_sr(self,scanrate):
        self.session.write(b'sr=%d\r\n'%scanrate)

    def read_state(self):
        # 0 不稳定 1稳定
        self.session.write(b'st\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def read_set_temp(self):
        self.session.write(b's\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def coolstate(self):
        self.session.write(b'co\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)

    def set_cool(self,state : str):
        #on off outo
        self.session.write(('co=%s\r\n'%state).encode())

    def read_current_temp(self):
        self.session.write(b't\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret


    def heatpower(self):
        self.session.write(b'po\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret      

    def read_holdtime(self):
        self.session.write(b'pt\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret



if __name__ == "__main__":
    zctb = ZCTB_400L('COM11')
    # zctb.set_temp(16)
    while True:
        state = zctb.read_state()
        if state=='1':
            print('ok')
            break
        time.sleep(5)

    
