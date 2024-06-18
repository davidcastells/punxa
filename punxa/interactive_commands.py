# -*- coding: utf-8 -*-
"""
Created on Sat May 25 15:41:27 2024

@author: dcastel1
"""
import math
from .temp_helper import *

_ic_verbose = False
tbreak_address = None
_ci_hw = None
_ci_cpu = None

def list_commands():
    print('Interactive commands')
    print('  loadProgram - load a program (elf) in memory')
    print('  checkpoint  - save the system state in a file')
    print('  restore     - restore the system state from a file')
    print('  run         - run the system for a number of cycles')
    print('  step        - run an instruction step')
    print('  tbreak      - set a temporal breakpoint')
    print('  go          - run until the temporal breakpoint')
    print('  regs        - display the registers of the processor')
    print('  reportCSR   - display the content of CSRs')
    print('  console     - display the content of the console')
    print('  stack       - display the stack')


def regs():
    cpu = _ci_cpu
    print('pc: {:016X}'.format(cpu.pc))
    for i in range(8):
        print('r{:2}={:016X}  |  r{:2}={:016X}  |  r{:2}={:016X}  |  r{:2}={:016X} '.format(
            i, cpu.reg[i], i+8, cpu.reg[i+8], i+16, cpu.reg[i+16], i+24, cpu.reg[i+24]))
            
    for i in range(8):
        print('fr{:2}={:016X}  |  fr{:2}={:016X}  |  fr{:2}={:016X}  |  fr{:2}={:016X} '.format(
            i, cpu.freg[i], i+8, cpu.freg[i+8], i+16, cpu.freg[i+16], i+24, cpu.freg[i+24]))


def write_trace(filename='newtrace.json'):
    cpu.tracer.write_json(filename)

def console():
    for line in _ci_cpu.console:
        print(line)

def stack():
    indent = 0
    for idx, finfo in enumerate(_ci_cpu.stack):
        
        #f = cpu.getPhysicalAddressQuick(finfo[0])
        f = finfo[0]    # no need to translate, since symbols are provided in 
                        # virtual memory addresses for kernel
        j = finfo[2]    # indicates it is a jump

        ec = '|' if j else '+->'        
        if (f in _ci_cpu.funcs.keys()):
            print(' '*indent, ec, _ci_cpu.funcs[f])
        else:
            print(' '*indent, ec, '{:016X}'.format(f))
            
        if not(j): indent += 1

def isElf(filepath):
    from elftools.elf.elffile import ELFFile
    try:
        with open(filepath, 'rb') as file:
            elf = ELFFile(file)
            return True
    except Exception as e:
        return False


def loadElf(memory, filename, offset):
    from elftools.elf.elffile import ELFFile

    f = open(filename,'rb')
    elffile = ELFFile(f,'rb')

    for seg in elffile.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            adr = seg['p_paddr']
            data = seg.data()
            size = len(data)
            print('ELF segment. address: {:016X} - {:016X}'.format(adr, size))
            memory.reallocArea(adr - offset, 1 << int(math.ceil(math.log2(size))))
            p = adr - offset
            for x in data:
                memory.writeByte(p, x)
                p += 1

def loadSymbolsFromElf(cpu,  filename, offset):
    from elftools.elf.elffile import ELFFile
    
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        # Iterate through sections to find the symbol table
        for section in elffile.iter_sections():
            #if section.name == '.symtab':  # Commonly, the symbol table section is named '.symtab'
            if hasattr(section, 'iter_symbols'):
                for symbol in section.iter_symbols():
                    #if symbol['st_info']['type'] == 'STT_FUNC':
                    addr = symbol['st_value'] + offset
                    name = symbol.name
                    cpu.funcs[addr]= name


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

    if (_ic_verbose):    
        print('Code size:   {:10d}'.format(size))
        print('Memory size: {:10d}'.format(memory.getMaxSize()))
    
    memory.reallocArea(off, 1 << int(math.ceil(math.log2(size))))
    
    for x in code:
        memory.writeByte(off, x)
        off += 1
    file.close()

    if (_ic_verbose):
        print('program loaded!')

def multi_split(s, l):
    ret = [s]

    for el in l:
        ret2 = []
        for x in ret:
            for y in x.split(el):
                if (len(y)>0):
                    ret2.append(y)
        ret = ret2
    return ret

        
def loadSymbols(cpu, filename, address_fix=0):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    
    for line in lines:
        if not('\t' in line):
            continue
        
        part = multi_split(line, '\t\n ')
        
        #if not(part[0][23] == 'F'):
        #    continue
 
        try:       
            address = int(part[0][0:16],16) + address_fix
            func = part[4]
        
            cpu.funcs[address]= func
        
            #print('{:016X} = {}'.format( address, func))
        except:
            print('Failed to parse', part)


def step(steps = 1):
    import time
    sim = _ci_hw.getSimulator()
    sim.do_run = True
    count = 0
    
    if (steps >= 100):
        sim = _ci_hw.getSimulator()

        t0 = time.time()
        clk0 = sim.total_clks
        
        
        
    while (count < steps and sim.do_run == True ):
        inipc = _ci_cpu.pc
        while (_ci_cpu.pc == inipc and sim.do_run == True ):
            sim.clk(1)
            
        count += 1
        
    if (steps >= 100):
        tf = time.time()
        clkf = sim.total_clks
        
        if (tf != t0):    
            freq = (clkf-clk0)/(tf-t0)
        else:
            freq = '?'
            
        print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, freq))
        
def findFunction(name):
    for a in _ci_cpu.funcs.keys():
        if (_ci_cpu.funcs[a] == name):
            return a
    return None

def finish():
    tbreak(_ci_cpu.reg[1])
    go()

def tbreak(add):
    global tbreak_address
    tbreak_address = add
    
def go():
    import time
    global tbreak_address
    sim = _ci_hw.getSimulator()
    sim.do_run = True
    count = 0
    
    
    t0 = time.time()
    clk0 = sim.total_clks
    
    while (_ci_cpu.pc != tbreak_address and sim.do_run == True ):
        inipc = _ci_cpu.pc
        while (_ci_cpu.pc == inipc and sim.do_run == True ):
            sim.clk(1)
            
        count += 1            

    tf = time.time()
    clkf = sim.total_clks
    
    if (tf != t0):    
        freq = (clkf-clk0)/(tf-t0)
    else:
        freq = '?'
        
    print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, freq))
    tbreak_address = None

def reportCSR(csr):
    cpu = _ci_cpu
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

    elif (csr == 'fflags'):
        print('fflags: {:016X}'.format(v))
        print('   NV: invalid operation', get_bit(v, 4))                
        print('   DZ: divide by zero', get_bit(v, 3))                
        print('   OF: overflow', get_bit(v, 2))                
        print('   UF: underflow', get_bit(v, 1))                
        print('   NX: inexact', get_bit(v, 0))                
        
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

def checkpoint(filename='checkpoint.dat'):
    import shutil
    from serialize import Serializer 
    
    cpu = _ci_cpu
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

def restore(filename= 'checkpoint.dat'):
    from serialize import Deserializer 
    
    cpu = _ci_cpu
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
        _ci_cpu.setVerbose(False)
                        
    sim = _ci_hw.getSimulator()

    t0 = time.time()
    clk0 = sim.total_clks

    t0 = time.time()
    clk0 = sim.total_clks
    
    count = 0
    istart = _ci_cpu.csr[0xC02]
    ilast = istart
    
    while (cpu.pc != upto):
        sim.clk(1)
        count += 1
        icur = _ci_cpu.csr[0xC02]
        
        if not(sim.do_run):
            break;
        if (count > maxclks):
            break;
        if ((icur % 10000 == 0) and (icur != ilast)):
            print('ins: {:n}'.format(icur))
            ilast = icur
            
    if (_ci_cpu.pc != upto):
        print('did not reach address')

        if (sim.do_run and autoCheckpoint):
            print('auto checkpointing')
            checkpoint()

    if not(verbose):
        _ci_cpu.setVerbose(True)

    tf = time.time()
    clkf = sim.total_clks

    if (tf != t0):    
        freq = (clkf-clk0)/(tf-t0)
    else:
        freq = '?'

    print('clks: {} time: {} simulation freq: {}'.format(clkf-clk0, tf-t0, freq))


def dump(address, size=0x100, mem_base=0):
    memory = _ci_cpu.behavioural_memory
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
            # we assume thereis a sparse-memory starting at memory area
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
                #print('??', hex(block[0]), hex(block[1]))
