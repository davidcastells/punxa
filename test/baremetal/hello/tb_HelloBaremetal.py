# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:57:50 2024

@author: dcr
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
from punxa.single_cycle.singlecycle_processor import *
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

def buildHw(cpu_model='sc'):
    global memory
    global cpu
    global bus

    hw = HWSystem()

    port_c = MemoryInterface(hw, 'port_c', mem_width, 40)
    port_m = MemoryInterface(hw, 'port_m', mem_width, 20)     # 20	bits = 
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

    if (cpu_model == 'sc'):
        cpu = SingleCycleRISCV(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

    elif (cpu_model == 'up'):
        registerBase = mem_base +  (1 << 20) - 0x10000 # (8 * 8192)

        reset = hw.wire('reset')
        zero = hw.wire('zero')

        py4hw.Constant(hw, 'zero', 0, zero)
        py4hw.Reg(hw, 'auto_reset', zero, reset, reset_value=1)

        cpu = MicroprogrammedRISCVProxyKernel(hw, 'RISCV', reset, port_c, int_soft, int_timer, ext_int_targets, mem_base, registerBase)
                                              
    else:
        raise Exception(f'cpu model {cpu_model} not supported')
        
    cpu.min_clks_for_trace_event = 1000
    cpu.behavioural_memory = memory

    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    punxa.interactive_commands._ci_bus = bus
    
    return hw


def getHw():
    return hw

def getCpu():
    return cpu

def prepare(cpu_model='sc'):
    test_file = 'hello.elf'
    global hw
    hw = buildHw(cpu_model)
    programFile = ex_dir + test_file
    
    loadElf(memory, programFile, 0 ) # 32*4 - 0x10054)    
    loadSymbolsFromElf(cpu,  programFile, mem_base) # 32*4 - 0x10054)

    #start_adr = findFunction('_startup')
    start_adr = getElfEntryPoint(programFile)

    
    stack_base = 0x90000
    stack_size = 0x10000
    
    if (cpu_model == 'sc'):
        cpu.pc = start_adr
        cpu.reg[2] = mem_base + stack_base + stack_size - 8
    elif (cpu_model == 'up'):
        cpu.children['PC'].value = start_adr
        memory.reallocArea(cpu.registerBase , (32+32+32+4096)*8)

        addr_r2 = cpu.registerBase + 2*8
        value = mem_base + stack_base + stack_size - 8
        memory.write_i32(addr_r2, value)
        
    memory.reallocArea(stack_base, stack_size)

    cpu.heap_base = 0xA0000
    cpu.heap_size = 0x20000 

    memory.reallocArea(cpu.heap_base, cpu.heap_size)
    
    print('')
    print(f'\tStack base: 0x{stack_base:016X} size: 0x{stack_size:016X}')
    print(f'\tHeap base:  0x{cpu.heap_base:016X} size: 0x{cpu.heap_size:016X}')


def runTest(test_file):
    prepareTest(test_file)
    exit_adr = findFunction('exit')

    run(exit_adr, maxclks=10000, verbose=False)


def runHello(cpu_model='sc'):
    prepare(cpu_model)
    step(10000)
    print()
    print('Console Output')
    print('-'*80)
    console()

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
