all: hello_64.elf hello_32.elf

disasm: hello_64.disasm hello_32.disasm

clean:
	rm hello_??.elf
	rm hello_??.disasm

hello_64.elf: hello.c
	riscv64-unknown-elf-gcc hello.c -o hello_64.elf

hello_64.disasm: hello_64.elf
	riscv64-unknown-elf-objdump -d hello_64.elf > hello_64.disasm

hello_32.elf: hello.c
	riscv32-unknown-elf-gcc hello.c -o hello_32.elf

hello_32.disasm: hello_32.elf
	riscv32-unknown-elf-objdump -d hello_32.elf > hello_32.disasm
	
run_spike_64:
	 spike pk hello_64.elf

run_qemu_64:
	qemu-riscv64 hello_64.elf

run_punxa_64:
	python3 tb_HelloProxy.py -c "runHello()"
