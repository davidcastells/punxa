# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 12:14:54 2023

@author: dcr
"""

import json
import gzip
import shutil

class Tracer:
    events = [] # this is a list of string pairs , 
                # 1 -   '>' for function entry
                #       '<' for function exit
                # 2 - function name
    instants = []
    
    pending = {}
                
    def start(self, info):
        # info is a pair (function name, t0)
        f = info[0]
        self.pending[f] = info
    
    def ignore(self, fn):
        if (fn in self.pending.keys()):
            self.pending.pop(fn)
        
    def complete(self, tup):
        # info is a tuple (function name, t0, tf)
        if (tup[0] in self.pending.keys()):
            self.pending.pop(tup[0])
        self.events.append(tup)
    
    def instant(self, tup):
        self.instants.append(tup)

    def demangleEvents(self):
        from itanium_demangler import parse as demangle

        newevents = []
        
        for event in self.events:
            name = event[0]
            try:
                demangled = demangle(name)
                if (demangled is None):
                    pass
                else:
                    name = str(demangled)                
            except Exception as e:
                print('could not demangle', event[0], name, str(e))
                
            newevents.append((name, event[1], event[2]))
            
        return newevents
            
           
    def write_json(self, filename):
        import datetime
        
        ret = {}
        
        self.clk_freq = 50e6
            
        events = []
        
        demangled = self.demangleEvents()
        
        events.append(self.processInfo(1, 'punxa RISC-V ISS'))
        events.append(self.threadInfo(1, 1, 'HART-0'))

        if (len(demangled) > 0):
            events.append(self.processUptime(1, demangled[-1][2] / self.clk_freq))

        for event in self.pending.values():
            if (isinstance(event[0], int)):
                # ignore function addresses
                continue
            events.append(self.formatPendingEvent(1, 1, event))
            
        for event in demangled:
            events.append(self.formatEvent(1, 1, event))
            
        for event in self.instants:
            events.append(self.formatInstant(1, 1, event))
        
        ret['traceEvents'] = events
    
        metadata = {}
        metadata["highres-ticks"] = 1
        metadata["trace-capture-datetime"] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        ret['metadata'] = metadata
        
        write_to_json(ret, filename)
    
    def processInfo(self, pid, name):
        return { "args": { "name": name }, "cat": "__metadata", "name": "process_name", "ph": "M", "pid": pid, "tid": 0, "ts": 0}
     
    def threadInfo(self, pid, tid, name):
        return  {"args": {"name": name },"cat": "__metadata","name": "thread_name","ph": "M","pid": pid,"tid": tid,"ts": 0}

    def processUptime(self, pid, time):
        return { "args": {"uptime": str(time) }, "cat": "__metadata", "name": "process_uptime_seconds", "ph": "M", "pid": pid, "tid": 0, "ts": 0 }
    
    def formatPendingEvent(self, pid, tid, event):
        f = event[0] 
        us_inv = 1/1e-6
        t0 = event[1] * us_inv / self.clk_freq 
        
        return { "args": {}, "cat": "toplevel", "name": str(f), "ph": "B", "pid": pid, "tid": tid, "ts": t0}

    def formatEvent(self, pid, tid, event):
        f = event[0]
        us_inv = 1/1e-6
        t0 = event[1] * us_inv / self.clk_freq
        tf = event[2] * us_inv / self.clk_freq
        
        return { "args": {}, "cat": "toplevel", "dur": tf-t0, "name": str(f), "ph": "X", "pid": pid, "tdur": tf-t0, "tid": tid, "ts": t0, "tts": tf}
    
    def formatInstant(self, pid, tid, event):
        f = '{}-{}'.format(event[0], event[1])
        us_inv = 1/1e-6
        t0 = event[2] * us_inv / self.clk_freq
        
        return {"name": f, "ph": "i", "ts": t0, "pid": pid, "tid": tid, "s": "g"}
    
def write_to_json(info, filename):
    json_object = json.dumps(info, indent=4)
 
    # Writing to sample.json
    with open(filename, "w") as outfile:
        outfile.write(json_object)
        outfile.close()
        
    with open(filename, 'rb') as f_in:
        with gzip.open(filename+'.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
def remove_events_before(info, max_ts):
    events = info['traceEvents']
    newevents = []
    
    for event in events:
        if (event['ts'] < max_ts):
            newevents.append(event)
            
    info['traceEvents'] = newevents

def remove_events_from_pid(info, pid):
    events = info['traceEvents']
    newevents = []
    
    for event in events:
        if (event['pid'] != pid):
            newevents.append(event)
            
    info['traceEvents'] = newevents
    
def get_pids(info):
    ret = set([])
    
    for event in info['traceEvents']:
        ret.add(event['pid'])

    return ret
