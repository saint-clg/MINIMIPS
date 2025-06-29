# teste_erros.s
# Contém múltiplos erros para testar a capacidade de detecção do simulador.
# Pseudo-instruções foram trocadas por instruções base.

.data
msg_inicio: .asciiz "Inicio do teste de erros. Varios erros devem ser reportados a seguir."
msg_fim_teste: .asciiz "\nFim do teste de erros."

.text

    addi $v0, $zero, 4
    la $a0, msg_inicio
    syscall

    # Erro 1: Instrução desconhecida
    # O simulador deve reportar que 'fake_inst' não é uma instrução válida.
    fake_inst $t0, $t1, $t2

    # Erro 2: Tentativa de escrita no registrador $zero
    # O simulador deve ignorar esta operação e avisar o usuário.
    addi $zero, $zero, 10

    # Erro 3: Label de dados não encontrada
    # O simulador deve reportar que 'label_inexistente' não está na data_table.
    la $a0, label_inexistente

    # Erro 4: Acesso a endereço de memória inválido
    # O endereço 1024 é maior que o tamanho da memória (256).
    # O simulador deve reportar um erro de acesso à memória.
    lw $t0, 1024($zero)
    
    # Erro 5: Syscall com código desconhecido
    # O código 99 não é implementado (apenas 1, 4, 10).
    # O simulador deve reportar um erro de syscall inválida.
    addi $v0, $zero, 99
    syscall

    # Mensagem final para mostrar que o programa continuou apesar dos erros
    addi $v0, $zero, 4
    la $a0, msg_fim_teste
    syscall
    
    # Termina corretamente
    addi $v0, $zero, 10
    syscall