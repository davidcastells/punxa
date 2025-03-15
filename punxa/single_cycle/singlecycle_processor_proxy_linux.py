# -*- coding: utf-8 -*-
"""
Created on Mon May 27 05:49:18 2024

@author: dcastel1
"""

from punxa.single_cycle.singlecycle_processor import SingleCycleRISCV
from punxa.csr import *

import os

# Syscalls are listed in
# https://elixir.bootlin.com/linux/latest/source/include/uapi/asm-generic/unistd.h

SYSCALL_DUP = 23
SYSCALL_FCNTL = 25
SYSCALL_IOCTL = 29
SYSCALL_OPENAT = 56
SYSCALL_CLOSE = 57
SYSCALL_READ = 63
SYSCALL_WRITE = 64
SYSCALL_READLINKAT = 78
SYSCALL_FSTAT = 80
SYSCALL_EXIT = 93
SYSCALL_EXIT_GROUP = 94
SYSCALL_SET_TID_ADDRESS = 96
SYSCALL_SET_ROBUST_LIST = 99
SYSCALL_FUTEX = 98
SYSCALL_CLOCK_GET_TIME = 113
SYSCALL_BRK = 214
SYSCALL_MPROTECT = 226
SYSCALL_PRLIMIT64 = 261
SYSCALL_GETRANDOM = 278
SYSCALL_OPEN = 1024

O_WRONLY = 0x001
O_CREAT =  0x100

FUTEX_PRIVATE_FLAG = 128
FUTEX_WAIT = 0
FUTEX_WAIT_PRIVATE = FUTEX_PRIVATE_FLAG | FUTEX_WAIT

        
class SingleCycleRISCVProxyLinux(SingleCycleRISCV):
    
    def __init__(self, parent, name:str, memory, 
                 int_soft_machine, int_timer_machine, ext_int_targets, resetAddress):

        super().__init__( parent, name, memory, int_soft_machine, 
                         int_timer_machine, ext_int_targets, resetAddress)

        self.behavioural_memory = None
        self.console = [''] 
        self.open_files = {}
        
        self.open_files[1] = None
        
        setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_FS_POS, 2, 3)
        
        self.csr[CSR_PRIVLEVEL] = CSR_PRIVLEVEL_USER
        self.pr = print
        
        self.tid = 0x100

    def readMemoryStringz(self, add):
        ret = ''
        while (True):
            c = self.behavioural_memory.readByte(add)
            if (c == 0): return ret;
            ret += chr(c)
            add += 1

    def executeIIns(self):
        op = self.decoded_ins

        if (op == 'ECALL'): 
            syscall = self.reg[17]
            
            print('[SYSCALL] ', end='')
            
            if (syscall == SYSCALL_FSTAT):
                self.syscall_stat()
            elif (syscall == SYSCALL_IOCTL):
                self.syscall_ioctl()
            elif (syscall == SYSCALL_BRK):
                self.syscall_brk()
            elif (syscall == SYSCALL_READ):
                self.syscall_read()
            elif (syscall == SYSCALL_WRITE):
                self.syscall_write()
            elif (syscall == SYSCALL_EXIT):
                self.syscall_exit()
            elif (syscall == SYSCALL_EXIT_GROUP):
                self.syscall_exit_group()
            elif (syscall == SYSCALL_DUP):
                self.syscall_dup()
            elif (syscall == SYSCALL_OPEN):
                self.syscall_open()
            elif (syscall == SYSCALL_OPENAT):
                self.syscall_openat()    
            elif (syscall == SYSCALL_CLOSE):
                self.syscall_close()
                
            elif (syscall == SYSCALL_SET_TID_ADDRESS):
                self.syscall_set_tid_address()
            elif (syscall == SYSCALL_SET_ROBUST_LIST):
                self.syscall_set_robust_list()
                
            elif (syscall == SYSCALL_PRLIMIT64):
                self.syscall_prlimit64()
                
            elif (syscall == SYSCALL_READLINKAT):
                self.syscall_readlinkat()
                
            elif (syscall == SYSCALL_CLOCK_GET_TIME):
                clkid = self.reg[10]
                ts = self.reg[11]
                print(f'CLOCK GET TIME clkid:0x{clkid:X} ts:0x{ts:X}')
                self.reg[10] = 0
            elif (syscall == SYSCALL_MPROTECT):
                self.syscall_mprotect()

            elif (syscall == SYSCALL_FUTEX):
                self.syscall_futex()
                
            elif (syscall == SYSCALL_GETRANDOM):
                self.syscall_getrandom()
            else:
                self.syscall_unknown()
                
        else:
            yield from super().executeIIns()
            
    
    def syscall_dup(self):
        oldfd = self.reg[10]
        newfd = self.reg[11]
        flags = self.reg[12]
        
        print(f'DUP oldfd:{oldfd} newfd:{newfd} flags:0x{flags:X}')
        
        self.reg[10] = 0
        
    def syscall_brk(self):
        heap_end = self.heap_base + self.heap_size
        ptr = self.reg[10]
        if (ptr == 0):
            self.reg[10] = self.heap_base + self.heap_size
        else:
            newsize = ptr - self.heap_base
            if (newsize > self.heap_size):
                self.pr(f'Extending heap to size 0x{newsize:X}')
                self.heap_size = newsize
            else:
                self.pr('new size is smaller than previous one')
            self.reg[10] = self.heap_base + self.heap_size
	
        print(f'BRK ptr:0x{heap_end:X} -> brk:0x{self.reg[10]:X}')

        self.behavioural_memory.reallocArea(self.heap_base, self.heap_size, verbose=False)

    def syscall_mprotect(self):
        add = self.reg[10]
        buflen = self.reg[11]
        prot = self.reg[12]
        print(f'MPROTECT add:0x{add:X} len:{buflen} prot:0x{prot:X}')
        self.reg[10] = 0

    def syscall_readlinkat(self):
        dirfd = self.reg[10]
        path = self.readMemoryStringz(self.reg[11])
        buf = self.reg[12]
        bufsize = self.reg[13]
        
        print(f'READLINKAT dirfd:0x{dirfd:X} path:{path} buf:0x{buf:X} busize:{bufsize}')
        self.reg[10] = 0


    def syscall_prlimit64(self):
        resource = self.reg[10]
        rlimit = self.reg[11]
        print(f'PRLIMIT64 resource:0x{resource:X} rlimit:0x{rlimit:X}')
        self.reg[10] = 0    
        
    def syscall_set_robust_list(self):
        head = self.reg[10]
        listlen = self.reg[11]
        
        print(f'SET ROBUST LIST ADDRESS head:0x{head:X} len:{listlen}')
        self.reg[10] = 0
        
        
    def syscall_set_tid_address(self):
        tid = self.reg[10]
        print(f'SET TID ADDRESS fd:0x{tid:X}')
        self.reg[10] = self.tid
        
    def syscall_getrandom(self):
        buf = self.reg[10]
        buflen = self.reg[11]
        flags = self.reg[12]
        print(f'GETRANDOM buf:0x{buf:X} buflen:{buflen} flags:0x{flags:X}')
        self.reg[10] = buflen
        
    def syscall_futex(self):
        user_address = self.reg[10]
        op = self.reg[11]
        v = self.reg[12]
        timeout = self.reg[13]
        user_address2 = self.reg[14]
        
        print(f'FUTEX user address:0x{user_address:X} op:{op} val:{v} timeout:0x{timeout:X} address2:0x{user_address2:X}')
        
        #if (op == FUTEX_WAIT_PRIVATE):
        #    print('Should wait')
        self.reg[10] = 0
        
    def syscall_unknown(self):
        print('Unnkown syscall', self.reg[17])
        
    def syscall_write(self):
        fd = self.reg[10]
        buf = self.reg[11]
        count = self.reg[12]

        print(f'WRITE fd:0x{fd:X} buf:0x{buf:X} count:0x{count:X}')


        if (fd == 1): f = None
        else: f = self.open_files[fd]
        
        for i in range(count):
            b = self.behavioural_memory.readByte(buf+i)
            
            if (f is None): self.addConsoleChar(chr(b))
            else: 
                b = bytes([b])
                # print('w bytes', b)
                f.write(b)

        self.reg[10] = count
                        
        
        

            

    
    def syscall_read(self):
        fd = self.reg[10]
        buf = self.reg[11]
        count = self.reg[12]
        print(f'READ fd:0x{fd:X} buf:0x{buf:X} count:0x{count:X}')                
    
        f = self.open_files[fd]
        
        for i in range(count):
            b = f.read(1)

            if (len(b) == 0):
                self.reg[10] = i
                return 
                
            if (isinstance(b, str)):
                b = ord(b)
            elif (isinstance(b, bytes)):
                b = int.from_bytes(b, byteorder='little')
            
            self.behavioural_memory.writeByte(buf+i, b)
            
        self.reg[10] = count
            
            
    def syscall_openat(self):
        dirfd = self.reg[10]
        filename = self.readMemoryStringz(self.reg[11])
        flags = self.reg[12]
        mode = self.reg[13]
        print(f'OPENAT dirfd:{dirfd} {filename} f:0x{flags:X} m:0x{mode:X}')
        
        
        if (flags == 0x0 and mode ==0x0):
            py_mode = 'r'
        elif (flags == 0x241 and mode ==0x1b6):
            py_mode = 'wb'
        elif (flags == 0x601 and mode ==0x1b6):
            py_mode = 'wb'
        elif (flags == 0x0 and mode == 0x1B6):
            py_mode = 'rb'
        else:
            print(f'Unknown flags/mode 0x{flags:X}/0x{mode:X}')
            self.parent.getSimulator().stop()
            return -1

        file = open(filename, py_mode)
        self.open_files[file.fileno()] = file
        self.reg[10] = file.fileno()
        print(f'  fileno() = {self.reg[10]}')
    

    def syscall_open(self):
        filename = self.readMemoryStringz(self.reg[10])
        flags = self.reg[11]
        mode = self.reg[12]
        print(f'OPEN {filename} f:0x{flags:X} m:0x{mode:X}')
        
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
        self.reg[10] = file.fileno()
    
        
    def syscall_close(self):
        fd = self.reg[10]
        print(f'CLOSE fd:0x{fd:X}')
        
        if not(fd in self.open_files.keys()):
            print(f'WARNING! syscall stat on unknown file number: {fd}')
            return -1

        f = self.open_files.pop(fd)
        f.close()  
        self.reg[10] = 0  

    def syscall_ioctl(self):
        fd = self.reg[10]
        p1 = self.reg[11]
        p2 = self.reg[12]
        print(f'IOCTL fd:0x{fd:X} p1:{p1} p2:{p2}')
        self.reg[10] = 0  

        
    def syscall_stat(self):
        fd = self.reg[10]
        stat_ptr = self.reg[11]
        print(f'FSTAT fd:0x{fd:X} stat:0x{stat_ptr:X}')
                

        if not(fd in self.open_files.keys()):
            print(f'WARNING! syscall stat on unknown file number: {fd}')
            return -1
        else:
            file_stat = os.stat(fd)

        if (fd == 1):
            file_rdev = 0x00880001
        else:
            file_rdev = 0
                
        for i in range(128):
            self.behavioural_memory.writeByte(stat_ptr+i, 0)
            
        self.behavioural_memory.write_i32(stat_ptr+16, file_stat.st_mode)
        self.behavioural_memory.write_i32(stat_ptr+32, file_rdev)
        self.behavioural_memory.write_i64(stat_ptr+40, file_stat.st_size)
        
        #self.behavioural_memory.writei64( file_stat.st_size

        self.reg[10] = 0        

    def syscall_exit(self):
        print('EXIT')
        self.parent.getSimulator().stop()

    def syscall_exit_group(self):
        print('EXIT GROUP')
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


    def pushString(self, s):
        # stack pointer points to the last used position
        towrite = (len(s)+1)            # count the final zero
        towrite = ((towrite + 3)//4)*4  # align to 32 bits

        start = self.reg[2] - towrite
        
        for k in range(len(s)):
            self.behavioural_memory.writeByte(start+k, ord(s[k]))

        for k in range(len(s), towrite):
            self.behavioural_memory.writeByte(start+k, 0) # fill with zeros
            
    
    def pushInt64(self, v):
        for k in range(8):
            self.behavioural_memory.writeByte(self.reg[2], (v >> 56) & 0xFF)
            v = v << 8
            
        self.reg[2] -= 8
    
    def pushInt32(self, v):
        # stack should be aligned to 64 bits
        for k in range(4):
            self.behavioural_memory.writeByte(self.reg[2], (v >> 24) & 0xFF)
            v = v << 8

        self.reg[2] -= 8
