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

ex_dir = 'isa/'

if not(os.path.exists(ex_dir)):
    raise Exception('ISA tests not found')

from riscv.memory import *
from riscv.bus import *
from riscv.uart import *
from riscv.clint import *
from riscv.plic import *
from riscv.single_cycle.singlecycle_processor import *
from riscv.instruction_decode import *
from riscv.interactive_commands import *

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

    if (tf != t0):    
        freq = (clkf-clk0)/(tf-t0)
    else:
        freq = '?'

    print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, freq))
        
        
def step(steps = 1):
    sim = hw.getSimulator()
    sim.do_run = True
    count = 0
    
    while (count < steps and sim.do_run == True ):
        inipc = cpu.pc
        while (cpu.pc == inipc and sim.do_run == True ):
            sim.clk(1)
            
        count += 1
        
def regs():
    print('pc: {:016X}'.format(cpu.pc))
    for i in range(8):
        print('r{:2}={:016X}  |  r{:2}={:016X}  |  r{:2}={:016X}  |  r{:2}={:016X} '.format(
            i, cpu.reg[i], i+8, cpu.reg[i+8], i+16, cpu.reg[i+16], i+24, cpu.reg[i+24]))
            
    for i in range(8):
        print('fr{:2}={:016X}  |  fr{:2}={:016X}  |  fr{:2}={:016X}  |  fr{:2}={:016X} '.format(
            i, cpu.freg[i], i+8, cpu.freg[i+8], i+16, cpu.freg[i+16], i+24, cpu.freg[i+24]))
        
## used when upgrading stack from address to address+time
# def fix_stack():
#     newstack = []
#     for i in cpu.stack:
#         newstack.append((i,0))
        
#     cpu.stack = newstack
    
def stack():
    for idx, finfo in enumerate(cpu.stack):
        
        #f = cpu.getPhysicalAddressQuick(finfo[0])
        f = finfo[0]    # no need to translate, since symbols are provided in 
                        # virtual memory addresses for kernel
        
        if (f in cpu.funcs.keys()):
            print(' '*idx, cpu.funcs[f])
        else:
            print(' '*idx, '{:016X}'.format(f))
                  
def console():
    for line in uart.console:
        print(line)
        
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


def get_va_parts(v):
    ret = {}
    ret['vpn2'] = (v >> 30) & ((1<<9)-1)
    ret['vpn1'] = (v >> 21) & ((1<<9)-1)
    ret['vpn0'] = (v >> 12) & ((1<<9)-1)
    ret['offset'] = v & ((1<<12)-1)
    return ret
            
def pageTables(root=None, vbase = 0, level=2, printPTE=True):
    """
    Traverses the page tables from the provided root page table.
    The R flag indicates that the PTE is a leaf.
    
    Parameters
    ----------
    root : TYPE, optional
        DESCRIPTION. The default is None.
    vbase : TYPE, optional
        DESCRIPTION. The default is 0.
    level : TYPE, optional
        DESCRIPTION. The default is 2.
    printPTE : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    The number of valid page tables .

    """
    if (root is None):
        v = cpu.csr[0x180] # satp
        mode = (v >> 60) & ((1<<4)-1)
        smode = ['Base', '','','','','','','','Sv39','Sv48','Sv57','Sv64'][mode]
        asid = (v >> 44) & ((1<<16)-1)
        print('Virtual Memory Mode: {} {} ASID: {:04X}'.format(mode, smode, asid))
        root = (v & ((1<<44)-1)) << 12
        
        if (root == 0):
            return 0
    
    indent = ''
    for i in range(2-level): indent += ' '
    
    if (level == 2):
        tableName = 'Root'
    else:
        tableName = 'Table'
    print('{}{}: {:08X}'.format(indent, tableName, root))
    
    totalTables = 1
    
    for i in range(0, 512, 1):
        add = root+i*8
        v = memory.read_i64(add-mem_base)
        ppn2 = (v >> 28) & ((1<<26)-1)
        ppn1 = (v >> 19) & ((1<<9)-1)
        ppn0 = (v >> 10) & ((1<<9)-1)
        rsw = (v >> 8) & ((1<<2)-1)
        D = [' ','D'][(v >> 7) & 1]
        A = [' ','A'][(v >> 6) & 1]
        G = [' ','G'][(v >> 5) & 1]
        U = [' ','U'][(v >> 7) & 1]
        X = [' ','X'][(v >> 3) & 1]
        W = [' ','W'][(v >> 2) & 1]
        R = [' ','R'][(v >> 1) & 1]
        valid = v & 1
        
        va = vbase + (1 << [12,21,30][level]) * i
                
        phy = ppn2 << 30 | ppn1 << 21 | ppn0 << 12
        
        if (valid):
            if (printPTE):
                print('{} {:3d} ppn2:{:08X} ppn1:{:03X} ppn0:{:03X} rsw:{:0} '
                      '{}{}{}{}{}{}{} va: {:016X} pa: {:016X}'.format(
                          indent,  i, ppn2, ppn2, ppn0, rsw, 
                          D,A,G,U,X,W,R,
                          va, phy))
            
            if (X == ' ' and W == ' ' and R == ' '):
                totalTables += pageTables(phy, va, level-1, printPTE)
    
    return totalTables

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

    port_c = MemoryInterface(hw, 'port_c', mem_width, 40)
    port_m = MemoryInterface(hw, 'port_m', mem_width, 14)     # 14	bits = 
    port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
    port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
    port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
    #port_t = MemoryInterface(hw, 'port_t', mem_width, 8)     # 8 bits = 256
    # Memory initialization

    memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

    memory.reallocArea(0, 1 << 16)

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

    cpu = SingleCycleRISCV(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

    cpu.min_clks_for_trace_event = 1000

    # pass objects to interactive commands module
    import riscv.interactive_commands
    riscv.interactive_commands._ci_hw = hw
    riscv.interactive_commands._ci_cpu = cpu
    
    return hw


def prepareTest(test_file):
    global hw
    hw = buildHw()
    programFile = ex_dir + test_file
    symbolFile = programFile + '.sym'
    
    loadElf(memory, programFile, mem_base ) # 32*4 - 0x10054)
    
    if not(os.path.exists(symbolFile)):
        os.system('/opt/riscv/bin/riscv64-unknown-elf-objdump -t {} > {}'.format(programFile, symbolFile))
    loadSymbols(cpu,  symbolFile, 0) # 32*4 - 0x10054)


def runTest(test_file):
    prepareTest(test_file)
    #passAdr = findFunction('pass')
    write_tohost = findFunction('write_tohost')
    tohost_adr = findFunction('tohost')

    #run(passAdr, verbose=False)
    run(write_tohost, maxclks=10000, verbose=False)
    run(0, maxclks=20, verbose=False)

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
            
selected_prefixes = ['rv64mi-p', 'rv64si-p', 'rv64ssvnapot-p', 'rv64ua-p', 'rv64uc-p', 
                     'rv64ud-p', 'rv64uf-p',  'rv64ui-p',  'rv64um-p', 'rv64uzba-p', 'rv64uzbb-p', 'rv64uzbc-p', 'rv64uzbs-p', 'rv64uzfh-p']

def computeAllTests():
    files = os.listdir(ex_dir)
    ret = {}

    files = [name for name in files if  any(name.startswith(prefix) for prefix in selected_prefixes)]


    for f in files:
        if (isElf(ex_dir + f)):
            if (f[0:4] != 'rv64'):
                continue

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

def runAllTests():
    nOK = 0
    nTotal = 0
    ret = computeAllTests()
    
    for prefix in selected_prefixes:
        files = [name for name in ret.keys() if name.startswith(prefix) ]
        for t in files:
            nTotal += 1
            if (ret[t] =='OK'):
                 print('Test {:30} = {}'.format(t, ret[t]))
                 nOK += 1
            else:
                 print('Test {:30} = {} - {}'.format(t, ret[t][0], ret[t][1]))

    print('Total: {} Correct: {} ({:.1f} %)'.format(nTotal, nOK, nOK*100/nTotal))     

test_file = 'rv64mi-p-ma_addr'
runTest(test_file)


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
