import random
from models import Monoplano

n_candidatos = 1000

b_min_w = 1.5
c_min_w = 0.2
b_max_w = 2.5
c_max_w = 0.6

b_min_h = 0.2
c_min_h = 0.1
b_max_h = 1.2
c_max_h = 0.4

b_min_v = 0.1
c_min_v = 0.1
b_max_v = 0.5
c_max_v = 0.5

iw_max = 8
ih_max = 8

offset_max = 0.3
n_sect = 3
dist_nariz = 0.2
soma_dims = 3.2 - dist_nariz

perfis_asa = ['e423', 's1223']
perfis_eh = ['e168', 'naca0015']
perfis_ev = ['naca0009', 'e169']

def gerar_inicial():
    aeronaves = []
    for i in range(n_candidatos):
        cr = random.uniform(c_min_w, c_max_w)
        ct = random.uniform(c_min_w, cr)
        br = random.uniform(b_min_w/2, b_max_w/2)
        bt = random.uniform(0.1, b_max_w/2 - br)
        o1 = random.uniform(0, offset_max)
        o2 = random.uniform(0, offset_max)
        b = round(br + bt, 3)
        geometria_asa = [(0, cr, 0), (br, cr, o1), (b, ct, o2)]

        bh = random.uniform(b_min_h/2, b_max_h/2)
        ch = random.uniform(c_min_h, c_max_h)
        
        geometria_eh = [(0, ch, 0), (bh, ch, 0)]

        crv = random.uniform(c_min_v, c_max_v)
        ctv = random.uniform(c_min_v, crv)
        bv = random.uniform(b_min_v, b_max_v)
        
        geometria_ev = [(0, crv, 0), (bv, ctv, round(crv-ctv, 3))]

        iw =  random.uniform(0, iw_max)
        ih =  random.uniform(ih_max, 0)

        posicoes = { 'asa' : (0,0), 'eh' : (soma_dims - ch - b, 0), 'ev' : (soma_dims - ch - b, 0) }
        for perfil_asa in perfis_asa:
            for perfil_eh in perfis_eh:
                for perfil_ev in perfis_ev:
                    aeronaves.append(Monoplano(geometria_asa, perfil_asa, iw, geometria_eh, ih, perfil_eh, geometria_ev, perfil_ev, posicoes))
        print(aeronaves[-1].nome)
        
def reproducao():
    return

gerar_inicial()