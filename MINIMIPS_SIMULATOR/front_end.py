import tkinter as tk
from tkinter import filedialog, scrolledtext

# --- Funções dos botões (sem alterações) ---
def botao_file():
    print("Botão 'File' clicado")

def botao_executa():
    print("Botão 'Executar' clicado")

def botao_reseta():
    print("Botão 'Resetar' clicado")

#janela principal
root = tk.Tk()
root.title("Layout com Frames como Separadores")

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

#posicionamento dos botoes
buttonFile.grid(row=0, column=0, padx=5, pady=5)
buttonStart.grid(row=0, column=1, padx=5, pady=5)
buttonReset.grid(row=0, column=2, padx=5, pady=5)

#criacao do frame das areas
frame_meio = tk.Frame(root)
frame_meio.pack()

area_registradores = scrolledtext.ScrolledText(frame_meio, width=20, height=20)
area_registradores.pack(side=tk.LEFT, padx=10)
area_registradores.insert(tk.INSERT, "Registradores:\n")

area_bin = scrolledtext.ScrolledText(frame_meio, width=50, height=20)
area_bin.pack(side=tk.LEFT, padx=10)
area_bin.insert(tk.INSERT, "Binários:\n")

area_saidas = scrolledtext.ScrolledText(frame_meio, width=50, height=20)
area_saidas.pack(side=tk.RIGHT, padx=10)
area_saidas.insert(tk.INSERT, "Saídas:\n")

root.mainloop()