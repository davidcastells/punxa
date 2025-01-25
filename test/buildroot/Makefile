help:
	@echo "Make options:"
	@echo "  make clean_checkpoint -> cleans the checkpointed files"
	@echo "  make vmlinux.sym -> creates the linux symbols file"

clean_checkpoint:
	rm -fr checkpoint.dat
	rm -fr opensbi.dat
	rm -fr opensbi.json
	rm -fr opensbi.json.gz

vmlinux.sym:buildroot-2024.02.10/output/build/linux-6.1.44/vmlinux
	buildroot-2024.02.10/output/host/bin/riscv64-linux-objdump  -t buildroot-2024.02.10/output/build/linux-6.1.44/vmlinux > vmlinux.sym
	
linkconfig:
	cd buildroot-2024.02.10/output/build/linux-6.1.44/arch/riscv/configs/ && \
	ln -s ../../../../../../configs/punxa_rv64_linux_defconfig .

linkdevicetree:
	cd buildroot-2024.02.10/output/build/linux-6.1.44/arch/riscv/boot/dts/punxa && \
	ln -s ../../../../../../../../../punxa_rv64.dts  .

saveconfig:
	cp buildroot-2024.02.10/.config punxa_rv64_defconfig
	cp buildroot-2024.02.10/output/build/linux-6.1.44/.config punxa_rv64_linux_defconfig


