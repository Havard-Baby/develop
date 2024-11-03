# -*- encoding: utf-8 -*-
'''
@File    :   MultiMeter.py
@Time    :   2024/05/05 16:00:31
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''

# here put the import lib


import vxi11
import serial
import time


DEBUG = 1
def debugPrint(msg):
    if DEBUG:
        print(msg)


#  kesysight 的仪器仪表
class KEYSIGHT_344X():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret

    def measureVolt(self, dcac='DC'):
        ret = self.session.ask('MEAS:VOLT:%s?' % dcac)
        debugPrint(ret)
        return ret

    def measureCurrent(self, dcac='DC'):
        ret = self.session.ask('MEAS:CURR:%s?' % dcac)
        debugPrint(ret)
        return ret

class AGILENT_344X():
    def __init__(self, comport) -> None:
        self.session = serial.Serial(comport,9600,timeout=0.5)
        self.session.flushInput()
        self.session.flushOutput()
        self.session.write(b'SYSTem:REMote\r\n')

    def getIDN(self):
        self.session.write(b'*IDN?\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)

    def measureVolt(self, dcac='DC'):
        self.session.write(('MEASure:VOLTage:%s? DEF,DEF' % dcac).encode())
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)
        return ret

    def measureCurrent(self, dcac='DC'):
        self.session.write(('MEAS:CURR:%s? DEF,DEF' % dcac).encode())
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode("gbk")
        debugPrint(ret)
        return ret

class SDM3065():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret

    def measureVolt(self, dcac='DC'):
        ret = self.session.ask('MEAS:VOLT:%s?' % dcac)
        debugPrint(ret)
        return ret

    def measureCurrent(self, dcac='DC'):
        ret = self.session.ask('MEAS:CURR:%s?' % dcac)
        debugPrint(ret)
        return ret

    def average(self):
        ret = self.session.ask('CALCulate:AVERage:AVERage?')
        debugPrint(ret)
        return ret  

    def TRANsform(self,staute):
        self.session.write('CALCulate:TRANsform:HISTogram %s'%staute)
        
    def configCurrent(self, dcac='DC'):
        self.session.write('CONF:CURR:%s?' % dcac)

    def configVolt(self, dcac='DC'):
        self.session.write('CONF:VOLT:%s?' % dcac)

    def SampleCount(self,count:int):
        self.session.write('SAMP:COUN %s' % count)


if __name__ == "__main__":

    print("already~")
    # dmm = AGILENT_344X('COM7')
    # dmm.getIDN()
    # dmm.measureVolt()
    # a = SDM3065('192.168.12.250')
    # a.getIDN()
    # a.average()
    # a.TRANsform(1)
    # a.configVolt('AC')
    # a.SampleCount(1000)
    # a.session.write('TRIG:COUN 1')
    # a.session.write('TRIG:SOUR IMM')
    # a.session.write('CALCulate:CLEar')
    # a.session.write('INIT')

    # time.sleep(30)
    # a.average()


    ##############窗口命令行################
    # while True:
    #     cmd = input('>:')
    #     if cmd:
    #         try:
    #             exec(cmd)
    #         except:
    #             print('Error!')



