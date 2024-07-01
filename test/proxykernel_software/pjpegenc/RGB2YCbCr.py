# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 08:21:52 2024

@author: dcastel1
"""
import py4hw
from py4hw.helper import FixedPoint
from py4hw.helper import FPNum

class RGB2YCrCr_CustomInstruction(py4hw.Logic):
    def __init__(self, parent, name, port):
        super().__init__(parent, name)
        
        self.addInterfaceSink('', port)
        
        hlp = py4hw.LogicHelper(self)
        
        py4hw.Reg(self, 'done', port.start, port.done)
        
        y = self.wire('y', 32)
        cb = self.wire('cb', 32)
        cr = self.wire('cr', 32)
        
        rgb = hlp.hw_range(port.rs1, 31, 0)
        
        # RGB2YCbCr(self, 'rgb2yuv', rgb, y, cb, cr)
        RGB2YCbCrFunctional(self, 'rgb2yuv', rgb, y, cb, cr)
        
        rd_low = self.wire('rd_low', 32)
        py4hw.Mux(self, 'mux', hlp.hw_range(port.func7, 1, 0), [y,cb,cr, cr], rd_low)

        ones = hlp.hw_constant(32, -1)    
        py4hw.ConcatenateMSBF(self, 'rd', [ones, rd_low], port.rd)
        
class RGB2YCbCr(py4hw.Logic):
    
    def __init__(self, parent, name, rgb, y, cb, cr):
        super().__init__(parent, name)
        
        self.addIn('rgb', rgb)
        self.addOut('y', y)
        self.addOut('cb', cb)
        self.addOut('cr', cr)
        
        # unpack rgb
        r = self.wire('r', 8)
        g = self.wire('g', 8)
        b = self.wire('b', 8)
        
        py4hw.Range(self, 'r', rgb, 23, 16, r)
        py4hw.Range(self, 'g', rgb, 15, 8, g)
        py4hw.Range(self, 'b', rgb, 7, 0, b)
        
        # y = 0.299 * r + 0.587 * g + 0.114 * b
        yr = self.ConstantMult('yr', r, 0.299)
        yg = self.ConstantMult('yg', g, 0.587)
        yb = self.ConstantMult('yb', b, 0.114)

        ysum = self.Sum('ysum', [yr, yg, yb])
        
        py4hw.FixedPointtoFP_SP(self, 'y', ysum, (1,8,15), y, None)

        bias = self.Constant('bias', 128)
        
        # cb = 128 + ((-0.168736 * r - 0.331264 * g + 0.5 * b))
        cbr = self.ConstantMult('cbr', r, -0.168736)
        cbg = self.ConstantMult('cbg', g, -0.331264)
        cbb = self.ConstantMult('cbb', b, 0.5)
        
        cbsum = self.Sum('cbsum', [bias, cbr, cbg, cbb])
        
        py4hw.FixedPointtoFP_SP(self, 'cb', cbsum, (1,8,15), cb, None)
        
        # cr = 128 + ((0.5 * r - 0.41869 * g - 0.08131 * b))
        crr = self.ConstantMult('crr', r, 0.5)
        crg = self.ConstantMult('crg', g, -0.41869)  
        crb = self.ConstantMult('crb', b, -0.08131)
        
        crsum = self.Sum('crsum', [bias, crr, crg, crb])
        
        py4hw.FixedPointtoFP_SP(self, 'cr', crsum, (1,8,15), cr, None)

    def Constant(self, name, v):
        kv = FixedPoint(1, 8, 15, v)
        return kv.createConstant(self, name)
        
    def ConstantMult(self, name, v, k):
        kv = FixedPoint(1, 1, 22, k)
        mf = (1, 8, 15)        
        m = self.wire(name, sum(mf))
        py4hw.FixedPointMult(self, name, v, (0,8,0), kv.createConstant(self, 'k'+name), kv.getWidths(), m, mf)

        return m
    
    def Sum(self, name, v):
        
        a = v[0]
        f = (1,8,15)
        
        for i in range(1, len(v)):
            b = v[i]
            r = self.wire(name+f'{i}', sum(f))
            py4hw.FixedPointAdd(self, name+f'{i}', a, f, b, f, r, f)
            a = r
            
        return a
    
class RGB2YCbCrFunctional(py4hw.Logic):
    
    def __init__(self, parent, name, rgb, y, cb, cr):
        super().__init__(parent, name)
        
        self.rgb = self.addIn('rgb', rgb)
        self.y = self.addOut('y', y)
        self.cb = self.addOut('cb', cb)
        self.cr = self.addOut('cr', cr)

    def propagate(self):
        rgb = self.rgb.get()
        r = (rgb >> 16) & 0xFF
        g = (rgb >> 8) & 0xFF
        b = rgb & 0xFF
        
        y = 0.299 * r + 0.587 * g + 0.114 * b
        cb = 128 + ((-0.168736 * r - 0.331264 * g + 0.5 * b))
        cr = 128 + ((0.5 * r - 0.41869 * g - 0.08131 * b))
        
        self.y.put(FPNum(y).convert('sp'))
        self.cb.put(FPNum(cb).convert('sp'))
        self.cr.put(FPNum(cr).convert('sp'))
        
if __name__ == "__main__":
    
    hw = py4hw.HWSystem()
    
    rgb = hw.wire('rgb', 32)
    y = hw.wire('y', 32)
    cb = hw.wire('cb', 32)
    cr = hw.wire('cr', 32)
    yf = hw.wire('yf', 32)
    cbf = hw.wire('cbf', 32)
    crf = hw.wire('crf', 32)
    
    py4hw.Sequence(hw, 'rgb', [0x000000, 0xFF0000, 0x00FF00, 0x0000FF], rgb)

    rgb2yuv = RGB2YCbCr(hw, 'rgb2yuv', rgb, y, cb, cr)
    rgb2yuv_f = RGB2YCbCrFunctional(hw, 'golden_model', rgb, yf, cbf, crf)
    
    py4hw.gui.Workbench(hw)