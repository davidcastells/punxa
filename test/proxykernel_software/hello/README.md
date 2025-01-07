# Hello World

This is a classic Hello World app.

### Compiling

We use the baremetal RISC-V gcc compiler (riscv64-unknown-elf-gcc)

```
make
```


### Testing with Single Cycle Processor Model

You can run 

```
python -i tb_HelloProxy.py
```

then 

```
prepare()
step(3000)
console()
```

or, in a more compact way

```
runHello()
```



### Testing with Microprogrammed Processor Model

```
python -i tb_HelloProxy.py
```

then 

```
prepare('up')
step(3000)
console()
```

or, in a more compact way

```
runHello('up')
```

Simulation time is increased (by a factor $72.7\times$ ) due to two factors: 1) a lower simulation speed because of the higher circuit complexity 2) A higher number of cycles per instruction due to the microprogrammed architecture

