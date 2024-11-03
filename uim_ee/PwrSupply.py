# -*- encoding: utf-8 -*-
'''
@File    :   PwrSupply.py
@Time    :   2024/05/05 16:07:42
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''

# here put the import lib

import serial
import time
import vxi11

DEBUG = 1
def debugPrint(msg):
    if DEBUG:
        print(msg)


# 苏州固纬电子的电源
class GPD_X303X():
    def __init__(self, comport) -> None:
        self.session = serial.Serial(comport,9600,timeout=0.5)
        self.session.flushInput()
        self.session.flushOutput()

    def getIDN(self):
        self.session.write(b'*IDN?\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)

    def outputOn(self):
        self.session.write(b'OUT1\r\n')

    def outputOff(self):
        self.session.write(b'OUT0\r\n')

    def voltSet(self, chnn, volt):
        self.session.write(('VSET%s:%.3f\r\n' % (chnn, volt)).encode())

    def voltRead(self, chnn):
        self.session.write(('VOUT%s?\r\n' % chnn).encode())
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)

    def voltSetGet(self, chnn):
        self.session.write(('VSET%s?\r\n' % chnn).encode())
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)

    def currentSet(self, chnn, current):
        self.session.write(('ISET%s:%.3f\r\n' % (chnn, current)).encode())

    def currentRead(self, chnn):
        self.session.write(('IOUT%s?\r\n' % chnn).encode())
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)

    def currentSetGet(self, chnn):
        self.session.write(('ISET%s?\r\n' % chnn).encode())
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)

# RIGOL的电源
class DP800():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret
    
    def SelectChnnl(self,chnnl):
        '''select  chnnal '''
        self.session.write(':INST CH%s'%chnnl)

    def GetCurrChnnl(self):
        '''get which chnnal is selected'''
        ret = self.session.ask(':INST?')
        debugPrint(ret)
        return ret

    def outputOn(self,chnnl):
        '''open chnnanl output'''
        self.session.write(':OUTP CH%s,ON'%chnnl)

    def outputOff(self,chnnl):
        '''open chnnanl output'''
        self.session.write(':OUTP CH%s,OFF'%chnnl)

    def OutputSta(self,chnnl):
        '''get chnnl output status  ON or OFF'''
        ret = self.session.ask('OUTP? CH%s'%chnnl)
        debugPrint(ret)
        return ret    

    def GetChnnlAll(self,chnnl):
        '''get chnnal all information include voltage current and power'''   
        ret = self.session.ask(':MEAS:ALL? CH%s'%chnnl)
        debugPrint(ret)
        return ret 

    def voltRead(self,chnnl):
        ret = self.session.ask(':MEAS? CH%s'%chnnl)
        debugPrint(ret)
        return ret       

    def currentRead(self,chnnl):
        ret = self.session.ask(':MEAS:CURR? CH%s'%chnnl)
        debugPrint(ret)
        return ret 

    def powerRead(self,chnnl):
        ret = self.session.ask(':MEAS:POWE? CH%s'%chnnl)
        debugPrint(ret)
        return ret

    def voltage_cuurent_Set(self,chnnl:int,vol:int,current:int):
        self.session.write(':APPL CH%s,%s,%s'%(chnnl,vol,current))


    # def currentSet(self,chnnl,current):
    #     self.session.write(':APPL CH%s,,%s'%(chnnl,current))

    
    def voltSet(self,chnnl,volt):
        self.session.write(':APPL CH%s,%s'%(chnnl,volt))

    def voltSetGet(self,chnnl):
        ret = self.session.ask(':APPL? CH%s'%chnnl).split(',')[1]
        debugPrint(ret)
        return ret       

    def currentSetGet(self,chnnl):
        ret = self.session.ask(':APPL? CH%s'%chnnl).split(',')[2]
        debugPrint(ret)
        return ret 

# main函数
if __name__ == "__main__":

    psu = DP800('192.168.12.119')
    # psu.outputOff(1)
    # time.sleep(1)
    # psu.voltSet(chnnl=1,volt =1)
    # time.sleep(1)
    # psu.voltage_cuurent_Set(1,2,0.4)
    # psu.voltSetGet(1)
    # psu.currentSetGet(1)

    # psu.outputOn(1)
    # psu.GetChnnlAll(1)
    # psu.outputOff(1)
    # print(type(a))
    # psu.getIDN()

    # gpd3303d = GPD_X303X('COM9')
    # gpd3303d.getIDN()
    # time.sleep(1)
    # gpd3303d.voltSet(chnn=1, volt=1.1)
    # gpd3303d.currentSet(chnn=1, current=2.1)
    # gpd3303d.voltSet(chnn=2, volt=2.2)
    # gpd3303d.currentSet(chnn=2, current=2.2)
    # gpd3303d.outputOn()
    # time.sleep(2)
    # gpd3303d.voltSetGet(chnn=1)
    # gpd3303d.voltRead(chnn=1)
    # gpd3303d.currentSetGet(chnn=1)
    # gpd3303d.currentRead(chnn=1)
    # gpd3303d.voltSetGet(chnn=2)
    # gpd3303d.voltRead(chnn=2)
    # gpd3303d.currentSetGet(chnn=2)
    # gpd3303d.currentRead(chnn=2)

    # gpd3303d.outputOff()
