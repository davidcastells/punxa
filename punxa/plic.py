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
    0x001000 u32 interrupt_pending[1024//32]         # interrupt pending is independent of context
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
        self.int_source_priority = []
        for idx, source in enumerate(int_sources):
            self.int_sources.append(self.addIn('int_source{}'.format(idx), source))
            self.int_source_priority.append(0)
            
        self.int_targets = []
        self.int_context_priority_th = []
        for idx, target in enumerate(int_targets):
            self.int_targets.append(self.addOut('int_target{}'.format(idx), target))
            self.int_context_priority_th.append(0)
            
        nsources = len(self.int_sources)
        ntargets = len(self.int_targets)
        
        self.ie = [[0 for _ in range(nsources)] for _ in range(ntargets)]
        self.ip = [0 for _ in range(nsources)] 
        
        self.verbose = True

    def clock(self):
        # Check for interrupts
        for tidx, target in enumerate(self.int_targets):
            priority_th = self.int_context_priority_th[tidx]
            tval = 0
            for sidx, source in enumerate(self.int_sources):
                priority = self.int_source_priority[sidx]
                
                if (source.get() and self.ie[tidx][sidx] and priority > priority_th):
                    tval = 1

                self.ip[sidx] = source.get()
                    
                 
            target.prepare(tval)

        # Registers
        if ((self.port.read.get() == 0) and (self.port.write.get() == 0)):
            return

        be = self.port.be.get()
        address = self.port.address.get()
        field = ''
        write_data = self.port.write_data.get()
        write = self.port.write.get()
        read = self.port.read.get()
        read_data = 0
        
            

        if (bin(be).count('1') != 4):
            print('WARNING: plic log2(BE)!=4 : {:02X}'.format(be))
            self.parent.getSimulator().stop()
            return
        
        if (address >= 0 and address < 0x1000):
            source = address//4
            field = 'interrupt_source[{}] priority'.format(source)
            
            if (write):
                if (source < len(self.int_source_priority)):
                    self.int_source_priority[source] = write_data
                
        elif (address >= 0x1000 and address < 0x2000):
            v = address - 0x1000
            interrupt = v // 8
            interrupt_start = interrupt*32
            interrupt_end = min((interrupt+1)*32, len(self.int_sources))
            
            field = 'interrupt[{}:{}] pending'.format(interrupt_end, interrupt_start)
            
            if (read):
                val = 0
                for i in range(interrupt_start, interrupt_end):
                    val = val | (self.ip[i] << i)  
                read_data = val
                
        elif (address >= 0x2000 and address < 0x200000):
            v = address - 0x2000
            context = v // (1024 // 8)
            interrupt = v % (1024 // 8)
            field = 'interrupt[{}:{}] enable for context[{}]'.format((interrupt+1)*32-1, interrupt*32,  context )
            
            if (write):
                base_int = interrupt*32
                vie = write_data
                #print('write_data', hex(write_data))
                
                for i in range(32):
                    if ((base_int + i) < len(self.int_sources)):
                        self.ie[context][base_int +i] = (vie & 1)
                        #print(f'interrupt enable {base_int+i} = {vie & 1}')
                        
                    vie = vie >> 1
            if (read):
                base_int = interrupt*32
                read_data = 0
                for i in range(32):
                    if ((base_int + i) < len(self.int_sources)):
                        read_data = read_data | (self.ie[context][base_int +i] << i)
                
                        
                    
        elif (address >= 0x200000 and address < (0x200000 + 15872 * 0x1000)):
            v = address - 0x200000 
            context = v // 0x1000
            context_field = v % 0x1000
            
            if (context_field == 0x0):
                field = 'priority threshold for context[{}]'.format(context )
                
                if (write):
                    self.int_context_priority_th[context] = write_data
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
            
        self.port.read_data.prepare(read_data)
