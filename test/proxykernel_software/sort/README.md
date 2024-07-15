# Sorting a File #

This test application, reads a text file, sorts the values and writes the sorted values in a output file.

You can execute it with

``` 
python tb_Sort.py  -c "runTest()"
``` 

Or interactivelly with

``` 
python -i tb_Sort.py
>>>prepare()
>>>step(22776)
>>>console()
```


The input file content is 

```
Banana
Apple
Orange
Grapes
Pineapple
Watermelon
Cherry
Strawberry
Blueberry
Mango
Peach
Apricot
Blackberry
Raspberry
Cantaloupe
Kiwi
Lemon
Lime
Papaya
Plum
```
The sorted output file is

```
Apple
Apricot
Banana
Blackberry
Blueberry
Cantaloupe
Cherry
Grapes
Kiwi
Lemon
Lime
Mango
Orange
Papaya
Peach
Pineapple
Plum
Raspberry
Strawberry
Watermelon
```


As in the hello world application, you can inspect the invoked syscalls.
You should get something similar to the following list... 

<pre>
[SYSCALL] BRK ptr:0x190000 -> brk:0x190000
[SYSCALL] BRK ptr:0x190000 -> brk:0x190AF8
[SYSCALL] SET TID ADDRESS fd:0x1900D0
[SYSCALL] SET ROBUST LIST ADDRESS head:0x1900E0 len:24
[SYSCALL] PRLIMIT64 resource:0x0 rlimit:0x3
[SYSCALL] READLINKAT dirfd:0xFFFFFFFFFFFFFF9C path:/proc/self/exe buf:0x14EE90 busize:4096
[SYSCALL] GETRANDOM buf:0x855C0 buflen:8 flags:0x1
[SYSCALL] BRK ptr:0x190AF8 -> brk:0x190AF8
[SYSCALL] BRK ptr:0x190AF8 -> brk:0x1B1AF8
[SYSCALL] BRK ptr:0x1B1AF8 -> brk:0x1B2000
[SYSCALL] MPROTECT add:0x7A000 len:20480 prot:0x1
[SYSCALL] FSTAT fd:0x1 stat:0x14DBD0
[SYSCALL] IOCTL fd:0x1 p1:21505 p2:1366856
[SYSCALL] WRITE fd:0x1 buf:0x190FD0 count:0x39
[SYSCALL] OPENAT dirfd:18446744073709551516 input.txt f:0x0 m:0x0  fileno() = 4
[SYSCALL] FSTAT fd:0x4 stat:0x14DD20
[SYSCALL] WRITE fd:0x1 buf:0x190FD0 count:0x13
[SYSCALL] FSTAT fd:0x4 stat:0x14DB70
[SYSCALL] READ fd:0x4 buf:0x1931C0 count:0x2000
[SYSCALL] READ fd:0x4 buf:0x1931C0 count:0x2000
[SYSCALL] CLOSE fd:0x4
[SYSCALL] OPENAT dirfd:18446744073709551516 output.txt f:0x241 m:0x1B6  fileno() = 4
[SYSCALL] FSTAT fd:0x4 stat:0x14DBD0
[SYSCALL] WRITE fd:0x4 buf:0x1931C0 count:0x9D
[SYSCALL] CLOSE fd:0x4
[SYSCALL] WRITE fd:0x1 buf:0x190FD0 count:0x27
[SYSCALL] EXIT GROUP
</pre>



