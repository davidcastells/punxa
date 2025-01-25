# Hello World

This is a classic Hello World app.
The difference from this implementation compared with the one in proxykernel_software directory is that here we implement a kernel in machine mode that handles some ECALLs.
Actually, our main interest is handling the SYSCAL_WRITE to send characters to the UART model of the system.

The implementation of the syscall_write is very simple, we just have a for loop that sends bytes to the Tx register of the UART. No flow control is used. Since the UART model is behavioural it collects all received bytes that can be displayed by calling the "console()"  interactive command.

### Compiling

We use the baremetal RISC-V gcc compiler (riscv64-unknown-elf-gcc)

```
make
make disasm
```


### Testing with Single Cycle Processor Model

You can run 

```
python -i tb_HelloBaremetal.py
```

then 

```
>>>prepare()
>>>step(2070)
>>>console()
```

or, in a more compact way

```
>>>runHello()
```

You will be able to analyze how exceptions are raised when exeucting the ECALL instruction and how the trap handler calls the appropiate syscall. The trap handler must be implemented as a ***naked** function because we have to provide a manually designed function prolog and epilog to correctly saving registers and returning to the mepc + 4 address by calling MRET.


### Testing with Single Cycle Processor Model with Proxy Kernel

We can analyze how the execution of baremetal application (which provides a kernel implementation) is different when executed in the proxy kernel version of the processor. 

```
python -i tb_HelloBaremetal.py
```

then 

```
>>>prepare('scpk')
>>>step(2070)
>>>console()
```

or, in a more compact way

```
>>>runHello('scpk')
```

In this case less instructions are executed since the trap handler is not actually called as ECALL is intercepted by the proxy kernel processor and its appropiate functionality is provided by the host.
Simulation also stops earlier when syscall_exit is handled.

## Supported configurations

We support various configurations. We can use the single cycle processor, for 64 bits or 32 bits, and without and with proxy kernel. The following table describes the tested combinations so far.

<table>  
  <thead><tr><td>Processor Model</td><td>Configuration string</td><td>Result</td></tr></thead>
  <tr><td>Single Cycle 64 bits</td><td>sc<td>OK</td></tr>
  <tr><td>Single Cycle 64 bits with Proxy Kernel</td><td>scpk<td>OK</td></tr>
  <tr><td>Microprogramed 64 bits</td><td>up<td>OK</td></tr>
  <tr><td>Microprogramed 64 bits with Proxy Kernel</td><td>uppk<td>Not working yet</td></tr>
  <tr><td>Single Cycle 32 bits</td><td>sc32<td>OK</td></tr>
  <tr><td>Single Cycle 32 bits with Proxy Kernel</td><td>sc32pk<td>Not supported yet</td></tr>
  <tr><td>Microprogramed 32 bits</td><td>up32<td>OK</td></tr>
  <tr><td>Microprogramed 32 bits with Proxy Kernel</td><td>up32pk<td>Not supported yet</td></tr>
  
</table>


