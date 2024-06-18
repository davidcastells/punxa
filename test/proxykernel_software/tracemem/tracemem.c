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

void f(int fa, int* fb)
{
    TRACEMEM(&fa, "fa", sizeof(int))
    TRACEMEM(&fb, "fb", sizeof(int*))
}

void last();

int main(int argc, char* args[])
{
    int la=2;
    
    int* ph = malloc(sizeof(int) * 2);
    
    TRACEMEM(&ga, "ga", sizeof(int))
    TRACEMEM(&gb, "gb", sizeof(int))
    TRACEMEM(&la, "la", sizeof(int))
    TRACEMEM(&ph, "ph", sizeof(int*))
    TRACEMEM(ph, "h", sizeof(int)*2)
    
    f(la, ph);
    
    TRACEMEM(f, "code", (int)last - (int)f)
    
}

void last()
{
}
