# punxa
Python-based RISC-V Full System Simulator.

It suppports full system simulation and proxy kernel simulation (as in Spike).

## Testing

We started focussing on RV64 and Baremetal applications (compiled with riscv64-unknown-elf-gcc).
We are also implementing support for Linux applications (compiled with riscv64-unknown-linux-gnu-gcc).
When completed, next goal is Linux boot.

### RISC-V ISA Tests

RV64 ISA tests progress: 

96.0 %   |████████████████████████████████████████████░|

check [riscv-tests](https://github.com/davidcastells/punxa/blob/main/test/riscv-tests/README.md) for a complete list

### Proxy-kernel Apps

- Hello World
- [Mandelbrot](https://github.com/davidcastells/punxa/blob/main/test/proxykernel_software/mandelbrot/README.md)
- [File sort](https://github.com/davidcastells/punxa/tree/main/test/proxykernel_software/sort/README.md)
- [Paranoia](https://github.com/davidcastells/punxa/tree/main/test/proxykernel_software/paranoia/README.md)
