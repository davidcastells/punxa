#include <stdio.h>
#include <stdlib.h>

int ga = 0xCAFEBABE;
int gb;


#define ECALL(syscall_number, arg0, arg1, arg2) {      \
    register int a0 asm("a0") = (int)(arg0);      \
    register int a1 asm("a1") = (int)(arg1);      \
    register int a2 asm("a2") = (int)(arg2);      \
    register int a7 asm("a7") = (int)(syscall_number); \
    asm volatile (                               \
        "ecall"                                  \
        : "+r" (a0)                              \
        : "r" (a1), "r" (a2), "r" (a7)           \
        : "memory"                               \
    );                                           \
    a0;                                          \
}

#define TRACEMEM(arg0, arg1, arg2) ECALL(0xFF, arg0, arg1, arg2)

int fact(int fa, int* fb)
{
    int ret;
    
    // trick to print fa1, fa2, ...
    char sfa[] = {'f', 'a', '0'+*fb, 0};
    char sfb[] = {'f', 'b', '0'+*fb, 0};
        
    TRACEMEM(&fa, sfa, sizeof(int))
    TRACEMEM(&fb, sfb, sizeof(int*))
    
    if (fa == 1)
        return 1;
        
    else 
    {
        *fb += 1;
        ret = fact(fa -1, fb);
    }
}

void last();

int main(int argc, char* args[])
{
    // I play the trick of having a dummy function at the end (last) to estimate
    // the size of the code    
    TRACEMEM(fact, "code", (int)last - (int)fact)
    
    int la=5;
    
    int* ph = malloc(sizeof(int) * 2);
    ph[0] = 0;
    
    // Trace global variable locations
    TRACEMEM(&ga, "ga", sizeof(int))
    TRACEMEM(&gb, "gb", sizeof(int))
    
    // Trace local variables in this function scope
    
    TRACEMEM(&la, "la", sizeof(int))
    TRACEMEM(&ph, "ph", sizeof(int*)) // ph is a pointer
    TRACEMEM(ph, "h", sizeof(int)*2)  // I name h the value pointed by ph (which should be in the HEAP)
    
    ph[1] = fact(la, ph);
    
    printf("Factorial of %d = %d. Took %d iterations\n", la, ph[1], ph[0]);
}

void last()
{
}
