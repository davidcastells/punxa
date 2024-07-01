# -*- coding: utf-8 -*-

import py4hw
from py4hw.logic import *
from py4hw.logic.storage import *
from py4hw.simulation import Simulator
import py4hw.debug
import mmap

class MemoryInterface(Interface):
    
    def __init__(self, parent:Logic, name:str, data_width:int, address_width:int):
        super().__init__(parent, name);
        self.read = self.addSourceToSink("read", 1)
        self.read_data = self.addSinkToSource("readdata", data_width)
        self.address = self.addSourceToSink("address", address_width) 
        self.write = self.addSourceToSink("write", 1)
        self.write_data = self.addSourceToSink("writedata", data_width)
        if ((data_width % 8) != 0):
            raise Exception('data_width must be multiple of byte, {} not supported'.format(data_width))
        self.be = self.addSourceToSink('be', data_width // 8)
        self.resp = self.addSinkToSource('resp', 1) # by now response is just 0 = OK 1 = ERROR

class Memory(Logic):
    def __init__(self, parent:Logic, name:str, data_width:int, address_width:int, port:MemoryInterface, endianness='little'):
        super().__init__(parent, name)
        
        self.port = self.addInterfaceSink('port', port)        

        #self.values = [0] * numRegs
        self.verbose = False
        self.values = bytearray((1 << address_width) * (data_width // 8))
        self.little_endian = (endianness == 'little')
        
        if (self.little_endian == False):
            raise Exception('big endian not supported yet')

    def write(self, address:int, value:int, be:int):
        #self.values[address//4] = value
        raise Exception('not implemented')
        
    def read(self, address:int) -> int:
        #return self.values[address//4]
        raise Exception('not implemented')
        
    def clock(self):
        data_width = self.port.read_data.getWidth()
        
        address = self.port.address.get()
        be = self.port.be.get()
        self.port.resp.prepare(0)
        
        if (self.port.read.get()):

            value = 0
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            for i in range(data_width // 8):                
                value = value | (self.values[address + i] << (i*8))
                
            self.port.read_data.prepare(value)
            if (self.verbose): print('reading address ', hex(address), '=', hex(value))

        elif (self.port.write.get()):

            value = self.port.write_data.get()

            if (self.verbose): print('writing address ', hex(address), '=', hex(value))
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            
            for i in range(data_width // 8):           
                if ((be & 0x1) != 0):
                    self.values[address + i] = value & 0xFF
                be = be >> 1
                value = value >> 8



class SparseMemory(Logic):
    def __init__(self, parent:Logic, name:str, data_width:int, address_width:int, port:MemoryInterface, endianness='little', mem_base=0):
        super().__init__(parent, name)
        
        self.port = self.addInterfaceSink('port', port)        

        #self.values = [0] * numRegs
        self.verbose = False
        self.maxSize = (1 << address_width) * (data_width // 8)
        #self.values = bytearray((1 << address_width) * (data_width // 8))
        self.little_endian = (endianness == 'little')
        self.mem_base = mem_base
        
        self.area = []
        
        if (self.little_endian == False):
            raise Exception('big endian not supported yet')

    def getMaxSize(self):
        return self.maxSize
    
    def reallocArea(self, offset, size):
        start = offset
        end = offset + size -1
        mem_base = self.mem_base
        
        print(f'original area: {start+mem_base:016X}-{end+mem_base:016X}')

        # first check if it is already included , and expand 
        for block in self.area:
            bstart = block[0]
            bend = block[0] + block[1] -1
            
            if (start >= bstart and start <= bend and end >= bstart and end <= bend):
                print('new block already included in {:016X}-{:016X}'.format(bstart+mem_base, bend+mem_base))
                return
            
            if (start >= bstart and start <= bend):
                print('new block start {:016X} included in {:016X}-{:016X}, updating start'.format(start+mem_base, bstart+mem_base, bend+mem_base))
                start = bstart
                
            if (end >= bstart and end <= bend):
                print('new block end {:016X} included in {:016X}-{:016X}, updating end'.format(end+mem_base, bstart+mem_base, bend+mem_base))
                end = bend
                
        print(f'reshaped area: {start+mem_base:016X}-{end+mem_base:016X}')
        newsize = end + 1 - start
        
        if (newsize > size):
            size = newsize
            print('updating size to {:X} bytes'.format(size))
        
        # create area
        newarea = bytearray(size)
        newlist = []
        
        for block in self.area:
            bstart = block[0]
            bend = block[0] + block[1] -1
            bdata = block[2]
            
            if (bstart >= start and bstart <= end and bend >= start and bend <= end):
                print('copying block {:016X}-{:016X} into new block {:016X}-{:016X}'.format(bstart+mem_base, bend+mem_base, start+mem_base, end+mem_base))
                for i in range(len(bdata)):
                    newarea[bstart-start+i] = bdata[i]
                    
            else:
                newlist.append(block)
                
        
        #first avoid checking overlaps
        newlist.append((start, size, newarea))
        
        self.area = newlist
        
    def writeByte(self, address, value):
        for area in self.area:
            offset = area[0]
            size = area[1]
            data = area[2]
            #print('mem write byte address:{} - range: [{},{}]'.format(address, offset, size) )

            if (address >= offset and address <= (offset+size)):
                data[address-offset] = value
                return

        raise Exception('Address {:0X} not in memory'.format(address + self.mem_base))
                    
    def readByte(self, address):
        for area in self.area:
            offset = area[0]
            size = area[1]
            data = area[2]
            #print('mem write byte address:{} - range: [{},{}]'.format(address, offset, size) )

            if (address >= offset and address < (offset+size)):
                return data[address-offset]                 

        raise Exception('Address {:0X} not in memory'.format(address + self.mem_base))
        
    def read_i64(self, address):
        # reads in little endian (LEAST SIGNIFICANT BYTE FIRST)
        v = 0
        for i in range(8):
            v |= self.readByte(address+i) << (8*i)
            
        return v
    
    def write_i64(self, address, value):
        # writes in little endian (LEAST SIGNIFICANT BYTE FIRST)
        
        for i in range(8):
            self.writeByte(address+i, (value >> (8*i)) & 0xFF) 
        
    def write(self, address:int, value:int, be:int):
        #self.values[address//4] = value
        raise Exception('not implemented')
        
    def read(self, address:int) -> int:
        #return self.values[address//4]
        raise Exception('not implemented')
        
    def clock(self):
        data_width = self.port.read_data.getWidth()
        
        address = self.port.address.get()
        be = self.port.be.get()

        
        if (self.port.read.get()):

            value = 0
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            for i in range(data_width // 8):                
                value = value | (self.readByte(address+i) << (i*8))
                
            self.port.read_data.prepare(value)
            if (self.verbose): print('reading address ', hex(address+mem_base), '=', hex(value))

        elif (self.port.write.get()):

            value = self.port.write_data.get()

            if (self.verbose): print('writing address ', hex(address+mem_base), '=', hex(value))
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            
            for i in range(data_width // 8):           
                if ((be & 0x1) != 0):
                    self.writeByte(address + i, value & 0xFF)
                be = be >> 1
                value = value >> 8


class PersistentMemory(Logic):
    def __init__(self, parent:Logic, name:str, 
                 #data_width:int, address_width:int,
                 filename, 
                 port:MemoryInterface, endianness='little'):
        super().__init__(parent, name)
        
        self.port = self.addInterfaceSink('port', port)        
        self.verbose = True
        file = open(filename, 'r+b')
        self.mm = mmap.mmap(file.fileno(), 0)

    def clock(self):
        data_width = self.port.read_data.getWidth()
        
        address = self.port.address.get()
        be = self.port.be.get()

        
        if (self.port.read.get()):

            value = 0
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            for i in range(data_width // 8):                
                value = value | (self.readByte(address+i) << (i*8))
                
            self.port.read_data.prepare(value)
            if (self.verbose): print('reading address ', hex(address), '=', hex(value))

        elif (self.port.write.get()):

            value = self.port.write_data.get()

            if (self.verbose): print('writing address ', hex(address), '=', hex(value))
            
            # in little endian less significant byte is stored first
            # 0x0102 would be stored as 0x02 0x01
            
            for i in range(data_width // 8):           
                if ((be & 0x1) != 0):
                    self.writeByte(address + i, value & 0xFF)
                be = be >> 1
                value = value >> 8


    def writeByte(self, address, value):

        self.mm[address] = value
                    
    def readByte(self, address):

        return self.mm[address]
