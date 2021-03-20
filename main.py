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
for j in range(n):
    os.mkdir('./avl/configs/%s/geracao-%d' % (code, j+1))
    avl.caminho_geometrias = './avl/configs/%s/geracao-%d/' % (code,j + 1)
    candidatos = optimizer.reproducao(candidatos, 0.001*(n - j))
    melhor = max(candidatos, key= lambda a : a.nota)
    print("geração %d: %.3f" % (j, melhor.nota))
    print("CM0 = %.4f CMa = %.4f CL/CD = %.4f atrim = %.3f Sw = %.3f ME = %.2f%% PV = %.2f" % (melhor.CM0, melhor.CMa, melhor.CL0/melhor.CD0, melhor.atrim, melhor.Sw, melhor.ME*100, melhor.peso_vazio))

candidatos.sort(key=lambda a : a.nota)
os.mkdir('./avl/configs/%s/resultado' % code)
avl.caminho_geometrias = './avl/configs/%s/resultado/' % code
for escolhido in candidatos[:10]:
    print("%s\n\tSw = %.2f bw = %.2f VH = %.2f VV = %.2f atrim = %.2f ME = %.2f%% PV = %.2f" % (escolhido.nome, escolhido.Sw, escolhido.bw, escolhido.VH, escolhido.VV, escolhido.atrim, escolhido.ME*100, escolhido.peso_vazio))
    avl.criar_arquivo(escolhido)