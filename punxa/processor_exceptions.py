# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 20:41:52 2024

@author: dcr
"""

class ProcessorInterrupt(Exception):
    msg = ''
    tval = 0
    
class ProcessorException(Exception):
    msg = ''
    tval = 0

class UserSoftwareInterrupt(ProcessorInterrupt):
    code = 0

class SupervisorSoftwareInterrupt(ProcessorInterrupt):
    code = 1

class MachineSoftwareInterrupt(ProcessorInterrupt):
    code = 3

class UserTimerInterrupt(ProcessorInterrupt):
    code = 4

class SupervisorTimerInterrupt(ProcessorInterrupt):
    code = 5

class MachineTimerInterrupt(ProcessorInterrupt):
    code = 7

class UserExternalInterrupt(ProcessorInterrupt):
    code = 8

class SupervisorExternalInterrupt(ProcessorInterrupt):
    code = 9

class MachineExternalInterrupt(ProcessorInterrupt):
    code = 11


class InstructionAddressMisaligned(ProcessorException):
    code = 0

class InstructionAccessFault(ProcessorException):
    code = 1
    
    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval

class IllegalInstruction(ProcessorException):
    code = 2
    
    def __init__(self, msg, tval):
        self.msg = msg
        self.tval = tval

class Breakpoint(ProcessorException):
    code = 3

    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval
        
class LoadAddressMisaligned(ProcessorException):
    code = 4
    
    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval
    

class LoadAccessFault(ProcessorException):
    code = 5

class StoreAMOAddressMisaligned(ProcessorException):
    code = 6

    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval


class StoreAMOAccessFault(ProcessorException):
    code = 7

class EnvCallUMode(ProcessorException):
    code = 8

    def __init__(self, syscall):
        self.msg = f'syscall: 0x{syscall:X}'

class EnvCallSMode(ProcessorException):
    code = 9

    def __init__(self, syscall):
        self.msg = f'syscall: 0x{syscall:X}'

class EnvCallMMode(ProcessorException):
    code = 11

    def __init__(self, syscall):
        self.msg = f'syscall: 0x{syscall:X}'

class InstructionPageFault(ProcessorException):
    code = 12

    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval

class LoadPageFault(ProcessorException):
    code = 13
    
    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval

class StoreAMOPageFault(ProcessorException):
    code = 15

    def __init__(self, msg='', tval=0):
        self.msg = msg
        self.tval = tval
    
# Internal exceptions
    
class TLBMiss(Exception):
    pass
