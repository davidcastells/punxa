# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 20:41:52 2024

@author: dcr
"""

import math
from py4hw.helper import *

IEEE754_HP_CANONICAL_NAN=0x7E00
IEEE754_SP_CANONICAL_NAN=0x7FC00000
IEEE754_DP_CANONICAL_NAN=0x7FFC000000000000

IEEE754_SP_SIGNALING_NAN=0x7F800000
IEEE754_DP_SIGNALING_NAN=0x7FF8000000000000


# @todo should be part of py4hw
def get_bit(v, bit):
    return ((v>>bit) & 0x1)

# @todo should be part of py4hw
def get_bits(v, start, bits):
    return (v >> start) & ((1 << bits)-1)

# @todo should be part of py4hw
def sign(v):
    if (v >= 0):
        return 1
    else:
        return -1

# @todo should be part of py4hw
def signExtend_toremove(v, w):
    v = v & ((1<<w)-1)
    sign_bit = w - 1

    if (get_bit(v, sign_bit) == 0x1):
        v = - ((1<<w) - v)

    return v

# @todo should be part of py4hw
def zeroExtend(v, w):
    return v & ((1<<w) - 1)

def compose(v, parts):
    ret = 0
    bits = 0
    total_bits = 0
    
    for p in parts:        
        start = p[0]
        bits = p[1]
        
        ret = ret << bits
        
        ret |= (v >> start) & ((1 << bits)-1)
        
        total_bits += bits
    
    return ret

def compose_sign(v, parts):
    ret = 0
    bits = 0
    total_bits = 0
    
    for p in parts:        
        start = p[0]
        bits = p[1]
        
        ret = ret << bits
        
        ret |= (v >> start) & ((1 << bits)-1)
        
        total_bits += bits

    # @todo remove the assert
    assert(IntegerHelper.c2_to_signed(ret, total_bits) == signExtend_toremove(ret, total_bits))
    return IntegerHelper.c2_to_signed(ret, total_bits)
    
# We will remove this class with the next release of py4hw
class FloatingPointHelper:

    @staticmethod
    def min(a, b):
        if (a == 0.0 and b == 0.0):
            sa = math.copysign(1, a)
            sb = math.copysign(1, b)
            
            if (sa < sb):
                return a
            else:
                return b
        return min(a, b)

    @staticmethod
    def max(a, b):
        if (a == 0.0 and b == 0.0):
            sa = math.copysign(1, a)
            sb = math.copysign(1, b)
            
            if (sa > sb):
                return a
            else:
                return b
        return max(a, b)
        
        
    def ieee754_dp_neg(v):
        s = (v >> 63) & 1
        ns = int(not(s))
        return ns << 63 | (v & ((1<<63)-1)) 
        
    @staticmethod
    def fp_to_parts(v):
        if (math.isinf(v) or math.isnan(v)):
            raise Exception('invalid value {}'.format(v))
        e = 0
        s=0
        m = v
        if (m < 0):
            # if v is negative activate the sign, and change the value
            s = 1
            m = -m
    
        if (m > 0.0):
            while (m >= 2):
                # iterate until v is < 2 to determine the exponent
                m = m / 2
                e += 1
                #print('e:', e, 'v:', v)
            while (m < 1):
                m = m * 2
                e -= 1
                #print('e:', e, 'v:', v)
            
        return s, e, m

    @staticmethod
    def sp_to_fixed_point_parts(v):
        s,e,m = FloatingPointHelper.fp_to_parts(v)

        if (m == 0):
            return 0,0,0
        else:
            re = e
            rm = int(round(m * (1<<23)))

            return s, re, rm
    
    @staticmethod
    def half_to_ieee754_parts(v):
        '''
        Return the parts of the IEEE 754 representation of a half-precision floating-point number v

        Parameters
        ----------
        v : TYPE
        A half-precision floating-point number

        Returns
        -------
        tuple
        A tuple containing:
          - sign: 0 for positive, 1 for negative
          - biased_exponent: biased representation of exponent (e+15)
          - significand: representation of mantissa (m-1) << 10
        '''

        if (math.isinf(v)):
            s = 0 if v > 0 else 1
            e = 31
            m = 0
            return s, e, m

        if (math.isnan(v)):
            s = 0
            e = 31
            m = (1 << 10) - 1
            return s, e, m

        s,e,m = FloatingPointHelper.fp_to_parts(v)
        
        if (m == 0):
            v = math.copysign(1, v)
            s = 0 if v > 0 else 1
            return s,0,0
        else:
            if (e >= 16):
                return s,31,0  # infinity
                
            if (e <= -15):
                # denormalized values
                div = math.pow(2, (-15-e))
                #print('e',e,'div', div)
                m = m / div
                re = 0
                rm = int(round(m * (1 << 9)))
            else:
                im = int(round((m-1) * (1<<10)))
                if (im >= (1<<10)):
                    e += 1
                    m /= 2
                    
                re = 127 + e
                rm = int(round((m-1) * (1<<10)))
    
            return s, re, rm


    @staticmethod
    def sp_to_ieee754_parts(v):
        """
        Return the parts of the IEEE 754 representation of v

        Parameters
        ----------
        v : TYPE
            DESCRIPTION.

        Returns
        -------
        int
            sign.
        int
            biased representation of exponent (e+127)
        int
            representation of mantissa int((m-1)<<23) 

        """
        if (math.isinf(v)):
            s = 0 if v > 0 else 1
            e = 255
            m = 0
            return s,e,m
        
        if (math.isnan(v)):
            s = 0 
            e = 255
            m = (1<<23)-1
            return s,e,m
        
        s,e,m = FloatingPointHelper.fp_to_parts(v)

        if (m == 0):
            v = math.copysign(1, v)
            s = 0 if v > 0 else 1
            return s,0,0
        else:
            if (e >= 128):
                return s,255,0  # infinity
                
            if (e <= -127):
                # denormalized values
                div = math.pow(2, (-127-e))
                #print('e',e,'div', div)
                m = m / div
                re = 0
                rm = int(round(m * (1 << 22)))
            else:
                im = int(round((m-1) * (1<<23)))
                if (im >= (1<<23)):
                    e += 1
                    m /= 2
                    
                re = 127 + e
                rm = int(round((m-1) * (1<<23)))
    
            return s, re, rm

    def dp_to_ieee754_parts(v):
        """
        Return the parts of the IEEE 754 representation of v

        Parameters
        ----------
        v : TYPE
            DESCRIPTION.

        Returns
        -------
        int
            sign.
        int
            biased representation of exponent (e+1023)
        int
            representation of mantissa int((m-1)<<52) 

        """
        if (math.isinf(v)):
            s = 0 if v > 0 else 1
            e = 2047
            m = 0
            return s,e,m

        if (math.isnan(v)):
            s = 0 
            e = 2047
            m = (1<<51)-1
            return s,e,m

            
        s,e,m = FloatingPointHelper.fp_to_parts(v)

        if (m == 0):
            v = math.copysign(1, v)
            s = 0 if v > 0 else 1
            return s,0,0
        else:
            if (e >= 1024):
                return s,2047,0  # infinity
                
            if (e <= -1023):
                # denormalized values
                div = math.pow(2, (-1023-e))
                #print('e',e,'div', div)
                m = m / div
                re = 0
                rm = int(round(m * (1 << 51)))
            else:
                im = int(round((m-1) * (1<<52)))
                if (im >= (1<<52)):
                    e += 1
                    m /= 2
                    
                re = 1023 + e
                rm = int(round((m-1) * (1<<52)))
    
            return s, re, rm

    @staticmethod
    def ieee754_sp_split(v):
        s = (v >> 31) & 1
        e = (v >> 23) & 0xF
        m = (v & ((1<<23)-1))
        return s,e,m

    @staticmethod
    def sp_to_ieee754(v):
        s,e,m = FloatingPointHelper.sp_to_ieee754_parts(v)
        
        r = s << 31
        r = r | (e << 23)
        r = r | (m)
        return r
        
    @staticmethod
    def half_to_ieee754(v):
        s,e,m = FloatingPointHelper.half_to_ieee754_parts(v)
        
        r = s << 15
        r = r | (e << 10)
        r = r | (m)
        return r

    @staticmethod
    def ieee754_dp_split(v):
        s = (v >> 64) & 1
        e = (v >> 52) & 0x7FF
        m = (v & ((1<<52)-1))
        return s,e,m
    
    @staticmethod
    def dp_to_ieee754(v):
        s,e,m = FloatingPointHelper.dp_to_ieee754_parts(v)
        
        r = s << 63
        r = r | (e << 52)
        r = r | (m)
        return r

    @staticmethod
    def parts_to_fp(s, e, m):
        return math.pow(-1, s) * math.pow(2, e) * m

    @staticmethod
    def ieee754_parts_to_sp(s, e, m):
        """
        We build a floating point number from is sign/exponent/mantisa representation
        as it is store in the IEEE754 format

        Parameters
        ----------
        s : int
            sign.
        e : int
            exponent.
        m : TYPE
            mantisa.

        Returns
        -------
        float
            floating point number r = (-1)^s * 2^e * m

        """
        
        # zero is a special case
        if (e == 0 and m == 0):
            if (s == 1):
                return -0.0
            else:
                return 0.0
            
        if (e == 0):
            ef = -126
            mf = m / (1<<23)
        else:
            ef = e-127
            mf = ((1 << 23) | m) / (1<<23)
        
        return FloatingPointHelper.parts_to_fp(s , ef , mf)
    
    @staticmethod
    def ieee754_parts_to_dp(s, e, m):
        """
        We build a floating point number from is sign/exponent/mantisa representation
        as it is store in the IEEE754 format

        Parameters
        ----------
        s : int
            sign.
        e : int
            exponent.
        m : TYPE
            mantisa.

        Returns
        -------
        float
            floating point number r = (-1)^s * 2^e * m

        """
        
        # zero is a special case
        if (e == 0 and m == 0):
            if (s == 1):
                return -0.0
            else:
                return 0.0
            
        if (e == 0):
            ef = -1022
            mf = m / (1<<52)
        else:
            ef = e-1023
            mf = ((1 << 52) | m) / (1<<52)
        
        return FloatingPointHelper.parts_to_fp(s , ef , mf)
    
    @staticmethod
    def ieee754_to_sp(v):
        if (v == 0):
            return 0.0
        
        s = (v >> 31) & 1
        e = (v >> 23) & 0xFF
        m = (v & ((1<<23)-1))  
        
        if (e == 255):
            if (m == 0):
                return -math.inf if (s == 1) else math.inf
            else:
                return math.nan
        
        return FloatingPointHelper.ieee754_parts_to_sp(s, e, m)

    @staticmethod
    def ieee754_to_dp(v):
        if (v == 0):
            return 0.0
        
        s = (v >> 63) & 1
        e = (v >> 52) & 0x7FF
        m = (v & ((1<<52)-1))  
        
        if (e == 0x7FF):
            if (m == 0):
                return -math.inf if (s == 1) else math.inf 
            else:
                return math.nan

        return FloatingPointHelper.ieee754_parts_to_dp(s, e, m)

    @staticmethod
    def ieee754_stored_internally(v):
        s,e,m = FloatingPointHelper.sp_to_ieee754_parts(v)
        iv = FloatingPointHelper.ieee754_parts_to_sp(s, e, m)
        return iv

    @staticmethod
    def zp_bin(v:int, vl:int) -> str:
        """        
        Generates a the binary representation of an integer value in a number
        of bits. Leading zeros are added as needed.
        
        Parameters
        ----------
        v : int
            value.
        vl : int
            length of the output.

        Returns
        -------
        TYPE
            the binary string.

        """
        if (v >= 0):
            str = bin(v)[2:]
        else:
            # bin function does not handle 2's complement,
            # so let's do it for them
            p = -v
            mask = (1 << vl) -1
            r = (mask - p + 1) & mask
            str = bin(r)[2:] 
            
        return ('0' * (vl-len(str))) + str

