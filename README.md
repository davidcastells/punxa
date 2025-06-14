# punxa
Python-based RISC-V Full System Simulator.

Punxa provides HDL models of different parts of a full RISC-V system designed in different design styles using [py4hw](https://github.com/davidcastells/py4hw).

For the processor, we currently support two 64-bit models :

- Behavioral Model of a single-cycle execution processor without pipeline
- Microprogrammed structural design with an algorithmic Control Unit implementation
 

The single-cycle version suppports full system simulation and proxy-kernel simulation (as in Spike).
We also introduce a Linux proxy-kernel to simulate applications compiled with riscv64-unknown-linux-gnu-gcc.

We also support two 32-bit models:

- Behavioral Model of a single-cycle execution processor without pipeline
- Microprogrammed structural design with an algorithmic Control Unit implementation
  
## Testing

We started focussing on RV64 and Baremetal applications (compiled with risc64-unknown-elf-gcc).
Then, we moved to RV32.
When completed, next goal is Linux boot.

### RISC-V ISA Tests

***RV64*** ISA tests progress: 

<table>
 <tr><td>Version</td><td>Progress</td></tr>
 <tr>
  <td>Single Cycle </td><td>99.7 %   |█████████████████████████████████████████████|</td>
 </tr>
 <tr>
  <td>Microprogrammed </td><td>30.1 %   |██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|</td>  
 </tr>
</table>


***RV32*** ISA tests progress:

<table>
<tr><td>Version</td><td>Progress</td></tr>
<tr>
 <td>Single Cycle </td><td>99.6 %   |█████████████████████████████████████████████|</td>
</tr>
<tr>
 <td>Microprogrammed </td><td>53.8 %   |█████████████████████████░░░░░░░░░░░░░░░░░░░░|</td>
</tr>
</table>

check [riscv-tests](https://github.com/davidcastells/punxa/blob/main/test/riscv-tests/README.md) for a complete list

### Proxy-kernel Apps

- [Hello World](https://github.com/davidcastells/punxa/blob/main/test/proxykernel_software/hello/README.md)
- [Mandelbrot](https://github.com/davidcastells/punxa/blob/main/test/proxykernel_software/mandelbrot/README.md)
- [File sort](https://github.com/davidcastells/punxa/tree/main/test/proxykernel_software/sort/README.md)
- [Paranoia](https://github.com/davidcastells/punxa/tree/main/test/proxykernel_software/paranoia/README.md)

### Publications
Cite as

```
@article{castells2025punxa,
author={Castells-Rufas, David and Novo, David and Martorell, Xavier},
title={Punxa: A Python-Based RISC-V System Simulator for Education},
journal={Electronics Letters},
volume={61},
number={1},
pages={e70300},
doi={10.1049/ell2.70300},
year={2025}}
```

```
@INPROCEEDINGS{castells2024educational,
  author={Castells-Rufas, David and Novo, David and Martorell, Xavier},
  booktitle={2024 39th Conference on Design of Circuits and Integrated Systems (DCIS)}, 
  title={An Educational Tool to Analyze the Hardware/Software Integration in RISC-V Systems}, 
  year={2024},
  pages={1-6},
  doi={10.1109/DCIS62603.2024.10769201}}
```
