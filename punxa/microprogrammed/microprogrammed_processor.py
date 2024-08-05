# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 09:26:27 2024

@author: 2016570
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

def dummy_print(*args, **kargs):
    pass

pr = print

class ControlUnit(py4hw.Logic):
    def __init__(self, parent, name:str, reset, status, control):
        super().__init__(parent, name)
        
        self.addIn('reset', reset)
        
        self.status = {}
        self.control = {}
        self.vstatus = {}
        self.vcontrol = {}
        
        for key in status.keys():
            self.status[key] = self.addIn(key, status[key])
            self.vstatus[key] = 0
            
        for key in control.keys():
            self.control[key] = self.addOut(key, control[key])
            self.vcontrol[key] = 0
            

        self.state = 'init'
        self.verbose = False
        
        self.co = self.run()
        
            
    def clock(self):
        for key in self.vstatus.keys():
            self.vstatus[key] = self.status[key].get()
        next(self.co)
        for key in self.vcontrol.keys():
            self.control[key].prepare(self.vcontrol[key])
    
    def fetchIns(self):
        self.state = 'fetch'
        self.vcontrol['sel_data_address'] = 0
        self.vcontrol['read'] = 1
        yield
        self.vcontrol['read'] = 1
        self.vcontrol['ena_IR'] = 1
        yield
        self.vcontrol['read'] = 0
        self.vcontrol['ena_IR'] = 0
        yield
        
        ins = self.vstatus['IR']
        self.decoded_ins = ins_to_str(ins, 64)
        
        if (self.parent.getPc() in self.parent.funcs.keys()):
            pr(self.parent.funcs[self.parent.getPc()], ':')
            
        if (is_compact_ins(ins)):
            ins = (ins & 0xFFFF)
            self.ins = ins
            pr('{:08X}: {:04X}         {} '.format(self.parent.getPc(), ins, self.decoded_ins), end='' )
        else:
            ins = (ins & 0xFFFFFFFF)
            self.ins = ins
            pr('{:08X}: {:08X}     {} '.format(self.parent.getPc() , ins, self.decoded_ins), end='' )
        
    def nextPC(self):
        self.state = 'nextpc'
        self.vcontrol['sel_alu_1_PC'] = 1
        self.vcontrol['sel_alu_2_4'] = 1
        self.vcontrol['alu_op_sum'] = 1
        self.vcontrol['ena_PC'] = 1
        yield
        self.vcontrol['sel_alu_1_PC'] = 0
        self.vcontrol['sel_alu_2_4'] = 0
        self.vcontrol['alu_op_sum'] = 0
        self.vcontrol['ena_PC'] = 0
        yield

    def writeCsr(self, csr, v):
        yield from self.loadRegFromImm('R', v)
        yield from self.saveRegToCsr('R', csr)
    
    def setCsr(self, csr, v):
        yield from self.loadRegFromCsr('R', csr)
        assert(v < (1<<16))
        self.vcontrol['control_imm'] = v
        yield from self.aluOp('or', 'R', 'control_imm', 'R')
        yield from self.saveRegToCsr('R', csr)
    
    def clearCSRBits(self, csr, start, bits):
        yield from self.loadRegFromCsr('R', csr)
        vcsr = self.parent._wires['R'].get()
        v = vcsr & (((1<<bits)-1) << start)
        yield from self.writeCsr(csr, vcsr ^ v)

    def getCSRField(self, csr, start, bits):
        yield from self.loadRegFromCsr('R', csr)
        vcsr = self.parent._wires['R'].get()
        return (vcsr >> start) & ((1<<bits)-1) 
        
    def setCSRField(self, csr, start, bits, value):
        yield from self.clearCSRBits(csr, start, bits)
        yield from self.setCsr(csr, ((value & (1<<bits)-1) << start))
        
    def loadRegFromImm(self, intReg, imm):
        self.state = f'{intReg} = 0x{imm:X}'
        yield
            
        if (imm >= (1 << 32)):
            raise Exception('big imm (>32 bits) not supported yet!')
        if (imm >= (1 << 16)):
            immh = imm >> 16
            self.vcontrol['control_imm'] = immh
            yield from self.aluOp('bypass2', 'A', 'control_imm', intReg)
            self.vcontrol['control_imm'] = 16
            yield from self.aluOp('shift_left', intReg, 'control_imm', intReg)
            self.vcontrol['control_imm'] = imm
            yield from self.aluOp('or', intReg, 'control_imm', intReg)
        else:
            self.vcontrol['control_imm'] = imm
            yield from self.aluOp('bypass2', 'A', 'control_imm', intReg)

    def loadRegFromCsr(self, intReg, csr):
        self.state = f'{intReg} = CSR[0x{csr:X}]'
        self.vcontrol['control_imm'] = 0x200 + csr * 8 
        
        yield from self.aluOp('sum', 'reg_base', 'control_imm', 'MAR')
        
        # MAR already contains the address

        
        # Read
        # [intreg] = [MAR] 
        self.vcontrol['read'] = 1
        self.vcontrol['sel_data_address'] = 1
        yield
        yield
        self.vcontrol[f'ena_{intReg}'] = 1
        self.vcontrol[f'sel_{intReg}_mem'] = 1
        self.vcontrol['read'] = 0
        yield
        self.vcontrol['sel_data_address'] = 0
        self.vcontrol[f'ena_{intReg}'] = 0
        self.vcontrol[f'sel_{intReg}_mem'] = 0
        yield
        
        vr = self.parent._wires[intReg].get()
        
        if (self.verbose):
            pr(f'[CU] loadRegFromMem {intReg} = CSR[0x{csr:X}] -> {vr}')
        
    def loadRegFromMem(self, intReg, extRegName):
        # intReg in ['A', 'B', 'R', 'PC']
        # extRegName in ['r1', 'r2', 'rd']
        self.state = f'{intReg} = {extRegName}'
        
        
        # MAR = baseRegisters + extReg * 8
        self.vcontrol[f'sel_mar_{extRegName}_offset'] = 1
        self.vcontrol['ena_MAR'] = 1
        yield
        self.vcontrol[f'sel_mar_{extRegName}_offset'] = 0
        self.vcontrol['ena_MAR'] = 0
        yield
        
        # Read
        # [MAR] = [intreg]
        self.vcontrol['read'] = 1
        self.vcontrol['sel_data_address'] = 1
        yield
        yield
        self.vcontrol[f'ena_{intReg}'] = 1
        self.vcontrol[f'sel_{intReg}_mem'] = 1
        self.vcontrol['read'] = 0
        yield
        self.vcontrol['sel_data_address'] = 0
        self.vcontrol[f'ena_{intReg}'] = 0
        self.vcontrol[f'sel_{intReg}_mem'] = 0
        yield
        
        vr = self.parent._wires[intReg].get()
        
        if (self.verbose): 
            pr(f'[CU] loadRegFromMem {intReg} = {extRegName} -> {vr}')
        
    def saveRegToCsr(self, intReg, csr):
        self.state = f'CSR[0x{csr:X}] = {intReg}'
        self.vcontrol['control_imm'] = 0x200 + csr * 8 
        
        yield from self.aluOp('sum', 'reg_base', 'control_imm', 'MAR')

        # [MAR] = [intreg]
        self.vcontrol[f'sel_writedata_{intReg}'] = 1
        self.vcontrol['sel_data_address'] = 1
        self.vcontrol['write'] = 1
        self.vcontrol['be'] = 0xF
        yield
        self.vcontrol[f'sel_writedata_{intReg}'] = 0
        self.vcontrol['sel_data_address'] = 0
        self.vcontrol['write'] = 0
        self.vcontrol['be'] = 0
        yield
        
    def saveReg(self, intReg, be=0xF):
        # saves the reg to the current MAR address
        # [MAR] = [intreg]
        self.vcontrol[f'sel_writedata_{intReg}'] = 1
        self.vcontrol['sel_data_address'] = 1
        self.vcontrol['write'] = 1
        self.vcontrol['be'] = be
        yield
        self.vcontrol[f'sel_writedata_{intReg}'] = 0
        self.vcontrol['sel_data_address'] = 0
        self.vcontrol['write'] = 0
        self.vcontrol['be'] = 0
        yield
        
    def saveRegToMem(self, intReg, extRegName):
        # intReg in ['A', 'B', 'R', 'PC']
        # extRegName in ['r1', 'r2', 'rd']
        ins = self.ins
        rd = (ins >> 7) & 0x1F
        if (extRegName == 'rd' and rd == 0):
            if (self.verbose):
                print('WARNING! Trying to write R0')
            # self.parent.parent.getSimulator().stop()
            return
        
        if (self.verbose):
            pr(f'[CU] saveRegToMem {extRegName} = {intReg}')
        
        # MAR = baseRegisters + extReg * 8
        self.vcontrol[f'sel_mar_{extRegName}_offset'] = 1
        self.vcontrol['ena_MAR'] = 1
        yield
        self.vcontrol[f'sel_mar_{extRegName}_offset'] = 0
        self.vcontrol['ena_MAR'] = 0
        yield

        yield from self.saveReg(intReg)
        
    def setPrivLevelToMPP(self):
        print('WARNING! should change priv level')
        # self.csr[CSR_PRIVLEVEL] = (self.csr[CSR_MSTATUS] >> 11) & ((1<<2)-1) # change to the MPP Mode (mstatus)
        yield    
        
    def orMPIEtoMSTATUS(self):
        print('WARNING! should set MSTATUS')
        #self.csr[CSR_MSTATUS] |= CSR_MSTATUS_MPIE_MASK
        yield
        
    # self.csr[CSR_MSTATUS] &= ~CSR_MSTATUS_MPRV_MASK     # clear the MPRV bit
    def clearMPP(self):
        print('WARNING! should clear MPP')
        #setCSRField(self, CSR_MSTATUS, CSR_MSTATUS_MPP_POS, 2, 0) # clear MPP
        yield

    def executeRIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F
        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F


        
        if (op == 'ADD'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            # R = A + B
            yield from self.aluOp('sum', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} + r{} -> {:016X}'.format(rd, rs1, rs2, vrd))

        elif (op == 'ADD.UW'):
            self.reg[rd] = (zeroExtend(self.reg[rs1], 32) + self.reg[rs2] ) & ((1<<64)-1)  
            pr('r{} = r{} + r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'AND'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            # R = A + B
            yield from self.aluOp('and', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} & r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
            
        elif (op == 'ANDN'):
            self.reg[rd] = self.reg[rs1] & ~self.reg[rs2]      
            pr('r{} = r{} & ~r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'OR'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            # R = A + B
            yield from self.aluOp('or', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} | r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
            
        elif (op == 'ORN'):
            self.reg[rd] = (self.reg[rs1] | ~self.reg[rs2]) & ((1<<64)-1)     
            pr('r{} = r{} | ~r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'XOR'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            # R = A + B
            yield from self.aluOp('xor', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')

            pr('r{} = r{} ^ r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
        elif (op == 'XNOR'):
            self.reg[rd] = (self.reg[rs1] ^ ~self.reg[rs2]) & ((1<<64)-1)      
            pr('r{} = r{} ^ r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SUB'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            # R = A + B
            yield from self.aluOp('sub', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')

            pr('r{} = r{} - r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
        elif (op == 'MUL'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            # R = A + B
            yield from self.aluOp('mul', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')
            
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
        elif (op == 'CLMUL'):
            self.reg[rd] = clmul(self.reg[rs1], self.reg[rs2]) & ((1<<64)-1)      
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'CLMULH'):
            self.reg[rd] = clmul(self.reg[rs1], self.reg[rs2]) >> 64       
            pr('r{} = r{} * r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'CLMULR'):
            self.reg[rd] = (self.reg[rs1] * self.reg[rs2]) & ((1<<64)-1)      
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
            self.reg[rd] = ( IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32) * IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)  )  & ((1<<32)-1)  
            pr('r{} = r{} * r{} -> {:08X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIV'):
            if (self.reg[rs2] == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                self.reg[rd] = int(IntegerHelper.c2_to_signed(self.reg[rs1], 64) / IntegerHelper.c2_to_signed(self.reg[rs2]  , 64)) & ((1<<64)-1)    
            pr('r{} = r{} / r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIVU'):
            if (self.reg[rs2] == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                self.reg[rd] = self.reg[rs1] // self.reg[rs2]      
            pr('r{} = r{} / r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIVW'):
            if (self.reg[rs2] == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                v1 = IntegerHelper.c2_to_signed(self.reg[rs1] & ((1<<32)-1), 32)
                v2 = IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)
                if (sign(v1) != sign(v2)):
                    v = -( abs(v1) // abs(v2) )
                    self.reg[rd] = signExtend(v & ((1<<32)-1), 32,64) 
                else:
                    v = ( v1 // v2 )
                    self.reg[rd] = signExtend(v & ((1<<32)-1), 32,64)  
            pr('r{} = r{} / r{} -> {:08X}'.format(rd, rs1, rs2, self.reg[rd]))            
        elif (op == 'DIVUW'):
            if (self.reg[rs2] == 0):
                self.reg[rd] = ((1<<64)-1)
            else:
                self.reg[rd] = signExtend((self.reg[rs1] & ((1<<32)-1)) // (self.reg[rs2] & ((1<<32)-1)), 32, 64) 
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
            v1 = self.reg[rs1]
            v2 = self.reg[rs2]
            if (v2 == 0):
                vr = v1
            else:
                vr = v1 % v2
            self.reg[rd] = vr      
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
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # B = r2
            yield from self.loadRegFromMem('B', 'r2')
            
            yield from self.aluOp('cmp', 'A', 'B', 'R')
            vcmp = self.parent._wires['R'].get()
            
            if ((vcmp & ALU_CMP_EQ) or (vcmp & ALU_CMP_GT)):
                # a > b
                vrd = self.parent._wires['A'].get()
                yield from self.saveRegToMem('A', 'rd')
            else:
                vrd = self.parent._wires['B'].get()
                yield from self.saveRegToMem('B', 'rd') 
            pr('r{} = max(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, vrd))

        elif (op == 'MAXU'):
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # B = r2
            yield from self.loadRegFromMem('B', 'r2')
            
            yield from self.aluOp('cmp', 'A', 'B', 'R')
            vcmp = self.parent._wires['R'].get()
            
            if ((vcmp & ALU_CMP_EQ) or (vcmp & ALU_CMP_GTU)):
                # a > b
                vrd = self.parent._wires['A'].get()
                yield from self.saveRegToMem('A', 'rd')
            else:
                vrd = self.parent._wires['B'].get()
                yield from self.saveRegToMem('B', 'rd') 

            pr('r{} = maxu(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, vrd))

        elif (op == 'MIN'):
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # B = r2
            yield from self.loadRegFromMem('B', 'r2')
            
            yield from self.aluOp('cmp', 'A', 'B', 'R')
            vcmp = self.parent._wires['R'].get()
            
            if ((vcmp & ALU_CMP_EQ) or (vcmp & ALU_CMP_LT)):
                # a > b
                vrd = self.parent._wires['A'].get()
                yield from self.saveRegToMem('A', 'rd')
            else:
                vrd = self.parent._wires['B'].get()
                yield from self.saveRegToMem('B', 'rd') 

            pr('r{} = min(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, vrd))

        elif (op == 'MINU'):
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # B = r2
            yield from self.loadRegFromMem('B', 'r2')
            
            yield from self.aluOp('cmp', 'A', 'B', 'R')
            vcmp = self.parent._wires['R'].get()
            
            if ((vcmp & ALU_CMP_EQ) or (vcmp & ALU_CMP_LTU)):
                # a > b
                vrd = self.parent._wires['A'].get()
                yield from self.saveRegToMem('A', 'rd')
            else:
                vrd = self.parent._wires['B'].get()
                yield from self.saveRegToMem('B', 'rd') 

            pr('r{} = minu(r{} , r{}) -> {:016X}'.format(rd, rs1, rs2, vrd))
            
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
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # B = r2
            yield from self.loadRegFromMem('B', 'r2')
            
            yield from self.aluOp('cmp', 'A', 'B', 'R')
            vcmp = self.parent._wires['R'].get()
            
            if (vcmp & ALU_CMP_LT):
                # a < b
                self.vcontrol['control_imm'] = 1                 
                yield from self.aluOp('bypass2', 'A', 'control_imm', 'R')
            else:
                self.vcontrol['control_imm'] = 0                 
                yield from self.aluOp('bypass2', 'A', 'control_imm', 'R')


            yield from self.saveRegToMem('R', 'rd')
            vrd = self.parent._wires['R'].get()
            
            pr('r{} = r{} < r{} -> {:016X}'.format(rd, rs1, rs2, vrd))                
        elif (op == 'SLTU'):
            self.reg[rd] = int(self.reg[rs1] < self.reg[rs2])
            pr('r{} = r{} < r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))                
        elif (op == 'ROR'): 
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            shv = self.parent._wires['B'].get()
            # R = A + B
            yield from self.aluOp('rotate_right', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} R>> r{} -> {:016X}'.format(rd, rs1, rs2, vrd))

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
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            shv = self.parent._wires['B'].get()
            # R = A + B
            yield from self.aluOp('rotate_left', 'A', 'B', 'R')
            vrd = self.parent._wires['R'].get()
            # rd = R
            yield from self.saveRegToMem('R', 'rd')

            pr('r{} = r{} R>> r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
            
        elif (op == 'ROLW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            if (shv > 0): 
                v = zeroExtend(self.reg[rs1], 32)
                v = ((v << shv ) | (v >> (32 - shv) )) & ((1<<32)-1)
            else: v = self.reg[rs1] 
            self.reg[rd] = signExtend(v , 32,64) 
            pr('r{} = r{} R<< r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))

        elif (op == 'SLL'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            #vr2 = self.parent._wires['B'].get()
            # R = A << shamt6
            yield from self.aluOp('shift_left', 'A', 'B', 'R')
            # rd = R
            vrd = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'rd')

            pr('r{} = r{} << r{} -> {:016X}'.format(rd, rs1, rs2, vrd))
            
        elif (op == 'SLLW'):
            shv = self.reg[rs2] & ((1<<5)-1)
            shifted = (self.reg[rs1] << shv) & ((1<<32)-1)
            self.reg[rd] = signExtend(shifted , 32, 64)       
            pr('r{} = r{} << r{} -> {:016X}'.format(rd, rs1, rs2, self.reg[rd]))
        elif (op == 'SRL'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # B = rs2
            yield from self.loadRegFromMem('B', 'r2')
            #vr2 = self.parent._wires['B'].get()
            # R = A << shamt6
            yield from self.aluOp('shift_right', 'A', 'B', 'R')
            # rd = R
            vrd = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} >> r{} -> {:016X}'.format(rd, rs1, rs2, vrd))

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
            self.reg[rd] = self.fpu.convert_hp_to_i32(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.WU.H'):
            self.reg[rd] = self.fpu.convert_hp_to_u32(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.WU.D'):
            self.reg[rd] = self.fpu.convert_dp_to_u32(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.W.S'):
            self.reg[rd] = self.fpu.convert_sp_to_i32(self.freg[rs1])
            pr('r{} = fr{} -> {:016X}'.format(rd, rs1, self.reg[rd]))
        elif (op == 'FCVT.WU.S'):
            self.reg[rd] = self.fpu.convert_sp_to_u32(self.freg[rs1])
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
                self.reg[rd] = 0    
                self.reserveAddress(-1,-1)
                pr('[r{}] = r{}, r[{}]=0 -> [{}]={:016X}'.format(rs1, rs2, rd, self.addressFmt(address), newvalue))
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
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= self.reg[rd] + self.reg[rs2] & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = [r{}] + r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOADD.W'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(self.reg[rd], 32, 64) 
            newvalue= self.reg[rd] + self.reg[rs2] & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = [r{}] + r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOAND.W'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(self.reg[rd], 32, 64) 
            newvalue= self.reg[rd] & self.reg[rs2] & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = [r{}] & r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOAND.D'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= self.reg[rd] & self.reg[rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = [r{}] & r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOOR.W'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(self.reg[rd], 32, 64) 
            newvalue= self.reg[rd] | self.reg[rs2] & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = [r{}] | r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOOR.D'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= self.reg[rd] | self.reg[rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = [r{}] | r{} -> [{}]={:016X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOXOR.W'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(self.reg[rd], 32,64) 
            newvalue= self.reg[rd] ^ self.reg[rs2] & 0xFFFFFFFF
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = [r{}] ^ r{} -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOXOR.D'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= self.reg[rd] ^ self.reg[rs2] 
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
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
            self.reg[rd] = v & ((1<<64)-1)
            newvalue= max(v , IntegerHelper.c2_to_signed(self.reg[rs2], 32)) & ((1<<32)-1)
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = max([r{}] , r{}) -> [{}]={:08X}'.format(rd, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMAXU.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = zeroExtend(v, 32) 
            self.reg[rd] = signExtend(v, 32,64) 
            newvalue= max(v , self.reg[rs2] & ((1<<32)-1))
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = max([r{}] , r{}) -> [{}]={:08X}'.format(rd, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMAX.D'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 64//8)
            self.reg[rd] = signExtend(v, 64, 64) 
            newvalue= max(self.reg[rd] , self.reg[rs2]) & ((1<<64)-1)
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
            self.reg[rd] = v & ((1<<64)-1)
            newvalue= min(v , IntegerHelper.c2_to_signed(self.reg[rs2] & ((1<<32)-1), 32)) & ((1<<32)-1)
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMINU.W'):
            address = self.reg[rs1]
            v = yield from self.virtualMemoryLoad(address, 32//8)
            v = zeroExtend(v, 32) 
            self.reg[rd] = signExtend(v, 32,64) 
            newvalue= min(v , self.reg[rs2] & ((1<<32)-1))
            yield from self.virtualMemoryWrite(address, 32//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMIN.D'):
            address = self.reg[rs1]
            vm = yield from self.virtualMemoryLoad(address, 64//8)
            vm = IntegerHelper.c2_to_signed(vm, 64)
            vr = IntegerHelper.c2_to_signed(self.reg[rs2], 64)
            self.reg[rd] = vm & ((1<<64)-1)
            newvalue= min(vm , vr) & ((1<<64)-1)
            yield from self.virtualMemoryWrite(address, 64//8, newvalue)
            pr('[r{}] = min([r{}] , r{}) -> [{}]={:08X}'.format(rs1, rs1, rs2, self.addressFmt(address), newvalue))
        elif (op == 'AMOMINU.D'):
            address = self.reg[rs1]
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            newvalue= min(self.reg[rd] , self.reg[rs2]) & ((1<<64)-1)
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
    
    def executeJIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F
        off21_J = compose_sign(ins, [[31,1], [12,8], [20,1], [21,10]]) << 1  


        if (op == 'JAL'):
            jmpCall = (rd == 0)
            
            # if rd != 0
            if (rd != 0):
                if (self.verbose):
                    pr('[CU] R = PC + 4')
                
                # R = pc + 4
                yield from self.aluOp('sum', 'P', '4', 'R')
                
                # reg[rd] = R
                # pr(f'[CU] r{rd} = R')

                yield from saveRegToMem('R', 'rd')


                
            self.should_jump = True
            self.jmp_address = self.parent.getPc() + off21_J
            
            
            
            # PC = PC + off21_J
            yield from self.aluOp('sum', 'PC', 'off21_J', 'PC')
                
            self.parent.functionEnter(self.jmp_address, jmpCall)
            
            if (rd== 0):
                pr('pc + {} ->  {}'.format(off21_J, self.parent.addressFmt(self.jmp_address)))
            else:                
                pr('pc + {}  r{}=pc+4 ->  {},{:016X}'.format(off21_J, rd, self.parent.addressFmt(self.jmp_address), self.reg[rd]))
    
        yield
        
    def executeBIns(self):
        op = self.decoded_ins
        ins = self.ins

        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F
        soff12 = compose_sign(ins, [[31,1], [7,1], [25,6], [8,4]]) << 1

        # A = r1
        yield from self.loadRegFromMem('A', 'r1')
        # B = r2 
        yield from self.loadRegFromMem('B', 'r2')
        # R = r1 - r2
        yield from self.aluOp('cmp', 'A', 'B', 'R')

        vr = self.parent._wires['R'].get() 

        iseq = vr & 1
        isneq = not(iseq)
        isltu = (vr >> 1) & 1
        islt = (vr >> 2) & 1
        isgtu = (vr >> 3) & 1
        isgt = (vr >> 4) & 1
        isge = isgt or iseq
        isgeu = isgtu or iseq
        
        if (op == 'BEQ'):
            if (iseq):
                self.should_jump=True
        elif (op == 'BGE'):
            if (isge):
                self.should_jump=True
        elif (op == 'BGEU'):
            if (isgeu):
                self.should_jump=True
        elif (op == 'BLT'):
            if (islt):
                self.should_jump=True
        elif (op == 'BLTU'):
            if (isltu):
                self.should_jump=True
        elif (op == 'BNE'):
            if (isneq):
                self.should_jump=True
        else:
            print(' - BIns Not supported!')
            self.parent.getSimulator().stop()

        self.jmp_address = self.parent.getPc() + soff12
            
        if (self.should_jump):
            yield from self.aluOp('sum', 'PC', 'soff12', 'PC')

        pr('r{} != r{} ? {} pc+0x{:X} = {:016X}'.format(rs1, rs2, self.should_jump, soff12, self.jmp_address))    

    def executeSIns(self):
        op = self.decoded_ins
        ins = self.ins

        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F
        
        soff12_S = compose_sign(ins, [[25,7],[7,5]])

        yield from self.loadRegFromMem('B', 'r2')
        vr2 = self.parent._wires['B'].get()
        
        yield from self.loadRegFromMem('A', 'r1')
        yield from self.aluOp('sum', 'A', 'soff12_S', 'MAR')
        address = self.parent._wires['MAR'].get()
        #address = self.reg[rs1]+soff12
        saddr = self.parent.addressFmt(address)

        
        if (op == 'SD'):
            pr('[r{} + {}] = r{} -> [{}]={:016X}'.format(rs1, soff12_S, rs2, saddr, self.reg[rs2]))
            yield from self.virtualMemoryWrite(address, 64//8, self.reg[rs2])
        elif (op == 'FSH'):
            pr('[r{} + {}] = fr{} -> [{}]={:016X}'.format(rs1, soff12_S, rs2, saddr, self.freg[rs2]))
            yield from self.virtualMemoryWrite(address, 16//8, self.freg[rs2])
        elif (op == 'FSD'):
            pr('[r{} + {}] = fr{} -> [{}]={:016X}'.format(rs1, soff12_S, rs2, saddr, self.freg[rs2]))
            yield from self.virtualMemoryWrite(address, 64//8, self.freg[rs2])
        elif (op == 'FSW'):
            pr('[r{} + {}] = fr{} -> [{}]={:08X}'.format(rs1, soff12_S, rs2, saddr, self.freg[rs2]))
            yield from self.virtualMemoryWrite(address, 32//8, self.freg[rs2])
        elif (op == 'SW'):
            yield from self.saveReg('B', be=0x7)
            pr('[r{} + {}] = r{} -> [{}]={:08X}'.format(rs1, soff12_S, rs2, saddr, vr2 & ((1<<32)-1)))
            #yield from self.virtualMemoryWrite(address, 32//8, self.reg[rs2])
        elif (op == 'SH'):
            
            pr('[r{} + {}] = r{} -> [{}]={:04X}'.format(rs1, soff12_S, rs2, saddr, vr2 & ((1<<16)-1)))
            #yield from self.virtualMemoryWrite(address, 16//8, self.reg[rs2])
            raise Exception('not implemented')
        elif (op == 'SB'):
            address = self.reg[rs1]+soff12
            pr('[r{} + {}] = r{} -> [{}]={:02X}'.format(rs1, soff12_S, rs2, saddr, self.reg[rs2] & ((1<<8)-1)))
            yield from self.virtualMemoryWrite(address, 8//8, self.reg[rs2])
        else:
            print(' - S-Type instruction not supported!')
            self.parent.getSimulator().stop()

    def aluOp(self, op, p1, p2, prr):
        sop = {'sum':'+', 'sub':'-', 'mul':'*', 'cmp':'cmp', 
               'and':'&', 'or':'|', 'xor':'^',
               'shift_left':'<<', 'shift_right':'>>',
               'rotate_left':'r<<', 'rotate_right':'r>>',
               'bypass2':'*0 + '}
        
        self.state = f'{prr} = {p1} {sop[op]} {p2}'

        if (self.verbose):
            pr(f'[CU] {prr} = {p1} {sop[op]} {p2}')
        
        self.vcontrol[f'sel_alu_1_{p1}'] = 1
        self.vcontrol[f'sel_alu_2_{p2}'] = 1
        self.vcontrol[f'alu_op_{op}'] = 1
        self.vcontrol[f'ena_{prr}'] = 1
        yield
        self.vcontrol[f'sel_alu_1_{p1}'] = 0
        self.vcontrol[f'sel_alu_2_{p2}'] = 0
        self.vcontrol[f'alu_op_{op}'] = 0
        self.vcontrol[f'ena_{prr}'] = 0
        yield
 
    def signExtend(self, reg, wfrom, wto):
        rs = wto - wfrom
        yield from self.aluOp('shift_left', reg, str(rs), reg)
        yield from self.aluOp('shift_right', reg, str(rs), reg)

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
            if (self.verbose):
                pr('[CU] ADDI')
            
            yield from self.loadRegFromMem('A', 'r1')
            yield from self.aluOp('sum', 'A', 'simm12', 'R')
            
            vr = self.parent._wires['R'].get()

            yield from self.saveRegToMem('R', 'rd')
            
            pr('r{} = r{} + {} -> {:016X}'.format(rd, rs1, simm12, vr))
        elif (op == 'SLTI'):
            self.reg[rd] = 0            
            if  (IntegerHelper.c2_to_signed(self.reg[rs1], 64) < simm12):
                self.reg[rd] = 1
            pr('r{} = r{} < {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'SLTIU'):
            self.reg[rd] = 0            
            if  (self.reg[rs1] < signExtend(simm12, 12, 64)):
                self.reg[rd] = 1
            pr('r{} = r{} < {} -> {:016X}'.format(rd, rs1, simm12, self.reg[rd]))
        elif (op == 'ANDI'):
            if (self.verbose): pr('[CU] ANDI')
            yield from self.loadRegFromMem('A', 'r1')
            yield from self.aluOp('and', 'A', 'simm12', 'R')
            vr = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} & {} -> {:016X}'.format(rd, rs1, simm12, vr))

        elif (op == 'ADDIW'):
            if (self.verbose): pr('[CU] ADDIW')
            
            yield from self.loadRegFromMem('A', 'r1')
            yield from self.aluOp('sum', 'A', 'simm12', 'R')

            yield from self.signExtend('R', 32, 64)            
            vr = self.parent._wires['R'].get()

            yield from self.saveRegToMem('R', 'rd')
     
            pr('r{} = r{} + {} -> {:016X}'.format(rd, rs1, simm12, vr))
            
        elif (op == 'ORI'):
            if (self.verbose): pr('[CU] ORI')
            yield from self.loadRegFromMem('A', 'r1')
            yield from self.aluOp('or', 'A', 'simm12', 'R')

            yield from self.signExtend('R', 32, 64)            
            vr = self.parent._wires['R'].get()

            yield from self.saveRegToMem('R', 'rd')
            
            pr('r{} = r{} | {} -> {:016X}'.format(rd, rs1, simm12, vr))

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
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 64//8)
            pr('r{} = [r{} + {}] -> [{}]={:016X}'.format(rd, rs1, simm12, self.addressFmt(address), self.reg[rd]))
        elif (op == 'LW'):
            address = self.reg[rs1] + simm12
            pr('r{} = [r{} + {}] '.format(rd, rs1, simm12), end = '')
            v = yield from self.virtualMemoryLoad(address, 32//8)
            self.reg[rd] = signExtend(v, 32, 64) 
            pr('-> [{}]={:016X}'.format(self.addressFmt(address), self.reg[rd]))
        elif (op == 'LWU'):
            address = self.reg[rs1] + simm12
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 32//8)
            pr('r{} = [r{} + {}] -> [{}]={:016X}'.format(rd, rs1, simm12, self.addressFmt(address), self.reg[rd]))
        elif (op == 'LH'):
            address = self.reg[rs1] + simm12
            v = yield from self.virtualMemoryLoad(address, 16//8)
            self.reg[rd] = signExtend(v, 16, 64) 
            pr('r{} = [r{} + {}] -> [{}]={:016X}'.format(rd, rs1, simm12, self.addressFmt(address), self.reg[rd]))
        elif (op == 'LHU'):
            address = self.reg[rs1] + simm12
            self.reg[rd] = yield from self.virtualMemoryLoad(address, 16//8)
            pr('r{} = [r{} + {}] -> [{}]={:04X}'.format(rd, rs1, simm12, self.addressFmt(address), self.reg[rd]))
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
            pr('r{}'.format(rs1))
            
        elif (op == 'CSRRW'):
            csrname = self.parent.implemented_csrs[csr]
            
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            v1 = self.parent._wires['A'].get()
            
            
            # B = csr
            yield from self.loadRegFromMem('B', 'csr')     
            vcsr = self.parent._wires['B'].get()
            
            # rd = B
            yield from self.saveRegToMem('B', 'rd')
            
            # csr = A
            yield from self.saveRegToMem('A', 'csr')
            
            #v1 = self.reg[rs1]
            #vcsr, allowed = self.readCSR(csr)
            #if (rd == 0):
            #    self.writeCSR(csr, v1)
            #    
            #    pr('{} = r{} -> {:016X}'.format(csrname, rs1, self.csr[csr]))            
            #else:
            #    self.writeCSR(csr, v1)
            #    if (rd != 0) and (allowed): self.reg[rd] = vcsr
            #    csrname = self.implemented_csrs[csr]
                
            if (rd == 0):
                pr('{} = r{} -> {:016X}'.format(csrname, rs1, v1))
            else:
                pr('r{} = {}, {} = r{} -> {:016X},{:016X}'.format(rd, csrname, csrname, rs1, vcsr, v1))

        elif (op == 'CSRRS'):
            # Read and set
            # rd <= csr, csr <= csr | rs1 
            
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            
            # B = csr
            yield from self.loadRegFromMem('B', 'csr')            
            
            # rd = B, 
            if (rd != 0):
                yield from self.saveRegToMem('B', 'rd')
                vrd = self.parent._wires['B'].get()
            
            # R = A | B
            yield from self.aluOp('or', 'A', 'B', 'R')
            
            # csr = R
            vcsr = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'csr')
            
            #vcsr, allowed = self.readCSR(csr)
            #if (v1 != 0): self.setCSR(csr, v1)
            #if (rd != 0) and allowed: self.reg[rd] = vcsr
            csrname = self.parent.implemented_csrs[csr]
            
            if (rd == 0):
                pr('{} |= r{} -> {:016X}'.format(csrname, rs1, vcsr)) 
            elif (rs1 == 0):
                pr('r{} = {} -> {:016X}'.format(rd, csrname, vrd))           
            else:
                pr('r{} = {}, {} |= r{} -> {:016X},{:016X}'.format(rd, csrname, csrname, rs1, vrd, vcsr))            
        
        elif (op == 'CSRRC'):
            # Read and clear
            # rd <= csr, csr <= csr & ^rs1 

            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            
            # B = csr
            yield from self.loadRegFromMem('B', 'csr')            
            
            # rd = B, 
            if (rd != 0):
                yield from self.saveRegToMem('B', 'rd')
                vrd = self.parent._wires['B'].get()

            # B = B ^ -1
            yield from self.aluOp('xor', 'B', 'm1', 'B')
            # R = A & B
            yield from self.aluOp('and', 'A', 'B', 'R')
            
            # csr = R
            vcsr = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'csr')

            #v1 = self.reg[rs1]
            #csrv , allowed = self.readCSR(csr)
            #if (v1 != 0): self.clearCSR(csr, v1)
            #if (rd != 0) and allowed: self.reg[rd] = csrv
            csrname = self.parent.implemented_csrs[csr]
            
            if (rd == 0):
                pr('{} &= ~r{} -> {:016X}'.format(csrname, rs1, vcsr))            
            else:
                pr('r{} = {}, {} &= ~r{} -> {:016X},{:016X}'.format(rd, csrname, csrname, rs1, vrd, vcsr))            
        
        elif (op == 'CSRRWI'):
            csrname = self.parent.implemented_csrs[csr]
            
            # A = csr
            yield from self.loadRegFromMem('A', 'csr')
            
            # B = rs1
            yield from self.loadRegFromMem('B', 'r1')            

            # rd = A
            yield from self.saveRegToMem('A', 'rd')
            vrd = self.parent._wires['A'].get()
            
            # csr = B
            yield from self.saveRegToMem('B', 'csr')
            
            if (rd == 0):
                pr('{} = {}'.format(csrname, rs1))
            else:
                pr('r{} = {}, {} = {} -> {:016X}'.format(rd, csrname, csrname, rs1, vrd))
                
        elif (op == 'CSRRSI'):
            # A = r1
            #yield from self.loadRegFromMem('A', 'r1')
            yield from self.aluOp('bypass2', 'A', 'r1', 'A')
            
            # B = csr
            yield from self.loadRegFromMem('B', 'csr')            
            
            # rd = B, 
            if (rd != 0):
                yield from self.saveRegToMem('B', 'rd')
                vrd = self.parent._wires['B'].get()
            
            # R = A | B
            yield from self.aluOp('or', 'A', 'B', 'R')
            
            # csr = R
            vcsr = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'csr')


            #crsv, allowed = self.readCSR(csr)
            #if (rs1 != 0): self.setCSR(csr, rs1)
            #if (rd != 0) and allowed: self.reg[rd] = crsv
            csrname = self.parent.implemented_csrs[csr]

            if (rd == 0):
                pr('{} |= {} -> {:016X}'.format(csrname, rs1, vcsr))       
            else:
                pr('r{} = {}, {} |= {} -> {:016X}, {:016X}'.format(rd, csrname, csrname, rs1, vrd, vcsr))       
                 
        elif (op == 'CSRRCI'):
            crsv, allowed = self.readCSR(csr)
            if (rs1 != 0): self.clearCSR(csr, rs1)
            if (rd != 0) and allowed: self.reg[rd] = crsv
            csrname = self.implemented_csrs[csr]
            pr('r{} = {}, {} &= ~{} -> {:016X}'.format(rd, csrname, csrname, rs1, self.reg[rd]))                        
        elif (op == 'RORI'):
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # R = A r>> shamt6
            yield from self.aluOp('rotate_right', 'A', 'shamt6', 'R')
            # rd = R
            vcsr = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'rd')

            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, vrd))
            
        elif (op == 'RORIW'):
            v = ((self.reg[rs1] >> shamt6) | (self.reg[rs1] << (32-shamt6))) & ((1<<32)-1)
            self.reg[rd] = signExtend(v, 32, 64)
            pr('r{} = r{} >> {} -> {:016X}'.format(rd, rs1, shamt6, self.reg[rd]))
        elif (op == 'SLLI'):
            # A = rs1
            yield from self.loadRegFromMem('A', 'r1')
            # R = A << shamt6
            yield from self.aluOp('shift_left', 'A', 'shamt6', 'R')
            # rd = R
            vrd = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'rd')
            pr('r{} = r{} << {} -> {:016X}'.format(rd, rs1, shamt6, vrd))
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
            
            yield from self.loadRegFromCsr('PC', CSR_MEPC)
            self.jmp_address = self.parent._wires['PC'].get()
            
            self.parent.functionExit()
            
            yield from self.setPrivLevelToMPP()
            yield from self.orMPIEtoMSTATUS()
            # self.csr[CSR_MSTATUS] &= ~CSR_MSTATUS_MPRV_MASK     # clear the MPRV bit
            yield from self.clearMPP()
            
            pr('pc = mepc -> {:016X}'.format(self.jmp_address)) 
        elif (op == 'SRET'):
            if (self.csr[CSR_MSTATUS] & CSR_MSTATUS_TSR_MASK ):
                raise IllegalInstruction('SRET with TSR', self.ins)
                
            self.should_jump = True
            self.jmp_address = self.csr[CSR_SEPC]
            self.functionExit()
            self.csr[CSR_PRIVLEVEL] = (self.csr[CSR_MSTATUS] >> 8) & 1 # we use MSTATUS instead of SSTATUS. change to the SPP Mode (status)   
            pr('pc = sepc -> {:016X}'.format(self.jmp_address)) 
        elif (op == 'JALR'):
            self.should_jump = True
            
            if (rd != 0):
                # R = PC + 4
                yield from self.aluOp('sum', 'PC', 'k4', 'R')
                # rd = R
                yield from self.saveRegToMem('R', 'rd')
                vrd = self.parent._wires['R'].get()
                
            # A = r1
            yield from self.loadRegFromMem('A', 'r1')
            # PC = r1 + simm12
            yield from self.aluOp('sum', 'A', 'simm12', 'PC')
            
            self.jmp_address = self.parent._wires['PC'].get()            
            jmpCall = (rd != 1) # or (rd == 0) 
            
            if (rd == 0):
                pr('r{} +  {} -> {}'.format(rs1, simm12, self.parent.addressFmt(self.jmp_address)))
            else:
                pr('r{} + {} , r{} = pc+4 -> {},{}'.format(rs1, simm12, rd, self.parent.addressFmt(self.jmp_address), self.parent.addressFmt(vrd)))
            self.parent.functionEnter(self.jmp_address, jmpCall)

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
            yield from self.loadRegFromCsr('R', 0xFFF)
            #curpriv = self.csr[0xFFF] # current privilege
            curpriv = self.parent._wires['R'].get()
            
            if (curpriv == 3): 
                raise EnvCallMMode()
            elif (curpriv == 1):
                raise EnvCallSMode()
            elif (curpriv == 0):
                raise EnvCallUMode()
            else:
                raise Exception('unknown privilege level {}'.format(curpriv))
        elif (op == 'EBREAK'):
            raise Breakpoint()
        else:
            raise Exception('{} I-Type instruction not supported!'.format(op))
            #self.parent.getSimulator().stop()
    
    def executeUIns(self):
        op = self.decoded_ins
        ins = self.ins

        rd = (ins >> 7) & 0x1F
        rs1 = (ins >> 15) & 0x1F
        rs2 = (ins >> 20) & 0x1F

        if (op == 'AUIPC'):
            simm = compose(ins, [[12,20]]) << 12
            simm = signExtend(simm, 32, 64)
            
            yield from self.aluOp('sum', 'PC', 'simm20', 'R')
            vr = self.parent._wires['R'].get()
            yield from self.saveRegToMem('R', 'rd')
            
            pr('r{} = pc + {:08X} -> {:016X}'.format(rd, simm, vr))      
            
        elif (op == 'LUI'):
            # A = 0 (probably rs1 is 0)
            yield from self.loadRegFromImm('A', 0)
            
            # R = A + simm20            
            yield from self.aluOp('sum', 'A', 'simm20', 'R')
            
            # rd = R
            yield from self.saveRegToMem('R', 'rd')
            
            simm20 = (compose_sign(ins, [[12,20]]) << 12) & ((1<<64)-1)

            pr('r{} = {:016X} '.format(rd, simm20))    
        else:
            pr(' - U-Type instruction not supported!')
            self.parent.getSimulator().stop()
            
    def execute(self):
        op = self.decoded_ins

        if (op in RTypeIns):
            yield from self.executeRIns()
        elif (op in JTypeIns):
            yield from self.executeJIns()
        elif (op in BTypeIns):
            yield from self.executeBIns()
        elif (op in ITypeIns):
            yield from self.executeIIns()
        elif (op in UTypeIns):
            yield from self.executeUIns()  
        elif (op in STypeIns):
            yield from self.executeSIns()
        elif (op == 'FENCE'):
            pr('ignored')
        elif (op == 'FENCE.I'):
            pr('ignored')
        else:
            raise Exception('{} - Not supported!'.format(op))

    def run(self):
        while True:
            try:
                self.should_jump = False
                yield from self.fetchIns()
                yield from self.execute()

            except ProcessorException as e:
                pr('\n\tException:', e.msg, 'code:', e.code, f'tval: 0x{e.tval:X}',  end=' ' )
                
                yield from self.loadRegFromCsr('R', CSR_PRIVLEVEL)
                priv = self.parent._wires['R'].get()
                

                # Exceptions are always handled by machine mode, unless they are delegated
                # to lower modes
                
                if (priv == CSR_PRIVLEVEL_MACHINE): # machine
                    yield from self.setCsr(CSR_MSTATUS, (3 << 11))
                elif (priv == CSR_PRIVLEVEL_SUPERVISOR): # supervisor
                    self.csr[CSR_MSTATUS] |= (1 << 11) # set M-Mode as previous mode in MPP

                yield from self.loadRegFromCsr('R', CSR_MEDELEG)
                medeleg = self.parent._wires['R'].get() 
                #medeleg = self.csr[CSR_MEDELEG] # medeleg
                
                if (get_bit(medeleg, e.code)):
                    # this should be delegated to supervisor mode
                    vec = self.csr[CSR_STVEC] # stvec
                    self.csr[CSR_STVAL] = e.tval
                    self.csr[0x100] |= (priv << 8) # set previous mode in SPP
                    self.csr[CSR_SEPC] = self.pc # sepc
                    self.csr[CSR_SCAUSE] = e.code  # scause
                    vecname = self.implemented_csrs[0x105]
                    self.csr[CSR_PRIVLEVEL] = 1

                else:
                    # this is executed in machine mode    
                    yield from self.loadRegFromCsr('R', CSR_MTVEC)
                    vec = self.parent._wires['R'].get() 
                    
                    yield from self.writeCsr(CSR_MTVAL, e.tval)
                    yield from self.setCsr(CSR_MSTATUS, priv << 11) # set previous mode in MPP
                    yield from self.saveRegToCsr('PC', CSR_MEPC)
                    yield from self.writeCsr(CSR_MCAUSE, e.code)
                    
                    v = yield from self.getCSRField(CSR_MSTATUS, CSR_MSTATUS_MPIE_POS, 1)
                    yield from self.setCSRField(CSR_MSTATUS, CSR_MSTATUS_MPIE_POS, 1, v)
                    yield from self.setCSRField(CSR_MSTATUS, CSR_MSTATUS_MIE_POS, 1, 0)
                    
                    vecname = self.parent.implemented_csrs[0x305]
                    yield from self.writeCsr(CSR_PRIVLEVEL, 3)
                    
                addr = vec & 0xFFFFFFFFFFFFFFFC
                self.should_jump = True
                
                if ((vec & 3) == 0):
                    # should change this
                    pr('jumping to {}'.format(vecname), hex(addr))
                    yield from self.loadRegFromImm('PC', addr)
                elif ((vec & 3) == 1):
                    addr = addr + e.code * 4
                    yield from self.loadRegFromImm('PC', addr)
            
                               
                
            if (self.should_jump):
                # jump to the PC 
                pass
            else:
                # pr('[CU] pc = pc + 4')
                yield from self.nextPC()

def AbstractClassInit(self, parent:py4hw.Logic, name:str):
    super(self.__class__, self).__init__(parent, name)
    
def AbstractClass(class_name):
    return type(class_name, # class name
                (py4hw.Logic,), # base classes
                {'__init__': AbstractClassInit} # methods
                )

    
def compose_sign_hw(parent, name, a, pairs, shiftLeft):
    abstract_class = AbstractClass(name)
    obj = abstract_class(parent, name)
    
    rname = f'{name}_r'
    pr = parent.wire(rname, 64)
    
    obj.addIn(a.name, a)
    obj.addOut('r', pr)
    r = []
    hlp = py4hw.LogicHelper(obj)
    for pair in pairs:
        down = pair[0]
        up = down + pair[1] - 1
        r.append(hlp.hw_range(a, up, down))
    preshift = hlp.hw_concatenate_msbf(r)
    
    r = hlp.hw_shift_left_constant(preshift, shiftLeft)
    
    SignExtend(obj, 'sign_ext', r, pr)
    return pr

def compose_hw(parent, name, a, pairs, shiftLeft):
    abstract_class = AbstractClass(name)
    obj = abstract_class(parent, name)

    rname = f'{name}_r'
    pr = parent.wire(rname, 64)

    obj.addIn(a.name, a)
    obj.addOut('r', pr)

    r = []
    hlp = py4hw.LogicHelper(obj)
    for pair in pairs:
        down = pair[0]
        up = down + pair[1] - 1
        r.append(hlp.hw_range(a, up, down))
    preshift = hlp.hw_concatenate_msbf(r)
    
    if (shiftLeft > 0):
        r = hlp.hw_shift_left_constant(preshift, shiftLeft)
    else:
        r = preshift
        
    py4hw.Buf(obj, 'pr', r, pr)
    
    return pr

ALU_CMP_GT =  1 << 4
ALU_CMP_GTU = 1 << 3
ALU_CMP_LT =  1 << 2
ALU_CMP_LTU = 1 << 1
ALU_CMP_EQ =  1

class ALU(py4hw.Logic):
    def __init__(self, parent, name:str, q_i, q_a, q_b, q_pc, q_r, alu_r, control, registerBase):
        super().__init__(parent, name)
        
        self.q_i = self.addIn('q_i', q_i)
        self.q_a = self.addIn('q_a', q_a)
        self.q_b = self.addIn('q_b', q_b)
        self.q_pc = self.addIn('q_pc', q_pc)
        self.q_r = self.addIn('q_r', q_r)
        
        self.alu_r = self.addOut('alu_r', alu_r)
        
        hlp = py4hw.LogicHelper(self)
        k_reg_base = hlp.hw_constant(64, registerBase)
        
        off21_J = compose_sign_hw(self, 'off21_J', q_i, [[31,1], [12,8], [20,1], [21,10]], 1)   
        soff12 = compose_sign_hw(self, 'soff12', q_i, [[31,1], [7,1], [25,6], [8,4]], 1) 
        soff12_S = compose_sign_hw(self, 'soff12_S', q_i, [[25,7],[7,5]], 0)

        simm12 = compose_sign_hw(self, 'simm12', q_i, [[20, 12]], 0)
        simm20 = compose_sign_hw(self, 'simm20', q_i, [[12, 20]], 12)
        shamt6 = compose_hw(self, 'shamt6', q_i, [[20,6]], 0)

        used_controls = ['sel_alu_1_A', 'sel_alu_1_B', 'sel_alu_1_R', 'sel_alu_1_PC', 'sel_alu_1_reg_base',
                         'sel_alu_2_4', 'sel_alu_2_32', 'sel_alu_2_m1', 'sel_alu_2_r1',
                         'sel_alu_2_off21_J', 
                         'sel_alu_2_soff12', 'sel_alu_2_soff12_S', 'sel_alu_2_simm12', 
                         'sel_alu_2_simm20', 'sel_alu_2_shamt6', 'sel_alu_2_B',
                         'sel_alu_2_control_imm', 
                         'alu_op_sum', 'alu_op_sub', 'alu_op_mul', 'alu_op_cmp', 'alu_op_or',
                         'alu_op_shift_left', 'alu_op_shift_right',
                         'alu_op_rotate_left', 'alu_op_rotate_right',
                         'alu_op_bypass2',
                         'control_imm']
        
        self.control = {}
        for key in control.keys():
            if (key in used_controls):
                self.control[key] = self.addIn(key, control[key])
            
        alu_1 = self.wire('alu_1', 64)
        alu_2 = self.wire('alu_2', 64)
        
        k4 = self.wire('k4', 64)
        k32 = self.wire('k32', 64)
        km1 = self.wire('km1', 64)
        r1 = self.wire('r1', 64)
        control_imm = self.wire('control_imm', 64)
        
        py4hw.ZeroExtend(self, 'control_imm', control['control_imm'], control_imm)
        
        py4hw.Constant(self, 'k4', 4, k4)
        py4hw.Constant(self, 'k32', 32, k32)
        py4hw.Constant(self, 'km1', -1, km1)
        
        r1 = compose_hw(self, 'r1', q_i, [[15,5]], 0)

        py4hw.OneHotMux(self, 'alu_1', 
                     [control['sel_alu_1_A'], 
                      control['sel_alu_1_B'], 
                      control['sel_alu_1_R'], 
                      control['sel_alu_1_PC'],
                      control['sel_alu_1_reg_base']], 
                     [q_a, q_b, q_r, q_pc, k_reg_base], 
                     alu_1)
        
        py4hw.OneHotMux(self, 'alu_2', 
                     [control['sel_alu_2_4'],
                      control['sel_alu_2_32'],
                      control['sel_alu_2_m1'],
                      control['sel_alu_2_r1'],
                      control['sel_alu_2_off21_J'], 
                      control['sel_alu_2_soff12'],
                      control['sel_alu_2_soff12_S'],
                      control['sel_alu_2_simm12'],
                      control['sel_alu_2_simm20'],
                      control['sel_alu_2_shamt6'],
                      control['sel_alu_2_B'],
                      control['sel_alu_2_control_imm']], 
                     [k4, k32, km1, r1, off21_J, soff12, soff12_S, simm12, simm20, shamt6, q_b, control_imm], 
                     alu_2)
        
        alu_add_r = self.wire('alu_add_r', 64)
        alu_sub_r = self.wire('alu_sub_r', 64)
        alu_mul_r = self.wire('alu_mul_r', 64)
        alu_and_r = self.wire('alu_and_r', 64)
        alu_or_r = self.wire('alu_or_r', 64)
        alu_xor_r = self.wire('alu_xor_r', 64)
        alu_cmp_r = self.wire('alu_cmp_r', 64)
        
        alu_shift_left_r = self.wire('alu_shift_left_r', 64)
        alu_shift_right_r = self.wire('alu_shift_right_r', 64)
        alu_rotate_left_r = self.wire('alu_rotate_left_r', 64)
        alu_rotate_right_r = self.wire('alu_rotate_right_r', 64)
        
        py4hw.Add(self, 'add', alu_1, alu_2, alu_add_r)
        py4hw.Sub(self, 'sub', alu_1, alu_2, alu_sub_r)
        py4hw.Mul(self, 'mul', alu_1, alu_2, alu_mul_r)
        py4hw.And2(self, 'and', alu_1, alu_2, alu_and_r)
        py4hw.Or2(self, 'or', alu_1, alu_2, alu_or_r)
        py4hw.Xor2(self, 'xor', alu_1, alu_2, alu_xor_r)
        
        gt = self.wire('gt')
        gtu = self.wire('gtu')
        lt = self.wire('lt')
        ltu = self.wire('ltu')
        eq = self.wire('eq')
        
        py4hw.ComparatorSignedUnsigned(self, 'cmp', alu_1, alu_2, gtu, eq, ltu, gt, lt)
        
        py4hw.ConcatenateMSBF(self, 'alu_cmp_r', [gt,gtu,lt,ltu,eq], alu_cmp_r)
        
        
        # maximum shifting is 1<<6 = 64 bits
        alu_2_shift = self.wire('alu_2_shift', 6)
        
        py4hw.Range(self, 'alu_2_shift', alu_2, 5, 0, alu_2_shift)
        
        py4hw.ShiftLeft(self, 'shift_left', alu_1, alu_2_shift, alu_shift_left_r)
        py4hw.ShiftRight(self, 'shift_right', alu_1, alu_2_shift, alu_shift_right_r)
        py4hw.RotateLeft(self, 'rotate_left', alu_1, alu_2_shift, alu_rotate_left_r)
        py4hw.RotateRight(self, 'rotate_right', alu_1, alu_2_shift, alu_rotate_right_r)
        
        py4hw.OneHotMux(self, 'select_alu_r', 
                        [control['alu_op_sum'], 
                         control['alu_op_sub'], 
                         control['alu_op_mul'], 
                         control['alu_op_cmp'], 
                         control['alu_op_and'],
                         control['alu_op_or'],
                         control['alu_op_xor'],
                         control['alu_op_shift_left'],
                         control['alu_op_shift_right'],
                         control['alu_op_rotate_left'],
                         control['alu_op_rotate_right'],
                         control['alu_op_bypass2']],
                        [alu_add_r, alu_sub_r, alu_mul_r, alu_cmp_r, 
                         alu_and_r, alu_or_r, alu_xor_r,
                         alu_shift_left_r, alu_shift_right_r, 
                         alu_rotate_left_r, alu_rotate_right_r, 
                         alu_2],
                        alu_r)
                        
        
class MicroprogrammedRISCV(py4hw.Logic):
    
    def __init__(self, parent, name:str, 
                 reset,
                 memory:MemoryInterface, 
                 int_soft_machine, int_timer_machine, ext_int_targets, resetAddress, registerBase):

        super().__init__(parent, name)
        
        self.mem = self.addInterfaceSource('memory', memory)

        self.addIn('reset', reset)
        self.int_soft_machine = self.addIn('int_soft_machine', int_soft_machine)
        self.int_timer_machine = self.addIn('int_timer_machine', int_timer_machine)
        self.int_ext_machine = self.addIn('int_ext_machine', ext_int_targets[0])
        self.int_ext_supervisor = self.addIn('int_ext_supervisor', ext_int_targets[0])        
        
        self.funcs = {}
        self.stack = []             # list of addresses

        self.registerBase = registerBase
        
        status = {}
        control = {}
        
        self.implemented_csrs = {}
        
        self.initStaticCSRs()
        self.initDynamicCSRs()
        
        self.tracer = Tracer()
        self.enable_tracing = True
        self.min_clks_for_trace_event = 0
        self.ignore_unknown_functions = True

        hlp = py4hw.LogicHelper(self)
        
        q_a = self.wire('A', 64)
        q_b = self.wire('B', 64)
        q_r = self.wire('R', 64)
        q_mar = self.wire('MAR', 64)
        q_i = self.wire('IR', 32)
        self.q_pc = self.wire('PC', 64)
        
        d_a = self.wire('dA', 64)
        d_b = self.wire('dB', 64)
        d_r = self.wire('dR', 64)
        d_mar = self.wire('dMAR', 64)
        d_i = self.wire('dIR', 32)
        d_pc = self.wire('dPC', 64)
        
        control['ena_A'] = self.wire('ena_A')
        control['ena_B']= self.wire('ena_B')
        control['ena_R'] = self.wire('ena_R')
        control['ena_MAR'] = self.wire('ena_MAR')
        control['ena_IR'] = self.wire('ena_IR')
        control['ena_PC'] = self.wire('ena_PC')
        
        control['sel_alu_1_A'] = self.wire('sel_alu_1_A')
        control['sel_alu_1_B'] = self.wire('sel_alu_1_B')
        control['sel_alu_1_R'] = self.wire('sel_alu_1_R')
        control['sel_alu_1_PC'] = self.wire('sel_alu_1_PC')
        control['sel_alu_1_reg_base'] = self.wire('sel_alu_1_reg_base')
        
        
        control['sel_alu_2_4'] = self.wire('sel_alu_2_4')
        control['sel_alu_2_32'] = self.wire('sel_alu_2_32')
        control['sel_alu_2_m1'] = self.wire('sel_alu_2_m1')
        control['sel_alu_2_r1'] = self.wire('sel_alu_2_r1')
        control['sel_alu_2_off21_J'] = self.wire('sel_alu_2_off21_J')
        control['sel_alu_2_soff12'] = self.wire('sel_alu_2_soff12')
        control['sel_alu_2_soff12_S'] = self.wire('sel_alu_2_soff12_S')
        
        control['sel_alu_2_simm12'] = self.wire('sel_alu_2_simm12')
        control['sel_alu_2_simm20'] = self.wire('sel_alu_2_simm20')
        control['sel_alu_2_shamt6'] = self.wire('sel_alu_2_shamt6')
        control['sel_alu_2_B'] = self.wire('sel_alu_2_B')
        control['sel_alu_2_control_imm'] = self.wire('sel_alu_2_control_imm')
        #control['sel_alu_2_r1_offset'] = self.wire('sel_alu_2_r1_offset')
        #control['sel_alu_2_r2_offset'] = self.wire('sel_alu_2_r2_offset')
        #control['sel_alu_2_rd_offset'] = self.wire('sel_alu_2_rd_offset')
        
        control['sel_data_address'] = self.wire('sel_data_address')
        
        control['sel_writedata_A'] = self.wire('sel_writedata_A')
        control['sel_writedata_B'] = self.wire('sel_writedata_B')
        control['sel_writedata_R'] = self.wire('sel_writedata_R')
        control['sel_writedata_PC'] = self.wire('sel_writedata_PC')
        
        control['write'] = memory.write
        control['read'] = memory.read
        control['be'] = memory.be
        
        control['sel_A_mem'] = self.wire('sel_A_mem')
        control['sel_B_mem'] = self.wire('sel_B_mem')
        control['sel_R_mem'] = self.wire('sel_R_mem')
        control['sel_IR_mem'] = self.wire('sel_IR_mem')
        #control['sel_MAR_mem'] = self.wire('sel_MAR_mem')
        control['sel_PC_mem'] = self.wire('sel_PC_mem')
        
        control['sel_mar_r1_offset'] = self.wire('sel_mar_r1_offset')
        control['sel_mar_r2_offset'] = self.wire('sel_mar_r2_offset')
        control['sel_mar_rd_offset'] = self.wire('sel_mar_rd_offset')
        control['sel_mar_csr_offset'] = self.wire('sel_mar_csr_offset')
        
        control['control_imm'] = self.wire('control_imm', 16)
        
        py4hw.OneHotMux(self, 'sel_writedata', 
                     [control['sel_writedata_A'], 
                      control['sel_writedata_B'], 
                      control['sel_writedata_R'], 
                      control['sel_writedata_PC']],
                     [q_a, q_b, q_r, self.q_pc], memory.write_data)

        py4hw.Buf(self, 'd_i', memory.read_data, d_i)
        
        alu_r = self.wire('alu_r', 64)      
        
        rd_m8 = compose_hw(self, 'rd_m8', q_i, [[7, 5]], 3)
        rs1_m8 = compose_hw(self, 'rs1_m8', q_i, [[15,5]], 3)
        rs2_m8 = compose_hw(self, 'rs2_m8', q_i, [[20,5]], 3)
        csr_m8 = compose_hw(self, 'csr_m8', q_i, [[20, 12]], 3)
        #csrimm_m8 = compose_hw(self, 'csrimm_m8', q_i, [[0, 12]], 3)

        base_regs = hlp.hw_constant(64, registerBase)
        base_fregs = hlp.hw_constant(64, 32 * 8)
        base_csrs =  hlp.hw_constant(64, 64 * 8)
        r1_offset = hlp.hw_or2(base_regs, rs1_m8)
        r2_offset = hlp.hw_or2(base_regs, rs2_m8)
        rd_offset = hlp.hw_or2(base_regs, rd_m8)
        csr_offset = hlp.hw_or2(base_regs, hlp.hw_add(base_csrs, csr_m8))
        #csrimm_offset = hlp.hw_or2(base_regs, hlp.hw_add(base_csrs, csrimm_m8))        
        
        py4hw.Mux2(self, 'sel_A', control['sel_A_mem'], alu_r, memory.read_data, d_a)
        py4hw.Mux2(self, 'sel_B', control['sel_B_mem'], alu_r, memory.read_data, d_b)
        py4hw.Mux2(self, 'sel_R', control['sel_R_mem'], alu_r, memory.read_data, d_r)
        py4hw.Mux2(self, 'sel_PC', control['sel_PC_mem'], alu_r, memory.read_data, d_pc)
        
        py4hw.SelectDefault(self, 'sel_MAR', 
                            [control['sel_mar_r1_offset'], 
                             control['sel_mar_r2_offset'], 
                             control['sel_mar_rd_offset'],
                             control['sel_mar_csr_offset']],
                            [r1_offset, r2_offset, rd_offset, csr_offset], alu_r, d_mar)
        
        py4hw.Reg(self, 'A', d_a, q_a, control['ena_A'], reset)
        py4hw.Reg(self, 'B', d_b, q_b, control['ena_B'], reset)
        py4hw.Reg(self, 'R', d_r, q_r, control['ena_R'], reset)
        py4hw.Reg(self, 'MAR', d_mar, q_mar, control['ena_MAR'], reset)
        py4hw.Reg(self, 'I', d_i, q_i, control['ena_IR'], reset)
        py4hw.Reg(self, 'PC', d_pc, self.q_pc, control['ena_PC'], reset, reset_value=resetAddress)
        
        py4hw.Mux2(self, 'sel_data_address', control['sel_data_address'], self.q_pc, q_mar, memory.address)
        
        status['IR'] = q_i
        status['write_resp'] = memory.resp

        control['alu_op_sum'] = self.wire('alu_op_sum')
        control['alu_op_sub'] = self.wire('alu_op_sub')
        control['alu_op_mul'] = self.wire('alu_op_mul')
        control['alu_op_cmp'] = self.wire('alu_op_cmp')
        control['alu_op_and'] = self.wire('alu_op_and')
        control['alu_op_or'] = self.wire('alu_op_or')
        control['alu_op_xor'] = self.wire('alu_op_xor')
        control['alu_op_shift_left'] = self.wire('alu_op_shift_left')
        control['alu_op_shift_right'] = self.wire('alu_op_shift_right')
        control['alu_op_rotate_left'] = self.wire('alu_op_rotate_left')
        control['alu_op_rotate_right'] = self.wire('alu_op_rotate_right')
        control['alu_op_bypass2'] = self.wire('alu_op_bypass2')
        
        ALU(self, 'ALU', q_i, q_a, q_b, self.q_pc, q_r, alu_r, control, registerBase)

        ControlUnit(self, 'CU', reset, status, control)
        
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

    def getReg(self, idx):
        regbase = self.registerBase - self.behavioural_memory.mem_base
        return self.behavioural_memory.read_i64(regbase + idx * 8)

    def getFreg(self, idx):
        regbase = self.registerBase - self.behavioural_memory.mem_base
        fregbase = regbase + 32*8
        return self.behavioural_memory.read_i64(fregbase + idx * 8)
        
    def getCSR(self, idx):
        regbase = self.registerBase - self.behavioural_memory.mem_base
        fregbase = regbase + 32*8
        csrBase = fregbase + 32*8 
        return self.behavioural_memory.read_i64(csrBase+ idx * 8)
    
    def getPc(self):
        return self.q_pc.get()
    
    
    def functionEnter(self, f, jmp=False):
        # jmp is True if the enter to the function was done with a jump, which
        # should provoke to pop the parent from the stack when exiting

        if (jmp):
            if (len(self.stack) > 1) and (self.stack[-1][0] == f):
                return
        
        clks = self.parent.getSimulator().total_clks
        pair = (f, clks, jmp)
        self.stack.append(pair)

        if (not(self.enable_tracing)):
            return
        
        fn = f
        # @todo remove fn ,translation should be done at stack command
        #if (fn in self.funcs.keys()): 
        #    fn = self.funcs[f]
        
        pairn = (fn, clks, jmp)        
        self.tracer.start(pairn)
                
    def functionExit(self):
        if (len(self.stack) == 0):
            return
    		
        finfo = self.stack.pop()

        clks = self.parent.getSimulator().total_clks
        
        f = finfo[0]
        t0 = finfo[1]
        jmp = finfo[2]

        if (self.enable_tracing):
    
            fn = f
            if (fn in self.funcs.keys()):
                fn = self.funcs[f]

            if (isinstance(fn, int) and self.ignore_unknown_functions):
                fn = None

            tf = clks
            dur = tf - t0
            
            if (dur < self.min_clks_for_trace_event) or (fn is None):
                self.tracer.ignore(fn)
            else:            
                self.tracer.complete((fn, t0, tf))
        
        if (jmp):
            # repeat exit
            self.functionExit()

    def addressFmt(self, address):
        #phy_address = self.getPhysicalAddressQuick(address)
        phy_address = address
        
        if (phy_address in self.funcs.keys()):
            return '{:X} <{}>'.format(phy_address, self.funcs[phy_address])
            
        return '{:016X}'.format(address)

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

        #self.csr[CSR_MISA] = 2 << 62 | self.encodeFeatures('ACDIFMSU') # misa
        #self.csr[CSR_MCPUID] = 2 << 62 | self.encodeFeatures('ACDIFMSU') # mcpuid
        #self.csr[0xf10] = 0 # mhartid @todo is this wrong???

        #self.csr[CSR_MVENDORID] = 0x414255 # UAB
        #self.csr[CSR_MARCHID] = 0
        #self.csr[CSR_MIMPID] = 0x70756e7861323431  # @todo should be reversed
        #self.csr[CSR_MHARTID] = 0 # mhartid
        

        self.implemented_csrs[CSR_MCPUID] = 'mcpuid'
        self.implemented_csrs[CSR_MVENDORID] = 'mvendorid'
        self.implemented_csrs[CSR_MARCHID] = 'marchid'
        self.implemented_csrs[CSR_MIMPID] = 'mimpid'
        self.implemented_csrs[CSR_MHARTID] = 'mhartid'
        

    def initDynamicCSRs(self):

        self.implemented_csrs[CSR_MISA] = 'misa'
        self.implemented_csrs[CSR_FFLAGS] = 'fflags'
        self.implemented_csrs[CSR_FRM] = 'frm'
        
        # self.csr[CSR_FRM] = CSR_FRM_RTZ
        
        self.implemented_csrs[CSR_FCSR] = 'fcsr'
        
        self.implemented_csrs[CSR_SSTATUS] = 'sstatus'
        self.implemented_csrs[CSR_SIE] = 'sie'
        self.implemented_csrs[0x105] = 'stvec'        
        self.implemented_csrs[0x106] = 'scounteren'
        
        self.implemented_csrs[0x140] = 'sscratch'
        self.implemented_csrs[0x141] = 'sepc'
        self.implemented_csrs[0x142] = 'scause'
        self.implemented_csrs[0x143] = 'stval'
        self.implemented_csrs[0x144] = 'sip'

        self.implemented_csrs[CSR_SATP] = 'satp'

        #self.csr[CSR_MSTATUS] = CSR_MSTATUS_SXL_64_BITS_MASK | CSR_MSTATUS_UXL_64_BITS_MASK
        self.implemented_csrs[CSR_MSTATUS] = 'mstatus'
        
        self.implemented_csrs[0x302] = 'medeleg'
        self.implemented_csrs[0x303] = 'mideleg'
        self.implemented_csrs[0x304] = 'mie'
        self.implemented_csrs[0x305] = 'mtvec'
        self.implemented_csrs[0x306] = 'mcounteren'
        
        self.implemented_csrs[0x320] = 'mcountinhibit'

        for i in range(3,32):
            self.implemented_csrs[0x320+i] = 'mhpmevent{}'.format(i)


        self.implemented_csrs[0x340] = 'mscratch'
        self.implemented_csrs[0x341] = 'mepc'
        self.implemented_csrs[0x342] = 'mcause'
        self.implemented_csrs[0x343] = 'mtval'
        self.implemented_csrs[0x344] = 'mip'
        self.implemented_csrs[0x380] = 'mbase'
        
        self.implemented_csrs[0x3A0] = 'pmpcfg0'
        

        for i in range(1): # was 64 (not 1)
            self.implemented_csrs[0x3B0+i] = 'pmpaddr{}'.format(i)
        
        self.implemented_csrs[CSR_TSELECT] = 'tselect'
        self.implemented_csrs[CSR_TDATA1] = 'tdata1'
        self.implemented_csrs[CSR_TDATA2] = 'tdata2'
        self.implemented_csrs[CSR_TDATA3] = 'tdata3'
        self.implemented_csrs[CSR_TCONTROL] = 'tcontrol'
        self.implemented_csrs[CSR_MCONTEXT] = 'mcontext'

        self.implemented_csrs[CSR_MCYCLE] = 'mcycle'
        self.implemented_csrs[CSR_MINSTRET] = 'minstret'

        # for i in range(3,32):
        #     self.implemented_csrs[0xB00+i] = 'mhpmcounter{}'.format(i)

        self.implemented_csrs[CSR_MNSCRATCH] = 'mnscratch'
        self.implemented_csrs[CSR_MNEPC] = 'mnepc'
        self.implemented_csrs[CSR_MNCAUSE] = 'mncause'
        self.implemented_csrs[CSR_MNSTATUS] = 'mnstatus'
 
        self.implemented_csrs[CSR_CYCLE] = 'cycle'
        self.implemented_csrs[CSR_TIME] = 'time'
        self.implemented_csrs[CSR_INSTRET] = 'instret'
        
        self.implemented_csrs[CSR_PRIVLEVEL] = 'privlevel'  # this is my own CSR to store the current privilege level

        #self.csr[CSR_PRIVLEVEL] = CSR_PRIVLEVEL_MACHINE # (Machine =3, Supervisor = 1, User = 0)
        
    