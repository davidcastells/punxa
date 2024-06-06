CC = riscv64-unknown-elf-g++
CC_FLAGS=-DLINUX -O2 -g
LINK=$(CC) -o $@  $< 
OBJDUMP = riscv64-unknown-elf-objdump

EXEC = sort.elf
DISASM = sort.disasm

SOURCES=sort.c 
	

OBJECTS=$(SOURCES:.c=.o)

$(EXEC): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(EXEC)

# To obtain object files
%.o: %.c
	$(CC) -c $(CC_FLAGS) $< -o $@


all: $(EXEC)

host:
	@$(MAKE) clean_host
	@$(MAKE) CC=gcc EXEC=sort.host all
	
disasm: $(EXEC)
	$(OBJDUMP) $(EXEC) -d > $(DISASM)

clean:
	rm -f $(EXEC) $(OBJECTS) output.txt

clean_host:
	rm -f $(OBJECTS) output.txt sort.host

run_spike:
	spike pk $(EXEC) 

run_qemu:
	qemu-riscv64 $(EXEC) 

run_punxa:
	python3 tb_JpegEnc.py -c "runJpegEnc()"
