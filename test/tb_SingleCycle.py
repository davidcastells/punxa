# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:13:48 2022

@author: dcr
"""

import sys
import os

baseDir = '../'

mem_width = 64

if not(baseDir in sys.path):
    print('appending .. to path')
    sys.path.append(baseDir)

ex_dir = 'linux_boot/'

from riscv.memory import *
from riscv.bus import *
from riscv.uart import *
from riscv.clint import *
from riscv.plic import *
from riscv.single_cycle.singlecycle_processor import *
from riscv.instruction_decode import *
    

import py4hw    
import py4hw.debug
import py4hw.gui as gui
import zlib

mem_base = 0x80000000

def help():
    print('Interactive commands')
    print('loadProgram - loads a program in memory')
    print('loadSymbols - loads symbols')
    print('checkpoint')
    print('restore')
    print('run')
    print('step')
    
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
    
    print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, (clkf-clk0)/(tf-t0)))
        
        
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

def reportCSR(csr):
    if (not(isinstance(csr, str))):
        ncsr = csr
        csr = cpu.implemented_csrs[ncsr]
        
    if (isinstance(csr, str)):
         rlist = [k for k, v in cpu.implemented_csrs.items() if v == csr]
         if (len(rlist) == 0):
             return
         ncsr = rlist[0]

    v = cpu.csr[ncsr]
    
    if (csr == 'mstatus'):
        print('mstatus: {:016X}'.format(v))
        part = [[63,1],[34,2],[32,2],[22,1],[21,1],[20,1],[19,1],[18,1],[17,1],[15,2],[13,2],
                [11,2],[8,1],[7,1],[5,1],[4,1],[3,1],[1,1],[0,1]]
        pname = ['SD - Dirty summary', 'SXL - XLEN in S-Mode', 'UXL - XLEN in U-Mode',
                 'TSR - Trap SRET', 'TW - Timeout Wait', 'TVM - Trap Virtual Memory',
                 'MXR - Make Executable Readable', 'SUM - Permit Supervisor User Memory Access',
                 'MPRV - Modify Privilege', 'XS - Extensions status', 'FS - Floating point status',
                 'MPP - M-Mode Previous Privilege','SPP - S-Mode Previous Privilege',
                 'MPIE', 'SPIE','UPIE','MIE','SIE','UIE']
        
        for i in range(len(pname)):
            x = (v >> part[i][0]) & ((1<<part[i][1])-1)
            print('  * {}: {}'.format(pname[i], x))    
        
    elif (csr == 'mepc'):
        print('mepc: {}'.format(cpu.addressFmt(v)))
    elif (csr == 'satp'):
        print('satp: {:016X}'.format(v))
        n = (v >> 60) & ((1<<4)-1)
        sn = ['Base', '','','','','','','','Sv39','Sv48','Sv57','Sv64'][n]
        print('  * Mode: {} {}'.format(n, sn))
        n = (v >> 44) & ((1<<16)-1)
        print('  * ASID: {:04X}'.format(n))
        n = v & ((1<<44)-1)
        n2 = n << 12
        print('  * PPN: {:016X} -> {:016X}'.format(n, n2))
            
    elif (csr == 'privlevel'):
        print('privlevel: {}'.format(v), end=' ')
        if (v == 0): print('USER')
        if (v == 1): print('SUPERVISOR')
        if (v == 3): print('MACHINE')
    elif (csr == 'mip'):
        print('mip: {:016X}'.format(v))
        print('   MEIP: machine-mode external interrup pending', get_bit(v, 11))
        print('   SEIP: supervisor-mode external interrup pending', get_bit(v, 9))
        print('   UEIP: user-mode external interrup pending', get_bit(v, 8))
        print('   MTIP: machine-mode timer interrup pending', get_bit(v, 7))
        print('   STIP: supervisor-mode timer interrup pending', get_bit(v, 5))
        print('   UTIP: user-mode timer interrup pending', get_bit(v, 4))
        print('   MSIP: machine-mode software interrup pending', get_bit(v, 3))
        print('   SSIP: supervisor-mode software interrup pending', get_bit(v, 1))
        print('   USIP: user-mode software interrup pending', get_bit(v, 0))
    elif (csr == 'mie'):
        print('mie: {:016X}'.format(v))
        print('   MEIE: machine-mode external interrup enable', get_bit(v, 11))
        print('   SEIE: supervisor-mode external interrup enable', get_bit(v, 9))
        print('   UEIE: user-mode external interrup enable', get_bit(v, 8))
        print('   MTIE: machine-mode timer interrup enable', get_bit(v, 7))
        print('   STIE: supervisor-mode timer interrup enable', get_bit(v, 5))
        print('   UTIE: user-mode timer interrup enable', get_bit(v, 4))
        print('   MSIE: machine-mode software interrup enable', get_bit(v, 3))
        print('   SSIE: supervisor-mode software interrup enable', get_bit(v, 1))
        print('   USIE: user-mode software interrup enable', get_bit(v, 0))
        
    elif (csr == 'medeleg'): 
        print('medeleg:')
        print(' delegate exceptions to lower privilege modes.')
        msg = ['Instruction address misaligned',
               'Instruction access fault',
               'Illegal instruction',
               'Breakpoint',
                'Load address misaligned',
                'Load access fault',
                'Store/AMO address misaligned',
                'Store/AMO access fault',
                'Environment call from U-mode',
                'Environment call from S-mode',
                'Reserved',
                'Environment call from M-mode',
                'Instruction page fault',
                'Load page fault',
                'Reserved',
                'Store/AMO page fault' ]
        
        for i in range(16):
            if (get_bit(v, i)): print('  * {}'.format(msg[i]))
            
    else:
        print('{}: {}'.format(csr, v))
            
def pageTables(root=None, vbase = 0, level=2, printPTE=True):
    """
    Traverses the page tables from the provided root page table
    
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
            return hex(a)
    return 'not found'

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

loadSymbols(cpu, ex_dir + 'fw_payload.sym', 0) # 32*4 - 0x10054)
loadSymbols(cpu, ex_dir + 'vmlinux.sym', 0) # 0x0000000080200000 - 0xffffffe000000000) # 32*4 - 0x10054)


cpu.min_clks_for_trace_event = 1000

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
    #dtsFile = 'c:\\projects/research/INT_Papers/01 Dev - FPL2023 - Trimmed RISCV/riscvisacoverage/example/ariane-dtc.json'
    fdtFile = ex_dir + 'fdt.bin'
    
    loadProgram(memory, programFile, 0x80000000-mem_base ) # 32*4 - 0x10054)
    #loadProgram(memory, dtsFile, 0xB0200000)
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
