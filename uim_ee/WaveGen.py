# -*- encoding: utf-8 -*-
'''
@File    :   WaveGen.py
@Time    :   2024/05/05 16:10:13
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''

# here put the import lib

from tkinter import E
import vxi11
import serial
import time


DEBUG = 1
def debugPrint(msg):
    if DEBUG:
        print(msg)

# 鼎阳的信号发生器
class SDG6000X_E():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret

    def OutputOn(self,chnnl = 1):
        self.session.write('C%s:OUTP ON'%chnnl)

    def OutputOff(self,chnnl = 1):
        self.session.write('C%s:OUTP OFF'%chnnl)

    def WaveType(self,chnnl,type):
        '''
        def output wave type
        SINE  SQUARE   RAMP   PULSE   NOISE   APB   DC   PRBS   IQ
        '''
        self.session.write('C%s:BSWV WVTP,%s'%(chnnl,type))

    def Frequency(self,chnnl,frequency):
        '''
        def output wave frequency
        '''
        self.session.write('C%s:BSWV FRQ,%s'%(chnnl,frequency))

    def Period(self,chnnl,period):
        '''
        def output wave period
        '''
        self.session.write('C%s:BSWV PERI,%s'%(chnnl,period))

    def Amplitude(self,chnnl,amplitude):
        '''
        def output wave amplitude
        '''
        self.session.write('C%s:BSWV AMP,%s'%(chnnl,amplitude))

    def Offset(self,chnnl,offset):
        '''
        def output wave offset
        '''
        self.session.write('C%s:BSWV OFST,%s'%(chnnl,offset))


    def Duty(self,chnnl,duty):
        '''
        def output wave duty
        '''
        self.session.write('C%s:BSWV DUTY,%s'%(chnnl,duty))


    def Time_Rise(self,chnnl,rise):
        '''
        def output wave rise time(10% ~ 90%)
        '''
        self.session.write('C%s:BSWV RISE,%s'%(chnnl,rise))

    def Time_Fall(self,chnnl,fall):
        '''
        def output wave fall time(10% ~ 90%)
        '''
        self.session.write('C%s:BSWV FALL,%s'%(chnnl,fall))

    def HighLevel(self,chnnl,highlevel):
        '''
        def output wave highlevel
        '''
        self.session.write('C%s:BSWV HLEV,%s'%(chnnl,highlevel))   

    def LowLevel(self,chnnl,lowlevel):
        '''
        def output wave lowlevel
        '''
        self.session.write('C%s:BSWV LLEV,%s'%(chnnl,lowlevel))   


    def getchnnlStatus(self,chnnl):
        '''
        return current chnnl status include type frequency period and etc
        '''
        ret = self.session.ask('C%s:BSWV?'%(chnnl))
        debugPrint(ret)
        return ret       

    # def RecallWav(self,chnnl : int,name : str ):
    #     '''
    #     recall the wave stroe in generator
    #     '''
    #     # self.session.write('C%s:WVDT USER,%s'%(chnnl,name))  
    #     self.session.write('WVDT?\s USER,%s'%(name))   

    # def GetRecallWav(self,chnnl:int,name:str):
    #     ret = self.session.ask('WVDT? USER,%s'%(name))
    #     debugPrint(ret)
    #     return ret         

    def GetStoreInWaveName(self):
        '''
        get stroe in user local's wave name
        '''
        ret = self.session.ask('STL? USER')
        debugPrint(ret)
        return ret.split(',')[1:]      

    def SetARB(self,chnnl:int,name:str):
        '''
        set arb 
        eg: wave650mv800mv30ms  local
        '''
        self.session.write('C%s:ARWV NAME,%s'%(chnnl,name))
        print('C%s:ARWV NAME,''%s'''%(chnnl,name))

        
    def GetARB(self,chnnl:int):
        '''
        get current arb name
        '''
        ret = self.session.ask('C%s:ARWV?'%(chnnl))
        debugPrint(ret)
        return ret  

    # def SetARBMode(self,chnnl,mode):
    #     '''
    #     mode : AFG  AWG
    #     '''
    #     self.session.write(':C%s:ARBMode %s'%(chnnl,mode))


    # def GetARBmode(self,chnnl):
    #     ret = self.session.ask(':C%s:ARBMode?'%(chnnl))
    #     debugPrint(ret)
    #     return ret       


# main函数
if __name__ == "__main__":
    a = SDG6000X_E('192.168.12.149')
    a.getIDN()
    c = a.GetStoreInWaveName()
    a.Period(2,0.5)

     
