import tkinter as tk
# Foram adicionadas as importações 'filedialog' e 'scrolledtext' que eram necessárias para a GUI
from tkinter import filedialog, scrolledtext


# --- CLASSE PRINCIPAL DA APLICAÇÃO ---
# O código foi encapsulado em uma classe para gerenciar o estado da GUI 
# e conectar a lógica do simulador aos widgets (botões, caixas de texto).
class MipsSimulatorGUI:
    def __init__(self, master):
        """
        Construtor da classe. Inicializa a janela principal e todas as variáveis do simulador.
        """
        self.master = master
        self.master.title("Simulador MIPS")
        # Define um tamanho inicial para a janela
        self.master.geometry("1600x900")

        #               (VÁRIAVEIS PARA A SIMULAR OS REGISTRADORES E INSTRUÇÕES) 

        # O vetor memória simula a pilha, podendo ser carregado em até 256 valores 
        self.memoria = [0] * 256

        # Vetor de registradores 
        # Fizemos uma simplificação, diminuindo a quantidade de registradores para apenas 10 
        # Aqui será salvo cada valor para os registradores, com excessão de sp 
        self.vetor_reg = [0] * 10 # $zero, $v0, $a0, $t0-$t3, $sp, $HI, $LO 

        # Um dicionário para ler os registradores que o .s nos enviar 
        # Cada instrução retorna um número que a posição do registrador no vetor de registradores 
        # Basicamente simulando um endereço para a memória onde fica armazenado seu valor 
        self.reg_dic = { 
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
        
        # O vetor de índice 7 representa o $sp 
        # Neste vetor ele irá salvar uma "posição" na memória, para simular a pilha 
        # Nada mais é que um índice que indica uma posição no vetor memória 
        # Começa apontando para o último índice e precisa ser "subtraido" para abrir espaço na pilha 
        self.vetor_reg[self.reg_dic["$sp"]] = len(self.memoria) - 1 # "Len(memoria)" retorna o tamanho do vetor memória em python 

        # LEMBRAR: Não esquecer de pesquisar como funcionam os regs $HI e $LO 

        # DICIONÁRIO DE CONTROLE ---- (prestar atenção para não esquecer) 

        # Control: [RegDst, ALUSrc, MemToReg, RegWrite, MemRead, MemWrite] 
        # ALUSrc: 0=Reg, 1=Imediato 
        # MemToReg: 0=ALUResult, 1=MemData 
        # RegWrite: 1=Escreve no registrador 
        # MemRead/Write: 1=Lê/Escreve na memória 

        self.inst_dic = { 
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

        self.opcode_dic = {
            "add": "000000", "sub": "000000", "mult": "000000", "and": "000000",
            "or": "000000", "sll": "000000", "slt": "000000", "syscall": "000000",
            "addi": "001000", "lw": "100011", "sw": "101011", "lui": "001111",
            "slti": "001010"
        }
        self.funct_dic = {
            "add": "100000", "sub": "100010", "mult": "011000", "and": "100100",
            "or": "100101", "sll": "000000", "slt": "101010", "syscall": "001100"
        }

        # --- VARIÁVEIS DE ESTADO DO SIMULADOR --- 
        self.file_path = "" # Path do arquivo a ser lido
        self.PC = 0 # Program Counter 
        self.EPC = 0 # EPC  
        self.CAUSE = 0 # CAUSE
        self.programa = []
        self.data_table = {}
        # Variável para o Checkbutton
        self.step_by_step = tk.BooleanVar(value=True)

        # Criação dos widgets da interface
        self._create_widgets()
        # Inicia a interface com os displays atualizados
        self.atualizar_displays()

    # --- FUNÇÕES DO BACKEND (SIMULADOR) ---
    # As funções do simulador foram transformadas em métodos da classe
    # para que possam acessar e modificar o estado do simulador (ex: self.memoria, self.PC)

    def read_arq(self, file_path): 
        """ 
        Lê um arquivo .s com seções .data e .text. 

        - Popula a memória da classe 'self.memoria' com os dados da seção .data. 
        - Cria uma tabela de símbolos para os rótulos de dados. 
        - Retorna a matriz de instruções da seção .text e a tabela de dados. 
        """ 
        # A variável global foi trocada por self.memoria
        data_table = {} 
        matriz_programa = [] 
        
        data_pointer = 0 
        topico_atual = None

        try: 
            with open(file_path, 'r', encoding='utf-8') as f: 
                linhas = f.readlines() 
        except FileNotFoundError: 
            self.log_saida(f"Erro: Arquivo '{file_path}' não encontrado.")
            # Fazer um código Cause (Não conseguiu ler o arquivo)
            return None, None 

        for linha in linhas: 
            linha_limpa = linha.split('#', 1)[0].strip() 

            if not linha_limpa: 
                continue 

            if linha_limpa == '.data': 
                topico_atual = 'data' 
                continue 
            elif linha_limpa == '.text': 
                topico_atual = 'text' 
                continue 

            if topico_atual == 'data': 
                try: 
                    label, resto = linha_limpa.split(':', 1) 
                    label = label.strip() 
                    directive_value = resto.strip().split(maxsplit=1)
                    directive = directive_value[0] 
                    
                    data_table[label] = data_pointer

                    if directive == '.asciiz': 
                        str_val = directive_value[1].strip('"') 
                        for char in str_val: 
                            self.memoria[data_pointer] = ord(char) 
                            data_pointer += 1 
                        self.memoria[data_pointer] = 0 
                        data_pointer += 1 
                    
                    elif directive == '.word': 
                        values = directive_value[1].split(',') 
                        for val in values: 
                            self.memoria[data_pointer] = int(val.strip()) 
                            data_pointer += 1  

                except Exception as e: 
                    self.log_saida(f"Erro ao processar linha de dados '{linha_limpa}': {e}")
                    # Adicionar um CAUSE aq para erros ao ler uma linha 

            elif topico_atual == 'text': 
                slices = linha_limpa.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
                matriz_programa.append(slices) 

        return matriz_programa, data_table

    def _to_binary(self, n, bits):
        """Converte um número inteiro para sua representação em string binária."""
        if n >= 0:
            return format(n, 'b').zfill(bits)
        else:
            return format((1 << bits) + n, 'b')

    def traduzir_instrucao_para_binario(self, instrucao):
        """Traduz uma instrução MIPS para o formato binário."""
        if not instrucao: return ""
        opcode_str = instrucao[0]
        try:
            if opcode_str in ["add", "sub", "and", "or", "slt"]:
                opcode = self.opcode_dic[opcode_str]
                rd = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = self._to_binary(self.reg_dic[instrucao[2]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[3]], 5)
                return f"{opcode} {rs} {rt} {rd} 00000 {self.funct_dic[opcode_str]} (Tipo R)"
            elif opcode_str == "mult":
                opcode = self.opcode_dic[opcode_str]
                rs = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[2]], 5)
                return f"{opcode} {rs} {rt} 00000 00000 {self.funct_dic[opcode_str]} (Tipo R)"
            elif opcode_str == "sll":
                opcode = self.opcode_dic[opcode_str]
                rd = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[2]], 5)
                shamt = self._to_binary(int(instrucao[3]), 5)
                return f"{opcode} 00000 {rt} {rd} {shamt} {self.funct_dic[opcode_str]} (Tipo R)"
            elif opcode_str in ["addi", "slti"]:
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = self._to_binary(self.reg_dic[instrucao[2]], 5)
                imediato = self._to_binary(int(instrucao[3]), 16)
                return f"{opcode} {rs} {rt} {imediato} (Tipo I)"
            elif opcode_str in ["lw", "sw"]:
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                imediato = self._to_binary(int(instrucao[2]), 16)
                rs = self._to_binary(self.reg_dic[instrucao[3]], 5)
                return f"{opcode} {rs} {rt} {imediato} (Tipo I)"
            elif opcode_str == "lui":
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                imediato = self._to_binary(int(instrucao[2]), 16)
                return f"{opcode} 00000 {rt} {imediato} (Tipo I)"
            elif opcode_str == "syscall":
                return f"{self.opcode_dic[opcode_str]} {'0'*20} {self.funct_dic[opcode_str]} (Syscall)"
            # A instrução 'la' é uma pseudo-instrução e não tem uma tradução binária direta
            elif opcode_str == "la":
                return "Pseudo-instrução (não possui formato binário direto)"
            else:
                return "Tradução não implementada."
        except (KeyError, IndexError, ValueError) as e:
            return f"Erro na tradução: {e}" 

    def decode_execute(self, instrucao): 
        """Decodifica e executa uma instrução. Atualiza o self.PC.""" 
        # As referências a variáveis globais foram trocadas por 'self'
        opcode = instrucao[0] 
        if opcode not in self.inst_dic: 
            self.log_saida(f"Erro na linha {self.PC+1}: Instrução '{opcode}' desconhecida.") 
            self.PC += 1
            return 
            # Colocar um CAUSE aqui para Instrução não encontrada

        # --- Instruções Type-R ---
        if opcode in ["add", "sub", "and", "or", "slt"]:
            reg_dst_name, reg_src_name, reg_temp_name = instrucao[1], instrucao[2], instrucao[3]
            idx_dst = self.reg_dic[reg_dst_name]
            val_src = self.vetor_reg[self.reg_dic[reg_src_name]]
            val_temp = self.vetor_reg[self.reg_dic[reg_temp_name]]
            resultado = 0
            if opcode == "add": resultado = val_src + val_temp
            elif opcode == "sub": resultado = val_src - val_temp
            elif opcode == "and": resultado = val_src & val_temp
            elif opcode == "or": resultado = val_src | val_temp
            elif opcode == "slt": resultado = 1 if val_src < val_temp else 0
            if idx_dst != 0: self.vetor_reg[idx_dst] = resultado
            else: self.log_saida("AVISO: Tentativa de escrita no registrador $zero ignorada.")

        # MULT
        elif opcode == "mult":
            reg_src_name, reg_temp_name = instrucao[1], instrucao[2]
            val_src = self.vetor_reg[self.reg_dic[reg_src_name]]
            val_temp = self.vetor_reg[self.reg_dic[reg_temp_name]]
            resultado_64bits = val_src * val_temp
            self.vetor_reg[self.reg_dic["$LO"]] = resultado_64bits & 0xFFFFFFFF
            self.vetor_reg[self.reg_dic["$HI"]] = resultado_64bits >> 32

        # Shift
        elif opcode == "sll":
            reg_dst_name, reg_temp_name, shamt = instrucao[1], instrucao[2], int(instrucao[3])
            idx_dst = self.reg_dic[reg_dst_name]
            val_temp = self.vetor_reg[self.reg_dic[reg_temp_name]]
            resultado = val_temp << shamt
            if idx_dst != 0: self.vetor_reg[idx_dst] = resultado

        # --- Instruções Type-I ---
        elif opcode in ["addi", "slti", "lui"]:
            reg_temp_name = instrucao[1]
            idx_temp = self.reg_dic[reg_temp_name]
            resultado = 0
            if opcode == "lui":
                imediate = int(instrucao[2])
                resultado = imediate << 16
            else:
                reg_src_name, imediate = instrucao[2], int(instrucao[3])
                val_src = self.vetor_reg[self.reg_dic[reg_src_name]]
                if opcode == "addi": resultado = val_src + imediate
                elif opcode == "slti": resultado = 1 if val_src < imediate else 0
            if idx_temp != 0: self.vetor_reg[idx_temp] = resultado

        # --- Instruções Type-I para memoria ---
        elif opcode in ["lw", "sw"]:
            reg_temp_name, offset, reg_src_name = instrucao[1], int(instrucao[2]), instrucao[3]
            mem_adress = offset + self.vetor_reg[self.reg_dic[reg_src_name]]
            if not (0 <= mem_adress < len(self.memoria)):
                self.log_saida(f"ERRO: Acesso a endereço de memória inválido ({mem_adress}) na linha {self.PC + 1}")
            else:
                if opcode == "lw":
                    if reg_temp_name not in self.reg_dic:
                        self.log_saida(f"ERRO DE SINTAXE: 'lw' requer um registrador de destino, mas recebeu '{reg_temp_name}' na linha {self.PC+1}")
                    else:
                        self.vetor_reg[self.reg_dic[reg_temp_name]] = self.memoria[mem_adress]
                elif opcode == "sw":
                     val_temp = self.vetor_reg[self.reg_dic[reg_temp_name]]
                     self.memoria[mem_adress] = val_temp
       
        # --- LOAD ADRESS ---
        elif opcode == "la":
            reg_temp_name, label_name = instrucao[1], instrucao[2]
            if label_name in self.data_table:
                adress = self.data_table[label_name]
                idx_temp = self.reg_dic[reg_temp_name]
                if idx_temp != 0: self.vetor_reg[idx_temp] = adress
            else:
                self.log_saida(f"ERRO: Etiqueta de dados '{label_name}' não encontrada na linha {self.PC + 1}.")
        
        # --- Syscall ---
        elif opcode == "syscall":
            call_code = self.vetor_reg[self.reg_dic["$v0"]]
            if call_code == 1:
                self.log_saida(f"{self.vetor_reg[self.reg_dic['$a0']]}")
            elif call_code == 4:
                starting = self.vetor_reg[self.reg_dic["$a0"]]
                string = ""
                while 0 <= starting < len(self.memoria) and self.memoria[starting] != 0:
                    string += chr(self.memoria[starting])
                    starting += 1
                self.log_saida(f"{string}")
            elif call_code == 10:
                self.log_saida("--- Syscall: Fim da Execução ---")
                self.PC = len(self.programa) # Pula o PC para o final para parar o loop
                return # Retorna para não incrementar o PC novamente
            else:
                self.log_saida(f"ERRO: Syscall com código desconhecido ({call_code}) na linha {self.PC + 1}.")

        self.vetor_reg[0] = 0
        self.PC += 1

    # --- FUNÇÕES DE CONTROLE DA GUI ---

    #Função para carregar o arquivo .s para a execução do programa
    def _load_program(self, path):
        """Método interno para carregar e preparar o programa do arquivo."""
        # Reseta o estado antes de carregar um novo arquivo
        self.resetar_simulador()
        
        self.file_path = path
        programa, data_table = self.read_arq(path)
        
        if programa is not None:
            self.programa = programa
            self.data_table = data_table
            return True
        return False

    #Função para o usuario selecionar o arquivo que ele deseja executar
    def selecionar_arquivo(self):
        """Abre uma caixa de diálogo para o usuário selecionar um arquivo .s e o carrega."""
        path = filedialog.askopenfilename(
            title="Selecione um arquivo .s",
            filetypes=(("Arquivos MIPS", "*.s"), ("Todos os arquivos", "*.*"))
        )
        if path:
            if self._load_program(path):
                self.log_saida(f"Arquivo '{self.file_path.split('/')[-1]}' carregado com {len(self.programa)} instruções.", clear=True)
                self.atualizar_displays()

    #Inicia a execução do programa
    def executar_programa(self):
        """Inicia a execução do programa carregado."""
        if not self.programa:
            self.log_saida("Nenhum programa carregado. Selecione um arquivo primeiro.")
            return

        if self.PC >= len(self.programa):
            self.log_saida("O programa já terminou. Pressione 'Resetar' para executar novamente.")
            return

        # Modo Passo a Passo
        if self.step_by_step.get():
            instrucao_atual = self.programa[self.PC]
            self.log_saida(f"PC={self.PC}: Executando -> {' '.join(instrucao_atual)}")
            self.decode_execute(instrucao_atual)
        # Modo Contínuo
        else:
            self.log_saida("--- INÍCIO DA EXECUÇÃO CONTÍNUA ---")
            while self.PC < len(self.programa):
                instrucao_atual = self.programa[self.PC]
                # Para a execução se encontrar um syscall 10 no meio do caminho
                if instrucao_atual[0] == 'syscall' and self.vetor_reg[self.reg_dic['$v0']] == 10:
                    self.decode_execute(instrucao_atual)
                    break 
                self.decode_execute(instrucao_atual)
            
            # Mensagem de fim apenas se o programa não foi terminado por um syscall 10
            if self.PC >= len(self.programa) and not (instrucao_atual[0] == 'syscall' and self.vetor_reg[self.reg_dic['$v0']] == 10):
                 self.log_saida("--- FIM DA EXECUÇÃO ---")
        
        self.atualizar_displays()

    #Reseta todas as variaveis para as iniciais do programa
    def resetar_simulador(self):
        """Reseta o estado do simulador para os valores iniciais."""
        self.memoria = [0] * 256
        self.vetor_reg = [0] * 10
        self.vetor_reg[self.reg_dic["$sp"]] = len(self.memoria) - 1
        self.PC = 0
        #Esvazia as instruções do programa.
        self.programa = []
        #Tabela de dados e caminho do arquivo limpos
        self.data_table = {}
        self.file_path = ""
        self.log_saida("Simulador resetado. Carregue um novo arquivo", clear=True)
    
        #Chama a função para redesenhar a interface. Como self.programa está vazia,
        #a área de código fonte e binário ficará limpa.
        self.atualizar_displays()

    def log_saida(self, mensagem, clear=False):
        """Adiciona uma mensagem à área de saídas na GUI."""
        # Garante que o widget exista antes de tentar usá-lo
        if not hasattr(self, 'area_saidas'):
            return
        # Habilita a edição para inserir texto
        self.area_saidas.config(state=tk.NORMAL)
        if clear:
            self.area_saidas.delete('1.0', tk.END)
        self.area_saidas.insert(tk.END, mensagem + "\n")
        self.area_saidas.see(tk.END) # Rola para o final
        # Desabilita a edição para o usuário não poder digitar
        self.area_saidas.config(state=tk.DISABLED)


    #Atualiza em tempo real os registradores, funçoes e saidas da execução
    def atualizar_displays(self):
        """Atualiza todas as áreas de texto com o estado atual do simulador."""
        # Garante que os widgets existam
        if not hasattr(self, 'area_registradores'):
            return
        
        # --- Atualiza Registradores ---
        self.area_registradores.config(state=tk.NORMAL)
        self.area_registradores.delete('1.0', tk.END)
        self.area_registradores.insert(tk.INSERT, "--- REGISTRADORES ---\n")
        for nome, endereco in self.reg_dic.items():
            valor = self.vetor_reg[endereco]
            linha = f"{nome:<5}: {valor:<10} (0x{valor:08X})\n"
            self.area_registradores.insert(tk.END, linha)
        self.area_registradores.config(state=tk.DISABLED)

        # --- Atualiza Código Fonte e Binário ---
        self.area_bin.config(state=tk.NORMAL)
        self.area_bin.delete('1.0', tk.END)
        self.area_bin.insert(tk.INSERT, "--- CÓDIGO FONTE E BINÁRIO ---\n")
        for i, instrucao in enumerate(self.programa):
            prefixo = ">>" if i == self.PC else "  "
            texto_instrucao = ' '.join(instrucao)
            binario_str = self.traduzir_instrucao_para_binario(instrucao)
            linha = f"{prefixo} {i:<3} {texto_instrucao:<25} | {binario_str}\n"
            self.area_bin.insert(tk.END, linha)
        self.area_bin.config(state=tk.DISABLED)
        
        # --- Atualiza Memória ---
        # Adicionei uma visualização da memória para depuração
        self.area_memoria.config(state=tk.NORMAL)
        self.area_memoria.delete('1.0', tk.END)
        self.area_memoria.insert(tk.INSERT, "--- MEMÓRIA (início) ---\n")
        for i in range(0, 64, 4): # Exibe os primeiros 64 bytes
            addr = f"0x{i:04X}"
            val1 = self.memoria[i]
            val2 = self.memoria[i+1]
            val3 = self.memoria[i+2]
            val4 = self.memoria[i+3]
            linha = f"{addr}: {val1:<5} {val2:<5} {val3:<5} {val4:<5}\n"
            self.area_memoria.insert(tk.END, linha)
        self.area_memoria.config(state=tk.DISABLED)


    #Criação da interface do programa
    def _create_widgets(self):
        """
        Cria e posiciona todos os widgets (botões, caixas de texto, etc.) da interface gráfica.
        """
        # Frame principal que contém todos os outros elementos
        frame_principal = tk.Frame(self.master, padx=10, pady=10)
        frame_principal.pack(fill="both", expand=True)

        # --- Frame para os botões de controle ---
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(fill="x", pady=(0, 10))

        buttonFile = tk.Button(frame_botoes, text="Selecionar Arquivo (.s)", command=self.selecionar_arquivo)
        buttonStart = tk.Button(frame_botoes, text="Executar/Próximo Passo", command=self.executar_programa)
        buttonReset = tk.Button(frame_botoes, text="Resetar", command=self.resetar_simulador)
        checkButton = tk.Checkbutton(frame_botoes, text="Executar Passo a Passo", variable=self.step_by_step)

        buttonFile.pack(side=tk.LEFT, padx=(0, 5))
        buttonStart.pack(side=tk.LEFT, padx=5)
        buttonReset.pack(side=tk.LEFT, padx=5)
        checkButton.pack(side=tk.LEFT, padx=5)
        
        # --- Frame para os displays de texto ---
        # Este frame usa grid para melhor alinhamento e redimensionamento
        frame_displays = tk.Frame(frame_principal)
        frame_displays.pack(fill="both", expand=True)
        frame_displays.rowconfigure(0, weight=1)
        frame_displays.columnconfigure(0, weight=3) # Coluna do código binário maior
        frame_displays.columnconfigure(1, weight=2) # Coluna dos registradores e memória
        frame_displays.columnconfigure(2, weight=3) # Coluna de saída

        # --- Coluna da Esquerda (Código Binário) ---
        self.area_bin = scrolledtext.ScrolledText(frame_displays, width=60, height=20, font=("Courier New", 10), relief="solid", borderwidth=1)
        self.area_bin.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        
        # --- Coluna do Meio (Registradores e Memória) ---
        frame_meio = tk.Frame(frame_displays)
        frame_meio.grid(row=0, column=1, sticky="nsew", padx=5)
        frame_meio.rowconfigure(0, weight=1)
        frame_meio.rowconfigure(1, weight=1) # Divide o espaço entre regs e mem
        frame_meio.columnconfigure(0, weight=1)

        self.area_registradores = scrolledtext.ScrolledText(frame_meio, width=35, height=10, font=("Courier New", 10), relief="solid", borderwidth=1)
        self.area_registradores.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        
        # Adicionando visualizador de memória
        self.area_memoria = scrolledtext.ScrolledText(frame_meio, width=35, height=10, font=("Courier New", 10), relief="solid", borderwidth=1)
        self.area_memoria.grid(row=1, column=0, sticky="nsew")

        # --- Coluna da Direita (Saídas) ---
        self.area_saidas = scrolledtext.ScrolledText(frame_displays, width=50, height=20, font=("Courier New", 10), relief="solid", borderwidth=1)
        self.area_saidas.grid(row=0, column=2, sticky="nsew", padx=(5,0))


# --- Ponto de Entrada Principal da Aplicação ---
if __name__ == "__main__":
    # A execução do programa agora consiste em criar a janela principal
    # e instanciar a classe da nossa aplicação.
    root_window = tk.Tk()
    app = MipsSimulatorGUI(master=root_window)
    root_window.mainloop()