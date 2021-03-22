from models import Monoplano
from matplotlib import pyplot as plt
import optimizer
import avl
import os
import random

code = str(random.randint(10000, 99999))
os.mkdir('./avl/configs/'+code+'/')
os.mkdir('./avl/configs/%s/geracao-%d' % (code, 0))

avl.caminho_geometrias = './avl/configs/%s/geracao-%d/' % (code, 0)

candidatos = optimizer.gerar_inicial()
ant = 0
n = 100
nota_ant = -1000
notas = []
for j in range(n):
    os.mkdir('./avl/configs/%s/geracao-%d' % (code, j+1))
    avl.caminho_geometrias = './avl/configs/%s/geracao-%d/' % (code,j + 1)
    candidatos = optimizer.reproducao(candidatos, 0.02)
    melhor = max(candidatos, key= lambda a : a.nota)
    print("geração %d: %.3f" % (j+1, melhor.nota))
    print("cp = %.3f CL/CD = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% PV = %.2f pouso = %.2f decolagem = %.2f cma = %.2f arw = %.3f arh = %.3f" % (melhor.posicoes['cp'][0], melhor.CL_CD, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.peso_vazio, melhor.x_pouso, melhor.x_decolagem, melhor.CMa, melhor.ARw, melhor.ARh))
    notas.append(melhor.nota)
    if abs(melhor.nota - sum(notas)/5) < 1 and len(notas) == 5:
        break
    if len(notas) == 5:
        notas.pop(0)

candidatos.sort(key=lambda a : a.nota, reverse=True)
os.mkdir('./avl/configs/%s/resultado' % code)
avl.caminho_geometrias = './avl/configs/%s/resultado/' % code
i = 1
for melhor in candidatos[:10]:
    melhor.nome = '%d'%i
    i += 1
    print("%s\n  cw = %.3f CL/CD = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% PV = %.2f pouso = %.2f decolagem = %.2f perf = %s arw = %.3f arh = %.3f" % (melhor.nome, melhor.cw, melhor.CL_CD, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.peso_vazio, melhor.x_pouso, melhor.x_decolagem, melhor.perfil_asa, melhor.ARw, melhor.ARh))
    avl.criar_arquivo(melhor, False)