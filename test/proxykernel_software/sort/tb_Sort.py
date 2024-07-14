# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:57:50 2024

@author: dcastel1
"""


import sys
import os

baseDir = '../../../'

mem_width = 64

if not(baseDir in sys.path):
    print('appending .. to path')
    sys.path.append(baseDir)

ex_dir = ''


from punxa.memory import *
from punxa.bus import *
from punxa.uart import *
from punxa.clint import *
from punxa.plic import *
from punxa.single_cycle.singlecycle_processor_proxy_kernel import *
from punxa.instruction_decode import *
from punxa.interactive_commands import *
    

import py4hw    
import py4hw.debug
import py4hw.gui as gui
import zlib


mem_base =  0x00000000
#test_base = 0x80001000

    
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


    


def checkpoint(filename=ex_dir + 'checkpoint.dat'):
    import shutil
    from serialize import Serializer 
    
    if (os.path.exists(filename)):
        shutil.copyfile(filename, filename+'.bak')
        
    ser = Serializer(filename)

    # Serialize CPU info
    ser.write_i64(cpu.pc)    
    
    for i in range(32):
        ser.write_i64(cpu.reg[i])
    for i in range(32):
        ser.write_i64(cpu.freg[i])
    for i in range(4096):
        ser.write_i64(cpu.csr[i])

    ser.write_int_pair_list(cpu.stack)
    
    # Serialize Memory Info
    ser.write_i64(len(memory.area))
    for mem in memory.area:        
        offset = mem[0]
        size = mem[1]
        data = mem[2]
        zmem = zlib.compress(data)
        ser.write_i64(offset)
        ser.write_i64(size)
        ser.write_i64(len(zmem))
        ser.write_bytearray(zmem)
        
    # Serialize UART Info
    ser.write_string_list(uart.console)
    
    
    # Serialize pending tracing (comple tracing is discarded)
    ser.write_dictionary(cpu.tracer.pending)
    
    ser.close()

def restore(filename=ex_dir + 'checkpoint.dat'):
    from serialize import Deserializer 
    
    ser = Deserializer(filename)
    
    # Deserialize CPU info
    cpu.pc = ser.read_i64()
    
    for i in range(32):
        cpu.reg[i] = ser.read_i64()
    for i in range(32):
        cpu.freg[i] = ser.read_i64()
    for i in range(4096):
        cpu.csr[i] = ser.read_i64()

    cpu.stack = ser.read_int_pair_list()

    # Deserialize Memory Info
    memory.area = []
    num_area = ser.read_i64()
    for i in range(num_area):        
        offset = ser.read_i64()
        size = ser.read_i64()
        csize = ser.read_i64()
        zmem = ser.read_bytearray(csize)
        
        mem = zlib.decompress(zmem)
        
        memory.area.append((offset, size, bytearray(mem)))

    # Deserialize UART info
    uart.console = ser.read_string_list()
    
    # Deerialize pending tracing (comple tracing is discarded)
    cpu.tracer.pending = ser.read_dictionary()
            
    ser.close()

                
def reallocMem(add, size):
    memory.reallocArea(add - mem_base, size)
    

#  +-----+    +-----+     +-----+
#  | CPU |--C-| bus |--M--| mem |
#  +-----+    |     |     +-----+
#             |     |     +------+
#             |     |--U--| uart |
#             |     |     +------+
#             |     |     +------+
#             |     |--P--| PLIC |
#             |     |     +------+
#             |     |     +-------+
#             |     |--L--| CLINT |
#             |     |     +-------+
#             +-----+
#  | start          | stop           | device        |
#  | 0000 0000 0000 | 0001 BFEF FFFF | memory (5GB)  |
#  | 0000 BFF0 0000 | 0002 8000 0000 | pmem (3GB)    |
#  | 00FF F0C2 C000 | 00FF F0C2 CFFF | uart          |
#  | 00FF F102 0000 | 00FF F102 FFFF | CLINT         |
#  | 00FF F110 0000 | 00FF F11F FFFF | PLIC          |

def buildHw():
    global memory
    global cpu
    global bus

    hw = HWSystem()

    port_c = MemoryInterface(hw, 'port_c', mem_width, 40)
    port_m = MemoryInterface(hw, 'port_m', mem_width, 24)     # 22	bits = 
    port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
    port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
    port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
    #port_t = MemoryInterface(hw, 'port_t', mem_width, 8)     # 8 bits = 256
    # Memory initialization

    memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

    #memory.reallocArea(0, 1 << 16)

    #test = ISATestCommunication(hw, 'test', mem_width, 8, port_t)


    # Uart initialization
    uart = Uart(hw, 'uart', port_u)


    int_soft = hw.wire('int_soft')
    int_timer = hw.wire('int_timer')

    ext_int_sources = []
    ext_int_sources.append(hw.wire('ext_int_0'))
    ext_int_sources.append(hw.wire('ext_int_1'))
    Constant(hw, 'ext_int_0', 0, ext_int_sources[0])
    Constant(hw, 'ext_int_1', 0, ext_int_sources[1])

    ext_int_targets = []
    ext_int_targets.append(hw.wire('int_machine'))
    ext_int_targets.append(hw.wire('int_supervisor'))

    # CLINT initialization
    clint = CLINT(hw, 'clint', port_l, int_soft, int_timer)

    # PLIC initialization
    plic = PLIC(hw, 'plic', port_p, ext_int_sources, ext_int_targets)

    bus = MultiplexedBus(hw, 'bus', port_c, [(port_m, mem_base),
                                          #(port_t, test_base),
                                          #(port_d, 0x01BFF00000),
                                          (port_u, 0xFFF0C2C000),
                                          (port_p, 0xFFF1100000),
                                          (port_l, 0xFFF1020000)])

    cpu = SingleCycleRISCVProxyKernel(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

    cpu.min_clks_for_trace_event = 1000
    cpu.behavioural_memory = memory

    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    
    return hw

def pushString(s):
    memory.writeByte(cpu.reg[2], 0)
    cpu.reg[2] -= 1
    for k in range(len(s)):
        memory.writeByte(cpu.reg[2], ord(s[len(s)-1-k]) )
        cpu.reg[2] -= 1

def pushInt64(v):
    for k in range(8):
        memory.writeByte(cpu.reg[2], (v >> 56) & 0xFF)
        cpu.reg[2] -= 1
        v = v << 8

def pushInt32(v):
    for k in range(4):
        memory.writeByte(cpu.reg[2], (v >> 24) & 0xFF)
        cpu.reg[2] -= 1
        v = v << 8

def prepareTest(test_file, args):
    global hw
    hw = buildHw()
    programFile = ex_dir + test_file
    

    memory.reallocArea(0x10000, 0x80000)

    loadElf(memory, programFile, 0 )     
    loadSymbolsFromElf(cpu,  programFile, mem_base) 


    start_adr = findFunction('_start')

    cpu.pc = start_adr
    
    stack_base = 0x90000
    stack_size = 0X50000
    cpu.reg[2] = mem_base + stack_base + stack_size - 8

    memory.reallocArea(stack_base, stack_size)

    cpu.heap_base = 0x100000
    cpu.heap_size = 0x040000 

    memory.reallocArea(cpu.heap_base, cpu.heap_size)
    
    print('')
    print(f'\tStack base: 0x{stack_base:016X} size: 0x{stack_size:016X}')
    print(f'\tHeap base:  0x{cpu.heap_base:016X} size: 0x{cpu.heap_size:016X}')

    # Now push the arguments to the stack
    args = [programFile] + args
    argc = len(args)
    argsp = [0] * argc

    for i in range(argc):
        param = args[argc-1-i]
        pushString(param)
        argsp[i] = cpu.reg[2] + 1

    pushInt64(0)

    for i in range(argc):
        add = argsp[i]
        pushInt64(add)

    pushInt64(argc)

    cpu.reg[2] += 1
    

def runTest():
    prepareTest('sort.elf', [])
    exit_adr = findFunction('exit')

    run(0, maxclks=89800, verbose=True)
    #run(passAdr, verbose=False)
    #run(exit_adr, maxclks=100000, verbose=True)
    #run(0, maxclks=20, verbose=False)

    # print('Test', test_file, end='')

    #if (cpu.pc != passAdr):
    #value = memory.readByte(tohost_adr-mem_base)
    
    #if (value != 1):
    #    raise Exception('Test return value = {}'.format(value))
    #else:
    #    print('Test return value = {}'.format(value))


def prepare():
    prepareTest('sort.elf', ['-v' ])
    #step(10000000)
    #print()
    #print('Console Output')
    #print('-'*80)
    #console()

if __name__ == "__main__":
    print(sys.argv)

    if (len(sys.argv) > 1):
         if (sys.argv[1] == '-c'):
             eval(sys.argv[2])
             os._exit(0)
         elif (sys.argv[1] == '-trace'):
             cpu.min_clks_for_trace_event=5000

             for i in range(10*60//2):
                 # 120 minutes // 2
                 #run(0xffffffe00060074c, maxclks=10000000000, verbose=False)
                 run(0, maxclks=50000*60*2, verbose=False) # run simulation for 2 minutesº
                 write_trace() 
                 checkpoint()
