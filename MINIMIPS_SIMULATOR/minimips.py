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

control_vetor = [0,0,0,0,0,0]
# [RegDest, ALUSrc, MemToReg, RegWrite, MemRead, MemWrite] ind = 6
inst_dic = {
    "add"   : [1,0,0,1,0,0],
    "addi"  : [1,1,0,0,0,0],
    "sub"   : [1,0,0,1,0,0],
    "mult"  : [1,0,0,1,0,0],
    "and"   : [1,0,0,1,0,0],
    "or"    : [1,0,0,1,0,0],
    "sll"   : [1,0,0,1,0,0],
    "lw"    : [0,1,1,1,1,0],
    "sw"    : [0,1,0,0,0,1],
    "lui"   : [0,1,1,1,1,0],
    "slt"   : [1,0,0,1,0,0],
    "slti"  : [1,1,0,0,0,0],
    "syscall"   : [0,0,0,0,0,0]
}

file_path = "C:\\Users\\joao_francisco\\Documents\\GitHub\MINIMIPS\\MINIMIPS_SIMULATOR\\arquivo.s"
PC = 0
EPC = 0
CAUSE = 0

def matriz_program(file_path):
    matriz = []

    with open(file_path, 'r', encoding='utf-8') as f:
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

        return matriz

def intruction_bank(matriz, PC, inst_dic):

    control = inst_dic.get(matriz[PC][0])

    return control

def reg_bank(matriz, PC, reg_vetor, control_vetor):
    if control_vetor[0] == 1:
        RD = matriz[PC][1]
        RS = matriz[PC][2]
        RT = matriz[PC][3]
    

matriz = matriz_program(file_path)
control_vetor = intruction_bank(matriz, PC, inst_dic)


print(control_vetor)
