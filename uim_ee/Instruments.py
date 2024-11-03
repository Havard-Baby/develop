# -*- encoding: utf-8 -*-
'''
@File    :   Instruments.py
@Time    :   2024/04/29 21:30:05
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''

# here put the import lib

import pyvisa as visa
import time
import numpy as np
import serial
import see  


# debug 信息
DEBUG = 1
def debugPrint(msg):
    if DEBUG:
        print(msg)


# 仪器初始化
class InstrumentInitial(object):
    def __init__(self, instr_id):
        self.instr_id = instr_id
        self.rm = visa.ResourceManager()
        self.dev_connect_visa = False
        self.dev_list = self.rm.list_resources()
        self.inst = None
        self.list_connected_devices()

    def instr_initial(self):
        try:
            self.inst = self.rm.open_resource('{}'.format(self.instr_id))
        except(visa.errors.Error, visa.errors.VisaIOError) as e:
            print("\033[0;31mERROR: {} UNCONNECT\033[0m".format(self.instr_id))     # 30-37

    @property
    def dev_info(self):
        return self.inst.query("*IDN?")

    def write_command(self, command):
        self.inst.write(command)

    def query_command(self, command):
        return self.inst.query(command)

    def list_connected_devices(self):
        self.dev_list = self.rm.list_resources()
        self.dev_connect_visa = False
        # 'IP:169.254.174.89'   # 'TCPIP0::169.254.174.89::inst0::INSTR'
        # 'GPIB:2'      # 'GPIB0::12::INSTR'
        if 'IP' in self.instr_id:
            self.instr_id = 'TCPIP0::{}::inst0::INSTR'.format(self.instr_id.split(':')[1])
        elif 'GPIB' in self.instr_id:
            self.instr_id = 'GPIB0::{}::INSTR'.format(self.instr_id.split(':')[1])
        elif 'USB' in self.instr_id:
            pass
        elif 'COM' in self.instr_id:
            pass
        else:
            print("\033[0;37;41mERROR: Unrecognized instrument interface types, only IP and GPIB can be recognized !!\033[0m")

        for dev_ in self.dev_list:
            if self.instr_id in dev_:
                self.dev_connect_visa = True
        if not self.dev_connect_visa:
            pass
            # print("\033[0;37;41mERROR: The instrument is not linked to VISA !!\033[0m")


"""数字万用表"""
class DigitalMultimeterSDM3065X(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def clear_state(self):
        # 清除状态命令。清除所有寄存器组中的事件寄存器。也会清除错误队列。
        self.write_command('*CLS')  #

    def reset_dev(self):
        # 将仪器恢复为出厂默认状态
        self.write_command('*RST')

    def dc_voltage(self, counts=1, plc=0.005):
        # 等待 测量完成并将所有可用的测量结果复制到仪器的输出缓冲区
        self.write_command('CONF:VOLT:DC')
        # self.write_command('TRIG:SOUR IMM')  # 设置触发源为立即触发
        self.write_command('VOLT:DC:NPLC {}'.format(plc))

        self.write_command('SAMP:COUN {}'.format(counts))  # 设置采样次数

        voltage_str = self.query_command('READ?')[:-1]  # 读取本次测量生成的测量值
        voltage_out = []
        for voltage in voltage_str.split(','):
            voltage_out.append(float(voltage))
        return voltage_out

    def measure_dc_current(self, plc=0.05, RANG=20e-3):
        # Measure Current
        # PLC: 0.005,0.05,0.5,1,10,100
        # RANG: Auto,200e-6,2e-3,20e-3,200e-3
        self.write_command('CONF:CURR:DC')
        self.write_command('CURR:DC:NPLC {}'.format(plc))
        self.write_command('CURR:DC:RANG {}'.format(RANG))
        ret = self.query_command('READ?')[:-1]
        # ret = self.query_command('MEAS:CURR:DC?')
        # time.sleep(wait_time)
        current = float(ret.replace('\n', ''))
        return current

    def measure_dc_voltage(self, plc=0.05, RANG=200):
        # Measure Voltage
        # PLC: 0.005,0.05,0.5,1,10,100
        # RANG: Auto,200e-3,2,20,200,1000
        self.write_command('CONF:VOLT:DC')
        self.write_command('VOLT:DC:NPLC {}'.format(plc))
        self.write_command('VOLT:DC:RANG {}'.format(RANG))
        ret = self.query_command('READ?')[:-1]
        voltage = float(ret.replace('\n', ''))
        return voltage

    def measure_resistence(self, plc=0.05, RANG=200):
        # Rang: 200 Ω|2 kΩ|20 kΩ|200 kΩ|1 MΩ|10 MΩ|100 MΩ
        # PLC: 0.005,0.05,0.5,1,10,100
        self.write_command('CONF:RES')
        self.write_command('RES:RANG {}'.format(RANG))
        self.write_command('RES:NPLC {}'.format(plc))
        ret = self.query_command('READ?')[:-1]
        resistence = float(ret.replace('\n', ''))
        return resistence

class Keysight34461A(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def clear_state(self):
        # 清除状态命令。清除所有寄存器组中的事件寄存器。也会清除错误队列。
        self.write_command('*CLS')  #

    def reset_dev(self):
        # 将仪器恢复为出厂默认状态
        self.write_command('*RST')

    def dc_voltage(self, counts=1, plc=0.02):
        # 等待 测量完成并将所有可用的测量结果复制到仪器的输出缓冲区
        self.write_command('CONF:VOLT:DC {}, 0.003'.format(plc))
        self.write_command('TRIG:SOUR IMM')  # 设置触发源为立即触发
        self.write_command('VOLT:DC:RANG:AUTO ON')  # 设置电压量程自动调整
        self.write_command('SAMP:COUN {}'.format(counts))  # 设置采样次数
        voltage_str = self.query_command('READ?')[:-1]  # 读取本次测量生成的测量值
        voltage_out = []
        for voltage in voltage_str.split(','):
            voltage_out.append(float(voltage))
        return voltage_out

    def dc_voltage_counts(self, counts=10, plc=0.02):
        # 等待 测量完成并将所有可用的测量结果复制到仪器的输出缓冲区
        self.write_command('CONF:VOLT:DC {},0.003'.format(plc))
        self.write_command('VOLT:DC:RANG:AUTO ON')  # 设置电压量程自动调整
        # self.write_command('VOLT:DC:RANG:MAX')  # 设置电压量程自动调整
        self.write_command('TRIG:SOUR BUS')  # 设置触发源为等待触发
        self.write_command('SAMP:COUN {}'.format(counts))  # 设置采样次数
        self.write_command('INIT')
        self.write_command('*TRG')
        time.sleep(0.1)
        voltage_str = self.query_command('FETC?')[:-1]  # 读取本次测量生成的测量值
        # vol = voltage_str.split(',')[0]
        voltage_float = []
        for vol in voltage_str.split(','):
            voltage_float.append(float(vol))
        print(np.mean(voltage_float))
        return np.mean(voltage_float)

    def measure_dc_current(self, wait_time=2):
        # counts = 1
        ret = self.query_command('MEAS:CURR:DC?')
        time.sleep(wait_time)
        current = float(ret.replace('\n', ''))
        return current


"""信号发生器"""
class SDG7102A(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def set_wvtp(self, channel, wvtp):
        self.write_command('C{}:BSWV WVTP,{}'.format(channel, wvtp))

    def set_freq(self, channel, freq, amp=3.3, offset=2):
        self.write_command('C{}:BSWV FRQ,{}'.format(channel, freq))
        self.write_command('C{}:BSWV AMP,{}'.format(channel, amp))
        self.write_command('C{}:BSWV OFST,{}'.format(channel, offset))


"""示波器"""
class OscilloscopeSDS2504X(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def get_measure(self, ch, type='FREQ'):
        """

        :param ch: 通道{1,2,3,4}
        :param type: {PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN
                    |STDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPR
                    E|OVSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|
                    NDUTY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE10T90|
                    FALL90T10|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLE
                    S|REDGES|FEDGES|EDGES|PPULSES|NPULSES|PHA|S
                    KEW|FRR|FRF|FFR|FFF|LRR|LRF|LFR|LFF|PACArea|NAC
                    Area|ACArea|ABSACArea|PSLOPE|NSLOPE|TSR|TSF|THR
                    |THF}
        :return:
        """
        self.write_command('MEAS:SIMP:SOUR C{}'.format(ch))
        time.sleep(2)
        value = float(self.query_command('MEAS:SIMP:VAL? {}'.format(type)).split('\n')[0])
        return value

    def trigger_state(self, mode='STOP'):
        self.write_command('TRIG:{}'.format(mode))

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
        Frequency, Duty cycle:DUTY, Mean:MEAN
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
        time.sleep(0.1)
        self.session.write('SCDP')

"""电源"""
class DP832A(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def set_voltage_current(self, channel, voltage, current=1):
        self.write_command(':APPL CH{},{},{}'.format(channel, voltage, current))

    def channel_state(self, channel, state):
        self.write_command(':OUTP CH{},{}'.format(channel, state.upper()))


class SPD3303X(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def set_voltage_current(self, channel, voltage, current=1):
        self.write_command('CH{}:VOLTage {}'.format(channel, voltage))
        self.write_command('CH{}:CURRent {}'.format(channel, current))

    def channel_state(self, channel, state):
        self.write_command('OUTP CH{},{}'.format(channel, state.upper()))


class GPO_2303S(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def set_voltage_current(self, channel, voltage, current=1):
        self.write_command('VSET{}:{}'.format(channel, round(voltage, 3)))
        self.write_command('ISET{}:{}'.format(channel, current))

    def channel_state(self, state):
        if 'ON' in state.upper():
            self.write_command('OUT1')
        elif 'OFF' in state.upper():
            self.write_command('OUT0')
        else:
            print("\033[0;37;41mERROR: Command Error !!\033[0m")


"""源表"""
class B2902B(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        self.instr_initial()

    def rst_dev(self):
        self.write_command('*RST')

    def set_voltage(self, channel, voltage, curr_lim=1e3):
        self.write_command(':SOUR{}:FUNC:MODE VOLT'.format(channel))
        self.write_command(':SOUR{}:VOLT {}'.format(channel, voltage))
        self.write_command(':SOUR{}:VOLT RANG:AUTO ON'.format(channel))
        # self.write_command(':SOUR{}:VOLT:RANG:AUTO:LLIM {}'.format(channel, volt_range))
        self.write_command(':SENS{}:CURR:PROT {}'.format(channel, curr_lim))

    def set_current(self, channel, current, curr_range=10):
        self.write_command(':SOUR{}:FUNC:MODE CURR'.format(channel))
        self.write_command(':SOUR{}:CURR {}'.format(channel, current))
        # self.write_command(':SOUR{}:CURR RANG:AUTO ON'.format(channel))
        # self.write_command(':SOUR{}:CURR:RANG:AUTO:LLIM {}'.format(channel, curr_range))

    def set_state(self, channel, state):
        self.write_command(':OUTP{} {}'.format(channel, state.upper()))

    def meas_set(self, channel, nplc=0.1, curr_lim=1, volt_lim=20):
        self.write_command(":SENS{}:FUNC 'CURR','VOLT'".format(channel))
        self.write_command(":SENS{}:CURR:RANG:AUTO ON".format(channel))
        self.write_command(":SENS{}:CURR:NPLC {}".format(channel, nplc))
        self.write_command(":SENS{}:CURR:PROT {}".format(channel, curr_lim))
        self.write_command(":SENS{}:VOLT:RANG:AUTO ON".format(channel))
        self.write_command(":SENS{}:VOLT:NPLC {}".format(channel, nplc))
        self.write_command(":SENS{}:VOLT:PROT {}".format(channel, volt_lim))

    def get_curr(self, channel):
        ret = self.query_command(':MEAS{}:CURR?'.format(channel))
        current = float(ret.replace('\n', ''))
        return current

    def get_volt(self, channel):
        ret = self.query_command(':MEAS{}:VOLT?'.format(channel))
        voltage = float(ret.replace('\n', ''))
        return voltage


"""电子负载"""
class DL3021A(InstrumentInitial):
    def __ini__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
    def connect(self):
        self.instr_initial()
    # def cc_setting(self, current=0.2):
    #     self.write_command("*IDN?")
    #     self.write_command(":SOUR:FUNC CUR")
    #     self.write_command(":SOUR:CURR:LEV:IMM,{}".format(current))
    def turn_on(self):
        self.write_command(":SOUR:INP:STAT 1")
    def turn_off(self):
        self.write_command(":SOUR:INP:STAT 0")
    def cur_keep(self, current=3):
        self.write_command(":SOUR:FUNC CURR")
        self.write_command(":SOUR:CURR:LEV:IMM {}".format(current))


""""油槽"""
class ZCTB(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        # self.instr_initial()
        self.session = serial.Serial(dev_id, 9600, timeout=0.5)

    def getID(self):
        self.write_command('*ver\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt)
        debugPrint(ret)

    def set_temp(self,temp):
        self.write_command('s={}\n'.format(temp))

    def set_sr(self,scanrate):
        self.write_command('sr={}\n'.format(scanrate))

    def read_state(self):
        # 0 不稳定 1稳定
        self.write_command('st\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def read_set_temp(self):
        self.write_command('s\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def coolstate(self):
        self.write_command('co\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)

    def set_cool(self,state : str):
        #on off outo
        self.write_command(('co={}\n'.format(state)).encode())

    def read_current_temp(self):
        self.write_command('t\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def heatpower(self):
        self.write_command('po\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def read_holdtime(self):
        self.write_command('pt\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret


"""温箱"""
class TEMP_BOX(InstrumentInitial):
    def __init__(self, dev_id):
        """
        :param dev_id: dev_id = 'COM10'
        """
        InstrumentInitial.__init__(self, dev_id)
        # self.instr_initial()
        self.session = serial.Serial(dev_id, 9600, timeout=0.5)

    def getID(self):
        self.write_command('*ver\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt)
        debugPrint(ret)

    def set_temp(self,temp):
        self.write_command('s={}\n'.format(temp))

    def set_sr(self,scanrate):
        self.write_command('sr={}\n'.format(scanrate))

    def read_state(self):
        # 0 不稳定 1稳定
        self.write_command('st\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def read_set_temp(self):
        self.write_command('s\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def coolstate(self):
        self.write_command('co\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)

    def set_cool(self,state : str):
        #on off outo
        self.write_command(('co={}\n'.format(state)).encode())

    def read_current_temp(self):
        self.write_command('t\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def heatpower(self):
        self.write_command('po\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret

    def read_holdtime(self):
        self.write_command('pt\n')
        time.sleep(0.1)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode().split(':')[1].rstrip('\n')
        debugPrint(ret)
        return ret


"""快速温冲"""   #### UIM实验室暂无
class ATS5XX(InstrumentInitial):
    def __init__(self, dev_id):
        InstrumentInitial.__init__(self, dev_id)
        # self.instr_initial()
        self.session = serial.Serial(dev_id, 9600, timeout=0.5)

    def set_temp(self,state, temp):
        """
        state, temp = 2, -40
        :param state: 0 高温
        :param temp:
        :return:
        """

        # self.session.write(b'*RST')
        self.session.write(b'%RM')
        self.session.write(b'SETN %d\n' % state)
        self.session.write(b'SETP %f\n' % temp)

    def read_current_temp(self):
        self.session.write(b'TEMP?\n')
        time.sleep(0.5)
        cnt = self.session.in_waiting
        ret = self.session.read(cnt).decode()  # .split(':')
        print(ret)
        return ret

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
        time.sleep(1)
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


"""主函数"""

if __name__ == '__main__':

    print("dedededed")
    rm = visa.ResourceManager()
    print(rm.list_resources())

    ## 串口通信
    # ser = serial.Serial('COM6',115200,timeout=0.5)
    # a = ser.read(100)
    # print(a)
    # print(str(a[0]))
    # print(str(a[1]))
    # print(str(a[2]))
    # print(list(a))

    ##############################
    # 电源dp832a
    # dp832a = DP832A('IP:192.168.12.118')
    # print(dp832a.dev_info)
    # dp832a.set_voltage_current(1, 1.2)
    # dp832a.channel_state(1, 'ON')

    ##############################
    # # 电源b2902b
    # b2902b = B2902B('IP:192.168.12.111')
    # b2902b.set_voltage(1, 3.3)

    ##############################
    # # 电源gpo_2303s
    # gpo_2303s = GPO_2303S("COM3")
    # print(gpo_2303s.dev_info)
    # gpo_2303s.set_voltage_current(2, 5, 1)
    # gpo_2303s.channel_state('ON')
    # gpo_2303s.channel_state('OFF')

    ##############################
    # # 数字万用表
    # sdm3065 = DigitalMultimeterSDM3065X('IP:192.168.12.20')
    # current = sdm3065.measure_dc_current()
    # key34461 = Keysight34461A('IP:169.254.4.61')
    # volt = key34461.dc_voltage()

    ##############################
    # # 温箱
    # temp_box = TEMP_BOX('COM10')
    # temp_box.session.readinto(10)
    # temp_box.session.write(42101)
    # temp_box.dev_info()

    ##############################
    # # 油槽
    # zctb = ZCTB_400L('COM10')
    # zctb.set_temp(16)

    ##############################
    # 负载
    # dl3021a = DL3021A('IP:192.168.12.126')
    # dl3021a.connect()
    # dl3021a.cur_keep(15e-3)
    # dl3021a.turn_on()

    ##############################
    # # 快速温箱
    # temp_box = ATS5XX('COM14')
    # temp_box.set_temp(1, 25)
    # state, temp=2, -40.0
    # spd3303 = SPD3303X('IP:192.168.12.43')
    # # list_A = list(range(1, 10, 3))
    # # for i in list_A:
    # spd3303.set_voltage_current(1, 0, 0.4)
    # spd3303.channel_state(1, "ON")
    # time.sleep(1)
    # for i in range(1, 10, 3):
    #     spd3303.set_voltage_current(1, i/10, 0.4)
    #     time.sleep(1)
    # spd3303.channel_state(1, "OFF")


    ##############窗口命令行################
    # while True:
    #     cmd = input('>:')
    #     if cmd:
    #         try:
    #             exec(cmd)
    #         except:
    #             print('Error!')




