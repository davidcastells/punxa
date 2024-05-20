# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 09:53:00 2022

@author: dcr
"""

import py4hw
from py4hw.logic import *
from py4hw.logic.storage import *
from py4hw.simulation import Simulator
import py4hw.debug


class MultiplexedBus(Logic):
    
    def __init__(self, parent:Logic, name:str, master, slaves):
        super().__init__(parent, name);

        self.master = self.addInterfaceSink('master', master)

        self.slaves = []
        self.start = []
        self.stop = []
        
        
        for idx, slave in enumerate(slaves):
            port = slave[0]
            start = slave[1]
            
            size = (1 << port.address.getWidth())
            
            if (len(slave) > 2):
                # size is provided
                addressSize = size
                size = slave[2]
                if (size > addressSize):
                    raise Exception('address size does not allow required memory map')
            
            stop = start + size - 1
            
            self.slaves.append(port)
            self.start.append(start)
            self.stop.append(stop)
            
            self.addInterfaceSource('slave_{}'.format(idx), port)
            
            print('Slave {} = [{:016X}]-[{:016X}]'.format(idx, start, stop))
            
    def propagate(self):
        addr = self.master.address.get()
        read = self.master.read.get()
        write = self.master.write.get()
        be = self.master.be.get()
        write_data = self.master.write_data.get()
        
        handled = False
        
        for idx, slave in enumerate(self.slaves):
            start = self.start[idx]
            stop = self.stop[idx]

            if (addr >= start and addr <= stop and (read > 0 or write > 0)):
                addr -= start
            
                slave.address.put(addr)
                slave.read.put(read)
                slave.write.put(write)
                slave.write_data.put(write_data)
                slave.be.put(be)
                
                self.master.read_data.put(slave.read_data.get())
                handled = True
            else:
                slave.address.put(0)
                slave.read.put(0)
                slave.write.put(0)
                slave.write_data.put(0)
                slave.be.put(0)
                
                
        # if we reach here, this was an invalid 
        if (not(handled)):
            if (read):
                print('Invalid read access to : {:016X}'.format(addr))
                self.parent.getSimulator().stop()
            if (write):
                print('Invalid write access to : {:016X}'.format(addr))
                self.parent.getSimulator().stop()
