# Hello World Linux App

In this test we compile a hello world app with riscv64-unknown-linux-gnu-gcc 
and statically linked glibc and to test the processor implementation of
linux proxy kernel.

This Linux proxy-kernel is similar to Spike proxy-kernel (that is used to test 
bare-metal applications), but implements more system calls used by Linux.

You can see the syscalls used by hello world by executing

<pre>
$python -i tb_HelloProxy
>>>prepare()
>>>run(0, 10000000, verbose=False)
</pre>

you should get an output similar to

<pre>
[SYSCALL] BRK ptr:0xC0000 -> brk:0xC0000
[SYSCALL] BRK ptr:0xC0000 -> brk:0xC0AF8
[SYSCALL] SET TID ADDRESS fd:0xC00D0
[SYSCALL] SET ROBUST LIST ADDRESS head:0xC00E0 len:24
[SYSCALL] PRLIMIT64 resource:0x0 rlimit:0x3
[SYSCALL] READLINKAT dirfd:0xFFFFFFFFFFFFFF9C path:/proc/self/exe buf:0x9EE90 busize:4096
[SYSCALL] GETRANDOM buf:0x7F5C0 buflen:8 flags:0x1
[SYSCALL] BRK ptr:0xC0AF8 -> brk:0xC0AF8
[SYSCALL] BRK ptr:0xC0AF8 -> brk:0xE1AF8
[SYSCALL] BRK ptr:0xE1AF8 -> brk:0xE2000
[SYSCALL] MPROTECT add:0x75000 len:16384 prot:0x1
[SYSCALL] FSTAT fd:0x1 stat:0x9FCB0
[SYSCALL] IOCTL fd:0x1 p1:21505 p2:654376
[SYSCALL] WRITE fd:0x1 buf:0xC0FD0 count:0xD
[SYSCALL] EXIT GROUP
</pre>