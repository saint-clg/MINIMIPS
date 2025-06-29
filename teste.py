import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

class MipsInterface:
    def __init__(self, root):
        """
        Construtor da classe. Inicializa a interface e as variáveis do simulador.
        """
        self.root = root
        self.root.title("Simulador MIPS com Tradutor Binário")
        self.root.geometry("1280x720")

        # --- VARIÁVEIS DO SIMULADOR COMO ATRIBUTOS DA CLASSE ---
        self.memoria = []
        self.vetor_reg = []
        self.reg_dic = {
            "$zero": 0, "$v0": 1, "$a0": 2, "$t0": 3, "$t1": 4, 
            "$t2": 5, "$t3": 6, "$sp": 7, "$HI": 8, "$LO": 9
        }
        
        # Dicionários para a tradução para binário
        self.opcode_dic = {
            # Tipo-R (opcode é 0)
            "add": "000000", "sub": "000000", "mult": "000000",
            "and": "000000", "or": "000000", "sll": "000000",
            "slt": "000000", "syscall": "000000",
            # Tipo-I
            "addi": "001000", "lw": "100011", "sw": "101011",
            "lui": "001111", "slti": "001010"
        }
        self.funct_dic = {
            "add": "100000", "sub": "100010", "mult": "011000",
            "and": "100100", "or": "100101", "sll": "000000",
            "slt": "101010", "syscall": "001100"
        }

        self.PC = 0
        self.programa = []
        self.stepByStep = tk.BooleanVar()
        self.file_path_var = tk.StringVar(value="Nenhum arquivo carregado.")
        
        # Inicializa o estado do simulador
        self.reset_simulator()
        
        # Cria a interface gráfica
        self.create_widgets()
        
        # Atualiza os displays iniciais
        self.atualizar_display_registradores()

    def reset_simulator(self):
        """Reseta o estado do simulador para os valores iniciais."""
        self.memoria = [0] * 256
        self.vetor_reg = [0] * 10
        self.vetor_reg[self.reg_dic["$sp"]] = len(self.memoria) - 1 # $sp aponta para o fim da memória
        self.PC = 0
        self.programa = []
        print("Simulador resetado.")
        if hasattr(self, 'area_saidas'): # Verifica se a área de saídas já foi criada
            self.log_saida("Simulador resetado.")
            self.atualizar_display_registradores()
            self.area_bin.delete('1.0', tk.END)
            self.area_bin.insert(tk.INSERT, "Código MIPS Carregado:\n")
            self.file_path_var.set("Nenhum arquivo carregado.")

    def create_widgets(self):
        """Cria todos os componentes da interface gráfica."""
        # --- FRAME SUPERIOR PARA BOTÕES ---
        frame_botoes = tk.Frame(self.root, relief="ridge", borderwidth=2, padx=5, pady=5)
        frame_botoes.pack(side="top", fill="x")

        buttonFile = tk.Button(frame_botoes, text="Carregar Arquivo", command=self.botao_file)
        buttonStart = tk.Button(frame_botoes, text="Executar", command=self.botao_executa)
        buttonReset = tk.Button(frame_botoes, text="Resetar", command=self.botao_reseta)
        checkButton = tk.Checkbutton(frame_botoes, text="Executar Passo a Passo", variable=self.stepByStep, command=self.muda_step)

        buttonFile.pack(side="left", padx=5, pady=5)
        buttonStart.pack(side="left", padx=5, pady=5)
        buttonReset.pack(side="left", padx=5, pady=5)
        checkButton.pack(side="left", padx=5, pady=5)
        
        # Label para mostrar o caminho do arquivo
        label_arquivo = tk.Label(frame_botoes, textvariable=self.file_path_var, fg="gray")
        label_arquivo.pack(side="left", padx=10)

        # --- FRAME INFERIOR PARA ÁREAS DE TEXTO ---
        frame_meio = tk.Frame(self.root)
        frame_meio.pack(expand=True, fill="both", padx=10, pady=10)

        self.area_registradores = scrolledtext.ScrolledText(frame_meio, width=30, height=20, font=("Courier New", 10))
        self.area_registradores.pack(side="left", expand=True, fill="both", padx=5)
        
        self.area_bin = scrolledtext.ScrolledText(frame_meio, width=40, height=20, font=("Courier New", 10))
        self.area_bin.pack(side="left", expand=True, fill="both", padx=5)
        self.area_bin.insert(tk.INSERT, "Código MIPS Carregado:\n")

        self.area_saidas = scrolledtext.ScrolledText(frame_meio, width=50, height=20, font=("Courier New", 10))
        self.area_saidas.pack(side="left", expand=True, fill="both", padx=5)
        self.area_saidas.insert(tk.INSERT, "Saídas do Simulador:\n")

    def log_saida(self, mensagem):
        """Adiciona uma mensagem à área de saídas."""
        self.area_saidas.insert(tk.END, mensagem + "\n")
        self.area_saidas.see(tk.END) # Auto-scroll para o final

    def atualizar_display_registradores(self):
        """Limpa e reescreve a área de texto dos registradores com os valores atuais."""
        self.area_registradores.config(state=tk.NORMAL)
        self.area_registradores.delete('1.0', tk.END) 
        self.area_registradores.insert(tk.INSERT, "--- REGISTRADORES ---\n\n")
        for nome, indice in self.reg_dic.items():
            valor = self.vetor_reg[indice]
            linha = f"{nome:<8}: {valor:<10} (0x{valor:08X})\n"
            self.area_registradores.insert(tk.END, linha)
        self.area_registradores.config(state=tk.DISABLED)

    def botao_file(self):
        path = filedialog.askopenfilename(
            title="Selecione um arquivo .s",
            filetypes=(("Arquivos MIPS", "*.s"), ("Todos os arquivos", "*.*"))
        )
        if path:
            self.file_path_var.set(path)
            self.carregar_programa_na_tela()
            self.log_saida(f"Arquivo carregado: {path}")

    def carregar_programa_na_tela(self):
        """Lê o arquivo e exibe seu conteúdo na área de texto."""
        self.area_bin.delete('1.0', tk.END)
        self.area_bin.insert(tk.INSERT, "Código MIPS Carregado:\n\n")
        try:
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as f:
                self.area_bin.insert(tk.END, f.read())
        except Exception as e:
            self.area_bin.insert(tk.END, f"Erro ao ler o arquivo: {e}")

    def botao_executa(self):
        if "Nenhum arquivo" in self.file_path_var.get():
            messagebox.showerror("Erro", "Nenhum arquivo MIPS foi carregado!")
            return
            
        self.log_saida("\n--- INICIANDO EXECUÇÃO ---")
        self.executa_programa()
        self.log_saida("--- FIM DA EXECUÇÃO ---")

    def botao_reseta(self):
        self.reset_simulator()
    
    def muda_step(self):
        self.log_saida(f"Modo passo-a-passo {'ativado' if self.stepByStep.get() else 'desativado'}.")

    def executa_programa(self):
        """Lê, decodifica e executa o programa carregado."""
        
        def matriz_program(file_path):
            matriz = []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    linhas = f.read().splitlines()
            except FileNotFoundError:
                self.log_saida(f"Erro: Arquivo '{file_path}' não encontrado.")
                return None
            
            linhas_limpas = [l for l in linhas if l.strip() != '' and not l.strip().startswith('#')]
            for linha in linhas_limpas:
                partes = linha.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
                matriz.append(partes)
            return matriz

        self.programa = matriz_program(self.file_path_var.get())
        if not self.programa:
            return

        self.PC = 0
        while self.PC < len(self.programa):
            instrucao_atual = self.programa[self.PC]
            self.log_saida(f"PC={self.PC}: Executando -> {' '.join(instrucao_atual)}")
            
            novo_pc = self.decode_execute(instrucao_atual)
            self.PC = novo_pc
            
            self.atualizar_display_registradores()

            if self.stepByStep.get():
                if self.PC < len(self.programa):
                    if not messagebox.askokcancel("Passo a Passo", f"Próxima instrução: {' '.join(self.programa[self.PC])}\n\nDeseja continuar?"):
                        self.log_saida("Execução passo-a-passo interrompida pelo usuário.")
                        break

        self.atualizar_display_registradores()

    def _to_binary(self, n, bits):
        """Converte um número para uma string binária com 'bits' de comprimento (complemento de dois para negativos)."""
        if n >= 0:
            return format(n, 'b').zfill(bits)
        else:
            return format((1 << bits) + n, 'b')

    def traduzir_e_logar_binario(self, instrucao):
        """Recebe uma instrução, traduz para binário e printa na tela."""
        opcode_str = instrucao[0]
        binary_string = ""
        
        try:
            # --- TIPO R --- (ex: add $t1, $t2, $t3)
            if opcode_str in ["add", "sub", "and", "or", "slt"]:
                opcode = self.opcode_dic[opcode_str]
                rd = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = self._to_binary(self.reg_dic[instrucao[2]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[3]], 5)
                shamt = "00000"
                funct = self.funct_dic[opcode_str]
                binary_string = f"{opcode} {rs} {rt} {rd} {shamt} {funct} (Tipo R)"
            
            # --- TIPO R (mult) --- (ex: mult $t1, $t2)
            elif opcode_str == "mult":
                opcode = self.opcode_dic[opcode_str]
                rs = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[2]], 5)
                rd = "00000"
                shamt = "00000"
                funct = self.funct_dic[opcode_str]
                binary_string = f"{opcode} {rs} {rt} {rd} {shamt} {funct} (Tipo R)"

            # --- TIPO R (sll) --- (ex: sll $t1, $t2, 4)
            elif opcode_str == "sll":
                opcode = self.opcode_dic[opcode_str]
                rd = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[2]], 5)
                rs = "00000"
                shamt = self._to_binary(int(instrucao[3]), 5)
                funct = self.funct_dic[opcode_str]
                binary_string = f"{opcode} {rs} {rt} {rd} {shamt} {funct} (Tipo R)"

            # --- TIPO I --- (ex: addi $t1, $t2, 100)
            elif opcode_str in ["addi", "slti"]:
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = self._to_binary(self.reg_dic[instrucao[2]], 5)
                imediato = self._to_binary(int(instrucao[3]), 16)
                binary_string = f"{opcode} {rs} {rt} {imediato} (Tipo I)"
            
            # --- TIPO I (lw/sw) --- (ex: lw $t1, 16($sp))
            elif opcode_str in ["lw", "sw"]:
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                imediato = self._to_binary(int(instrucao[2]), 16)
                rs = self._to_binary(self.reg_dic[instrucao[3]], 5)
                binary_string = f"{opcode} {rs} {rt} {imediato} (Tipo I)"

            # --- TIPO I (lui) --- (ex: lui $t1, 16)
            elif opcode_str == "lui":
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = "00000"
                imediato = self._to_binary(int(instrucao[2]), 16)
                binary_string = f"{opcode} {rs} {rt} {imediato} (Tipo I)"

            # --- Syscall (special) ---
            elif opcode_str == "syscall":
                opcode = self.opcode_dic[opcode_str]
                funct = self.funct_dic[opcode_str]
                code = "0" * 20 # code field for syscall
                binary_string = f"{opcode} {code} {funct} (Syscall)"

            else:
                binary_string = "Tradução não implementada para esta instrução."

        except (KeyError, IndexError, ValueError) as e:
            binary_string = f"Erro na tradução: {e}. Verifique os operandos."

        self.log_saida(f"  -> Binário: {binary_string}")

    def decode_execute(self, instrucao):
        opcode = instrucao[0]
        if opcode not in self.opcode_dic:
            self.log_saida(f"Erro na linha {self.PC+1}: Instrução '{opcode}' desconhecida.")
            return self.PC + 1

        # LOGA A REPRESENTAÇÃO BINÁRIA
        self.traduzir_e_logar_binario(instrucao)

        # Lógica de execução da instrução
        try:
            if opcode in ["add", "sub", "and", "or", "slt"]:
                idx_dst = self.reg_dic[instrucao[1]]
                val_src1 = self.vetor_reg[self.reg_dic[instrucao[2]]]
                val_src2 = self.vetor_reg[self.reg_dic[instrucao[3]]]
                resultado = 0
                if opcode == "add": resultado = val_src1 + val_src2
                elif opcode == "sub": resultado = val_src1 - val_src2
                elif opcode == "and": resultado = val_src1 & val_src2
                elif opcode == "or":  resultado = val_src1 | val_src2
                elif opcode == "slt": resultado = 1 if val_src1 < val_src2 else 0
                if idx_dst != 0: self.vetor_reg[idx_dst] = resultado
            
            elif opcode == "mult":
                val_src1 = self.vetor_reg[self.reg_dic[instrucao[1]]]
                val_src2 = self.vetor_reg[self.reg_dic[instrucao[2]]]
                resultado_64bits = val_src1 * val_src2
                self.vetor_reg[self.reg_dic["$LO"]] = resultado_64bits & 0xFFFFFFFF
                self.vetor_reg[self.reg_dic["$HI"]] = resultado_64bits >> 32

            elif opcode == "sll":
                idx_dst = self.reg_dic[instrucao[1]]
                val_src = self.vetor_reg[self.reg_dic[instrucao[2]]]
                shamt = int(instrucao[3])
                if idx_dst != 0: self.vetor_reg[idx_dst] = val_src << shamt

            elif opcode in ["addi", "slti", "lui"]:
                idx_dst = self.reg_dic[instrucao[1]]
                resultado = 0
                if opcode == "lui":
                    imediato = int(instrucao[2])
                    resultado = imediato << 16
                else:
                    val_src = self.vetor_reg[self.reg_dic[instrucao[2]]]
                    imediato = int(instrucao[3])
                    if opcode == "addi": resultado = val_src + imediato
                    elif opcode == "slti": resultado = 1 if val_src < imediato else 0
                if idx_dst != 0: self.vetor_reg[idx_dst] = resultado

            elif opcode in ["lw", "sw"]:
                reg_rt_nome = instrucao[1]
                offset = int(instrucao[2])
                reg_base_nome = instrucao[3]
                endereco_memoria = offset + self.vetor_reg[self.reg_dic[reg_base_nome]]
                if not (0 <= endereco_memoria < len(self.memoria)):
                    self.log_saida(f"ERRO: Acesso inválido à memória ({endereco_memoria}) na linha {self.PC + 1}")
                else:
                    if opcode == "lw":
                        self.vetor_reg[self.reg_dic[reg_rt_nome]] = self.memoria[endereco_memoria]
                    elif opcode == "sw":
                        self.memoria[endereco_memoria] = self.vetor_reg[self.reg_dic[reg_rt_nome]]
            
            elif opcode == "syscall":
                call_code = self.vetor_reg[self.reg_dic["$v0"]]
                if call_code == 1:
                    self.log_saida(f"SAÍDA DO SISTEMA: {self.vetor_reg[self.reg_dic['$a0']]}")
                elif call_code == 10:
                    self.log_saida("--- Syscall: Fim da Execução ---")
                    return len(self.programa) # Termina a execução
                else:
                    self.log_saida(f"ERRO: Syscall desconhecido ({call_code})")

        except (KeyError, IndexError, ValueError) as e:
            self.log_saida(f"ERRO DE EXECUÇÃO na linha {self.PC+1}: {e}. Verifique a sintaxe da instrução.")
            return len(self.programa) # Para a execução em caso de erro

        self.vetor_reg[0] = 0 # Garante que $zero seja sempre 0
        return self.PC + 1

if __name__ == "__main__":
    root = tk.Tk()
    app = MipsInterface(root)
    root.mainloop()
