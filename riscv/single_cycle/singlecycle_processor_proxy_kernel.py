# -*- coding: utf-8 -*-
"""
Created on Mon May 27 05:49:18 2024

@author: dcastel1
"""

from riscv.single_cycle.singlecycle_processor import SingleCycleRISCV

SYSCALL_OPENAT = 56
SYSCALL_CLOSE = 57
SYSCALL_READ = 63
SYSCALL_WRITE = 64
SYSCALL_FSTAT = 80
SYSCALL_EXIT = 93
SYSCALL_BRK = 214

class SingleCycleRISCVProxyKernel(SingleCycleRISCV):
    
    def __init__(self, parent, name:str, memory, 
                 int_soft_machine, int_timer_machine, ext_int_targets, resetAddress):

        super().__init__( parent, name, memory, int_soft_machine, 
                         int_timer_machine, ext_int_targets, resetAddress)

        self.behavioural_memory = None
        self.console = ['']        

    def executeIIns(self):
        op = self.decoded_ins

        if (op == 'ECALL'):            
            syscall = self.reg[17]
            
            if (syscall == SYSCALL_FSTAT):
                fd = self.reg[10]
                stat = self.reg[11]
                print(f'FSTAT fd:0x{fd:X} stat:0x{stat:X}')
                
                self.reg[10] = 0
            elif (syscall == SYSCALL_BRK):
                ptr = self.reg[10]
                print(f'BRK ptr:0x{ptr:X}')
            elif (syscall == SYSCALL_WRITE):
                fd = self.reg[10]
                buf = self.reg[11]
                count = self.reg[12]
                print(f'WRITE fd:0x{fd:X} buf:0x{buf:X} count:0x{count:X}')
                self.syscall_write(buf, count)                
                self.reg[10] = 0
            elif (syscall == SYSCALL_EXIT):
                print('EXIT')
                self.parent.getSimulator().stop()
            else:
                print('my syscall', syscall)
        else:
            yield from super().executeIIns()
            
    def syscall_write(self, buf, count):
        for i in range(count):
            b = self.behavioural_memory.readByte(buf+i)
            self.addConsoleChar(chr(b))
            
    def addConsoleChar(self, c):
        if (c == '\n'):
            clen = len(self.console)
            if (clen > 80):
                self.console = self.console[1:] # remove one line
            self.console.append('')
        else:
            clen = len(self.console)
            self.console[clen-1] += c
