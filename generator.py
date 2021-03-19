import random
from models import Monoplano
from avl import criar_arquivo

n_candidatos = 100
n_selecionados = 50

b_min_w = 1.5
c_min_w = 0.2
b_max_w = 3.0
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
ih_max = -8

offset_max = 0.3
n_sect = 3
dist_nariz = 0.25
soma_dims = 3.2 - dist_nariz

perfis_asa = ['s1223'] #, 's1223']
perfis_eh = ['e168'] #, 'naca0015']
perfis_ev = ['naca0009'] #, 'e169']

def gerar_inicial():
    aeronaves = []
    for i in range(n_candidatos):
        cr = random.uniform(c_min_w, c_max_w)
        ct = random.uniform(c_min_w, cr)
        br = random.uniform(b_min_w/2, b_max_w/2 - 0.1)
        bt = random.uniform(0.1, b_max_w/2 - br)
        o1 = random.uniform(0, offset_max)
        b = br + bt
        geometria_asa = [(0, cr, 0), (br, cr, 0), (b, ct, o1)]

        bh = random.uniform(b_min_h/2, b_max_h/2)
        ch = random.uniform(c_min_h, c_max_h)
        
        geometria_eh = [(0, ch, 0), (bh, ch, 0)]

        crv = random.uniform(c_min_v, c_max_v)
        ctv = random.uniform(c_min_v, crv)
        bv = random.uniform(b_min_v, b_max_v)
        
        geometria_ev = [(0, crv, 0), (bv, ctv, crv-ctv)]

        iw =  random.uniform(0, iw_max)
        ih =  random.uniform(ih_max, 0)

        posicoes = { 'asa' : (0,0), 'eh' : (soma_dims - ch - b*2, 0), 'ev' : (soma_dims - crv - b*2, 0) }
        for perfil_asa in perfis_asa:
            for perfil_eh in perfis_eh:
                for perfil_ev in perfis_ev:
                    aeronaves.append(Monoplano(geometria_asa, perfil_asa, iw, geometria_eh, perfil_eh, ih, geometria_ev, perfil_ev, posicoes))
    return aeronaves

def variar(aeronave, sigma):
    geometria_asa = aeronave.geometria_asa.copy()
    geometria_eh = aeronave.geometria_eh.copy()
    geometria_ev = aeronave.geometria_ev.copy()

    br, cr, o1 = geometria_asa[1]
    b, ct, o2 = geometria_asa[2]
    bt = b - br
    
    ch = geometria_eh[0][1]
    bh = geometria_eh[1][0]

    crv = geometria_ev[0][1]
    ctv = geometria_ev[1][1]
    bv  = geometria_ev[1][0]
    
    b  = trunc_gauss(b,  sigma, br, b_max_w/2)
    bt = trunc_gauss(bt, sigma, 0.1, b_max_w/2 - br)
    cr = trunc_gauss(cr, sigma, ct, c_max_w)
    o1 = trunc_gauss(o1, sigma, 0, offset_max)
    ct = trunc_gauss(ct, sigma, c_min_w, cr)
    br = b - bt

    ch = trunc_gauss(ch, sigma, c_min_h, c_max_h)
    bh = trunc_gauss(bh, sigma, b_min_h/2, b_max_h/2)

    ctv = trunc_gauss(ctv, sigma, c_min_v, crv)
    crv = trunc_gauss(crv, sigma, ctv, c_max_v)
    bv = trunc_gauss(bv, sigma, b_min_v, b_max_v)

    iw = trunc_gauss(aeronave.iw, sigma*10, 0, iw_max)
    ih = trunc_gauss(aeronave.ih, sigma, ih_max, 0)
    
    geometria_asa = [(0, cr, 0), (br, cr, 0), (b, ct, o1)]
    geometria_eh = [(0, ch, 0), (bh, ch, 0)]
    geometria_ev = [(0, crv, 0), (bv, ctv, crv-ctv)]

    posicoes = { 'asa' : (0,0), 'eh' : (soma_dims - ch - b*2, 0), 'ev' : (soma_dims - crv - b*2, 0) }

    return Monoplano(geometria_asa, aeronave.perfil_asa, iw, geometria_eh, aeronave.perfil_eh, ih, geometria_ev, aeronave.perfil_ev, posicoes)

def nota(aeronave):
    res = 0
    if aeronave.lh <= 0 or aeronave.lv <= 0:
        return -1000
    if aeronave.CM0 < 0:
        res -= 100
    res += -abs(aeronave.atrim - 5)
    res += aeronave.CL0*0.2/aeronave.CD0
    res += aeronave.Sw
    return res

def reproducao(gerados, sigma):
    pais = sorted(gerados, key=nota, reverse=True)[:n_selecionados]
    filhos = []
    j = 0
    for pai in pais:
        for i in range(int(len(gerados)/len(pais))):
            filhos.append(variar(pai, sigma))
            j += 1
        #print("%d/%d" % ( j, len(gerados) ))
    return filhos

def trunc_gauss(mu, sigma, bottom, top):
    a = random.gauss(mu,sigma)
    if(top < bottom or not(bottom <= mu <= top)):
        raise Exception("fora dos limites, val = %.2f bot = %.2f top = %.2f" % (mu, bottom, top))
    while not(bottom <= a <= top):
        a = random.gauss(mu,sigma)
    return a

candidatos = gerar_inicial()
ant = 0
n = 100
for j in range(n):
    candidatos = reproducao(candidatos, 0.0001*(n - j))
    melhor = max(candidatos, key=nota)
    print("geração %d: %.3f" % (j, nota(melhor)))
    print("CM0 = %.4f CMa = %.4f CL/CD = %.4f atrim = %.3f Sw = %.3f" % (melhor.CM0, melhor.CMa, melhor.CL0/melhor.CD0, melhor.atrim, melhor.Sw))

criar_arquivo(melhor)
print("Sw = %.3f\nVH = %.3f\nVV = %.3f\nlh = %.2f\nlv = %.2f\nBw = %.2f, cw = %.2f" % (melhor.Sw, melhor.VH, melhor.VV, melhor.lh, melhor.lv, melhor.bw, melhor.cw))