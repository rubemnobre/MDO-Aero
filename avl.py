import re
import subprocess
import os
pi = 3.14159265358979323846264

def criar_arquivo(aeronave):
    arq = open('./avl/configs/' + aeronave.nome + '.avl', 'w')
    arq.write(aeronave.nome + '\n')
    arq.write('0.0\n')          # Mach
    arq.write('0 0 0.0\n') # IYsym   IZsym   Zsym
    arq.write('%.3f %.3f %.3f\n' % (aeronave.Sw, aeronave.cw, aeronave.bw)) # Sref    Cref    Bref
    arq.write('%.3f 0.0 0.0\n' % aeronave.xcg) # Xref    Yref    Zref

    arq.write("\nSURFACE\n")
    arq.write("Asa\n")
    arq.write("8 1.0 12 1.0\n") # Discretização
    arq.write("YDUPLICATE\n0.0\n")
    arq.write("ANGLE\n%.3f\n" % aeronave.iw)
    arq.write("COMPONENT\n1\n")
    for sect in aeronave.geometria_asa:
        arq.write("SECTION\n")
        arq.write("%.3f %.3f 0.0 %.3f 0\n" % (sect[2], sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
        arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_asa)
    
    arq.write("\nSURFACE\n")
    arq.write("EH\n")
    arq.write("4 1.0 6 1.0\n") # Discretização
    arq.write("YDUPLICATE\n0.0\n")
    arq.write("ANGLE\n%.3f\n" % aeronave.ih)
    arq.write("COMPONENT\n2\n")
    for sect in aeronave.geometria_eh:
        arq.write("SECTION\n")
        arq.write("%.3f %.3f 0.0 %.3f 0\n" % (aeronave.posicoes["eh"][0] + sect[2], sect[0], sect[1])) # Xle    Yle    Zle     Chord   Ainc
        arq.write("AFILE\navl/%s.dat\n" % aeronave.perfil_eh)
    arq.close()

def resultados_avl(aeronave): # CM0, CL0, CLa, CMa, Xnp
    criar_arquivo(aeronave)
    process = subprocess.Popen(['avl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out = process.communicate(bytes('load avl/configs/%s\noper\na a 0\nx\nst\n\nquit\n' % aeronave.nome, 'utf-8'))[0]
    process.terminate()
    output = out.decode('utf-8')
    match = re.search(r'(Cmtot =..........)', output)
    CM0 = float(output[match.start() + 7:match.start() + 17])
    match = re.search(r'(CLtot =..........)', output)
    CL0 = float(output[match.start() + 7:match.start() + 17])
    match = re.search(r'(CLa =...........)', output)
    CLa = float(output[match.start() + 7:match.start() + 17]) * pi/180
    match = re.search(r'(Cma =...........)', output)
    CMa = float(output[match.start() + 7:match.start() + 17]) * pi/180
    match = re.search(r'(Xnp =...........)', output)
    Xnp = float(output[match.start() + 7:match.start() + 17])
    match = re.search(r'(CDtot =...........)', output)
    CD0 = float(output[match.start() + 7:match.start() + 17])
    os.remove('./avl/configs/%s.avl' % aeronave.nome)
    return CM0, CL0, CD0, CLa, CMa, Xnp