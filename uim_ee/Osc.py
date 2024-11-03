# -*- encoding: utf-8 -*-
'''
@File    :   Osc.py
@Time    :   2024/05/05 16:04:03
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''

# here put the import lib

import re
from tkinter import OFF
import serial
import time
import vxi11


DEBUG = 1
def debugPrint(msg):
    if DEBUG:
        print(msg)


# 苏州固纬电子的示波器
class GDS_2000x():
    def __init__(self, comport) -> None:
        self.session = serial.Serial(comport,9600,timeout=0.5)
        self.session.flushInput()
        self.session.flushOutput()

    def getIDN(self):
        self.session.write(b'*IDN?\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode()
        debugPrint(ret)
        return ret

    def saveImage(self, filename, disk=1):
        diskpath = 'Disk:/'
        usbpath = 'USB:/'
        if disk:
            filepath = diskpath
        else:
            filepath = usbpath
        filefullpath = filepath+filename 
        self.session.write((':SAVe:IMAGe "%s.PNG"\r\n' % filefullpath).encode())
        
    def setSaveImgFmt(self, fmt: str='PNG'):
        self.session.write((':SAVe:IMAGe:FILEFormat %s\r\n' % fmt).encode())

    def setInkSaverOn(self):
        self.session.write(b':SAVe:IMAGe:INKSaver ON\r\n')

    def setInkSaverOff(self):
        self.session.write(b':SAVe:IMAGe:INKSaver OFF\r\n')

    
    def run(self):
        self.session.write(b':RUN\r\n')

    def stop(self):
        self.session.write(b':STOP\r\n')
    
    def single(self):
        self.session.write(b':SINGle\r\n')

    def getTrigStat(self):
        """Returns the current state of the triggering system.
        """
        self.session.write(b':TRIGger:STATe?\r\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode()
        debugPrint(ret)
        return ret

    def setTrigSrc(self, src: str='CH1'):
        """Set the trigger source
        
        :src: {CH1-4, EXT, LINE, D0-15}
        """
        self.session.write((':TRIGger:SOURce %s\r\n' % src).encode())

    def setTrigLevel(self, level):
        """Set the trigger level

        :level: {TTL | ECL | SETTO50 | <NRf>}
        """
        self.session.write((':TRIGger:LEVel %s\r\n' % level).encode())

    def setTrigNormalMode(self):
        self.session.write(b':TRIGger:MODe NORMal\r\n')
    
    def setTrigAutoMode(self):
        self.session.write(b':TRIGger:MODe AUTO\r\n')

    def setTrigSlope(self, slope: str='RISe'):
        """
        :slope: { RISe | FALL | EITher}
        """
        self.session.write((':TRIGger:EDGe:SLOP %s\r\n' % slope).encode())       

    def setVerticalPos(self, chnn:int, pos:float):
        self.session.write((':CHANnel%s:POSition %s\r\n' % (chnn, pos)).encode())

    def setVerticalScale(self, chnn:int, scale:float):
        self.session.write((':CHANnel%s:SCALe %s\r\n' % (chnn, scale)).encode())

    def setLabel(self, chnn:int, label:str):
        self.session.write((':CHANnel%s:LABel "%s"\r\n' % (chnn, label)).encode())

    def setLabelDispOn(self, chnn:int):
        self.session.write((':CHANnel%s:LABel:DISPlay ON\r\n' % chnn).encode())
    
    def setLabelDispOff(self, chnn:int):
        self.session.write((':CHANnel%s:LABel:DISPlay OFF\r\n' % chnn).encode())

    def setHorizontalPos(self, pos:float):
        self.session.write((':TIMebase:POSition %s\r\n' % pos).encode())

    def setHorizontalScale(self, scale:float):
        self.session.write((':TIMebase:SCALe %s\r\n' % scale).encode())

    def setMainMode(self):
        self.session.write((':TIMebase:MODe MAIN\r\n').encode())

    def setXYMode(self):
        self.session.write((':TIMebase:MODe XY\r\n').encode())
    
    def setZoomMode(self):
        self.session.write((':TIMebase:MODe WINDow\r\n').encode())

    def setZoomPos(self, pos:float):
        self.session.write((':TIMebase:WINDow:POSition %s\r\n' % pos).encode())

    def setZoomScale(self, scale:float):
        self.session.write((':TIMebase:WINDow:SCALe %s\r\n' % scale).encode())
       


# LECROY的示波器
class LECROY_HD9000():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret
    
    def setOffset(self, chnn, ofst):
        """
        <channel>:= <C1 to Cn>
        <offset>:= <any valid value>
        """
        self.session.write('%s:OFFSET %sV' % (chnn, ofst))

    def setTimeDiv(self, tdiv):
        """
        <value>:= <any valid value>
        """
        self.session.write('TIME_DIV %E' % tdiv)

    def setVoltDiv(self, chnn, vdiv):
        """
        <channel>:= <C1 to Cn>
        <v_gain>:= <any valid value><unit=V>
        """
        self.session.write('%s:VOLT_DIV %sV' % (chnn, vdiv))

    def setAutoMode(self):
        self.session.write('TRIG_MODE AUTO')

    def setNormalMode(self):
        self.session.write('TRIG_MODE Normal')

    def setSingleMode(self):
        self.session.write('TRIG_MODE SINGLE')

    def setStopMode(self):
        self.session.write('TRIG_MODE Stop')

    def getTrigMode(self):
        ret = self.session.ask('TRIG_MODE?')
        debugPrint(ret)
        return ret

    def setTrigTypeSrc(self, type, src):
        """
        type:DROP,EDGE,GLIT,INTV,PA,RUNT,SLEW,SQ,TEQ,TEQ1,SNG,STD
        src:C1,C2,Cn
        """
        self.session.write('TRIG_SELECT %s,SR,%s' % (type, src))

    def setTrigSlope(self, src, slope):
        """
        <trig_source>:= {C1, C2, C3, C4, LINE, EX, EX10, ETM10}
        <trig_slope>:= {NEG, POS}
        """
        self.session.write('%s:TRIG_SLOPE %s' % (src, slope))

    def setTrigLevel(self, src, level):
        """
        <trig_source>:= <C1 to Cn, EX, EX10, ETM10>
        <trig_level>V
        """
        self.session.write('%s:TRIG_LEVEL %sV' % (src, level))

    def setDispOn(self, chnn):
        """
        <trace>:= C1 to Cn, F1 to Fn, TA to TD
        """
        self.session.write('%s:TRACE ON' % chnn)

    def setDispOff(self, chnn):
        """
        <trace>:= C1 to Cn, F1 to Fn, TA to TD
        """
        self.session.write('%s:TRACE OFF' % chnn)

    def setLabel(self, chnn, label:str):
        self.session.write('%s:TRACE_LABEL %s' % (chnn, label))

    def getParameterCustom(self, col):
        ret = self.session.ask('PACU? %s' % col)
        debugPrint(ret)
        return ret

    def deletePACU(self, col):
        self.session.write('PADL %s' % col)

    def setParameterCustom(self, col, meastyp, chnn):
        self.session.write('PACU %s,%s,C%s' % (col, meastyp, chnn))

    def getValuePACU(self, meastyp, chnn):
        '''
        Frequency, 
        Duty cycle:DUTY, Mean:MEAN, risetime:RISE, falltime:FALL, 

        '''
        ret = self.session.ask('C%s:PAVA? %s' % (chnn, meastyp))
        debugPrint(ret)
        if 'UNDEF' in ret.split(',')[1]:
            return 'UNDEF'
        else:


        # debugPrint(ret.split(',')[1].split(' ')[0])
            return float(ret.split(',')[1].split(' ')[0])

    def saveScreenImg(self, dirpath, filename):
        """
        HARDCOPY_SETUP DEV,<device>,FORMAT,<format>,BCKG,<bckg>,
        DEST,<destination>,DIR,"<directory>",AREA,<hardcopyarea>
        [,FILE,"<filename>",PRINTER,"<printername>",PORT,<portname>]
        <device>:= {BMP, JPEG, PNG, TIFF}
        <format>:= {PORTRAIT, LANDSCAPE}
        <bckg>:= {BLACK, WHITE}
        <destination>:= {PRINTER, CLIPBOARD, EMAIL, FILE, REMOTE}
        <area>:= {GRIDAREAONLY, DSOWINDOW, FULLSCREEN}
        <directory>:= legal DOS path, for FILE mode only
        <filename>:= filename string, no extension, for FILE mode only
        <printername>:= valid printer name, for PRINTER mode only
        <portname>:= {GPIB, NET}
        """
        self.session.write('HCSU DEV,PNG,FORMAT,PORTRAIT,BCKG,BLACK,DEST,FILE,DIR,"%s",AREA,GRIDAREAONLY,FILE,"%s"' % (dirpath, filename))
        self.session.ask('INR?')
        time.sleep(1)
        self.session.write('SCDP')
        print('saved!')


# 鼎阳的示波器
class SDS2504X():
    def __init__(self, ipaddr) -> None:
        self.session = vxi11.Instrument(ipaddr)

    def getIDN(self):
        ret = self.session.ask('*IDN?')
        debugPrint(ret)
        return ret


    def setTimeDiv(self,time):
        '''
        set time div
        '''
        self.session.write('TIM:SCAL %s'%(time))


    def getValuePACU(self, meastyp, chnn):
        '''
        Frequency, Duty cycle:DUTY, Mean:MEAN
        '''
        ret = self.session.ask('C%s:PAVA? %s' % (chnn, meastyp))
        debugPrint(ret)
        if '****' in ret.split(',')[1]:
            return 'UNDEF'
        else:
        # debugPrint(ret.split(',')[1].split(' ')[0])
            return float(ret.split(',')[1].split('V')[0])

    def TrigeMode(self,mode='NORMal'):
        '''
        mode : SINGle  NORMal   AUTO
        '''
        self.session.write('TRIGger:MODE %s'%(mode))

    def getTrigMode(self):
        '''
        query returns the current state of the trigger\n
        return str
        '''
        ret = self.session.ask('TRIG:STAT?')
        debugPrint(ret)
        return ret  

      
    def setOffset(self, chnn, offset_value):
        """
        CHAN1:OFFS -3.8E+00  
        """
        self.session.write('CHAN%s:OFFS %s'%(chnn, offset_value))

    def setTrigTypeSrc(self,type,src):
        '''
        set the type of trigger\n
        type:EDGE|PULSE|SLOPe|INTerval|PATTern|RUNT|QUALified|WINDow|DROPout\n
        |VIDeo|QUALified|NTHEdge|DELay|SETuphold|IIC|SPI|UART|LIN|CAN|FLEXray\n
        |CANFd|IIS|1553B|SENT\n 
        src:1 2 3 4

        '''
        self.session.write('TRIGger:TYPE %s'%(type))
        self.session.write('TRIG:%s:SOUR C%s'%(type,src))



    def setEdgeLevel(self,level):
        '''
        set the trigger level of the edge trigger
        '''
        self.session.write('TRIG:EDGE:LEV %s'%(level))


    def setEdgeSlope(self,slope):
        '''
        set the slope of the edge trigger\n
        type:RISing FALLing  ALTernate
        '''
        self.session.write('TRIG:EDGE:SLOP %s'%(slope))

    

    def SaveImage(self,path,reverse='OFF',format='PNG'):
        '''
        save Image: local  U-disk0  M
        format:bmp   jpg   png
        eg:local/test.png
        U-disk0/test.png
        net_storage/power/
        '''
        self.session.write(':SAVE:IMAGe "%s",%s,%s'%(path,format,reverse))



# main函数
if __name__ == "__main__":


    time.sleep(1)
    print(123)
    time.sleep(1)
    print(123)
    time.sleep(1)

    # osc = SDS2504X('192.168.12.253')
    # osc = LECROY_HD9000('192.168.12.128')
    # osc.TrigeMode('SINGle')
    # osc.setTimeDiv(1)

    # osc.getIDN()
    # osc.saveScreenImg(dirpath='\\192.168.12.182\\ctf2301a\\11.jpg',invert='OFF')
    # osc.session.write(':SAVE:IMAGe "U-disk0/test.png",PNG,ON')
    # wave=11
    # osc.SaveImage(path='net_storage/power/%s-%s.png'%(wave,time.strftime("-%y%m%d_%H%M%S")),reverse='OFF',format='PNG')
    # print(a)
    # osc.saveScreenImg(dirpath=r"\\"+'XIEFEIYANG\exp'+'\\', filename='test.jpg')

# while True:
#     cmd = input('>:')
#     if cmd:
#         try:
#             exec(cmd)
#         except:
#             print('Error!')