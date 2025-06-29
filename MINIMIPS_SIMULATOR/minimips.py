#               (VÁRIAVEIS PARA A SIMULAR OS REGISTRADORES E INSTRUÇÕES) 

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
    "la":    [0, 0, 1, 0, 0],
    "syscall": [0, 0, 0, 0, 0]
} 

# --- VARIÁVEIS DE ESTADO DO SIMULADOR ---
file_path = "" # Simplifiquei o path para o exemplo
PC = 0 # Program Counter
EPC = 0 # EPC 
CAUSE = 0 # CAUSE

# FUNÇÕES: 

# --- READ ARQ --- 
# Recebe o arquivo
# Verifica e lê o arquivo
# Separa em Tópicos (.data: .text:)
# Trata linhas vazias e comentários, excluindo e ignorando respectivamente
# Em .data: Separa e armazena endereços na memória a depender da directive (.ascizz ou .word)
# Em .text: Separa as instruções em uma  matriz Programa, onde as colunas são as instruções e reg
# Retorna uma matriz_programa (armazena todas as instruções) e uma data_table (endereços para o vetor memória)
def read_arq(file_path): 
    """ 
    Lê um arquivo .s com seções .data e .text. 

    - Popula a memória global 'memoria' com os dados da seção .data. 
    - Cria uma tabela de símbolos para os rótulos de dados. 
    - Retorna a matriz de instruções da seção .text e a tabela de dados. 
    """ 
    global memoria # Váriavel global para ser modificada pela função

    data_table = {} 
    matriz_programa = [] 
     
    # Ponteiro para o próximo endereço livre na memória de dados. Começa em 0.
    # Sempre começa do indice 0 no vetor memoria
    data_pointer = 0 
    topico_atual = None #   Os tópicos podem ser .data ou . text

    try: 
        with open(file_path, 'r', encoding='utf-8') as f: 
            linhas = f.readlines() 
    except FileNotFoundError: 
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
        # Fazer um código Cause (Não conseguiu ler o arquivo)
        return None, None 

    for linha in linhas: 
        # Tratamento linha a linha, exclui coméntarios e linhas vazias
        linha_limpa = linha.split('#', 1)[0].strip() 

        if not linha_limpa: 
            continue 

        # --- Tópicos --- 
        if linha_limpa == '.data': 
            topico_atual = 'data' 
            continue 
        elif linha_limpa == '.text': 
            topico_atual = 'text' 
            continue 

        # --- Tratamento baseado nos tópicos ---
        # Para .data, preenche data_table 
        # Para .text, preenche a matriz_programa

        # Apartir daqui será criada a data_table (Tabela de dados com endereços para o vetor memoria)
        if topico_atual == 'data': 
            try: 
                # Separa a string em:
                # Label = "Nome da variável que será salva com o endereço na data_table"
                # Resto = "Código que será tratado depois e oque será salvo"
                label, resto = linha_limpa.split(':', 1) 
                # Tratamento de espaços desnecessários
                label = label.strip() 
                # Salva a diretiva e o dado que será armazenado na memória em uma tupla  
                directive_value = resto.strip().split(maxsplit=1) # Só pode separar uma vez, pois só terá um espaço
                # Salva o valor da diretiva, pode ser .asciiz ou .word nesse simulador
                directive = directive_value[0] 
                 
                # Armazena o endereço ATUAL na tabela de dados para este rótulo 
                data_table[label] = data_pointer

                if directive == '.asciiz': 
                    # .ascizz serve para strings, salva a string já ->SEM ASPAS<-
                    str = directive_value[1].strip('"') 
                    for char in str: 
                        # Armazena cada caractere como um byte (seu valor ASCII, com a função ord()) na memória 
                        # Isso acontece para evitar erros no vetor memoria]
                        memoria[data_pointer] = ord(char) 
                        data_pointer += 1 
                    # Adiciona uma 'Flag' para avisar ao código o fim da string
                    memoria[data_pointer] = 0 
                    data_pointer += 1 
                 
                elif directive == '.word': 
                    # .word vai servir para armazenar números inteiros ou caracteres
                    # Você pode armazenar vetores colocando os números ou caracteres entre vírgulas
                    # Cria uma lista com todos os valores separados por ','
                    values = directive_value[1].split(',') 
                    for val in values: 
                        memoria[data_pointer] = int(val.strip()) 
                        data_pointer += 1  

            except Exception as e: 
                print(f"Erro ao processar linha de dados '{linha_limpa}': {e}")
                # Adicionar um CAUSE aq para erros ao ler uma linha 

        # Neste tópico se encontram as instruções
        # Apartir daqui será criada a matriz de instruções
        elif topico_atual == 'text': 
            # Separa a instruçãi em fatias (Slices) já tratadas, cada fatia:
                # Retira as vírgulas 
                # Retira '(' e ')' para instruções do tipo offset($sp)
            slices = linha_limpa.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()

            # Função .append() adiciona um elemento no final da matriz, assim elas se empilham de baixo para cima
            matriz_programa.append(slices) 

    return matriz_programa, data_table 

def decode_execute(instrucao, PC, data_table, programa): 

    """Decodifica e executa uma instrução. Retorna o novo PC.""" 
    global vetor_reg, memoria 

    opcode = instrucao[0] 
    if opcode not in inst_dic: 
        print(f"Erro na linha {PC+1}: Instrução '{opcode}' desconhecida.") 
        return PC + 1 
        # Colocar um CAUSE aqui para Instrução não encontrada

    # --- Instruções Type-R --- 
    # Instruções que usam (RD, RS, RT) nesse formato
    if opcode in ["add", "sub", "and", "or", "slt"]:
        # O nome dos registradores será usado como um valor de endereço para eles no dicionário 
        reg_dst_name = instrucao[1] # RD
        reg_src_name = instrucao[2] # RT
        reg_temp_name = instrucao[3] # RT

        # Salva o índice do registrador destino (Será usado como endereço para altera-lo no vetor_reg) 
        idx_dst = reg_dic[reg_dst_name] 
        
        # Retira o valor dos dicionários tomando como referência o nome dos registradores
        val_src = vetor_reg[reg_dic[reg_src_name]] 
        val_temp = vetor_reg[reg_dic[reg_temp_name]] 
         
        # Sempre reinicia o resultado
        resultado = 0 

        # O nome da instrução será usado como Opcode/funct, nesse caso seria o funct
        if opcode == "add": 
            resultado = val_src + val_temp 
        elif opcode == "sub":
            resultado = val_src - val_temp 
        elif opcode == "and": 
            resultado = val_src & val_temp
        elif opcode == "or": 
            resultado = val_src | val_temp
        elif opcode == "slt": 
            resultado = 1 if val_src < val_temp else 0 

        # O writeBack acontece logo em seguida, verificando primeiramente se o usuário não quer mudar o $zero
        if idx_dst != 0: 
            vetor_reg[idx_dst] = resultado 
        else:
            print(f"REGISTRADOR $zero IDENTIFICADO COMO DESTINO, ERRO AO ALOCAR VALOR")
            # Colocar um CAUSE como erro tentativa de modificação do reg $zero
            # Tratamento: Pulando essa ação e avisando ao usuário na saída

    # MULT
    # É tipo R mas usa apenas (RT, RS) e exige tratamento especial para 64bits
    elif opcode in ["mult"]: 
        reg_src_name = instrucao[1] 
        reg_temp_name = instrucao[2] 
        val_src = vetor_reg[reg_dic[reg_src_name]] 
        val_temp = vetor_reg[reg_dic[reg_temp_name]] 

        if opcode == "mult": 
            # Mult usa os registradores especiais HI e LO:
                # Motivo, será um valor 64bits
                # HI: Salva os 32bits mais significativos
                # LO: Salva os 32bits menos significativos
            resultado_64bits = val_src * val_temp 
            
            # Aplica a máscara (1)x32bits com o &(Comparador Byte a Byte)
            vetor_reg[reg_dic["$LO"]] = resultado_64bits & 0xFFFFFFFF # Pega os 32 bits de baixo

            # 'Empurra' todos os bits para a esquerda 32, restando apenas os 32 primeiros 
            vetor_reg[reg_dic["$HI"]] = resultado_64bits >> 32 # Pega os 32 bits de cima

    # Shift
    # Será tratado separadamente pois exige um Shamt que é um valor imediato que fica no lugar de RT
    elif opcode == "sll": 
        reg_dst_name = instrucao[1] 
        reg_temp_name = instrucao[2]  
        shamt = int(instrucao[3])   # Shamt (Shift-Amount) 

        idx_dst = reg_dic[reg_dst_name] 
        val_temp = vetor_reg[reg_dic[reg_temp_name]] 
         
        # Usa << para deslocar o valor de RT shamt vezes
        resultado = val_temp << shamt 
         
        if idx_dst != 0: 
            vetor_reg[idx_dst] = resultado 

    # --- Instruções Type-I --- 
    # Instruções que vão usar (RT, RS, VALOR IMEDIATO), aqui o registrador RT será o destino
    elif opcode in ["addi", "slti", "lui"]: 
        reg_temp_name = instrucao[1] 
        idx_temp = reg_dic[reg_temp_name]
        resultado = 0

        if opcode == "lui": 
            # Explicação da Função, *Não usamos em sala*:
                # Salva os 16bits mais significativos de um valor imediato, o resto vira 0 
            imediate = int(instrucao[2])
            resultado = imediate << 16 
        else:
            # ELSE: (ADDI OU SLLI), os dois usam (RT, RS, VALOR IMEDIATO) por isso o mesmo tratamento
            reg_src_name = instrucao[2] 
            imediate = int(instrucao[3]) 
            val_src = vetor_reg[reg_dic[reg_src_name]] 
             
            if opcode == "addi": 
                resultado = val_src + imediate 
            elif opcode == "slti": 
                resultado = 1 if val_src < imediate else 0 
 
        if idx_temp != 0: 
            vetor_reg[idx_temp] = resultado 

    # --- Instruções Type-I para memoria --- 
    # Utilizam do vetor memoria
    elif opcode in ["lw", "sw"]:
        reg_temp_name = instrucao[1]
        offset = int(instrucao[2])
        reg_src_name = instrucao[3]

        mem_adress = offset + vetor_reg[reg_dic[reg_src_name]]

        if not (0 <= mem_adress < len(memoria)):
            print(f"ERRO: Acesso a endereço de memória inválido ({mem_adress}) na linha {PC + 1}")
            # Aplicar CAUSE para erro ao acessar endereço de memória inválido
            # Aplicar tratamento, igonarar essa linhar, avisar o usuário e ir para a próxima inst
        else:
            if opcode == "lw":
                if reg_temp_name not in reg_dic:
                    print(f"ERRO DE SINTAXE: 'lw' requer um registrador de destino, mas recebeu '{reg_temp_name}' na linha {PC+1}")
                    # Aplicar CAUSE para registrador de destino para load inválido
                else:
                    vetor_reg[reg_dic[reg_temp_name]] = memoria[mem_adress]
            elif opcode == "sw":
                if reg_temp_name in reg_dic:
                    val_temp = vetor_reg[reg_dic[reg_temp_name]]
                    memoria[mem_adress] = val_temp
                else:
                    try:
                        imediate = int(reg_temp_name)
                        memoria[mem_adress] = imediate
                    except ValueError:
                        print(f"ERRO DE SINTAXE: Operando '{reg_temp_name}' para 'sw' não é um registrador válido nem um número inteiro na linha {PC+1}")
                        # Aplicar CAUSE para valor de alocação para a memória inválido

    # --- LOAD ADRESS ---
    # Caso especial nescessário, mexe com o data_table que armazena endereços do vetor memoria
    elif opcode == "la":  
        reg_temp_name = instrucao[1] 
        label_name = instrucao[2] 

        # Verifica se a label existe dentro de data_table 
        if label_name in data_table: 
            # Pega o endereço de memória (Índice no vetor memoria) associado à label
            adress = data_table[label_name] 
             
            # Índice de registrador destino (RT neste caso) 
            idx_temp = reg_dic[reg_temp_name] 

            # O registrador (RT) recebe o 'endereço' para a memória
            if idx_temp != 0: 
                vetor_reg[idx_temp] = adress
        else: 
            print(f"ERRO: Etiqueta de dados '{label_name}' não encontrada na linha {PC + 1}.")
            # Aplicar CAUSE, erro ao buscar Label em dados (data_table)

    # --- Syscall --- 
    # Tem o processo mais diferente e sempre acessa os reg ($v0 e $a0)
    elif opcode == "syscall": 

        # Usaremo o reg $v0 para ser o código para nossa chamada:
            # O código da chamada decide que ação a chamada de sistema irá reproduzir
            # Código 1 = Printa o valor inteiro ou a char armazenada em $a0
            # Código 4 = Pinta a string que começa no endereço de memória armazenado em $a0
            # Código 10 = Encerra o Programa
        call_code = vetor_reg[reg_dic["$v0"]] 
         
        if call_code == 1: # Imprimir Inteiro 
            print(f"Saída do Sistema: {vetor_reg[reg_dic['$a0']]}")

        elif call_code == 4: # Imprimir String

            starting = vetor_reg[reg_dic["$a0"]] # Começa no endereço armazenado em $a0
            string = "" 
    
            # Loop para ler caractere por caractere da memória até achar a 'flag' (0) 
            while 0 <= starting < len(memoria) and memoria[starting] != 0:
                string += chr(memoria[starting]) # Vai somando caracteres até formar a string completa
                starting += 1 
            print(f"Saída do Sistema: {string}") # Printa a String completa

        elif call_code == 10: # Sair (Padrão MIPS) 
            print("--- Syscall: Fim da Execução ---") 
            return len(programa) # Pula o PC para o final para parar o loop 
        else: 
            print(f"ERRO: Syscall com código desconhecido ({call_code}) na linha {PC + 1}.")
            # Aplicar um CAUSE, para código de chamada de sistema desconhecido

    # SEMPRE REINICIA O REG $zero PARA EVITAR ERROS
    vetor_reg[0] = 0
     
    # ADDER PARA O PC, basicamente vai para a próxima linha da matriz, ou próxima instrução
    return PC + 1 


# EXECUÇÃO DO PROGRAMA:

matriz_programa, data_table = read_arq(file_path) 

if matriz_programa: 
    print("--- INÍCIO DA SIMULAÇÃO ---") 
    print(f"Estado inicial dos registradores: {vetor_reg}")
    print(f"Tabela de dados encontrada: {data_table}\n")
     
    # Loop de execução 
    while PC < len(matriz_programa): 
        instrucao_atual = matriz_programa[PC] 
        print(f"PC={PC}: Executando -> {' '.join(instrucao_atual)}") 
         
        PC = decode_execute(instrucao_atual, PC, data_table, matriz_programa) 
         
        # Imprime o estado após a instrução (para depuração) 
        print(f"  Registradores: $v0={vetor_reg[reg_dic['$v0']]} $a0={vetor_reg[reg_dic['$a0']]}\
                $t0={vetor_reg[reg_dic['$t0']]} $t1={vetor_reg[reg_dic['$t1']]}") 
        print("-" * 20) 

    print("\n--- FIM DA SIMULAÇÃO ---") 
    print(f"Estado final dos registradores: {vetor_reg}")
    print(f"Estado final da memória (primeiros 32 bytes): {memoria[:32]}")
