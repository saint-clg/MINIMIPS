zero = 0;
pilha_sp = []
vetor_reg = [zero,0,0,0,0,0,0,0,pilha_sp,0]
reg_dic = {
    "$zero" : vetor_reg[0],
    "$v0"   : vetor_reg[1],
    "$a0"   : vetor_reg[2],
    "$t0"   : vetor_reg[3],
    "$t1"   : vetor_reg[4],
    "$t2"   : vetor_reg[5],
    "$t3"   : vetor_reg[6],
    "$sp"   : vetor_reg[7],
    "$HI"   : vetor_reg[8],
    "$LO"   : vetor_reg[9]
}
inst_dic = {
    "add"   : [],
    "addi"  : [],
    "sub"   : [],
    "mult"  : [],

}

matriz = []

with open('arquivo.s', 'r', encoding='utf-8') as f:
    linhas = f.read().splitlines()

# Remove linhas vazias
linhas = [linha for linha in linhas if linha.strip() != '']

for linha in linhas:
    # Remove vírgulas internas e separa por espaço
    partes = linha.replace(',', '').split()
    
    # Garante que tenha no mínimo 4 colunas (preenche com None se faltar)
    while len(partes) < 4:
        partes.append(None)
    
    # Adiciona apenas os 4 primeiros elementos à matriz
    matriz.append(partes[:4])
