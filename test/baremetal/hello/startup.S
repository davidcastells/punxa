.section .text
.globl _start
.globl _startup
.type _startup, @function 
_startup:
    la t0, trap_handler
    csrw mtvec, t0
    j _start
