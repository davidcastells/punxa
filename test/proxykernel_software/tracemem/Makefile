all: tracemem.elf

disasm: tracemem.disasm

clean:
	rm tracemem.elf
	rm tracemem.disasm

tracemem.elf: tracemem.c
	riscv64-unknown-elf-gcc tracemem.c -o tracemem.elf

tracemem.disasm: tracemem.elf
	riscv64-unknown-elf-objdump -d tracemem.elf > tracemem.disasm

#run_spike:
#	 spike pk hello.elf

#run_qemu:
#	qemu-riscv64 hello.elf

run_punxa:
	python3 tb_TraceMem.py -c "runTraceMem()"
