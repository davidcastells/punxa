# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 09:54:32 2023

@author: dcr


Info obtained from
https://uim.fei.stuba.sk/wp-content/uploads/2018/02/riscv-privileged-2022.pdf
should check latest in
https://drive.google.com/file/d/17GeetSnT5wW3xNuAHI95-SI1gPGd5sJ_/view?usp=drive_link


and
https://riscv.org/wp-content/uploads/2019/03/riscv-debug-release.pdf

Latest Debug Specification Used: 1.0.0-rc4
    https://github.com/riscv/riscv-debug-spec/releases/download/1.0.0-rc4/riscv-debug-specification.pdf

"""

#-----------------------------
# CSRs
#-----------------------------



CSR_FFLAGS =        0x001
CSR_FRM =           0x002
CSR_FCSR =          0x003

CSR_SSTATUS =       0x100
CSR_SIE =           0x104
CSR_STVEC =         0x105
CSR_SCOUNTEREN =    0x106
CSR_SSCRATCH =      0x140
CSR_SEPC =          0x141
CSR_SCAUSE =        0x142
CSR_STVAL =         0x143
CSR_SIP =           0x144
CSR_STIMECMP =      0x14D
CSR_STIMECMPH =     0x15D
CSR_SATP =          0x180

CSR_MSTATUS =       0x300
CSR_MISA =          0x301
CSR_MEDELEG =       0x302
CSR_MIDELEG =       0x303
CSR_MIE =           0x304
CSR_MTVEC =         0x305
CSR_MCOUNTEREN =    0x306
CSR_MENVCFG =       0x30A
CSR_MCOUNTINHIBIT = 0x320

CSR_MHPMEVENT3 =    0x323

#        for i in range(3,32):
#            self.implemented_csrs[0x320+i] = 'mhpmevent{}'.format(i)


CSR_MSCRATCH =      0x340
CSR_MEPC =          0x341
CSR_MCAUSE =        0x342
CSR_MTVAL =         0x343
CSR_MIP =           0x344
CSR_MBASE =         0x380
        
CSR_PMPCFG0 =       0x3A0
        
# for i in range(64):
#     self.implemented_csrs[0x3B0+i] = 'pmpaddr{}'.format(i)
        

# Machine non-maskable interrupt handling
CSR_MNSCRATCH =     0x740
CSR_MNEPC =         0x741
CSR_MNCAUSE =       0x742
CSR_MNSTATUS =      0x744
CSR_MSECCFG =       0x747

# Debug/Trace registers
CSR_TSELECT =       0x7A0
CSR_TDATA1 =        0x7A1
CSR_TDATA2 =        0x7A2
CSR_TDATA3 =        0x7A3
CSR_TINFO =         0x7A4
CSR_TCONTROL =      0x7A5
CSR_MCONTEXT =      0x7A8

CSR_MCYCLE =        0xB00
CSR_MINSTRET =      0xB02
CSR_MHPMCOUNTER3 =  0xB03

# for i in range(3,32):
#     self.implemented_csrs[0xB00+i] = 'mhpmcounter{}'.format(i)

CSR_CYCLE =         0xC00
CSR_TIME =          0xC01
CSR_INSTRET =       0xC02

CSR_MCPUID =        0xF00
CSR_MVENDORID =     0xF11   # Vendor ID
CSR_MARCHID =       0xF12   # Architecture ID
CSR_MIMPID =        0xF13   # Implementation ID
CSR_MHARTID =       0xF14   # Hardware thread ID
CSR_MCONFIGPTR =    0xF15   # pointer to configuration data structure

CSR_PRIVLEVEL =     0xFFF

# ------------------------------------

# Inmutable Read-only CSRs
csr_fix_ro = [CSR_MISA, CSR_MCPUID, CSR_MVENDORID, CSR_MARCHID, CSR_MIMPID, CSR_MHARTID, CSR_MCONFIGPTR] 

# Non writable CSR that CPU state can change
csr_var_ro = [CSR_CYCLE] 

# Writable CSR that CPU state can change
csr_var_rw = [CSR_FFLAGS] 

# Writable CSR not affected by CPU state
csr_unf_rw = []

# Mirrors of other CSRs depending on the privilege level
csr_mirrored = {CSR_SIE:CSR_MIE, CSR_SIP:CSR_MIP}



csr_partial_wr_mask = {CSR_MIE: 0xAAA, CSR_MIDELEG: 0x222}
csr_mirror_mask = {CSR_SIE:-1, CSR_SIP:-1} # @todo define the correct masks

# ------------------------------------

# 0x001 - FFLAGS
CSR_FFLAGS_INVALID_OPERATION_MASK = 16
CSR_FFLAGS_DIVIDE_BY_ZERO_MASK = 8
CSR_FFLAGS_OVERFLOW_MASK = 4
CSR_FFLAGS_UNDERFLOW_MASK = 2
CSR_FFLAGS_INEXACT_MASK = 1

# 0x002 - FRM
CSR_FRM_RNE = 0b000 # Round to nearest, ties to Even
CSR_FRM_RTZ = 0b001 # Round towards zero
CSR_FRM_RDN = 0b010 # Round towards -infinity 
CSR_FRM_RUP = 0b011 # Round towards infinity
CSR_FRM_RMM = 0b100 # Round to nearest, ties to max magnitude
CSR_FRM_DYN = 0x111 # Use instructions'm RM field

# 0x003 - FCSR
CSR_FCSR_ROUNDING_MODE_MASK = 0b111 << 5
CSR_FCSR_INVALID_OPERATION_MASK = 16
CSR_FCSR_DIVIDE_BY_ZERO_MASK = 8
CSR_FCSR_OVERFLOW_MASK = 4
CSR_FCSR_UNDERFLOW_MASK = 2
CSR_FCSR_INEXACT_MASK = 1

csr_partial_wr_mask[CSR_FCSR]= (1<<8)-1

# 0x100 - SSTATUS
CSR_SSTATUS_SD_MASK = (1 << 63)
CSR_SSTATUS_UXL_32_BITS_MASK = (1<<32)
CSR_SSTATUS_UXL_64_BITS_MASK = (2<<32)
CSR_SSTATUS_UXL_128_BITS_MASK = (3<<32)
CSR_SSTATUS_UXL_MASK = (3 << 32)
CSR_SSTATUS_MXR_MASK = (1 << 19)
CSR_SSTATUS_SUM_MASK = (1 << 18)
CSR_SSTATUS_XS_MASK = (3 << 15)
CSR_SSTATUS_FS_MASK = (3 << 13)
CSR_SSTATUS_SPP_MASK = (1 << 8)
CSR_SSTATUS_SPIE_MASK = (1 << 5)
CSR_SSTATUS_UPIE_MASK = (1 << 4)
CSR_SSTATUS_SIE_MASK = (1 << 1)
CSR_SSTATUS_UIE_MASK = (1 )

# This is the Read Subset from MSTATUS that SSTATUS see
csr_mirrored[CSR_SSTATUS] = CSR_MSTATUS
csr_mirror_mask[CSR_SSTATUS] =  CSR_SSTATUS_SD_MASK | CSR_SSTATUS_UXL_MASK |  CSR_SSTATUS_MXR_MASK | CSR_SSTATUS_SUM_MASK | CSR_SSTATUS_XS_MASK | CSR_SSTATUS_FS_MASK | CSR_SSTATUS_SPP_MASK | CSR_SSTATUS_SPIE_MASK | CSR_SSTATUS_UPIE_MASK | CSR_SSTATUS_SIE_MASK | CSR_SSTATUS_UIE_MASK

# 0x300 - MSTATUS
CSR_MSTATUS_SD_MASK = (1 << 63)

CSR_MSTATUS_FS_POS = 13 
CSR_MSTATUS_FS_MASK = (3 << CSR_MSTATUS_FS_POS)

CSR_MSTATUS_SXL_32_BITS_MASK = (1<<34)
CSR_MSTATUS_SXL_64_BITS_MASK = (2<<34)
CSR_MSTATUS_SXL_128_BITS_MASK = (3<<34)
CSR_MSTATUS_SXL_MASK = (3<<34)

CSR_MSTATUS_UXL_32_BITS_MASK = (1<<32)
CSR_MSTATUS_UXL_64_BITS_MASK = (2<<32)
CSR_MSTATUS_UXL_128_BITS_MASK = (3<<32)
CSR_MSTATUS_UXL_MASK = (3<<32)

CSR_MSTATUS_TSR_MASK = (1<<22)
CSR_MSTATUS_TW_MASK = (1<<21)
CSR_MSTATUS_TVM_MASK = (1<<20)

CSR_MSTATUS_MXR_MASK = (1<<19)
CSR_MSTATUS_SUM_MASK = (1<<18)

CSR_MSTATUS_MPRV_POS = 17
CSR_MSTATUS_MPRV_MASK = (1<<17) 

CSR_MSTATUS_XS_MASK = (3 << 15)
CSR_MSTATUS_FS_MASK = (3 << 13)

CSR_MSTATUS_MPP_POS = 11
CSR_MSTATUS_MPP_MASK = (3 << 11)

CSR_MSTATUS_SPP_POS = 8 
CSR_MSTATUS_SPP_MASK = (1 << 8)

CSR_MSTATUS_MPIE_POS = 7
CSR_MSTATUS_MPIE_MASK = (1<<7)
CSR_MSTATUS_SPIE_POS = 5
CSR_MSTATUS_SPIE_MASK = (1<<5)
CSR_MSTATUS_UPIE_MASK = (1<<4)

CSR_MSTATUS_MIE_POS = 3
CSR_MSTATUS_MIE_MASK = (1 << 3)
CSR_MSTATUS_SIE_POS = 1
CSR_MSTATUS_SIE_MASK = (1 << 1)
CSR_MSTATUS_UIE_MASK = (1)

csr_partial_wr_mask[CSR_MSTATUS] = CSR_MSTATUS_SD_MASK  | CSR_MSTATUS_TSR_MASK | CSR_MSTATUS_TW_MASK | CSR_MSTATUS_TVM_MASK | CSR_MSTATUS_MXR_MASK | CSR_MSTATUS_SUM_MASK | CSR_MSTATUS_MPRV_MASK | CSR_MSTATUS_FS_MASK | CSR_MSTATUS_MPP_MASK | CSR_MSTATUS_SPP_MASK | CSR_MSTATUS_MPIE_MASK | CSR_MSTATUS_SPIE_MASK | CSR_MSTATUS_UPIE_MASK | CSR_MSTATUS_MIE_MASK | CSR_MSTATUS_SIE_MASK | CSR_MSTATUS_UIE_MASK


# 0x303 - MIDELEG
CSR_MIDELEG_SSI_MASK = (1<<1) # supervisor software interrupt
CSR_MIDELEG_MSI_MASK = (1<<3)
CSR_MIDELEG_STI_MASK = (1<<5)
CSR_MIDELEG_MTI_MASK = (1<<7)
CSR_MIDELEG_SEI_MASK = (1<<9)
CSR_MIDELEG_MEI_MASK = (1<<11)
CSR_MIDELEG_COF_MASK = (1<<13)


# 0x304 - MIE  
CSR_MIE_MEIE_MASK = (1<<11)
CSR_MIE_SEIE_MASK = (1<<9)
CSR_MIE_UEIE_MASK = (1<<8)
CSR_MIE_MTIE_MASK = (1<<7)
CSR_MIE_STIE_MASK = (1<<5)
CSR_MIE_UTIE_MASK = (1<<4)
CSR_MIE_MSIE_MASK = (1<<3)
CSR_MIE_SSIE_MASK = (1<<1)
CSR_MIE_USIE_MASK = 1

# 0x344 - MIP
CSR_MIP_MEIP_MASK = (1<<11)
CSR_MIP_SEIP_MASK = (1<<9)
CSR_MIP_UEIP_MASK = (1<<8)
CSR_MIP_MTIP_MASK = (1<<7)
CSR_MIP_STIP_MASK = (1<<5)
CSR_MIP_UTIP_MASK = (1<<4)
CSR_MIP_MSIP_MASK = (1<<3)
CSR_MIP_SSIP_MASK = (1<<1)
CSR_MIP_USIP_MASK = 1

# 0x7A1 - TDATA1 
CSR_TDATA1_EXECUTE_MASK = (1 << 2)   
CSR_TDATA1_STORE_MASK = (1 << 1)
CSR_TDATA1_LOAD_MASK = (1)

# 0x7A5 - TCONTROL
CSR_TCONTROL_MTE_MASK = (1 << 3)
CSR_TCONTROL_MPTE_MASK = (1 << 7)

# 0xFFF - PRIVLEVEL
CSR_PRIVLEVEL_MACHINE = 3
CSR_PRIVLEVEL_SUPERVISOR = 1
CSR_PRIVLEVEL_USER = 0


def getCSRPrivilege(csr):
    return (csr >> 8) & 0x3

def clearCSRBits(cpu, csr, start, bits):
    v = cpu.csr[csr] & (((1<<bits)-1) << start)
    cpu.csr[csr] = cpu.csr[csr] ^ v 

def getCSRField(cpu, csr, start, bits):
    return (cpu.csr[csr] >> start) & ((1<<bits)-1) 
    
def setCSRField(cpu, csr, start, bits, value):
    clearCSRBits(cpu, csr, start, bits)
    v = cpu.csr[csr] | ((value & (1<<bits)-1) << start)
    cpu.csr[csr] = v
