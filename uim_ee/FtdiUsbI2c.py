# -*- encoding: utf-8 -*-
'''
@File    :   FtdiUsbI2c.py
@Time    :   2024/04/29 21:27:37
@Author  :   feiyang.xie 
@Version :   1.0
@Contact :   feiyang.xie@uim-solution.com
'''
# here put the import lib

from pyftdi.i2c import *
import re
import usb.core
from pyftdi.ftdi import Ftdi
from pyftdi.ftdi import UsbTools
import time


# usb转i2c
class USB2IIC():

    # 初始化
    def __init__(self, url=UsbTools.build_dev_strings('ftdi', Ftdi.VENDOR_IDS, Ftdi.PRODUCT_IDS, Ftdi.list_devices())[0][0], sla=0x5C):
        self.url = url
        self.sla = sla
        self.port = I2cController()
        self.port.configure(url)
        # self.session = self.port.get_port(sla>>1)
        self.i2cPort = self.port.get_port(self.sla>>1)

    # 配置寄存器
    def configRegister(self, bigendian: bool = False, width: int = 1):
        """Reconfigure the format of the slave address register (if any)

            :param bigendian: True for a big endian encoding, False otherwise
            :param width: width, in bytes, of the register
        """
        self.i2cPort.configure_register(bigendian, width)

    # 设置从机地址
    def setSla(self, sla):
        """set slave address

            :sla: 8 bit slave address
        """
        self.sla = sla
        self.i2cPort = self.port.get_port(sla>>1)

    # 从机应答
    def slaAck(self):
        """detect slave address

            :sla: 8 bit slave address
        """
        try:
            self.port._do_prolog1(self.sla)
            return True
        except:
            return False

    # 设置i2c的速率
    def setSpeed(self, speed):
        """set i2c speed
            :speed: Hz, float value the I2C bus frequency in Hz
        """
        self.port.configure(self.dev, interface = self.interface, frequency=speed)
    
    # 读字节
    def readBytes(self, addr, length=1):
        """read protocal, START->SLA|W->REGADDR->SLA|R->DATA_R->STOP

            :addr: register address
            :length: read length
        """
        ret = self.i2cPort.read_from(addr, length)
        if length==1:
            ret = ord(ret)
        else:
            ret = list(ret)
        return ret

    #  读字节(选择cmd写，减少delay时间)
    def readBytes1(self, addr, length=1):
        """read protocal, START->SLA|W->REGADDR->SLA|R->DATA_R->STOP
        optimize cmd write, decrease delay time

            :addr: register address
            :length: read length
        """
        ret = self.i2cPort.read_from1(addr, length)
        if length==1:
            ret = ret[-1]
        else:
            ret = list(ret[3+'BHI'.index(self.i2cPort._format):])
        return ret

    # 写字节
    def writeBytes(self, addr, val):
        """write protocal, START->SLA|W->REGADDR->DATA_W->STOP

            :addr: register address
            :val: register value write
        """
        if isinstance(val, list):
            self.i2cPort.write_to(addr, val)
        else:
            self.i2cPort.write_to(addr, [val])

    # 写字节(选择cmd写，减少delay时间)
    def writeBytes1(self, addr, val):
        """write protocal, START->SLA|W->REGADDR->DATA_W->STOP
        optimize cmd write, decrease delay time
            :addr: register address
            :val: register value write
        """
        if isinstance(val, list):
            self.i2cPort.write_to1(addr, val)
        else:
            self.i2cPort.write_to1(addr, [val])

    # 写位
    def writeBits(self, regparts: str, val):
        """write specified bits

            :regparts: e.g. "0x10[7:6]", 0x10 register bits 7-6
        """
        regparts = re.split('(\[)(.*)(\:)(.*)(\])', regparts)
        addr = int(regparts[0], 16)
        bith = int(regparts[2])
        bitl = int(regparts[4])
        valr = self.readBytes(addr)
        valw = 0
        for i in range(7, -1, -1):
            if bith >= i and i >= bitl:
                valw = valw << 1
            else:
                valw = (valw << 1) | 1
        valw = valr & valw | (val << bitl)
        self.writeBytes(addr, valw)

    # 写位(选择cmd写，减少delay时间)
    def writeBits1(self, regparts: str, val):
        """write specified bits
        optimize cmd write, decrease delay time

            :regparts: e.g. "0x10[7:6]", 0x10 register bits 7-6
        """
        regparts = re.split('(\[)(.*)(\:)(.*)(\])', regparts)
        addr = int(regparts[0], 16)
        bith = int(regparts[2])
        bitl = int(regparts[4])
        valr = self.readBytes1(addr)
        valw = 0
        for i in range(7, -1, -1):
            if bith >= i and i >= bitl:
                valw = valw << 1
            else:
                valw = (valw << 1) | 1
        valw = valr & valw | (val << bitl)
        self.writeBytes1(addr, valw)

    # 读位
    def readBits(self, regparts: str):
        """write specified bits

            :regparts: e.g. "0x10[7:6]", 0x10 register bits 7-6
        """
        regparts = re.split('(\[)(.*)(\:)(.*)(\])', regparts)
        addr = int(regparts[0], 16)
        bith = int(regparts[2])
        bitl = int(regparts[4])
        valr = self.readBytes(addr)
        valtmp = 1
        for i in range(bith):
            valtmp = valtmp << 1 | 1
        return (valr & valtmp) >> bitl

    # 读位(选择cmd写，减少delay时间)
    def readBits1(self, regparts: str):
        """read specified bits
        optimize cmd write, decrease delay time

            :regparts: e.g. "0x10[7:6]", 0x10 register bits 7-6
        """
        regparts = re.split('(\[)(.*)(\:)(.*)(\])', regparts)
        addr = int(regparts[0], 16)
        bith = int(regparts[2])
        bitl = int(regparts[4])
        valr = self.readBytes1(addr)
        valtmp = 1
        for i in range(bith):
            valtmp = valtmp << 1 | 1
        return (valr & valtmp) >> bitl

    # 单个bit读
    def singleRead(self):
        return self.i2cPort.read(1)

    def singleRead1(self):
        return self.i2cPort.read1(1)[-1]

    # 单个bit写
    def singleWrite(self, val):
        self.i2cPort.write(val)

    def singleWrite1(self, val):
        self.i2cPort.write1(val)

    # 设置gpio模式
    def setGpioMode(self, ionum:int, iomode:bool):
        if iomode:
            self.gpioPort.set_direction(1<<ionum, 1<<ionum)
        else:
            self.gpioPort.set_direction(1<<ionum, 0)

    # 写gpio       
    def writeGpio(self, ionum:int, out:bool):
        ret = self.gpioPort.read(with_output=True)
        if out:
            self.gpioPort.write(ret | 1<<ionum)
        else:
            self.gpioPort.write(ret & (~(1<<ionum)))

    # 读gpio
    def readGpio(self, ionum:int):
        ret = self.gpioPort.read(with_output=True)
        return (ret >> ionum) & 0x01


# main函数
if __name__ == "__main__":
    
    ## example
    # a = USB2IIC(sla=0x98)
    # a.writeBytes1(0x4C,0x08)
    # a.readBits1(0x00,1)
    print('SDDD')

    ## for yourself
    
    