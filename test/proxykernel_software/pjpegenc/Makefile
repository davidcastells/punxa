CC = riscv64-unknown-elf-g++
CC_FLAGS=-DLINUX -O2 -g
LINK=$(CC) -o $@  $< 
OBJDUMP = riscv64-unknown-elf-objdump

EXEC = pjpegenc_baseline.elf
DISASM = pjpegenc_baseline.disasm

SOURCES = main.cpp FileOutputStream.cpp Bitmap.cpp JpegEncoder.cpp DCT.cpp Huffman.cpp \
	JpegInfo.cpp OutputStream.cpp BufferedOutputStream.cpp  \
	ByteArrayOutputStream.cpp PerformanceCounter.cpp \
	SmallEmbeddedImage.cpp
	

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
