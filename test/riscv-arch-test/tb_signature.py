import sys
import os


mem_width = 64



from punxa.memory import *
from punxa.bus import *
from punxa.uart import *
from punxa.clint import *
from punxa.plic import *
from punxa.gpio import *
from punxa.single_cycle.singlecycle_processor import *
from punxa.instruction_decode import *
from punxa.interactive_commands import *

import py4hw    
import py4hw.debug
import py4hw.gui as gui
import zlib

mem_base =  0x0080000000000000

    
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


    
from elftools.elf.elffile import ELFFile



    
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
#             |     |     +------+
#             |     |--G--| GPIO |
#             |     |     +------+
#             +-----+
#  | start               | stop                | device        |
#  | 0080 0000 0000 0000 | 0080 0000 FFFF FFFF | memory (2GB)  |
#  | 0000 00FF F0C2 C000 | 0000 00FF F0C2 CFFF | UART          |
#  | 0000 0000 0200 0000 | 0000 0000 0202 FFFF | CLINT         |
#  | 0000 0000 0C00 0000 | 0000 0000 0C0F FFFF | PLIC          |
#  | 0000 0000 0C00 0000 | 0000 0000 0C0F FFFF | GPIO          |

def buildHw():
    global memory
    global cpu
    global bus

    hw = HWSystem()

    port_c = MemoryInterface(hw, 'port_c', mem_width, 64)     # The whole address space
    port_m = MemoryInterface(hw, 'port_m', mem_width, 28)     # 20	bits = 
    port_u = MemoryInterface(hw, 'port_u', mem_width, 8)      # 8 bits = 256
    port_l = MemoryInterface(hw, 'port_l', mem_width, 16)      # 8 bits = 256
    port_p = MemoryInterface(hw, 'port_p', mem_width, 24)      # 8 bits = 256
    port_g = MemoryInterface(hw, 'port_g', mem_width, 8)      # 8 bits = 256
    #port_t = MemoryInterface(hw, 'port_t', mem_width, 8)     # 8 bits = 256
    # Memory initialization

    memory = SparseMemory(hw, 'main_memory', mem_width, 32, port_m, mem_base=mem_base)

    memory.reallocArea(0, 1 << 20, verbose=False)

    #test = ISATestCommunication(hw, 'test', mem_width, 8, port_t)


    # Uart initialization
    uart = Uart(hw, 'uart', port_u)


    int_soft = hw.wire('int_soft')
    int_timer = hw.wire('int_timer')

    int_dummy = hw.wire('int_dummy')
    py4hw.Constant(hw, 'dummy', 0, int_dummy)
    
    int_gpio = hw.wire('int_gpio')
    
    gpio = GPIO(hw, 'gpio', port_g, int_gpio)

    ext_int_sources = [int_dummy, int_dummy, int_dummy, int_gpio]

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
                                          (port_u, 0x0010000000),
                                          (port_p, 0x000C000000),
                                          (port_l, 0x0002000000),
                                          (port_g, 0x0010060000)])

    cpu = SingleCycleRISCV(hw, 'RISCV', port_c, int_soft, int_timer, ext_int_targets, mem_base)

    cpu.behavioural_memory = memory
    cpu.min_clks_for_trace_event = 1000

    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    punxa.interactive_commands._ci_bus = bus
    
    return hw

def reportInterrupts():
    print('Interrupt Status')
    print(' CPU:') # be prepared for multiple CPUs

    timer_wire = cpu.int_timer_machine.get()
    soft_wire = cpu.int_soft_machine.get()
    ext_m_wire = cpu.int_ext_machine.get()    
    ext_s_wire = cpu.int_ext_supervisor.get()    
    
    mideleg_mt = 1 if (cpu.csr[CSR_MIDELEG] & CSR_MIDELEG_MTI_MASK) else 0
    mideleg_st = 1 if (cpu.csr[CSR_MIDELEG] & CSR_MIDELEG_STI_MASK) else 0

    meip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_MEIP_MASK) else 0
    seip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_SEIP_MASK) else 0
    ueip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_UEIP_MASK) else 0
        
    mtip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_MTIP_MASK) else 0
    stip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_STIP_MASK) else 0
    utip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_UTIP_MASK) else 0

    msip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_MSIP_MASK) else 0
    ssip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_SSIP_MASK) else 0
    usip = 1 if (cpu.csr[CSR_MIP] & CSR_MIP_USIP_MASK) else 0

    meie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_MEIE_MASK) else 0
    seie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_SEIE_MASK) else 0
    ueie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_UEIE_MASK) else 0

    mtie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_MTIE_MASK) else 0
    stie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_STIE_MASK) else 0
    utie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_UTIE_MASK) else 0

    msie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_MSIE_MASK) else 0
    ssie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_SSIE_MASK) else 0
    usie = 1 if (cpu.csr[CSR_MIE] & CSR_MIE_USIE_MASK) else 0
    
    mie = 1 if (cpu.csr[CSR_MSTATUS] & CSR_MSTATUS_MIE_MASK) else 0
    sie = 1 if (cpu.csr[CSR_MSTATUS] & CSR_MSTATUS_SIE_MASK) else 0
    uie = 1 if (cpu.csr[CSR_MSTATUS] & CSR_MSTATUS_UIE_MASK) else 0

    time = hw.children['clint'].mtime        
    timecmp = hw.children['clint'].mtimecmp
    
    tcmp = '<' if time < timecmp else '>='
            
    time_csr = cpu.csr[CSR_TIME]
    
    nclks_to_interrupt = timecmp - time
    seconds_to_interrupt = nclks_to_interrupt / 50E6
        
    gpio = hw.children['gpio']
    gpio_int = hw.children['gpio'].interrupt.get()
    
    
    
    print(f'   CLINT')  
    print(f'   time: {time:016X} {tcmp} {timecmp:016X} : timecmp ')
    print(f'   Interrupt {nclks_to_interrupt} clks away ({seconds_to_interrupt} seconds)')
    print()
    print(f'   GPIO')  
    print(f'   oval:{gpio.oval:08X} oe:{gpio.oe:08X}' )
    print(f'   ival:{gpio.ival:08X} ie:{gpio.ie:08X}  value:{gpio.value:08X}' )
    print(f'   hip: {gpio.hip:08X} hie: {gpio.hie:08X}  ')
    print(f'   lip: {gpio.lip:08X} hie: {gpio.lie:08X}  ')
    print(f'   rip: {gpio.rip:08X} rie: {gpio.rie:08X}  ')
    print(f'   fip: {gpio.fip:08X} fie: {gpio.fie:08X}  ')
    print(f'   Interrupt {gpio_int}')
    print()
    print(f'   PLIC')

    for idx, target in enumerate(hw.children['plic'].int_targets):
        priority_th = hw.children['plic'].int_context_priority_th[idx]
    
        for sidx, source in enumerate(hw.children['plic'].int_sources):
            priority = hw.children['plic'].int_source_priority[sidx]
            ie = hw.children['plic'].ie[idx][sidx]
            print(f'   source {sidx} [{source.get()}] priority:[{priority}] IE:[{ie}]')

        print(f'   --> target {idx} [{target.get()}] pri.th:[{priority_th}]')
        print('   ------------------------------')
        
    
    print()
    print(f'   CSRs')  
    print(f'   time: {time_csr:016X}')
    if (mideleg_st):
        print(f'         MIDELEG     MIP          MIE       MSTATUS')
        print(f'   timer [{timer_wire}]    MTIP [{mtip}] --> MTIE [{mtie}] --> MIE [{mie}]')
        print(f'            \-> STIP [{stip}] --> STIE [{stie}] --> SIE [{sie}]')
        print(f'   sw-i  [{soft_wire}]--> MSIP [{msip}] --> MSIE [{msie}] --> MIE [{mie}]')
        print(f'       (sw) --> SSIP [{ssip}] --> SSIE [{ssie}] --> SIE [{sie}]')
        print(f'   ext-M [{ext_m_wire}]--> MEIP [{meip}] --> MEIE [{meie}] --> MIE [{mie}]')
        print(f'   ext-S [{ext_s_wire}]--> SEIP [{seip}] --> SEIE [{seie}] --> SIE [{sie}]')

    else:
        print(f'         MIDELEG     MIP          MIE       MSTATUS')
        print(f'   timer [{timer_wire}]--> MTIP [{mtip}] --> MTIE [{mtie}] --> MIE [{mie}]')
        print(f'       (sw) --> STIP [{stip}] --> STIE [{stie}] --> SIE [{sie}]')
        
        print(f'   sw-i  [{soft_wire}]--> MSIP [{msip}] --> MSIE [{msie}] --> MIE [{mie}]')
        print(f'       (sw) --> SSIP [{ssip}] --> SSIE [{ssie}] --> SIE [{sie}]')
        print(f'   ext-M [{ext_m_wire}]--> MEIP [{meip}] --> MEIE [{meie}] --> MIE [{mie}]')
        print(f'   ext-S [{ext_s_wire}]--> SEIP [{seip}] --> SEIE [{seie}] --> SIE [{sie}]')

def reallocMem(add, size):
    memory.reallocArea(add - mem_base, size)

def prepareTest(test_file, verbose=True):
    global hw
    hw = buildHw()
    programFile = test_file
    
    loadElf(memory, programFile, mem_base , verbose) # 32*4 - 0x10054)
    loadSymbolsFromElf(cpu, programFile, 0)
    loadSymbolsFromElf(cpu, programFile, 0xffffffff7fe00000)    # for virtual memory tests
    
    reallocMem(0x87FFF000, 0x400)
    reallocMem(0x80200000, 0x10000)
    reallocMem(0x84212348, 0x400)

    
    a2f, f2a = getSymbolsFromElf(elf_file, 0)

    start = f2a['begin_signature'][0]
    end = f2a['end_signature'][0]

    i = 1
    add = start + 4
    
    while (add < end):
        cpu.funcs[add] = f'test_result_{i}'
        i += 1
        add += 4


def runTest(test_file, verbose=False):
    prepareTest(test_file)
    #passAdr = findFunction('pass')
    triggerFunc = findFunction('write_tohost')
    
    if (triggerFunc is None):
        # Try with terminate
        triggerFunc = findFunction('terminate')
        
    tohost_adr = findFunction('tohost')

    if (tohost_adr is None):
        print('tohost symbol not found in', cpu.funcs)
        return

    #run(passAdr, verbose=False)
    run(triggerFunc, maxclks=100000, verbose=verbose)
    run(0, maxclks=20, verbose=False)

    # print('Test', test_file, end='')
    #if (cpu.pc != passAdr):
    value = memory.readByte(tohost_adr-mem_base)
    
    if (value != 1):
        raise Exception('Test return value = {}'.format(value))
    else:
        print('Test return value = {}'.format(value))



def asciiProgressBar(n, t):
    p = n*100/t
    pl = 45
    pok = math.ceil(pl*n/t)
    pko = pl - pok
    sok = '█' * pok
    sko = '░' * pko
    sp = '{:.1f} %'.format(p)
    s = '{:8} |{}{}|'.format(sp,sok,sko)
    return s
    
def runAllTests():
    nOK = 0
    nTotal = 0
    ret = computeAllTests()
    
    groupResults = {}
    
    for prefix in selected_prefixes:
        nOKGroup = 0
        nTotalGroup = 0

        files = [name for name in ret.keys() if name.startswith(prefix) ]
        for t in files:
            nTotal += 1
            nTotalGroup += 1
            if (ret[t] =='OK'):
                 print('Test {:30} = {}'.format(t, ret[t]))
                 nOK += 1
                 nOKGroup += 1
            else:
                 print('Test {:30} = {} - {}'.format(t, ret[t][0], ret[t][1]))

        groupResults[prefix]=(nOKGroup, nTotalGroup)
        
    print('Total: {} Correct: {} ({:.1f} %)'.format(nTotal, nOK, nOK*100/nTotal))     
    print(asciiProgressBar(nOK, nTotal))

    for prefix in selected_prefixes:
        nOKGroup = groupResults[prefix][0]
        nTotalGroup = groupResults[prefix][1]
        print('Group: {} Total: {} Correct: {} ({:.1f} %)'.format(prefix, nTotalGroup, nOKGroup, nOKGroup*100/nTotalGroup))     

    for prefix in selected_prefixes:
        nOKGroup = groupResults[prefix][0]
        nTotalGroup = groupResults[prefix][1]
        print(f'{prefix:15}', asciiProgressBar(nOKGroup, nTotalGroup))
        
        
def startsWith(s, p):
    return s[0:len(p)] == p
    
def parseArgs(args):
    global signature_file
    global signature_granularity
    global elf_file
    global doPrepare
    global mem_base
    
    doPrepare = False
    
    i = 1
    while i < len (args):
        arg = args[i]

        #print('param' , i, arg)
        
        if (startsWith(arg, '+signature=')):
            signature_file = arg[len('+signature='):]
            print('Signature File=', signature_file)
        elif (startsWith(arg, '+signature-granularity=')):
            signature_granularity = int(arg[len('+signature-granularity='):])
            print('Signature granularity=', signature_granularity)
        elif (arg == '-prepare'):
            doPrepare = True
        elif (startsWith(arg, '-mem_base=')):
            mem_base = eval(arg[len('-mem_base='):])
        else:
            elf_file = arg
            print('Elf file=', elf_file)
            
        i += 1        
        
if __name__ == "__main__":
    global signature_file
    global signature_granularity
    global elf_file
    global doPrepare

    parseArgs(sys.argv)
    

    
    try:
        if (doPrepare):
            prepareTest(elf_file)
        else:
            runTest(elf_file)
            
    except:
        print('ERROR! Program failed\n')
    
    if not(doPrepare):
        a2f, f2a = getSymbolsFromElf(elf_file, 0)
    
        start = f2a['begin_signature'][0]
        end = f2a['end_signature'][0]
            
        text = ''
        
        if (signature_granularity == 4):
            for i in range(start, end, 4):
                v = memory.read_i32(i-mem_base)
                
                if (v == 0xDEADBEEF):
                    break

                #print(f'add {i:016X} = {v:016X} ')
                text += f'{v:08x}\n'                
        elif (signature_granularity == 8):
            for i in range(start, end, 8):
                v = memory.read_i64(i-mem_base)
                #print(f'add {i:016X} = {v:016X} ')
                text += f'{v:016x}\n'
        else:
            raise Exception(f'invalid granularity {signature_granularity}')
                
        with open(signature_file, 'w') as file:
            file.write(text)

