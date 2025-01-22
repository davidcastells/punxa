
#include <stdint.h>

#define CSR_MEPC   0x341
#define CSR_MCAUSE 0x342

#define ENV_CALL_MMODE  11

#define SYSCALL_OPENAT  56
#define SYSCALL_CLOSE  57
#define SYSCALL_READ  63
#define SYSCALL_WRITE  64
#define SYSCALL_FSTAT  80
#define SYSCALL_EXIT  93
#define SYSCALL_BRK  214
#define SYSCALL_OPEN  1024

#if __riscv_xlen == 32
    #pragma message "Compiling for 32-bit RISC-V"
    #define UINT uint32_t
#elif __riscv_xlen == 64
    #pragma message "Compiling for 64-bit RISC-V"
    #define UINT uint64_t
#endif

UINT syscall_fstat(UINT fd, UINT buf);
UINT syscall_write(UINT fd, UINT buf, UINT count);

__attribute__((always_inline)) 
static inline void read_csr_mcause() {
    asm volatile ("csrr t0, %0" : : "i"(CSR_MCAUSE));
}

__attribute__((always_inline)) 
static inline UINT read_csr_mepc() {
    uintmax_t result;
    asm volatile ("csrr %0, %1" : "=r"(result) : "i"(CSR_MEPC));
    return result;
}

__attribute__((always_inline)) 
static inline void write_csr_mepc(UINT value) {
    asm volatile ("csrw %0, %1" : : "i"(CSR_MEPC), "r"(value));
}


__attribute__((aligned(8))) 
__attribute__((naked)) 
void trap_handler() {

#if __riscv_xlen == 32
    asm volatile (
        "addi sp, sp, -16\n"       // Adjust stack pointer (16 bytes for 4 registers)
        "sw ra, 12(sp)\n"          // Save return address (ra) 
        "sw s0, 8(sp)\n"          // Save frame pointer (s0) 
        "sw s1, 4(sp)\n"           // Save callee-saved register (s1) 
        "sw s2, 0(sp)\n"           // Save callee-saved register (s2) 
    );
#else
    asm volatile (
        "addi sp, sp, -32\n"       // Adjust stack pointer (32 bytes for 4 registers)
        "sd ra, 24(sp)\n"          // Save return address (ra) 
        "sd s0, 16(sp)\n"          // Save frame pointer (s0) 
        "sd s1, 8(sp)\n"           // Save callee-saved register (s1) 
        "sd s2, 0(sp)\n"           // Save callee-saved register (s2) 
    );
#endif

    register UINT mcause asm("t0");
    read_csr_mcause();
    
    register UINT a0 asm("a0");
    register UINT a1 asm("a1");
    register UINT a2 asm("a2");
    register UINT a3 asm("a3");
    register UINT syscall asm("a7");
            
    asm volatile("" : : : "a0");  // Clobber the register
    asm volatile("" : : : "a1");  // Clobber the register
    asm volatile("" : : : "a2");  // Clobber the register
    asm volatile("" : : : "a3");  // Clobber the register
    asm volatile("" : : : "a7");  // Clobber the register
    
    // Check if the trap was caused by ECALL
    if (mcause == ENV_CALL_MMODE) 
    {
        // 11: ECALL in Machine mode


        
        if (syscall == SYSCALL_FSTAT)
        {
            a0 = syscall_fstat(a0, a1);
        }
        else if (syscall == SYSCALL_BRK)
        {
        }
        else if (syscall == SYSCALL_READ)
        {
                /*
        fd = self.reg[10]
                buf = self.reg[11]
                count = self.reg[12]
                print(f'READ fd:0x{fd:X} buf:0x{buf:X} count:0x{count:X}')                
                self.reg[10] = self.syscall_read(fd, buf, count)
        */

        }
        else if (syscall == SYSCALL_WRITE)
        {
            a0 = syscall_write(a0, a1, a2);
        }
        
    }
    
    {
        register UINT mepc = read_csr_mepc();
        write_csr_mepc(mepc+4);
        
#if __riscv_xlen == 32
        asm volatile 
        (
        // Restore callee-saved registers and return address from the stack
        "lw ra, 12(sp)\n"         // Load return address (ra) from offset 24
        "lw s0, 8(sp)\n"         // Load frame pointer (s0) from offset 16
        "lw s1, 4(sp)\n"          // Load callee-saved register (s1) from offset 8
        "lw s2, 0(sp)\n"          // Load callee-saved register (s2) from offset 0
        // Adjust the stack pointer back to its original value
        "addi sp, sp, 16\n"       // Restore stack pointer (undo allocation)
        );
#else        
        asm volatile 
        (
        // Restore callee-saved registers and return address from the stack
        "ld ra, 24(sp)\n"         // Load return address (ra) from offset 24
        "ld s0, 16(sp)\n"         // Load frame pointer (s0) from offset 16
        "ld s1, 8(sp)\n"          // Load callee-saved register (s1) from offset 8
        "ld s2, 0(sp)\n"          // Load callee-saved register (s2) from offset 0
        // Adjust the stack pointer back to its original value
        "addi sp, sp, 32\n"       // Restore stack pointer (undo allocation)
        );
#endif 
    
        asm volatile("mret"); 
    }
}

#define UART_BASE 0x10000000
#define UART_THR_OFFSET 0

UINT syscall_fstat(UINT fd, UINT buf)
{
    // char* pbuf = (char*) buf;
    return -1; 
}

UINT syscall_write(UINT fd, UINT buf, UINT count)
{
    char* pbuf = (char*) buf;
    char* uart = (char*) UART_BASE;
    int i;
    
    for (i=0; i < count; i++)
    {
        uart[UART_THR_OFFSET] = pbuf[i];
    }
    
    return 0;
}
