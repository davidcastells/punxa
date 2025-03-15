# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 12:57:18 2022

@author: dcr
"""

import py4hw
from py4hw.logic import *
from py4hw.logic.storage import *
from py4hw.simulation import Simulator
import py4hw.debug


class Uart8250(Logic):
    # Info from here
    # https://github.com/riscv-software-src/opensbi/blob/b9edf49b67a1b5e47b1c35dcd7c75efccaf22ea3/lib/utils/serial/uart8250.c
    
    UART_RBR_OFFSET	= 0	# In:  Recieve Buffer Register 
    UART_THR_OFFSET = 0	# Out: Transmitter Holding Register */
    UART_DLL_OFFSET	= 0	# Out: Divisor Latch Low */
    UART_IER_OFFSET = 1	# I/O: Interrupt Enable Register */
    UART_DLM_OFFSET	= 1	# Out: Divisor Latch High */
    UART_FCR_OFFSET	= 2	# Out: FIFO Control Register */
    UART_IIR_OFFSET	= 2	# I/O: Interrupt Identification Register */
    UART_LCR_OFFSET	= 3	# Out: Line Control Register */
    UART_MCR_OFFSET	= 4	# Out: Modem Control Register */
    UART_LSR_OFFSET	= 5	# In:  Line Status Register */
    UART_MSR_OFFSET	= 6	# In:  Modem Status Register */
    UART_SCR_OFFSET	= 7	# I/O: Scratch Register */
    UART_MDR1_OFFSET	 = 8 # I/O:  Mode Register */
    
    #define UART_LSR_FIFOE		0x80	/* Fifo error */
    UART_LSR_TEMT =	0x40	# Transmitter empty 
    UART_LSR_THRE = 0x20    # Transmit-hold-register empty 
    #define UART_LSR_BI		0x10	/* Break interrupt indicator */
    #define UART_LSR_FE		0x08	/* Frame error indicator */
    #define UART_LSR_PE		0x04	/* Parity error indicator */
    #define UART_LSR_OE		0x02	/* Overrun error indicator */
    #define UART_LSR_DR		0x01	/* Receiver data ready */
    #define UART_LSR_BRK_ERROR_BITS	0x1E	/* BI, FE, PE, OE bits */

    
    def __init__(self, parent:Logic, name:str, port, reg_size=1):
        super().__init__(parent, name)
        
        self.port = self.addInterfaceSink('port', port)
        self.console = ['']        
        self.verbose = False
        self.reg_size = reg_size

    def addConsoleChar(self, c):
        if (c == '\n'):
            clen = len(self.console)
            if (clen > 80):
                self.console = self.console[1:] # remove one line
            self.console.append('')
        else:
            clen = len(self.console)
            self.console[clen-1] += c
            
    def readReg(self, reg):
        if (reg == self.UART_LSR_OFFSET):
            return self.UART_LSR_THRE | self.UART_LSR_TEMT # report tx empty
        else:
            return 0
        
    def writeReg(self, reg, v):
        if (reg == self.UART_THR_OFFSET):
            #print('Consolse Out: ', chr(v))
            self.addConsoleChar(chr(v))
        else:
            pass
        
    def clock(self):
        read = self.port.read.get()
        write = self.port.write.get()
        write_data = self.port.write_data.get()
        addr = self.port.address.get()
        be = self.port.be.get()
        
        if (read == 1 or write == 1):
            if (read == 1):
                reg_addr = addr
                idx = 0
                v = 0
                if (self.reg_size == 4):
                    v = self.readReg(addr // 4)
                elif (self.reg_size == 1):
                    while (be > 0):
                        if ((be & 1) == 1):
                            #print('READ UART REG {}'.format(reg_addr))
                            v |= self.readReg(reg_addr) << (8*idx)  
                        be = be >> 1
                        reg_addr += 1
                        idx += 1
                else:
                    raise Exception()
                
                self.port.read_data.prepare(v)
                if (self.verbose): print('READ UART addr:{:04X} be:{:0X} = {:04X}'.format(addr, be, v)) 
                
            if (write == 1):
                if (self.verbose): print('WRITE UART addr:{:04X} be:{} = {:04X}'.format(addr, be, write_data)) 
                reg_addr = addr
                idx = 0
                v = write_data
                if (self.reg_size == 4):
                    self.writeReg(addr // 4, v)
                elif (self.reg_size == 1):
                    while (be > 0):
                        if ((be & 1) == 1):
                            #print('WRITE UART REG {}'.format(reg_addr))
                            self.writeReg(reg_addr, (v >> (8*idx)) & 0xFF)  
                        be = be >> 1
                        reg_addr += 1
                        idx += 1
                else:
                    raise Exception()
                
                self.port.read_data.prepare(0)

