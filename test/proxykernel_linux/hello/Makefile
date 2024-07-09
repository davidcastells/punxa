all: hello.elf

disasm: hello.disasm

clean:
	rm hello.elf
	rm hello.disasm

hello.elf: hello.c
	riscv64-unknown-linux-gnu-gcc -static hello.c -o hello.elf

hello.disasm: hello.elf
	riscv64-unknown-linux-gnu-objdump -d hello.elf > hello.disasm

run_spike:
	 spike pk hello.elf

run_qemu:
	qemu-riscv64 hello.elf

run_punxa:
	python3 tb_HelloProxy.py -c "runHello()"
