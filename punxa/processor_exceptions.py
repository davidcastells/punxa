# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 20:41:52 2024

@author: dcr
"""


class ProcessorException(Exception):
    msg = ''
    tval = 0

class UserSoftwareInterrupt(ProcessorException):
    code = 0

class SupervisorSoftwareInterrupt(ProcessorException):
    code = 1

class MachineSoftwareInterrupt(ProcessorException):
    code = 3

class UserTimerInterrupt(ProcessorException):
    code = 4

class SupervisorTimerInterrupt(ProcessorException):
    code = 5

class MachineTimerInterrupt(ProcessorException):
    code = 7

class UserExternalInterrupt(ProcessorException):
    code = 8

class SupervisorExternalInterrupt(ProcessorException):
    code = 9

class MachineExternalInterrupt(ProcessorException):
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

class LoadAddressMisaligned(ProcessorException):
    code = 4

class LoadAccessFault(ProcessorException):
    code = 5

class StoreAMOAddressMisaligned(ProcessorException):
    code = 6

class StoreAMOAccessFault(ProcessorException):
    code = 7

class EnvCallUMode(ProcessorException):
    code = 8

class EnvCallSMode(ProcessorException):
    code = 9

class EnvCallMMode(ProcessorException):
    code = 11

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
