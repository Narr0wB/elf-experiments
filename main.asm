section .data
    my_string db "Hello world! i am a string in the data section!", 0

section .text
    global _start

_start: 
    mov rax, 1
    mov rdi, 1
    mov rsi, my_string 
    mov rdx, 0x30
    syscall

    mov rax, 0x3C
    mov rdi, 0
    syscall

