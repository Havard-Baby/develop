# -*- encoding: utf-8 -*-
'''
@File    :   ElecLoad.py
@Time    :   2024/04/29 21:21:36
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


######   Rigol 仪器设备  ######################

class DL3000():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret

    def getInVol(self):
        '''get input voltage'''
        ret = self.session.ask(':MEASure:VOLTage:DC?')
        debugPrint(ret)
        return ret

    def getInCur(self):
        '''get input current'''
        ret = self.session.ask(':MEASure:CURRent:DC?')
        debugPrint(ret)
        return ret

    def getInResis(self):
        '''get input resistance'''
        ret = self.session.ask(':MEASure:RESistance:DC?')
        debugPrint(ret)
        return ret

    def getInPower(self):
        '''get input power'''
        ret = self.session.ask(':MEASure:POWer:DC?')
        debugPrint(ret)
        return ret

    def OutputOn(self):
        '''output on'''
        self.session.write(':SOUR:INP:STAT 1')
 

    def OutputOff(self):
        '''output off'''
        self.session.write(':SOUR:INP:STAT 0')

    def getInSta(self):
        '''get Output is open?  return 0:close 1:open'''
        ret = self.session.ask(':SOUR:INP:STAT?')
        debugPrint(ret)
        return ret    

    def setmode(self,mode:str):
        '''
        set operation mode
        CURRent:CURR RESistance:RES VOLTage:VOLT  POWer:POW
        '''
        self.session.write(':SOUR:FUNC %s'%mode)

    def getmode(self):
        '''
        get operation mode 
        return CC CV CR CP
        '''
        ret = self.session.ask(':SOUR:FUNC?')
        debugPrint(ret)
        return ret   

    def setModeRange(self,mode:str,range):
        '''set mode range  
            mode : CURR  VOLT  RES
            CC: 4 or MIN  40 or MAX
            CV: 15 or MIN  150 or MAX
            CR: 15 or MIN  15000 or MAX
            '''
        self.session.write(':SOUR:%s:RANG %s'%(mode,range))

    def getModeRange(self,mode:str):
        '''get mode range  
            mode : CURR  VOLT  RES
            CC: 4    40 
            CV: 15   150 
            CR: 15   15000 
        '''
        ret = self.session.ask(':SOUR:%s:RANG?'% mode)
        debugPrint(ret)
        return ret       


    def setModeValue(self,mode:str,value):
        '''
        set mode value
        mode : CURR VOLT RES POW
        '''
        self.session.write(':SOUR:%s:LEV:IMM %s'%(mode,value))

    def getsetModeValue(self,mode:str):
        '''
        get set mode value
        '''
        ret = self.session.ask('SOUR:%s:LEV:IMM?'% mode)
        debugPrint(ret)
        return ret 


    def setModeCurretLimit(self,mode:str,value):
        '''
        set mode current limit value
        '''
        self.session.write(':SOUR:%s:ILIM %s'%(mode,value))

    def getsetModeCurrentLimit(self,mode:str):
        '''
        get set mode current limit value
        '''
        ret = self.session.ask('SOUR:%s:ILIM?'% mode)
        debugPrint(ret)
        return ret 

    def setModeVolLimit(self,mode:str,value):
        '''
        set mode voltage limit value
        '''
        self.session.write(':SOUR:%s:VLIM %s'%(mode,value))

    def getsetModeVolLimit(self,mode:str):
        '''
        get set mode voltage limit value
        '''
        ret = self.session.ask('SOUR:%s:VLIM?'% mode)
        debugPrint(ret)
        return ret 

    def CCmodeVon(self,value):
        '''
        set CC mode Volatage on
        '''
        self.session.write(':SOUR:CURR:VON %s'%(value))




if __name__ == "__main__":
    # 建立通信
    # elecload = DL3000('192.168.12.238')

    # 参数设置
    # elecload.setmode('RES')
    # elecload.OutputOn()
    # elecload.getmode()
    # time.sleep(5)
    # elecload.OutputOff()
    # elecload.setModeRange('RES','MAX')
    # elecload.getModeRange('CURR')
    # elecload.getInVol()

