all: hamming_64.elf hamming_ci_64.elf hamming_32.elf

disasm: hamming_64.disasm hamming_ci_64.disasm hamming_32.disasm

clean:
	rm hamming_*.elf
	rm hamming_*.disasm

hamming_64.elf: hamming.c
	riscv64-unknown-elf-gcc -march=rv64gc -mabi=lp64d -falign-functions=8 -falign-jumps=8 -falign-loops=8 hamming.c -o hamming_64.elf
	
hamming_ci_64.elf: hamming.c
	riscv64-unknown-elf-gcc -DUSE_CI -march=rv64gc -mabi=lp64d -falign-functions=8 -falign-jumps=8 -falign-loops=8 hamming.c -o hamming_ci_64.elf

hamming_64.disasm: hamming_64.elf
	riscv64-unknown-elf-objdump -d hamming_64.elf > hamming_64.disasm

hamming_ci_64.disasm: hamming_ci_64.elf
	riscv64-unknown-elf-objdump -d hamming_ci_64.elf > hamming_ci_64.disasm

hamming_32.elf: hamming.c
	riscv32-unknown-elf-gcc hamming.c -o hamming_32.elf

hamming_32.disasm: hamming_32.elf
	riscv32-unknown-elf-objdump -d hamming_32.elf > hamming_32.disasm
	
run_spike_64:
	 spike pk hamming_64.elf

run_qemu_64:
	qemu-riscv64 hamming_64.elf

run_punxa_64:
	python3 tb_HammingProxy.py -c "runHamming()"
