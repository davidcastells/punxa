import sys
import py4hw
from py4hw.helper import *
import numpy as np
from decimal import Decimal
    
from .temp_helper import *
from .csr import *

        
FP_CLASS_NEG_INF = 1 << 0
FP_CLASS_NEG_NORMAL = 1 << 1
FP_CLASS_NEG_SUBNORMAL = 1 << 2
FP_CLASS_NEG_ZERO = 1 << 3
FP_CLASS_POS_ZERO = 1 << 4
FP_CLASS_POS_SUBNORMAL = 1 << 5
FP_CLASS_POS_NORMAL = 1 << 6
FP_CLASS_POS_INF = 1 << 7
FP_CLASS_SNAN = 1 << 8
FP_CLASS_QNAN = 1 << 9




    
class FPU:
    
    def __init__(self, cpu):
        self.cpu = cpu
        
    def sp_unbox(self, x):
        # gets the sp from the dp
        mask = ((1<<32)-1)
        h = (x >> 32) & mask
        l = x & mask
        if (h == mask):
            # correct NaN boxed value, return lower part
            return l
        else:
            return IEEE754_SP_CANONICAL_NAN

    def hp_unbox(self, x):
        mask = ((1 << 16) -1)
        h = (x >> 16) & ((1<<48)-1)
        l = x & mask
        if (h == ((1<<48)-1)):
            # correct NaN boxed value, return lower part
            return l
        else:
            return IEEE754_HP_CANONICAL_NAN
        
    def hp_box(self, x):
        # generates Nan boxed dp from sp
        mask = ((1<<48)-1) << 16
        return mask | x
            
    def sp_box(self, x):
        # generates Nan boxed dp from sp
        mask = ((1<<32)-1) << 32
        return mask | x
        
    def is_boxed(self, x):
        mask = ((1<<32)-1) << 32
        return ((x & mask) == mask)

    def is_half_boxed(self, x):
        mask = ((1<<48)-1) << 16
        return ((x & mask) == mask)


    def class_hp(self, xv):
        v = FPNum(self.hp_unbox(xv), 'hp')
        s, e, m = v.unpack_ieee754_hp_parts(xv)
                
        if (v.infinity):
            if (s == 1): return FP_CLASS_NEG_INF
            else: return FP_CLASS_POS_INF
        if (v.nan):
            if (m == 1): return FP_CLASS_SNAN
            else: return FP_CLASS_QNAN
        if (v.m == 0):
            if (s == 1): return FP_CLASS_NEG_ZERO
            else: return FP_CLASS_POS_ZERO
        if (e == 0):
            if (s == 1): return FP_CLASS_NEG_SUBNORMAL
            else: return FP_CLASS_POS_SUBNORMAL
            
        if (s == 1): return FP_CLASS_NEG_NORMAL
        else: return FP_CLASS_POS_NORMAL

    def class_sp(self, xv):
        v = FPNum(self.sp_unbox(xv), 'sp')
        s, e, m = v.unpack_ieee754_sp_parts(xv)
                
        if (v.infinity):
            if (s == 1): return FP_CLASS_NEG_INF
            else: return FP_CLASS_POS_INF
        if (v.nan):
            if (m == 1): return FP_CLASS_SNAN
            else: return FP_CLASS_QNAN
        if (v.m == 0):
            if (s == 1): return FP_CLASS_NEG_ZERO
            else: return FP_CLASS_POS_ZERO
        if (e == 0):
            if (s == 1): return FP_CLASS_NEG_SUBNORMAL
            else: return FP_CLASS_POS_SUBNORMAL
            
        if (s == 1): return FP_CLASS_NEG_NORMAL
        else: return FP_CLASS_POS_NORMAL

    def class_dp(self, x):
        fp = FloatingPointHelper()
        v = fp.ieee754_to_dp(x)
        s,e,m = fp.ieee754_dp_split(x)
        
        isinf = math.isinf(v)
        isnan = math.isnan(v)
        isquietnan = (isnan and (m >> 51))
        issignalingnan = (isnan and not(m >> 51))
        
        iszero = (v == 0)
        isnormal = (not(isinf) and not(isnan) and not(iszero))
        issubnormal = (isnormal and (e==0))
        sign = math.copysign(1, v)
        isneg = (sign == -1)
        ispos = (sign == 1)
        r = 0
        if (isinf and isneg):
            r |= 1 << 0
        if (isnormal and isneg):
            if (not(issubnormal)):
                r |= 1 << 1
            else:
                r |= 1 << 2
        if (iszero and isneg):
            r |= 1 << 3
        if (iszero and ispos):
            r |= 1 << 4
        if (isnormal and ispos):
            if (issubnormal):
                r |= 1 << 5
            else:
                r |= 1 << 6
        if (isinf and ispos):
            r |= 1 << 7
        if (issignalingnan):
            r |= 1 << 8
        if (isquietnan):
            r |= 1 << 9
        return r
                
    def sign_inject_dp(self, xa, xb):
        return (xa & ((1<<63)-1)) | ((1<<63) & xb)
        
    def sign_n_inject_dp(self, xa, xb):
        return (xa & ((1<<63)-1)) | ((1<<63) & (xb ^ ((1<<64)-1)))
        
    def sign_xor_inject_dp(self, xa, xb):
        return (xa & ((1<<63)-1)) | (((1<<63) & xa) ^ ((1<<63) & xb))
        
    def sign_inject_sp(self, xa, xb):
        f1_high_0 = ((xa >> 32) == 0) 
        f1_high_1 = ((xa >> 32) == ((1<<32)-1))
        f2_high_0 = ((xb >> 32) == 0) 
        f2_high_1 = ((xb >> 32) == ((1<<32)-1))
        
        f1_valid = (f1_high_0 or f1_high_1)
        f2_valid = (f2_high_0 or f2_high_1)
        
        fp = FloatingPointHelper()
        b = fp.ieee754_to_sp(xb)
        
        sign_a = ((xa>>31) & 1) 
        
        if (self.is_boxed(xb)):
            sign_b = ((xb>>31) & 1) 
        else:
            sign_b = ((xb>>63) & 1) 
        sign_r = sign_b
        
        #abs a
        if (sign_a): xa = xa ^ (1 << 31)
        
        if (f1_valid and f2_valid):
            # valid single precision       
            return self.sp_box(xa | (sign_r<<31) )
        else:
            if (not(f1_valid) and f2_high_1):
                return ((1<<32)-1)<<32 | (1<<31) | IEEE754_SP_CANONICAL_NAN
            elif (not(f2_valid) and (b==0)):
                return xa
            else:
                return ((1<<32)-1)<<32 | IEEE754_SP_CANONICAL_NAN
                
    def sign_inject_half(self, xa, xb):
        
        fp = FloatingPointHelper()
        b = fp.ieee754_to_sp(xb)
        
        sign_a = ((xa>>15) & 1) 
        
        if (self.is_half_boxed(xb)):
            sign_b = ((xb>>15) & 1) 
        else:
            sign_b = ((xb>>63) & 1) 
        sign_r = sign_b
        
        #abs a
        if (sign_a): xa = xa ^ (1 << 15)
        
        if (True): # (f1_valid and f2_valid):
            # valid half precision       
            return self.hp_box(xa | (sign_r<<15) )
        else:
            if (not(f1_valid) and f2_high_1):
                return ((1<<32)-1)<<32 | (1<<31) | IEEE754_SP_CANONICAL_NAN
            elif (not(f2_valid) and (b==0)):
                return xa
            else:
                return ((1<<32)-1)<<32 | IEEE754_SP_CANONICAL_NAN

    def sign_n_inject_half(self, xa, xb):
        return self.sign_inject_half(xa, self.sp_box(xb ^ (1<<15)))
                
    def sign_n_inject_sp(self, xa, xb):
        return self.sign_inject_sp(xa, self.sp_box(xb ^ (1<<31)))

    def fsub_dp(self, xa, xb):
        fp = FloatingPointHelper()
        return self.fma_dp(fp.dp_to_ieee754(1.0), xa , FloatingPointHelper.ieee754_dp_neg(xb))  
    
    def fms_hp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')
        c = FPNum(self.hp_unbox(xc), 'hp')
    
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        c.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.mul(b).sub(c)
    
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.hp_box(r.convert('hp'))

    def fms_sp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')
        c = FPNum(self.sp_unbox(xc), 'sp')
    
        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        c.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.mul(b).sub(c)
    
        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.sp_box(r.convert('sp'))

    def fms_dp(self, xa, xb, xc):
        return self.fma_dp(xa , xb, FloatingPointHelper.ieee754_dp_neg(xc))
 
    def fnms_hp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')
        c = FPNum(self.hp_unbox(xc), 'hp')
    
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        c.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.mul(b).sub(c).neg()
    
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.hp_box(r.convert('hp'))


    def fnms_sp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')
        c = FPNum(self.sp_unbox(xc), 'sp')
    
        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        c.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.mul(b).sub(c).neg()
    
        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.sp_box(r.convert('sp'))

    def fma_hp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')
        c = FPNum(self.hp_unbox(xc), 'hp')
    
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        c.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.mul(b).add(c)
    
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.hp_box(r.convert('hp'))

    def fma_sp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')
        c = FPNum(self.sp_unbox(xc), 'sp')
    
        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        c.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.mul(b).add(c)
    
        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.sp_box(r.convert('sp'))

    def fma_dp(self, xa, xb, xc):
        # fused multiply-add r = a*b +c
        # update floating point flags
        from decimal import Decimal
        
        fp = FloatingPointHelper()
        a = fp.ieee754_to_dp(xa)
        b = fp.ieee754_to_dp(xb)
        c = fp.ieee754_to_dp(xc)
        
        self.cpu.csr[CSR_FFLAGS] = 0
        r = a*b+c
            
        if (math.isnan(r)):
            xr = 0x7FF8000000000000 # signaling Nan
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK 
        elif (math.isinf(a) and math.isinf(b)):
            if (math.copysign(1, a) == math.copysign(1, b)):
                r = a           
                xr = fp.dp_to_ieee754(r)
            else:
                print('Invalid inf')
                xr = 0x7FF8000000000000 # signaling Nan
                self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            rd = Decimal(a)*Decimal(b)+Decimal(c)
        
            if (rd != r):
                self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INEXACT_MASK
            
            xr = fp.dp_to_ieee754(r)
            
        return xr

    def fnma_hp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')
        c = FPNum(self.hp_unbox(xc), 'hp')
    
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        c.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.mul(b).add(c).neg()
    
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.hp_box(r.convert('hp'))

    def fnma_sp(self, xa, xb, xc):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')
        c = FPNum(self.sp_unbox(xc), 'sp')
    
        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        c.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.mul(b).add(c).neg()
    
        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
                
        return self.sp_box(r.convert('sp'))
    
    def set_sp_result(self, r):
        # @todo should be removed
        fp = FloatingPointHelper()

        self.cpu.csr[CSR_FFLAGS] = 0

        if (math.isnan(r)):
            xr = 0x7FC00000 # Nan
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            '''            
            elif (math.isinf(a) and math.isinf(b)):
                if (math.copysign(1, a) == math.copysign(1, b)):
                    r = a           
                    xr = fp.sp_to_ieee754(r)
                else:
                    print('Invalid inf')
                    xr = 0x7F800000 # signaling Nan
                    self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            '''
        else:
            xr = fp.sp_to_ieee754(r)
            r2 = fp.ieee754_to_sp(xr)
            
            if (r != r2):
                self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INEXACT_MASK            
            
        return self.sp_box(xr)
        
    def set_dp_result(self, r, precisionLoss = None):
        # @todo should be removed
        fp = FloatingPointHelper()

        self.cpu.csr[CSR_FFLAGS] = 0

        if (math.isnan(r)):
            xr = 0x7FC0000000000000 # Nan
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            '''            
            elif (math.isinf(a) and math.isinf(b)):
                if (math.copysign(1, a) == math.copysign(1, b)):
                    r = a           
                    xr = fp.sp_to_ieee754(r)
                else:
                    print('Invalid inf')
                    xr = 0x7F800000 # signaling Nan
                    self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            '''
        else:
            xr = fp.dp_to_ieee754(r)

            if (precisionLoss is None):
                r2 = fp.ieee754_to_dp(xr)
                precisionLoss = (r != r2)
            
            if (precisionLoss):
                self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INEXACT_MASK            
            
        return xr

    def fdiv_hp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'hp')
        b = FPNum(self.sp_unbox(xb), 'hp')
    
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.div(b)
    
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        else:
            r2 = r.mul(b)
            if (r2.compare(a) != 0): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        
        return self.hp_box(r.convert('hp'))

    def fdiv_sp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')

        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.div(b)

        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        else:
            r2 = r.mul(b)
            if (r2.compare(a) != 0): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        
        return self.sp_box(r.convert('sp'))

   

    def fdiv_dp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(xa, 'dp')
        b = FPNum(xb, 'dp')

        a.reducePrecision(IEEE754_DP_PRECISION)
        b.reducePrecision(IEEE754_DP_PRECISION)

        r = a.div(b)
        
        r.reducePrecisionWithRounding(IEEE754_DP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        else:
            r2 = r.mul(b)
            if (r2.compare(a) != 0): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)

        return r.convert('dp')

    def fsqrt_hp(self, xa):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        
        if (a.s == -1): 
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            r = FPNum(1, 0x1F, IEEE754_HP_NAN_MANTISA, 0) # nan
            return self.hp_box(r.convert('hp'))
        
        a.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.sqrt()
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        r3 = FPNum(r.convert('hp'), 'hp')
        
        # check result to fix inexact flag
        r2 = r3.mul(r3)
        
        if (r2.compare(a) != 0):
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
         
        return self.hp_box(r.convert('hp'))

    def fsqrt_sp(self, xa):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        
        if (a.s == -1): 
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            r = FPNum(1, 0xFF, IEEE754_SP_NAN_MANTISA, 0) # nan
            return self.sp_box(r.convert('sp'))
            
        a.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.sqrt()
        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        r3 = FPNum(r.convert('sp'), 'sp')
        
        # check result to fix inexact flag
        r2 = r3.mul(r3)
        
        if (r2.compare(a) != 0):
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
         
        return self.sp_box(r.convert('sp'))

    def fsqrt_dp(self, xa):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(xa, 'dp')
        
        if (a.s == -1): 
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            r = FPNum(1, 0x7FF, IEEE754_DP_NAN_MANTISA, 0) # nan
            return r.convert('dp')
            
        a.reducePrecision(IEEE754_DP_PRECISION)
        
        r = a.sqrt()
        r.reducePrecisionWithRounding(IEEE754_DP_PRECISION)
        
        r3 = FPNum(r.convert('dp'), 'dp')
        r2 = r3.mul(r3)
        
        if (r2.compare(a) != 0):
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
         
        return r.convert('dp')
     
        
    def fsub_hp(self, xa, xb):
        a = FPNum(self.sp_unbox(xa), 'hp')
        b = FPNum(self.sp_unbox(xb), 'hp')
    
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.sub(b)
    
        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        self.last_result = r
        
        return self.sp_box(r.convert('hp'))
     
        
    def fsub_sp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')
    
        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.sub(b)
    
        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.nan): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
        elif (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        
        return self.sp_box(r.convert('sp'))
    
    def fadd_hp(self, xa, xb):
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')

        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.add(b)

        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        self.last_result = r
        
        return self.hp_box(r.convert('hp'))

    def fadd_sp(self, xa, xb):
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')

        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.add(b)

        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        self.last_result = r
        
        return self.sp_box(r.convert('sp'))
    
    def fmul_hp(self, xa, xb):
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')

        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        
        r = a.mul(b)

        r.reducePrecisionWithRounding(IEEE754_HP_PRECISION)
        
        self.last_result = r
        
        return self.hp_box(r.convert('hp'))

    def fmul_sp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')

        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        
        r = a.mul(b)

        r.reducePrecisionWithRounding(IEEE754_SP_PRECISION)
        
        if (r.inexact): 
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        
        return self.sp_box(r.convert('sp'))

    def fadd_dp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(xa, 'dp')
        b = FPNum(xb, 'dp')

        a.reducePrecision(IEEE754_DP_PRECISION)
        b.reducePrecision(IEEE754_DP_PRECISION)
        
        r = a.add(b)

        r.reducePrecisionWithRounding(IEEE754_DP_PRECISION)
        
        if (r.inexact): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INEXACT_MASK)
        
        return r.convert('dp')

    def fma_sp(self, xa, xb, xc):
        # fused multiply-add r = a*b +c
        # update floating point flags
        
        fp = FloatingPointHelper()
        a = fp.ieee754_to_sp(xa)
        b = fp.ieee754_to_sp(xb)
        c = fp.ieee754_to_sp(xc)
        
        r = a*b+c
            
        return self.set_sp_result(r)
        
        
    def min_hp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')
        
        r = a if (a.compare(b) <= 0) else b
        
        if (a.nan and b.nan): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
        elif (a.nan): r = b
        elif (b.nan): r = a
        
        # @todo remove
        #print('min', a.to_float(), b.to_float(), '=', r.to_float())
        
        return self.hp_box(r.convert('hp'))
        
    def min_sp(self, xa, xb):
        r = 0
        fp = FloatingPointHelper()
        a = fp.ieee754_to_sp(xa)
        b = fp.ieee754_to_sp(xb)
        
        any_nan = (math.isnan(a) or math.isnan(b))
        all_nan = (math.isnan(a) and math.isnan(b))
        signaling = 0
        invalid = 0
        
        if (any_nan):
            signaling = self.is_sp_signaling_nan(xa, a)
            signaling |= self.is_sp_signaling_nan(xb, b)
            #print()
            #print('signaling a: ', self.is_dp_signaling_nan(xa, a), get_bit(xa,51), a)
            #print('signaling b: ', self.is_dp_signaling_nan(xb, b), get_bit(xb,51), b)
        
        if (all_nan):
            #print('all-nan')
            r = IEEE754_SP_SIGNALING_NAN # signaling Nan
            invalid = False
        elif (math.isnan(a)):
            r = fp.sp_to_ieee754(b)
            invalid = signaling
        elif (math.isnan(b)):
            r = fp.sp_to_ieee754(a)
            invalid = signaling
        else:
            r = fp.sp_to_ieee754(fp.min(a,b))
            invalid = (math.isinf(a) or math.isinf(b))
        
        
        print('invalid:', a, b, invalid)
            
        if (invalid):
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            
        return r
        
        
    def min_dp(self, xa, xb):
        r = 0
        fp = FloatingPointHelper()
        a = fp.ieee754_to_dp(xa)
        b = fp.ieee754_to_dp(xb)
        
        any_nan = (math.isnan(a) or math.isnan(b))
        all_nan = (math.isnan(a) and math.isnan(b))
        signaling = 0
        invalid = 0
        
        if (any_nan):
            signaling = self.is_dp_signaling_nan(xa, a)
            signaling |= self.is_dp_signaling_nan(xb, b)
            #print()
            #print('signaling a: ', self.is_dp_signaling_nan(xa, a), get_bit(xa,51), a)
            #print('signaling b: ', self.is_dp_signaling_nan(xb, b), get_bit(xb,51), b)
        
        if (all_nan):
            #print('all-nan')
            r = IEEE754_DP_SIGNALING_NAN # signaling Nan
            invalid = False
        elif (math.isnan(a)):
            r = fp.dp_to_ieee754(b)
            invalid = signaling
        elif (math.isnan(b)):
            r = fp.dp_to_ieee754(a)
            invalid = signaling
        else:
            r = fp.dp_to_ieee754(fp.min(a,b))
            invalid = (math.isinf(a) or math.isinf(b))
        
        
        print('invalid:', a, b, invalid)
            
        if (invalid):
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            
        return r
        
    def max_hp(self, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')
        
        r, nr = (a,b) if (a.compare(b) >= 0) else (b,a)
        
        if (a.nan and b.nan): pass
        elif (a.nan): r,nr = b,a
        elif (b.nan): r,nr = a,b
        
        if (nr.nan and (nr.m == IEEE754_HP_SNAN_MANTISA)): 
            # signaling nan
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
        
        # @todo remove
        #print('min', a.to_float(), b.to_float(), '=', r.to_float())
        
        return self.hp_box(r.convert('hp'))
    
    def max_sp(self, xa, xb):
        # @todo implement as max_hp
        r = 0
        fp = FloatingPointHelper()
        a = fp.ieee754_to_sp(xa)
        b = fp.ieee754_to_sp(xb)
        
        any_nan = (math.isnan(a) or math.isnan(b))
        all_nan = (math.isnan(a) and math.isnan(b))
        signaling = 0
        invalid = 0
        
        if (any_nan):
            signaling = self.is_sp_signaling_nan(xa, a)
            signaling |= self.is_sp_signaling_nan(xb, b)
            #print('signaling a: ', self.is_dp_signaling_nan(xa, a), get_bit(xa,51), a)
        
        if (all_nan):
            #print('all-nan')
            r = IEEE754_SP_CANONICAL_NAN # canonical Nan
            invalid = False
        elif (math.isnan(a)):
            r = fp.sp_to_ieee754(b)
            invalid = signaling
        elif (math.isnan(b)):
            r = fp.sp_to_ieee754(a)
            invalid = signaling
        else:
            r = fp.sp_to_ieee754(fp.max(a,b))
            invalid = (math.isinf(a) or math.isinf(b))
                
        #print('invalid:', a, b, invalid)
            
        if (invalid):
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            
        return r
                
    def max_dp(self, xa, xb):
        r = 0
        fp = FloatingPointHelper()
        a = fp.ieee754_to_dp(xa)
        b = fp.ieee754_to_dp(xb)
        
        any_nan = (math.isnan(a) or math.isnan(b))
        all_nan = (math.isnan(a) and math.isnan(b))
        signaling = 0
        invalid = 0
        
        if (any_nan):
            signaling = self.is_dp_signaling_nan(xa, a)
            signaling |= self.is_dp_signaling_nan(xb, b)
            #print('signaling a: ', self.is_dp_signaling_nan(xa, a), get_bit(xa,51), a)
        
        if (all_nan):
            #print('all-nan')
            r = IEEE754_DP_SIGNALING_NAN # signaling Nan
            invalid = False
        elif (math.isnan(a)):
            r = fp.dp_to_ieee754(b)
            invalid = signaling
        elif (math.isnan(b)):
            r = fp.dp_to_ieee754(a)
            invalid = signaling
        else:
            r = fp.dp_to_ieee754(fp.max(a,b))
            invalid = (math.isinf(a) or math.isinf(b))
                
        #print('invalid:', a, b, invalid)
            
        if (invalid):
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            
        return r

    def is_sp_signaling_nan(self, xv, v):
        return (math.isnan(v) and not(get_bit(xv, 22)))

    def is_dp_signaling_nan(self, xv, v):
        return (math.isnan(v) and not(get_bit(xv, 51)))

    def cmp_dp(self, op, xa, xb):
        self.cpu.csr[CSR_FFLAGS] = 0

        fp = FloatingPointHelper()
        a = fp.ieee754_to_dp(xa)
        b = fp.ieee754_to_dp(xb)
        
        any_nan = (math.isnan(a) or math.isnan(b))
        signaling = 0
        invalid = 0
        
        if (any_nan):
            signaling = self.is_dp_signaling_nan(xa, a)
            signaling |= self.is_dp_signaling_nan(xb, b)
            
        if (op == 'eq'):
            r = (a == b)
            
            if (any_nan):
                r = 0
            
            invalid = signaling
        elif (op == 'le'):
            r = (a <= b)
            invalid = any_nan
        elif (op == 'lt'):
            r = (a < b)
            invalid = any_nan
        else:
            raise Exception('unkwon op {}'.format(op))
            
        
        if (invalid):
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
            
        return r
        
    def cmp_sp(self, op, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        
        a = FPNum(self.sp_unbox(xa), 'sp')
        b = FPNum(self.sp_unbox(xb), 'sp')

        a.reducePrecision(IEEE754_SP_PRECISION)
        b.reducePrecision(IEEE754_SP_PRECISION)
        
        c = a.compare(b)

        if (op == 'eq'):
            r = (c == 0)
            if (a.nan or b.nan):
                if (a.nan and (a.m == IEEE754_SP_SNAN_MANTISA)): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
                if (b.nan and (b.m == IEEE754_SP_SNAN_MANTISA)): self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
                return 0
            
        elif (op == 'le'):
            r = (c == 0) or (c == -1)
            if (a.nan or b.nan):
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
                return 0
        elif (op == 'lt'):
            r = (c == -1)
            if (a.nan or b.nan):
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
                return 0
        else:
            raise Exception('unkwon op {}'.format(op))
    
        r = 1 if r else 0
            
        return r
        
    def cmp_hp(self, op, xa, xb):
        self.cpu.writeCSR(CSR_FFLAGS,  0)
        
        a = FPNum(self.hp_unbox(xa), 'hp')
        b = FPNum(self.hp_unbox(xb), 'hp')

        if (a.nan or b.nan):
            self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            return 0
        
        a.reducePrecision(IEEE754_HP_PRECISION)
        b.reducePrecision(IEEE754_HP_PRECISION)
        
        c = a.compare(b)

        if (op == 'eq'):
            r = (c == 0)
        elif (op == 'le'):
            r = (c == 0) or (c == -1)
        elif (op == 'lt'):
            r = (c == -1)
        else:
            raise Exception('unkwon op {}'.format(op))
    
        r = 1 if r else 0
            
        return r
    
    def convert_hp_to_sp(self, v):
        return self.sp_box(FPNum(v, 'hp').convert('sp'))
    
    def convert_hp_to_dp(self, v):
        return FPNum(v, 'hp').convert('dp')
    
    def convert_sp_to_hp(self, v):
        return self.hp_box(FPNum(v, 'sp').convert('hp'))
    
    def convert_sp_to_dp(self, v):
        return FPNum(v, 'sp').convert('dp')
    
    def convert_dp_to_hp(self, v):
        return self.hp_box(FPNum(v, 'dp').convert('hp'))

    def convert_dp_to_sp(self, v):
        return self.sp_box(FPNum(v, 'dp').convert('sp'))
    
    def convert_i32_to_hp(self, v):
        sv = IntegerHelper.c2_to_signed(v, 32)
        return self.hp_box(FPNum(sv).convert('hp'))

    def convert_u32_to_hp(self, v):
        return self.hp_box(FPNum(v & ((1<<32)-1)).convert('hp'))
    
    def convert_i64_to_hp(self, v):
        sv = IntegerHelper.c2_to_signed(v, 64)
        return self.hp_box(FPNum(sv).convert('hp'))

    def convert_u64_to_hp(self, v):
        return self.hp_box(FPNum(v & ((1<<64)-1)).convert('hp'))
    
    def convert_i64_to_dp(self, v):
        fp = FloatingPointHelper()
        return fp.dp_to_ieee754(signExtend(v, 64))


    def convert_dp_to_i64(self, v):
        fp = FloatingPointHelper()
        MIN_I64 = -(1<<63)
        MAX_I64 = (1<<63)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        dp = fp.ieee754_to_dp(v)
        
        if (math.isnan(dp)):
            iv = MAX_I64
        elif (math.isinf(dp)):
            if (dp < 0):
                iv = MIN_I64
            else:
                iv = MAX_I64
        else:
            iv = int(dp)
        
        if (iv < MIN_I64):
            ret = MIN_I64 & ((1<<64)-1) 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_I64):
            ret = MAX_I64
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            if (iv != dp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
        

    def convert_sp_to_i64(self, v):
        fp = FloatingPointHelper()
        MIN_I64 = -(1<<63)
        MAX_I64 = (1<<63)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        sp = fp.ieee754_to_sp(v)
        
        if (math.isnan(sp)):
            iv = MAX_I64
        elif (math.isinf(sp)):
            if (sp < 0):
                iv = MIN_I64
            else:
                iv = MAX_I64
        else:
            iv = int(sp)
        
        if (iv < MIN_I64):
            ret = MIN_I64 & ((1<<64)-1) 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_I64):
            ret = MAX_I64
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            if (iv != sp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
                
    def convert_dp_to_u64(self, v):
        fp = FloatingPointHelper()
        MIN_U64 = 0
        MAX_U64 = (1<<64)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        dp = fp.ieee754_to_dp(v)

        if (math.isnan(dp)):
            iv = MAX_U64
        elif (math.isinf(dp)):
            if (dp < 0):
                iv = MIN_U64
            else:
                iv = MAX_U64
        else:
            iv = int(dp)
        
        if (iv < MIN_U64):
            ret = MIN_U64 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_U64):
            ret = MAX_U64
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            #ret = signExtend(ret, 32) & ((1<<64)-1)
            
            if (iv != dp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
        
    def convert_sp_to_u64(self, v):
        fp = FloatingPointHelper()
        MIN_U64 = 0
        MAX_U64 = (1<<64)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        sp = fp.ieee754_to_sp(v)

        if (math.isnan(sp)):
            iv = MAX_U64
        elif (math.isinf(sp)):
            if (sp < 0):
                iv = MIN_U64
            else:
                iv = MAX_U64
        else:
            iv = int(sp)
        
        if (iv < MIN_U64):
            ret = MIN_U64 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_U64):
            ret = MAX_U64
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            #ret = signExtend(ret, 32) & ((1<<64)-1)
            
            if (iv != sp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret

    def convert_hp_to_i32(self, v):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(v, 'hp')
        
        MIN_I32 = -(1<<31)
        MAX_I32 = (1<<31)-1
        
        if (a.nan):
            r = MAX_I32
        elif (a.infinity):
            if (a.s == 1): r = MAX_I32
            elif (a.s == -1): r = MIN_I32
            else: raise Exception()
        else:
            iv = int(a.to_float())
            b = FPNum(iv)
            
            if (iv < MIN_I32):
                r = MIN_I32 
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            elif (iv > MAX_I32):
                r = MAX_I32
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            else:
                r = iv & ((1<<32) -1) 
            
            if (a.compare(b) != 0):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
                
        return signExtend(r, 32) & ((1<<64)-1)

    def convert_hp_to_u32(self, v):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(v, 'hp')
        
        MIN_U32 = 0
        MAX_U32 = (1<<32)-1
        
        if (a.nan):
            r = MAX_U32
        elif (a.infinity):
            if (a.s == 1): r = MAX_U32
            elif (a.s == -1): r = MIN_U32
            else: raise Exception()
        else:
            iv = int(a.to_float())
            b = FPNum(iv)
            
            if (iv < MIN_U32):
                r = MIN_U32 
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            elif (iv > MAX_U32):
                r = MAX_U32
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            else:
                r = iv & ((1<<32) -1) 
            
            if (a.compare(b) != 0):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
                
        return signExtend(r, 32) & ((1<<64)-1)
    
    def convert_hp_to_i64(self, v):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(v, 'hp')
        
        MIN_I64 = -(1<<63)
        MAX_I64 = (1<<63)-1
        
        if (a.nan):
            r = MAX_I64
        elif (a.infinity):
            if (a.s == 1): r = MAX_I64
            elif (a.s == -1): r = MIN_I64
            else: raise Exception()
        else:
            iv = int(a.to_float())
            b = FPNum(iv)
            
            if (iv < MIN_I64):
                r = MIN_I64 
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            elif (iv > MAX_I64):
                r = MAX_I64
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            else:
                r = iv & ((1<<64) -1) 
            
            if (a.compare(b) != 0):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
                
        return r & ((1<<64)-1)

    def convert_hp_to_u64(self, v):
        self.cpu.writeCSR(CSR_FFLAGS, 0)
        a = FPNum(v, 'hp')
        
        MIN_U64 = 0
        MAX_U64 = (1<<64)-1
        
        if (a.nan):
            r = MAX_U64
        elif (a.infinity):
            if (a.s == 1): r = MAX_U64
            elif (a.s == -1): r = MIN_U64
            else: raise Exception()
        else:
            iv = int(a.to_float())
            b = FPNum(iv)
            
            if (iv < MIN_U64):
                r = MIN_U64 
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            elif (iv > MAX_U64):
                r = MAX_U64
                self.cpu.setCSR(CSR_FFLAGS, CSR_FFLAGS_INVALID_OPERATION_MASK)
            else:
                r = iv & ((1<<64) -1) 
            
            if (a.compare(b) != 0):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
                
        return r & ((1<<64)-1)
    
    def convert_dp_to_i32(self, v):
        fp = FloatingPointHelper()
        MIN_I32 = -(1<<31)
        MAX_I32 = (1<<31)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        dp = fp.ieee754_to_dp(v)
        
        if (math.isnan(dp)):
            iv = MAX_I32
        elif (math.isinf(dp)):
            if (dp < 0):
                iv = MIN_I32
            else:
                iv = MAX_I32
        else:
            iv = int(dp)
        
        if (iv < MIN_I32):
            ret = MIN_I32 & ((1<<64)-1) 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_I32):
            ret = MAX_I32
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            if (iv != dp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
    
    def convert_dp_to_u32(self, v):
        fp = FloatingPointHelper()
        MIN_U32 = 0
        MAX_U32 = (1<<32)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        dp = fp.ieee754_to_dp(v)
        if (math.isnan(dp)):
            iv = MAX_U32
        elif (math.isinf(dp)):
            if (dp < 0):
                iv = MIN_U32
            else:
                iv = MAX_U32
        else:
            iv = int(dp)
        
        if (iv < MIN_U32):
            ret = MIN_U32 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_U32):
            ret = MAX_U32
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            ret = signExtend(ret, 32) & ((1<<64)-1)
            
            if (iv != dp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
        
    def convert_sp_to_i32(self, v):
        fp = FloatingPointHelper()
        MIN_I32 = -(1<<31)
        MAX_I32 = (1<<31)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        sp = fp.ieee754_to_sp(v)
        
        if (math.isnan(sp)):
            iv = MAX_I32
        elif (math.isinf(sp)):
            if (sp < 0):
                iv = MIN_I32
            else:
                iv = MAX_I32
        else:
            iv = int(sp)
        
        if (iv < MIN_I32):
            ret = MIN_I32 & ((1<<64)-1) 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_I32):
            ret = MAX_I32
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            if (iv != sp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
        
    def convert_sp_to_u32(self, v):
        fp = FloatingPointHelper()
        MIN_U32 = 0
        MAX_U32 = (1<<32)-1
        
        self.cpu.csr[CSR_FFLAGS] = 0
        sp = fp.ieee754_to_sp(v)
        if (math.isnan(sp)):
            iv = MAX_U32
        elif (math.isinf(sp)):
            if (sp < 0):
                iv = MIN_U32
            else:
                iv = MAX_U32
        else:
            iv = int(sp)
        
        if (iv < MIN_U32):
            ret = MIN_U32 
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (iv > MAX_U32):
            ret = MAX_U32
            self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            ret = iv & ((1<<64) -1) 
            
            ret = signExtend(ret, 32) & ((1<<64)-1)
            
            if (iv != sp):
                self.cpu.csr[CSR_FFLAGS] = CSR_FFLAGS_INEXACT_MASK
        return ret
