# punxa
Python-based RISC-V Full System Simulator.

It suppports full system simulation and proxy kernel simulation (as in Spike).

## Testing

We started focussing on RV64 and Baremetal applications (compiled with risc64-unknown-elf-gcc).
When completed, next goal is Linux boot.

### RISC-V ISA Tests

Some instructions from the rv64uzbs and rv64uzfh are not implemented. 
We have some bugs in floating point operations.

RV64 (excluding vector and cache management instructions) progress: 

90.3 %   |█████████████████████████████████████████░░░░|

check [riscv-tests](https://github.com/davidcastells/punxa/blob/main/test/riscv-tests/README.md) for a complete list

### Proxy-kernel Apps

- Hello World
