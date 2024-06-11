CC = riscv64-unknown-elf-g++
CC_FLAGS=-DNOPAUSE -O2 -g
LINK=$(CC) -o $@  $< 
OBJDUMP = riscv64-unknown-elf-objdump

EXEC = paranoia.elf
DISASM = paranoia.disasm

SOURCES=paranoia.c 
	

OBJECTS=$(SOURCES:.c=.o)

$(EXEC): $(OBJECTS)
	$(CC) $(OBJECTS) -D NOPAUSE -o $(EXEC)

# To obtain object files
%.o: %.c
	$(CC) -c $(CC_FLAGS) $< -o $@


all: $(EXEC)

host:
	@$(MAKE) clean_host
	@$(MAKE) CC=gcc EXEC=paranoia.host all
	
disasm: $(EXEC)
	$(OBJDUMP) $(EXEC) -d > $(DISASM)

clean:
	rm -f $(EXEC) $(OBJECTS) 

clean_host:
	rm -f $(OBJECTS) paranoia.host

run_spike: $(EXEC)
	spike pk $(EXEC) 

run_qemu: $(EXEC)
	qemu-riscv64 $(EXEC) 

run_punxa: $(EXEC)
	python3 tb_Paranoia.py -c "runParanoia()"

