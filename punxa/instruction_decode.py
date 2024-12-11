# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 10:41:17 2022

@author: dcr
"""

from .processor_exceptions import *

#|   31 - 27     | 26-25 | 24 - 20 | 19 - 15 | 14 - 12 | 11 - 7      |  6 - 0 | Instruction Type |
#|-----------------------|---------|---------|---------|-------------|--------|------------------|
#| funct7                | rs2     | rs1     | funct3  | rd          | opcode | R-Type           |
#| funct5        | func2 | rs2     | rs1     | funct3  | rd          | opcode | R4-Type          |
#| imm[11:0]                       | rs1     | funct3  | rd          | opcode | I-Type           |
#| imm[11:5]             | rs2     | rs1     | funct3  | imm[4:0]    | opcode | S-Type           |
#| imm[12|10:5]          | rs2     | rs1     | funct3  | imm[4:1|11] | opcode | B-Type           |
#| imm[31:12]                                          | rd          | opcode | U-Type           |
#| imm[20|10:1|11|19:12]                               | rd          | opcode | J-Type           |

#|  15 - 13  | 12 | 11 - 7     |  6 - 2    |  1 - 0   | Instruction Type |
#|----------------|------------|-----------|----------|------------------|
#| func3_c   |  imm            | r25_c     | opcode_c | CSS              |
 
rv32i_instructions = ['LUI','AUIPC','JAL','JALR','BEQ','BNE','BLT','BGE','BLTU', 
                      'BGEU','LB','LH','LW','LBU','LHU','SB','SH','SW','ADDI',
                      'SLTI','SLTIU','XORI','ORI','ANDI','SLLI','SRLI','SRAI',
                      'ADD','SUB','SLL','SLT','SLTU','XOR','SRL','SRA','OR','AND',
                      'FENCE', 'FENCE.I','ECALL','EBREAK','CSRRW','CSRRS','CSRRC',
                      'CSRRWI','CSRRSI','CSRRCI',
                      # I add privileged instructions here
                      'URET', 'SRET', 'MRET', 'WFI', 'SFENCE.VMA'
                      ]

rv32m_instructions = ['MUL','MULH','MULHSU','MULHU','DIV','DIVU','REM','REMU']  

rv32f_instructions = ['FLW','FSW','FMADD.S','FMSUB.S','FNMSUB.S','FNMADD.S',
                      'FADD.S','FSUB.S','FMUL.S','FDIV.S','FSQRT.S','FSGNJ.S',
                      'FSGNJN.S','FSGNJX.S',
                      'FMIN.S','FMAX.S',
                      'FMIN.H','FMAX.H',
                      'FCVT.W.S',
                      'FCVT.WU.S','FMV.X.W','FEQ.S','FLT.S','FLE.S','FCLASS.S',
                      'FCVT.S.W','FCVT.S.WU','FCVT.S.H',
                      'FMV.W.X']

rv32d_instructions = ['FLD', 'FSD', 'FMADD.D', 'FMSUB.D', 'FNMSUB.D', 'FNMADD.D',
                      'FADD.D', 'FSUB.D', 'FMUL.D', 'FDIV.D', 'FSQRT.D', 'FSGNJ.D',
                      'FSGNJN.D', 'FSGNJX.D', 'FMIN.D', 'FMAX.D', 'FCVT.S.D',
                      'FCVT.D.S', 'FEQ.D', 'FLT.D', 'FLE.D', 'FCLASS.D', 'FCVT.W.D',
                      'FCVT.WU.D', 'FCVT.D.W', 'FCVT.D.WU' ]

rv32a_instructions = ['LR.W','SC.W','AMOSWAP.W','AMOADD.W','AMOXOR.W','AMOAND.W','AMOOR.W','AMOMIN.W','AMOMAX.W','AMOMINU.W','AMOMAXU.W']
        
    
# 'SLLI','SRLI' appear in the table for RV64I, but are already part of RV32I
rv64i_instructions = ['LWU','LD','SD','ADDIW','SLLIW','SRLIW','SRAIW','ADDW','SUBW','SLLW','SRLW','SRAW']

rv64m_instructions = ['MULW', 'DIVW', 'DIVUW', 'REMW', 'REMUW']

rv64f_instructions = ['FCVT.L.S','FCVT.LU.S','FCVT.S.L','FCVT.S.LU']

rv64a_instructions = ['LR.D','SC.D','AMOSWAP.D','AMOADD.D','AMOXOR.D','AMOAND.D','AMOOR.D','AMOMIN.D','AMOMAX.D','AMOMINU.D','AMOMAXU.D',]

rvc_instructions = ['C.ADDI4SPN', 'C.FLD', 'C.LQ', 'C.LW', 'C.FLW', 'C.LD', 'C.FSD', 'C.SQ', 'C.SW', 'C.FSW', 'C.SD',
                    'C.NOP', 'C.ADDI', 'C.JAL', 'C.ADDIW', 'C.LI', 'C.ADDI16SP', 'C.LUI', 'C.SRLI', 'C.SRLI64', 'C.SRAI', 
                    'C.SRAI64', 'C.ANDI', 'C.SUB', 'C.XOR', 'C.OR', 'C.AND', 'C.SUBW', 'C.ADDW',
                    'C.J', 'C.BEQZ', 'C.BNEZ', 'C.SLLI', 'C.SLLI64', 'C.FLDSP', 'C.LQSP', 'C.LWSP',
                    'C.FLWSP', 'C.LDSP', 'C.JR', 'C.MV', 'C.EBREAK', 'C.JALR', 'C.ADD', 'C.FSDSP',
                    'C.SQSP', 'C.SWSP', 'C.FSWSP', 'C.SDSP']


rvzbb_instructions = ['CLZ','CTZ','PCNT','ANDN','ORC','XORC','MIN','MAX','MINU','MAXU','CLZW','CTZW']

rvzfh_instructions = ['FLH', 'FADD.H', 'FCVT.S.H', 'FCVT.D.H','FSQRT.H', 'FMSUB.H', 'FNMSUB.H']

# All instructions dealing with FPU
fpu_instructions = []
fpu_instructions.extend(rv32f_instructions)
fpu_instructions.extend(rv32d_instructions)
fpu_instructions.extend(rv64f_instructions)
fpu_instructions.extend(rvzfh_instructions)

    
RTypeIns = ['AND','OR','XOR', 'XNOR',
            'ADD','ADD.UW','SUB',
            'MUL', 'MULH', 'MULHU', 'MULHSU', 'MULW',
            'CLMUL','CLMULH', 'CLMULR',
            'DIV', 'DIVU', 'DIVW', 'DIVUW', 'REM', 'REMU', 'REMW', 'REMUW',
            'ROL','ROLW','ROR','RORW','SLL','SLT','SLTU','SRA','SRL',
            'FADD.H','FSUB.H','FMUL.H','FDIV.H','FMIN.H','FMAX.H','FCLASS.H','FEQ.H','FLT.H','FLE.H','FSQRT.H',
            'FADD.S','FSUB.S','FMUL.S','FDIV.S','FMIN.S','FMAX.S','FCLASS.S','FEQ.S','FLT.S','FLE.S','FSQRT.S',
            'FADD.D','FSUB.D','FMUL.D','FDIV.D','FMIN.D','FMAX.D','FCLASS.D','FEQ.D','FLT.D','FLE.D','FSQRT.D',
            'FCVT.W.H','FCVT.W.S','FCVT.W.D','FCVT.WU.H','FCVT.WU.S','FCVT.WU.D',  
            'FCVT.L.H','FCVT.L.S','FCVT.L.D','FCVT.LU.H','FCVT.LU.S','FCVT.LU.D',
            'FCVT.H.S','FCVT.H.D','FCVT.H.W','FCVT.H.WU','FCVT.H.L','FCVT.H.LU',
            'FCVT.S.H', 'FCVT.S.D','FCVT.S.W','FCVT.S.WU','FCVT.S.L','FCVT.S.LU',
            'FCVT.D.S','FCVT.D.H','FCVT.D.L','FCVT.D.LU','FCVT.D.W','FCVT.D.WU',
            'LR.W', 'SC.W','LR.D', 'SC.D',
            'AMOSWAP.W','AMOADD.W','AMOAND.W','AMOOR.W','AMOXOR.W','AMOMAX.W','AMOMIN.W','AMOMAXU.W','AMOMINU.W',
            'AMOSWAP.D','AMOADD.D','AMOAND.D','AMOOR.D','AMOXOR.D','AMOMAX.D','AMOMIN.D','AMOMAXU.D','AMOMINU.D',
            'ADDW','SLLW','SRLW','SUBW','SRAW',
            'SFENCE.VMA',
            'ANDN','ORN','ORC','XORC','MIN','MAX','MINU','MAXU', 
            'ZEXT.H', 
            'SH1ADD','SH1ADD.UW','SH2ADD','SH2ADD.UW','SH3ADD','SH3ADD.UW',
            'BEXT','BINV','BSET', 'BCLR']
R4TypeIns = ['FMADD.S', 'FMSUB.S', 'FNMSUB.S', 'FNMADD.S',
             'FMADD.D', 'FMSUB.D', 'FNMSUB.D', 'FNMADD.D',
             'FMADD.H', 'FMSUB.H', 'FNMSUB.H', 'FNMADD.H',
             'FSGNJ.S', 'FSGNJN.S', 'FSGNJX.S',
             'FSGNJ.D', 'FSGNJN.D', 'FSGNJX.D',
             'FSGNJ.H', 'FSGNJN.H', 'FSGNJX.H',
             'FMV.X.W', 'FMV.W.X', 
             'FMV.X.H', 'FMV.H.X',
             'FMV.D.X', 'FMV.X.D']
             
ITypeIns = ['JALR','LB','LH','LW','LWU','LBU','LHU','LD','ADDI','SLTI','SLTIU',
            'XORI', 'ADDIW', 'ORI','ANDI',
            'SLLI','SLLI.UW','SRLI','SRAI','SLLIW','SRLIW','SRAIW','RORI','RORIW',
            'CSRRW','CSRRS','CSRRC','CSRRWI','CSRRSI','CSRRCI',
            'WFI', 'MRET', 'SRET', 'URET', 'ECALL', 'EBREAK',
            'FLD','FLW', 'FLH',
            'CLZ', 'CTZ','CPOP','CPOPW','CLZW','CTZW', 'SEXT.B', 'SEXT.H', 
            'BEXTI','BINVI','BSETI', 'BCLRI','GREVI','GORCI',
            'CBO.CLEAN', 'CBO.FLUSH', 'CBO.INVAL', 'CBO.ZERO']
            
STypeIns = ['SB','SH','SW','SD', 'FSD', 'FSW','FSH']
BTypeIns = ['BEQ','BNE','BLT','BGE','BLTU','BGEU']
UTypeIns = ['LUI','AUIPC']
JTypeIns = ['JAL']
CSRRIns   = ['CSRRW','CSRRS','CSRRC']
CSRIIns   = ['CSRRWI','CSRRSI','CSRRCI']

CRTypeIns = ['C.ADD', 'C.MV', 'C.EBREAK','C.JR','C.JALR', 'C.JAL']
CITypeIns = ['C.NOP', 'C.LWSP', 'C.LDSP', 'C.SLLI',
             'C.LQSP', 'C.FLWSP', 'C.FLDSP', 'C.LI', 'C.LUI',
             'C.ADDI','C.ADDIW','C.ADDI16SP']
CIWTypeIns = ['C.ADDI4SPN']
CLTypeIns = ['C.LW', 'C.LD', 'C.LQ', 'C.FLW', 'C.FLD']
CSTypeIns = ['C.AND', 'C.OR', 'C.XOR', 'C.SUB', 'C.ADDW', 'C.SUBW',
             'C.SW','C.SD','C.SQ','C.FSW', 'C.FSD']
CSSTypeIns = ['C.SWSP','C.SDSP','C.SQSP','C.FSWSP','C.FSDSP']
CBTypeIns = ['C.ANDI','C.BEQZ', 'C.BNEZ','C.SRLI','C.SRAI']
CJTypeIns = ['C.J']

CustomTypeIns = ['CUSTOM0', 'CUSTOM1', 'CUSTOM2', 'CUSTOM3' ]

def is_compact_ins(ins):
    opcode_c = ins & 0x03
    if (opcode_c == 0x03):
        return False
    return True

def ins_to_str(ins, isa=32):
    ins16 = ins & 0xFFFF
    opcode_c = ins & 0x03
    opcode = ins & 0x7F
    func2 = (ins >> 25) & 0x3
    func3 = (ins >> 12) & 0x7
    func3_c = (ins >> 13) & 0x7
    func5 = (ins >> 27) & 0x1F
    func6 = (ins >> 26) & 0x3F
    func7 = (ins >> 25) & 0x7F
    rs2 = (ins >> 20) & 0x1F
    rd5_c = (ins >> 7) & 0x1F
    rdu2_c = (ins >> 10) & 0x03
    r2u2_c = (ins >> 5) & 0x03
    r25_c = (ins >> 2) & 0x1F
    imm1_c = ((ins >> 12) & 0x1) 
    imm5_c = (((ins >> 12) & 0x1) << 5) | ((ins >> 2) & 0x1F)
    imm3_c = (((ins >> 12) & 0x1) << 2) | ((ins >> 5) & 0x03)
    imm12 = (ins >> 20) & 0xFFF
    
    if (ins16 == 0x00):
        raise IllegalInstruction('Illegal Instruction', ins)
        
    if (opcode_c == 0x00):
        if (func3_c == 0x00): return 'C.ADDI4SPN'
        if (func3_c == 0x01):
            if (isa == 128):
                return 'C.LQ'
            return 'C.FLD' 
        if (func3_c == 0x02): return 'C.LW'
        if (func3_c == 0x03): 
            if (isa == 32):
                return 'C.FLW' 
            return 'C.LD'
        if (func3_c == 0x05):
            if (isa == 128):
                return 'C.SQ'
            return 'C.FSD' 
        if (func3_c == 0x06): return 'C.SW'
        if (func3_c == 0x07):
            if (isa == 32):
                return 'C.FSW' 
            return 'C.SD'
        
    if (opcode_c == 0x01):
        if (ins16 == 0x00):   return 'C.NOP'
        if (func3_c == 0x00): return 'C.ADDI'
        if (func3_c == 0x01):
            if (isa == 32):
                return 'C.JAL'
            return 'C.ADDIW'
        if (func3_c == 0x02): return 'C.LI'
        if (func3_c == 0x03):
             if (rd5_c == 0x02):
                 return 'C.ADDI16SP'
             else:
                 return 'C.LUI'             
        if (func3_c == 0x04):
            if (rdu2_c == 0x00):
                if (imm5_c == 0x00):
                    return 'C.SRLI64'
                else:
                    return 'C.SRLI' 
            if (rdu2_c == 0x01):
                if (imm5_c == 0x00): return 'C.SRAI64'
                else: return 'C.SRAI'
            if (rdu2_c == 0x02): return 'C.ANDI'
            if (rdu2_c == 0x03):
                if (imm3_c == 0x00): return 'C.SUB'
                if (imm3_c == 0x01): return 'C.XOR'
                if (imm3_c == 0x02): return 'C.OR'
                if (imm3_c == 0x03): return 'C.AND'
                if (imm3_c == 0x04): return 'C.SUBW'
                if (imm3_c == 0x05): return 'C.ADDW'
        if (func3_c == 0x05): return 'C.J'
        if (func3_c == 0x06): return 'C.BEQZ'
        if (func3_c == 0x07): return 'C.BNEZ'
    
    if (opcode_c == 0x02):
        if (func3_c == 0x00):
            if (isa == 128 and imm5_c == 0x00):
                return 'C.SLLI64'
            else:
                return 'C.SLLI'
        if (func3_c == 0x01):
            if (isa == 128):
                return 'C.LQSP'
            return 'C.FLDSP' 
        if (func3_c == 0x02): return 'C.LWSP' 
        if (func3_c == 0x03):
            if (isa == 32):
                return 'C.FLWSP'
            return 'C.LDSP'
        if (func3_c == 0x04):
            if (imm5_c == 0x00): return 'C.JR'
            if (imm1_c == 0x00): return 'C.MV'
            if (imm1_c == 0x01):
                if (rd5_c == 0x00):
                    return 'C.EBREAK'
                if (r25_c == 0x00):
                    return 'C.JALR'
                else:
                    return 'C.ADD'
        if (func3_c == 0x05):
            if (isa == 128):
                return 'C.SQSP'
            return 'C.FSDSP' 
        if (func3_c == 0x06): return 'C.SWSP'
        if (func3_c == 0x07):
            if (isa == 32):
                return 'C.FSWSP'
            return 'C.SDSP'
        
    if (opcode == 0x03):
        if (func3 == 0x00): return 'LB'
        if (func3 == 0x01): return 'LH'
        if (func3 == 0x02): return 'LW'
        if (func3 == 0x03): return 'LD'
        if (func3 == 0x04): return 'LBU'
        if (func3 == 0x05): return 'LHU'
        if (func3 == 0x06): return 'LWU'
    if (opcode == 0x07):
        if (func3 == 0x01): return 'FLH'
        if (func3 == 0x02): return 'FLW'
        if (func3 == 0x03): return 'FLD'    
    if (opcode == 0x0b): return 'CUSTOM0'
    if (opcode == 0x0F):
        if (func3 == 0x00): return 'FENCE'
        if (func3 == 0x01): return 'FENCE.I'
        if (func3 == 0x02): 
            if (imm12 == 0x00): return 'CBO.INVAL'
            if (imm12 == 0x00): return 'CBO.CLEAN'
            if (imm12 == 0x02): return 'CBO.FLUSH'
            if (imm12 == 0x04): return 'CBO.ZERO'
    if (opcode == 0x13):
        if (func3 == 0x00):
            return 'ADDI'
        if (func3 == 0x01):
            if (func5 == 0x05): return 'BSETI'
            if (func5 == 0x09): return 'BCLRI'
            if (func5 == 0x0D): return 'BINVI'
            if (func6 == 0x00): return 'SLLI'
            if (func6 == 0x02): return 'SHFLI'
            if (func7 == 0x30):
                if (rs2 == 0x00): return 'CLZ'
                if (rs2 == 0x01): return 'CTZ'
                if (rs2 == 0x02): return 'CPOP'
                if (rs2 == 0x03): return 'BMATFLIP'
                if (rs2 == 0x04): return 'SEXT.B'
                if (rs2 == 0x05): return 'SEXT.H'
                
                if (rs2 == 0x10): return 'CRC32.B'
                if (rs2 == 0x11): return 'CRC32.H'
                if (rs2 == 0x12): return 'CRC32.W'
                if (rs2 == 0x13): return 'CRC32.D'
                if (rs2 == 0x18): return 'CRC32C.B'
                if (rs2 == 0x19): return 'CRC32C.H'
                if (rs2 == 0x1A): return 'CRC32C.W'
                if (rs2 == 0x1B): return 'CRC32C.D'
        if (func3 == 0x02): return 'SLTI'
        if (func3 == 0x03): return 'SLTIU'
        if (func3 == 0x04): return 'XORI'
        if (func3 == 0x05):
            if (func5 == 0x04): return 'SROI'
            if (func5 == 0x05): return 'GORCI'
            if (func5 == 0x09): return 'BEXTI'
            if (func5 == 0x0C): return 'RORI'
            if (func5 == 0x0D): return 'GREVI'
            if (func6 == 0x00): return 'SRLI'
            if (func6 == 0x10): return 'SRAI'
            if (func6 == 0x02): return 'UNSHFLI'
        if (func3 == 0x06): return 'ORI'
        if (func3 == 0x07): return 'ANDI'
    if (opcode == 0x17): return 'AUIPC'
    if (opcode == 0x1B):
        if (func3 == 0x00): return 'ADDIW'
        if (func3 == 0x01):
            if (func5 == 0x01): return 'SLLI.UW'
            if (func7 == 0x00): return 'SLLIW'
            if (func7 == 0x30):
                if (rs2 == 0x00): return 'CLZW'
                if (rs2 == 0x01): return 'CTZW'
                if (rs2 == 0x02): return 'CPOPW'
        if (func3 == 0x05):
            if (func7 == 0x00): return 'SRLIW'
            if (func7 == 0x20): return 'SRAIW'
            if (func7 == 0x30): return 'RORIW'
    if (opcode == 0x23):
        if (func3 == 0x00): return 'SB'
        if (func3 == 0x01): return 'SH'
        if (func3 == 0x02): return 'SW'
        if (func3 == 0x03): return 'SD'
    if (opcode == 0x27):
        if (func3 == 0x01): return 'FSH'
        if (func3 == 0x02): return 'FSW'
        if (func3 == 0x03): return 'FSD'
        if (func3 == 0x04): return 'FSQ'
    if (opcode == 0x2B): return 'CUSTOM1'
    if (opcode == 0x2F):
        if (func3 == 0x02):
            if (func5 == 0x00): return 'AMOADD.W'
            if (func5 == 0x01): return 'AMOSWAP.W'
            if (func5 == 0x02): return 'LR.W'
            if (func5 == 0x03): return 'SC.W'
            if (func5 == 0x04): return 'AMOXOR.W'
            if (func5 == 0x08): return 'AMOOR.W'
            if (func5 == 0x0C): return 'AMOAND.W'
            if (func5 == 0x10): return 'AMOMIN.W'
            if (func5 == 0x14): return 'AMOMAX.W'
            if (func5 == 0x18): return 'AMOMINU.W'
            if (func5 == 0x1C): return 'AMOMAXU.W'
        if (func3 == 0x03):
            if (func5 == 0b00010): return 'LR.D'
            if (func5 == 0b00011): return 'SC.D'
            if (func5 == 0b00001): return 'AMOSWAP.D'
            if (func5 == 0b00000): return 'AMOADD.D'
            if (func5 == 0b00100): return 'AMOXOR.D'
            if (func5 == 0b01100): return 'AMOAND.D'
            if (func5 == 0b01000): return 'AMOOR.D'
            if (func5 == 0b10000): return 'AMOMIN.D'
            if (func5 == 0b10100): return 'AMOMAX.D'
            if (func5 == 0b11000): return 'AMOMINU.D'
            if (func5 == 0b11100): return 'AMOMAXU.D'            
    if (opcode == 0x33):
        if (func3 == 0x00):
            if (func7 == 0x00): return 'ADD'
            if (func7 == 0x01): return 'MUL'
            if (func7 == 0x20): return 'SUB'
        if (func3 == 0x01):
            if (func7 == 0x00): return 'SLL'
            if (func7 == 0x01): return 'MULH'
            if (func7 == 0x04): return 'SHFL'
            if (func7 == 0x05): return 'CLMUL'
            if (func7 == 0x14): return 'BSET'
            if (func7 == 0x24): return 'BCLR'
            if (func7 == 0x30): return 'ROL'
            if (func7 == 0x34): return 'BINV'
        if (func3 == 0x02):
            if (func7 == 0x00): return 'SLT'
            if (func7 == 0x01): return 'MULHSU'
            if (func7 == 0x05): return 'CLMULR'
            if (func7 == 0x10): return 'SH1ADD'
        if (func3 == 0x03):
            if (func7 == 0x00): return 'SLTU'
            if (func7 == 0x01): return 'MULHU'
            if (func7 == 0x04): return 'BMATOR'
            if (func7 == 0x05): return 'CLMULH'
            if (func7 == 0x24): return 'BMATXOR'
        if (func3 == 0x04):
            if (func7 == 0x00): return 'XOR'
            if (func7 == 0x01): return 'DIV'
            if (func7 == 0x05): return 'MIN'
            if (func7 == 0x10): return 'SH2ADD'
            if (func7 == 0x20): return 'XNOR'
        if (func3 == 0x05):
            if (func7 == 0x00): return 'SRL'
            if (func7 == 0x01): return 'DIVU'
            if (func7 == 0x04): return 'UNSHFL'
            if (func7 == 0x05): return 'MINU'
            if (func7 == 0x20): return 'SRA'
            if (func7 == 0x24): return 'BEXT'
            if (func7 == 0x30): return 'ROR'
            if (func7 == 0x34): return 'GREV'
        if (func3 == 0x06):
            if (func7 == 0x00): return 'OR'
            if (func7 == 0x01): return 'REM'
            if (func7 == 0x04): return 'BCOMPRESS'
            if (func7 == 0x05): return 'MAX'
            if (func7 == 0x10): return 'SH3ADD'
            if (func7 == 0x20): return 'ORN'
            if (func7 == 0x24): return 'BDECOMPRESS'
        if (func3 == 0x07):
            if (func7 == 0x00): return 'AND'
            if (func7 == 0x01): return 'REMU'
            if (func7 == 0x05): return 'MAXU'
            if (func7 == 0x20): return 'ANDN'
            if (func7 == 0x24): return 'BFP'            
    if (opcode == 0x37):
        return 'LUI'
    if (opcode == 0x3B):
        if (func3 == 0x00):
            if (func7 == 0x00): return 'ADDW'
            if (func7 == 0x01): return 'MULW'
            if (func7 == 0x04): return 'ADD.UW'
            if (func7 == 0x20): return 'SUBW'
        if (func3 == 0x01):
            if (func7 == 0x00): return 'SLLW'
            if (func7 == 0x10): return 'SLOW'
            if (func7 == 0x30): return 'ROLW'
        if (func3 == 0x02):
            if (func7 == 0x10): return 'SH1ADD.UW'
        if (func3 == 0x04):
            if (func7 == 0x01): return 'DIVW'
            if (func7 == 0x04): return 'ZEXT.H'
            if (func7 == 0x10): return 'SH2ADD.UW'
        if (func3 == 0x05):
            if (func7 == 0x00): return 'SRLW'
            if (func7 == 0x01): return 'DIVUW'
            if (func7 == 0x10): return 'SROW'
            if (func7 == 0x20): return 'SRAW'
            if (func7 == 0x30): return 'RORW'
        if (func3 == 0x06):
            if (func7 == 0x01): return 'REMW'
            if (func7 == 0x10): return 'SH3ADD.UW'
        if (func3 == 0x07):
            if (func7 == 0x01): return 'REMUW'    
    if (opcode == 0x43):
        if (func2 == 0x00): return 'FMADD.S'
        if (func2 == 0x01): return 'FMADD.D'
        if (func2 == 0x02): return 'FMADD.H'
    if (opcode == 0x47):
        if (func2 == 0x00): return 'FMSUB.S'
        if (func2 == 0x01): return 'FMSUB.D'
        if (func2 == 0x02): return 'FMSUB.H'        
    if (opcode == 0x4b):
        if (func2 == 0x00): return 'FNMSUB.S'
        if (func2 == 0x01): return 'FNMSUB.D'        
        if (func2 == 0x02): return 'FNMSUB.H'
    if (opcode == 0x4f):
        if (func2 == 0x00): return 'FNMADD.S'
        if (func2 == 0x01): return 'FNMADD.D'
        if (func2 == 0x02): return 'FNMADD.H'
    if (opcode == 0x53):
        if (func7 == 0x00): return 'FADD.S'
        if (func7 == 0x01): return 'FADD.D'
        if (func7 == 0x02): return 'FADD.H'
        if (func7 == 0x04): return 'FSUB.S'
        if (func7 == 0x05): return 'FSUB.D'
        if (func7 == 0x06): return 'FSUB.H'
        if (func7 == 0x08): return 'FMUL.S'
        if (func7 == 0x09): return 'FMUL.D'
        if (func7 == 0x0A): return 'FMUL.H'
        if (func7 == 0x0C): return 'FDIV.S'
        if (func7 == 0x0D): return 'FDIV.D'
        if (func7 == 0x0E): return 'FDIV.H'
        if (func7 == 0x10):
            if (func3 == 0x00): return 'FSGNJ.S'
            if (func3 == 0x01): return 'FSGNJN.S'
            if (func3 == 0x02): return 'FSGNJX.S'
        if (func7 == 0x11):
            if (func3 == 0b000): return 'FSGNJ.D'
            if (func3 == 0b001): return 'FSGNJN.D'
            if (func3 == 0b010): return 'FSGNJX.D'
        if (func7 == 0x12):
            if (func3 == 0x00): return 'FSGNJ.H'
            if (func3 == 0x01): return 'FSGNJN.H'
            if (func3 == 0x02): return 'FSGNJX.H'
        if (func7 == 0x14):
            if (func3 == 0b000): return 'FMIN.S'
            if (func3 == 0b001): return 'FMAX.S'
        if (func7 == 0x15):
            if (func3 == 0b000): return 'FMIN.D'
            if (func3 == 0b001): return 'FMAX.D'
        if (func7 == 0x16):
            if (func3 == 0x00): return 'FMIN.H'
            if (func3 == 0x01): return 'FMAX.H'
        if (func7 == 0x20):
            if (rs2 == 0x01): return 'FCVT.S.D'
            if (rs2 == 0x02): return 'FCVT.S.H'
        if (func7 == 0x21):
            if (rs2 == 0x00): return 'FCVT.D.S'
            if (rs2 == 0x02): return 'FCVT.D.H'
        if (func7 == 0x22):
            if (rs2 == 0x00): return 'FCVT.H.S'
            if (rs2 == 0x01): return 'FCVT.H.D'
        if (func7 == 0x2C):
            if (rs2 == 0x00): return 'FSQRT.S'
        if (func7 == 0x2D):
            if (rs2 == 0x00): return 'FSQRT.D'
        if (func7 == 0x2E):
            if (rs2 == 0x00): return 'FSQRT.H'
        if (func7 == 0x50):
            if (func3 == 0b010): return 'FEQ.S'
            if (func3 == 0b001): return 'FLT.S'
            if (func3 == 0b000): return 'FLE.S'
        if (func7 == 0x51):
            if (func3 == 0b000): return 'FLE.D'
            if (func3 == 0b001): return 'FLT.D'
            if (func3 == 0b010): return 'FEQ.D'
        if (func7 == 0x52):
            if (func3 == 0x00): return 'FLE.H'
            if (func3 == 0x01): return 'FLT.H'
            if (func3 == 0x02): return 'FEQ.H'
        if (func7 == 0x60):
            if (rs2 == 0x00): return 'FCVT.W.S'
            if (rs2 == 0x01): return 'FCVT.WU.S'
            if (rs2 == 0x02): return 'FCVT.L.S'
            if (rs2 == 0x03): return 'FCVT.LU.S'
        if (func7 == 0x61):
            if (rs2 == 0x00): return 'FCVT.W.D'
            if (rs2 == 0x01): return 'FCVT.WU.D'
            if (rs2 == 0x02): return 'FCVT.L.D'
            if (rs2 == 0x03): return 'FCVT.LU.D'
        if (func7 == 0x62):
            if (rs2 == 0x00): return 'FCVT.W.H'
            if (rs2 == 0x01): return 'FCVT.WU.H'
            if (rs2 == 0x02): return 'FCVT.L.H'
            if (rs2 == 0x03): return 'FCVT.LU.H'
        if (func7 == 0x68):
            if (rs2 == 0b000): return 'FCVT.S.W'
            if (rs2 == 0b001): return 'FCVT.S.WU'
            if (rs2 == 0b010): return 'FCVT.S.L'
            if (rs2 == 0b011): return 'FCVT.S.LU'
        if (func7 == 0x69):
            if (rs2 == 0b00000): return 'FCVT.D.W'
            if (rs2 == 0b00001): return 'FCVT.D.WU'
            if (rs2 == 0b00010): return 'FCVT.D.L'
            if (rs2 == 0b00011): return 'FCVT.D.LU'
        if (func7 == 0x6A):
            if (rs2 == 0x00): return 'FCVT.H.W'
            if (rs2 == 0x01): return 'FCVT.H.WU'
            if (rs2 == 0x02): return 'FCVT.H.L'
            if (rs2 == 0x03): return 'FCVT.H.LU'
        if (func7 == 0x70):
            if (rs2 == 0b000):
                if (func3 == 0b000): return 'FMV.X.W'
                if (func3 == 0b001): return 'FCLASS.S'
        if (func7 == 0x71):
            if (rs2 == 0b000):
                if (func3 == 0b000): return 'FMV.X.D'
                if (func3 == 0b001): return 'FCLASS.D'
        if (func7 == 0x72):
            if (rs2 == 0x00):
                if (func3 == 0x00): return 'FMV.X.H'
                if (func3 == 0x01): return 'FCLASS.H'
        if (func7 == 0x78):
            if (rs2 == 0b000):
                if (func3 == 0b000): return 'FMV.W.X'
        if (func7 == 0x79):
            if (rs2 == 0b000):
                if (func3 == 0b000): return 'FMV.D.X'
        if (func7 == 0x7A):
            if (rs2 == 0x00):
                if (func3 == 0x00): return 'FMV.H.X'
    if (opcode == 0x5B): return 'CUSTOM2'
    if (opcode == 0x63):
        if (func3 == 0x00): return 'BEQ'
        if (func3 == 0x01): return 'BNE'
        if (func3 == 0b100): return 'BLT'
        if (func3 == 0b101): return 'BGE'
        if (func3 == 0b110): return 'BLTU'
        if (func3 == 0b111): return 'BGEU'
    if (opcode == 0x67):
        if (func3 == 0x00): return 'JALR'
    if (opcode == 0x6F):
        return 'JAL'    
    if (opcode == 0x73):
        if (func3 == 0x00):
            if (ins == 0x00000073): return 'ECALL'
            if (ins == 0x00200073): return 'URET'
            if (ins == 0x10200073): return 'SRET'
            if (ins == 0x10500073): return 'WFI'
            if (ins == 0x30200073): return 'MRET'
            if (ins == 0x00100073): return 'EBREAK'
            if (func7 == 0b0001001): return 'SFENCE.VMA'
        if (func3 == 0x01): return 'CSRRW'
        if (func3 == 0x02): return 'CSRRS'
        if (func3 == 0x03): return 'CSRRC'
        if (func3 == 0x05): return 'CSRRWI'
        if (func3 == 0x06): return 'CSRRSI'
        if (func3 == 0x07): return 'CSRRCI'
    if (opcode == 0x7b): return 'CUSTOM3' 
    #return 'Unknown opcode {:x} func3 {:x} func7 {:x} full {:08x}'.format(opcode, func3, func7, ins)
    if (is_compact_ins(ins)):
        raise Exception('Unknown opcode {:02b} func3 {:03b}  full {:08x}'.format(opcode_c, func3_c,  ins))
    else:
        raise Exception('Unknown opcode {:07b} func3 {:03b} func7 {:07b} rs2 {:04b} full {:08x}'.format(opcode, func3, func7, rs2, ins))
 
