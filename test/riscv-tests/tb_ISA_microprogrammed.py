# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 09:27:23 2024

@author: 2016570
"""


import sys
import os

baseDir = '../..'

mem_width = 64

if not(baseDir in sys.path):
    print('appending .. to path')
    sys.path.append(baseDir)

ex_dir = 'isa/'

if not(os.path.exists(ex_dir)):
    raise Exception('ISA tests not found')

from punxa.memory import *
from punxa.bus import *
from punxa.uart import *
from punxa.clint import *
from punxa.plic import *
from punxa.microprogrammed.microprogrammed_processor import *
from punxa.instruction_decode import *
from punxa.interactive_commands import *

import py4hw    
import py4hw.debug
import py4hw.gui as gui
import zlib

mem_base =  0x80000000
test_base = 0x80001000

    
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


    
from elftools.elf.elffile import ELFFile



def write_trace(filename=ex_dir + 'newtrace.json'):
    cpu.tracer.write_json(filename)


                  

def memoryMap():
    for i in range(len(bus.start)):
        size = bus.stop[i] - bus.start[i]
        units = 'B'
        if (size > 1024):
            size = size/1024
            units = 'KiB'
        if (size > 1024):
            size = size/1024
            units = 'MiB'
        if (size > 1024):
            size = size/1024
            units = 'GiB'
        
        print('* {:016X} - {:016X} {:.0f} {}'.format(bus.start[i], bus.stop[i], size, units))
        
        if (bus.start[i] == mem_base):
            # details on memory
            for block in memory.area:
                size = block[1]
                units = 'B'
                if (size > 1024):
                    size = size/1024
                    units = 'KiB'
                if (size > 1024):
                    size = size/1024
                    units = 'MiB'
                if (size > 1024):
                    size = size/1024
                    units = 'GiB'
                print('  {:016X} - {:016X} {:.0f} {}'.format(mem_base + block[0], mem_base + block[0] + block[1] - 1, size, units))
                
def reallocMem(add, size):
    memory.reallocArea(add - mem_base, size)
    
def findFunction(name):
    for a in cpu.funcs.keys():
        if (cpu.funcs[a] == name):
            return a
    return None

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

    port_c = MemoryInterface(hw, 'port_c', mem_width, 64)     # The whole address space
    port_m = MemoryInterface(hw, 'port_m', mem_width, 20)     # 20	bits = 
    port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
    port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
    port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
    #port_t = MemoryInterface(hw, 'port_t', mem_width, 8)     # 8 bits = 256
    # Memory initialization

    memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

    memory.reallocArea(0, 1 << 20)
    memory.verbose = False

    #test = ISATestCommunication(hw, 'test', mem_width, 8, port_t)


    # Uart initialization
    uart = Uart(hw, 'uart', port_u)


    int_soft = hw.wire('int_soft')
    int_timer = hw.wire('int_timer')
    reset = hw.wire('reset')
    zero = hw.wire('zero')

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

    
    py4hw.Constant(hw, 'zero', 0, zero)
    py4hw.Reg(hw, 'auto_reset', zero, reset, reset_value=1)

    registerBase = mem_base +  (1 << 20) - 0x10000 # (8 * 8192)
    
    print('register base:', hex(registerBase))
    cpu = MicroprogrammedRISCV(hw, 'RISCV', reset, port_c, int_soft, int_timer, ext_int_targets, mem_base, registerBase)

    cpu.behavioural_memory = memory
    cpu.min_clks_for_trace_event = 1000

    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    
    return hw


def prepareTest(test_file):
    global hw
    hw = buildHw()
    programFile = ex_dir + test_file
    symbolFile = programFile + '.sym'
    
    loadElf(memory, programFile, mem_base ) # 32*4 - 0x10054)
    loadSymbolsFromElf(cpu, programFile, 0)
    loadSymbolsFromElf(cpu, programFile, 0xffffffff7fe00000)    # for virtual memory tests
    
    #if not(os.path.exists(symbolFile)):
    #    os.system('/opt/riscv/bin/riscv64-unknown-elf-objdump -t {} > {}'.format(programFile, symbolFile))
    #loadSymbols(cpu,  symbolFile, 0) # 32*4 - 0x10054)


def runTest(test_file, verbose=False):
    prepareTest(test_file)
    #passAdr = findFunction('pass')
    write_tohost = findFunction('write_tohost')
    tohost_adr = findFunction('tohost')

    if (tohost_adr is None):
        print('tohost symbol not found in', cpu.funcs)
        return

    #run(passAdr, verbose=False)
    run(write_tohost, maxclks=70000, verbose=verbose)
    run(0, maxclks=200, verbose=False)

    # print('Test', test_file, end='')
    #if (cpu.pc != passAdr):
    value = memory.readByte(tohost_adr-mem_base)
    
    if (value != 1):
        raise Exception('Test return value = {}'.format(value))
    else:
        print('Test return value = {}'.format(value))


prefixes = ['rv32mi-p', 'rv32si-p', 'rv32ua-p',
            'rv32ua-v', 'rv32uc-p', 'rv32uc-v', 'rv32ud-p', 'rv32ud-v', 'rv32uf-p', 'rv32uf-v',
            'rv32ui-p', 'rv32ui-v', 'rv32um-p', 'rv32um-v', 'rv32uzba-p', 'rv32uzba-v', 'rv32uzbb-p', 
            'rv32uzbb-v', 'rv32uzbc-p', 'rv32uzbc-v', 'rv32uzbs-p', 'rv32uzbs-v', 'rv32uzfh-p', 'rv32uzfh-v', 
            'rv64mi-p', 'rv64mzicbo-p', 'rv64si-p', 'rv64ssvnapot-p', 'rv64ua-p', 'rv64ua-v', 'rv64uc-p', 
            'rv64uc-v', 'rv64ud-p', 'rv64ud-v', 'rv64uf-p', 'rv64uf-v', 'rv64ui-p', 'rv64ui-v', 'rv64um-p', 'rv64um-v',
            'rv64uzba-p', 'rv64uzba-v', 'rv64uzbb-p', 'rv64uzbb-v', 'rv64uzbc-p', 'rv64uzbc-v', 'rv64uzbs-p', 'rv64uzbs-v',
            'rv64uzfh-p', 'rv64uzfh-v']

#selected_prefixes = ['rv32mi-p', 'rv32si-p', 'rv32ua-p',
#            'rv32uc-p', 'rv32ud-p', 'rv32uf-p', 
#            'rv32ui-p', 'rv32um-p', 'rv32uzba-p', 'rv32uzbb-p', 
#            'rv32uzbc-p', 'rv32uzbs-p', 'rv32uzfh-p', 
#            'rv64mi-p', 'rv64mzicbo-p', 'rv64si-p', 'rv64ssvnapot-p', 
#            'rv64ua-p', 'rv64uc-p', 
#            'rv64ud-p', 'rv64uf-p', 'rv64ui-p', 'rv64um-p', 
#            'rv64uzba-p', 'rv64uzbb-p', 'rv64uzbc-p', 'rv64uzbs-p', 
#            'rv64uzfh-p']

            
selected_prefixes = ['rv64mi-p', 'rv64mzicbo-p', 'rv64si-p', 'rv64ssvnapot-p', 'rv64ua-p', 'rv64ua-v', 'rv64uc-p', 
                     'rv64uc-v', 'rv64ud-p', 'rv64ud-v', 'rv64uf-p', 'rv64uf-v', 'rv64ui-p', 'rv64ui-v', 'rv64um-p', 'rv64um-v',
                     'rv64uzba-p', 'rv64uzba-v', 'rv64uzbb-p', 'rv64uzbb-v', 'rv64uzbc-p', 'rv64uzbc-v', 'rv64uzbs-p', 'rv64uzbs-v',
                     'rv64uzfh-p', 'rv64uzfh-v']

def computeAllTests():
    files = os.listdir(ex_dir)
    ret = {}

    files = [name for name in files if  any(name.startswith(prefix) for prefix in selected_prefixes)]


    for f in files:
        if (isElf(ex_dir + f)):
            #if (f[0:4] != 'rv64'):
            #    continue

            print('Run test', f, end=' ')
            try:
                runTest(f)
                print('PASSED')
                ret[f] = ('OK')
            except Exception as e:
                print('FAILED')
                ret[f] = ('FAILED', e)
        else:
            print(f'{f} not ELF')

    return ret

def asciiProgressBar(n, t):
    p = n*100/t
    pl = 45
    pok = math.ceil(pl*n/t)
    pko = pl - pok
    sok = '█' * pok
    sko = '░' * pko
    sp = '{:.1f} %'.format(p)
    s = '{:8} |{}{}|'.format(sp,sok,sko)
    return s
    
def runAllTests():
    nOK = 0
    nTotal = 0
    ret = computeAllTests()
    
    groupResults = {}
    
    for prefix in selected_prefixes:
        nOKGroup = 0
        nTotalGroup = 0

        files = [name for name in ret.keys() if name.startswith(prefix) ]
        for t in files:
            nTotal += 1
            nTotalGroup += 1
            if (ret[t] =='OK'):
                 print('Test {:30} = {}'.format(t, ret[t]))
                 nOK += 1
                 nOKGroup += 1
            else:
                 print('Test {:30} = {} - {}'.format(t, ret[t][0], ret[t][1]))

        groupResults[prefix]=(nOKGroup, nTotalGroup)
        
    print('Total: {} Correct: {} ({:.1f} %)'.format(nTotal, nOK, nOK*100/nTotal))     
    print(asciiProgressBar(nOK, nTotal))

    for prefix in selected_prefixes:
        nOKGroup = groupResults[prefix][0]
        nTotalGroup = groupResults[prefix][1]
        print('Group: {} Total: {} Correct: {} ({:.1f} %)'.format(prefix, nTotalGroup, nOKGroup, nOKGroup*100/nTotalGroup))     

    for prefix in selected_prefixes:
        nOKGroup = groupResults[prefix][0]
        nTotalGroup = groupResults[prefix][1]
        print(f'{prefix:15}', asciiProgressBar(nOKGroup, nTotalGroup))
        
#test_file = 'rv64mi-p-ma_addr'
#runTest(test_file)


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
