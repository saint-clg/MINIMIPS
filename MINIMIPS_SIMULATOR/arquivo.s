addi $t0, $t1, 100


add $a0, $a0, $t0
addi $v0, $zero, 1
syscall



addi $sp, $sp, -4
sw $t1, 4($sp)





lw $t1, 4($sp)

