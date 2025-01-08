
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

uint64_t syscall_fstat(uint64_t fd, uint64_t buf);
uint64_t syscall_write(uint64_t fd, uint64_t buf, uint64_t count);

__attribute__((always_inline)) 
static inline void read_csr_mcause() {
    asm volatile ("csrr t0, %0" : : "i"(CSR_MCAUSE));
}

__attribute__((always_inline)) 
static inline uint64_t read_csr_mepc() {
    uint64_t result;
    asm volatile ("csrr %0, %1" : "=r"(result) : "i"(CSR_MEPC));
    return result;
}

__attribute__((always_inline)) 
static inline void write_csr_mepc(uint64_t value) {
    asm volatile ("csrw %0, %1" : : "i"(CSR_MEPC), "r"(value));
}

__attribute__((always_inline)) 
static inline uint64_t read_a0() {
    uint64_t value;
    asm volatile("mv %0, a0" : "=r"(value));
    return value;
}
__attribute__((always_inline)) 
static inline uint64_t read_a7() {
    uint64_t value;
    asm volatile("mv %0, a7" : "=r"(value));
    return value;
}
__attribute__((aligned(8))) 
__attribute__((naked)) 
void trap_handler() {

    asm volatile (
        "addi sp, sp, -32\n"       // Adjust stack pointer (32 bytes for 4 registers)
        "sd ra, 24(sp)\n"          // Save return address (ra) at offset 24
        "sd s0, 16(sp)\n"          // Save frame pointer (s0) at offset 16
        "sd s1, 8(sp)\n"           // Save callee-saved register (s1) at offset 8
        "sd s2, 0(sp)\n"           // Save callee-saved register (s2) at offset 0
    );
    
    register uint64_t mcause asm("t0");
    read_csr_mcause();
    
    register uint64_t a0 asm("a0");
    register uint64_t a1 asm("a1");
    register uint64_t a2 asm("a2");
    register uint64_t a3 asm("a3");
    register uint64_t syscall asm("a7");
            
    asm volatile("" : : : "a0");  // Clobber the register
    asm volatile("" : : : "a1");  // Clobber the register
    asm volatile("" : : : "a2");  // Clobber the register
    asm volatile("" : : : "a3");  // Clobber the register
    asm volatile("" : : : "a7");  // Clobber the register
    
    // Check if the trap was caused by ECALL
    if (mcause == ENV_CALL_MMODE) 
    {
        // 11: ECALL in Machine mode
        //register uint64_t syscall = read_a7();

        
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
        register uint64_t mepc = read_csr_mepc();
        write_csr_mepc(mepc+4);
        
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
    
        asm volatile("mret"); 
    }
}

#define UART_BASE 0xFFF0C2C000
#define UART_THR_OFFSET 0

uint64_t syscall_fstat(uint64_t fd, uint64_t buf)
{
    // char* pbuf = (char*) buf;
    return -1; 
}

uint64_t syscall_write(uint64_t fd, uint64_t buf, uint64_t count)
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
