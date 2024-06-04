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

def help():
    print('Interactive commands')
    print('  loadProgram - load a program in memory')
    print('  checkpoint  - save the system state in a file')
    print('  restore     - restore the system state from a file')
    print('  run')
    print('  step        - run an instruction step')
    print('  tbreak      - set a temporal breakpoint')
    print('  go          - run until the temporal breakpoint')
    print('  regs        - display the registers of the processor')
    print('  reportCSR   - display the content of CSRs')



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
            if section.name == '.symtab':  # Commonly, the symbol table section is named '.symtab'
                for symbol in section.iter_symbols():
                    if symbol['st_info']['type'] == 'STT_FUNC':
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
