import tkinter as tk
from tkinter import filedialog, scrolledtext
from minimips import vetor_reg, memoria, reg_dic, file_path, Executa

caminho_arquivo = ""
stepByStep = False

class MipsInterface:
    # --- Funções dos botões (sem alterações) ---
    def botao_file():
        print("Botão 'File' clicado")
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo",
            filetypes=(
                ("Arquivos Binarios", "*.s"),
                ("Todos os arquivos", "*.*")
            )
        )
        print(file_path)

    def botao_executa():
        Executa = True
        print("Botão 'Executar' clicado")

    def botao_reseta():
        print("Botão 'Resetar' clicado")
        caminho_arquivo = ""
        print(caminho_arquivo)
        vetor_reg = [0] * 10
        memoria = [0] * 256 


    def muda_step():
        global stepByStep
        stepByStep = not stepByStep
        print(str(stepByStep))


    #janela principal
    root = tk.Tk()
    root.title("MINI-MIPS")

    #frame principal
    frame_principal = tk.Frame(root, relief="ridge", borderwidth=2)
    frame_principal.pack(fill="both", expand=True)

    #configuracao do grid
    frame_principal.rowconfigure(2, weight=1)
    frame_principal.columnconfigure(4, weight=1)

    #criacao dos botoes
    buttonFile = tk.Button(frame_principal, text="File", command=botao_file)
    buttonStart = tk.Button(frame_principal, text="Executar", command=botao_executa)
    buttonReset = tk.Button(frame_principal, text="Resetar", command=botao_reseta)
    checkButton = tk.Checkbutton(frame_principal, text="StepByStep", command=muda_step)

    #posicionamento dos botoes
    buttonFile.grid(row=0, column=0, padx=5, pady=5)
    buttonStart.grid(row=0, column=1, padx=5, pady=5)
    buttonReset.grid(row=0, column=2, padx=5, pady=5)
    checkButton.grid(row=0, column=3, padx=5, pady=5)

    #criacao do frame das areas
    frame_meio = tk.Frame(root)
    frame_meio.pack()

    area_registradores = scrolledtext.ScrolledText(frame_meio, width=20, height=20)
    area_registradores.pack(side=tk.LEFT, padx=10)
    area_registradores.insert(tk.INSERT, "Registradores:\n")
    nomes_dos_registradores = ["$zero", "$v0", "$a0", "$t0", "$t1", "$t2", "$t3", "$sp", "$HI", "$LO"]
    for nome_do_registrador in nomes_dos_registradores:
    # Usa o nome para pegar o ENDEREÇO do registrador no dicionário
        endereco = reg_dic[nome_do_registrador]
    # Usa o ENDEREÇO para pegar o VALOR ATUAL na lista de memória
        valor_atual = vetor_reg[endereco]
    # Cria a linha formatada e insira no ScrolledText
        linha = f"{nome_do_registrador}: {valor_atual}\n"
        area_registradores.insert(tk.END, linha)

    area_bin = scrolledtext.ScrolledText(frame_meio, width=50, height=20)
    area_bin.pack(side=tk.LEFT, padx=10)
    area_bin.insert(tk.INSERT, "Binários:\n")

    area_saidas = scrolledtext.ScrolledText(frame_meio, width=50, height=20)
    area_saidas.pack(side=tk.RIGHT, padx=10)
    area_saidas.insert(tk.INSERT, "Saídas:\n")

    root.mainloop()