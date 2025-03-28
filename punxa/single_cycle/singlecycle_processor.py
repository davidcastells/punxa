# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:12:41 2022

@author: dcr

Latest Unprivileged:
    https://github.com/riscv/riscv-isa-manual/releases/download/riscv-isa-release-db98c92-2024-12-20/riscv-unprivileged.pdf
    
Latest Privileged Extention Used: 20241101
    https://github.com/riscv/riscv-isa-manual/releases/download/riscv-isa-release-db98c92-2024-12-20/riscv-privileged.pdf
    
Latest Debug Specification Used: 1.0.0-rc4
    https://github.com/riscv/riscv-debug-spec/releases/download/1.0.0-rc4/riscv-debug-specification.pdf
    
"""
import sys
import py4hw

baseDir = '../'

if not(baseDir in sys.path):
    sys.path.append(baseDir)

from ..fpu import *
from ..memory import *
from ..instruction_decode import *
from ..csr import *
from ..tracing import *
from ..processor_exceptions import *
from ..temp_helper import *

MEMORY_OP_LOAD = 1
MEMORY_OP_STORE = 2
MEMORY_OP_EXECUTE = 3
    
def dummy_print(*args, **kargs):
    pass


pr = print

# @todo Move it to py4hw helper functions
def count_leading_zeros(v, w):
    for i in range(w):
        if (v & (1<<(w-1))): return i
        v = v << 1
    return w
        
# @todo Move it to py4hw helper functions
def count_trailing_zeros(v, w):
    for i in range(w):
        if (v & 1): return i
        v = v >> 1
    return w
        
# @todo Move it to py4hw helper functions
def pop_count(v, w):
    c = 0
    for i in range(w):
        if (v & 1): c += 1
        v = v >> 1
    return c

def grev(x, shamt):
    if (shamt & 1): x = ((x & 0x5555555555555555) << 1) | ((x & 0xAAAAAAAAAAAAAAAA) >> 1)
    if (shamt & 2): x = ((x & 0x3333333333333333) << 2) | ((x & 0xCCCCCCCCCCCCCCCC) >> 2)
    if (shamt & 4): x = ((x & 0x0F0F0F0F0F0F0F0F) << 4) | ((x & 0xF0F0F0F0F0F0F0F0) >> 4)
    if (shamt & 8): x = ((x & 0x00FF00FF00FF00FF) << 8) | ((x & 0xFF00FF00FF00FF00) >> 8)
    if (shamt & 16): x = ((x & 0x0000FFFF0000FFFF) << 16) | ((x & 0xFFFF0000FFFF0000) >> 16)
    if (shamt & 32): x = ((x & 0x00000000FFFFFFFF) << 32) | ((x & 0xFFFFFFFF00000000) >> 32)
    return x

def gorc(x,  shamt ):
    if (shamt & 1): x |= ((x & 0x5555555555555555) << 1) | ((x & 0xAAAAAAAAAAAAAAAA) >> 1);
    if (shamt & 2): x |= ((x & 0x3333333333333333) << 2) | ((x & 0xCCCCCCCCCCCCCCCC) >> 2);
    if (shamt & 4): x |= ((x & 0x0F0F0F0F0F0F0F0F) << 4) | ((x & 0xF0F0F0F0F0F0F0F0) >> 4);
    if (shamt & 8): x |= ((x & 0x00FF00FF00FF00FF) << 8) | ((x & 0xFF00FF00FF00FF00) >> 8);
    if (shamt & 16): x |= ((x & 0x0000FFFF0000FFFF) << 16) | ((x & 0xFFFF0000FFFF0000) >> 16);
    if (shamt & 32): x |= ((x & 0x00000000FFFFFFFF) << 32) | ((x & 0xFFFFFFFF00000000) >> 32);
    return x
     
def clmul(a, b):
    x = 0
    for i in range(64):
        if (b >> i) & 1:
            x = x ^ (a << i)
    return x

def clmulr(a, b):
    x = 0
    for i in range(64):
        if (b >> i) & 1:
            x = x ^ (a >> (64-1-i))
    return x

def div_tz(v1, v2):
    # integer division with rounding toward zero
    if (sign(v1) != sign(v2)):
        v = -( abs(v1) // abs(v2) )
    else:
        v = ( v1 // v2 )
    return v


class SingleCycleRISCV(py4hw.Logic):
    
    def __init__(self, parent, name:str, memory:MemoryInterface, 
                 int_soft_machine, int_timer_machine, ext_int_targets, resetAddress):

        super().__init__(parent, name)
        
        self.mem = self.addInterfaceSource('memory', memory)

        self.int_soft_machine = self.addIn('int_soft_machine', int_soft_machine)
        self.int_timer_machine = self.addIn('int_timer_machine', int_timer_machine)
        self.int_ext_machine = self.addIn('int_ext_machine', ext_int_targets[0])
        self.int_ext_supervisor = self.addIn('int_ext_supervisor', ext_int_targets[1])
        
        self.mem_width = memory.read_data.getWidth()
        print('MEM WIDTH', self.mem_width)
        
        self.v_mem_address = 0
        self.v_mem_write_data = 0
        self.v_mem_read_data = 0
        self.v_mem_read = 0
        self.v_mem_write = 0
        self.v_mem_be = 0

        self.pc = resetAddress
        self.reg = [0] * 32     # register file
        self.freg = [0] * 32    # floating-point register file
        self.csr = [0] * 4096
        
        self.implemented_csrs = {}  # dictionary <address> -> <name>
        self.stack = []             # list of addresses
        
        self.per_thread_stack = {}

        self.tracer = Tracer()
        self.enable_tracing = True
        self.min_clks_for_trace_event = 0
        self.ignore_unknown_functions = True
        
        self.initStaticCSRs()
        self.initDynamicCSRs()
        
        self.stopOnExceptions = False   
        self.funcs = {}
        self.tlb = {}
        
        # Instruction and Data Caches (indexed by address)
        self.icache = {}
        self.dcache = {}
        
        self.fpu = FPU(self)
        
        # self.setCSR(CSR_MSTATUS, 3 << CSR_MSTATUS_FS_POS)   # Enable FPU by default
        
        self.reserved_address_start = -1
        self.reserved_address_stop = -1
        self.reserved_accessed = False
        
        # debugging
        self.debug_pc = False
        self.debug_vm = False
        self.debug_insret = False
        
        self.isa = 64 # @todo we should change this for XLEN
        self.XLEN = self.isa
        
        self.debugTrigger = False 
        self.csr_write_verbose = False

        self.co = self.run()
        
    def setVerbose(self, verbose):
        global pr
        global print
        global dummy_print
        
        if (verbose):
            pr = print
        else:
            pr = dummy_print
            
        # we also assign the function to the object
        self.pr = pr
            
    def run(self):
        yield
        
        while (True):
            try:
                yield from self.fetchIns()
                
                self.decode()
                yield from self.execute()
                
                if (self.should_jump):
                    self.pc = self.jmp_address
                else:
                    if is_compact_ins(self.ins):
                        self.pc += 2
                    else:
                        self.pc += 4

            except ProcessorInterrupt as e:
                emsg = f'Interrupt: {e.msg} code: {e.code} tval: 0x{e.tval:X}'
                epc = self.pc
                pr('\n\t', emsg, end=' ' )
                
                priv = self.csr[CSR_PRIVLEVEL]
                

                # Interrupts are always handled by machine mode, unless they are delegated
                # to lower modes (see priv-spec section 3.1.8)
                
                mideleg = self.csr[CSR_MIDELEG] # mideleg
                
                entertype = 1 # machine mode exception
                
                if (get_bit(mideleg, e.code)):
                    # this should be delegated to supervisor mode
                    vec = self.csr[CSR_STVEC] # stvec
                    self.csr[CSR_STVAL] = e.tval
                    assert(priv <= CSR_PRIVLEVEL_SUPERVISOR)
                    #self.csr[CSR_MSTATUS] |= (priv&1 << 8) 
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPP_POS, 1, priv&1 ) # set previous mode in SPP
                    self.csr[CSR_SEPC] = self.pc # sepc
                    self.csr[CSR_SCAUSE] = (1 << (self.XLEN -1))  | e.code  # scause

                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPIE_POS, 1, getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SIE_POS, 1))
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SIE_POS, 1, 0)
                    vecname = self.implemented_csrs[0x105]
                    self.csr[CSR_PRIVLEVEL] = 1
                    entertype = 2 # supervisor mode exception

                else:
                    # this is executed in machine mode    
                    vec = self.csr[CSR_MTVEC] # mtvec
                    self.csr[CSR_MTVAL] = e.tval
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPP_POS, 2, priv ) # set previous mode in SPP
                    self.csr[CSR_MEPC] = self.pc # mepc
                    self.csr[CSR_MCAUSE] = (1 << (self.XLEN -1))  | e.code  
                    
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPIE_POS, 1, getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MIE_POS, 1))
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MIE_POS, 1, 0)

                    vecname = self.implemented_csrs[0x305]
                    self.csr[CSR_PRIVLEVEL] = 3
                    
                addr = vec & 0xFFFFFFFFFFFFFFFC
                
                if ((vec & 3) == 0):
                    pr('jumping to {}'.format(vecname))
                    self.pc = addr                    
                elif ((vec & 3) == 1):
                    self.pc = addr + e.code * 4
                else:
                    raise Exception('unhandled exception cause')                    
                
                if (self.enable_tracing):
                    self.tracer.instant((emsg, epc, self.csr[CSR_CYCLE]))
                    
                # @todo shouldn't we check is this is +4 or +2 ?
                self.functionEnter(self.pc, epc+4, entertype, False)

                if (self.stopOnExceptions):
               	   # always stop the simulation on exceptions
               	   self.parent.getSimulator().stop()
               	               
            except ProcessorException as e:
                priv = self.csr[CSR_PRIVLEVEL]
                emsg = f'Exception: {e.msg} code: {e.code} tval: 0x{e.tval:X} priv:{priv}'
                epc = self.pc
                pr('\n\t', emsg, end=' ' )
                
                
                # Exceptions are always handled by machine mode, unless they are delegated
                # to lower modes (see priv-spec section 3.1.8)
                
                #if (priv == CSR_PRIVLEVEL_MACHINE): # machine
                #    self.csr[CSR_MSTATUS] |= (3 << 11) # set M-Mode as previous mode in MPP
                #elif (priv == CSR_PRIVLEVEL_SUPERVISOR): # supervisor
                #    self.csr[CSR_MSTATUS] |= (1 << 11) # set M-Mode as previous mode in MPP

                medeleg = self.csr[0x302] # medeleg
                
                entertype = 1 # machine mode exception
                
                if (get_bit(medeleg, e.code) ):
                    # this should be delegated to supervisor mode
                    vec = self.csr[CSR_STVEC] # stvec
                    self.csr[CSR_STVAL] = e.tval
                    assert(priv <= CSR_PRIVLEVEL_SUPERVISOR)
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPP_POS, 1, priv&1 ) # set previous mode in SPP
                    self.csr[CSR_SEPC] = self.pc # sepc
                    self.csr[CSR_SCAUSE] = e.code  # scause
                    
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPIE_POS, 1, getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SIE_POS, 1))
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SIE_POS, 1, 0)
                    vecname = self.implemented_csrs[0x105]
                    self.csr[CSR_PRIVLEVEL] = 1
                    entertype = 2 # supervisor mode exception

                else:
                    # this is executed in machine mode    
                    vec = self.csr[CSR_MTVEC] # mtvec
                    self.csr[CSR_MTVAL] = e.tval
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPP_POS, 2, priv ) # set previous mode in SPP
                    self.csr[CSR_MEPC] = self.pc # mepc
                    self.csr[CSR_MCAUSE] = e.code  
                    
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPIE_POS, 1, getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MIE_POS, 1))
                    setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MIE_POS, 1, 0)
                    vecname = self.implemented_csrs[0x305]
                    self.csr[CSR_PRIVLEVEL] = 3
                    
                addr = vec & 0xFFFFFFFFFFFFFFFC
                
                if ((vec & 3) == 0):
                    pr('jumping to {}'.format(vecname))
                    self.pc = addr                    
                elif ((vec & 3) == 1):
                    #pr('vectorized jump to entry {}'.format(e.code))
                    #self.pc = addr + e.code * 4
                    pr('VECTORED mode is irrelevant for exceptions jumping to {}'.format(vecname))
                    self.pc = addr                    
                else:
                    raise Exception('unhandled exception cause')                    
                
                if (self.enable_tracing):
                    self.tracer.instant((emsg, epc, self.csr[CSR_CYCLE]))
                    
                # @todo shouldn't we check is this is +4 or +2 ?
                self.functionEnter(self.pc, epc+4, entertype, False)

                if (self.stopOnExceptions):
               	   # always stop the simulation on exceptions
               	   self.parent.getSimulator().stop()

    def functionEnter(self, f, ra, et, jmp):
        # et (exit type) can be 0 (function) 1 (M exception) 2 (S exception)
        # jmp is True if the enter to the function was done with a jump, which
        # should provoke to pop the parent from the stack when exiting

        #if (jmp):
        #    if (len(self.stack) > 1) and (self.stack[-1][0] == f):               
        #        return
        
        pair = (f, self.csr[CSR_CYCLE], jmp, ra, et)
        self.stack.append(pair)
        
        thread = self.reg[4]
        
        if not(thread in self.per_thread_stack.keys()):
            self.per_thread_stack[thread] = []
            
        self.per_thread_stack[thread].append(pair)

        if (not(self.enable_tracing)):
            return
        

        pairn = (f, self.csr[CSR_CYCLE], jmp)        
        self.tracer.start(pairn)
                
    def functionExit(self, et=0):
        # et (exit type) can be 0 (function) 1 (M exception) 2 (S exception)

        thread = self.reg[4]
        
        if not(thread in self.per_thread_stack.keys()):
            self.per_thread_stack[thread] = []

        if not(len(self.per_thread_stack[thread]) == 0):
            self.per_thread_stack[thread].pop()


        if (len(self.stack) == 0):
            return
    		
        finfo = self.stack.pop()

        
        f = finfo[0]
        t0 = finfo[1]
        jmp = finfo[2]
        ra = finfo[3]
        etsv = finfo[4] # saved enter type
        
        if (et == 0):
            ets = 'return address register'
            rap = self.reg[1] # ra from processor
        elif (et == 1):
            ets = 'mepc'
            rap = self.csr[CSR_MEPC]
        elif (et == 2):
            ets = 'sepc'
            rap = self.csr[CSR_SEPC]
            
        
        if not(jmp) and (ra != rap):
            if (etsv != et):
                if (et == 2) and (etsv == 0):
                    print(f'WARNING! Entering Supervisor Mode from function {f}')
            else:
                fn = f
                if (fn in self.funcs.keys()):
                    fn = self.funcs[f]
                else:
                    fn = f'{f:016X}'

                print(f'WARNING! function exit address {ra:016X} does not match {ets} {rap:016X} in {fn}' )

        if (self.enable_tracing):
    
            fn = f
            if (fn in self.funcs.keys()):
                fn = self.funcs[f]

            if (isinstance(fn, int) and self.ignore_unknown_functions):
                fn = None

            tf = self.csr[CSR_CYCLE]
            dur = tf - t0
            
            if (dur < self.min_clks_for_trace_event) or (fn is None):
                self.tracer.ignore(fn)
            else:            
                self.tracer.complete((fn, t0, tf))
        
        if (jmp):
            # repeat exit
            self.functionExit()

    def fetchIns(self):
        self.updateMIP() # force to update the MIP register
            
        # Machine Mode exceptions should always be checked
        if (self.csr[CSR_MSTATUS] & CSR_MSTATUS_MIE_MASK):
            # check interrupts
            if ((self.csr[CSR_MIE] & self.csr[CSR_MIP]) != 0):
                if (self.csr[CSR_MIE] & CSR_MIE_MEIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_MEIP_MASK): raise MachineExternalInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_SEIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_SEIP_MASK): raise SupervisorExternalInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_UEIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_UEIP_MASK): raise UserExternalInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_MTIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_MTIP_MASK): raise MachineTimerInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_STIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_STIP_MASK): raise SupervisorTimerInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_UTIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_UTIP_MASK): raise UserTimerInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_MSIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_MSIP_MASK): raise MachineSoftwareInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_SSIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_SSIP_MASK): raise SupervisorSoftwareInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_USIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_USIP_MASK): raise UserSoftwareInterrupt()
                
                print('WARNING: Should handle interrupt mip={:016X}'.format(self.csr[CSR_MIP]))
            
        # Supervisor exceptions should only be checked when running in supervisor or user mode
        if (self.csr[CSR_PRIVLEVEL] <= CSR_PRIVLEVEL_SUPERVISOR) and (self.csr[CSR_MSTATUS] & CSR_MSTATUS_SIE_MASK):
            # check interrupts
            if ((self.csr[CSR_MIE] & self.csr[CSR_MIP]) != 0): # SIE and MIE are mirrors 
                #if (self.csr[CSR_MIE] & CSR_MIE_MEIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_MEIP_MASK): raise MachineExternalInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_SEIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_SEIP_MASK): raise SupervisorExternalInterrupt()
                #if (self.csr[CSR_MIE] & CSR_MIE_UEIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_UEIP_MASK): raise UserExternalInterrupt()
                #if (self.csr[CSR_MIE] & CSR_MIE_MTIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_MTIP_MASK): raise MachineTimerInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_STIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_STIP_MASK): raise SupervisorTimerInterrupt()
                #if (self.csr[CSR_MIE] & CSR_MIE_UTIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_UTIP_MASK): raise UserTimerInterrupt()
                #if (self.csr[CSR_MIE] & CSR_MIE_MSIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_MSIP_MASK): raise MachineSoftwareInterrupt()
                if (self.csr[CSR_MIE] & CSR_MIE_SSIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_SSIP_MASK): raise SupervisorSoftwareInterrupt()
                #if (self.csr[CSR_MIE] & CSR_MIE_USIE_MASK) and (self.csr[CSR_MIP] & CSR_MIP_USIP_MASK): raise UserSoftwareInterrupt()
                
                print('WARNING: Should handle interrupt mip={:016X}'.format(self.csr[CSR_MIP]))
                
        if (self.pc in self.funcs.keys()):
            pr(self.funcs[self.pc], ':')
            
        if ((self.pc % 2) != 0):
            raise InstructionAddressMisaligned(tval=self.pc)
            #raise Exception('pc is not multiple of 2!', self.pc)
            
        if (self.debug_pc):
            print(f'FETCH {self.pc:016X}')

        if (self.debug_insret):
            print(self.csr[CSR_INSTRET], end = ' - ')
        
        try:
            if (self.debug_vm): print(f'load to execute: {self.pc:016X}') 
            self.ins = yield from self.virtualMemoryLoad(self.pc, 32//8, MEMORY_OP_EXECUTE)
        except InstructionPageFault as e:
            if (self.debug_vm): print(f'Instruction Page Fault') 
            #raise LoadPageFault(e.msg, e.tval)
            raise e
        except LoadPageFault as e:
            if (self.debug_vm): print(f'Load Page Fault') 
            raise e
        except ProcessorException as e:
            if (self.debug_vm): print(f'Other Exception') 
            raise InstructionAccessFault(f'could not load instruction: {e.msg}', tval=self.pc)

    def getPTEFromPageTables(self, pageTable, address, level):
        # returns the level and the PTE of the address by page walking
        # this is the fundamental function to do address tanslation (VA -> PA)
        vpn=[0,0,0]
        off=[0,0,0]
        offmask=[0,0,0]
        
        # check sign extension
        if (signExtend(address, 39, 64) != address):
            raise LoadPageFault('high vpn bits not correctly sign extended', address)
        
        vpn[2] = (address >> 30) & ((1<<9)-1)
        vpn[1] = (address >> 21) & ((1<<9)-1)
        vpn[0] = (address >> 12) & ((1<<9)-1)
        offmask[2] = ((1<<30)-1)
        offmask[1] = ((1<<21)-1)
        offmask[0] = ((1<<12)-1)
        off[2] = (address) & offmask[2]
        off[1] = (address) & offmask[1] 
        off[0] = (address) & offmask[0]
            
        pteaddr = pageTable + vpn[level]*8
        
        if (self.debug_vm): print(f'Loading PTE from {pteaddr:016X}')
        #pr('va: {:016X} vpn2: {} vpn1: {} vpn0: {}'.format(address, vpn[2], vpn[1], vpn[0]))
        #pr('load pte: {:016X} level:{} index:{}'.format(pageTable + vpn[level]*8, level, vpn[level]))
        pte = yield from self.memoryLoad64(pteaddr, 64//8)

        N = (pte >> 63) & 1
        ppn2 = (pte >> 28) & ((1<<26)-1)
        ppn1 = (pte >> 19) & ((1<<9)-1)
        ppn0 = (pte >> 10) & ((1<<9)-1)
        ppn = [ppn0, ppn1, ppn2]
        X = (pte >> 3) & 1
        W = (pte >> 2) & 1
        R = (pte >> 1) & 1
        valid = pte & 1

        # if not(valid): raise LoadPageFault('invalid PTE', address)

        if (valid) and (X == 0 and R == 0):
            # this is a pointer to the next level, page walk
            phy = (ppn2 << 30 | ppn1 << 21 | ppn0 << 12) 
            level, pte = yield from self.getPTEFromPageTables(phy, address, level-1)
            return level, pte
            
        else:
            if (N):
                # NAPOT, we have to substitute the lower bits 
                assert(ppn[level] & 0x8)
                ppnmask2 = (((1<<26)-1) >> 4) << (4 + 28)
                ppnmask1 = (((1<<9)-1) >> 4) << (4 + 19)
                ppnmask0 = (((1<<9)-1) >> 4) << (4 + 10)
                ppnmask = [ppnmask0, ppnmask1, ppnmask2]
                ppnoff2 = 28
                ppnoff1 = 19
                ppnoff0 = 10
                ppnoff = [ppnoff0, ppnoff1, ppnoff2]
                return level, (pte & ppnmask[level]) | ((vpn[level] & ((1<<4)-1)) << ppnoff[level])
                
            return level, pte
        
    def getPhysicalAddressFromPTE(self,  address, level, pte, memory_op):
        priv = self.csr[0xfff]

        offmask=[0,0,0]
        off=[0,0,0]

        offmask[2] = ((1<<30)-1)
        offmask[1] = ((1<<21)-1)
        offmask[0] = ((1<<12)-1)
        off[2] = (address) & offmask[2]
        off[1] = (address) & offmask[1] 
        off[0] = (address) & offmask[0]
        N = (pte >> 63) & 1
        ppn2 = (pte >> 28) & ((1<<26)-1)
        ppn1 = (pte >> 19) & ((1<<9)-1)
        ppn0 = (pte >> 10) & ((1<<9)-1)
        
        #accum_ppn2 = (pte >> 28) & ((1<<26)-1)
        #accum_ppn1 = (pte >> 19) & ((1<<(26+9))-1)
        #accum_ppn0 = (pte >> 10) & ((1<<(26+9+9))-1)
        #acum_ppn = [accum_ppn0, accum_ppn1, accum_ppn2]
        #ppn_pos = [12,21,30]
                
        reserved = (pte >> 54) & ((1<<7)-1)
        rsw = (pte >> 8) & ((1<<2)-1)
        D = (pte >> 7) & 1
        A = (pte >> 6) & 1
        G = (pte >> 5) & 1
        U = (pte >> 4) & 1
        X = (pte >> 3) & 1
        W = (pte >> 2) & 1
        R = (pte >> 1) & 1
        valid = pte & 1
        
        mxr = getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MXR_POS, 1)
        sum = getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SUM_POS, 1)
        opX = (memory_op == MEMORY_OP_EXECUTE)
        opL = (memory_op == MEMORY_OP_LOAD)
        opS = (memory_op == MEMORY_OP_STORE)
        
        if (self.debug_vm):
            print(f'PTE level {level} ppn2: {ppn2:03X} ppn1: {ppn1:03X} ppn0: {ppn0:03X}')
            
        #pr('pte: {:016X} valid: {}'.format(pte, valid))
        
        # Check PTE bits
        if (opX):
            if (valid == 0):
                raise InstructionPageFault('PTE @ level {} not valid trying to access va:{:016X}'.format(level, address), address)
            if (A == 0):
                raise InstructionPageFault('Access bit not set', address)    
            if (X == 0):
                raise InstructionPageFault('Executable bit not set', address)    
            if (reserved != 0):
                raise LoadPageFault('Reserved bits not zero', address)                
                
        if (opL):
            if (valid == 0):
                raise LoadPageFault('PTE @ level {} not valid trying to access va:{:016X}'.format(level, address), address)
            if (A == 0):
                raise LoadPageFault('Access bit not set', address)
            if (R == 0 and not(mxr and X)):
                raise LoadPageFault('Read bit not set', address)
            if (reserved != 0):
                raise LoadPageFault('Reserved bits not zero', address)
                
        if (opS):
            if (D == 0):
                raise StoreAMOPageFault('Dirty bit not set', address)
            if (W == 0):
                raise StoreAMOPageFault('Write bit not set', address)
        
            
        if (priv == CSR_PRIVLEVEL_USER) and not(U):
            # User mode can only access User pages
            if (opL):
                raise LoadPageFault(f'PTE not User accessible pte:{pte:016X} R (U:{U})', address)
            else:
                raise InstructionPageFault(f'PTE not User accessible pte:{pte:016X} X (U:{U})', address)

        if (priv != CSR_PRIVLEVEL_USER) and U and not(sum and (opL)):
            # Non user modes cannot access User pages
            if (opL):
                raise LoadPageFault(f'PTE is restricted to User pte:{pte:016X} R (U:{U})', address)
            else:
                raise InstructionPageFault(f'PTE is restricted to User pte:{pte:016X} X (U:{U})', address)

            
        
        if (level == 2) and ((ppn1 != 0) or (ppn0 != 0)):
            if (opL):
                raise LoadPageFault('Lower PPN bits not zero', address)
            elif (opX):
                raise InstructionPageFault('Lower PPN bits not zero', address)
            else:
                raise StoreAMOPageFault('Lower PPN bits not zero', address)
        
        #phy = accum_ppn[level] << ppn_pos[level] 
        phy = (ppn2 << 30 | ppn1 << 21 | ppn0 << 12) 
        
        #phy +=  off[level]
        #pr('VMA: {:016X} PHY: {:016X}'.format(address, phy))
        return phy , offmask[level], off[level]

    def getPmaskFromPTE(self,  address, level, pte, memory_op):
        offmask=[0,0,0]

        offmask[2] = ((1<<30)-1)
        offmask[1] = ((1<<21)-1)
        offmask[0] = ((1<<12)-1)
        
        return  offmask[level]
        
    def getPhysicalAddressFromTLB(self, address, memory_op):
        # returns the base and mask
        offmask=[0,0,0]
        offmask[2] = ((1<<30)-1)
        offmask[1] = ((1<<21)-1)
        offmask[0] = ((1<<12)-1)

        if (self.debug_vm):
            import traceback
            print('Traceback:', traceback.format_stack())
            
        for vbase in self.tlb.keys():
            if (self.debug_vm): print(f'Checking TLB vbase: {vbase:016X}')
            level, pte = self.tlb[vbase]
            #base, pmask , _off = self.getPhysicalAddressFromPTE(address, level, pte, memory_op)
            pmask = self.getPmaskFromPTE(address, level, pte, memory_op)
            
            basemask = ((1<<64)-1)-offmask[level]
            add_vbase = address & basemask
            
            if (pmask == offmask[level] and add_vbase == vbase):
                # if the masks are the same, we have a hit
                if (self.debug_vm): print(f'Get PA from PTE address: {address:016X} pte: {pte:016X} mem op: {memory_op}')
                base, pmask , _off = self.getPhysicalAddressFromPTE(address, level, pte, memory_op)
            
                return base , pmask
        
        raise TLBMiss()
        
    def getPhysicalAddress(self, address, memory_op):
        # returns the physical address and a flag if virtual address was translated
        priv = self.csr[0xfff]
        satp = self.csr[CSR_SATP] # satp
        mpvr = self.csr[CSR_MSTATUS] & CSR_MSTATUS_MPRV_MASK
        mpp = getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPP_POS, 2)
        translated = False

        if (priv != CSR_PRIVLEVEL_MACHINE) or (priv == CSR_PRIVLEVEL_MACHINE and (memory_op != MEMORY_OP_EXECUTE) 
                                               and (mpvr != 0) and (mpp < CSR_PRIVLEVEL_MACHINE)):
            if (satp != 0): 
                try:
                    # First, try to see if we already have the address in the TLB
                    va = address
                    base, offmask = self.getPhysicalAddressFromTLB(address, memory_op)
                    address = base + (address & offmask)
                    
                    if (self.debug_vm): print(f'VM VA:{va:016X} PA:{address:016X}')
                except TLBMiss:
                    if (self.debug_vm): print('TLB miss')
                    #mode = (satp >> 60) & ((1<<4)-1)
                    #smode = ['Base', '','','','','','','','Sv39','Sv48','Sv57','Sv64'][mode]
                    #asid = (satp >> 44) & ((1<<16)-1)
                    root = (satp & ((1<<44)-1)) << 12
                    
                    if (self.debug_vm): print(f'ROOT PA:{root:016X}')
                    
                    level, pte = yield from self.getPTEFromPageTables(root, address, 2)

                    if (self.debug_vm): print(f'VA:{address:016X} pte:{pte:016X} level:{level}')
                    base, offmask, off = self.getPhysicalAddressFromPTE(address, level, pte, memory_op)
                    
                    vbasemask = ((1<<64)-1) - offmask
                    base = base & vbasemask
                    vbase = address & vbasemask
                    
                    if (self.debug_vm): print(f'tranlation VA: {address:016X} PA: {vbase:X} + {off:X} = {base+off:016X} (level:{level})')
                    
                    self.tlb[vbase] = (level, pte)
                    #print('ADDING TLB ENTRY - VBASE:{:016X} PBASE:{:016X} OFF:{:016X}'.format(vbase, base, offmask))
                    address = base + off
                    
                    translated = True
        
        return address, translated
            
    def virtualMemoryLoad(self, address, b, memory_op=MEMORY_OP_LOAD):
        self.checkReservedAddress(address, b)
        
        if (self.debugTrigger):
            #match = (self.csr[CSR_TDATA2] >= address) and (self.csr[CSR_TDATA2] <= (address+b))
            match = (self.csr[CSR_TDATA2] == address) 
            if (memory_op == MEMORY_OP_EXECUTE) and (self.csr[CSR_TDATA1] & CSR_TDATA1_EXECUTE_MASK) and (match): raise Breakpoint()
            if (memory_op == MEMORY_OP_LOAD) and (self.csr[CSR_TDATA1] & CSR_TDATA1_LOAD_MASK) and (match): raise Breakpoint()

        pa, isVa  = yield from self.getPhysicalAddress(address, memory_op)    
        
        if (isVa):
            # Any error should be treated as PageFault
            try:
                if (self.mem_width == 32):
                    value = yield from self.memoryLoad32(pa, b, memory_op)
                elif (self.mem_width == 64):
                    value = yield from self.memoryLoad64(pa, b, memory_op)
                else:
                    raise Exception()
                return value
            except:
                raise LoadPageFault('Invalid memory access of translated VA')
                #if (memory_op == MEMORY_OP_LOAD): raise LoadPageFault()
                #if (memory_op == MEMORY_OP_EXECUTE): raise InstructionPageFault()
                #raise Exception()

        if (self.mem_width == 32):
            value = yield from self.memoryLoad32(pa, b, memory_op)
        elif (self.mem_width == 64):
            value = yield from self.memoryLoad64(pa, b, memory_op)
        else:
            raise Exception()
        return value

    def virtualMemoryWrite(self, va, b, v):
        self.checkReservedAddress(va, b)
        
        if (self.debugTrigger):
            if (self.csr[CSR_TDATA1] & CSR_TDATA1_STORE_MASK) and (va == self.csr[CSR_TDATA2]): raise Breakpoint()
            
        pa, isVa = yield from self.getPhysicalAddress(va, MEMORY_OP_STORE)
        #print('\nWR va: {:016X} -> pa: {:016X}'.format(va,pa)) 
        if (self.mem_width == 32):
            yield from self.memoryWrite32(pa, b, v)
        elif (self.mem_width == 64):
            yield from self.memoryWrite64(pa, b, v)
        else:
            raise Exception()
            
        
    def memoryLoad32(self, address, b, memory_op=MEMORY_OP_LOAD):
        #if (address < 0x80000000 or address >= 0x80400000 ):
        #    print('Invalid read access to : {:016X}'.format(address))
        #    self.parent.getSimulator().stop()
            
        #print('mem load ', address, b)
        if (b == 4):
            # 32 bits memory access
            self.v_mem_address = address
            self.v_mem_read = 1
            self.v_mem_write = 0
            self.v_mem_be = 0xF
                    
            yield
            yield
            yield
            self.v_mem_read = 0
            value = self.v_mem_read_data
        elif (b == 8):
            # 64 bits memory access
            low = yield from self.memoryLoad32(address, 4)
            high = yield from self.memoryLoad32(address+4, 4)
            value = high << 32 | low
        elif (b == 2):
            # @todo we could do better
            # 16 bits memory access
            low = yield from self.memoryLoad32(address, 1)
            high = yield from self.memoryLoad32(address+1, 1)
            value = high << 8 | low
        elif (b == 1):
            aligned_address = address & 0xFFFFFFFFFFFFFFFC
            aligned_bit = address & 0x3
            value = yield from self.memoryLoad32(aligned_address, 4)
            value = (value >> (aligned_bit*8)) & 0xFF            
        else:
            raise Exception('unsupported memory load size {}'.format(b))
 
        if (self.v_mem_resp == 1):
            if (memory_op == MEMORY_OP_EXECUTE):
                raise InstructionAccessFault('Failed to load physical memory', address)
            else:
                raise LoadAccessFault('Failed to load physical memory', address) # StoreAMOPageFault()            
            
        return value
    
    def memoryWrite32(self, address, b, v):
            
        if (b == 4):
            if ((address & 3) != 0):
                # Unaligned memory write
                print('WARNING: Unaligned memory write')
                for i in range(4):
                    b = (v >> (i*8)) & 0xFF
                    yield from self.memoryWrite32(address+1, 1, b)
                
            else:
                # 32 bits memory access
                self.v_mem_address = address
                self.v_mem_read = 0
                self.v_mem_write = 1
                self.v_mem_be = 0xF
                self.v_mem_write_data = v                    
                yield
                self.v_mem_write = 0
                yield
                yield
        elif (b == 8):
            low = v & 0xFFFFFFFF
            high = (v >> 32)
            yield from self.memoryWrite32(address, 4, low)
            yield from self.memoryWrite32(address+4, 4, high)
        elif (b == 2):
            # @todo by now do 2 writes , this should be better handled
            low = v & 0xFF
            high = (v >> 8) & 0xFF
            yield from self.memoryWrite32(address, 1, low)
            yield from self.memoryWrite32(address+1, 1 , high)
        elif (b == 1):
            self.v_mem_address = address & 0xFFFFFFFFFFFFFFFC
            self.v_mem_read = 0
            self.v_mem_write = 1
            self.v_mem_be = 1 << (address & 0x3)
            self.v_mem_write_data = v << ((address & 0x3) * 8)
            yield
            self.v_mem_write = 0
            yield
            yield
        else:
            raise Exception('unsupported memory store size {}'.format(b))
            
        if (self.v_mem_resp == 1):
            raise StoreAMOPageFault('Failed to load physical memory', address)
            
    def memoryLoad64(self, address, b,  memory_op=MEMORY_OP_LOAD):
        
        if (memory_op == MEMORY_OP_LOAD):
            if (address in self.dcache.keys()):
                value = self.dcache[address]
                return value & ((1 << (8*b))-1)
        
        #if (address < 0x80000000 or address >= 0x80400000 ):
        #    print('Invalid read access to : {:016X}'.format(address))
        #    self.parent.getSimulator().stop()
            
        #print('mem load ', address, b)
        
        # 64 bits memory access, ignore alignment
        self.v_mem_address = address
        self.v_mem_read = 1
        self.v_mem_write = 0
        self.v_mem_be = ((1 << b)-1)
                
        yield
        yield
        yield
        self.v_mem_read = 0
        value = self.v_mem_read_data & ((1 << (8*b))-1)

        if (self.v_mem_resp == 1):
            if (memory_op == MEMORY_OP_EXECUTE):
                raise InstructionAccessFault('Failed to load physical memory', address)
            else:
                raise LoadAccessFault('Failed to load physical memory', address) # StoreAMOPageFault()
            
        return value
    
    def memoryWrite64(self, address, b, v):            
        self.v_mem_address = address
        self.v_mem_read = 0
        self.v_mem_write = 1
        self.v_mem_be = ((1 << b)-1)                
        self.v_mem_write_data = v                    
        yield
        self.v_mem_write = 0
        yield
        yield
    
        if (self.v_mem_resp == 1):
            raise StoreAMOAccessFault('Failed to store physical memory', address)
    
    def decode(self):
        ins = self.ins
        self.decoded_ins = ins_to_str(self.ins, 64)
        priv = self.csr[0xFFF]
        priv_s = ['U','S','-','M'][priv]
        
        if (is_compact_ins(ins)):
            ins = (ins & 0xFFFF)
            self.ins = ins
            pr('{} {:08X}: {:04X}         {} '.format(priv_s, self.pc , ins,  self.decoded_ins), end='' )
        else:
            pr('{} {:08X}: {:08X}     {} '.format(priv_s, self.pc , ins,  self.decoded_ins), end='' )
        
    def getPhysicalAddressQuick(self, address, memory_op=MEMORY_OP_LOAD):
        # Only used for formating output
        priv = self.csr[0xfff] # privilege
        satp = self.csr[0x180] # satp

        if (priv != 3):
            if (satp != 0): 
                try:
                    base, offmask = self.getPhysicalAddressFromTLB(address, memory_op)
                    address = base + (address & offmask)
                    return address
                #except TLBMiss:
                except: # any exception
                    return address
        
        return address
        
    def addressFmt(self, address):
        phy_address = self.getPhysicalAddressQuick(address)
        
        if (phy_address in self.funcs.keys()):
            return '{:X} <{}>'.format(phy_address, self.funcs[phy_address])
            
        return '{:016X}'.format(address)
        
    
    
    def execute(self):
        op = self.decoded_ins
        self.should_jump = False
        self.jmp_address = 0
        
        ins = self.ins

        fpu_ena = (self.csr[CSR_MSTATUS] & CSR_MSTATUS_FS_MASK) >> CSR_MSTATUS_FS_POS 

        if (fpu_ena == 0):
            if (op in fpu_instructions):
                raise IllegalInstruction('FP instruction with disabled FPU', ins)
        
        if (op in RTypeIns):
            yield from self.executeRIns()
        elif (op in R4TypeIns):
            self.executeR4Ins()
        elif (op in ITypeIns):
            yield from self.executeIIns()
        elif (op in BTypeIns):
            self.executeBIns()
        elif (op in JTypeIns):
            self.executeJIns()
        elif (op in STypeIns):
            yield from self.executeSIns()
        elif (op in UTypeIns):
            self.executeUIns()
        elif (op in CRTypeIns):
            self.executeCRIns()
        elif (op in CITypeIns):
            yield from self.executeCIIns()
        elif (op in CSTypeIns):
            yield from self.executeCSIns()
        elif (op in CSSTypeIns):
            yield from self.executeCSSIns();
        elif (op in CIWTypeIns):
            self.executeCIWIns()
        elif (op in CBTypeIns):
            self.executeCBIns()
        elif (op in CJTypeIns):
            self.executeCJIns()
        elif (op in CLTypeIns):
            yield from self.executeCLIns()
                                

        elif (op == 'FENCE'):
            pr('ignored')
        elif (op == 'FENCE.I'):
            pr('ignored')
        elif (op == 'CUSTOM0'):
            yield from self.executeCustom(0)
        elif (op == 'CUSTOM1'):
            yield from self.executeCustom(1)
        elif (op == 'CUSTOM2'):
            yield from self.executeCustom(2)
        elif (op == 'CUSTOM3'):
            yield from self.executeCustom(3)
        else:
            raise Exception('{} - Not supported!'.format(op))
            #self.parent.getSimulator().stop()
            
        if (self.reg[0] != 0):
            print(' WARNING - R0 was writen!')
            if (self.stopOnExceptions):
                self.parent.getSimulator().stop()
            self.reg[0] = 0

        self.csr[0xc02] += 1            
        
    def executeRIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F
        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F

        fp = FloatingPointHelper()
        fd1 = fp.ieee754_to_dp(self.freg[rs1])
        fd2 = fp.ieee754_to_dp(self.freg[rs2])
        f1 = fd1 # @deprecated, use fd1
        f2 = fd2 # @deprecated, use fd2
        fs1 = fp.ieee754_to_sp(self.freg[rs1])
        fs2 = fp.ieee754_to_sp(self.freg[rs2])

        
        if (op == 'ADD'):
            self.reg[rd] = (self.reg[rs1] + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'ADD.UW'):
            self.reg[rd] = (zeroExtend(self.reg[rs1], 32) + self.reg[rs2] ) & ((1<<64)-1)  
            pr('r{} = r{} + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'AND'):
            self.reg[rd] = self.reg[rs1] & self.reg[rs2]      
            pr('r{} = r{} & r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'ANDN'):
            self.reg[rd] = self.reg[rs1] & ~self.reg[rs2]      
            pr('r{} = r{} & ~r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'OR'):
            self.reg[rd] = self.reg[rs1] | self.reg[rs2]      
            pr('r{} = r{} | r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'ORN'):
            self.reg[rd] = (self.reg[rs1] | ~self.reg[rs2]) & ((1<<64)-1)     
            pr('r{} = r{} | ~r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'XOR'):
            self.reg[rd] = self.reg[rs1] ^ self.reg[rs2]      
            pr('r{} = r{} ^ r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'XNOR'):
            self.reg[rd] = (self.reg[rs1] ^ ~self.reg[rs2]) & ((1<<64)-1)      
            pr('r{} = r{} ^ r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SUB'):
            #print('{:016X} - {:016X}'.format(self.reg[rs1] , self.reg[rs2]))
            self.reg[rd] = (self.reg[rs1] - self.reg[rs2]) & ((1<<64)-1)
            pr('r{} = r{} - r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MUL'):
            self.reg[rd] = (self.reg[rs1] * self.reg[rs2]) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'CLMUL'):
            self.reg[rd] = clmul(self.reg[rs1], self.reg[rs2]) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'CLMULH'):
            self.reg[rd] = clmul(self.reg[rs1], self.reg[rs2]) >> 64       
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'CLMULR'):
            self.reg[rd] = clmulr(self.reg[rs1], self.reg[rs2]) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MULH'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1], 64)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
            self.reg[rd] = ((v1 * v2) >> 64) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))

        elif (op == 'MULHU'):
            v1 = self.reg[rs1]
            v2 = self.reg[rs2]
            self.reg[rd] = ((v1 * v2) >> 64) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MULHSU'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1], 64)
            v2 = self.reg[rs2]
            self.reg[rd] = ((v1 * v2) >> 64) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MULW'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)
            self.reg[rd] = signExtend( v1 * v2 , 32, 64 )   
            pr('r{} = r{} * r{} -> {:08X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIV'):
            if (self.reg[rs2] == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                v1 = IntegerHelper.c2_to_signed(self.reg[rs1], 64)
                v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
                self.reg[rd] = div_tz(v1, v2) & ((1<<64)-1)    
            pr('r{} = r{} / r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIVU'):
            if (self.reg[rs2] == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                self.reg[rd] = self.reg[rs1] // self.reg[rs2]      
            pr('r{} = r{} / r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIVW'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)
            if (v2 == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                self.reg[rd] = signExtend(div_tz(v1, v2) & ((1<<32)-1), 32, 64) 
            pr('r{} = r{} / r{} -> {:08X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIVUW'):
            v1 = self.reg[rs1] & ((1<<32)-1)
            v2 = self.reg[rs2] & ((1<<32)-1)
            if (v2 == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                vr = signExtend(v1 // v2, 32, 64) 
                self.reg[rd] = vr 
            pr('r{} = r{} / r{} -> {:08X}'.format(rd, rs1, rs2, self.reg[rd]))   
        elif (op == 'REM'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1], 64)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
            if (v2 == 0):
                vr = v1
            else:
                vr = abs(v1) % abs(v2)
                if (sign(v1) == -1):
                    vr = -vr
            self.reg[rd] = vr & ((1<<64)-1)
            pr('r{} = r{} % r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))         
        elif (op == 'REMW'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)  
            
            if (v2 == 0):
                vr = v1
            else:
                vr = ( v1 % v2)
            
                if (vr != 0) and ( (v1 < 0 and v2 >= 0) or (v1 >= 0 and v2 < 0)):
                    vr = vr - v2
            
            self.reg[rd] = vr & ((1<<64)-1)  
            pr('r{} = r{} % r{} -> {:08X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'REMU'):
            v1 = self.reg[rs1] 
            v2 = self.reg[rs2] 
            if (v2 == 0):
                vr = v1
            else:
                vr = v1 % v2
            self.reg[rd] = vr      
            pr('r{} = r{} % r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))   
        elif (op == 'REMUW'):
            v1 = self.reg[rs1] & ((1<<32)-1)
            v2 = self.reg[rs2] & ((1<<32)-1)
            if (v2 == 0):
                vr = v1
            else:
                vr = v1 % v2
            self.reg[rd] = signExtend(vr, 32, 64)      
            pr('r{} = r{} % r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))       
        elif (op == 'ADDW'):
            v = (self.reg[rs1] & ((1<<32) -1)) + ( self.reg[rs2] & ((1<<32) -1))
            v = v & ((1<<32) -1)
            self.reg[rd] = signExtend(v,32,64)      
            pr('r{} = r{} + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SUBW'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32) -1), 32)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32) -1), 32)
            self.reg[rd] = signExtend((v1 - v2) & ((1<<32)-1), 32, 64)       
            pr('r{} = r{} - r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MAX'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1], 64)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
            self.reg[rd] = max(v1 , v2) & ((1<<64)-1)
            pr('r{} = max(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MAXU'):
            self.reg[rd] = max(self.reg[rs1] , self.reg[rs2])   
            pr('r{} = maxu(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MIN'):
            v1 = IntegerHelper.c2_to_signed(self.reg[rs1], 64)
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
            self.reg[rd] = min(v1 , v2) & ((1<<64)-1)
            pr('r{} = min(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'MINU'):
            self.reg[rd] = min(self.reg[rs1] , self.reg[rs2])   
            pr('r{} = minu(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
            
        elif (op == 'BEXT'):
            sham = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = (self.reg[rs1] >> sham) & 1
            pr('r{} = r{}[r{}] -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'BINV'):
            #if (self.isa == 32): 
            #    self.reg[rd] = self.reg[rs1] | (1 << shamt5)
            #else:
            sham = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = self.reg[rs1] ^ (1 << sham)
            pr('r{} = r{} ^ (1<<r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'BCLR'):
            #if (self.isa == 32): 
            #    self.reg[rd] = self.reg[rs1] | (1 << shamt5)
            #else:
            sham = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = self.reg[rs1] & ~(1 << sham)
            pr('r{} = r{} & ~(1<<r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'BSET'):
            #if (self.isa == 32): 
            #    self.reg[rd] = self.reg[rs1] | (1 << shamt5)
            #else:
            sham = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = self.reg[rs1] | (1 << sham)
            pr('r{} = r{} | (1<<r{}) -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SLT'):
            if (IntegerHelper.c2_to_signed(self.reg[rs1], 64) < IntegerHelper.c2_to_signed(self.reg[rs2], 64)):
                self.reg[rd] = 1
            else:
                self.reg[rd] = 0            
            pr('r{} = r{} < r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))                
        elif (op == 'SLTU'):
            self.reg[rd] = int(self.reg[rs1] < self.reg[rs2])
            pr('r{} = r{} < r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))                
        elif (op == 'ROR'): 
            shv = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = ((self.reg[rs1] >> shv ) | (self.reg[rs1] << (64 - shv) ) ) & ((1<<64) -1)      
            pr('r{} = r{} R>> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'RORW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            if (shv > 0): 
                v = zeroExtend(self.reg[rs1], 32)
                v = ((v >> shv ) | (v << (32 - shv) )) & ((1<<32)-1)
                v = signExtend(v , 32,64)       
            else: v = self.reg[rs1]
            self.reg[rd] = v
            pr('r{} = r{} R>> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'ROL'):
            shv = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = ((self.reg[rs1] << shv ) | (self.reg[rs1] >> (64 - shv) ) ) & ((1<<64) -1)      
            pr('r{} = r{} R>> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'ROLW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            if (shv > 0): 
                v = zeroExtend(self.reg[rs1], 32)
                v = ((v << shv ) | (v >> (32 - shv) )) & ((1<<32)-1)
            else: v = self.reg[rs1] 
            self.reg[rd] = signExtend(v , 32,64) 
            pr('r{} = r{} R<< r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SLL'):
            shv = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = (self.reg[rs1] << shv ) & ((1<<64) -1)      
            pr('r{} = r{} << r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SLLW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            shifted = (self.reg[rs1] << shv) & ((1<<32)-1)
            self.reg[rd] = signExtend(shifted , 32, 64)       
            pr('r{} = r{} << r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SRL'):
            shv = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = (self.reg[rs1] >> shv ) & ((1<<64) -1)      
            pr('r{} = r{} >> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SRLW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            if (shv == 0):
            	v = self.reg[rs1] & ((1<<32) -1)
            	self.reg[rd] = signExtend(v, 32, 64) 
            else:
                v = self.reg[rs1] & ((1<<32) -1)
                v = (v >> shv ) & ((1<<32) -1)
                self.reg[rd] = signExtend(v, 32, 64) 
            pr('r{} = r{} >> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SRA'):
            shv = self.reg[rs2] & ((1<<6)-1)
            self.reg[rd] = (IntegerHelper.c2_to_signed(self.reg[rs1], 64) >> shv ) & ((1<<64) -1)      
            pr('r{} = r{} >> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SRAW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            v = IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32) -1), 32) 
            if (shv == 0):
                v = self.reg[rs1] 
            elif (v < 0):
                v = (v >> shv) 
            else:
                v = ((v & ((1<<32) -1)) >> shv) 
            self.reg[rd] = signExtend(v & ((1<<32) -1), 32, 64) 
            pr('r{} = r{} >> r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SH1ADD'):
            self.reg[rd] = ((self.reg[rs1] << 1) + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} << 1 + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SH1ADD.UW'):
            self.reg[rd] = ((zeroExtend(self.reg[rs1],32) << 1) + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} << 1 + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SH2ADD'):
            self.reg[rd] = ((self.reg[rs1] << 2) + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} << 2 + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SH2ADD.UW'):
            self.reg[rd] = ((zeroExtend(self.reg[rs1],32) << 2) + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} << 2 + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SH3ADD'):
            self.reg[rd] = ((self.reg[rs1] << 3) + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} << 3 + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SH3ADD.UW'):
            self.reg[rd] = ((zeroExtend(self.reg[rs1],32) << 3) + self.reg[rs2]) & ((1<<64)-1)  
            pr('r{} = r{} << 3 + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'FADD.H'):
            self.freg[rd] = self.fpu.fadd_hp(self.freg[rs1] , self.freg[rs2])
            pr('fr{} = fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FADD.S'):
            self.freg[rd] = self.fpu.fadd_sp(self.freg[rs1] , self.freg[rs2])      
            pr('fr{} = fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FADD.D'):
            self.freg[rd] = self.fpu.fadd_dp(self.freg[rs1] , self.freg[rs2])
            pr('fr{} = fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSUB.H'):
            self.freg[rd] = self.fpu.fsub_hp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = fr{} - fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSUB.S'):
            self.freg[rd] = self.fpu.fsub_sp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = fr{} - fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSUB.D'):
            self.freg[rd] = self.fpu.fsub_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = fr{} - fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))            
        elif (op == 'FMUL.H'):
            self.freg[rd] = self.fpu.fmul_hp(self.freg[rs1] , self.freg[rs2])      
            pr('fr{} = fr{} * fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMUL.S'):
            self.freg[rd] = self.fpu.fmul_sp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = fr{} * fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMUL.D'):
            self.freg[rd] = self.fpu.fmul_dp(self.freg[rs1] , self.freg[rs2])
            pr('fr{} = fr{} * fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))            
        elif (op == 'FDIV.H'):
            self.freg[rd] = self.fpu.fdiv_hp(self.freg[rs1], self.freg[rs2])  
            pr('fr{} = fr{} / fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FDIV.S'):
            self.freg[rd] = self.fpu.fdiv_sp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = fr{} / fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FDIV.D'):            
            self.freg[rd] = self.fpu.fdiv_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = fr{} / fr{} -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMIN.H'):
            self.freg[rd] = self.fpu.min_hp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = min(fr{}, fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMIN.S'):
            self.freg[rd] = self.fpu.min_sp(self.freg[rs1], self.freg[rs2])    
            pr('fr{} = min(fr{}, fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMIN.D'):
            self.freg[rd] = self.fpu.min_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = min(fr{}, fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMAX.H'):
            self.freg[rd] = self.fpu.max_hp(self.freg[rs1], self.freg[rs2])      
            pr('fr{} = max(fr{}, fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FMAX.S'):
            self.freg[rd] = self.fpu.max_sp(self.freg[rs1], self.freg[rs2])      
            pr('fr{} = max(fr{}, fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSQRT.H'):
            self.freg[rd] = self.fpu.fsqrt_hp(self.freg[rs1])
            pr('fr{} = sqrt(fr{}) -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FSQRT.S'):
            self.freg[rd] = self.fpu.fsqrt_sp(self.freg[rs1])
            pr('fr{} = sqrt(fr{}) -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FSQRT.D'):
            self.freg[rd] = self.fpu.fsqrt_dp(self.freg[rs1])
            pr('fr{} = sqrt(fr{}) -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FMAX.D'):
            self.freg[rd] = self.fpu.max_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = max(fr{}, fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FCLASS.H'):
            self.reg[rd] = self.fpu.class_hp(self.freg[rs1])
            pr('r{} = class(fr{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCLASS.S'):
            self.reg[rd] = self.fpu.class_sp(self.freg[rs1])
            pr('r{} = class(fr{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCLASS.D'):
            self.reg[rd] = self.fpu.class_dp(self.freg[rs1])
            pr('r{} = class(fr{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FEQ.H'):
            self.reg[rd] = self.fpu.cmp_hp('eq', self.freg[rs1], self.freg[rs2])
            pr('r{} = (fr{}==fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FEQ.S'):
            self.reg[rd] = self.fpu.cmp_sp('eq', self.freg[rs1], self.freg[rs2]) 
            pr('r{} = (fr{}==fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FEQ.D'):
            self.reg[rd] = self.fpu.cmp_dp('eq', self.freg[rs1], self.freg[rs2])
            pr('r{} = (fr{}==fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FLE.H'):
            self.reg[rd] = self.fpu.cmp_hp('le', self.freg[rs1], self.freg[rs2]) 
            pr('r{} = (fr{}<=fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FLE.S'):
            self.reg[rd] = self.fpu.cmp_sp('le', self.freg[rs1], self.freg[rs2]) 
            pr('r{} = (fr{}<=fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FLT.H'):
            self.reg[rd] = self.fpu.cmp_hp('lt', self.freg[rs1], self.freg[rs2]) 
            pr('r{} = (fr{}<fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FLT.S'):
            self.reg[rd] = self.fpu.cmp_sp('lt', self.freg[rs1], self.freg[rs2]) 
            pr('r{} = (fr{}<fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FLE.D'):
            self.reg[rd] = self.fpu.cmp_dp('le', self.freg[rs1], self.freg[rs2])
            pr('r{} = (fr{}<=fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FLT.D'):
            self.reg[rd] = self.fpu.cmp_dp('lt', self.freg[rs1], self.freg[rs2])
            pr('r{} = (fr{}<fr{}) -> {:016X}'.format(rd, rs1,rs2, self.reg[rd]))
        elif (op == 'FCVT.D.H'):
            self.freg[rd] = self.fpu.convert_hp_to_dp(self.freg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.D.S'):
            self.freg[rd] = self.fpu.convert_sp_to_dp(self.freg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.D.L'):
            self.freg[rd] = self.fpu.convert_i64_to_dp(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.D.LU'):
            self.freg[rd] = fp.dp_to_ieee754(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.D.W'):
            self.freg[rd] = fp.dp_to_ieee754(IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32))
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.D.WU'):
            self.freg[rd] = fp.dp_to_ieee754(self.reg[rs1] & ((1<<32)-1))
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.L.H'):
            self.reg[rd] = self.fpu.convert_hp_to_i64(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.L.S'):
            self.reg[rd] = self.fpu.convert_sp_to_i64(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.L.D'):
            self.reg[rd] = self.fpu.convert_dp_to_i64(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.LU.H'):
            self.reg[rd] = self.fpu.convert_hp_to_u64(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.LU.S'):
            self.reg[rd] = self.fpu.convert_sp_to_u64(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.LU.D'):
            self.reg[rd] = self.fpu.convert_dp_to_u64(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.W.D'):
            self.reg[rd] = self.fpu.convert_dp_to_i32(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.W.H'):
            v = self.fpu.convert_hp_to_i32(self.freg[rs1])
            self.reg[rd] = signExtend(v, 32, 64)
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.WU.H'):
            v = self.fpu.convert_hp_to_u32(self.freg[rs1])
            self.reg[rd] = signExtend(v, 32, 64)
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.WU.D'):
            self.reg[rd] = self.fpu.convert_dp_to_u32(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.W.S'):
            v = self.fpu.convert_sp_to_i32(self.freg[rs1])
            self.reg[rd] = signExtend(v, 32, 64)
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.WU.S'):
            v = self.fpu.convert_sp_to_u32(self.freg[rs1])
            self.reg[rd] = signExtend(v, 32, 64)
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.S.H'):
            self.freg[rd] = self.fpu.convert_hp_to_sp(self.freg[rs1])
            pr('fr{} = fr{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.S.D'):
            self.freg[rd] = self.fpu.convert_dp_to_sp(self.freg[rs1])
            pr('fr{} = fr{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.S.W'):
            self.freg[rd] = self.fpu.sp_box(fp.sp_to_ieee754(IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32)))
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.H.S'):
            self.freg[rd] = self.fpu.convert_sp_to_hp(self.freg[rs1])
            pr('fr{} = fr{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.H.D'):
            self.freg[rd] = self.fpu.convert_dp_to_hp(self.freg[rs1])
            pr('fr{} = fr{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.H.W'):
            self.freg[rd] = self.fpu.convert_i32_to_hp(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.H.WU'):
            self.freg[rd] = self.fpu.convert_u32_to_hp(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.H.L'):
            self.freg[rd] = self.fpu.convert_i64_to_hp(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.H.LU'):
            self.freg[rd] = self.fpu.convert_u64_to_hp(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.S.WU'):
            self.freg[rd] = fp.sp_to_ieee754(self.reg[rs1] & ((1<<32)-1))
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.S.L'):
            self.freg[rd] = fp.sp_to_ieee754(IntegerHelper.c2_to_signed(self.reg[rs1], 64))
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FCVT.S.LU'):
            self.freg[rd] = fp.sp_to_ieee754(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))

        elif (op == 'LR.W'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            self.reserveAddress(address, 32//8)
            pr('r{} = [r{}] -> [{}]={:08X}'.format(rd, rs1, self.addressFmt(address), self.reg[rd]))
        elif (op == 'LR.D'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            self.reserveAddress(address, 64//8)
            pr('r{} = [r{}] -> [{}]={:016X}'.format(rd, rs1, self.addressFmt(address), self.reg[rd]))
        elif (op == 'SC.D'):
            address = self.reg[rs1]
            newvalue = self.reg[rs2]
            if (self.isReserved(address, 64//8)):
                yield from self.virtualMemoryWrite(address, 64//8, newvalue)
                self.reserveAddress(-1,-1)
                if (rd == 0):
                    pr('[r{}] = r{} -> [{}]={:016X}'.format(rs1, rs2, self.addressFmt(address), newvalue))
                else:
                    self.reg[rd] = 0    
                    pr('[r{}] = r{}, r[{}]=0 -> [{}]={:016X}'.format(rs1, rs2, rd, self.addressFmt(address), newvalue))
            else:
                if (rd == 0):
                    pr('[r{}] = r{} -> not reserved'.format(rs1, rs2))
                else:
                    self.reg[rd] = 1
                    pr('[r{}] = r{}, r[{}]=1 -> not reserved'.format(rs1, rs2, rd))
        elif (op == 'SC.W'):
            address = self.reg[rs1]
            newvalue = self.reg[rs2]
            if (self.isReserved(address, 32//8)):
                yield from self.virtualMemoryWrite(address, 32//8, newvalue)
                self.reg[rd] = 0    
                pr('[r{}] = r{}, r{}=0 -> [{}]={:016X}'.format(rs1, rs2, rd, self.addressFmt(address), newvalue))
            else:
                self.reg[rd] = 1
                pr('[r{}] = r{}, r{}=1 -> [{}] not reserved'.format(rs1, rs2, rd, self.addressFmt(address)))
        elif (op == 'AMOADD.D'):
            address = self.reg[rs1]
            oldvalue = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= oldvalue + self.reg[rs2] & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            if (rd == 0):
                pr('[r{}] = [r{}] + r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
            else:      
                self.reg[rd] = oldvalue
                pr('r{} = [r{}], [r{}] = [r{}] + r{} -> {:016X}, [{}]={:016X}'.format(rd, rs1, rs1, rs1, rs2, oldvalue, self.addressFmt(address), newvalue))
        elif (op == 'AMOADD.W'):
            address = self.reg[rs1]
            oldvalue = yield from self.virtualMemoryLoad(address, 32//8)
            oldvalue = signExtend(oldvalue, 32, 64) 

            newvalue= oldvalue + self.reg[rs2] & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            if (rd == 0):
                pr('[r{}] = [r{}] + r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
            else:
                self.reg[rd] = oldvalue
                pr('r{} = [r{}], [r{}] = [r{}] + r{} -> {:016X}, [{}]={:08X}'.format(rd, rs1, rs1, rs1, rs2, oldvalue, self.addressFmt(address), newvalue))
                                            
        elif (op == 'AMOAND.W'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(self.reg[rd], 32, 64) 
            newvalue= self.reg[rd] & self.reg[rs2] & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = [r{}] & r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOAND.D'):
            address = self.reg[rs1]
            oldvalue = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= oldvalue & self.reg[rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            if (rd == 0):
                pr('[r{}] = [r{}] & r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
            else:
                self.reg[rd] = oldvalue
                pr('r{} = [r{}], [r{}] = [r{}] & r{} -> {:016X}, [{}]={:016X}'.format(rd, rs1, rs1, rs1, rs2, oldvalue, self.addressFmt(address), newvalue))
        elif (op == 'AMOOR.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = signExtend(v, 32, 64) 
            v2 = signExtend(self.reg[rs2], 32, 64)
            newvalue= (v | v2) & ((1<<32) -1)
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            if (rd != 0):
                self.reg[rd] = v
            pr('[r{}] = [r{}] | r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOOR.D'):
            address = self.reg[rs1]
            oldvalue = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= oldvalue | self.reg[rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            if (rd == 0):
                pr('[r{}] = [r{}] | r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
            else:
                self.reg[rd] = oldvalue
                pr('r{} = [r{}], [r{}] = [r{}] | r{} -> {:016X}, [{}]={:016X}'.format(rd, rs1, rs1, rs1, rs2, oldvalue, self.addressFmt(address), newvalue))
        elif (op == 'AMOXOR.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = signExtend(v, 32,64) 
            newvalue= (v ^ self.reg[rs2]) & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            if (rd != 0):
                self.reg[rd] = v
            pr('[r{}] = [r{}] ^ r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOXOR.D'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= v ^ self.reg[rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            if (rd != 0):
                self.reg[rd] = v
            pr('[r{}] = [r{}] ^ r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOSWAP.W'):
            # [rs1] -> rd
            #    r2 -> [rs1]
            address = self.reg[rs1]
            
            oldvalue = yield from self.virtualMemoryLoad(address, 32//8)
            oldvalue = signExtend(oldvalue, 32,64)                 
            newvalue = self.reg[rs2] & 0xFFFFFFFF
            self.reg[rd] = oldvalue            
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('r{} = [r{}], [r{}] = r{} -> {:016X} [{}]={:08X}'.format(rd, rs1, rs1, rs2, self.reg[rd], self.addressFmt(address), newvalue))
        elif (op == 'AMOSWAP.D'):
            # [rs1] -> rd
            #    r2 -> [rs1]
            address = self.reg[rs1]
            oldvalue = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue = self.reg[rs2]
            self.reg[rd] = oldvalue
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('r{}:[r{}] X r{} -> {:016X} [{}]={:016X}'.format(rd, rs1, rs2, self.reg[rd], self.addressFmt(address), newvalue))
        elif (op == 'AMOMAX.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = IntegerHelper.c2_to_signed(v, 32) 
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 32)
            self.reg[rd] = signExtend(v, 32, 64) 
            newvalue= max(v , v2) 
            newvalue = signExtend(newvalue, 32,64) 
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = max([r{}] , r{}), r{}=[r{}] -> [{}]={:08X}, {:016X}'.format(rs1, rs1, rs2, rd, rs1, self.addressFmt(address), newvalue, self.reg[rd]))
        elif (op == 'AMOMAXU.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = zeroExtend(v, 32) 
            newvalue= max(v , self.reg[rs2] & ((1<<32)-1))
            self.reg[rd] = signExtend(v, 32,64) 
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = max([r{}] , r{}) -> [{}]={:08X}'.format(rd, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMAX.D'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 64//8)
            v = IntegerHelper.c2_to_signed(v, 64) 
            v2 = IntegerHelper.c2_to_signed(self.reg[rs2], 64) 
            self.reg[rd] = v & ((1<<64) -1)             
            newvalue= max(v , v2) & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = max([r{}] , r{}) -> [{}]={:08X}'.format(rd, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMAXU.D'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            #self.reg[rd] = signExtend(self.reg[rd], 32) & ((1<<64)-1)
            newvalue= max(self.reg[rd] , self.reg[rs2]) & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = max([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMIN.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = IntegerHelper.c2_to_signed(v, 32) 
            newvalue= min(v , IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)) & ((1<<32)-1)
            self.reg[rd] = v & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMINU.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = zeroExtend(v, 32) 
            newvalue= min(v , self.reg[rs2] & ((1<<32)-1))
            self.reg[rd] = signExtend(v, 32,64) 
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMIN.D'):
            address = self.reg[rs1]
            vm = yield from self.virtualMemoryLoad(address, 64//8)
            vm = IntegerHelper.c2_to_signed(vm, 64)
            vr = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
            newvalue= min(vm , vr) & ((1<<64)-1)
            self.reg[rd] = vm & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMINU.D'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= min(v , self.reg[rs2]) & ((1<<64)-1)
            self.reg[rd] = v
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'SFENCE.VMA'):
            if (self.csr[CSR_PRIVLEVEL] == CSR_PRIVLEVEL_SUPERVISOR) and (self.csr[CSR_MSTATUS] & CSR_MSTATUS_TVM_MASK):
                raise IllegalInstruction('TVM does not allow SFENCE.VMA', self.ins)
            pr('flusing tlb')
            self.tlb = {}
        elif (op == 'ZEXT.H'):
            self.reg[rd] = zeroExtend(self.reg[rs1] , 16)    
            pr('r{} = r{}[15:0]  -> {:016X}'.format(rd, rs1, self.reg[rd]))
        else:
            raise Exception('{} - R-Type instruction not supported!'.format(op))
            #self.parent.getSimulator().stop()

    def executeR4Ins(self):
        op = self.decoded_ins
        ins = self.ins

        rd = get_bits(ins, 7, 5)
        rs1 = get_bits(ins, 15, 5)
        rs2 = get_bits(ins, 20, 5)
        rs3 = get_bits(ins, 27, 5)
        fp = FloatingPointHelper()
        fs1 = fp.ieee754_to_sp(self.freg[rs1])
        fs2 = fp.ieee754_to_sp(self.freg[rs2])
        fs3 = fp.ieee754_to_sp(self.freg[rs3])
        fd1 = fp.ieee754_to_dp(self.freg[rs1])
        fd2 = fp.ieee754_to_dp(self.freg[rs2])
        fd3 = fp.ieee754_to_dp(self.freg[rs3])

        
        if (op == 'FMADD.H'):
            self.freg[rd] = self.fpu.fma_hp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('fr{} = fr{} * fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FMADD.S'):
            self.freg[rd] = self.fpu.fma_sp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3]) 
            pr('fr{} = fr{} * fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FMADD.D'):
            self.freg[rd] = self.fpu.fma_dp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('fr{} = fr{} * fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FMSUB.H'):
            self.freg[rd] = self.fpu.fms_hp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('fr{} = fr{} * fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FMSUB.S'):
            self.freg[rd] = self.fpu.fms_sp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('r{} = r{} * r{} - r{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FMSUB.D'):
            self.freg[rd] = self.fpu.fms_dp(self.freg[rs1] , self.freg[rs2], self.freg[rs3])
            pr('r{} = r{} * r{} - r{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FNMSUB.H'):
            self.freg[rd] = self.fpu.fnms_hp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('fr{} = fr{} * fr{} + fr{} -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FNMSUB.S'):
            self.freg[rd] = self.fpu.fnms_sp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('r{} = -(r{} * r{} - r{}) -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FNMSUB.D'):
            self.freg[rd] = self.fpu.fnms_dp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])
            pr('r{} = -(r{} * r{} - r{}) -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FNMADD.H'):
            self.freg[rd] = self.fpu.fnma_hp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])      
            pr('r{} = -(r{} * r{} + r{}) -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FNMADD.S'):
            self.freg[rd] = self.fpu.fnma_sp(self.freg[rs1] , self.freg[rs2] , self.freg[rs3])      
            pr('r{} = -(r{} * r{} + r{}) -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FNMADD.D'):
            self.freg[rd] = self.fpu.fma_dp(FloatingPointHelper.ieee754_dp_neg(self.freg[rs1]) , self.freg[rs2] , FloatingPointHelper.ieee754_dp_neg(self.freg[rs3]))
            pr('fr{} = -(fr{} * fr{} + fr{}) -> {:016X}'.format(rd, rs1, rs2, rs3, self.freg[rd]))
        elif (op == 'FMV.X.H'):
            self.reg[rd] = signExtend(self.freg[rs1] & ((1<<16)-1), 16,64) 
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FMV.H.X'):
            self.freg[rd] = self.fpu.hp_box(self.reg[rs1])
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FMV.X.D'):
            self.reg[rd] = self.freg[rs1] 
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FMV.D.X'):
            self.freg[rd] = self.reg[rs1]
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FMV.X.W'):
            self.reg[rd] = signExtend(self.freg[rs1] & ((1<<32)-1), 32,64) 
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FMV.W.X'):
            self.freg[rd] = self.fpu.sp_box(self.reg[rs1] & ((1<<32)-1))
            pr('fr{} = r{} -> {:016X}'.format(rd, rs1, self.freg[rd]))
        elif (op == 'FSGNJ.D'):
            self.freg[rd] = self.fpu.sign_inject_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * sign(fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJN.D'):
            self.freg[rd] = self.fpu.sign_n_inject_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * not(sign(fr{})) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJX.D'):
            self.freg[rd] = self.fpu.sign_xor_inject_dp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * (sign(fr{})^sign(fr{})) -> {:016X}'.format(rd, rs1, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJ.S'):
            self.freg[rd] = self.fpu.sign_inject_sp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * sign(fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJ.H'):
            self.freg[rd] = self.fpu.sign_inject_half(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * sign(fr{}) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJN.S'):
            self.freg[rd] = self.fpu.sign_n_inject_sp(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * not(sign(fr{})) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJN.H'):
            self.freg[rd] = self.fpu.sign_n_inject_half(self.freg[rs1], self.freg[rs2])
            pr('fr{} = abs(fr{}) * not(sign(fr{})) -> {:016X}'.format(rd, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJX.S'):
            self.freg[rd] = (self.freg[rs1] & ((1<<31)-1)) | (((1<<31) & (self.freg[rs1])) ^ ((1<<31) & (self.freg[rs2])))
            pr('fr{} = abs(fr{}) * (sign(fr{})^sign(fr{})) -> {:016X}'.format(rd, rs1, rs1, rs2, self.freg[rd]))
        elif (op == 'FSGNJX.H'):
            self.freg[rd] = (self.freg[rs1] & ((1<<15)-1)) | (((1<<15) & (self.freg[rs1])) ^ ((1<<15) & (self.freg[rs2])))
            pr('fr{} = abs(fr{}) * (sign(fr{})^sign(fr{})) -> {:016X}'.format(rd, rs1, rs1, rs2, self.freg[rd]))
        else:
            raise Exception('{} - R4-Type instruction not supported!'.format(op))
            #self.parent.getSimulator().stop()
    
    def executeIIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F
        rs1 = (ins >> 15) & 0x1F
        simm12 = compose_sign(ins, [[20, 12]])
        shamt6 = compose(ins, [[20,6]])
        shamt5 = compose(ins, [[20,5]])
        csr = compose(ins, [[20, 12]])

        if (op == 'ADDI'):
            self.reg[rd] = (self.reg[rs1] + simm12) & ((1<<64)-1)
            pr('r{} = r{} + {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'SLTI'):
            v = 1 if (IntegerHelper.c2_to_signed(self.reg[rs1], 64) < simm12) else 0 
            if (rd != 0):
                self.reg[rd] = v            
            pr('r{} = r{} < {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'SLTIU'):
            self.reg[rd] = 0            
            if  (self.reg[rs1] < signExtend(simm12, 12, 64)):
                self.reg[rd] = 1
            pr('r{} = r{} < {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'ANDI'):
            self.reg[rd] = self.reg[rs1] & (simm12 & ((1<<64)-1))
            pr('r{} = r{} & {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'ADDIW'):
            self.reg[rd] = signExtend((self.reg[rs1] + simm12) & 0xFFFFFFFF, 32, 64) 
            pr('r{} = r{} + {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'ORI'):
            self.reg[rd] = self.reg[rs1] | (simm12 & ((1<<64)-1))
            pr('r{} = r{} | {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'XORI'):
            self.reg[rd] = self.reg[rs1] ^ (simm12 & ((1<<64)-1))
            pr('r{} = r{} ^ {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'GREVI'):
            self.reg[rd] = grev(self.reg[rs1] , shamt6)
            pr('r{} = r{} grev {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'GORCI'):
            self.reg[rd] = gorc(self.reg[rs1] , shamt6)
            pr('r{} = r{} gorc {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'BEXTI'):
            self.reg[rd] = (self.reg[rs1] >> shamt6) & 1
            pr('r{} = r{}[{}] -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'BINVI'):
            #if (self.isa == 32): 
            #    self.reg[rd] = self.reg[rs1] | (1 << shamt5)
            #else:
            self.reg[rd] = self.reg[rs1] ^ (1 << shamt6)
            pr('r{} = r{} ^ (1<<{}) -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))

        elif (op == 'BCLRI'):
            #if (self.isa == 32): 
            #    self.reg[rd] = self.reg[rs1] | (1 << shamt5)
            #else:
            self.reg[rd] = self.reg[rs1] & ~(1 << shamt6)
            pr('r{} = r{} & ~(1<<{}) -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'BSETI'):
            #if (self.isa == 32): 
            #    self.reg[rd] = self.reg[rs1] | (1 << shamt5)
            #else:
            self.reg[rd] = self.reg[rs1] | (1 << shamt6)
            pr('r{} = r{} | (1<<{}) -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'CLZ'):
            self.reg[rd] = count_leading_zeros(self.reg[rs1], 64)
            pr('r{} = clz(r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'CLZW'):
            self.reg[rd] = count_leading_zeros(self.reg[rs1], 32)
            pr('r{} = clzw(r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'CTZ'):
            self.reg[rd] = count_trailing_zeros(self.reg[rs1], 64)
            pr('r{} = ctz(r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'CTZW'):
            self.reg[rd] = count_trailing_zeros(self.reg[rs1], 32)
            pr('r{} = ctzw(r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'CPOP'):
            self.reg[rd] = pop_count(self.reg[rs1], 64)
            pr('r{} = cpop(r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'CPOPW'):
            self.reg[rd] = pop_count(self.reg[rs1] & ((1<<32)-1), 32)
            pr('r{} = cpop(r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'SEXT.B'):
            self.reg[rd] = signExtend(self.reg[rs1] & 0xFF, 8, 64) 
            pr('r{} = sign extend 8 (r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'SEXT.H'):
            self.reg[rd] = signExtend(self.reg[rs1] & 0xFFFF, 16, 64) 
            pr('r{} = sign extend 16 (r{}) -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'LD'):
            address = self.reg[rs1] + simm12
            pr(f'r{rd} = [r{rs1} + {simm12}]', end='')
            if ((address & 0x7) != 0):
                raise LoadAddressMisaligned(tval=address)
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('-> [{}]={:016X}'.format(self.addressFmt(address), self.reg[rd]))
        elif (op == 'LW'):
            address = self.reg[rs1] + simm12
            pr('r{} = [r{} + {}] '.format(rd, rs1, simm12), end = '')
            if ((address & 0x3) != 0):
                raise LoadAddressMisaligned(tval=address)
            v = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(v, 32, 64) 
            pr('-> [{}]={:016X}'.format(self.addressFmt(address), self.reg[rd]))
        elif (op == 'LWU'):
            address = self.reg[rs1] + simm12
            pr('r{} = [r{} + {}] '.format(rd, rs1, simm12))
            if ((address & 0x3) != 0):
                raise LoadAddressMisaligned(tval=address)
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            pr('-> [{}]={:016X}'.format(self.addressFmt(address), self.reg[rd]))
        elif (op == 'LH'):
            address = self.reg[rs1] + simm12
            pr('r{} = [r{} + {}] '.format(rd, rs1, simm12))
            if ((address & 0x1) != 0):
                raise LoadAddressMisaligned(tval=address)
            v = yield from self.virtualMemoryLoad(address, 16//8)
            self.reg[rd] = signExtend(v, 16, 64) 
            pr('-> [{}]={:016X}'.format(self.addressFmt(address), self.reg[rd]))
        elif (op == 'LHU'):
            address = self.reg[rs1] + simm12
            pr('r{} = [r{} + {}] '.format(rd, rs1, simm12))
            if ((address & 0x1) != 0):
                raise LoadAddressMisaligned(tval=address)
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 16//8)
            pr('-> [{}]={:016X}'.format(self.addressFmt(address), self.reg[rd]))
        elif (op == 'LB'):
            address = self.reg[rs1] + simm12
            v = yield from self.virtualMemoryLoad(address, 8//8)
            self.reg[rd] = signExtend(v, 8, 64) 
            pr('r{} = [r{} + {}] -> [{}]={:016X}'.format(rd, rs1, simm12, self.addressFmt(address), self.reg[rd]))
        elif (op == 'LBU'):
            address = self.reg[rs1] + simm12
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 8//8)
            pr('r{} = [r{} + {}] -> [{}]={:02X}'.format(rd, rs1, simm12, self.addressFmt(address), self.reg[rd]))
        elif (op == 'FLH'):
            address = self.reg[rs1] + simm12
            v = yield from self.virtualMemoryLoad(address, 16//8)
            #self.freg[rd] = signExtend(v, 16) & ((1<<64)-1)
            self.freg[rd] = self.fpu.hp_box(v)
            pr('r{} = [r{} + {}] -> [{}]={:016X}'.format(rd, rs1, simm12, self.addressFmt(address), self.freg[rd]))
        elif (op == 'CBO.ZERO'):
            self.dcache[self.reg[rs1]] = 0
            pr('r{}'.format(rs1))
        elif (op == 'CSRRW'):
            newvalue = self.reg[rs1]
            oldvalue, allowed = yield from self.readCSR(csr)
            if (rd == 0):
                csrname = self.implemented_csrs[csr]
                pr('{} = r{} -> {:016X}'.format(csrname, rs1, newvalue))            
            else:
                if (rd != 0) and (allowed): self.reg[rd] = oldvalue
                csrname = self.implemented_csrs[csr]
                
                if (rd == 0):
                    pr('{} = r{} -> {:016X}'.format(csrname, rs1, newvalue))
                else:
                    pr('r{} = {}, {} = r{} -> {:016X},{:016X}'.format(rd, csrname, csrname, rs1, oldvalue, newvalue))
            self.writeCSR(csr, newvalue)

        elif (op == 'CSRRS'):
            # Read and set
            # rd <= csr, csr <= csr | rs1 
            v1 = self.reg[rs1] 
            oldvalue, allowed = yield from self.readCSR(csr)
            if (rd != 0) and allowed: self.reg[rd] = oldvalue
            csrname = self.implemented_csrs[csr]
            newvalue = oldvalue | v1
            
            if (rd == 0):
                pr('{} |= r{} -> {:016X}'.format(csrname, rs1, newvalue)) 
            elif (rs1 == 0):
                pr('r{} = {} -> {:016X}'.format(rd, csrname, self.reg[rd]))           
            else:
                pr('r{} = {}, {} |= r{} -> {:016X},{:016X}'.format(rd, csrname, csrname, rs1, self.reg[rd], newvalue))            

            if (v1 != 0): self.setCSR(csr, v1)
        
        elif (op == 'CSRRC'):
            # Read and clear
            v1 = self.reg[rs1]
            csrv , allowed = yield from self.readCSR(csr)
            csrname = self.implemented_csrs[csr]
            if (rd == 0):
                pr('{} &= ~r{} -> {:016X}'.format(csrname, rs1, self.csr[csr]))            
            else:
                pr('r{} = {}, {} &= ~r{} -> {:016X},{:016X}'.format(rd, csrname, csrname, rs1, self.reg[rd], self.csr[csr]))            
            if (v1 != 0): self.clearCSR(csr, v1)
            if (rd != 0) and allowed: self.reg[rd] = csrv
        
        elif (op == 'CSRRWI'):
            vcsr, allowed = yield from self.readCSR(csr)
            if (rd != 0) and allowed: self.reg[rd] = vcsr
            self.writeCSR(csr, rs1)
            csrname = self.implemented_csrs[csr]
            if (rd == 0):
                pr('{} = {}'.format(csrname, rs1))
            else:
                pr('r{} = {}, {} = {} -> {:016X}'.format(rd, csrname, csrname, rs1, self.reg[rd]))
        elif (op == 'CSRRSI'):
            vcsr, allowed = yield from self.readCSR(csr)
            nvcsr = vcsr | rs1
            csrname = self.implemented_csrs[csr]
            if (rd == 0):
                pr('{} |= {} -> {:016X}'.format(csrname, rs1, nvcsr))
            else:
                pr('r{} = {}, {} |= {} -> {:016X}'.format(rd, csrname, csrname, rs1, nvcsr))                     
            if (rs1 != 0): self.setCSR(csr, rs1)
            if (rd != 0) and allowed: self.reg[rd] = vcsr
        elif (op == 'CSRRCI'):
            oldValue, allowed = yield from self.readCSR(csr)
            csrname = self.implemented_csrs[csr]

            if (rs1 != 0): 
                pr('r{} = {}, {} &= ~{} -> {:016X}'.format(rd, csrname, csrname, rs1, oldValue))                        
                self.clearCSR(csr, rs1)
            else:
                pr('{} &= ~{} '.format(csrname, rs1))                                    
            if (rd != 0) and allowed: self.reg[rd] = oldValue
        elif (op == 'RORI'):
            self.reg[rd] = ((self.reg[rs1] >> shamt6) | (self.reg[rs1] << (64-shamt6))) & ((1<<64)-1)
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'RORIW'):
            v = ((self.reg[rs1] >> shamt6) | (self.reg[rs1] << (32-shamt6))) & ((1<<32)-1)
            self.reg[rd] = signExtend(v, 32, 64)
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SLLI'):
            self.reg[rd] = (self.reg[rs1] << shamt6) & ((1<<64)-1)
            pr('r{} = r{} << {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SLLIW'):
            v = self.reg[rs1] << shamt6
            self.reg[rd] = signExtend(v & ((1<<32)-1), 32, 64) 
            pr('r{} = r{} << {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SLLI.UW'):
            v = zeroExtend(self.reg[rs1], 32) <<  shamt6
            self.reg[rd] = v  & ((1<<64)-1)
            pr('r{} = r{} << {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SRLI'):
            self.reg[rd] = self.reg[rs1] >> shamt6
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SRLIW'):
            self.reg[rd] = IntegerHelper.c2_to_signed((self.reg[rs1] & ((1<<32)-1)) >> shamt6, 32) & ((1<<64)-1)
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SRAI'):
            self.reg[rd] = (IntegerHelper.c2_to_signed(self.reg[rs1], 64) >> shamt6) & ((1<<64)-1)
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SRAIW'):
            self.reg[rd] = (IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32) >> shamt6) & ((1<<64)-1)
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'WFI'):
            pr('ignored')
        elif (op == 'MRET'):
            self.should_jump = True
            self.jmp_address = self.csr[CSR_MEPC]
            self.csr[CSR_PRIVLEVEL] = (self.csr[CSR_MSTATUS] >> 11) & ((1<<2)-1) # change to the MPP Mode (mstatus)
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MIE_POS, 1, getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPIE_POS, 1))
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPP_POS, 2, 0) # clear MPP
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPIE_POS, 1, 1)
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPRV_POS, 1, 0)
            pr('pc = mepc -> {:016X}'.format(self.jmp_address)) 
            self.functionExit(et=1)
        elif (op == 'SRET'):
            if (self.csr[CSR_MSTATUS] & CSR_MSTATUS_TSR_MASK ):
                raise IllegalInstruction('SRET with TSR', self.ins)                
            self.should_jump = True
            self.jmp_address = self.csr[CSR_SEPC]
            self.csr[CSR_PRIVLEVEL] = (self.csr[CSR_MSTATUS] >> 8) & 1 # we use MSTATUS instead of SSTATUS. change to the SPP Mode (status)   
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SIE_POS, 1, getCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPIE_POS, 1))
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPP_POS, 1, 0) # clear SPP
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_SPIE_POS, 1, 1)
            setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPRV_POS, 1, 0)
            pr('pc = sepc -> {:016X}'.format(self.jmp_address)) 
            self.functionExit(et=2)
        elif (op == 'JALR'):
            self.should_jump = True
            self.jmp_address = (self.reg[rs1] + simm12) & ((1<<64)-2)
            ra = self.pc + 4
            jmpCall = (rd != 1) # or (rd == 0) 
            if (rd == 0):
                pr('r{} +  {} -> {}'.format(rs1, simm12, self.addressFmt(self.jmp_address)))
            else:
                self.reg[rd] = self.pc + 4
                pr('r{} + {} , r{} = pc+4 -> {},{}'.format(rs1, simm12, rd, self.addressFmt(self.jmp_address), self.addressFmt(self.reg[rd])))
            self.functionEnter(self.jmp_address, ra, 0, jmpCall)
        elif (op == 'FLD'):
            off = simm12 
            address = self.reg[rs1] + off
            self.freg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('fr{} = [r2 + {}] -> {:016X}'.format(rd, off, self.freg[rd]))
        elif (op == 'FLW'):
            off = simm12 
            address = self.reg[rs1] + off
            v = yield from self.virtualMemoryLoad(address, 32//8)
            self.freg[rd] = self.fpu.sp_box(v)
            pr('fr{} = [r2 + {}] -> {:016X}'.format(rd, off, self.freg[rd]))
        elif (op == 'ECALL'):
            curpriv = self.csr[0xFFF] # current privilege
            syscall = self.reg[17] # current privilege
            if (curpriv == 3): 
                raise EnvCallMMode(syscall)
            elif (curpriv == 1):
                raise EnvCallSMode(syscall)
            elif (curpriv == 0):
                raise EnvCallUMode(syscall)
            else:
                raise Exception('unknown privilege level {}'.format(curpriv))
        elif (op == 'EBREAK'):
            raise Breakpoint(tval=self.pc)
        else:
            raise Exception('{} I-Type instruction not supported!'.format(op))
            #self.parent.getSimulator().stop()
            
    def executeJIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F
        off21_J = compose_sign(ins, [[31,1], [12,8], [20,1], [21,10]]) << 1  

        if (op == 'JAL'):
            jmpCall = (rd != 1)
            ra = self.pc + 4
            if (rd != 0):
                self.reg[rd] = ra
            self.should_jump = True
            self.jmp_address = self.pc + off21_J
            
            if (rd== 0):
                pr('pc + {} ->  {}'.format(off21_J, self.addressFmt(self.jmp_address)))
            else:                
                pr('pc + {}  r{}=pc+4 ->  {},{:016X}'.format(off21_J, rd, self.addressFmt(self.jmp_address), self.reg[rd]))
            self.functionEnter(self.jmp_address, ra, 0, jmpCall)
        else:
            raise Exception('{} - J-Type instruction not supported!'.format(op))
            #self.parent.getSimulator().stop()

    def executeBIns(self):
        op = self.decoded_ins
        ins = self.ins

        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F
        soff12 = compose_sign(ins, [[31,1], [7,1], [25,6], [8,4]]) << 1


        if (op == 'BEQ'):
            if (self.reg[rs1] == self.reg[rs2]):
                self.should_jump=True
            self.jmp_address = self.pc + soff12
            pr('r{} == r{} ? -> {:016X} {}'.format(rs1, rs2, self.jmp_address, self.should_jump))                            
        elif (op == 'BGE'):
            if (IntegerHelper.c2_to_signed(self.reg[rs1], 64) >= IntegerHelper.c2_to_signed(self.reg[rs2], 64)):
                self.should_jump=True
            self.jmp_address = self.pc + soff12
            pr('r{} >= r{} ? -> {} {:016X}'.format(rs1, rs2, self.should_jump, self.jmp_address ))                            
        elif (op == 'BGEU'):
            if (self.reg[rs1] >= self.reg[rs2] ):
                self.should_jump=True
            self.jmp_address = self.pc + soff12
            pr('r{} >= r{} ? -> {} {:016X}'.format(rs1, rs2, self.should_jump, self.jmp_address ))                            
        elif (op == 'BLT'):
            if (IntegerHelper.c2_to_signed(self.reg[rs1], 64) < IntegerHelper.c2_to_signed(self.reg[rs2], 64)):
                self.should_jump=True
            self.jmp_address = self.pc + soff12
            pr('r{} < r{} ? -> {:016X} {}'.format(rs1, rs2, self.jmp_address, self.should_jump))                            
        elif (op == 'BLTU'):
            if (self.reg[rs1] < self.reg[rs2]):
                self.should_jump=True
            self.jmp_address = self.pc + soff12
            pr('r{} < r{} ? -> {:016X} {}'.format(rs1, rs2, self.jmp_address, self.should_jump))                            
        elif (op == 'BNE'):
            if (self.reg[rs1] != self.reg[rs2]):
                self.should_jump=True
            self.jmp_address = self.pc + soff12
            pr('r{} != r{} ? {} {:016X}'.format(rs1, rs2, self.should_jump, self.jmp_address))    
            #print(self.reg[rs1] , self.reg[rs2])
        else:
            raise Exception(' - BIns Not supported!')
            #self.parent.getSimulator().stop()

    def executeSIns(self):
        op = self.decoded_ins
        ins = self.ins

        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F
        
        soff12 = compose_sign(ins, [[25,7],[7,5]])
        address = self.reg[rs1]+soff12
        saddr = self.addressFmt(address)
        
        if (op == 'SD'):
            pr('[r{} + {}] = r{} -> [{}]={:016X}'.format(rs1, soff12, rs2, saddr, self.reg[rs2]))
            if ((address & 0x7) != 0):
                raise StoreAMOAddressMisaligned(tval = address)
            yield from self.virtualMemoryWrite(address, 64//8, self.reg[rs2])
        elif (op == 'FSH'):
            pr('[r{} + {}] = fr{} -> [{}]={:016X}'.format(rs1, soff12, rs2, saddr, self.freg[rs2]))
            yield from self.virtualMemoryWrite(address, 16//8, self.freg[rs2])
        elif (op == 'FSD'):
            pr('[r{} + {}] = fr{} -> [{}]={:016X}'.format(rs1, soff12, rs2, saddr, self.freg[rs2]))
            yield from self.virtualMemoryWrite(address, 64//8, self.freg[rs2])
        elif (op == 'FSW'):
            pr('[r{} + {}] = fr{} -> [{}]={:08X}'.format(rs1, soff12, rs2, saddr, self.freg[rs2]))
            yield from self.virtualMemoryWrite(address, 32//8, self.freg[rs2])
        elif (op == 'SW'):
            address = self.reg[rs1]+soff12
            pr('[r{} + {}] = r{} -> [{}]={:08X}'.format(rs1, soff12, rs2, saddr, self.reg[rs2] & ((1<<32)-1)))
            if ((address & 0x3) != 0):
                raise StoreAMOAddressMisaligned(tval = address)
            yield from self.virtualMemoryWrite(address, 32//8, self.reg[rs2])
        elif (op == 'SH'):
            address = self.reg[rs1]+soff12
            pr('[r{} + {}] = r{} -> [{}]={:04X}'.format(rs1, soff12, rs2, saddr, self.reg[rs2] & ((1<<16)-1)))
            if ((address & 0x1) != 0):
                raise StoreAMOAddressMisaligned(tval = address)
            yield from self.virtualMemoryWrite(address, 16//8, self.reg[rs2])
        elif (op == 'SB'):
            address = self.reg[rs1]+soff12
            pr('[r{} + {}] = r{} -> [{}]={:02X}'.format(rs1, soff12, rs2, saddr, self.reg[rs2] & ((1<<8)-1)))
            yield from self.virtualMemoryWrite(address, 8//8, self.reg[rs2])
        else:
            raise Exception(' - S-Type instruction not supported!')
            #self.parent.getSimulator().stop()

    def executeUIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F

        if (op == 'AUIPC'):
            simm = compose(ins, [[12,20]]) << 12
            simm = signExtend(simm, 32, 64)
            self.reg[rd] = (self.pc + simm) & ((1<<64)-1)
            pr('r{} = pc + {:08X} -> {:016X}'.format(rd, simm, self.reg[rd]))      
        elif (op == 'LUI'):
            simm = (compose_sign(ins, [[12,20]]) << 12) & ((1<<64)-1)
            self.reg[rd] = simm
            pr('r{} = {:016X} '.format(rd, simm)  )    
        else:
            raise Exception(' - U-Type instruction not supported!')
            #self.parent.getSimulator().stop()
        
    def executeCRIns(self):
        op = self.decoded_ins
        ins = self.ins

        c_rs2 = get_bits(ins, 2, 5)
        c_rs1 = get_bits(ins, 7, 5)

        if (op == 'C.MV'):
            self.reg[c_rs1] = self.reg[c_rs2]      
            pr('r{} = r{} -> {:016X}'.format(c_rs1, c_rs2, self.reg[c_rs1]))
        elif (op == 'C.ADD'):
            if (c_rs1 != 0):
                self.reg[c_rs1] = (self.reg[c_rs1] + self.reg[c_rs2] ) & ((1<<64)-1)    
            pr('r{} = r{} + r{} -> {:016X}'.format(c_rs1, c_rs1, c_rs2, self.reg[c_rs1]))
        elif (op == 'C.JR'):
            self.should_jump = True
            self.jmp_address = self.reg[c_rs1] & ~1 # Spec says we have to ignore lower bit if misalignment
            pr('r{} -> {:016X}'.format(c_rs1, self.jmp_address))
            if (c_rs1 == 1):
                # function exit is identifyied by a jumping to return address register
                self.functionExit()
            else:
                self.functionEnter(self.jmp_address, 0, 0, True)
        elif (op == 'C.JALR'):
            self.should_jump = True
            self.jmp_address = self.reg[c_rs1] & ~1 # Spec says we have to ignore lower bit if misalignment
            ra = self.pc + 2
            self.reg[1] = ra
            pr('r{}, r1 = pc+2 -> {},{}'.format(c_rs1, self.addressFmt(self.jmp_address), self.addressFmt(self.reg[1])))
            self.functionEnter(self.jmp_address, ra, 0, False)
            
        elif (op == 'C.EBREAK'):
            raise Breakpoint(tval=self.pc)
            # 
            #print('C.EBREAK is a BUG?')
            #self.parent.getSimulator().stop()
        else:
            raise Exception(' - CR-Type instruction not supported!')
            #self.parent.getSimulator().stop()
            
    def executeCIIns(self):
        op = self.decoded_ins
        ins = self.ins

        c_rd = get_bits(ins, 7, 5)
        
        # imm6 = compose(ins, [[12,1],[2,5]])
        if (op == 'C.LI'):
            simm6 = compose_sign(ins, [[12,1],[2,5]])
            self.reg[c_rd] = simm6 & ((1<<64)-1)
            pr('r{} = {} -> {:016X}'.format(c_rd,  simm6, self.reg[c_rd]))            
        elif (op == 'C.LUI'):
            simm6 = compose_sign(ins, [[12,1],[2,5]]) << 12
            self.reg[c_rd] = simm6 & ((1<<64)-1)
            pr('r{} = {} -> {:016X}'.format(c_rd,  simm6, self.reg[c_rd]))            
        elif (op == 'C.LWSP'):
            off = compose(ins, [[2,2],[12,1],[4,3]]) << 2
            address = self.reg[2] + off
            v = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[c_rd] = signExtend(v, 32, 64) 
            pr('r{} = [r2 + {}] -> [{}] = {:016X}'.format(c_rd, off, self.addressFmt(address), self.reg[c_rd]))
        elif (op == 'C.LDSP'):
            off = compose(ins, [[2,3], [12,1], [5,2]]) << 3
            address = self.reg[2] + off
            self.reg[c_rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('r{} = [r2 + {}] -> [{}]={:016X}'.format(c_rd, off, self.addressFmt(address), self.reg[c_rd]))
        elif (op == 'C.LQSP'):
            raise Exception('128 instruction')
            # off = compose(ins, [[2,4],[12,1],[6,1]]) << 4
            # address = self.reg[2] + off
            # self.reg[c_rd] = yield from self.memoryLoad(address, 64//8)
            # print('r{} = [r2 + {}] -> {:016X}'.format(c_rd, off, self.reg[c_rd]))
        elif (op == 'C.FLWSP'):
            off = compose(ins, [[2,2],[12,1],[4,3]]) << 2
            address = self.reg[2] + off
            self.freg[c_rd] = yield from self.virtualMemoryLoad(address, 32//8)
            pr('fr{} = [r2 + {}] -> {:016X}'.format(c_rd, off, self.freg[c_rd]))
        elif (op == 'C.FLDSP'):
            off = compose(ins, [[2,3], [12,1], [5,2]]) << 3
            address = self.reg[2] + off
            self.freg[c_rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('fr{} = [r2 + {}] -> {:016X}'.format(c_rd, off, self.freg[c_rd]))
        elif (op == 'C.SLLI'):
            imm6 = compose(ins, [[12,1],[2,5]])
            self.reg[c_rd] = (self.reg[c_rd] << imm6) & ((1<<64)-1)
            pr('r{} = r{} << {} -> {:016X}'.format(c_rd, c_rd, imm6, self.reg[c_rd]))
        elif (op == 'C.ADDI'):
            imm6 = compose_sign(ins, [[12,1],[2,5]])
            self.reg[c_rd] = (self.reg[c_rd] + imm6) & ((1<<64)-1)
            pr('r{} = r{} + {} -> {:016X}'.format(c_rd, c_rd, imm6, self.reg[c_rd]))
        elif (op == 'C.ADDIW'):
            imm6 = compose_sign(ins, [[12,1],[2,5]])
            self.reg[c_rd] = signExtend((self.reg[c_rd] + imm6) & 0xFFFFFFFF, 32, 64) 
            pr('r{} = r{} + {} -> {:016X}'.format(c_rd, c_rd, imm6, self.reg[c_rd]))
        elif (op == 'C.ADDI16SP'):
            imm6 = compose_sign(ins, [[12,1],[3,2],[5,1],[2,1],[6,1]]) << 4
            self.reg[2] = self.reg[2] + imm6
            pr('r2 = r2 + {} -> {:016X}'.format(imm6, self.reg[2]))
        else:
            raise Exception('{} - CI-Type instruction not supported!'.format(op))
            #self.parent.getSimulator().stop()
    
    def executeCSIns(self):
        op = self.decoded_ins
        ins = self.ins
        
        c_rd = 8 + get_bits(ins, 7, 3)
        c_rs1 = c_rd
        c_rs2 = 8 + get_bits(ins, 2, 3)
        
        if (op == 'C.AND'):
            self.reg[c_rd] = self.reg[c_rs1] & self.reg[c_rs2]
            pr('r{} = r{} & r{} -> {:016X}'.format(c_rd, c_rs1, c_rs2, self.reg[c_rd]))
        elif (op == 'C.OR'):
            self.reg[c_rd] = self.reg[c_rs1] | self.reg[c_rs2]
            pr('r{} = r{} | r{} -> {:016X}'.format(c_rd, c_rs1, c_rs2, self.reg[c_rd]))
        elif (op == 'C.XOR'):
            self.reg[c_rd] = self.reg[c_rs1] ^ self.reg[c_rs2]
            pr('r{} = r{} ^ r{} -> {:016X}'.format(c_rd, c_rs1, c_rs2, self.reg[c_rd]))
        elif (op == 'C.SUB'):
            self.reg[c_rd] = (self.reg[c_rs1] - self.reg[c_rs2]) & ((1<<64)-1)
            pr('r{} = r{} - r{} -> {:016X}'.format(c_rd, c_rs1, c_rs2, self.reg[c_rd]))
        elif (op == 'C.ADDW'):
            self.reg[c_rd] = signExtend((self.reg[c_rs1] + self.reg[c_rs2]) & 0xFFFFFFFF, 32, 64) 
            pr('r{} = r{} + r{} -> {:016X}'.format(c_rd, c_rs1, c_rs2, self.reg[c_rd]))
        elif (op == 'C.SUBW'):
            self.reg[c_rd] = signExtend((self.reg[c_rs1] - self.reg[c_rs2]) & 0xFFFFFFFF, 32, 64) 
            pr('r{} = r{} - r{} -> {:016X}'.format(c_rd, c_rs1, c_rs2, self.reg[c_rd]))
        elif (op == 'C.SW'):
            off = compose(ins, [[5,1],[10,3],[6,1]]) << 2
            address = self.reg[c_rs1] + off
            value = self.reg[c_rs2] & ((1<<32)-1)
            yield from self.virtualMemoryWrite(address, 32//8, value)
            pr('[r{}+{}]=r{} -> [{}]={:08X}'.format(c_rs1, off, c_rs2, self.addressFmt(address), value))
        elif (op == 'C.SD'):
            off = compose(ins, [[5,2],[10,3]]) << 3
            address = self.reg[c_rs1] + off
            value = self.reg[c_rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, value)
            pr('[r{}+{}]=r{} -> [{}]={:016X}'.format(c_rs1, off, c_rs2, self.addressFmt(address), value))
        elif (op == 'C.FSD'):
            off = compose(ins, [[5,2],[10,3]]) << 3
            address = self.reg[c_rs1] + off
            value = self.freg[c_rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, value)
            pr('[r{}+{}]=fr{} -> [{}]={:016X}'.format(c_rs1, off, c_rs2, self.addressFmt(address), value))
        else:
            raise Exception(' - CS-Type instruction not supported!')
            #self.parent.getSimulator().stop()
    
    def executeCSSIns(self):
        op = self.decoded_ins
        ins = self.ins

        rs2 = get_bits(ins, 2, 5)
        
        if (op == 'C.SWSP'):
            off = compose(ins, [[7,2],[9,4]]) << 2
            address = self.reg[2] + off
            yield from self.virtualMemoryWrite(address, 32//8, self.reg[rs2])
            pr('[r2 + {}]=r{} -> [{:016X}]={:08X}'.format(off, rs2, address, self.reg[rs2] & 0xFFFFFFFF))
        elif (op == 'C.SDSP'):
            off = compose(ins, [[7,3],[10,3]]) << 3
            address = self.reg[2] + off
            yield from self.virtualMemoryWrite(address, 64//8, self.reg[rs2])
            pr('[r2 + {}]=r{} -> [{:016X}]={:016X}'.format(off, rs2, address, self.reg[rs2]))
        elif (op == 'C.FSDSP'):
            off = compose(ins, [[7,3],[10,3]]) << 3
            address = self.reg[2] + off
            yield from self.virtualMemoryWrite(address, 64//8, self.freg[rs2])
            pr('[r2 + {}]=r{} -> [{:016X}]={:016X}'.format(off, rs2, address, self.reg[rs2]))
        else:
            raise Exception(' - CSS-Type instruction not supported!')
            #self.parent.getSimulator().stop()
        
        
    def executeCIWIns(self):
        op = self.decoded_ins
        ins = self.ins

        c_rd = 8 + get_bits(ins, 2, 3)
        imm8 = compose(ins, [[7,4],[11,2],[5,1],[6,1]]) << 2
        
        if (op == 'C.ADDI4SPN'):
            self.reg[c_rd] = self.reg[2] + imm8
            pr('r{} = r2 + {} -> {:016X}'.format(c_rd, imm8 , self.reg[c_rd]))            
        else:
            raise Exception(' - CIW-Type instruction not supported!')
            #self.parent.getSimulator().stop()
        
    def executeCBIns(self):
        op = self.decoded_ins
        ins = self.ins
        
        c_rd = 8 + get_bits(ins, 7, 3)
        c_rs1 = c_rd
        
        if (op == 'C.ANDI'):
            imm6 = compose_sign(ins, [[12,1],[2,5]])
            self.reg[c_rd] = self.reg[c_rd] & imm6
            pr('r{} = r{} & {} -> {:016X}'.format(c_rd, c_rd, imm6, self.reg[c_rd]))
        elif (op == 'C.SRLI'):
            imm6 = compose(ins, [[12,1],[2,5]])
            self.reg[c_rd] = self.reg[c_rd] >> imm6
            pr('r{} = r{} >> {} -> {:016X}'.format(c_rd, c_rd, imm6, self.reg[c_rd]))
        elif (op == 'C.SRAI'):
            imm6 = compose(ins, [[12,1],[2,5]])
            self.reg[c_rd] = (IntegerHelper.c2_to_signed(self.reg[c_rd],64) >> imm6) & ((1<<64)-1)
            pr('r{} = r{} >> {} -> {:016X}'.format(c_rd, c_rd, imm6, self.reg[c_rd]))
        elif (op == 'C.BEQZ'):
            off = compose_sign(ins, [[12,1],[5,2],[2,1],[10,2],[3,2]]) << 1
            if (self.reg[c_rs1] == 0):
                self.should_jump = True
                self.jmp_address = self.pc + off
                
            pr('r{} == 0 ? {} -> {:016X}'.format(c_rs1, self.should_jump, self.jmp_address))
        elif (op == 'C.BNEZ'):
            off = compose_sign(ins, [[12,1],[5,2],[2,1],[10,2],[3,2]]) << 1
            if (self.reg[c_rs1] != 0):
                self.should_jump = True
                self.jmp_address = self.pc + off
                
            pr('r{} != 0 ? {} -> {:016X}'.format(c_rs1, self.should_jump, self.jmp_address))
        else:
            raise Exception(' - CIW-Type instruction not supported!')
            #self.parent.getSimulator().stop()

    def executeCJIns(self):
        op = self.decoded_ins
        ins = self.ins
        
        if (op == 'C.J'):
            off12 = compose_sign(ins, [[12,1],[8,1],[9,2],[6,1],[7,1],[2,1],[11,1],[3,3]]) << 1
            self.should_jump = True
            self.jmp_address = self.pc + off12
            pr('{} -> {:016X}'.format(off12, self.jmp_address))
            #self.functionEnter(self.jmp_address, True)
        else:
            raise Exception(' - CJ-Type instruction not supported!')
            #self.parent.getSimulator().stop()

    def executeCLIns(self):
        op = self.decoded_ins
        ins = self.ins

        c_rd = 8 + get_bits(ins, 2, 3)
        c_rs1 = 8 + get_bits(ins, 7, 3)
        
        if (op == 'C.LW'):
            off = compose(ins, [[5,1],[10,3],[6,1]]) << 2
            address = self.reg[c_rs1] + off
            v = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[c_rd] = signExtend(v, 32,64)  
            pr('r{} = [r{} + {}] -> [{}]={:08X}'.format(c_rd, c_rs1, off, self.addressFmt(address), self.reg[c_rd]))
        elif (op == 'C.LD'):
            off = compose(ins, [[5,2],[10,3]]) << 3
            address = self.reg[c_rs1] + off
            self.reg[c_rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('r{} = [r{} + {}] -> [{}]={:016X}'.format(c_rd, c_rs1, off, self.addressFmt(address), self.reg[c_rd]))
        elif (op == 'C.FLW'):
            off = compose(ins, [[5,1],[10,3],[6,1]]) << 2
            address = self.reg[c_rs1] + off
            self.freg[c_rd] = yield from self.virtualMemoryLoad(address, 32//8)
            pr('fr{} = [r{} + {}] -> {:016X}'.format(c_rd, c_rs1, off, self.freg[c_rd]))
        elif (op == 'C.FLD'):
            off = compose(ins, [[5,2],[10,3]]) << 3
            address = self.reg[c_rs1] + off
            self.freg[c_rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('fr{} = [r{} + {}] -> {:016X}'.format(c_rd, c_rs1, off, self.freg[c_rd]))
        else:
            raise Exception(' - CL-Type instruction not supported!')
            #self.parent.getSimulator().stop()


    def encodeFeatures(self, str):
        r = 0
        for c in str:
            r |= 1 << (ord(c)-65)
        return r
    
    def initStaticCSRs(self):
        # CSRs can be found here
        # https://people.eecs.berkeley.edu/~krste/papers/riscv-priv-spec-1.7.pdf
        # and here
        # https://web.cecs.pdx.edu/~harry/riscv/RISCV-Summary.pdf

        self.csr[CSR_MISA] = 2 << 62 | self.encodeFeatures('ACDIFMSU') # misa
        self.csr[CSR_MCPUID] = 2 << 62 | self.encodeFeatures('ACDIFMSU') # mcpuid
        self.csr[0xf10] = 0 # mhartid @todo is this wrong???

        self.csr[CSR_MVENDORID] = 0x414255 # UAB
        self.csr[CSR_MARCHID] = 0
        self.csr[CSR_MIMPID] = 0x70756e7861323431  # @todo should be reversed
        self.csr[CSR_MHARTID] = 0 # mhartid
        

        self.implemented_csrs[CSR_MCPUID] = 'mcpuid'
        self.implemented_csrs[CSR_MVENDORID] = 'mvendorid'
        self.implemented_csrs[CSR_MARCHID] = 'marchid'
        self.implemented_csrs[CSR_MIMPID] = 'mimpid'
        self.implemented_csrs[CSR_MHARTID] = 'mhartid'
        self.implemented_csrs[CSR_MCONFIGPTR] = 'mconfigptr'
        

    def initDynamicCSRs(self):

        self.implemented_csrs[CSR_MISA] = 'misa'
        self.implemented_csrs[CSR_FFLAGS] = 'fflags'
        self.implemented_csrs[CSR_FRM] = 'frm'
        
        self.csr[CSR_FRM] = CSR_FRM_RTZ
        
        self.implemented_csrs[CSR_FCSR] = 'fcsr'
        
        self.implemented_csrs[CSR_SSTATUS] = 'sstatus'
        self.implemented_csrs[CSR_SIE] = 'sie'
        self.implemented_csrs[0x105] = 'stvec'        
        self.implemented_csrs[0x106] = 'scounteren'
        
        self.implemented_csrs[CSR_SSCRATCH] = 'sscratch'
        self.implemented_csrs[CSR_SEPC] = 'sepc'
        self.implemented_csrs[CSR_SCAUSE] = 'scause'
        self.implemented_csrs[CSR_STVAL] = 'stval'
        self.implemented_csrs[CSR_SIP] = 'sip'
        self.implemented_csrs[CSR_STIMECMP] = 'stimecmp'
        self.implemented_csrs[CSR_STIMECMPH] = 'stimecmph'
        
        self.implemented_csrs[CSR_SATP] = 'satp'

        self.csr[CSR_MSTATUS] = CSR_MSTATUS_SXL_64_BITS_MASK | CSR_MSTATUS_UXL_64_BITS_MASK
        self.implemented_csrs[CSR_MSTATUS] = 'mstatus'
        
        self.implemented_csrs[0x302] = 'medeleg'
        self.implemented_csrs[0x303] = 'mideleg'
        self.implemented_csrs[0x304] = 'mie'
        self.implemented_csrs[0x305] = 'mtvec'
        self.implemented_csrs[0x306] = 'mcounteren'
        self.implemented_csrs[CSR_MENVCFG] = 'menvcfg'
        self.implemented_csrs[0x320] = 'mcountinhibit'

        for i in range(3,32):
            self.implemented_csrs[0x320+i] = 'mhpmevent{}'.format(i)


        self.implemented_csrs[0x340] = 'mscratch'
        self.implemented_csrs[0x341] = 'mepc'
        self.implemented_csrs[0x342] = 'mcause'
        self.implemented_csrs[CSR_MTVAL] = 'mtval'
        self.implemented_csrs[CSR_MIP] = 'mip'
        self.implemented_csrs[CSR_MBASE] = 'mbase'
        
        self.implemented_csrs[0x3A0] = 'pmpcfg0'
        self.implemented_csrs[0x3A2] = 'pmpcfg2'
        

        for i in range(16): # was 64 (not 1)
            self.implemented_csrs[0x3B0+i] = 'pmpaddr{}'.format(i)
        
        self.implemented_csrs[CSR_TSELECT] = 'tselect'
        self.implemented_csrs[CSR_TDATA1] = 'tdata1'
        self.implemented_csrs[CSR_TDATA2] = 'tdata2'
        self.implemented_csrs[CSR_TDATA3] = 'tdata3'
        self.implemented_csrs[CSR_TCONTROL] = 'tcontrol'
        self.implemented_csrs[CSR_MCONTEXT] = 'mcontext'

        self.implemented_csrs[CSR_MCYCLE] = 'mcycle'
        self.implemented_csrs[CSR_MINSTRET] = 'minstret'

        for i in range(3,32):
             self.implemented_csrs[0xB00+i] = 'mhpmcounter{}'.format(i)

        self.implemented_csrs[CSR_MNSCRATCH] = 'mnscratch'
        self.implemented_csrs[CSR_MNEPC] = 'mnepc'
        self.implemented_csrs[CSR_MNCAUSE] = 'mncause'
        self.implemented_csrs[CSR_MNSTATUS] = 'mnstatus'
        self.implemented_csrs[CSR_MSECCFG] = 'mseccfg'
 
        self.implemented_csrs[CSR_CYCLE] = 'cycle'
        self.implemented_csrs[CSR_TIME] = 'time'
        self.implemented_csrs[CSR_INSTRET] = 'instret'

        
        self.implemented_csrs[CSR_PRIVLEVEL] = 'privlevel'  # this is my own CSR to store the current privilege level

        self.csr[CSR_PRIVLEVEL] = CSR_PRIVLEVEL_MACHINE # (Machine =3, Supervisor = 1, User = 0)
        
    def getCSR(self, idx):
        return self.csr[idx]
    
    def getPc(self):
        return self.pc
    
    def getReg(self, r):
        return self.reg[r]
    
    def getFreg(self, r):
        return self.freg[r]
    
    def updateMIP(self):
        v = self.csr[CSR_MIP]
        
        if (self.csr[CSR_MIDELEG] & CSR_MIDELEG_STI_MASK):
            #v = v & ~CSR_MIP_STIP_MASK
            if (self.int_timer_machine.get() == 1):
                v = v | CSR_MIP_STIP_MASK
        else:
            v = v & ~CSR_MIP_MTIP_MASK
            if (self.int_timer_machine.get() == 1):
                v = v | CSR_MIP_MTIP_MASK
        
        if (self.csr[CSR_MIDELEG] & CSR_MIDELEG_SSI_MASK):
            #v = v & ~CSR_MIP_SSIP_MASK
            if (self.int_soft_machine.get() == 1):
                v = v | CSR_MIP_SSIP_MASK
        else:
            v = v &  ~CSR_MIP_MSIP_MASK
            if (self.int_soft_machine.get() == 1):
                v = v | CSR_MIP_MSIP_MASK

        if (self.csr[CSR_MIDELEG] & CSR_MIDELEG_SEI_MASK):
            if (self.int_ext_machine.get() == 1):
                v = v | CSR_MIP_SEIP_MASK

        v = v &  ~CSR_MIP_MEIP_MASK
        if (self.int_ext_machine.get() == 1):
            v = v | CSR_MIP_MEIP_MASK
                
        self.csr[CSR_MIP] = v
    
    def readCSR(self, idx):
        # Returns the value of the CSR, and if the access was allowed
        # Take into consideration that some accesses raise an exception, while others just do not return the value
        allowed = True
        if not(idx in self.implemented_csrs):
            raise InstructionAccessFault(' - CSR {:03X} not supported!'.format(idx))

        csrname = self.implemented_csrs[idx]

        v = self.csr[idx]
        
        if (idx in csr_mirrored.keys()):
            # do read special things            
            real_idx = csr_mirrored[idx]
            v = self.csr[real_idx] & csr_mirror_mask[idx]
        
        if (idx == CSR_SATP):
            if (self.csr[CSR_PRIVLEVEL] == CSR_PRIVLEVEL_SUPERVISOR) and (self.csr[CSR_MSTATUS] & CSR_MSTATUS_TVM_MASK):
                raise IllegalInstruction('Trying to read SATP with TVM', self.ins)
                
        if (getCSRPrivilege(idx) > self.csr[CSR_PRIVLEVEL]):
            raise IllegalInstruction('CSR priv: {}  current priv: {}'.format(getCSRPrivilege(idx), self.csr[CSR_PRIVLEVEL]), self.ins) 
            
        if (idx == CSR_TIME):
            address = 0x2000000 | 0xBFF8 # @todo should be configurable on creation 
            v = yield from self.memoryLoad64(address, 64//8)
            # make a copy for reports
            self.csr[CSR_TIME] = v
            
        if (idx == CSR_MIP):
            if (self.csr[CSR_MIDELEG] & CSR_MIDELEG_STI_MASK):
                #v = v & ~CSR_MIP_STIP_MASK
                if (self.int_timer_machine.get() == 1):
                    v = v | CSR_MIP_STIP_MASK
            else:
                v = v & ~CSR_MIP_MTIP_MASK
                if (self.int_timer_machine.get() == 1):
                    v = v | CSR_MIP_MTIP_MASK
            
            if (self.csr[CSR_MIDELEG] & CSR_MIDELEG_SSI_MASK):
                #v = v & ~CSR_MIP_SSIP_MASK
                if (self.int_soft_machine.get() == 1):
                    v = v | CSR_MIP_SSIP_MASK
            else:
                v = v &  ~CSR_MIP_MSIP_MASK
                if (self.int_soft_machine.get() == 1):
                    v = v | CSR_MIP_MSIP_MASK
                    
            if (self.csr[CSR_MIDELEG] & CSR_MIDELEG_SEI_MASK):
                if (self.int_ext_machine.get() == 1):
                    v = v | CSR_MIP_SEIP_MASK

            v = v &  ~CSR_MIP_MEIP_MASK
            if (self.int_ext_machine.get() == 1):
                v = v | CSR_MIP_MEIP_MASK
                
            self.csr[CSR_MIP] = v

        
        return v, allowed

    def writeCSR(self, idx, v):
        if not(idx in self.implemented_csrs):
            raise InstructionAccessFault(' - CSR {:03X} not supported!'.format(idx))

        csrname = self.implemented_csrs[idx]

        real_idx = idx
        
        if (self.csr_write_verbose):
            print(f'Write CSR[{idx:03X}] {csrname:10} = {v:16X}         pc: {self.pc:016X}')

        if (idx in csr_mirrored.keys()):
            # do read special things            
            real_idx = csr_mirrored[idx]
            v = (self.csr[real_idx] & ~csr_mirror_mask[idx]) | (v & csr_mirror_mask[idx])

        if ((real_idx in csr_fix_ro) or (real_idx in csr_var_ro)):
            #if (self.csr[CSR_PRIVLEVEL] == CSR_PRIVLEVEL_MACHINE):
            #    print('WARNING! trying to write read-only CSR {}'.format(csrname))
            #    return
            #else:
            #    raise IllegalInstruction('trying to write read-only CSR {}'.format(csrname), self.ins)
            raise IllegalInstruction('trying to write read-only CSR {}'.format(csrname), self.ins)
        
        # do write special things
        if (real_idx in csr_partial_wr_mask.keys()):
            v = (self.csr[real_idx] & (((1<<64)-1)^csr_partial_wr_mask[real_idx])) | (v & csr_partial_wr_mask[real_idx])
            
        if (real_idx == CSR_SATP):
            if (self.csr[CSR_PRIVLEVEL] == CSR_PRIVLEVEL_SUPERVISOR) and (self.csr[CSR_MSTATUS] & CSR_MSTATUS_TVM_MASK):
                raise IllegalInstruction('Trying to write SATP with TVM', self.ins)
            
            n = (v >> 60) & ((1<<4)-1)
            sn = ['Base', '','','','','','','','Sv39','Sv48','Sv57','Sv64'][n]
            
            if (sn != 'Sv39'):
                print('WARNING: trying to set VM mode', sn)
                return 
                
            root = (v & ((1<<44)-1)) << 12
            
            if (root == 0):
                # quick check for invalid SATP, if activating the VM causes an exception we should raise
                # the exception before, to tell that we are unable to access the instruction
                raise InstructionAccessFault(f'Trying to set an invalid root in SATP {root:016X}', self.ins)
                
        if (real_idx == CSR_FCSR):
            # write also in FFLAGS
            self.csr[CSR_FFLAGS] = v & ((1<<5)-1)
            
        if (real_idx == CSR_FFLAGS):
            self.csr[CSR_FCSR] = (self.csr[CSR_FCSR] & (((1<<64)-1) ^ ((1<<5)-1))) | (v & ((1<<5)-1))
        if (real_idx == CSR_FRM):
            self.csr[CSR_FCSR] = (self.csr[CSR_FCSR] & (((1<<64)-1) ^ CSR_FCSR_ROUNDING_MODE_MASK)) | (v << 5) 
        
        if (real_idx == CSR_TSELECT):
            # we only support 1 trigger context
            if (v != 0):
                return
            
        if (real_idx == CSR_TDATA1):
            xlen = 64
            tdata_type = get_bits(v, xlen-4, 4)
            self.debugTrigger = (tdata_type != 0)

        #print('CSR WRITE {} = {:016X}'.format(csrname, v))
        self.csr[real_idx] = v
        
    def setCSR(self, idx, v):
        allowed = True
        if not(idx in self.implemented_csrs):
            raise InstructionAccessFault(' - CSR {:03X} not supported!'.format(idx))

        csrname = self.implemented_csrs[idx]

        real_idx = idx
        if (idx in csr_mirrored.keys()):
            real_idx = csr_mirrored[idx]
        
        v = self.csr[real_idx] | v
        
        self.writeCSR(idx, v)

        
    
    def clearCSR(self, idx, v):
        allowed = True
        if not(idx in self.implemented_csrs):
            raise InstructionAccessFault(' - CSR {:03X} not supported!'.format(idx))

        csrname = self.implemented_csrs[idx]

        real_idx = idx
        if (idx in csr_mirrored.keys()):
            real_idx = csr_mirrored[idx]
        
        v = self.csr[real_idx] & (~v) 
        
        self.writeCSR(idx , v)
        
    
    def reserveAddress(self, add, count):
        self.reserved_address_start = add
        self.reserved_address_stop = add + count
        self.reserved_accessed = False        
        
    def checkReservedAddress(self, add, count):
        # activates the access flag is anyone access the range
        a = add
        b = add + count
        ra = self.reserved_address_start
        rb = self.reserved_address_stop
        if  (a < rb and b > ra):
            self.reserved_accessed = True
    
    def isReserved(self, add, count):
        if (self.reserved_accessed): return False
        a = add
        b = add + count
        ra = self.reserved_address_start
        rb = self.reserved_address_stop
        if (a >= ra and a < rb) and (b > ra and b <= rb):
            return True
        return False
            
    def clock(self):
        next(self.co)
        # @todo the acquisition of values should be done before the block edge
        self.v_mem_read_data = self.mem.read_data.get()
        self.v_mem_resp = self.mem.resp.get()
        
        self.mem.address.prepare(self.v_mem_address)        
        self.mem.read.prepare(self.v_mem_read)
        self.mem.write.prepare(self.v_mem_write)
        self.mem.write_data.prepare(self.v_mem_write_data)
        self.mem.be.prepare(self.v_mem_be)
        
        self.csr[CSR_CYCLE] += 1
