# -*- coding: utf-8 -*-
"""
Created on Sat May 25 15:41:27 2024

@author: dcastel1
"""
from elftools.elf.elffile import ELFFile
import math

_ic_verbose = False

def help():
    print('Interactive commands')
    print('  loadProgram - loads a program in memory')
    print('  checkpoint  - save the system state in a file')
    print('  restore     - restore the system state from a file')
    print('  run')
    print('  step        - run an instruction step')
    print('  tbreak      - set a temporal breakpoint')



def isElf(filepath):
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


tbreak_address = None
_ci_hw = None
_ci_cpu = None

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
