from tools import avaliar_geometria, cla, a0l, constantes_perfil
import random
from avl import resultados_avl
import math

n = 1
rho = 1.16
g = 9.81
astall = 13
mu = 0.09
v_cruzeiro = 16
pi = 3.1415926535897932384626433832795

nomes = ['arara', 'papagaio', 'pavao', 'pomba', 'avestruz', 'galinha', 'galo', 'aguia', 'gaviao', 'harpia', 'tucano', 'pinguim']
class Monoplano:
    geometria_asa = [] # Tuples de formato semelhante ao do XFLR5 (y, corda, offset, perfil)
    geometria_eh = []
    geometria_ev = []
    posicoes = {} # Referência: centro do bordo de ataque da asa
    
    def __init__(self, asa, perfil_asa, iw, eh, perfil_eh, ih, ev, perfil_ev, posicoes, mtow):
        self.geometria_asa = asa.copy()
        self.geometria_eh = eh.copy()
        self.geometria_ev = ev.copy()
        self.posicoes = posicoes.copy()
        self.atualizar_geometria()
        self.mtow = mtow
        self.xcg, self.carga_paga, self.peso_vazio = self.estimar_cg()
        #self.xcg = 0.2*self.cw
        self.iw = iw
        self.ih = ih
        #self.atualizar_constantes()
        self.perfil_asa = perfil_asa
        self.perfil_eh = perfil_eh
        self.perfil_ev = perfil_ev
        self.nome = random.choice(nomes) + '-' + random.choice(nomes) + '-' + str(random.randint(1000, 9999))
        self.hw = 0.2416 #altura da asa
        self.res0 = resultados_avl(self, ('alpha', 0))
        self.CM0 = self.res0['CM']
        self.CL0 = self.res0['CL']
        self.CLa = self.res0['CLa']
        self.CMa = self.res0['CMa']
        self.Xnp = self.res0['Xnp']

        self.resgnd = resultados_avl(self, ('solo', 0))
        self.phi = ((16*self.hw/self.bw)**2)/(1 + ((16*self.hw/self.bw)**2))
        self.K = 1/(pi*0.85*self.ARw)
        self.CD0 = self.resgnd['CD'] - self.K*self.CL0**2

        self.restrim = resultados_avl(self, ('trim', 0))
        if self.restrim != None:
            self.atrim = self.restrim['Alpha']
            try:
                self.CL_CD = self.restrim['CL']/self.restrim['CD']
            except:
                self.CL_CD = 100
            self.CLtrim = self.restrim['CL']
        else:
            self.atrim = -self.CM0/self.CMa
            self.CLtrim = (self.CLa*self.atrim + self.CL0)
            self.CL_CD = self.CLtrim/self.polar_arrasto(self.CLtrim, 1)
        self.ME = (self.Xnp - self.xcg)/self.cw
        
        self.CLmax = self.resgnd['CL'] + (astall - self.iw)*self.resgnd['CLa']
        self.vestol = math.sqrt(2*self.mtow*g/(rho*self.Sw*self.CLmax))

        vd = 1.2*self.vestol
        L = 0.5*rho*self.Sw*self.resgnd['CL']*(0.7*vd)**2
        D = 0.5*rho*self.Sw*self.polar_arrasto(self.resgnd['CL'], self.phi)* (0.7*vd)**2
        T = tracao(0.7*vd)
        W = self.mtow*g
        self.x_decolagem = 1.44*(W**2)/(g*rho*self.Sw*self.CLmax*(T - D - mu*(W - L)))
        #self.x_decolagem = self.decolagem()

        vp = 1.3*self.vestol
        L = 0.5*rho*self.Sw*self.resgnd['CL']*(0.7*vp)**2
        D = 0.5*rho*self.Sw*self.polar_arrasto(self.resgnd['CL'], self.phi)* (0.7*vp)**2
        self.x_pouso = 1.69*(W**2)/(g*rho*self.Sw*self.CLmax*(D + mu*(W - L)))
        #self.x_pouso = self.pouso()

        self.avaliar()
    
    def atualizar_geometria(self):
        self.Sw, self.bw, self.cw, self.ARw, self.Xacw = avaliar_geometria(self.geometria_asa)
        self.Sh, self.bh, self.ch, self.ARh, self.Xach = avaliar_geometria(self.geometria_eh)
        self.Sv, self.bv, self.cv, self.ARv, self.Xacv = avaliar_geometria(self.geometria_ev)
        self.lh = self.posicoes["eh"][0] - 0.25*(self.cw - self.ch)
        self.lv = self.posicoes["ev"][0] - 0.25*(self.cw - self.cv)
        self.VH = (self.lh*self.Sh)/(self.cw*self.Sw)
        self.VV = (self.Sv*self.lv)*2/(self.Sw*self.bw)

    def polar_arrasto(self, CL, phi):
        return self.CD0 + phi*self.K*(CL**2)

    def estimar_cg(self):
        massaHELICE2021 = 0.11174  # ajustar #
        bracoHELICE2019 = 0.0089
        momentoHELICE = g * massaHELICE2021 * bracoHELICE2019

        massaMOTOR2021 = 0.7034  # ajustar #
        bracoMOTOR2019 = 0.0974  # ajustar #
        momentoMOTOR = g * massaMOTOR2021 * bracoMOTOR2019

        massaTANQUEVAZIO2021 = 0.037  # ajustar #
        bracoTANQUEVAZIO2019 = 0.1885
        momentoTANQUEVAZIO = g * massaTANQUEVAZIO2021 * bracoTANQUEVAZIO2019

        massaCAIXAELETRICO2019 = 0.13244
        bracoCAIXAELETRICO2019 = 0.2588
        momentoCAIXAELETRICO = g * massaCAIXAELETRICO2019 * bracoCAIXAELETRICO2019

        massaFUSELAGEM2019 = 0.40628
        bracoFUSELAGEM2019 = 0.4846
        momentoFUSELAGEM = g * massaFUSELAGEM2019 * bracoFUSELAGEM2019

        massaEH2019 = 0.16235
        areaEH2019 = 0.21

        massaEH2021 = (self.bh * self.ch) * (massaEH2019 / areaEH2019)
        bracoEH2021 = 0.25 + self.Xacw + self.lh + 0.15 * self.ch
        momentoEH = g * massaEH2021 * bracoEH2021

        massaEV2019 = 0.06406
        areaEV2019 = 0.10236

        massaEV2021 = 2*self.Sv * (massaEV2019 / areaEV2019)
        bracoEV2021 = 0.25 + self.Xacw + self.lv + 0.1 * self.cv
        momentoEV = g * massaEV2021 * bracoEV2021

        massaASA2019 = 0.73368
        areaASA2019 = 0.9

        massaASA2021 = self.Sw * (massaASA2019 / areaASA2019)
        bracoASA2021 = 0.25 + 0.4 * self.cw  # considerando que o berco do motor tera 0.25 e o CG da asa sera em 40 % da cma #
        momentoASA = g * massaASA2021 * bracoASA2021

        carga_paga = self.mtow - (massaHELICE2021 + massaMOTOR2021 + massaTANQUEVAZIO2021 + massaCAIXAELETRICO2019 + massaFUSELAGEM2019 + massaASA2021 + massaEH2021 + massaEV2021)

        massaCARGAPAGA = carga_paga  # ajustar #
        bracoCARGAPAGA2019 = 0.25 + self.posicoes['cp'][0]
        momentoCARGAPAGA = g * massaCARGAPAGA * bracoCARGAPAGA2019

        SomaMomentos = momentoHELICE + momentoMOTOR + momentoTANQUEVAZIO + momentoCAIXAELETRICO + momentoFUSELAGEM + \
                        momentoASA + momentoEH + momentoEV + momentoCARGAPAGA
        SomaPesos = g * self.mtow

        XCG = SomaMomentos / SomaPesos

        PosXCG = XCG - 0.25
        peso_vazio = self.mtow - carga_paga
        return PosXCG, carga_paga, peso_vazio
    
    def decolagem(self):
        CL = self.resgnd['CL']
        CD = self.resgnd['CD']
        W = self.mtow*g
        v = 0
        x = 0
        t = 0
        dt = 0.01
        L = 0
        while L <= W:
            L = 0.5*rho*v*v*self.Sw*CL
            D = 0.5*rho*v*v*self.Sw*CD
            R = mu*(W-L)
            T = tracao(v)
            a = (T - R - D)/self.mtow
            v += a*dt
            x += v*dt + 0.5*a*dt*dt
            t += dt
            if x >= 100:
                break
        return x
    
    def decolagem_old(self):
        Lf = 0.11  # Alterar - LARGURA DA FUSELAGEM 0.11 POR ENQUANTO#

        Areah = self.Sh
        Arh = self.ARh
        HT = self.posicoes['eh'][1]
        BHT = self.bh
        CHT = self.ch
        modelo = "Monoplano"
        Areaw = self.Sw
        B = self.bw
        cordar = self.geometria_asa[0][1]
        Ar = self.ARw
        MTOW = self.mtow
        v_ari = 0
        CMA = self.cw
        CVMED = self.cv
        viscosidade = 1.6 * 10 ** (-5)

        eh = 1.78 * (1 - (0.045 * (Arh ** 0.68))) - 0.64  # coeficiente de Oswald (Gudmudsson)#

        kh = 1 / (pi * Arh * eh)

        hw = 0.2416  # (valor fixado incialmente) Altura da asa em relacao ao solo#
        ht = hw + HT

        sigmah = (16 * ht / BHT) ** 2 / (1 + (16 * ht / BHT) ** 2)
        Sweth = (Areah - (CHT * 0.11)) * 1.07 * 2

        c_atrito = 0.09
        clh = (c_atrito) / (2 * kh * sigmah)

        if modelo == "Monoplano" or modelo == "MonoVoador":
            sigmaw = (16 * hw / B) ** 2 / (1 + (16 * hw / B) ** 2)  # Prediz o efeito solo#
            Swetw = (Areaw - (cordar * Lf)) * 1.07 * 2  # Area molhada da asa#
            if modelo == "Monoplano":
                ew = 1.78 * (1 - (0.045 * (Ar ** 0.68))) - 0.64  # coeficiente de Oswald (Gudmudsson)#

        kw = 1 / (pi * Ar * ew)  # Constante de proporcionalidade#
        clw = (c_atrito) / (
                2 * kw * sigmaw)  # Coeficiente de sustentacao para o menor comprimento de pista para decolagem#
        m = MTOW  # MTOW desejado#
        x = 0
        v = 0  # Velocidade em relacao ao solo#
        t = 0
        v_ar = v + v_ari
        L = 0.5 * rho * (v_ar ** 2) * Areaw * clw
        delta_t = 0.01

        while L < m * g:  # decolagem#
            Re = rho * v_ar * CMA / viscosidade
            if Re > 0:
                if Re > 3.5e5:  # De acordo com o Roskam, a partir daqui acaba sendo parte laminar e parte turbulento#
                    cfw = 0.455 / (
                            (math.log10(Re)) ** 2.58) - 1700 / Re  # Coeficiente de Friccao de arrasto transicao(Gudmudsson)#
                elif Re > 1e7:
                    cfw = 0.455 / ((math.log10(Re)) ** 2.58)  # Coeficiente de Friccao turbulento#
                else:
                    cfw = 1.328 / (Re ** 0.5)  # Coeficiente de Friccao de arrasto laminar (Gudmudsson)#
                Rev = rho * v_ar * CVMED / viscosidade
                if Rev > 3.5e5:  # De acordo com o Roskam, a partir daqui acaba sendo parte laminar e parte turbulento#
                    cfv = 0.455 / (
                            (math.log10(Re)) ** 2.58) - 1700 / Re  # Coeficiente de Friccao de arrasto transicao(Gudmudsson)#
                elif Rev > 1e7:
                    cfv = 0.455 / ((math.log10(Re)) ** 2.58)  # Coeficiente de Friccao turbulento#
                else:
                    cfv = 1.328 / (Re ** 0.5)  # Coeficiente de Friccao de arrasto laminar (Gudmudsson)#

                cdfw = (Swetw / Areaw) * cfw

                cdw = cdfw + sigmaw * kw * clw ** 2  # Coeficiente de arrasto#
                cdv = cfv
                Dv = 0.5 * rho * (v_ar ** 2) * Areah * cdv
            
                if modelo == "Monoplano" or modelo == "Biplano":
                    Reh = rho * v_ar * CHT / viscosidade
                    if Reh > 3.5 * 10 ** 5:  # De acordo com o Roskam, a partir daqui acaba sendo parte laminar e parte turbulento#
                        cfh = 0.455 / (
                                (math.log10(Reh)) ** 2.58) - 1700 / Reh  # Coeficiente de Friccao de arrasto transicao(Gudmudsson)#
                    elif Reh > 1 * 10 ** 7:
                        cfw = 0.455 / ((math.log10(Re)) ** 2.58)  # Coeficiente de Friccao turbulento#
                    else:
                        cfh = 1.328 / (Reh ** 0.5)  # Coeficiente de Friccao de arrasto laminar (Gudmudsson)#

                    cdfh = (Sweth / Areah) * cfh
                    cdh = cdfh + sigmah * kh * clh ** 2

                    Lw = 0.5 * rho * (v_ar ** 2) * Areaw * clw
                    Lh = 0.5 * rho * (v_ar ** 2) * Areah * clh
                    L = Lw - Lh

                    Dw = 0.5 * rho * (v_ar ** 2) * Areaw * cdw
                    Dh = 0.5 * rho * (v_ar ** 2) * Areah * cdh
                    D = Dw + Dh + Dv
                else:
                    L = 0.5 * rho * (v_ar ** 2) * Areaw * clw
                    Dw = 0.5 * rho * (v_ar ** 2) * Areaw * cdw
                    D = Dw + Dv
            else:
                L = 0
                D = 0

            t = t + delta_t
            
            T = -0.0144 * v ** 2 - 0.935 * v + 46.4  # Dados que vem do ensaio de tracao#
            R = c_atrito * (m * g - L)  # Forca de atrito#
            Eforcas = T - D - R
            a = Eforcas / m  # aceleracao#
            v = v + delta_t * a  # velocidade instantanea da aeronave#
            x = x + delta_t * v  # pista#
            v_ar = v + v_ari

        v = v - delta_t * a  # Retirar o ultimo acrescimo#
        x = x - delta_t * v
        cl = L / (0.5 * rho * (v ** 2) * (Areaw))
        return x

    def pouso(self):
        CL = self.resgnd['CL']
        CD = self.resgnd['CD']
        W = self.mtow*g
        v = 1.3*self.vestol
        x = 0
        t = 0
        dt = 0.01
        L = 0
        while v >= 0.1:
            L = 0.5*rho*v*v*self.Sw*CL
            D = 0.5*rho*v*v*self.Sw*CD
            R = mu*(W-L)
            a = (-R - D)/self.mtow
            v += a*dt
            x += v*dt + 0.5*a*dt*dt
            t += dt
        return x

    def avaliar(self):
        res = 0
        # Requesitos de estabilidade estática e dinâmica (sadraey tabela 6.3)
        CLcruzeiro = (2*g*self.mtow)/(rho*(v_cruzeiro**2)*self.Sw)
        
        self.dist_fuga = math.sqrt((self.posicoes['eh'][1])**2 + (self.geometria_asa[0][1] - self.posicoes['eh'][0])**2)

        #res += func_erro_neg(self.cw, self.dist_fuga, 10000)
        res += func_erro_neg(self.CLtrim, self.CLmax, 1000)
        res += func_erro_neg(self.CMa, 0, 100000)
        res += func_erro_neg(0, self.CM0, 1000)
        res += func_erro_neg(0, self.atrim, 1000)
        res += func_erro_neg(0.05, self.ME, 100000)
        res += func_erro_neg(self.ARh, 11, 1000)

        res += 20*func_erro(self.CMa * 180/pi, -0.1, -0.8)
        res += 20*func_erro(self.res0['CMq'] * 180/pi, -5, -40)
        res += 20*func_erro(self.res0['Cnb'] * 180/pi, 0.05, 0.4)
        res += 20*func_erro(self.res0['Cnr'] * 180/pi, -0.1, -1)
        res += 1000*func_erro(self.ME*100, 5, 15)

        res += 500*func_erro(self.atrim, 3, 9)
        res += 3*func_erro(self.VH, 0.3, 0.5)
        res += 3*func_erro(self.VV, 0.02, 0.05)
        res += 2*func_erro(self.CL_CD, 10, 50)
        res += 5*func_erro(self.x_pouso, 80, 120)
        res += 100*func_erro(self.x_decolagem, 49.5, 50)
        res += 20*func_erro(self.CLtrim, CLcruzeiro - 0.1, CLcruzeiro + 0.1)
        res += 5*func_erro(self.ARw, 4, 8)
        res += 50*func_erro(self.ARh, 3, 5)
        res += 1200*(self.carga_paga)**2
        self.nota = res

def func_erro(valor, bot, top):
    weight = 4/((bot-top)**2)
    return -weight*(valor - bot)*(valor - top)

def func_erro_neg(valor, top, w):
    if valor < top:
        return 1
    else:
        return 1-(w*(valor-top))**2

def tracao(v):
    return 46.439 - 0.935*v - 0.0144*v*v
