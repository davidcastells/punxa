all: hello_64.elf

disasm: hello.disasm

clean:
	rm hello_64.elf
	rm hello_64.disasm

hello_64.elf: hello.c
	riscv64-unknown-elf-gcc  -e _startup startup.S kernel.c hello.c -o hello_64.elf

hello_32.elf: hello.c
	riscv32-unknown-elf-gcc  -e _startup startup.S kernel.c hello.c -o hello_32.elf

hello_64.disasm: hello_64.elf
	riscv64-unknown-elf-objdump -d hello_64.elf > hello_64.disasm

run_spike:
	 spike pk hello.elf

run_qemu:
	qemu-riscv64 hello.elf

run_punxa:
	python3 tb_HelloProxy.py -c "runHello()"
