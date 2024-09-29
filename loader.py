import ctypes

class Elf64_Ehdr(ctypes.Structure):
    _fields_ = [
        ("e_ident", ctypes.c_ubyte * 16),
        ("e_type", ctypes.c_uint16),
        ("e_machine", ctypes.c_uint16),
        ("e_version", ctypes.c_uint32),
        ("e_entry", ctypes.c_uint64),
        ("e_phoff", ctypes.c_uint64),
        ("e_shoff", ctypes.c_uint64),
        ("e_flags", ctypes.c_uint32),
        ("e_ehsize", ctypes.c_uint16),
        ("e_phentsize", ctypes.c_uint16),
        ("e_phnum", ctypes.c_uint16),
        ("e_shentsize", ctypes.c_uint16),
        ("e_shnum", ctypes.c_uint16),
        ("e_shstrndx", ctypes.c_uint16)
    ]


class Elf64_Phdr(ctypes.Structure):
    _fields_ = [
        ("p_type", ctypes.c_uint32),
        ("p_flags", ctypes.c_uint32),
        ("p_offset", ctypes.c_uint64),
        ("p_vaddr", ctypes.c_uint64),
        ("p_paddr", ctypes.c_uint64),
        ("p_filesz", ctypes.c_uint64),
        ("p_memsz", ctypes.c_uint64),
        ("p_align", ctypes.c_uint64),
    ]


PT_LOAD = 1
PF_X    = 0x1 
PF_W    = 0x2
PF_R    = 0x4

if __name__ == "__main__":
    elf_header = Elf64_Ehdr()
    
    elf_header.e_ident[:4] = b"\x7fELF"
    elf_header.e_ident[4]  = 2 # EI_CLASS ELFCLASS64
    elf_header.e_ident[5]  = 1 # EI_DATA (little endian)
    elf_header.e_ident[6]  = 1 # EI_VERSION 
    elf_header.e_ident[7]  = 0 # EI_ABI
    elf_header.e_ident[8]  = 0 # EI_ABIVERSION

    elf_header.e_type      = 2  # ET_EXEC
    elf_header.e_machine   = 62 # EM_X86_64
    elf_header.e_version   = 1  # Current version (always 1)
    elf_header.e_entry     = 0x401000
    elf_header.e_phoff     = 0x40
    elf_header.e_shoff     = 0x0 
    elf_header.e_flags     = 0x0 
    elf_header.e_ehsize    = ctypes.sizeof(Elf64_Ehdr) 
    elf_header.e_phentsize = ctypes.sizeof(Elf64_Phdr)
    elf_header.e_phnum     = 2
    elf_header.e_shentsize = 0 
    elf_header.e_shnum     = 0
    elf_header.e_shstrndx  = 0
    
    text_segment_header = Elf64_Phdr()
    data_segment_header = Elf64_Phdr()

    data_segment = b"" 
    text_segment = b""

    header = Elf64_Ehdr() 
    with open("elf", "rb") as elf_file:
        data = elf_file.read(ctypes.sizeof(Elf64_Ehdr))
        ctypes.memmove(ctypes.addressof(header), data, ctypes.sizeof(Elf64_Ehdr))
        elf_file.seek(header.e_phoff)

        for i in range(header.e_phnum):
            ph_hdr = Elf64_Phdr()
            ctypes.memmove(ctypes.addressof(ph_hdr), elf_file.read(header.e_phentsize), header.e_phentsize)
            
            # Find the text/code segment and load it into text_segment
            if (ph_hdr.p_type == PT_LOAD and (ph_hdr.p_flags & (PF_R | PF_X) == (PF_R | PF_X)) ):
                current = elf_file.tell()
                elf_file.seek(ph_hdr.p_offset)
                text_segment = elf_file.read(ph_hdr.p_filesz)
                elf_file.seek(current)
           
            # Find the data segment and load it into data_segment
            if (ph_hdr.p_type == PT_LOAD and (ph_hdr.p_flags & (PF_R | PF_W) == (PF_R | PF_W))):
                current = elf_file.tell()
                elf_file.seek(ph_hdr.p_offset)
                data_segment = elf_file.read(ph_hdr.p_filesz)
                elf_file.seek(current)

    text_segment_header.p_type   = PT_LOAD   
    text_segment_header.p_flags  = PF_X | PF_R 
    text_segment_header.p_offset = 0x1000 
    text_segment_header.p_vaddr  = 0x401000 
    text_segment_header.p_paddr  = 0x401000
    text_segment_header.p_filesz = len(text_segment)
    text_segment_header.p_memsz  = len(text_segment)
    text_segment_header.p_align  = 0x1000

    data_segment_header.p_type   = PT_LOAD   
    data_segment_header.p_flags  = PF_W | PF_R
    data_segment_header.p_offset = 0x2000 
    data_segment_header.p_vaddr  = 0x402000 
    data_segment_header.p_paddr  = 0x402000
    data_segment_header.p_filesz = len(data_segment)
    data_segment_header.p_memsz  = len(data_segment)
    data_segment_header.p_align  = 0x1000

    with open("pyelf", "wb") as file:
        file.write(elf_header)
        file.write(text_segment_header)
        file.write(data_segment_header)
        file.seek(0x1000)
        file.write(text_segment)
        file.seek(0x2000)
        file.write(data_segment)
    
    print("Created new elf file")
