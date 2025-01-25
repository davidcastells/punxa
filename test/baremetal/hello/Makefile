all: compile disasm

compile: hello_64.elf hello_32.elf

disasm: hello_32.disasm hello_64.disasm

clean:
	rm -f hello_32.elf
	rm -f hello_64.elf
	rm -f hello_32.disasm
	rm -f hello_64.disasm

hello_64.elf: hello.c
	riscv64-unknown-elf-gcc  -e _startup startup.S kernel.c hello.c -o hello_64.elf

hello_32.elf: hello.c
	riscv32-unknown-elf-gcc  -e _startup startup.S kernel.c hello.c -o hello_32.elf

hello_64.disasm: hello_64.elf
	riscv64-unknown-elf-objdump -d hello_64.elf > hello_64.disasm

hello_32.disasm: hello_32.elf
	riscv32-unknown-elf-objdump -d hello_32.elf > hello_32.disasm

run_spike:
	 spike pk hello.elf

run_qemu:
	qemu-riscv64 hello.elf

run_punxa:
	python3 tb_HelloProxy.py -c "runHello()"
