# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 16:04:02 2022

@author: dcr
"""

import py4hw
from py4hw.logic import *
from py4hw.logic.storage import *
from py4hw.simulation import Simulator
import py4hw.debug

class PLIC(Logic):
    """
    For a nice description of the Platform Level Interrupt Controller (PLIC)
    watch this video https://www.youtube.com/watch?v=jK3TLK4CpWk
    
    more details in
    https://github.com/riscv/riscv-plic-spec/blob/master/riscv-plic.adoc
    
    The PLIC Memory Map
    
    offset
    0x000000 u32 interrupt_source_priority[1024]     # the interrupt zero does not exist 
    0x001000 u32 interrupt_pending[1024//32]         # 
    0x002000 u32 interrupt_enable[15872][1024//32]   # interrupt enable for every possible context

    0x200000
    struct
    {
         0x00 u32 priority_threshold for context
         0x04 u32 claim/complete for context 
         0x08 u32 reserved[0x3fe]
    }  context[15872]                               # every context entry uses 0x1000 bytes  
    """

    def __init__(self, parent:Logic, name:str, port, int_sources, int_targets):
        super().__init__(parent, name)
        
        self.port = self.addInterfaceSink('port', port)
        
        self.int_sources = []
        for idx, source in enumerate(int_sources):
            self.int_sources.append(self.addIn('int_source{}'.format(idx), source))
            
        self.int_targets = []
        for idx, target in enumerate(int_targets):
            self.int_targets.append(self.addOut('int_target{}'.format(idx), target))
            
        self.verbose = True

    def clock(self):
        if ((self.port.read.get() == 0) and (self.port.write.get() == 0)):
            return

        be = self.port.be.get()
        address = self.port.address.get()
        field = ''
        write_data = self.port.write_data.get()
        read_data = 0

        if (bin(be).count('1') != 4):
            print('WARNING: plic log2(BE)!=4 : {:02X}'.format(be))
            self.parent.getSimulator().stop()
            return
        
        if (address >= 0 and address < 0x1000):
            field = 'interrupt_source[{}] priority'.format(address//4)
        elif (address >= 0x1000 and address < 0x2000):
            v = address - 0x1000
            field = 'interrupt[{}:{}] pending'.format(v*8, v*8-1)
        elif (address >= 0x2000 and address < 0x200000):
            v = address - 0x2000
            context = v // (1024 // 8)
            interrupt = v % (1024 // 8)
            field = 'interrupt[{}:{}] enable for context[{}]'.format((interrupt+1)*32-1, interrupt*32,  context )
        elif (address >= 0x200000 and address < (0x200000 + 15872 * 0x1000)):
            v = address - 0x200000 
            context = v // 0x1000
            context_field = v % 0x1000
            
            if (context_field == 0x0):
                field = 'priority threshold for context[{}]'.format(context )
            elif (context_field == 0x4):
                field = 'claim/complete for context[{}]'.format(context )                
            else:
                field = 'unknown {:016X}'.format(address)
        else:
            field = 'unknown {:016X}'.format(address)

        if (self.port.read.get() == 1):            
            print('PLIC reading field {} = {:08X}'.format(field, read_data))
            #self.parent.getSimulator().stop()
            
        if (self.port.write.get() == 1):
            print('PLIC writing field {} = {:08X}'.format(field, write_data))
            #self.parent.getSimulator().stop()
