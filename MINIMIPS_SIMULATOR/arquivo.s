# Programa de teste completo para o MiniMIPS
.data
mensagem_inicial: .asciiz "Iniciando teste do processador..."
valor_x:          .word   15
valor_y:          .word   7

.text
# Imprime a mensagem inicial
addi $v0, $zero, 4
la   $a0, mensagem_inicial
syscall

add $a0, $a0, $t0
addi $v0, $zero, 1
syscall

# Testa operações aritméticas
add  $t3, $t1, $t2     # $t3 = 15 + 7 = 22
sub  $t0, $t1, $t2     # $t0 = 15 - 7 = 8 (reutilizando $t0)
mult $t1, $t2          # $LO = 15 * 7 = 105, $HI = 0

# Testa operações lógicas e de shift
addi $t0, $zero, 12    # $t0 = 12 (binário: 1100)
addi $a0, $zero, 10    # $a0 = 10 (binário: 1010)
and  $t1, $t0, $a0     # $t1 = 12 & 10 = 8 (binário: 1000)
or   $t2, $t0, $a0     # $t2 = 12 | 10 = 14 (binário: 1110)
sll  $t3, $a0, 2       # $t3 = 10 << 2 = 40

addi $sp, $sp, -4
sw $t1, 4($sp)

# Salva um resultado na memória e o imprime
sw   $t3, 0($sp)       # Salva 40 no topo da pilha (memoria[255])
lw   $a0, 0($sp)       # Carrega 40 em $a0 para impressão
addi $v0, $zero, 1     # Syscall para imprimir inteiro
syscall




lw $t1, 4($sp)

