# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:57:50 2024

@author: dcastel1
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
from punxa.single_cycle.singlecycle_processor_proxy_kernel import *
from punxa.instruction_decode import *
from punxa.interactive_commands import *
    

import py4hw    
import py4hw.debug
import py4hw.gui as gui
import zlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

mem_base =  0x00000000
#test_base = 0x80001000

# We maintain a list of (addr, name, size)
mem_trace = []

saved_mem_traces = []

def showMemTraces():
    global saved_mem_traces
    if not(mem_trace in saved_mem_traces):
        saved_mem_traces.append(mem_trace)
        
    for mt in saved_mem_traces:
        showMemTrace(mt)
        
def showMemTrace(mem_trace):
    mem_trace.sort(key=lambda x: x[0])
    
    last_start = 0
    mem_trace2 = []
    last_end = 0
    
    for start, name, size in mem_trace:    
        end = start + size
        h = math.ceil(size // 4)
        
        if (start != last_end):
            # insert a gap
            mem_trace2.append((last_end, '', start-last_end))
            
        mem_trace2.append((start, name, size))
        last_end = start + size

    mem_trace2.append((last_end, '', 1<<8)) # random size
        
    fig, ax = plt.subplots(figsize=(4, 8))
    colors = plt.cm.tab20.colors  # Use a colormap with enough colors
    # Plot each memory segment as a rectangle
    i = 0
    c = 1
    for start, name, size in mem_trace2:
        end = start + size
        if (size == 0):
            continue
        h = math.ceil(size / 8)
        if (h > 16):
            h = 3
        elif (h > 1):
            h = 0.5
            
            
        print(f'{i}: {name}= {start:08X} - {end:08X} - h:{h}')
        
        if (len(name) == 0):
            color = 'lightgray' 
        else:
            color = colors[c]  
            c = (c+1) %  len(colors)
            
        rect = patches.Rectangle((0.2, i), 0.7, h, linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(rect)

        if (len(name) != 0):
            ax.text(-0.1, i, f'{start:08X}', verticalalignment='bottom', fontsize=8, color='black')
            ax.text(0.5, i , f'{name}', verticalalignment='bottom', horizontalalignment='center', fontsize=10, color='white', weight='bold')
        i += h

        
    # Set limits and labels
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_xlim(-0.5, 1)
    ax.set_ylim( 0, i)
    ax.set_xticks([])
    ax.set_yticks([])
    # Add title
    plt.title('Memory Layout')
    # Show plot
    plt.savefig('memtrace.pdf')
    plt.show()


def newMemTraceColumn(cpu):
    global stack_top
    global stack_current
    global stack_bottom
    global mem_trace
    
    # store a copy of the current mem_trace in saved_mem_traces
    saved_mem_traces.append(mem_trace)
    
    # create a copy of the mem_trace removing stack elements below current stack
    cs = cpu.reg[2]
    
    mem_trace2 = []
    for start, name, size in mem_trace:    
        if not(start < cs and start > stack_bottom): 
            mem_trace2.append((start, name, size))

    mem_trace = mem_trace2

    stack_current = cs
    
def myFunctionExit(self, et=0):    
    # et (exit type) can be 0 (function) 1 (M exception) 2 (S exception)
    global stack_top
    global stack_current
    global stack_bottom
    
    if (self.reg[2] > stack_current):
        # We should deallocate all elements below
        newMemTraceColumn(self)

    
    self.old_functionExit(et)

def unknown_syscall(self):
    global stack_top
    global stack_current
    global stack_bottom
    
    syscall = self.reg[17]
    
    if (syscall != 0xFF):
        print('my new unknown syscall', syscall)
        return
    
    print('trace mem')
    addr = self.reg[10]
    name_ptr = self.reg[11]
    size = self.reg[12]
    
    stack_current = self.reg[2]
    
    name = ''

    c = -1
    while (c != 0):    
        c = self.behavioural_memory.readByte(name_ptr)
        if (c != 0):
            name += chr(c)
        name_ptr += 1
    
    mem_trace.append((addr, name, size))
    
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
    port_m = MemoryInterface(hw, 'port_m', mem_width, 20)     # 24	bits = 
    port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
    port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
    port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
    #port_t = MemoryInterface(hw, 'port_t', mem_width, 8)     # 8 bits = 256
    # Memory initialization

    memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

    #memory.reallocArea(0, 1 << 16)

    #test = ISATestCommunication(hw, 'test', mem_width, 8, port_t)


    # Uart initialization
    uart = Uart8250(hw, 'uart', port_u)


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

    cpu = SingleCycleRISCVProxyKernel(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

    cpu.min_clks_for_trace_event = 1000
    cpu.behavioural_memory = memory


    # inject new syscall to trace memory references
    import types
    cpu.syscall_unknown = types.MethodType(unknown_syscall, cpu)
        
    cpu.old_functionExit = cpu.functionExit
    cpu.functionExit = types.MethodType(myFunctionExit, cpu)
        
    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    
    return hw


def prepareTest(test_file):
    global hw
    global stack_top
    global stack_current
    global stack_bottom
    
    hw = buildHw()
    programFile = ex_dir + test_file
    
    memory.reallocArea(0x10000, 0x10000)
    
    loadElf(memory, programFile, 0 ) # 32*4 - 0x10054)    
    loadSymbolsFromElf(cpu,  programFile, mem_base) # 32*4 - 0x10054)

    start_adr = findFunction('_start')

    cpu.pc = start_adr
    
    stack_base = 0x90000
    stack_size = 0x10000
    cpu.reg[2] = mem_base + stack_base + stack_size - 8

    stack_top = mem_base + stack_base + stack_size
    stack_current = cpu.reg[2]
    stack_bottom = mem_base + stack_base 

    memory.reallocArea(stack_base, stack_size)

    cpu.heap_base = 0xA0000
    cpu.heap_size = 0x20000 

    memory.reallocArea(cpu.heap_base, cpu.heap_size)
    
    print('')
    print(f'\tStack base: 0x{stack_base:016X} size: 0x{stack_size:016X}')
    print(f'\tHeap base:  0x{cpu.heap_base:016X} size: 0x{cpu.heap_size:016X}')


def prepare():
    prepareTest('tracemem.elf')
        
def runTest(test_file):
    prepareTest(test_file)
    exit_adr = findFunction('exit')

    
    #run(passAdr, verbose=False)
    run(exit_adr, maxclks=10000, verbose=False)
    #run(0, maxclks=20, verbose=False)

    # print('Test', test_file, end='')

    #if (cpu.pc != passAdr):
    #value = memory.readByte(tohost_adr-mem_base)
    
    #if (value != 1):
    #    raise Exception('Test return value = {}'.format(value))
    #else:
    #    print('Test return value = {}'.format(value))


def runTraceMem():
    prepareTest('tracenen.elf')
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
