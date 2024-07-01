# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:07:06 2024

@author: 2016570
"""
import sys
import json
import gzip
import shutil

def read_from_json(filename):
    # Decompress the gzipped JSON file
    file_json_gz = filename
    file_json = filename[:-3]
    
    with gzip.open(file_json_gz, 'rb') as f_in:
        with open(file_json, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Read the decompressed JSON file
    with open(file_json, 'r') as infile:
        data = json.load(infile)
    
    return data

def write_to_json(info, filename):
    json_object = json.dumps(info, indent=4)
 
    # Writing to sample.json
    with open(filename, "w") as outfile:
        outfile.write(json_object)
        outfile.close()
        
    with open(filename, 'rb') as f_in:
        with gzip.open(filename+'.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def changeToProcess(events, pid):
    ret = []
    
    for item in events:
        item['pid'] = pid
        
        if not(item['name'] in ['None', 'exit', '__call_exitprocs']):
            if ('dur' in item.keys()):
                if (item['dur'] > 100):
                    ret.append(item)
            else:
                ret.append(item)
        
    return ret

if __name__ == "__main__":
    
    print(sys.argv)
    
    if (len(sys.argv) == 3):
        f1 = sys.argv[1]
        f2 = sys.argv[2]
    else:
        f1 = 'trace_normal.json.gz'
        f2 = 'trace_custom_instruction.json.gz'
    
    data1 = read_from_json(f1)
    data2 = read_from_json(f2)
    
    print('num events in {} = {}'.format(f1, len(data1['traceEvents'])))
    print('num events in {} = {}'.format(f2, len(data2['traceEvents'])))
    
    data = {}
    #data['traceEvents'] = data1['traceEvents']
    data['traceEvents'] = []
    data['traceEvents'].extend( changeToProcess(data1['traceEvents'], 1))
    data['metadata'] = data1['metadata']
    
    data['traceEvents'].extend( changeToProcess(data2['traceEvents'], 2))
    
    
    write_to_json(data, 'combined.json')