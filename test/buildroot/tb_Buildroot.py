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



def buildHw():
    
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
    global memory
    global cpu
    global hw
    global uart
        
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
    cpu.csr_write_verbose = True
    cpu.behavioural_memory = memory



    cpu.min_clks_for_trace_event = 1000

    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    punxa.interactive_commands._ci_bus = bus
    punxa.interactive_commands._ci_uart = uart 


# pass objects to interactive commands module
import punxa.interactive_commands



def restoreOpensbi():
    buildHw()   
    print('Restoring patched memory to avoid relocation')
    restore('opensbi.dat')
    programFile = ex_dir + 'fw_payload.elf'
    loadSymbolsFromElf(cpu, programFile, 0)
    linuxSymbols = 'vmlinux.sym'
    #loadSymbols(cpu, linuxSymbols)
    #loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80200000)

def restoreLinux():
    buildHw()
    print('Restoring patched memory to avoid relocation')
    restore('checkpoint.dat')
    programFile = ex_dir + 'fw_payload.elf'
    linuxSymbols = 'vmlinux.sym'
    loadSymbols(cpu, linuxSymbols)
    loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80200000)
    
def runOpensbi():
    #tbreak(0x80200000); go()
    run(0x80200000, 1000000000, verbose=False) 
    checkpoint('opensbi.dat')
    write_trace('opensbi.json')
    
def dumpLog():
    pa_prb = translateVirtualAddress(findFunction('prb'))
    va_desc_ring = memory.read_i64(pa_prb-mem_base)
    va_text_ring = memory.read_i64(pa_prb-mem_base+8)
    print('va desc_ring = {:016X}'.format(va_desc_ring))
    print('va textring = {:016X}'.format(va_text_ring))
    
    
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
    
def saveDTB():
    global mem_base
    va = findFunction('_dtb_early_va')
    pa = translateVirtualAddress(va)
    va = memory.read_i64(pa-mem_base)
    address = translateVirtualAddress(va)
    size = 2973
    
    filename = 'exported.dtb'
    #memory = _ci_cpu.behavioural_memory
    pos = address 
    with open(filename, "wb") as f:
        for i in range(size):
            value = memory.readByte(pos-mem_base)
            #print('{:02X}'.format(value), end='')
            f.write(value.to_bytes(1, byteorder='little'))
            pos += 1
            
        

def loadOpenSBISymbols():
    programFile = ex_dir + 'fw_payload.elf'
    loadSymbolsFromElf(cpu,  programFile, 0)

def loadLinuxSymbols():
    linuxSymbols = 'vmlinux.sym'
    loadSymbols(cpu, linuxSymbols)
    loadSymbols(cpu, linuxSymbols, -0xffffffff80000000 + 0x80200000)

def prepare():
    global memory
    global cpu
    buildHw()
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

    reallocMem(0x80020000, 0x10000)
    reallocMem(0x80200000, 0x3fe00000)



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
    
def runIters(iters=5):
    iter = 0 
    while (iter < iters):              
        run(0, 1000000, verbose=False)

        stack()
        iter += 1
        
        for line in uart.console[-10:]:
            print(line)

def runToMemblockAddRange(iters=10):
    va = findFunction('memblock_add_range')
    if (va is None):
        va = findFunction('memblock_add_range.isra.0')
        if (va is None):
            raise Exception()
         
    iter = 0 
    while (iter < iters):              
        run(va, 1000000, verbose=False)

        if (cpu.pc == va):
            reallocMem(cpu.reg[11], cpu.reg[12]);step(10)
            checkpoint()
        else:
            stack()
            iter += 1

def runUntilInterrupt(max_clks=100000):
    sim = hw.getSimulator()
    cnt = 0
    while (cnt < max_clks):
        timer_wire = cpu.int_timer_machine.get()
        cnt += 1
        sim.clk()
        
        if (timer_wire == 1):
            print('Timer Interrupt!')
            return
            
def reportInterrupts():
    print('Interrupt Status')
    print(' CPU:') # be prepared for multiple CPUs
    timer_wire = cpu.int_timer_machine.get()
    
    mideleg_mt = 1 if (cpu.csr[CSR_MIDELEG] & CSR_MIDELEG_MTI_MASK) else 0
    mideleg_st = 1 if (cpu.csr[CSR_MIDELEG] & CSR_MIDELEG_STI_MASK) else 0
        
    mtip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_MTIP_MASK) else 0
    stip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_STIP_MASK) else 0
    utip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_UTIP_MASK) else 0

    mtie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_MTIE_MASK) else 0
    stie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_STIE_MASK) else 0
    utie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_UTIE_MASK) else 0
    
    mie = 1 if (cpu.csr[CSR_MSTATUS] & CSR_MSTATUS_MIE_MASK) else 0
    sie = 1 if (cpu.csr[CSR_MSTATUS] & CSR_MSTATUS_SIE_MASK) else 0
    uie = 1 if (cpu.csr[CSR_MSTATUS] & CSR_MSTATUS_UIE_MASK) else 0
        
    if (mideleg_st):
        print(f'   CLINT MIDELEG     MIP          MIE       MSTATUS')
        print(f'   timer [{timer_wire}]    MTIP [{mtip}] --> MTIE [{mtie}] --> MIE [{mie}]')
        print(f'            \-> STIP [{stip}] --> STIE [{stie}] --> SIE [{sie}]')

    else:
        print(f'   CLINT MIDELEG     MIP          MIE       MSTATUS')
        print(f'   timer [{timer_wire}]--> MTIP [{mtip}] --> MTIE [{mtie}] --> MIE [{mie}]')
        print(f'       (sw) --> STIP [{stip}] --> STIE [{stie}] --> SIE [{sie}]')

    
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
        

	
