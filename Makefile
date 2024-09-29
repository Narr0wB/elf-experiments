
all:
	nasm -f elf64 -o elf.o main.asm
	ld elf.o -o elf
	rm elf.o
	python3 loader.py
	chmod a+x pyelf
