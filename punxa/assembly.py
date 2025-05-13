# -*- coding: utf-8 -*-
"""
Created on Wed May  7 16:57:41 2025

@author: 2016570
"""
from .temp_helper import *
from .instruction_decode import *
import re

def split_parts(s):
    parts = re.split('[, ()]', s)
    ret = []
    
    for part in parts:
        if len(part)>0:
            ret.append(part)
            
    return ret

def assemble(asm):
    ret = 0
    
    ret = parts_to_ins(split_parts(asm))
    return ret 


#LoadIns = ['LB','LH','LW','LWU','LBU','LHU','LD', 'FLD','FLW', 'FLH',]
RegOffsetRegIns = ['LB','LH','LW','LWU','LBU','LHU','LD',
                   'SB','SH','SW','SD',] # , 'FLD','FLW', 'FLH',]
RegImmIns = ['LUI', 'JAL']
RegRegImmIns = ['ADDI','SLTI','SLTIU', 'XORI', 'ADDIW', 'ORI','ANDI', 'SLLI',
                'SLLI.UW','SRLI','SRAI','SLLIW','SRLIW','SRAIW','RORI','RORIW',
                'CSRRW','CSRRS','CSRRC','CSRRWI','CSRRSI','CSRRCI',
                'BEQ','BNE','BLT','BGE','BLTU','BGEU']
RegRegRegIns = ['AND','OR','XOR', 'XNOR',
            'ADD','ADD.UW','SUB',
            'MUL', 'MULH', 'MULHU', 'MULHSU', 'MULW',
            'CLMUL','CLMULH', 'CLMULR',
            'DIV', 'DIVU', 'DIVW', 'DIVUW', 'REM', 'REMU', 'REMW', 'REMUW',
            'ROL','ROLW','ROR','RORW','SLL','SLT','SLTU','SRA','SRL',
            'ADDW','SLLW','SRLW','SUBW','SRAW',
            'ANDN','ORN', 'MIN','MAX','MINU','MAXU', 
            'SH1ADD','SH1ADD.UW','SH2ADD','SH2ADD.UW','SH3ADD','SH3ADD.UW',
            'BEXT','BINV','BSET', 'BCLR']

def disassemble(v):
    ret = ''
    
    parts = ins_to_parts(v)
    
    ret = parts[0] 
    
    #if (ret in STypeIns):
    #    ret += f' {parts[1]}'
    #    ret += f', {parts[2]}({parts[3]})'
    # elif (ret in LoadIns):
    #     ret += f' {parts[1]}'
    #     ret += f', {parts[2]}({parts[3]})'        
    if (ret in RegOffsetRegIns):
         ret += f' {parts[1]}'
         ret += f', {parts[2]}({parts[3]})'        
    elif (ret in RegRegRegIns):
        ret += f' {parts[1]}'
        ret += f', {parts[2]}'
        ret += f', {parts[3]}'
    elif (ret in RegImmIns):
        ret += f' {parts[1]}'
        ret += f', {parts[2]}'
    else:
        ret += f' {parts[1]}'
        ret += f', {parts[2]}'
        ret += f', {parts[3]}'
    
    return ret

def reg_to_index(reg):
    reg = reg.lower()
    if (reg[0] == 'x'): return int(reg[1:])
    if (reg == 'zero'): return 0
    if (reg == 'ra'):   return 1
    if (reg == 'sp'):   return 2
    if (reg == 'gp'):   return 3
    if (reg == 'tp'):   return 4
    if (reg == 't0'):   return 5
    if (reg == 't1'):   return 6
    if (reg == 't2'):   return 7
    if (reg == 'fp'):   return 8
    if (reg == 's0'):   return 8
    if (reg == 's1'):   return 9
    if (reg == 'a0'):   return 10
    if (reg == 'a1'):   return 11
    if (reg == 'a2'):   return 12
    if (reg == 'a3'):   return 13
    if (reg == 'a4'):   return 14
    if (reg == 'a5'):   return 15
    if (reg == 'a6'):   return 16
    if (reg == 'a7'):   return 17
    if (reg == 's2'):   return 18
    if (reg == 's3'):   return 19
    if (reg == 's4'):   return 20
    if (reg == 's5'):   return 21
    if (reg == 's6'):   return 22
    if (reg == 's7'):   return 23
    if (reg == 's8'):   return 24
    if (reg == 's9'):   return 25
    if (reg == 's10'):   return 26
    if (reg == 's11'):   return 27
    if (reg == 't3'):   return 28
    if (reg == 't4'):   return 29
    if (reg == 't5'):   return 30
    if (reg == 't6'):   return 31
    
    
    return 0

def get_int(v):
    if (isinstance(v, int)):
        return v
    if (isinstance(v, str)):
        if (v[0:2] == '0x'):
            return int(v, 16)
        else:
            return int(v)

def parts_to_ins(parts):
    
    # encode an instruction into its parts
    #ins16 = ins & 0xFFFF
    #opcode_c = ins & 0x03
    #opcode = ins & 0x7F
    #func2 = (ins >> 25) & 0x3
    #func3 = (ins >> 12) & 0x7
    #func3_c = (ins >> 13) & 0x7
    #func5 = (ins >> 27) & 0x1F
    #func6 = (ins >> 26) & 0x3F
    #func7 = (ins >> 25) & 0x7F
    #rd = get_bits(ins, 7, 5)
    #rs1 = get_bits(ins, 15, 5)
    #rs2 = get_bits(ins, 20, 5)
    #rs3 = get_bits(ins, 27, 5)
    
    #rd5_c = (ins >> 7) & 0x1F
    #rdu2_c = (ins >> 10) & 0x03
    #r2u2_c = (ins >> 5) & 0x03
    #r25_c = (ins >> 2) & 0x1F
    #imm1_c = ((ins >> 12) & 0x1) 
    #imm5_c = (((ins >> 12) & 0x1) << 5) | ((ins >> 2) & 0x1F)
    #imm3_c = (((ins >> 12) & 0x1) << 2) | ((ins >> 5) & 0x03)
    #imm10_c = (ins >> 2) & 0x3FF
    #imm12 = (ins >> 20) & 0xFFF
    
    #simm12 = compose_sign(ins, [[20, 12]])
    
    pop = parts[0].upper()
    pr = parts[1]
    p1 = parts[2] if (len(parts)>2) else ''
    p2 = parts[3] if (len(parts)>3) else ''
    
    # if (len(parts) > 3):
    #     p2 = parts[3] 
    #     rs2 = reg_to_index(p2) << 20
    #     simm12 = get_int(p2) << 20
    # else:
    #     ps = ''
    #     rs2 = 0
    #     simm12 = 0
    
    # rd = reg_to_index(pr) << 7
    # rs1 = reg_to_index(p1) << 15
    
    #soff12_s = int(p2) compose_sign(ins, [[25,7],[7,5]])
    
    # Handle pseudo-instructons
    if (pop == 'LI'):
        pop = 'ADDI'
        p2 = p1
        p1 = 'x0'
    elif (pop == 'MV'):
        pop = 'ADDI'
        p2 = 0
    elif (pop == 'J'):
        pop = 'JAL'
        p1 = pr
        pr = 'x0'
    
    if (pop in RegOffsetRegIns):
        simm12 = get_int(p1) << 20
        rd = reg_to_index(pr) << 7
        rs1 = reg_to_index(p2) << 15
        
        if (pop == 'LB'): opcode, func3 = 0x03, 0x00 << 12
        elif (pop == 'LH'): opcode, func3 = 0x03, 0x01 << 12
        elif (pop == 'LW'): opcode, func3 = 0x03, 0x02 << 12
        elif (pop == 'LD'): opcode, func3 = 0x03, 0x03 << 12
        elif (pop == 'LBU'): opcode, func3 = 0x03, 0x04 << 12
        elif (pop == 'LHU'): opcode, func3 = 0x03, 0x05 << 12
        elif (pop == 'LWU'): opcode, func3 = 0x03, 0x06 << 12
        elif (pop in STypeIns):
            if (pop == 'SW'):
                opcode = 0x23
                func3 = 0x02 << 12
                
                rs2 = reg_to_index(pr) << 20
                off = get_int(p1)
                # rs1 = reg_to_index(p2) << 15
                
                simm12_4_0 = get_bits(off, 0, 5) << 7
                simm12_11_5 = get_bits(off, 5, 7) << 25
                return (simm12_11_5 | rs2 | rs1 | func3 | simm12_4_0 | opcode) & ((1 << 32)-1)
            else: raise Exception(f'unhandled instruction {pop}')
            
        else: raise Exception(f'unhandled instruction {pop}')
        return (simm12 | rs1 | func3 | rd | opcode) & ((1 << 32)-1)
    
    elif (pop in RegRegImmIns):
        
        rd = reg_to_index(pr) << 7
        rs1 = reg_to_index(p1) << 15
        v2 = get_int(p2)
        simm12 = v2 << 20

        if (pop == 'ADDI'): opcode, func3 = 0x13,  0x00 << 12
        elif (pop == 'SLTI'): opcode, func3 = 0x13,  0x02 << 12
        elif (pop == 'SLTIU'): opcode, func3 = 0x13,  0x03 << 12
        elif (pop == 'XORI'): opcode, func3 = 0x13,  0x04 << 12
        elif (pop == 'ORI'): opcode, func3 = 0x13,  0x06 << 12
        elif (pop == 'ANDI'): opcode, func3 = 0x13,  0x07 << 12

        elif (pop == 'SLLI'):
            opcode, func3, func6 = 0x13, 0x01 << 12,  0x00 << 26
            return (func6 | simm12 | rs1 | rd | func3 | opcode) & ((1 << 32)-1)
        
        elif (pop == 'ADDIW'): opcode, func3 = 0x1B, 0x00 << 12
        
        
        elif (pop in BTypeIns):
            rs1 = reg_to_index(pr) << 15
            rs2 = reg_to_index(p1) << 20
            
            simm13_B = get_bit(v2, 12) << 31 | get_bits(v2, 5, 6) << 25 |  get_bit(v2, 11) << 7 | get_bits(v2, 1, 4) << 8

            if (pop == 'BEQ'): return simm13_B | rs2 | rs1 | (0x00 << 12) | 0x63
            elif (pop == 'BNE'): return simm13_B | rs2 | rs1 | (0x01 << 12) | 0x63
            elif (pop == 'BLT'): return simm13_B | rs2 | rs1 | (0x04 << 12) | 0x63
            elif (pop == 'BGE'): return simm13_B | rs2 | rs1 | (0x05 << 12) | 0x63
            elif (pop == 'BLTU'): return simm13_B | rs2 | rs1 | (0x06 << 12) | 0x63
            elif (pop == 'BGEU'): return simm13_B | rs2 | rs1 | (0x07 << 12) | 0x63
            else: raise Exception(f'unhandled instruction {pop}')
            
        else: raise Exception(f'unhandled instruction {pop}')
        
        return (simm12 | rs1 | rd | func3 | opcode) & ((1 << 32)-1)
    
    elif (pop == 'SB'):
        opcode = 0x23
        func3 = 0x00
        raise Exception('')
        
    elif (pop == 'SH'):
        opcode = 0x23
        func3 = 0x01
        raise Exception('')
        
    
    
    #if (pop in ITypeIns):
        
    elif (pop in RegImmIns):
        rd = reg_to_index(pr) << 7
        imm = get_int(p1)
        
        
        if (pop == 'LUI'): opcode, imm_enc = 0x37, imm << 12
        elif (pop == 'JAL'): opcode, imm_enc = 0x6F, get_bit(imm, 20) << 31 | get_bits(imm, 1, 10) << 21 | get_bit(imm, 11) << 20 | get_bits(imm, 12, 8) << 12
        
        return (imm_enc | rd |  opcode) & ((1 << 32)-1)

    elif (pop in RegRegRegIns):
        rd = reg_to_index(pr) << 7
        rs1 = reg_to_index(p1) << 15
        rs2 = reg_to_index(p2) << 20
        
        
        if (pop == 'ADD'):   opcode, func3, func7 = 0x33, 0x00 << 12,  0x00 << 25
        elif (pop == 'MUL'): opcode, func3, func7 = 0x33, 0x00 << 12,  0x01 << 25
        elif (pop == 'SUB'): opcode, func3, func7 = 0x33, 0x00 << 12,  0x20 << 25

        elif (pop == 'SLL'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x00 << 25
        elif (pop == 'MULH'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x01 << 25
        elif (pop == 'SHFL'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x04 << 25
        elif (pop == 'CLMUL'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x05 << 25
        elif (pop == 'BSET'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x14 << 25
        elif (pop == 'BCLR'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x24 << 25
        elif (pop == 'ROL'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x30 << 25
        elif (pop == 'BINV'): opcode, func3, func7 = 0x33, 0x01 << 12,  0x34 << 25

        elif (pop == 'SLT'): opcode, func3, func7 = 0x33, 0x02 << 12,  0x00 << 25
        elif (pop == 'MULHSU'): opcode, func3, func7 = 0x33, 0x02 << 12,  0x01 << 25
        elif (pop == 'CLMULR'): opcode, func3, func7 = 0x33, 0x02 << 12,  0x05 << 25
        elif (pop == 'SH1ADD'): opcode, func3, func7 = 0x33, 0x02 << 12,  0x10 << 25

        elif (pop == 'SLTU'): opcode, func3, func7 = 0x33, 0x03 << 12,  0x00 << 25
        elif (pop == 'MULHU'): opcode, func3, func7 = 0x33, 0x03 << 12,  0x01 << 25
        elif (pop == 'BMATOR'): opcode, func3, func7 = 0x33, 0x03 << 12,  0x04 << 25
        elif (pop == 'CLMULH'): opcode, func3, func7 = 0x33, 0x03 << 12,  0x05 << 25
        elif (pop == 'BMATXOR'): opcode, func3, func7 = 0x33, 0x03 << 12,  0x24 << 25

        elif (pop == 'SRL'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x00 << 25
        elif (pop == 'DIVU'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x01 << 25
        elif (pop == 'UNSHFL'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x04 << 25
        elif (pop == 'MINU'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x05 << 25
        elif (pop == 'SRA'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x20 << 25
        elif (pop == 'BEXT'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x24 << 25
        elif (pop == 'ROR'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x30 << 25
        elif (pop == 'GREV'): opcode, func3, func7 = 0x33, 0x05 << 12,  0x34 << 25

        elif (pop == 'AND'): opcode, func3, func7 = 0x33, 0x07 << 12,  0x00 << 25
        elif (pop == 'REMU'): opcode, func3, func7 = 0x33, 0x07 << 12,  0x01 << 25
        elif (pop == 'MAXU'): opcode, func3, func7 = 0x33, 0x07 << 12,  0x05 << 25
        elif (pop == 'ANDN'): opcode, func3, func7 = 0x33, 0x07 << 12,  0x20 << 25
        elif (pop == 'BFP'): opcode, func3, func7 = 0x33, 0x07 << 12,  0x24 << 25
                
        elif (pop == 'XOR'): opcode, func3, func7 = 0x33, 0x04 << 12,  0x00 << 25
        elif (pop == 'DIV'): opcode, func3, func7 = 0x33, 0x04 << 12,  0x01 << 25
        elif (pop == 'ZEXT.H'): opcode, func3, func7 = 0x33, 0x04 << 12,  0x04 << 25
        elif (pop == 'MIN'): opcode, func3, func7 = 0x33, 0x04 << 12,  0x05 << 25
        elif (pop == 'SH2ADD'): opcode, func3, func7 = 0x33, 0x04 << 12,  0x10 << 25
        elif (pop == 'XNOR'): opcode, func3, func7 = 0x33, 0x04 << 12,  0x20 << 25

        elif (pop == 'OR'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x00 << 25
        elif (pop == 'REM'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x01 << 25
        elif (pop == 'BCOMPRESS'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x04 << 25
        elif (pop == 'MAX'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x05 << 25
        elif (pop == 'SH3ADD'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x10 << 25
        elif (pop == 'ORN'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x20 << 25
        elif (pop == 'BDECOMPRESS'): opcode, func3, func7 = 0x33, 0x06 << 12,  0x24 << 25
        
        
        elif (pop == 'ADDW'): opcode, func3, func7 = 0x3B, 0x00 << 12,  0x00 << 25
        elif (pop == 'MULW'): opcode, func3, func7 = 0x3B, 0x00 << 12,  0x01 << 25
        elif (pop == 'ADD.UW'): opcode, func3, func7 = 0x3B, 0x00 << 12,  0x04 << 25
        elif (pop == 'SUBW'): opcode, func3, func7 = 0x3B, 0x00 << 12,  0x20 << 25

        elif (pop == 'SLLW'): opcode, func3, func7 = 0x3B, 0x01 << 12,  0x00 << 25
        elif (pop == 'SLOW'): opcode, func3, func7 = 0x3B, 0x01 << 12,  0x10 << 25
        elif (pop == 'ROLW'): opcode, func3, func7 = 0x3B, 0x01 << 12,  0x30 << 25

        elif (pop == 'SH1ADD.UW'): opcode, func3, func7 = 0x3B, 0x02 << 12,  0x10 << 25

        elif (pop == 'DIVW'): opcode, func3, func7 = 0x3B, 0x04 << 12,  0x01 << 25
        elif (pop == 'ZEXT.H'): opcode, func3, func7 = 0x3B, 0x04 << 12,  0x04 << 25
        elif (pop == 'SH2ADD.UW'): opcode, func3, func7 = 0x3B, 0x04 << 12,  0x10 << 25

        elif (pop == 'SRLW'): opcode, func3, func7 = 0x3B, 0x05 << 12,  0x00 << 25
        elif (pop == 'DIVUW'): opcode, func3, func7 = 0x3B, 0x05 << 12,  0x01 << 25
        elif (pop == 'SROW'): opcode, func3, func7 = 0x3B, 0x05 << 12,  0x10 << 25
        elif (pop == 'SRAW'): opcode, func3, func7 = 0x3B, 0x05 << 12,  0x20 << 25
        elif (pop == 'RORW'): opcode, func3, func7 = 0x3B, 0x05 << 12,  0x30 << 25

        elif (pop == 'REMW'): opcode, func3, func7 = 0x3B, 0x06 << 12,  0x01 << 25
        elif (pop == 'SH3ADD.UW'): opcode, func3, func7 = 0x3B, 0x06 << 12,  0x10 << 25

        elif (pop == 'REMUW'): opcode, func3, func7 = 0x3B, 0x07 << 12,  0x01 << 25

        elif (pop == 'FADD.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x00 << 25
        elif (pop == 'FADD.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x01 << 25
        elif (pop == 'FADD.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x02 << 25
        elif (pop == 'FSUB.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x04 << 25
        elif (pop == 'FSUB.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x05 << 25
        elif (pop == 'FSUB.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x06 << 25
        elif (pop == 'FMUL.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x08 << 25
        elif (pop == 'FMUL.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x09 << 25
        elif (pop == 'FMUL.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x0A << 25
        elif (pop == 'FDIV.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x0C << 25
        elif (pop == 'FDIV.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x0D << 25
        elif (pop == 'FDIV.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x0E << 25

        elif (pop == 'FSGNJ.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x10 << 25
        elif (pop == 'FSGNJN.S'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x10 << 25
        elif (pop == 'FSGNJX.S'): opcode, func3, func7 = 0x53, 0x02 << 12,  0x10 << 25

        elif (pop == 'FSGNJ.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x11 << 25
        elif (pop == 'FSGNJN.D'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x11 << 25
        elif (pop == 'FSGNJX.D'): opcode, func3, func7 = 0x53, 0x02 << 12,  0x11 << 25

        elif (pop == 'FSGNJ.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x12 << 25
        elif (pop == 'FSGNJN.H'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x12 << 25
        elif (pop == 'FSGNJX.H'): opcode, func3, func7 = 0x53, 0x02 << 12,  0x12 << 25

        elif (pop == 'FMIN.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x14 << 25
        elif (pop == 'FMAX.S'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x14 << 25

        elif (pop == 'FMIN.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x15 << 25
        elif (pop == 'FMAX.D'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x15 << 25

        elif (pop == 'FMIN.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x16 << 25
        elif (pop == 'FMAX.H'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x16 << 25

        #elif (pop == 'FCVT.S.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x20 << 25 
        #elif (pop == 'FCVT.S.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x20 << 25

        # if (opcode == 0x53):
    
        #     if (func7 == 0x20):
        #         if (rs2 == 0x01): return 'FCVT.S.D'
        #         if (rs2 == 0x02): return 'FCVT.S.H'
        #     if (func7 == 0x21):
        #         if (rs2 == 0x00): return 'FCVT.D.S'
        #         if (rs2 == 0x02): return 'FCVT.D.H'
        #     if (func7 == 0x22):
        #         if (rs2 == 0x00): return 'FCVT.H.S'
        #         if (rs2 == 0x01): return 'FCVT.H.D'
        #     if (func7 == 0x2C):
        #         if (rs2 == 0x00): return 'FSQRT.S'
        #     if (func7 == 0x2D):
        #         if (rs2 == 0x00): return 'FSQRT.D'
        #     if (func7 == 0x2E):
        #         if (rs2 == 0x00): return 'FSQRT.H'

        elif (pop == 'FLE.S'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x50 << 25
        elif (pop == 'FLT.S'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x50 << 25
        elif (pop == 'FEQ.S'): opcode, func3, func7 = 0x53, 0x02 << 12,  0x50 << 25

        elif (pop == 'FLE.D'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x51 << 25
        elif (pop == 'FLT.D'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x51 << 25
        elif (pop == 'FEQ.D'): opcode, func3, func7 = 0x53, 0x02 << 12,  0x51 << 25

        elif (pop == 'FLE.H'): opcode, func3, func7 = 0x53, 0x00 << 12,  0x52 << 25
        elif (pop == 'FLT.H'): opcode, func3, func7 = 0x53, 0x01 << 12,  0x52 << 25
        elif (pop == 'FEQ.H'): opcode, func3, func7 = 0x53, 0x02 << 12,  0x52 << 25

        # if (func7 == 0x60):
        #     if (rs2 == 0x00): return 'FCVT.W.S'
        #     if (rs2 == 0x01): return 'FCVT.WU.S'
        #     if (rs2 == 0x02): return 'FCVT.L.S'
        #     if (rs2 == 0x03): return 'FCVT.LU.S'
        # if (func7 == 0x61):
        #     if (rs2 == 0x00): return 'FCVT.W.D'
        #     if (rs2 == 0x01): return 'FCVT.WU.D'
        #     if (rs2 == 0x02): return 'FCVT.L.D'
        #     if (rs2 == 0x03): return 'FCVT.LU.D'
        # if (func7 == 0x62):
        #     if (rs2 == 0x00): return 'FCVT.W.H'
        #     if (rs2 == 0x01): return 'FCVT.WU.H'
        #     if (rs2 == 0x02): return 'FCVT.L.H'
        #     if (rs2 == 0x03): return 'FCVT.LU.H'
        # if (func7 == 0x68):
        #     if (rs2 == 0b000): return 'FCVT.S.W'
        #     if (rs2 == 0b001): return 'FCVT.S.WU'
        #     if (rs2 == 0b010): return 'FCVT.S.L'
        #     if (rs2 == 0b011): return 'FCVT.S.LU'
        # if (func7 == 0x69):
        #     if (rs2 == 0b00000): return 'FCVT.D.W'
        #     if (rs2 == 0b00001): return 'FCVT.D.WU'
        #     if (rs2 == 0b00010): return 'FCVT.D.L'
        #     if (rs2 == 0b00011): return 'FCVT.D.LU'
        # if (func7 == 0x6A):
        #     if (rs2 == 0x00): return 'FCVT.H.W'
        #     if (rs2 == 0x01): return 'FCVT.H.WU'
        #     if (rs2 == 0x02): return 'FCVT.H.L'
        #     if (rs2 == 0x03): return 'FCVT.H.LU'
        # if (func7 == 0x70):
        #     if (rs2 == 0b000):
        #         if (func3 == 0b000): return 'FMV.X.W'
        #         if (func3 == 0b001): return 'FCLASS.S'
        # if (func7 == 0x71):
        #     if (rs2 == 0b000):
        #         if (func3 == 0b000): return 'FMV.X.D'
        #         if (func3 == 0b001): return 'FCLASS.D'
        # if (func7 == 0x72):
        #     if (rs2 == 0x00):
        #         if (func3 == 0x00): return 'FMV.X.H'
        #         if (func3 == 0x01): return 'FCLASS.H'
        # if (func7 == 0x78):
        #     if (rs2 == 0b000):
        #         if (func3 == 0b000): return 'FMV.W.X'
        # if (func7 == 0x79):
        #     if (rs2 == 0b000):
        #         if (func3 == 0b000): return 'FMV.D.X'
        # if (func7 == 0x7A):
        #     if (rs2 == 0x00):
        #         if (func3 == 0x00): return 'FMV.H.X'

        return (func7 | rs2 | rs1 | rd | func3 | opcode) & ((1 << 32)-1)
    
    else:
        raise Exception(f'{pop} not handled')    
    return
    
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
                if (imm10_c == 0x00):
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
        
        if (func3 == 0x05):
            if (func5 == 0x04): return 'SROI'
            if (func5 == 0x05): return 'GORCI'
            if (func5 == 0x09): return 'BEXTI'
            if (func5 == 0x0C): return 'RORI'
            if (func5 == 0x0D): return 'GREVI'
            if (func6 == 0x00): return 'SRLI'
            if (func6 == 0x10): return 'SRAI'
            if (func6 == 0x02): return 'UNSHFLI'
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
        if (func3 == 0x05):
            if (func7 == 0x00): return 'SRL'
            if (func7 == 0x01): return 'DIVU'
            if (func7 == 0x04): return 'UNSHFL'
            if (func7 == 0x05): return 'MINU'
            if (func7 == 0x20): return 'SRA'
            if (func7 == 0x24): return 'BEXT'
            if (func7 == 0x30): return 'ROR'
            if (func7 == 0x34): return 'GREV'
        if (func3 == 0x07):
            if (func7 == 0x00): return 'AND'
            if (func7 == 0x01): return 'REMU'
            if (func7 == 0x05): return 'MAXU'
            if (func7 == 0x20): return 'ANDN'
            if (func7 == 0x24): return 'BFP'            
    
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
    if (opcode == 0x5B): return 'CUSTOM2'
    
    if (opcode == 0x67):
        if (func3 == 0x00): return 'JALR'
    
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
 
def ins_to_parts(ins):
    
    # decodes an instruction into its parts
    ins16 = ins & 0xFFFF
    opcode_c = ins & 0x03
    opcode = ins & 0x7F
    func2 = (ins >> 25) & 0x3
    func3 = (ins >> 12) & 0x7
    func3_c = (ins >> 13) & 0x7
    func5 = (ins >> 27) & 0x1F
    func6 = (ins >> 26) & 0x3F
    func7 = (ins >> 25) & 0x7F
    rd = get_bits(ins, 7, 5)
    rs1 = get_bits(ins, 15, 5)
    rs2 = get_bits(ins, 20, 5)
    rs3 = get_bits(ins, 27, 5)
    
    rd5_c = (ins >> 7) & 0x1F
    rdu2_c = (ins >> 10) & 0x03
    r2u2_c = (ins >> 5) & 0x03
    r25_c = (ins >> 2) & 0x1F
    imm1_c = ((ins >> 12) & 0x1) 
    imm5_c = (((ins >> 12) & 0x1) << 5) | ((ins >> 2) & 0x1F)
    imm3_c = (((ins >> 12) & 0x1) << 2) | ((ins >> 5) & 0x03)
    imm10_c = (ins >> 2) & 0x3FF
    imm12 = (ins >> 20) & 0xFFF
    
    simm12 = compose_sign(ins, [[20, 12]])
    simm20 = compose_sign(ins, [[12, 31]])
    simm12_B = compose_sign(ins, [[31,1], [7,1], [25,6], [8,4]]) << 1
    
    off21_J = compose_sign(ins, [[31,1], [12,8], [20,1], [21,10]]) << 1
    
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
                if (imm10_c == 0x00):
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
        if (func3 == 0x00): return 'LB', f'x{rd}', simm12, f'x{rs1}'
        if (func3 == 0x01): return 'LH', f'x{rd}', simm12, f'x{rs1}'
        if (func3 == 0x02): return 'LW', f'x{rd}', simm12, f'x{rs1}'
        if (func3 == 0x03): return 'LD', f'x{rd}', simm12, f'x{rs1}'
        if (func3 == 0x04): return 'LBU', f'x{rd}', simm12, f'x{rs1}'
        if (func3 == 0x05): return 'LHU', f'x{rd}', simm12, f'x{rs1}'
        if (func3 == 0x06): return 'LWU', f'x{rd}', simm12, f'x{rs1}'
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
            return 'ADDI', f'x{rd}', f'x{rs1}', simm12
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
        if (func3 == 0x02): return 'SLTI', f'x{rd}', f'x{rs1}', simm12
        if (func3 == 0x03): return 'SLTIU', f'x{rd}', f'x{rs1}', simm12
        if (func3 == 0x04): return 'XORI', f'x{rd}', f'x{rs1}', simm12
        if (func3 == 0x05):
            if (func5 == 0x04): return 'SROI'
            if (func5 == 0x05): return 'GORCI'
            if (func5 == 0x09): return 'BEXTI'
            if (func5 == 0x0C): return 'RORI'
            if (func5 == 0x0D): return 'GREVI'
            if (func6 == 0x00): return 'SRLI'
            if (func6 == 0x10): return 'SRAI'
            if (func6 == 0x02): return 'UNSHFLI'
        if (func3 == 0x06): return 'ORI', f'x{rd}', f'x{rs1}', simm12
        if (func3 == 0x07): return 'ANDI', f'x{rd}', f'x{rs1}', simm12
    if (opcode == 0x17): return 'AUIPC'
    if (opcode == 0x1B):
        if (func3 == 0x00): return 'ADDIW', f'x{rd}', f'x{rs1}', simm12
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
        soff12 = compose_sign(ins, [[25,7],[7,5]])
        
        if (func3 == 0x00): return 'SB'
        if (func3 == 0x01): return 'SH'
        if (func3 == 0x02): return 'SW', f'x{rs1}', soff12, f'x{rs2}',
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
            if (func7 == 0x00): return 'ADD', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'MUL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'SUB', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x01):
            if (func7 == 0x00): return 'SLL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'MULH', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'SHFL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'CLMUL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x14): return 'BSET', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x24): return 'BCLR', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x30): return 'ROL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x34): return 'BINV', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x02):
            if (func7 == 0x00): return 'SLT', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'MULHSU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'CLMULR', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SH1ADD', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x03):
            if (func7 == 0x00): return 'SLTU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'MULHU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'BMATOR', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'CLMULH', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x24): return 'BMATXOR', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x04):
            if (func7 == 0x00): return 'XOR', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'DIV', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'ZEXT.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'MIN', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SH2ADD', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'XNOR', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x05):
            if (func7 == 0x00): return 'SRL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'DIVU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'UNSHFL', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'MINU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'SRA', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x24): return 'BEXT', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x30): return 'ROR', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x34): return 'GREV', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x06):
            if (func7 == 0x00): return 'OR', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'REM', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'BCOMPRESS', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'MAX', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SH3ADD', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'ORN', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x24): return 'BDECOMPRESS', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x07):
            if (func7 == 0x00): return 'AND', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'REMU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x05): return 'MAXU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'ANDN', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x24): return 'BFP', f'x{rd}', f'x{rs1}', f'x{rs2}'         
    if (opcode == 0x37):
        return 'LUI', f'x{rd}', f'0x{simm20:X}'
    if (opcode == 0x3B):
        if (func3 == 0x00):
            if (func7 == 0x00): return 'ADDW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'MULW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'ADD.UW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'SUBW', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x01):
            if (func7 == 0x00): return 'SLLW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SLOW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x30): return 'ROLW', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x02):
            if (func7 == 0x10): return 'SH1ADD.UW', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x04):
            if (func7 == 0x01): return 'DIVW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x04): return 'ZEXT.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SH2ADD.UW', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x05):
            if (func7 == 0x00): return 'SRLW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x01): return 'DIVUW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SROW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x20): return 'SRAW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x30): return 'RORW', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x06):
            if (func7 == 0x01): return 'REMW', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func7 == 0x10): return 'SH3ADD.UW', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func3 == 0x07):
            if (func7 == 0x01): return 'REMUW', f'x{rd}', f'x{rs1}', f'x{rs2}'
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
        if (func7 == 0x00): return 'FADD.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x01): return 'FADD.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x02): return 'FADD.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x04): return 'FSUB.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x05): return 'FSUB.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x06): return 'FSUB.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x08): return 'FMUL.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x09): return 'FMUL.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x0A): return 'FMUL.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x0C): return 'FDIV.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x0D): return 'FDIV.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x0E): return 'FDIV.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x10):
            if (func3 == 0x00): return 'FSGNJ.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x01): return 'FSGNJN.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x02): return 'FSGNJX.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x11):
            if (func3 == 0b000): return 'FSGNJ.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b001): return 'FSGNJN.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b010): return 'FSGNJX.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x12):
            if (func3 == 0x00): return 'FSGNJ.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x01): return 'FSGNJN.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x02): return 'FSGNJX.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x14):
            if (func3 == 0b000): return 'FMIN.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b001): return 'FMAX.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x15):
            if (func3 == 0b000): return 'FMIN.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b001): return 'FMAX.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x16):
            if (func3 == 0x00): return 'FMIN.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x01): return 'FMAX.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x20):
            if (rs2 == 0x01): return 'FCVT.S.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x02): return 'FCVT.S.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x21):
            if (rs2 == 0x00): return 'FCVT.D.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x02): return 'FCVT.D.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x22):
            if (rs2 == 0x00): return 'FCVT.H.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x01): return 'FCVT.H.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x2C):
            if (rs2 == 0x00): return 'FSQRT.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x2D):
            if (rs2 == 0x00): return 'FSQRT.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x2E):
            if (rs2 == 0x00): return 'FSQRT.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x50):
            if (func3 == 0b010): return 'FEQ.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b001): return 'FLT.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b000): return 'FLE.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x51):
            if (func3 == 0b000): return 'FLE.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b001): return 'FLT.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0b010): return 'FEQ.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x52):
            if (func3 == 0x00): return 'FLE.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x01): return 'FLT.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (func3 == 0x02): return 'FEQ.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x60):
            if (rs2 == 0x00): return 'FCVT.W.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x01): return 'FCVT.WU.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x02): return 'FCVT.L.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x03): return 'FCVT.LU.S', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x61):
            if (rs2 == 0x00): return 'FCVT.W.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x01): return 'FCVT.WU.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x02): return 'FCVT.L.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x03): return 'FCVT.LU.D', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x62):
            if (rs2 == 0x00): return 'FCVT.W.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x01): return 'FCVT.WU.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x02): return 'FCVT.L.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x03): return 'FCVT.LU.H', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x68):
            if (rs2 == 0b000): return 'FCVT.S.W', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0b001): return 'FCVT.S.WU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0b010): return 'FCVT.S.L', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0b011): return 'FCVT.S.LU', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x69):
            if (rs2 == 0b00000): return 'FCVT.D.W', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0b00001): return 'FCVT.D.WU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0b00010): return 'FCVT.D.L', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0b00011): return 'FCVT.D.LU', f'x{rd}', f'x{rs1}', f'x{rs2}'
        if (func7 == 0x6A):
            if (rs2 == 0x00): return 'FCVT.H.W', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x01): return 'FCVT.H.WU', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x02): return 'FCVT.H.L', f'x{rd}', f'x{rs1}', f'x{rs2}'
            if (rs2 == 0x03): return 'FCVT.H.LU', f'x{rd}', f'x{rs1}', f'x{rs2}'
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
        if (func3 == 0x00): return 'BEQ', f'x{rd}', f'x{rs1}', simm12_B 
        if (func3 == 0x01): return 'BNE', f'x{rd}', f'x{rs1}', simm12_B 
        if (func3 == 0b100): return 'BLT', f'x{rd}', f'x{rs1}', simm12_B 
        if (func3 == 0b101): return 'BGE', f'x{rd}', f'x{rs1}', simm12_B 
        if (func3 == 0b110): return 'BLTU', f'x{rd}', f'x{rs1}', simm12_B 
        if (func3 == 0b111): return 'BGEU', f'x{rd}', f'x{rs1}', simm12_B 
    if (opcode == 0x67):
        if (func3 == 0x00): return 'JALR'
    if (opcode == 0x6F):
        return 'JAL',  f'x{rd}', off21_J
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
 
