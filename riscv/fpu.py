import sys
import py4hw
import numpy as np
        
    
from .temp_helper import *
from .csr import *


def fclass_32(v):
    r = 0
    if (v == -math.inf):
        r |= 1 << 0
    if (v < 0):
        if (abs(v) >= np.finfo(np.float32).smallest_normal):
            r |= 1 << 1
        else:
            r |= 1 << 2
    if (v == -0):
        r |= 1 << 3
    if (v == 0):
        r |= 1 << 4
    if (v > 0):
        if (abs(v) >= np.finfo(np.float32).smallest_normal):
            r |= 1 << 5
        else:
            r |= 1 << 6
    if (v == math.inf):
        r |= 1 << 7
    # signaling nan r |= 1 << 8
    if (v == math.nan):
        r |= 1 << 9
    return r


    
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
            
    def sp_box(self, x):
        # generates Nan boxed dp from sp
        mask = ((1<<32)-1)
        return (mask << 32) | x

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
        
        sign_a = ((xa>>31) & 1) or ((xa >> 32) == ((1<<32)-1))
        sign_b = ((xb>>31) & 1) or ((xb >> 32) == ((1<<32)-1))
        sign_r = sign_b
        
        if (b == 0):
            sign_r = f2_high_1
        
        if (f1_valid and f2_valid):
            # valid single precision       
            return (xa & (((1<<32)-1)<<32)) | (xa & ((1<<31)-1)) | (sign_r<<31) 
        else:
            if (not(f1_valid) and f2_high_1):
                return ((1<<32)-1)<<32 | (1<<31) | IEEE754_SP_CANONICAL_NAN
            elif (not(f2_valid) and (b==0)):
                return xa
            else:
                return ((1<<32)-1)<<32 | IEEE754_SP_CANONICAL_NAN

    def fsub_dp(self, xa, xb):
        fp = FloatingPointHelper()
        return self.fma_dp(fp.dp_to_ieee754(1.0), xa , FloatingPointHelper.ieee754_dp_neg(xb))  
    
    def fms_dp(self, xa, xb, xc):
        return self.fma_dp(xa , xb, FloatingPointHelper.ieee754_dp_neg(xc))
    
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
    
    def fsub_sp(self, xa, xb):
        return self.fma_sp(fp.sp_to_ieee754(1.0), self.freg[rs1] , FloatingPointHelper.ieee754_sp_neg(self.freg[rs2]))

    def fma_sp(self, xa, xb, xc):
        # fused multiply-add r = a*b +c
        # update floating point flags
        from decimal import Decimal
        
        fp = FloatingPointHelper()
        a = fp.ieee754_to_sp(xa)
        b = fp.ieee754_to_sp(xb)
        c = fp.ieee754_to_sp(xc)
        
        self.cpu.csr[CSR_FFLAGS] = 0
        r = a*b+c
            
        if (math.isnan(r)):
            xr = 0x7F800000 # signaling Nan
            self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
        elif (math.isinf(a) and math.isinf(b)):
            if (math.copysign(1, a) == math.copysign(1, b)):
                r = a           
                xr = fp.sp_to_ieee754(r)
            else:
                print('Invalid inf')
                xr = 0x7F800000 # signaling Nan
                self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INVALID_OPERATION_MASK
        else:
            rd = Decimal(a)*Decimal(b)+Decimal(c)
        
            if (rd != r):
                self.cpu.csr[CSR_FFLAGS] |= CSR_FFLAGS_INEXACT_MASK
            
            xr = fp.sp_to_ieee754(r)
            
        return self.sp_box(xr)
        
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
        
        
    def max_sp(self, xa, xb):
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
        self.cpu.csr[CSR_FFLAGS] = 0

        fp = FloatingPointHelper()
        a = fp.ieee754_to_sp(self.sp_unbox(xa))
        b = fp.ieee754_to_sp(self.sp_unbox(xb))
        
        any_nan = (math.isnan(a) or math.isnan(b))
        signaling = 0
        invalid = 0
        
        if (any_nan):
            signaling = self.is_sp_signaling_nan(xa, a)
            signaling |= self.is_sp_signaling_nan(xb, b)
            
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
