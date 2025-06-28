import tkinter

# --- Funções dos botões (sem alterações) ---
def botao_file():
    print("Botão 'File' clicado")

def botao_executa():
    print("Botão 'Executar' clicado")

def botao_reseta():
    print("Botão 'Resetar' clicado")

#janela principal
root = tkinter.Tk()
root.title("Layout com Frames como Separadores")
root.geometry("1280x720")

#frame principal
frame_principal = tkinter.Frame(root, relief="ridge", borderwidth=2)
frame_principal.pack(fill="both", expand=True)

#configuracao do grid
frame_principal.rowconfigure(2, weight=1)
frame_principal.columnconfigure(4, weight=1)

#criacao dos botoes
buttonFile = tkinter.Button(frame_principal, text="File", command=botao_file)
buttonStart = tkinter.Button(frame_principal, text="Executar", command=botao_executa)
buttonReset = tkinter.Button(frame_principal, text="Resetar", command=botao_reseta)

# Trocamos ttk.Separator por um Frame com cor de fundo e espessura definida
separador_vertical = tkinter.Frame(frame_principal, width=2, bg='grey80')
separador_horizontal = tkinter.Frame(frame_principal, height=2, bg='grey80')


#posicionamento dos botoes
buttonFile.grid(row=0, column=0, padx=5, pady=5)
buttonStart.grid(row=0, column=1, padx=5, pady=5)
buttonReset.grid(row=0, column=2, padx=5, pady=5)

#separador horizontal
separador_horizontal.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

#separador vertical
separador_vertical.grid(row=0, column=3, rowspan=2, sticky="ns", padx=10)

root.mainloop()