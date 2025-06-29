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
        # Atributos da instância (self) que guardam o estado atual do simulador.
        self.memoria = []       # Simula a memória principal do MIPS, como uma lista.
        self.vetor_reg = []     # Simula o banco de registradores, como uma lista.
        self.programa = []      # Armazena o programa carregado, como uma lista de instruções.
        self.PC = 0             # Program Counter (Contador de Programa), aponta para a próxima instrução a ser executada.
        self.file_path = ""     # Caminho do arquivo .s carregado.
        self.step_by_step = tk.BooleanVar(value=False) # Variável do Tkinter para controlar o modo de execução (passo a passo ou contínuo).

        # --- DICIONÁRIOS DE TRADUÇÃO E CONTROLE ---
        # Dicionário que mapeia o nome de cada registrador para seu índice no vetor_reg.
        self.reg_dic = {
            "$zero": 0, "$v0": 1, "$a0": 2, "$t0": 3, "$t1": 4,
            "$t2": 5, "$t3": 6, "$sp": 7, "$HI": 8, "$LO": 9
        }
        # Dicionário que mapeia o nome da instrução para seu código de operação (opcode) em binário.
        self.opcode_dic = {
            # Tipo-R (opcode é sempre "000000")
            "add": "000000", "sub": "000000", "mult": "000000", "and": "000000",
            "or": "000000", "sll": "000000", "slt": "000000", "syscall": "000000",
            # Tipo-I
            "addi": "001000", "lw": "100011", "sw": "101011", "lui": "001111",
            "slti": "001010"
        }
        # Dicionário que mapeia o nome da instrução do Tipo-R ao seu código de função (funct) em binário.
        self.funct_dic = {
            "add": "100000", "sub": "100010", "mult": "011000", "and": "100100",
            "or": "100101", "sll": "000000", "slt": "101010", "syscall": "001100"
        }

        # --- INICIALIZAÇÃO DA GUI E DO SIMULADOR ---
        self._criar_widgets()       # Chama o método para criar os elementos visuais da interface.
        self.resetar_simulador()  # Chama o método para inicializar/resetar o estado do simulador.

    def _criar_widgets(self):
        """
        Cria e posiciona todos os widgets (botões, caixas de texto, etc.) da interface gráfica.
        Este método é chamado apenas uma vez, no construtor.
        """
        # --- ESTRUTURA DA JANELA (FRAMES) ---
        # O Frame principal contém todos os outros elementos.
        frame_principal = tk.Frame(self.root, relief="ridge", borderwidth=2)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        frame_principal.rowconfigure(1, weight=1)    # Permite que a linha 1 (com as áreas de texto) se expanda verticalmente.
        frame_principal.columnconfigure(0, weight=1) # Permite que a coluna 0 se expanda horizontalmente.

        # Frame para os botões de controle.
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.grid(row=0, column=0, columnspan=3, sticky="nw", pady=5) # Posiciona na parte superior.

        # --- BOTÕES ---
        buttonFile = tk.Button(frame_botoes, text="Selecionar Arquivo (.s)", command=self.selecionar_arquivo)
        buttonStart = tk.Button(frame_botoes, text="Executar/Próximo Passo", command=self.executar_programa)
        buttonReset = tk.Button(frame_botoes, text="Resetar", command=self.resetar_simulador)
        checkButton = tk.Checkbutton(frame_botoes, text="Executar Passo a Passo", variable=self.step_by_step)

        # Adiciona os botões ao frame de botões, um ao lado do outro.
        buttonFile.pack(side=tk.LEFT, padx=5)
        buttonStart.pack(side=tk.LEFT, padx=5)
        buttonReset.pack(side=tk.LEFT, padx=5)
        checkButton.pack(side=tk.LEFT, padx=5)

        # --- ÁREAS DE TEXTO ---
        # Frame que agrupa as três áreas de texto.
        frame_meio = tk.Frame(frame_principal)
        frame_meio.grid(row=1, column=0, sticky="nsew") # Posiciona abaixo dos botões.
        frame_meio.rowconfigure(0, weight=1) # Permite expansão vertical.
        frame_meio.columnconfigure(2, weight=1) # A terceira coluna (Saídas) tem prioridade para expandir horizontalmente.

        # Área de Texto para Registradores (com barra de rolagem).
        self.area_registradores = scrolledtext.ScrolledText(frame_meio, width=25, height=20, font=("Courier New", 10))
        self.area_registradores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Área de Texto para Código Binário (com barra de rolagem).
        self.area_bin = scrolledtext.ScrolledText(frame_meio, width=55, height=20, font=("Courier New", 10))
        self.area_bin.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Área de Texto para Saídas do Sistema (com barra de rolagem).
        self.area_saidas = scrolledtext.ScrolledText(frame_meio, width=50, height=20, font=("Courier New", 10))
        self.area_saidas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

    def _to_binary(self, n, bits):
        """
        Função utilitária para converter um número inteiro para sua representação em string binária.
        :param n: O número a ser convertido.
        :param bits: O número de bits que a string binária deve ter (preenche com zeros à esquerda).
        :return: A string binária formatada.
        """
        if n >= 0:
            return format(n, 'b').zfill(bits)
        else: # Lida com a representação em complemento de dois para números negativos.
            return format((1 << bits) + n, 'b')

    def traduzir_instrucao_para_binario(self, instrucao):
        """
        Recebe uma instrução (como uma lista de strings) e a traduz para o formato binário MIPS.
        :param instrucao: A instrução parseada, ex: ['add', '$t0', '$t1', '$t2'].
        :return: Uma string representando a instrução em binário.
        """
        if not instrucao: return "" # Retorna vazio se a instrução for inválida.
        opcode_str = instrucao[0]
        try:
            # A lógica de tradução é separada pelo tipo da instrução (R ou I).
            if opcode_str in ["add", "sub", "and", "or", "slt"]: # Tipo R padrão
                opcode = self.opcode_dic[opcode_str]
                rd = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = self._to_binary(self.reg_dic[instrucao[2]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[3]], 5)
                return f"{opcode} {rs} {rt} {rd} 00000 {self.funct_dic[opcode_str]} (Tipo R)"
            elif opcode_str == "mult": # Tipo R especial (sem rd)
                opcode = self.opcode_dic[opcode_str]
                rs = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[2]], 5)
                return f"{opcode} {rs} {rt} 00000 00000 {self.funct_dic[opcode_str]} (Tipo R)"
            elif opcode_str == "sll": # Tipo R especial (com shamt)
                opcode = self.opcode_dic[opcode_str]
                rd = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rt = self._to_binary(self.reg_dic[instrucao[2]], 5)
                shamt = self._to_binary(int(instrucao[3]), 5)
                return f"{opcode} 00000 {rt} {rd} {shamt} {self.funct_dic[opcode_str]} (Tipo R)"
            elif opcode_str in ["addi", "slti"]: # Tipo I padrão
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                rs = self._to_binary(self.reg_dic[instrucao[2]], 5)
                imediato = self._to_binary(int(instrucao[3]), 16)
                return f"{opcode} {rs} {rt} {imediato} (Tipo I)"
            elif opcode_str in ["lw", "sw"]: # Tipo I de memória
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                imediato = self._to_binary(int(instrucao[2]), 16)
                rs = self._to_binary(self.reg_dic[instrucao[3]], 5)
                return f"{opcode} {rs} {rt} {imediato} (Tipo I)"
            elif opcode_str == "lui": # Tipo I especial
                opcode = self.opcode_dic[opcode_str]
                rt = self._to_binary(self.reg_dic[instrucao[1]], 5)
                imediato = self._to_binary(int(instrucao[2]), 16)
                return f"{opcode} 00000 {rt} {imediato} (Tipo I)"
            elif opcode_str == "syscall": # Instrução de chamada de sistema
                return f"{self.opcode_dic[opcode_str]} {'0'*20} {self.funct_dic[opcode_str]} (Syscall)"
            else:
                return "Tradução não implementada."
        except (KeyError, IndexError, ValueError) as e:
            # Captura erros comuns de tradução (ex: registrador inválido, operando faltando).
            return f"Erro na tradução: {e}"

    def matriz_program(self, file_path):
        """
        Lê um arquivo de código assembly MIPS (.s) e o converte em uma lista de instruções.
        Cada instrução é, por sua vez, uma lista de seus componentes (opcode, operandos).
        :param file_path: O caminho para o arquivo .s.
        :return: Uma lista de listas representando o programa, ou None se o arquivo não for encontrado.
        """
        matriz = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                linhas = f.read().splitlines()
            # Filtra linhas vazias e linhas que são apenas comentários.
            linhas = [l for l in linhas if l.strip() and not l.strip().startswith('#')]
            for linha in linhas:
                # Normaliza a instrução: remove vírgulas e parênteses e divide em partes.
                # Ex: "addi $t0, $t1, 10" -> ['addi', '$t0', '$t1', '10']
                # Ex: "lw $t0, 4($sp)" -> ['lw', '$t0', '4', '$sp']
                partes = linha.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
                matriz.append(partes)
            return matriz
        except FileNotFoundError:
            self.log_saida(f"Erro: Arquivo '{file_path}' não encontrado.")
            return None

    def decode_execute(self, instrucao):
        """
        Decodifica e executa uma única instrução MIPS. Este é o coração do ciclo do processador.
        Atualiza o estado do simulador (registradores, memória, PC) de acordo com a instrução.
        :param instrucao: A instrução a ser executada.
        """
        opcode = instrucao[0]
        
        try:
            # --- Instruções do Tipo-R (operam entre registradores) ---
            if opcode in ["add", "sub", "and", "or", "slt"]:
                idx_dst = self.reg_dic[instrucao[1]]
                val_src1 = self.vetor_reg[self.reg_dic[instrucao[2]]]
                val_src2 = self.vetor_reg[self.reg_dic[instrucao[3]]]
                # Um mapa para simplificar a seleção da operação.
                res_map = {
                    "add": val_src1 + val_src2, "sub": val_src1 - val_src2, 
                    "and": val_src1 & val_src2, "or": val_src1 | val_src2,
                    "slt": 1 if val_src1 < val_src2 else 0
                }
                # Escreve o resultado no registrador de destino, a menos que seja $zero.
                if idx_dst != 0: self.vetor_reg[idx_dst] = res_map[opcode]
            
            # --- Multiplicação ---
            elif opcode == "mult":
                val_src1 = self.vetor_reg[self.reg_dic[instrucao[1]]]
                val_src2 = self.vetor_reg[self.reg_dic[instrucao[2]]]
                res64 = val_src1 * val_src2 # A multiplicação pode gerar um resultado de 64 bits.
                # Armazena os 32 bits menos significativos em $LO.
                self.vetor_reg[self.reg_dic["$LO"]] = res64 & 0xFFFFFFFF 
                # Armazena os 32 bits mais significativos em $HI.
                self.vetor_reg[self.reg_dic["$HI"]] = res64 >> 32      

            # --- Shift Lógico para a Esquerda ---
            elif opcode == "sll":
                idx_dst = self.reg_dic[instrucao[1]]
                val_src = self.vetor_reg[self.reg_dic[instrucao[2]]]
                shamt = int(instrucao[3]) # Quantidade de deslocamento.
                if idx_dst != 0: self.vetor_reg[idx_dst] = val_src << shamt
            
            # --- Instruções do Tipo-I (operam com um valor imediato) ---
            elif opcode in ["addi", "slti", "lui"]:
                idx_dst = self.reg_dic[instrucao[1]]
                if opcode == "lui": # Load Upper Immediate
                    imediato = int(instrucao[2])
                    res = imediato << 16 # Carrega o imediato nos 16 bits superiores do registrador.
                else: # addi, slti
                    val_src = self.vetor_reg[self.reg_dic[instrucao[2]]]
                    imediato = int(instrucao[3])
                    res = (val_src + imediato) if opcode == "addi" else (1 if val_src < imediato else 0)
                if idx_dst != 0: self.vetor_reg[idx_dst] = res
            
            # --- Instruções de Acesso à Memória (Load/Store) ---
            elif opcode in ["lw", "sw"]:
                reg_rt_name = instrucao[1]
                offset = int(instrucao[2])
                reg_base_nome = instrucao[3]
                # Calcula o endereço efetivo na memória: base + deslocamento.
                endereco = offset + self.vetor_reg[self.reg_dic[reg_base_nome]]
                
                # Verifica se o endereço é válido.
                if not (0 <= endereco < len(self.memoria)):
                    self.log_saida(f"ERRO: Acesso a endereço de memória inválido ({endereco})")
                    self.PC = len(self.programa) # Para a execução em caso de erro.
                    return
                
                if opcode == "lw": # Load Word: carrega da memória para o registrador.
                    self.vetor_reg[self.reg_dic[reg_rt_name]] = self.memoria[endereco]
                elif opcode == "sw": # Store Word: armazena do registrador para a memória.
                    self.memoria[endereco] = self.vetor_reg[self.reg_dic[reg_rt_name]]
            
            # --- Chamadas de Sistema ---
            elif opcode == "syscall":
                call_code = self.vetor_reg[self.reg_dic["$v0"]] # O código do serviço está em $v0.
                if call_code == 1: # Código 1: Imprimir Inteiro.
                    # O argumento (inteiro a ser impresso) está em $a0.
                    self.log_saida(f"Saída do Sistema (syscall 1): {self.vetor_reg[self.reg_dic['$a0']]}")
                elif call_code == 10: # Código 10: Terminar o programa.
                    self.log_saida("--- Syscall: Fim da Execução ---")
                    self.PC = len(self.programa) # Move o PC para o fim para parar o loop de execução.
                    return
                else:
                    self.log_saida(f"ERRO: Syscall com código desconhecido ({call_code}).")

            # --- Manutenção e Avanço do PC ---
            self.vetor_reg[0] = 0 # Garante que o registrador $zero seja sempre 0.
            self.PC += 1 # Incrementa o PC para a próxima instrução (não lida com saltos/desvios).

        except (KeyError, IndexError, ValueError) as e:
            # Captura erros de execução (ex: registrador não existe, operando inválido).
            self.log_saida(f"ERRO DE EXECUÇÃO na linha {self.PC}: {' '.join(instrucao)}")
            self.log_saida(f"  > Detalhe: {e}. Verifique os operandos e a sintaxe.")
            self.PC = len(self.programa) # Para a execução.

    # --- FUNÇÕES DE CONTROLE DA GUI (Callbacks dos botões) ---

    def selecionar_arquivo(self):
        """Abre uma caixa de diálogo para o usuário selecionar um arquivo .s e o carrega."""
        path = filedialog.askopenfilename(
            title="Selecione um arquivo .s",
            filetypes=(("Arquivos MIPS", "*.s"), ("Todos os arquivos", "*.*"))
        )
        if path: # Se o usuário selecionou um arquivo.
            self.file_path = path
            self.resetar_simulador() # Reseta o estado antes de carregar o novo programa.
            self.programa = self.matriz_program(self.file_path)
            if self.programa:
                self.log_saida(f"Arquivo '{self.file_path.split('/')[-1]}' carregado com {len(self.programa)} instruções.")
            self.atualizar_displays() # Atualiza a GUI para mostrar o programa carregado.

    def executar_programa(self):
        """
        Inicia a execução do programa carregado.
        Executa uma instrução (passo a passo) ou todas (contínuo).
        """
        if not self.programa:
            self.log_saida("Nenhum programa carregado. Selecione um arquivo primeiro.")
            return

        if self.PC >= len(self.programa):
            self.log_saida("O programa já terminou. Pressione 'Resetar' para executar novamente.")
            return

        if self.step_by_step.get(): # Se o modo "passo a passo" está ativo.
            instrucao_atual = self.programa[self.PC]
            self.log_saida(f"PC={self.PC}: Executando -> {' '.join(instrucao_atual)}")
            self.decode_execute(instrucao_atual) # Executa apenas uma instrução.
        else: # Execução contínua.
            self.log_saida("--- INÍCIO DA EXECUÇÃO CONTÍNUA ---")
            while self.PC < len(self.programa): # Loop até o PC chegar ao fim do programa.
                instrucao_atual = self.programa[self.PC]
                self.decode_execute(instrucao_atual)
            self.log_saida("--- FIM DA EXECUÇÃO ---")
        
        self.atualizar_displays() # Atualiza a GUI após a execução.

    def resetar_simulador(self):
        """Reseta o estado do simulador para os valores iniciais."""
        self.memoria = [0] * 256
        self.vetor_reg = [0] * 10
        # O ponteiro da pilha ($sp) começa no final da memória.
        self.vetor_reg[self.reg_dic["$sp"]] = len(self.memoria) - 1
        self.PC = 0
        self.programa = [] # Limpa o programa carregado.
        
        # Limpa as áreas de texto se elas já foram criadas.
        if hasattr(self, 'area_saidas'):
             self.log_saida("Simulador resetado. Carregue um novo arquivo.", clear=True)
             self.atualizar_displays()

    def log_saida(self, mensagem, clear=False):
        """
        Adiciona uma mensagem à área de saídas na GUI.
        :param mensagem: A string a ser exibida.
        :param clear: Se True, limpa a área de texto antes de adicionar a mensagem.
        """
        if clear:
            self.area_saidas.delete('1.0', tk.END)
        self.area_saidas.insert(tk.END, mensagem + "\n")
        self.area_saidas.see(tk.END) # Faz a barra de rolagem descer automaticamente.

    def atualizar_displays(self):
        """Atualiza todas as áreas de texto com o estado atual do simulador."""
        # --- Atualiza Área de Registradores ---
        self.area_registradores.delete('1.0', tk.END)
        self.area_registradores.insert(tk.INSERT, "--- REGISTRADORES ---\n")
        for nome, endereco in self.reg_dic.items():
            valor = self.vetor_reg[endereco]
            # Formata a linha para alinhar os valores e mostrar em decimal e hexadecimal.
            linha = f"{nome:<5}: {valor:<10} (0x{valor:08X})\n"
            self.area_registradores.insert(tk.END, linha)

        # --- Atualiza Área de Código Fonte e Binário ---
        self.area_bin.delete('1.0', tk.END)
        self.area_bin.insert(tk.INSERT, "--- CÓDIGO FONTE E BINÁRIO ---\n")
        for i, instrucao in enumerate(self.programa):
            # Adiciona ">>" para indicar a próxima instrução a ser executada (apontada pelo PC).
            prefixo = ">>" if i == self.PC else "  "
            texto_instrucao = ' '.join(instrucao)
            binario_str = self.traduzir_instrucao_para_binario(instrucao)
            linha = f"{prefixo} {i:<3} {texto_instrucao:<20} | {binario_str}\n"
            self.area_bin.insert(tk.END, linha)

# --- Ponto de Entrada Principal da Aplicação ---
# Este bloco só é executado quando o script é rodado diretamente (não quando é importado).
if __name__ == "__main__":
    root_window = tk.Tk()           # Cria a janela principal.
    app = MipsSimuladorGUI(root_window) # Cria uma instância da nossa classe de simulador.
    root_window.mainloop()          # Inicia o loop de eventos do Tkinter, que mantém a janela aberta e responsiva.
