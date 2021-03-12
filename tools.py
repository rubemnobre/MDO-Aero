def avaliar_geometria(geometria):
    if len(geometria) == 0:
        return 0, 0, 0, 0
    b = 2*geometria[-1][0] # Envergadura
    S = 0
    c = 0
    for i in range(1, len(geometria)):
        h = geometria[i][0] - geometria[i-1][0]
        cm = (geometria[i][1] + geometria[i-1][1])
        S += h*cm
        ck = geometria[i][1]
        ck1 = geometria[i-1][1]
        c += (ck1**2 + ck1*ck + ck**2)*h/3 # Integração do cma
    c = 2*c/S
    AR = b*b/S
    return S, b, c, AR