# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 20:41:52 2024

@author: dcastel1
"""

import py4hw

class CustomInstructionInterface(py4hw.Interface):
    
    def __init__(self, parent:py4hw.Logic, name:str, w:int):
        super().__init__(parent, name);
        self.start = self.addSourceToSink("start", 1)
        self.done = self.addSinkToSource("done", 1)
        
        self.rs1 = self.addSourceToSink("rs1", w) 
        self.rs2 = self.addSourceToSink("rs2", w)
        self.rd = self.addSinkToSource("rd", w)
