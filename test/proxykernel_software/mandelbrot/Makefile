CC = riscv64-unknown-elf-g++
CC_FLAGS=-DLINUX -O2 -g
LINK=$(CC) -o $@  $< 
OBJDUMP = riscv64-unknown-elf-objdump

EXEC = mandelbrot.elf
DISASM = mandelbrot.disasm

SOURCES = mandelbrot.c 
	

OBJECTS = $(SOURCES:.cpp=.o)

$(EXEC): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(EXEC)

# To obtain object files
%.o: %.cpp
	$(CC) -c $(CC_FLAGS) $< -o $@


all: $(EXEC)
	
disasm: $(EXEC)
	$(OBJDUMP) $(EXEC) -d > $(DISASM)

clean:
	rm -f $(EXEC) $(OBJECTS)

run_spike:
	spike pk $(EXEC) -m -o eclair.jpg -t

run_qemu:
	qemu-riscv64 $(EXEC) -m -o eclair.jpg -t -v

run_punxa:
	python3 tb_JpegEnc.py -c "runJpegEnc()"
