# teste_completo.s
# Testa a maioria das instruções implementadas no simulador.
# Pseudo-instruções foram trocadas por instruções base.

.data
msg_add: .asciiz "Resultado ADD (15 + 5): "
msg_sub: .asciiz "\nResultado SUB (15 - 5): "
msg_mult: .asciiz "\nResultado MULT (15 * 5) em $LO: "
msg_and: .asciiz "\nResultado AND (t0=15 & t1=5): "
msg_or: .asciiz "\nResultado OR (t0=15 | t1=5): "
msg_sll: .asciiz "\nResultado SLL (t0 << 2): "
msg_slt: .asciiz "\nResultado SLT (15 < 5 -> false): "
msg_slti: .asciiz "\nResultado SLTI (t0 < 20 -> true): "
msg_lui: .asciiz "\nResultado LUI (Carrega 255 nos 16 bits mais altos): "

.text
    # Inicia os registradores
    addi $t0, $zero, 15
    addi $t1, $zero, 5

    # --- Teste ADD ---
    add $t2, $t0, $t1       # t2 = 15 + 5 = 20
    la $a0, msg_add
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall

    # --- Teste SUB ---
    sub $t2, $t0, $t1       # t2 = 15 - 5 = 10
    la $a0, msg_sub
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall

    # --- Teste MULT ---
    mult $t0, $t1           # HI:LO = 15 * 5 = 75
    la $a0, msg_mult
    addi $v0, $zero, 4
    syscall
    add $a0, $LO, $zero     # mflo $a0
    addi $v0, $zero, 1
    syscall

    # --- Teste AND ---
    and $t2, $t0, $t1       # t2 = 15 & 5 = 5
    la $a0, msg_and
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall

    # --- Teste OR ---
    or $t2, $t0, $t1        # t2 = 15 | 5 = 15
    la $a0, msg_or
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall
    
    # --- Teste SLL ---
    sll $t2, $t0, 2         # t2 = 15 << 2 = 60
    la $a0, msg_sll
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall
    
    # --- Teste SLT ---
    slt $t2, $t0, $t1       # t2 = (15 < 5) ? 1 : 0.  Resultado: 0
    la $a0, msg_slt
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall
    
    # --- Teste SLTI ---
    slti $t2, $t0, 20       # t2 = (15 < 20) ? 1 : 0. Resultado: 1
    la $a0, msg_slti
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall
    
    # --- Teste LUI ---
    lui $t2, 255            # t2 = 255 << 16
    la $a0, msg_lui
    addi $v0, $zero, 4
    syscall
    add $a0, $t2, $zero     # move $a0, $t2
    addi $v0, $zero, 1
    syscall

    # --- Fim do Programa ---
    addi $v0, $zero, 10
    syscall