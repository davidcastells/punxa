# -*- coding: utf-8 -*-
"""
Created on Tue May 13 18:38:51 2025

@author: 2016570
"""

from punxa.single_cycle.singlecycle_processor_32 import *
from punxa.memory import *
from punxa.interactive_commands import *
from punxa.assembly import *
import punxa.interactive_commands 

def buildHw():
    global mem
    global cpu
    hw = HWSystem()
    
    mem_width = 8
    
    port_c = MemoryInterface(hw, 'port_c', 32, mem_width)   # CPU Bus    
    mem = Memory(hw, 'mem', 32, mem_width, port_c)
        
    gnd = hw.wire('gnd')
    py4hw.Constant(hw, 'gnd', 0, gnd)
    
    cpu = SingleCycleRISCV32(hw, 'RISCV', port_c, gnd, gnd, [gnd, gnd], 0)
    
    # pass objects to interactive commands module
    import punxa.interactive_commands
    punxa.interactive_commands._ci_hw = hw
    punxa.interactive_commands._ci_cpu = cpu
    
    cpu.stopOnExceptions = True
    return hw

def load_assembly_text(text, add=0):
    lines = text.split('\n')
    
    load_assembly_lines(lines, add)
    
def load_assembly_lines(asm_lines, add = 0):
    global mem
    global start_add 
    global end_add 
    
    start_add = add
    end_add = add
    
    for asm_line in asm_lines:
        
        asm_line = asm_line.strip() # strip line
        if ('#' in asm_line):
            # remove any comment
            asm_line = asm_line.split('#')[0]
            asm_line = asm_line.strip() # strip line
            
        if (asm_line == ''):
            continue
        
        #print(f'PROCESSING {asm_line}')
        
        ins = assemble(asm_line)
        asm = disassemble(ins)

        #print(f'{add:08X} = {asm_line} =  {ins:08X} = {asm}')

        mem.write_i32(end_add, ins)

        end_add += 4
        
def get_assembly():
    # returns a dictionary with address, assembly
    global start_add 
    global end_add 

    add = start_add
    ret = []
    
    while (add < end_add):
        ret.append((add, disassemble(mem.read_i32(add))))
        add += 4
    
    return ret

def buildInterface(mem_width=500):
    global mem
    import ipywidgets as widgets
    from IPython.display import display, clear_output
    import random

    # --- Create the 32 registers as text boxes in a vertical column ---
    registers = [widgets.Text(value='00000000', description=f'x{i:02}', style={'font_family': 'monospace'}, layout=widgets.Layout(width='180px')) for i in range(32)]
    #register_column = widgets.VBox(registers)
    register_grid = widgets.GridBox(registers, 
                                    style={'font_family': 'monospace'},
                                    layout=widgets.Layout(grid_template_columns="repeat(2, 200px)"))

    # --- Buttons ---
    reset_button = widgets.Button(description='Reset', button_style='info')
    clock_button = widgets.Button(description='Step', button_style='info')
    buttons = widgets.HBox([reset_button, clock_button])

    # --- Instructions list (for now just static) ---
    lines = [f'{x[0]:08X} - {x[1]}' for x in get_assembly()]
    instruction_list = widgets.Select(
        options=lines,
        description='Instructions:',
        rows=max(len(lines), 10),
        style={'font_family': 'monospace'},
        layout=widgets.Layout(width='400px')
    )

    # --- Memory display (e.g., 16 words starting from base) ---
    memory_display = widgets.Textarea(value='', description='Memory:',
                                      style={'font_family': 'monospace'},
                                      layout=widgets.Layout(width=f'{mem_width}px', height='300px'))

    # --- Combine instructions and register display side-by-side ---
    left_pane = widgets.VBox([instruction_list, memory_display], layout=widgets.Layout(width=f'{mem_width+50}px', height='600px'))
    top_layout = widgets.HBox([left_pane, register_grid])

    # --- Memory base address input ---
    base_address_input = widgets.Text(value='0x00000000', style={'font_family': 'monospace'}, description='Base Addr:')



    def update_memory_display(*args):
        try:
            base_addr = int(base_address_input.value, 16)
        except ValueError:
            memory_display.value = 'Invalid address'
            return

        lines = []
        cpl = 16
        for i in range(10):
            addr = base_addr + i * cpl
            s = f'{addr:08X}: '
            sa = ''
            for c in range(0, cpl):  # show 16 words
                addr = base_addr + i * cpl + c
                val = mem.readByte(addr)
                s += f'{val:02X}'
                sa += f'{chr(val)}' if (val >= 32) and (val < 128) else '·'

            lines.append(s + f' |{sa}|')

        memory_display.value = '\n'.join(lines)


    base_address_input.observe(update_memory_display, names='value')

    def on_reset_pressed(b):
        cpu = punxa.interactive_commands._ci_cpu
        cpu.pc = 0
        instruction_list.index = 0

    # --- Clock button action ---
    def on_clock_pressed(b):
        step()

        cpu = punxa.interactive_commands._ci_cpu

        for i in range(32):
            try:
                val = cpu.getReg(i)
                registers[i].value = f"{(val) & 0xFFFFFFFF:08X}"
            except ValueError:
                pass  # Ignore invalid input

        pc = cpu.pc
        # map the pc to the lines
        lines = get_assembly()

        line_map = {}
        for idx, line in enumerate(lines):
            line_map[line[0]] = idx

        if not(pc in line_map.keys()):
            print(f'Program finished! pc = {pc:08X}')
            print('Press RESET button to restart')
        else:
            #print('address', pc, 'in index', line_map[pc])
            instruction_list.index = line_map[pc]
            
        update_memory_display()


    reset_button.on_click(on_reset_pressed)
    clock_button.on_click(on_clock_pressed)

    # --- Layout ---
    display(widgets.HTML("<h2>RISC-V Simulator Interface</h2>"))
    display(buttons)
    display(top_layout)
    #display(widgets.HTML("<h3>Memory Viewer</h3>"))
    #display(base_address_input)
    #display(memory_display)

    # Initialize memory display
    update_memory_display()
