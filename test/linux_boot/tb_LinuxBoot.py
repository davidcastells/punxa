# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:13:48 2022

@author: dcr
"""

import sys
import os

baseDir = '../..'

mem_width = 64

if not(baseDir in sys.path):
    print('appending .. to path')
    sys.path.append(baseDir)

ex_dir = './'

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

mem_base = 0x80000000

    
def reallocMem(add, size):
    memory.reallocArea(add - mem_base, size)


    
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
    
def loadProgram(memory, filename, offset):
    """
    

    Parameters
    ----------
    memory : TYPE
        memory device.
    filename : TYPE
        file to load.
    offset : TYPE
        offset in memory were to store the program.

    Returns
    -------
    None.

    """
    
    file = open(filename, 'rb')
    
    code = file.read()
        
    size = len(code)
    off = offset
    
    print('Code size:   {:10d}'.format(size))
    print('Memory size: {:10d}'.format(memory.getMaxSize()))
    
    memory.reallocArea(off, 1 << int(math.ceil(math.log2(size))))
    
    for x in code:
        memory.writeByte(off, x)
        off += 1
    file.close()
    
    print('program loaded!')
        
def loadSymbols(cpu, filename, address_fix=0):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    
    for line in lines:
        if not('\t' in line):
            continue
        
        part = line.split('\t')
        
        #if not(part[0][23] == 'F'):
        #    continue
        
        address = int(part[0][0:16],16) + address_fix
        func = part[1][17:].strip()
        
        cpu.funcs[address]= func
        
        #print('{:016X} = {}'.format( address, func))



def run(upto, maxclks=100000, verbose=True, autoCheckpoint=False):
    import time
    global print
    global dummy_print

    
    if not(verbose):
        cpu.setVerbose(False)
                        
    sim = hw.getSimulator()

    t0 = time.time()
    clk0 = sim.total_clks

    t0 = time.time()
    clk0 = sim.total_clks
    
    count = 0
    istart = cpu.csr[0xC02]
    ilast = istart
    
    while (cpu.pc != upto):
        sim.clk(1)
        count += 1
        icur = cpu.csr[0xC02]
        
        if not(sim.do_run):
            break;
        if (count > maxclks):
            break;
        if ((icur % 10000 == 0) and (icur != ilast)):
            print('ins: {:n}'.format(icur))
            ilast = icur
            
    if (cpu.pc != upto):
        print('did not reach address')

        if (sim.do_run and autoCheckpoint):
            print('auto checkpointing')
            checkpoint()

    if not(verbose):
        cpu.setVerbose(True)

    tf = time.time()
    clkf = sim.total_clks
    
    print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, (clkf-clk0)/(tf-t0)))
        
        

                  
def dump(address, size=0x100):
    pos = address 
    for i in range((size+15)//16):
        sline = ''
        print('{:016X}:|'.format(pos), end='')
        for j in range(16):
            value = memory.readByte(pos-mem_base)
            print('{:02X}'.format(value), end='')
            if (value >= 32 and value < 127):
                sline += chr(value)
            else:
                sline += '·'
            pos += 1
            
        print('| "{}"'.format(sline))
#    memory.write(32*4+0x00, 0xfe010113) # addi    sp,sp,-32
#    memory.write(32*4+0x04, 0x00112e23) # sw      ra,28(sp)



    

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
#  | 0001 BFF0 0000 | 0002 8000 0000 | pmem (3GB)    |
#  | 00FF F0C2 C000 | 00FF F0C2 CFFF | uart          |
#  | 00FF F102 0000 | 00FF F102 FFFF | CLINT         |
#  | 00FF F110 0000 | 00FF F11F FFFF | PLIC          |

hw = HWSystem()

port_c = MemoryInterface(hw, 'port_c', mem_width, 40)
port_m = MemoryInterface(hw, 'port_m', mem_width, 33)     # 32bits = 8 GB
port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
port_d = MemoryInterface(hw, 'port_d', mem_width, 32)     # 4 GB
# Memory initialization

#memory = Memory(hw, 'main_memory', 32, 25-2, port)
memory = SparseMemory(hw, 'main_memory', mem_width, 33, port_m, mem_base=mem_base)

#memory.reallocArea(0xB0200000, 0x2000)

pmem = PersistentMemory(hw, 'pmem', ex_dir + 'pmem.img', port_d)

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


#memory.write(2*4, 512*4) # set the sp to the end of the memory
bus = MultiplexedBus(hw, 'bus', port_c, [(port_m, mem_base, 0x013ff00000),
                                          (port_d, 0x01BFF00000),
                                          (port_u, 0xFFF0C2C000),
                                          (port_p, 0xFFF1100000),
                                          (port_l, 0xFFF1020000)])

cpu = SingleCycleRISCV(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

cpu.stopOnExceptions = True
cpu.behavioural_memory = memory

loadSymbols(cpu, ex_dir + 'fw_payload.sym', 0) # 32*4 - 0x10054)
loadSymbols(cpu, ex_dir + 'vmlinux.sym',  0) # 32*4 - 0x10054)
loadSymbols(cpu, ex_dir + 'vmlinux.sym',  0xFFFFFFE00000704C - 0x8020704C) # 32*4 - 0x10054)
#loadSymbols(cpu, ex_dir + 'vmlinux.sym', 0) # 0x0000000080200000 - 0xffffffe000000000) # 32*4 - 0x10054)


cpu.min_clks_for_trace_event = 1000

# pass objects to interactive commands module
import punxa.interactive_commands
punxa.interactive_commands._ci_hw = hw
punxa.interactive_commands._ci_cpu = cpu
punxa.interactive_commands._ci_bus = bus
punxa.interactive_commands._ci_uart = uart 

#hw.getSimulator().clk(150000)

#for i in range(10):
#    hw.getSimulator().clk(1)
#    
#    print('IR=', cpu.IR.get())
#    print('PC=', cpu.PC.get())
#    print('MAR=', cpu.MAR.get())

#from py4hw.schematic import Schematic

#hw.getSimulator().clk(100)
#gui.Workbench(hw)


if (os.path.exists(ex_dir + 'checkpoint.dat')):
    print('Restoring patched memory to avoid relocation')
    restore()
else:
    print('No checkpoint, loading program')
    programFile = ex_dir + 'osbi.bin'
    fdtFile = ex_dir + 'fdt.bin'
    
    loadProgram(memory, programFile, 0x80000000-mem_base ) # 32*4 - 0x10054)
    loadProgram(memory, fdtFile, 0xB0200000-mem_base )

    reallocMem(0xFBFFF000,  0x4001000)
    reallocMem(0x1BA000000,  0x5f00000)

#hw.getSimulator().clk(15900)

# should write 1 in 0x3B030

#step(20)

#run(cpu.getPhysicalAddressQuick(0xFFFFFFE00060A1F4), maxclks=100000000)



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
         elif (sys.argv[1] == '-sprint'):
             cpu.min_clks_for_trace_event=500
             run(0, maxclks=50000*60*100, verbose=False) # run simulation for 2 minutesº
             write_trace() 
             checkpoint()
        

	
