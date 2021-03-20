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
n = 50
nota_ant = -1000
notas = []
for j in range(n):
    os.mkdir('./avl/configs/%s/geracao-%d' % (code, j+1))
    avl.caminho_geometrias = './avl/configs/%s/geracao-%d/' % (code,j + 1)
    candidatos = optimizer.reproducao(candidatos, 0.0005*(n - j))
    melhor = max(candidatos, key= lambda a : a.nota)
    print("geração %d: %.3f" % (j+1, melhor.nota))
    print("CM0 = %.4f CMa = %.4f CL/CD = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% PV = %.2f pouso = %.2f perf = %s" % (melhor.CM0, melhor.CMa, melhor.CL_CD, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.peso_vazio, melhor.x_pouso, melhor.perfil_asa))
    notas.append(melhor.nota)
    if abs(melhor.nota - sum(notas)/5) < 0.5 and len(notas) == 10:
        break
    if len(notas) == 9:
        notas.pop(0)

candidatos.sort(key=lambda a : a.nota)
os.mkdir('./avl/configs/%s/resultado' % code)
avl.caminho_geometrias = './avl/configs/%s/resultado/' % code
for escolhido in candidatos[:10]:
    print("%s\n\tSw = %.2f bw = %.2f VH = %.2f VV = %.2f atrim = %.2f ME = %.2f%% PV = %.2f" % (escolhido.nome, escolhido.Sw, escolhido.bw, escolhido.VH, escolhido.VV, escolhido.atrim, escolhido.ME*100, escolhido.peso_vazio))
    avl.criar_arquivo(escolhido)