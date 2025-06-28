#               (VÁRIAVEIS PARA A SIMULAR OS REGISTRADORES E INSTRUÇÕES)

# O vetor memória simula a pilha, podendo ser carregado em até 256 valores
memoria = [0] * 256 

# Vetor de registradores
# Fizemos uma simplificação, diminuindo a quantidade de registradores para apenas 10
# Aqui será salvo cada valor para os registradores, com excessão de sp
vetor_reg = [0] * 10 # $zero, $v0, $a0, $t0-$t3, $sp, $HI, $LO


# O vetor de índice 7 representa o $sp
# Neste vetor ele irá salvar uma "posição" na memória, para simular a pilha
# Nada mais é que um índice que indica uma posição no vetor memória
# Começa apontando para o último índice e precisa ser "subtraido" para abrir espaço na pilha
vetor_reg[7] = len(memoria) - 1 # "Len(memoria)" retorna o tamanho do vetor memória em python

# Um dicionário para ler os registradores que o .s nos enviar
# Cada instrução retorna um número que a posição do registrador no vetor de registradores
# Basicamente simulando um endereço para a memória onde fica armazenado seu valor
reg_dic = {
    "$zero": 0,
    "$v0": 1,
    "$a0": 2,
    "$t0": 3,
    "$t1": 4,
    "$t2": 5,
    "$t3": 6,
    "$sp": 7,
    "$HI": 8, # Usado em mult quando ultrapassar os 32bits para armazenar seus 16 bist mais sign
    "$LO": 9  # Usado em mult quando ultrapassar os 32bits para armazenar seus 16 bits menos sign
}

# LEMBRAR: Não esquecer de pesquisar como funcionam os regs $HI e $LO

# DICIONÁRIO DE CONTROLE ---- (prestar atenção para não esquecer)

# Control: [RegDst, ALUSrc, MemToReg, RegWrite, MemRead, MemWrite]
# ALUSrc: 0=Reg, 1=Imediato
# MemToReg: 0=ALUResult, 1=MemData
# RegWrite: 1=Escreve no registrador
# MemRead/Write: 1=Lê/Escreve na memória

inst_dic = {
    #               [ALUSrc, MemToReg, RegWrite, MemRead, MemWrite]
    "add":   [0, 0, 1, 0, 0],
    "addi":  [1, 0, 1, 0, 0],
    "sub":   [0, 0, 1, 0, 0],
    "mult":  [0, 0, 1, 0, 0],
    "and":   [0, 0, 1, 0, 0],
    "or":    [0, 0, 1, 0, 0],
    "sll":   [1, 0, 1, 0, 0], 
    "lw":    [1, 1, 1, 1, 0], 
    "sw":    [1, 0, 0, 0, 1],
    "lui":   [1, 0, 1, 0, 0],
    "slt":   [0, 0, 1, 0, 0],
    "slti":  [1, 0, 1, 0, 0], 
    "syscall": [0, 0, 0, 0, 0] 
}

# --- VARIÁVEIS DE ESTADO DO SIMULADOR ---
file_path = "MINIMIPS_SIMULATOR\\arquivo.s" # Simplifiquei o path para o exemplo
PC = 0 # Program Counter
EPC = 0 # EPC 
CAUSE = 0 # CAUSE

# --- FUNÇÕES DO SIMULADOR ---

def matriz_program(file_path):
    """Lê um arquivo .s e o transforma em uma matriz de instruções."""
    matriz = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            linhas = f.read().splitlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
        return None

    linhas = [linha for linha in linhas if linha.strip() != '' and not linha.strip().startswith('#')]

    for linha in linhas:
        partes = linha.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
        #A linha de cima trata as linhas da matriz
        # - Tira as vírgulas
        # - Transforma 4($sp) em "4" "$sp", lembrar disso
        matriz.append(partes)
    return matriz

def decode_execute(instrucao, PC):
    """Decodifica e executa uma instrução. Retorna o novo PC."""
    global vetor_reg, memoria, programa # Permite modificar todas as variáveis de estado

    opcode = instrucao[0]
    if opcode not in inst_dic:
        print(f"Erro na linha {PC+1}: Instrução '{opcode}' desconhecida.")
        return PC + 1

    # --- Instruções do Tipo-R (operam entre registradores) ---
    if opcode in ["add", "sub", "and", "or", "slt"]:
        reg_dst_nome = instrucao[1]
        reg_src1_nome = instrucao[2]
        reg_src2_nome = instrucao[3]
        
        idx_dst = reg_dic[reg_dst_nome]
        val_src1 = vetor_reg[reg_dic[reg_src1_nome]]
        val_src2 = vetor_reg[reg_dic[reg_src2_nome]]
        
        resultado = 0
        if opcode == "add":
            resultado = val_src1 + val_src2
        elif opcode == "sub":
            resultado = val_src1 - val_src2
        elif opcode == "and":
            resultado = val_src1 & val_src2 # CORRIGIDO: Bitwise AND
        elif opcode == "or":
            resultado = val_src1 | val_src2 # CORRIGIDO: Bitwise OR
        elif opcode == "slt":
            resultado = 1 if val_src1 < val_src2 else 0

        # Write-Back para instruções R-Type padrão
        if idx_dst != 0:
            vetor_reg[idx_dst] = resultado

    # --- Instruções de Multiplicação e Divisão (caso especial) ---
    elif opcode in ["mult", "div"]:
        # Sintaxe: mult $rs, $rt. Não usam $rd.
        reg_src1_nome = instrucao[1]
        reg_src2_nome = instrucao[2]
        val_src1 = vetor_reg[reg_dic[reg_src1_nome]]
        val_src2 = vetor_reg[reg_dic[reg_src2_nome]]

        if opcode == "mult":
            # CORRIGIDO: mult armazena o resultado de 64 bits em $HI e $LO
            resultado_64bits = val_src1 * val_src2
            vetor_reg[reg_dic["$LO"]] = resultado_64bits & 0xFFFFFFFF # Pega os 32 bits de baixo
            vetor_reg[reg_dic["$HI"]] = resultado_64bits >> 32      # Pega os 32 bits de cima

    # --- Instruções de Shift (caso especial de formato) ---
    elif opcode == "sll":
        # Sintaxe: sll $rd, $rt, shamt
        reg_dst_nome = instrucao[1]
        reg_src_nome = instrucao[2] # Este é o $rt
        shamt = int(instrucao[3])   # Este é o shift amount

        idx_dst = reg_dic[reg_dst_nome]
        val_src = vetor_reg[reg_dic[reg_src_nome]]
        
        # CORRIGIDO: Usa o operador de bitwise shift-left
        resultado = val_src << shamt
        
        if idx_dst != 0:
            vetor_reg[idx_dst] = resultado

    # --- Instruções do Tipo-I (operam com um valor imediato) ---
    elif opcode in ["addi", "slti", "lui"]:
        reg_dst_nome = instrucao[1]
        idx_dst = reg_dic[reg_dst_nome]

        if opcode == "lui":
            # Sintaxe: lui $rt, imediato
            imediato = int(instrucao[2]) # LUI só tem 2 operandos
            # CORRIGIDO: Carrega o imediato nos 16 bits de CIMA
            resultado = imediato << 16
        else: # addi, slti
            reg_src_nome = instrucao[2]
            imediato = int(instrucao[3])
            val_src = vetor_reg[reg_dic[reg_src_nome]]
            
            if opcode == "addi":
                resultado = val_src + imediato
            elif opcode == "slti":
                resultado = 1 if val_src < imediato else 0

        # Write-Back para instruções I-Type
        if idx_dst != 0:
            vetor_reg[idx_dst] = resultado

    # --- Instruções de Memória (Load/Store) ---
    elif opcode in ["lw", "sw"]:
        reg_src_name = instrucao[1]
        offset = int(instrucao[2])
        reg_base_nome = instrucao[3]

        endereco_memoria = offset + vetor_reg[reg_dic[reg_base_nome]]

        if not (0 <= endereco_memoria < len(memoria)):
            print(f"ERRO: Acesso a endereço de memória inválido ({endereco_memoria}) na linha {PC + 1}")
        else:
            if opcode == "lw":
                # Carrega DA memória PARA o registrador
                vetor_reg[reg_dic[reg_src_name]] = memoria[endereco_memoria]
            elif opcode == "sw":
                # Armazena DE um registrador PARA a memória
                if reg_src_name in reg_dic:
                    memoria[endereco_memoria] = vetor_reg[reg_dic[reg_src_name]]
                else:
                    imediato = int(reg_src_name)
                    memoria[endereco_memoria] = imediato
    # --- Chamadas de Sistema ---
    elif opcode == "syscall":
        call_code = vetor_reg[reg_dic["$v0"]]
        
        if call_code == 1: # Imprimir Inteiro (Padrão MIPS)
            print(f"Saída do Sistema: {vetor_reg[reg_dic['$a0']]}")
        elif call_code == 4: # Imprimir String (Não exigido, mas exemplo)
            # A ser implementado: ler da memória a partir do endereço em $a0
            print("Syscall 4 (imprimir string) não implementado.")
        elif call_code == 10: # Sair (Padrão MIPS)
            print("--- Syscall: Fim da Execução ---")
            return len(programa) # Pula o PC para o final para parar o loop
        else:
            print(f"ERRO: Syscall com código desconhecido ({call_code}) na linha {PC + 1}.")

    # --- Manutenção do Processador ---
    vetor_reg[0] = 0 # Garante que $zero seja sempre 0
    
    # Atualiza o PC para a próxima instrução (não se aplica a saltos e desvios)
    return PC + 1


# --- CICLO PRINCIPAL DE EXECUÇÃO ---

programa = matriz_program(file_path)

if programa:
    print("--- INÍCIO DA SIMULAÇÃO ---")
    print(f"Estado inicial dos registradores: {vetor_reg}\n")
    
    # Loop de execução
    while PC < len(programa):
        instrucao_atual = programa[PC]
        print(f"PC={PC}: Executando -> {' '.join(instrucao_atual)}")
        
        PC = decode_execute(instrucao_atual, PC)
        
        # Imprime o estado após a instrução (para depuração)
        print(f"  Registradores: $v0={vetor_reg[reg_dic['$v0']]} $a0={vetor_reg[reg_dic['$a0']]} $t0={vetor_reg[reg_dic['$t0']]} $t1={vetor_reg[reg_dic['$t1']]}")
        print("-" * 20)

    print("--- FIM DA SIMULAÇÃO ---")
    print(f"Estado final dos registradores: {vetor_reg}")
