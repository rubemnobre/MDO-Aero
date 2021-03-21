import re
import subprocess
import os
pi = 3.14159265358979323846264

caminho_perfis = './avl/'
caminho_geometrias = './avl/configs/'

def criar_arquivo(aeronave, efeito_solo):
    if efeito_solo:
        arq = open(caminho_geometrias + aeronave.nome + '-ge' + '.avl', 'w')
        arq.write(aeronave.nome + '\n')
        arq.write('0.0\n')          # Mach
        arq.write('0 1 %.2f\n' % -aeronave.hw) # IYsym   IZsym   Zsym
        arq.write('%.2f %.2f %.2f\n' % (aeronave.Sw, aeronave.cw, aeronave.bw)) # Sref    Cref    Bref
        arq.write('%.2f 0.0 0.0\n' % aeronave.xcg) # Xref    Yref    Zref
    else:
        arq = open(caminho_geometrias + aeronave.nome + '.avl', 'w')
        arq.write(aeronave.nome + '\n')
        arq.write('0.0\n')          # Mach
        arq.write('0 0 0.0\n') # IYsym   IZsym   Zsym
        arq.write('%.2f %.2f %.2f\n' % (aeronave.Sw, aeronave.cw, aeronave.bw)) # Sref    Cref    Bref
        arq.write('%.2f 0.0 0.0\n' % aeronave.xcg) # Xref    Yref    Zref
    arq.write("#M %.2f" % aeronave.mtow)
    arq.write("\nSURFACE\n")
    arq.write("Asa\n")
    arq.write("8 1.0 12 1.0\n") # Discretização
    arq.write("YDUPLICATE\n0.0\n")
    arq.write("ANGLE\n%.0f\n" % aeronave.iw)
    arq.write("COMPONENT\n1\n")
    for sect in aeronave.geometria_asa:
        arq.write("SECTION\n")
        arq.write("%.2f %.2f 0.0 %.2f 0\n" % (sect[2], sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
        arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_asa)
    
    arq.write("\nSURFACE\n")
    arq.write("EH\n")
    arq.write("4 1.0 6 1.0\n") # Discretização
    arq.write("YDUPLICATE\n0.0\n")
    arq.write("ANGLE\n%.0f\n" % aeronave.ih)
    arq.write("COMPONENT\n2\n")
    for sect in aeronave.geometria_eh:
        arq.write("SECTION\n")
        arq.write("%.2f %.2f %.2f %.2f 0\n" % (aeronave.posicoes["eh"][0] + sect[2], sect[0], aeronave.posicoes["eh"][1], sect[1])) # Xle    Yle    Zle     Chord   Ainc
        arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_eh)

    arq.write("\nSURFACE\n")
    arq.write("EV\n")
    arq.write("4 1.0 6 1.0\n") # Discretização
    arq.write("YDUPLICATE\n0.0\n")
    arq.write("COMPONENT\n2\n")
    for sect in aeronave.geometria_ev:
        arq.write("SECTION\n")
        arq.write("%.2f %.2f %.2f %.2f 0\n" % (aeronave.posicoes["ev"][0] + sect[2], aeronave.bh/2, sect[0] +  aeronave.posicoes["ev"][1], sect[1])) # Xle    Yle    Zle     Chord   Ainc
        arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_ev)
    arq.close()

def resultados_avl(aeronave, alpha, efeito_solo): # CM0, CL0, CLa, CMa, Xnp
    criar_arquivo(aeronave, efeito_solo)
    process = subprocess.Popen(['avl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if efeito_solo == False:
        out = process.communicate(bytes('load %s\noper\na a %.3f\nx\nst\n\nquit\n' % (caminho_geometrias + aeronave.nome, alpha), 'utf-8'))[0]
    else:
        out = process.communicate(bytes('load %s\noper\na a %.3f\nx\nst\n\nquit\n' % (caminho_geometrias + aeronave.nome + '-ge', alpha), 'utf-8'))[0]
    process.terminate()
    output = out.decode('utf-8')
    results = dict()
    
    match = re.search(r'(Cmtot =..........)', output)
    results['CM'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CLtot =..........)', output)
    results['CL'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CLa =...........)', output)
    results['CLa'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cma =...........)', output)
    results['CMa'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cmq =...........)', output)
    results['CMq'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cnb =...........)', output)
    results['Cnb'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cnr =...........)', output)
    results['Cnr'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Xnp =...........)', output)
    results['Xnp'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CDtot =...........)', output)
    results['CD'] = float(output[match.start() + 7:match.start() + 17])

    return results