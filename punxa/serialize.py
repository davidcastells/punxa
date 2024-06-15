# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 19:32:45 2022

@author: dcr
"""

class Serializer:
    def __init__(self, filename):
        self.file = open(filename, 'wb')
        
    def write_i64(self, v):
        self.file.write(int(v & ((1<<64)-1)).to_bytes(64//8, byteorder='big'))
        
    def write_bytearray(self, v):
        self.file.write(v)
    
    def write_string_list(self, v):
        self.write_i64(len(v))
        for s in v:
            self.write_string(s)
            
    def write_int_list(self, v):
        self.write_i64(len(v))
        for s in v:
            self.write_i64(s)

    def write_int_pair_list(self, v):
        self.write_i64(len(v))
        for s in v:
            self.write_i64(s[0])
            self.write_i64(s[1])
            
    def write_string(self, s):
        ba = bytes(s, 'UTF-8')
        self.write_i64(len(ba))
        self.file.write(ba)

    def write_dictionary(self, d):
        self.write_i64(len(d.keys()))
        
        for key in d.keys():
            self.write_object(key)
            self.write_object(d[key])

    def write_object(self, obj):
        #print('writing object ', obj)
        #print('object type', type(obj))        
        
        stype = str(type(obj))
        self.write_string(stype)

        if (stype == "<class 'str'>"):
            self.write_string(obj)
        elif (stype == "<class 'int'>"):
            self.write_i64(obj)
        elif (stype == "<class 'tuple'>"):
            self.write_i64(len(obj))
            for x in obj:
                self.write_object(x)
        else:
            raise Exception('Serialization of {} objects not supported'.format(stype))
        
    def close(self):
        self.file.close()
        
class Deserializer:
    
    def __init__(self, filename):
        
        self.file = open(filename, 'rb')
        
        
    def read_i64(self):
        return int.from_bytes(self.file.read(64//8), byteorder='big')
        
    def read_bytearray(self, n):
        return self.file.read(n)
    
    def read_string_list(self):
        ret = []
        
        n = self.read_i64()
        
        for i in range(n):
            ret.append(self.read_string())
            
        return ret

    def read_int_list(self):
        ret = []
        
        n = self.read_i64()
        
        for i in range(n):
            ret.append(self.read_i64())
            
        return ret

    def read_int_pair_list(self):
        ret = []
        
        n = self.read_i64()
        
        for i in range(n):
            v0 = self.read_i64()
            v1 = self.read_i64()
            ret.append((v0,v1))
            
        return ret
          
    def read_string(self):
        n = self.read_i64()
        ba = self.file.read(n)
        return str(ba, 'UTF-8')
        
    def read_dictionary(self):
        ret = {}
        
        dlen = self.read_i64()
        
        for i in range(dlen):
            key = self.read_object()
            value = self.read_object()
            ret[key] = value
            
        return ret

    def read_object(self):
        
        stype = self.read_string()

        if (stype == "<class 'str'>"):
            return self.read_string()
        elif (stype == "<class 'int'>"):
            return self.read_i64()
        elif (stype == "<class 'tuple'>"):
            olen = self.read_i64()
            temp = []
            for x in range(olen):
                temp.append(self.read_object())
                
            return tuple(temp)
        else:
            raise Exception('Serialization of {} objects not supported'.format(stype))
        
    def close(self):
        self.file.close()
        
    