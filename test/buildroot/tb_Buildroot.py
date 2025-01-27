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

ex_dir = 'buildroot-2024.02.10/output/images/'

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

# the following constants are inspired by opensbi/platform/fpga/ariane/platform.c
HART_COUNT = 1
UART_ADDR = 0x10000000
UART_FREQ = 0x50000000
UART_BAUDRATE = 115200
PLIC_ADDR =  0xc000000
PLIC_SIZE = (0x200000 + (HART_COUNT * 0x1000))
PLIC_NUM_SOURCES = 3
CLINT_ADDR = 0x2000000

#<----

mem_base = 0x80000000

    
def reallocMem(add, size):
    memory.reallocArea(add - mem_base, size)


    
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
    

        
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
#  | 0000 0C00 0000 | 0000 0C20 0FFF | PLIC          |
#  | 0000 1000 0000 | 0000 1000 0FFF | UART          |
#  | 0000 8000 0000 | 0001 BFEF FFFF | memory (5GB)  |
#  | 0001 BFF0 0000 | 0002 8000 0000 | pmem (3GB)    |
#  | 00FF F102 0000 | 00FF F102 FFFF | CLINT         |


hw = HWSystem()

port_c = MemoryInterface(hw, 'port_c', mem_width, 40)
port_m = MemoryInterface(hw, 'port_m', mem_width, 32)     # 32bits = 4 GB
port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
port_d = MemoryInterface(hw, 'port_d', mem_width, 32)     # 4 GB
# Memory initialization

#memory = Memory(hw, 'main_memory', 32, 25-2, port)
memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

#memory.reallocArea(0xB0200000, 0x2000)

#pmem = PersistentMemory(hw, 'pmem', ex_dir + 'pmem.img', port_d)

# Uart initialization
uart = Uart(hw, 'uart', port_u, reg_size=4)


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
bus = MultiplexedBus(hw, 'bus', port_c, [(port_m, mem_base),
                                          #(port_d, 0x01BFF00000),
                                          (port_u, UART_ADDR),
                                          (port_p, PLIC_ADDR),
                                          (port_l, CLINT_ADDR)])

cpu = SingleCycleRISCV(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

#cpu.stopOnExceptions = True
cpu.behavioural_memory = memory

#loadSymbols(cpu, ex_dir + 'fw_payload.sym', 0) # 32*4 - 0x10054)
#loadSymbols(cpu, ex_dir + 'vmlinux.sym',  0) # 32*4 - 0x10054)
#loadSymbols(cpu, ex_dir + 'vmlinux.sym',  0xFFFFFFE00000704C - 0x8020704C) # 32*4 - 0x10054)
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


def restoreOpensbi():
    print('Restoring patched memory to avoid relocation')
    restore('opensbi.dat')
    programFile = ex_dir + 'fw_payload.elf'
    loadSymbolsFromElf(cpu, programFile, 0)
    linuxSymbols = 'vmlinux.sym'
    #loadSymbols(cpu, linuxSymbols)
    #loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80200000)

def restoreLinux():
    print('Restoring patched memory to avoid relocation')
    restore('checkpoint.dat')
    programFile = ex_dir + 'fw_payload.elf'
    linuxSymbols = 'vmlinux.sym'
    loadSymbols(cpu, linuxSymbols)
    loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80200000)
    
def runOpensbi():
    tbreak(0x80200000); go()
    checkpoint('opensbi.dat')
    write_trace('opensbi.json')
    
def dumpLog():
    pa_prb = translateVirtualAddress(findFunction('prb'))
    va_desc_ring = memory.read_i64(pa_prb-mem_base)
    va_text_ring = memory.read_i64(pa_prb-mem_base+8)
    print('va desc_ring = {:016X}'.format(va_desc_ring))
    print('va textring = {:016X}'.format(va_text_ring))
    
def prepareXip():
    programFile = ex_dir + 'Image'
    loadProgram(memory, programFile, 0x80000000-mem_base )
    linuxSymbols = 'vmlinux.sym'
    loadSymbols(cpu, linuxSymbols)
    loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80000000)
    
def enableMemblockDebug():
    va = findFunction('memblock_debug')
    pa = translateVirtualAddress(va)
    memory.write_i64(pa-mem_base, 1)

def disableMemblockDebug():
    va = findFunction('memblock_debug')
    pa = translateVirtualAddress(va)
    memory.write_i64(pa-mem_base, 0)
    
def dumpDTB():
    va = findFunction('_dtb_early_va')
    pa = translateVirtualAddress(va)
    va = memory.read_i64(pa-mem_base)
    pa = translateVirtualAddress(va)
    dump(pa, 0x800)

def prepare():
    print('No checkpoint, loading program')
    programFile = ex_dir + 'fw_payload.elf'
    fdtFile = ex_dir + 'punxa_rv64.dtb'
    linuxSymbols = 'vmlinux.sym'
    
    loadElf(memory, programFile, mem_base, verbose=True ) # 32*4 - 0x10054)
    loadSymbolsFromElf(cpu,  programFile, 0)
    loadProgram(memory, fdtFile, 0x81000000-mem_base )
    loadSymbols(cpu, linuxSymbols)
    loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80200000)

    cpu.reg[11] = 0x81000000
    
    cpu.min_clks_for_trace_event = 1


    reallocMem(0x80020000, 0x400 * 400)
    reallocMem(0x82200000, 0x400 * 400)
    #reallocMem(0xFBFFF000,  0x4001000)
    #reallocMem(0x100100000, 0x400 * 0x400)
    #reallocMem(0x100200000, 0x400 * 0x400)
    #reallocMem(0x100300000, 0x400 * 0x400)
    #reallocMem(0x100400000, 0x400 * 0x400)
    #reallocMem(0x100800000, 0x400 * 0x400)
    #reallocMem(0x100900000, 0x400 * 0x400)
    #reallocMem(0x1BA000000,  0x5f00000)

#hw.getSimulator().clk(15900)

# should write 1 in 0x3B030

#step(20)

#run(cpu.getPhysicalAddressQuick(0xFFFFFFE00060A1F4), maxclks=100000000)

def getSz(ptr):
    doRun = True
    i = 0
    s = ''
    while (doRun):
        c = memory.read_i32(ptr+i-mem_base) & 0xFF
        if (c == 0):
            doRun = False
            continue
        
        s += chr(c)
        i += 1
    return s

def OpenSBIInfo():
    domain = findFunction('root')
    
    domain_name = domain + 0x18
    domain_harts_offset = domain + 0x58
    domain_mem_regions_offset = domain + 0x60
    
    domain_harts_ptr = memory.read_i32(domain_harts_offset-mem_base)
    domain_harts = memory.read_i32(domain_harts_ptr-mem_base)

    domain_mem_regions_ptr = memory.read_i32(domain_mem_regions_offset-mem_base)
    
    print('Open SBI')
    print('Domains:')
    print(' Root:', getSz(domain_name))
    print(' Harts Bitmap:', hex(domain_harts))
    
    print(' Memory Regions:')
    
    doRun = True
    i = 0
    while (doRun):
        domain_mem_region_order = memory.read_i64(domain_mem_regions_ptr - mem_base)
        domain_mem_region_base = memory.read_i64(domain_mem_regions_ptr + 8 - mem_base)
        domain_mem_region_flags = memory.read_i64(domain_mem_regions_ptr + 8*2 - mem_base)

        if (domain_mem_region_order == 0):
            doRun = False
            continue
        print(f'  Region {i} order: {domain_mem_region_order} base:{domain_mem_region_base:016X} flags:{domain_mem_region_flags:016X}')
        
        domain_mem_regions_ptr += 8*3
        i += 1

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
             run(0, maxclks=50000*60*5, verbose=False) # run simulation for 2 minutesº
             write_trace() 
             checkpoint()
        

	
