# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 09:54:32 2023

@author: dcr


Latest info obtained from
https://uim.fei.stuba.sk/wp-content/uploads/2018/02/riscv-privileged-2022.pdf

"""

#-----------------------------
# CSRs
#-----------------------------


CSR_MISA = 0x301

CSR_FFLAGS = 0x001
CSR_FRM = 0x002
CSR_FCSR = 0x003

CSR_SSTATUS = 0x100
CSR_SIE = 0x104
CSR_STVEC = 0x105
CSR_SCOUNTEREN = 0x106
CSR_SSCRATCH = 0x140
CSR_SEPC = 0x141
CSR_SCAUSE = 0x142
CSR_STVAL = 0x143
CSR_SIP = 0x144
CSR_SATP = 0x180

CSR_MSTATUS = 0x300
CSR_MEDELEG = 0x302
CSR_MIDELEG = 0x303
CSR_MIE = 0x304
CSR_MTVEC = 0x305
CSR_MCOUNTEREN = 0x306
CSR_MCOUNTINHIBIT = 0x320

CSR_MHPMEVENT3 = 0x323
#        for i in range(3,32):
#            self.implemented_csrs[0x320+i] = 'mhpmevent{}'.format(i)


CSR_MSCRATCH = 0x340
CSR_MEPC = 0x341
CSR_MCAUSE = 0x342
CSR_MTVAL = 0x343
CSR_MIP = 0x344
CSR_MBASE = 0x380
        
CSR_PMPCFG0 = 0x3A0
        
# for i in range(64):
#     self.implemented_csrs[0x3B0+i] = 'pmpaddr{}'.format(i)
        

# Machine non-maskable interrupt handling
CSR_MNSCRATCH = 0x740
CSR_MNEPC =     0x741
CSR_MNCAUSE =   0x742
CSR_MNSTATUS =  0x744

CSR_MCYCLE =    0xB00
CSR_MINSTRET =  0xB02

# for i in range(3,32):
#     self.implemented_csrs[0xB00+i] = 'mhpmcounter{}'.format(i)

CSR_CYCLE =     0xC00
CSR_TIME =      0xC01
CSR_INSTRET =   0xC02

CSR_MCPUID =    0xf00
CSR_MVENDORID = 0xF11
CSR_MARCHID =   0xF12
CSR_MIMPID =    0xF13
CSR_MHARTID =   0xf14

CSR_PRIVLEVEL = 0xFFF

# ------------------------------------

# Inmutable Read-only CSRs
csr_fix_ro = [CSR_MISA, CSR_MCPUID, CSR_MHARTID] 

# Non writable CSR that CPU state can change
csr_var_ro = [CSR_CYCLE] 

# Writable CSR that CPU state can change
csr_var_rw = [CSR_FFLAGS] 

# Writable CSR not affected by CPU state
csr_unf_rw = []

# Mirrors of other CSRs depending on the privilege level
csr_priv_mirror = [CSR_SSTATUS]

csr_partial_wr_mask = {}
csr_mirror_mask = {}

# ------------------------------------

# 0x001 - FFLAGS
CSR_FFLAGS_INVALID_OPERATION_MASK = 16
CSR_FFLAGS_DIVIDE_BY_ZERO_MASK = 8
CSR_FFLAGS_OVERFLOW_MASK = 4
CSR_FFLAGS_UNDERFLOW_MASK = 2
CSR_FFLAGS_INEXACT_MASK = 1

# 0x002 - FRM
CSR_FRM_RNE = 0b000
CSR_FRM_RTZ = 0b001
CSR_FRM_RDN = 0b010
CSR_FRM_RUP = 0b011
CSR_FRM_RMM = 0b100

# 0x003 - FCSR
CSR_FCSR_ROUNDING_MODE_MASK = 0b111 << 5
CSR_FCSR_INVALID_OPERATION_MASK = 16
CSR_FCSR_DIVIDE_BY_ZERO_MASK = 8
CSR_FCSR_OVERFLOW_MASK = 4
CSR_FCSR_UNDERFLOW_MASK = 2
CSR_FCSR_INEXACT_MASK = 1

csr_partial_wr_mask[CSR_FCSR]= (1<<8)-1

# 0x100 - SSTATUS
CSR_SSTATUS_UXL_32_BITS_MASK = (1<<32)
CSR_SSTATUS_UXL_64_BITS_MASK = (2<<32)
CSR_SSTATUS_UXL_128_BITS_MASK = (3<<32)

csr_mirror_mask[CSR_SSTATUS] = CSR_SSTATUS_UXL_128_BITS_MASK 

# 0x300 - MSTATUS
CSR_MSTATUS_FS_POS = 13 
CSR_MSTATUS_FS_MASK = (3 << CSR_MSTATUS_FS_POS)

CSR_MSTATUS_SXL_32_BITS_MASK = (1<<34)
CSR_MSTATUS_SXL_64_BITS_MASK = (2<<34)
CSR_MSTATUS_SXL_128_BITS_MASK = (3<<34)

CSR_MSTATUS_UXL_32_BITS_MASK = (1<<32)
CSR_MSTATUS_UXL_64_BITS_MASK = (2<<32)
CSR_MSTATUS_UXL_128_BITS_MASK = (3<<32)

CSR_MSTATUS_MPIE = (1<<7)

csr_partial_wr_mask[CSR_MSTATUS]= (1<<23)-1

# 0x344 - MIP
CSR_MIP_MEIP_MASK = (1<<11)
CSR_MIP_MTIP_MASK = (1<<7)
CSR_MIP_MSIP_MASK = (1<<3)


# 0xFFF - PRIVLEVEL
CSR_PRIVLEVEL_MACHINE = 3
CSR_PRIVLEVEL_SUPERVISOR = 1
CSR_PRIVLEVEL_USER = 0


def getCSRPrivilege(csr):
    return (csr >> 8) & 0x3

