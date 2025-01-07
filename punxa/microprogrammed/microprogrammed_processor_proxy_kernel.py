# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 19:44:39 2025

@author: dcr
"""

from punxa.microprogrammed.microprogrammed_processor import MicroprogrammedRISCV

import os
from types import MethodType

# Proxy Kernel Syscalls are listed in
# https://github.com/riscv-software-src/riscv-pk/blob/master/pk/syscall.h

SYSCALL_OPENAT = 56
SYSCALL_CLOSE = 57
SYSCALL_READ = 63
SYSCALL_WRITE = 64
SYSCALL_FSTAT = 80
SYSCALL_EXIT = 93
SYSCALL_BRK = 214
SYSCALL_OPEN = 1024

O_WRONLY = 0x001
O_CREAT =  0x100

def proxy_kernel_control_unit_executeIIns(self):
    op = self.decoded_ins

    if (op == 'ECALL'): 
        syscall = self.parent.getReg(17)
        
        if (syscall == SYSCALL_FSTAT):
            fd = self.parent.getReg(10)
            stat_ptr = self.parent.getReg(11)
            print(f'FSTAT fd:0x{fd:X} stat:0x{stat_ptr:X}')
            
            self.parent.setReg(10, self.parent.syscall_stat(fd, stat_ptr))
        elif (syscall == SYSCALL_BRK):
            ptr = self.parent.getReg(10)
            if (ptr == 0):
                self.parent.setReg(10, self.parent.heap_base + self.parent.heap_size)
            else:
                newsize = ptr - self.parent.heap_base
                if (newsize > self.parent.heap_size):
                    print(f'Extending heap to size 0x{newsize:X}')
                    self.parent.heap_size = newsize
                else:
                    print('new size is smaller than previous one')
                self.parent.setReg(10, self.parent.heap_base + self.parent.heap_size)
	
            newptr = self.parent.getReg(10)
            print(f'BRK ptr:0x{ptr:X} -> brk:0x{newptr:X}')

            self.parent.behavioural_memory.reallocArea(self.parent.heap_base, self.parent.heap_size)

        elif (syscall == SYSCALL_READ):
            fd = self.parent.getReg(10)
            buf = self.parent.getReg(11)
            count = self.parent.getReg(12)
            print(f'READ fd:0x{fd:X} buf:0x{buf:X} count:0x{count:X}')                
            self.parent.setReg(10, self.parent.syscall_read(fd, buf, count))
        elif (syscall == SYSCALL_WRITE):
            fd = self.parent.getReg(10)
            buf = self.parent.getReg(11)
            count = self.parent.getReg(12)
            print(f'WRITE fd:0x{fd:X} buf:0x{buf:X} count:0x{count:X}')
            self.parent.syscall_write(fd, buf, count)                
            self.parent.setReg(10, 0)
        elif (syscall == SYSCALL_EXIT):
            print('EXIT')
            self.parent.syscall_exit()
        elif (syscall == SYSCALL_OPEN):
            ptr = self.parent.getReg(10)
            filename = self.readMemoryStringz(ptr)
            flags = self.parent.getReg(11)
            mode = self.parent.getReg(12)
            print(f'OPEN {filename} f:0x{flags:X} m:0x{mode:X}')
            self.parent.setReg(10, self.parent.syscall_open(filename, flags, mode))
        elif (syscall == SYSCALL_CLOSE):
            fd = self.parent.getReg(10)
            print(f'CLOSE fd:0x{fd:X}')
            self.parent.setReg(10, self.parent.syscall_close(fd))
        else:
            self.parent.syscall_unknown()
            
    else:
        yield from self.old_executeIIns()

class MicroprogrammedRISCVProxyKernel(MicroprogrammedRISCV):
    
    def __init__(self, parent, name:str, reset, memory, 
                 int_soft_machine, int_timer_machine, ext_int_targets, resetAddress, registerBase):

        super().__init__( parent, name, reset, memory, int_soft_machine, 
                         int_timer_machine, ext_int_targets, resetAddress, registerBase)

        self.behavioural_memory = None
        self.console = [''] 
        self.open_files = {}
        
        CU = self.children['CU']
        
        CU.old_executeIIns = CU.executeIIns
        CU.executeIIns = MethodType(proxy_kernel_control_unit_executeIIns, CU)

    def readMemoryStringz(self, add):
        ret = ''
        while (True):
            c = self.behavioural_memory.readByte(add)
            if (c == 0): return ret;
            ret += chr(c)
            add += 1

            
    def syscall_unknown(self):
        print('Unnkown syscall', self.reg[17])
        
    def syscall_write(self, fd, buf, count):
        if (fd == 1): f = None
        else: f = self.open_files[fd]
        
        for i in range(count):
            b = self.behavioural_memory.readByte(buf+i)
            
            if (f is None): self.addConsoleChar(chr(b))
            else: 
                b = bytes([b])
                # print('w bytes', b)
                f.write(b)
                        
    def syscall_read(self, fd, buf, count):
        f = self.open_files[fd]
        
        for i in range(count):
            b = f.read(1)

            if (len(b) == 0):
                return i
                
            if (isinstance(b, str)):
                b = ord(b)
            elif (isinstance(b, bytes)):
                b = int.from_bytes(b, byteorder='little')
            
            self.behavioural_memory.writeByte(buf+i, b)
            
    def syscall_open(self, filename, flags, mode):
        if (flags == 0x601 and mode ==0x1b6):
            py_mode = 'wb'
        elif (flags == 0x0 and mode == 0x1B6):
            py_mode = 'rb'
        else:
            print(f'Unknown flags/mode 0x{flags:X}/0x{mode:X}')
            self.parent.getSimulator().stop()
            return -1

        file = open(filename, py_mode)
        self.open_files[file.fileno()] = file
        return file.fileno()
        
    def syscall_close(self, fd):
        if not(fd in self.open_files.keys()):
            print(f'WARNING! syscall stat on unknown file number: {fd}')
            return -1

        f = self.open_files.pop(fd)
        f.close()  
        return 0  
        
    def syscall_stat(self, fd, stat_ptr):
        if not(fd in self.open_files.keys()):
            print(f'WARNING! syscall stat on unknown file number: {fd}')
            return -1
        
        file_stat = os.stat(fd)
        
        for i in range(100):
            self.behavioural_memory.writeByte(stat_ptr+i, i)
            
        self.behavioural_memory.write_i64(stat_ptr+0x30, file_stat.st_size)
        
        #self.behavioural_memory.writei64( file_stat.st_size
    
        return 0        

    def syscall_exit(self):
        self.parent.getSimulator().stop()

    def addConsoleChar(self, c):
        if (c == '\n'):
            clen = len(self.console)
            if (clen > 80):
                self.console = self.console[1:] # remove one line
            self.console.append('')
        else:
            clen = len(self.console)
            self.console[clen-1] += c
