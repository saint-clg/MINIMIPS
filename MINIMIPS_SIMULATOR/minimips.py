# Importa as bibliotecas necessárias do Tkinter para a criação da interface gráfica.
import tkinter as tk
from tkinter import filedialog, scrolledtext

class MipsSimuladorGUI:
    """
    Classe principal que encapsula todo o simulador MIPS e sua interface gráfica (GUI).
    Ela gerencia o estado do processador (registradores, memória), o carregamento do programa,
    a execução (contínua ou passo a passo) e a exibição de todas as informações na tela.
    """
    def __init__(self, root):
        """
        Método construtor da classe. É chamado quando um objeto MipsSimuladorGUI é criado.
        Inicializa o simulador, as variáveis de estado e a interface gráfica.
        :param root: A janela principal (root) do Tkinter onde a interface será construída.
        """
        self.root = root
        self.root.title("MINI-MIPS Simulador") # Define o título da janela.

        # --- VARIÁVEIS DE ESTADO DO SIMULADOR ---
        self.memoria = []
        self.vetor_reg = []
        self.programa = []
        self.labels = {} # NOVO: Dicionário para guardar etiquetas (labels) e seus endereços.
        self.PC = 0
        self.file_path = ""
        self.step_by_step = tk.BooleanVar(value=False)

        # --- DICIONÁRIOS DE TRADUÇÃO E CONTROLE ---
        self.reg_dic = {
            "$zero": 0, "$v0": 1, "$a0": 2, "$t0": 3, "$t1": 4,
            "$t2": 5, "$t3": 6, "$sp": 7, "$HI": 8, "$LO": 9
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

        # --- INICIALIZAÇÃO DA GUI E DO SIMULADOR ---
        self._criar_widgets()
        self.resetar_simulador()

    def _criar_widgets(self):
        """
        Cria e posiciona todos os widgets (botões, caixas de texto, etc.) da interface gráfica.
        """
        frame_principal = tk.Frame(self.root, relief="ridge", borderwidth=2)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        frame_principal.rowconfigure(1, weight=1)
        frame_principal.columnconfigure(0, weight=1)

        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.grid(row=0, column=0, columnspan=3, sticky="nw", pady=5)

        buttonFile = tk.Button(frame_botoes, text="Selecionar Arquivo (.s)", command=self.selecionar_arquivo)
        buttonStart = tk.Button(frame_botoes, text="Executar/Próximo Passo", command=self.executar_programa)
        buttonReset = tk.Button(frame_botoes, text="Resetar", command=self.resetar_simulador)
        checkButton = tk.Checkbutton(frame_botoes, text="Executar Passo a Passo", variable=self.step_by_step)

        buttonFile.pack(side=tk.LEFT, padx=5)
        buttonStart.pack(side=tk.LEFT, padx=5)
        buttonReset.pack(side=tk.LEFT, padx=5)
        checkButton.pack(side=tk.LEFT, padx=5)

        frame_meio = tk.Frame(frame_principal)
        frame_meio.grid(row=1, column=0, sticky="nsew")
        frame_meio.rowconfigure(0, weight=1)
        frame_meio.columnconfigure(2, weight=1)

        self.area_registradores = scrolledtext.ScrolledText(frame_meio, width=25, height=20, font=("Courier New", 10))
        self.area_registradores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.area_bin = scrolledtext.ScrolledText(frame_meio, width=55, height=20, font=("Courier New", 10))
        self.area_bin.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.area_saidas = scrolledtext.ScrolledText(frame_meio, width=50, height=20, font=("Courier New", 10))
        self.area_saidas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

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
            else:
                return "Tradução não implementada."
        except (KeyError, IndexError, ValueError) as e:
            return f"Erro na tradução: {e}"

    def _load_program(self, file_path):
        """
        NOVO MÉTODO DE CARREGAMENTO.
        Lê um arquivo .s, processa as diretivas .data e .text, e carrega o programa
        na memória e na lista de instruções.
        """
        # Reinicia o estado do simulador para um novo carregamento.
        self.resetar_simulador()
        
        data_segment = []
        text_segment = []
        current_segment = None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.log_saida(f"Erro: Arquivo '{file_path}' não encontrado.")
            return None

        # 1ª Passagem: Separar as linhas em segmentos .data e .text
        for line in lines:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith('#'):
                continue
            
            if '.data' in clean_line:
                current_segment = 'data'
                continue
            elif '.text' in clean_line:
                current_segment = 'text'
                continue
            
            if current_segment == 'data':
                data_segment.append(clean_line)
            elif current_segment == 'text':
                text_segment.append(clean_line)

        # 2ª Passagem: Processar o segmento .data para preencher a memória e as etiquetas
        data_ptr = 0 # Ponteiro para a posição atual na memória de dados
        for line in data_segment:
            # Remove comentários da linha
            line_no_comment = line.split('#')[0].strip()
            if not line_no_comment:
                continue

            parts = line_no_comment.split()
            label = None
            if parts[0].endswith(':'):
                label = parts[0][:-1]
                self.labels[label] = data_ptr # Associa a etiqueta ao endereço de memória atual
                parts = parts[1:] # Remove a etiqueta da lista de partes
            
            if not parts:
                continue
            
            directive = parts[0]
            args = ' '.join(parts[1:])

            if directive == '.asciiz':
                # Extrai o conteúdo da string
                string_content = args.strip().strip('"')
                for char in string_content:
                    if data_ptr < len(self.memoria):
                        self.memoria[data_ptr] = ord(char) # Converte o caractere para seu valor ASCII
                        data_ptr += 1
                # Adiciona o terminador nulo
                if data_ptr < len(self.memoria):
                    self.memoria[data_ptr] = 0
                    data_ptr += 1
            elif directive == '.word':
                values = [int(v.strip()) for v in args.split(',')]
                for val in values:
                    if data_ptr < len(self.memoria):
                        self.memoria[data_ptr] = val
                        data_ptr += 1 
        
        # 3ª Passagem: Processar o segmento .text, substituindo pseudo-instruções
        program_matrix = []
        for line in text_segment:
            line_no_comment = line.split('#')[0].strip()
            if not line_no_comment:
                continue
            
            # Normaliza a linha para facilitar o parse
            parts = line_no_comment.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()

            if parts[0].endswith(':'):
                # Por agora, ignoramos as etiquetas de salto (jump/branch)
                parts = parts[1:]
            if not parts:
                continue
            
            # Expansão da pseudo-instrução 'la' (Load Address)
            if parts[0] == 'la':
                reg = parts[1]
                label = parts[2]
                if label in self.labels:
                    address = self.labels[label]
                    # Converte 'la $a0, msg' em 'addi $a0, $zero, [endereço_da_msg]'
                    program_matrix.append(['addi', reg, '$zero', str(address)])
                else:
                    self.log_saida(f"ERRO DE MONTAGEM: Etiqueta '{label}' não encontrada.")
                    return None
            else:
                program_matrix.append(parts)

        self.programa = program_matrix
        return True

    def decode_execute(self, instrucao):
        """Decodifica e executa uma única instrução MIPS."""
        opcode = instrucao[0]
        try:
            # --- Instruções do Tipo-R ---
            if opcode in ["add", "sub", "and", "or", "slt"]:
                idx_dst = self.reg_dic[instrucao[1]]
                val_src1 = self.vetor_reg[self.reg_dic[instrucao[2]]]
                val_src2 = self.vetor_reg[self.reg_dic[instrucao[3]]]
                res_map = {
                    "add": val_src1 + val_src2, "sub": val_src1 - val_src2, 
                    "and": val_src1 & val_src2, "or": val_src1 | val_src2,
                    "slt": 1 if val_src1 < val_src2 else 0
                }
                if idx_dst != 0: self.vetor_reg[idx_dst] = res_map[opcode]
            
            # --- Multiplicação ---
            elif opcode == "mult":
                val_src1 = self.vetor_reg[self.reg_dic[instrucao[1]]]
                val_src2 = self.vetor_reg[self.reg_dic[instrucao[2]]]
                res64 = val_src1 * val_src2
                self.vetor_reg[self.reg_dic["$LO"]] = res64 & 0xFFFFFFFF
                self.vetor_reg[self.reg_dic["$HI"]] = res64 >> 32
            # --- Shift ---
            elif opcode == "sll":
                idx_dst = self.reg_dic[instrucao[1]]
                val_src = self.vetor_reg[self.reg_dic[instrucao[2]]]
                shamt = int(instrucao[3])
                if idx_dst != 0: self.vetor_reg[idx_dst] = val_src << shamt
            
            # --- Instruções do Tipo-I ---
            elif opcode in ["addi", "slti", "lui"]:
                idx_dst = self.reg_dic[instrucao[1]]
                if opcode == "lui":
                    imediato = int(instrucao[2])
                    res = imediato << 16
                else:
                    val_src = self.vetor_reg[self.reg_dic[instrucao[2]]]
                    imediato = int(instrucao[3])
                    res = (val_src + imediato) if opcode == "addi" else (1 if val_src < imediato else 0)
                if idx_dst != 0: self.vetor_reg[idx_dst] = res
            
            # --- Instruções de Memória ---
            elif opcode in ["lw", "sw"]:
                reg_rt_name = instrucao[1]
                offset = int(instrucao[2])
                reg_base_nome = instrucao[3]
                endereco = offset + self.vetor_reg[self.reg_dic[reg_base_nome]]
                
                if not (0 <= endereco < len(self.memoria)):
                    self.log_saida(f"ERRO: Acesso a endereço de memória inválido ({endereco})")
                    self.PC = len(self.programa)
                    return
                
                if opcode == "lw":
                    self.vetor_reg[self.reg_dic[reg_rt_name]] = self.memoria[endereco]
                elif opcode == "sw":
                    self.memoria[endereco] = self.vetor_reg[self.reg_dic[reg_rt_name]]
            
            # --- Chamadas de Sistema ---
            elif opcode == "syscall":
                call_code = self.vetor_reg[self.reg_dic["$v0"]]
                if call_code == 1:
                    self.log_saida(f"Saída do Sistema (syscall 1): {self.vetor_reg[self.reg_dic['$a0']]}")
                elif call_code == 4:
                    endereco_atual = self.vetor_reg[self.reg_dic['$a0']]
                    string_impressa = []
                    while True:
                        if not (0 <= endereco_atual < len(self.memoria)):
                            self.log_saida(f"ERRO (syscall 4): Endereço de memória inválido ({endereco_atual}).")
                            break
                        byte_lido = self.memoria[endereco_atual]
                        if byte_lido == 0:
                            break
                        string_impressa.append(chr(byte_lido))
                        endereco_atual += 1
                    if string_impressa:
                        self.log_saida(f"Saída do Sistema (syscall 4): {''.join(string_impressa)}")
                elif call_code == 10:
                    self.log_saida("--- Syscall: Fim da Execução ---")
                    self.PC = len(self.programa)
                    return
                else:
                    self.log_saida(f"ERRO: Syscall com código desconhecido ({call_code}).")

            # --- Avanço ---
            self.vetor_reg[0] = 0
            self.PC += 1

        except (KeyError, IndexError, ValueError) as e:
            self.log_saida(f"ERRO DE EXECUÇÃO na linha {self.PC}: {' '.join(instrucao)}")
            self.log_saida(f"  > Detalhe: {e}. Verifique os operandos e a sintaxe.")
            self.PC = len(self.programa)

    # --- FUNÇÕES DE CONTROLE DA GUI ---

    def selecionar_arquivo(self):
        """Abre uma caixa de diálogo para o usuário selecionar um arquivo .s e o carrega."""
        path = filedialog.askopenfilename(
            title="Selecione um arquivo .s",
            filetypes=(("Arquivos MIPS", "*.s"), ("Todos os arquivos", "*.*"))
        )
        if path:
            self.file_path = path
            # ALTERADO: Chama o novo método de carregamento.
            if self._load_program(path):
                self.log_saida(f"Arquivo '{self.file_path.split('/')[-1]}' carregado com {len(self.programa)} instruções.")
                self.atualizar_displays()

    def executar_programa(self):
        """Inicia a execução do programa carregado."""
        if not self.programa:
            self.log_saida("Nenhum programa carregado. Selecione um arquivo primeiro.")
            return

        if self.PC >= len(self.programa):
            self.log_saida("O programa já terminou. Pressione 'Resetar' para executar novamente.")
            return

        if self.step_by_step.get():
            instrucao_atual = self.programa[self.PC]
            self.log_saida(f"PC={self.PC}: Executando -> {' '.join(instrucao_atual)}")
            self.decode_execute(instrucao_atual)
        else:
            self.log_saida("--- INÍCIO DA EXECUÇÃO CONTÍNUA ---")
            while self.PC < len(self.programa):
                instrucao_atual = self.programa[self.PC]
                self.decode_execute(instrucao_atual)
            # Evita duplicar a mensagem de fim se a última instrução for um syscall 10
            if not (instrucao_atual[0] == 'syscall' and self.vetor_reg[self.reg_dic['$v0']] == 10):
                 self.log_saida("--- FIM DA EXECUÇÃO ---")
        
        self.atualizar_displays()

    def resetar_simulador(self):
        """Reseta o estado do simulador para os valores iniciais."""
        self.memoria = [0] * 256
        self.vetor_reg = [0] * 10
        self.vetor_reg[self.reg_dic["$sp"]] = len(self.memoria) - 1
        self.PC = 0
        self.programa = []
        self.labels = {}
        
        if hasattr(self, 'area_saidas'):
             self.log_saida("Simulador resetado. Carregue um novo arquivo.", clear=True)
             self.atualizar_displays()

    def log_saida(self, mensagem, clear=False):
        """Adiciona uma mensagem à área de saídas na GUI."""
        if clear:
            self.area_saidas.delete('1.0', tk.END)
        self.area_saidas.insert(tk.END, mensagem + "\n")
        self.area_saidas.see(tk.END)

    def atualizar_displays(self):
        """Atualiza todas as áreas de texto com o estado atual do simulador."""
        self.area_registradores.delete('1.0', tk.END)
        self.area_registradores.insert(tk.INSERT, "--- REGISTRADORES ---\n")
        for nome, endereco in self.reg_dic.items():
            valor = self.vetor_reg[endereco]
            linha = f"{nome:<5}: {valor:<10} (0x{valor:08X})\n"
            self.area_registradores.insert(tk.END, linha)

        self.area_bin.delete('1.0', tk.END)
        self.area_bin.insert(tk.INSERT, "--- CÓDIGO FONTE E BINÁRIO ---\n")
        for i, instrucao in enumerate(self.programa):
            prefixo = ">>" if i == self.PC else "  "
            texto_instrucao = ' '.join(instrucao)
            binario_str = self.traduzir_instrucao_para_binario(instrucao)
            linha = f"{prefixo} {i:<3} {texto_instrucao:<20} | {binario_str}\n"
            self.area_bin.insert(tk.END, linha)

# --- Ponto de Entrada Principal da Aplicação ---
if __name__ == "__main__":
    root_window = tk.Tk()
    app = MipsSimuladorGUI(root_window)
    root_window.mainloop()
