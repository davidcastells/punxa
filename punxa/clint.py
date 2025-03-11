# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 18:56:57 2022

@author: dcr
"""

import py4hw
from py4hw.logic import *
from py4hw.logic.storage import *
from py4hw.simulation import Simulator
import py4hw.debug

# @todo should be part of py4hw
def get_bit(v, bit):
    return ((v>>bit) & 0x1)

# @todo should be part of py4hw
def signExtend(v, w):
    sign_bit = w - 1

    if (get_bit(v, sign_bit) == 0x1):
        v = - ((1<<w) - v)

    return v


class CLINT(Logic):
    """
    Inspired by
    https://chromitem-soc.readthedocs.io/en/latest/clint.html
    https://osblog.stephenmarz.com/ch5.html
    
    
    Memory map
    offset
    0x0000  u32     msip , machine software interrupts 
    0x4000  u64     mtimecmp, machine time compare value (low). when mtime reaches this value it issues an interrupt
    0xBFF8  u64     mtime, value of the time
    
    """
    def __init__(self, parent:Logic, name:str, port, int_soft, int_timer):
        super().__init__(parent, name)
        
        self.port = self.addInterfaceSink('port', port)
        
        self.int_soft = self.addOut('int_soft', int_soft)
        self.int_timer = self.addOut('int_timer', int_timer)
        
        self.mtimecmp = (1<<64)-1
        self.mtime = 0
        self.msip = 0

    def clock(self):
        if (self.msip & 1):
            if (self.int_soft.get() == 0):
                # only print debug messages at the positive edge
                print('WARNING: CLINT Software interrupt')
            self.int_soft.prepare(1)
        else:
            self.int_soft.prepare(0)
        
        if (self.mtimecmp < self.mtime):            
            if (self.int_timer.get() == 0):
                # only print debug messages at the positive edge
                print('WARNING: CLINT Timer interrupt {:016X} < {:016X}'.format(self.mtimecmp, self.mtime))
            self.int_timer.prepare(1)

        else:
            self.int_timer.prepare(0)

        self.mtime += 1
        
        if ((self.port.read.get() == 0) and (self.port.write.get() == 0)):
            return

        be = self.port.be.get()
        

        address = self.port.address.get()
        field = ''
        write_data = self.port.write_data.get()
        read_data = 0
        read = self.port.read.get() 
        write = self.port.write.get() 
        
        if (address == 0 ):
            field = 'msip'
        elif (address == 0x4000):
            field = 'mtimecmp'            
        elif (address == 0x4004):
            field = 'mtimecmph'
        elif (address == 0xBFF8):
            field = 'mtime'
        elif (address == 0xBFFC):
            field = 'mtimeh'
        else:
            field = 'unknown {:016X}'.format(address)

        if (self.port.read.get() == 1):
            
            if (field == 'mtime'):
                read_data = self.mtime 
            elif (field == 'mtimecmp'):
                read_data = self.mtimecmp 
            elif (field == 'mtimecmph'):
                read_data = (self.mtimecmp >> 32) & ((1<<32)-1)
                
            print('WARNING: CLINT read transaction to {} = {:016X}'.format(field, read_data))
            self.port.read_data.prepare(read_data)
            #self.parent.getSimulator().stop()
            
        if (self.port.write.get() == 1):
            
            if (field == 'msip'):
                self.msip = write_data & 1
            elif (field == 'mtimecmp'):
                if (be == 0xFF):
                    self.mtimecmp = write_data 
                elif (be == 0xF):
                    self.mtimecmp = (self.mtimecmp & (((1<<32)-1) << 32)) | (write_data & ((1<<32)-1))
                else:
                    print(f'WARNING: writing {field} with unknown be {be:02X} ')
            elif (field == 'mtimecmph'):
                if (be == 0xFF):
                    print(f'ERROR: writing {field} with invalid be {be:02X} ')
                elif (be == 0xF):
                    self.mtimecmp = (write_data << 32) | (self.mtimecmp & ((1<<32)-1))
                else:
                    print(f'WARNING: writing {field} with unknown be {be:02X} ')
            elif (field == 'mtime'):
                if (be == 0xFF):
                    self.mtime = write_data 
                elif (be == 0xF):
                    self.mtime = (self.mtime & (((1<<32)-1) << 32)) | (write_data & ((1<<32)-1))
                else:
                    print(f'WARNING: writing {field} with unknown be {be:02X} ')
            elif (field == 'mtimeh'):
                if (be == 0xFF):
                    #self.mtime = write_data 
                    print(f'ERROR: writing {field} with invalid be {be:02X} ')
                elif (be == 0xF):
                    self.mtime = (write_data << 32) | (self.mtime & ((1<<32)-1))
                else:
                    print(f'WARNING: writing {field} with unknown be {be:02X} ')
                
            print('WARNING: CLINT write transaction to {} = {:016X}'.format(field, write_data))
            #self.parent.getSimulator().stop()
            
