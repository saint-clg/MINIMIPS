# teste_memoria.s
# Demonstra o uso da memória (.data), da pilha ($sp) e da data_table.
# Pseudo-instruções foram trocadas por instruções base.

.data
minha_string: .asciiz "Ola, mundo da memoria MIPS!"
meu_vetor:    .word   100, 200, 300, 400

msg_valor_vetor: .asciiz "\nValor lido do vetor (indice 2): "
msg_valor_pilha: .asciiz "\nValor desempilhado: "

.text
    # 1. Imprime a string da seção .data
    la $a0, minha_string
    addi $v0, $zero, 4
    syscall

    # 2. Carrega um valor do vetor na memória
    la $t0, meu_vetor      
    lw $t1, 2($t0)         
    
    la $a0, msg_valor_vetor
    addi $v0, $zero, 4
    syscall
    add $a0, $t1, $zero    # move $a0, $t1
    addi $v0, $zero, 1
    syscall

    # 3. Empilha um valor
    addi $sp, $sp, -1      
    addi $t2, $zero, 999   
    sw $t2, 0($sp)         

    # 4. Desempilha o valor para outro registrador
    lw $t3, 0($sp)         
    addi $sp, $sp, 1       

    la $a0, msg_valor_pilha
    addi $v0, $zero, 4
    syscall
    add $a0, $t3, $zero    # move $a0, $t3
    addi $v0, $zero, 1
    syscall

    # Fim do programa
    addi $v0, $zero, 10
    syscall