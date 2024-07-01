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
from punxa.custom_instruction import *
from punxa.single_cycle.singlecycle_processor_proxy_kernel import *
from punxa.instruction_decode import *
from punxa.interactive_commands import *
    

import py4hw    
import py4hw.debug
import py4hw.gui as gui
import zlib

import RGB2YCbCr

mem_base =  0x00000000
#test_base = 0x80001000

    
cpu = None

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

    
def write_trace(filename=ex_dir + 'newtrace.json'):
    cpu.tracer.write_json(filename)



def executeCustom(self, n):
    #raise Exception(f'Custom {n} not implemented')
    
    ins = self.ins
    
    func3 = (ins >> 12) & 0x7
    func7 = (ins >> 25) & 0x7F
    
    rd = get_bits(ins, 7, 5)   # Y
    rs1 = get_bits(ins, 15, 5) # Cb
    rs2 = get_bits(ins, 20, 5) # Cr
    rs3 = get_bits(ins, 27, 5) # input RGB
    
    print('ins:', hex(ins))
    print('n=', n, 'f3', func3, 'f7', func7)
    
    print('frd = ', rd)
    print('rs1 = ', rs1)
    print('rs2 = ', rs2)
    print('rs3 = ', rs3, '=', hex(self.reg[rs3]))
    
    rgb = self.reg[rs1]
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8) & 0xFF
    b = (rgb) & 0xFF
    
    y = 0.299 * r + 0.587 * g + 0.114 * b;
    cb = 128 + ((-0.16874 * r - 0.33126 * g + 0.5 * b))
    cr = 128 + ((0.5 * r - 0.41869 * g - 0.08131 * b))
                   
    from py4hw.helper import FPNum
    if (func7 == 0):
        self.freg[rd] = self.fpu.sp_box(FPNum(y).convert('sp'))
    elif (func7 == 1):
        self.freg[rd] = self.fpu.sp_box(FPNum(cb).convert('sp'))
    elif (func7 == 2):
        self.freg[rd] = self.fpu.sp_box(FPNum(cr).convert('sp'))
    
    # hw.getSimulator().stop()
    
    yield
    
def executeCustomHW(self, n):
    #raise Exception(f'Custom {n} not implemented')
    
    ins = self.ins
    
    opcode = ins & 0x7F
    func3 = (ins >> 12) & 0x7
    func7 = (ins >> 25) & 0x7F
    
    rd = get_bits(ins, 7, 5)   # Y
    rs1 = get_bits(ins, 15, 5) # Cb
    rs2 = get_bits(ins, 20, 5) # Cr
    rs3 = get_bits(ins, 27, 5) # input RGB
    
    #print('ins:', hex(ins))
    #print('n=', n, 'f3', func3, 'f7', func7)
    
    #print('frd = ', rd)
    #print('rs1 = ', rs1)
    #print('rs2 = ', rs2)
    #print('rs3 = ', rs3, '=', hex(self.reg[rs3]))
    
    #from punxa.single_cycle.singlecycle_processor_proxy_kernel import pr
    self.pr(f'frd{rd} = custom{n}[{func7}](r{rs1})')
    
    self.ci.opcode.prepare(opcode)
    self.ci.func3.prepare(func3)
    self.ci.func7.prepare(func7)
    self.ci.start.prepare(1)
    self.ci.rs1.prepare(self.reg[rs1])
        
    yield
    self.ci.start.prepare(0)
    yield
    self.freg[rd] = self.ci.rd.get()    
        
    #print('done:', self.ci.done.get())
    #print('rd:', hex(self.ci.rd.get())   )
    yield
    
    
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

def buildHw(useHWCI):
    global memory
    global cpu
    global bus

    hw = HWSystem()

    port_c = MemoryInterface(hw, 'port_c', mem_width, 40)
    port_m = MemoryInterface(hw, 'port_m', mem_width, 22)     # 22	bits = 
    port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
    port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
    port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
    #port_t = MemoryInterface(hw, 'port_t', mem_width, 8)     # 8 bits = 256
    # Memory initialization

    memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

    #memory.reallocArea(0, 1 << 16)

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

    cpu = SingleCycleRISCVProxyKernel(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)
    
    
    
    if (useHWCI):
        # Modify the processor to add the custom instruction Hardware
        port_ci = CustomInstructionInterface(hw, 'ci', 64)
        cpu.ci = cpu.addInterfaceSource('ci', port_ci)
        
        RGB2YCbCr.RGB2YCrCr_CustomInstruction(hw, 'rgb2yuv', port_ci)
        
        # Motify the behavioural model to invoke the hardware
        import types
        cpu.executeCustom = types.MethodType(executeCustomHW, cpu)
        
    else:
        import types
        cpu.executeCustom = types.MethodType(executeCustom, cpu)

    cpu.min_clks_for_trace_event = 1000
    cpu.behavioural_memory = memory

    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    
    return hw

def pushString(s):
    memory.writeByte(cpu.reg[2], 0)
    cpu.reg[2] -= 1
    for k in range(len(s)):
        memory.writeByte(cpu.reg[2], ord(s[len(s)-1-k]) )
        cpu.reg[2] -= 1

def pushInt64(v):
    for k in range(8):
        memory.writeByte(cpu.reg[2], (v >> 56) & 0xFF)
        cpu.reg[2] -= 1
        v = v << 8

def pushInt32(v):
    for k in range(4):
        memory.writeByte(cpu.reg[2], (v >> 24) & 0xFF)
        cpu.reg[2] -= 1
        v = v << 8

def prepareTest(test_file, args, useHWCI):
    global hw
    hw = buildHw(useHWCI)
    programFile = ex_dir + test_file
    
    loadElf(memory, programFile, 0 )     
    loadSymbolsFromElf(cpu,  programFile, mem_base) 

    start_adr = findFunction('_start')

    cpu.pc = start_adr
    
    stack_base = 0x90000
    stack_size = 0x10000
    cpu.reg[2] = mem_base + stack_base + stack_size - 8

    memory.reallocArea(stack_base, stack_size)

    cpu.heap_base = 0xA0000
    cpu.heap_size = 0x20000 

    memory.reallocArea(cpu.heap_base, cpu.heap_size)
    
    print('')
    print(f'\tStack base: 0x{stack_base:016X} size: 0x{stack_size:016X}')
    print(f'\tHeap base:  0x{cpu.heap_base:016X} size: 0x{cpu.heap_size:016X}')

    # Now push the arguments to the stack
    args = [programFile] + args
    argc = len(args)
    argsp = [0] * argc

    for i in range(argc):
        param = args[argc-1-i]
        pushString(param)
        argsp[i] = cpu.reg[2] + 1

    pushInt64(0)

    for i in range(argc):
        add = argsp[i]
        pushInt64(add)

    pushInt64(argc)

    cpu.reg[2] += 1
    

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

def prepare(useHWCI):
    args = ['-m', '-o', 'eclair.jpg']
    if (useHWCI):
        args.append('-ci')
    prepareTest('pjpegenc_baseline.elf', args, useHWCI)
    cpu.min_clks_for_trace_event=100

    def dummy_cycle(self, n):
        for i in range(n):
            yield
            
    def new_execute(self):
        ins = self.decoded_ins
        if (ins in ['MUL','MULHU','MULW']):
            # 
            yield from self.dummy_cycle(3)
        elif (ins in ['FADD.S','FADD.D','FSUB.S','FSUB.D', 'FMADD.D', 'FMSUB.D', 'FMUL.S','FMUL.D', 'FNMSUB.D']):
            yield from self.dummy_cycle(5)
        elif (ins in ['DIV', 'DIVU', 'DIVUW', 'DIVW', 'FDIV.S','FDIV.D','FSQRT.D','REM', 'REMU', 'REMW']):
            yield from self.dummy_cycle(20)
        elif (ins in ['ECALL']):
            yield from self.dummy_cycle(100)
            
        yield from self.old_execute()
        
    import types
    cpu.old_execute = cpu.execute
    cpu.execute = types.MethodType(new_execute, cpu)
    cpu.dummy_cycle = types.MethodType(dummy_cycle, cpu)

def run_collect(max_n = math.inf):
    global ins_freq
    global ins_cycles
    global ins_latency
    
    from punxa.csr import CSR_CYCLE
    def new_syscall_exit(self):
        self.stop_collecting = True

    import types
    cpu.syscall_exit = types.MethodType(new_syscall_exit, cpu)

    cpu.stop_collecting = False
    
    ins_freq = {}
    ins_cycles = {}
    
    last_cycle = 0
    n = 0
    while not(cpu.stop_collecting) and (n < max_n):
        step()
        n += 1
        ins = cpu.decoded_ins
        clk = cpu.csr[CSR_CYCLE]
        
        latency = clk - last_cycle
        
        if (ins in ins_freq.keys()):
            ins_freq[ins] += 1
        else:
            ins_freq[ins] = 1
            
        if (ins in ins_cycles.keys()):
            ins_cycles[ins] += latency
        else:
            ins_cycles[ins] = latency
            
        last_cycle = clk
        
    ins_latency = {}
    
    for ins in ins_cycles.keys():
        ins_latency[ins] = ins_cycles[ins] / ins_freq[ins]    

def getHw():
    global hw
    return hw

def getCpu():
    global cpu
    return cpu

def runJpegEnc():
    prepareTest('pjpegenc_baseline.elf', ['-m', '-o', 'eclair.jpg'])
    step(10000000)
    #print()
    #print('Console Output')
    #print('-'*80)
    #console()

if __name__ == "__main__":
    print(sys.argv)

    if (len(sys.argv) > 1):
        if (sys.argv[1] == '-c'):
            eval(sys.argv[2])
            os._exit(0)
        elif (sys.argv[1] == '-trace'):
            prepare()
            exit_adr = findFunction('exit')

            cpu.min_clks_for_trace_event=100
            
            run(exit_adr, maxclks=10000000, verbose=False)
            run(0, maxclks=100, verbose=True)
            console()
            write_trace()
        elif (sys.argv[1] == '-combined-trace'):
            min_clks = 0
            #prepare(False)
            #exit_adr = findFunction('exit')
            #
            #cpu.min_clks_for_trace_event=min_clks 
            #
            #run(exit_adr, maxclks=10000000, verbose=False)
            #run(0, maxclks=100, verbose=True)
            #console()
            #write_trace('trace_normal.json')
            
            prepare(True)
            exit_adr = findFunction('exit')
            
            cpu.min_clks_for_trace_event=min_clks 
            
            run(exit_adr, maxclks=10000000, verbose=False)
            run(0, maxclks=100, verbose=True)
            console()
            write_trace('trace_custom_instruction.json')