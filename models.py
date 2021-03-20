from tools import avaliar_geometria, cla, a0l, constantes_perfil
import random
from avl import resultados_avl
import math

n = 1
rho = 1.16
g = 9.81
CLmax = 2.3
mu = 0.09
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
        self.iw = iw
        self.ih = ih
        #self.atualizar_constantes()
        self.perfil_asa = perfil_asa
        self.perfil_eh = perfil_eh
        self.perfil_ev = perfil_ev
        self.nome = random.choice(nomes) + '-' + random.choice(nomes) + '-' + str(random.randint(1000, 9999))
        self.res0 = resultados_avl(self, 0)
        self.CM0 = self.res0['CM']
        self.CL0 = self.res0['CL']
        self.CLa = self.res0['CLa']
        self.CMa = self.res0['CMa']
        self.Xnp = self.res0['Xnp']
        self.K = 1/(pi*0.85*self.ARw)
        self.CD0 = self.res0['CD'] - self.K*self.CL0*self.CL0
        self.atrim = -self.CM0/self.CMa
        self.ME = (self.Xnp - self.xcg)/self.bw
        CL = self.CL0 + self.atrim*self.CLa
        self.CL_CD = CL/self.polar_arrasto(CL)
        
        self.vestol = math.sqrt(2*self.mtow*g/(rho*self.Sw*CLmax))

        vd = 1.1*self.vestol
        L = 0.5*rho*self.Sw*self.CL0*(0.7*vd)**2
        D = 0.5*rho*self.Sw*self.polar_arrasto(self.CL0)* (0.7*vd)**2
        T = tracao(0.7*vd)
        W = self.mtow*g
        self.x_decolagem = 1.44*(W**2)/(g*rho*self.Sw*CLmax*(T - D - mu*(W - L)))

        vp = 1.3*self.vestol
        L = 0.5*rho*self.Sw*self.CL0*(0.7*vp)**2
        D = 0.5*rho*self.Sw*self.polar_arrasto(self.CL0)* (0.7*vp)**2
        self.x_pouso = 1.69*(W**2)/(g*rho*self.Sw*CLmax*(D + mu*(W - L)))

        self.avaliar()
    
    def atualizar_geometria(self):
        self.Sw, self.bw, self.cw, self.ARw, self.Xacw = avaliar_geometria(self.geometria_asa)
        self.Sh, self.bh, self.ch, self.ARh, self.Xach = avaliar_geometria(self.geometria_eh)
        self.Sv, self.bv, self.cv, self.ARv, self.Xacv = avaliar_geometria(self.geometria_ev)
        self.lh = self.posicoes["eh"][0] - 0.25*(self.cw - self.ch)
        self.lv = self.posicoes["ev"][0] - 0.25*(self.cw - self.cv)
        self.VH = (self.lh*self.Sh)/(self.cw*self.Sw)
        self.VV = (self.Sv*self.lv)*2/(self.Sw*self.bw)

    def polar_arrasto(self, CL):
        return self.CD0 + self.K*(CL**2)

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
        bracoCARGAPAGA2019 = 0.35
        momentoCARGAPAGA = g * massaCARGAPAGA * bracoCARGAPAGA2019

        SomaMomentos = momentoHELICE + momentoMOTOR + momentoTANQUEVAZIO + momentoCAIXAELETRICO + momentoFUSELAGEM + \
                        momentoASA + momentoEH + momentoEV + momentoCARGAPAGA
        SomaPesos = g * self.mtow

        XCG = SomaMomentos / SomaPesos

        PosXCG = XCG - 0.25
        peso_vazio = self.mtow - carga_paga
        return PosXCG, carga_paga, peso_vazio
    
    def avaliar(self):
        res = 0
        # Requesitos de estabilidade estática e dinâmica (sadraey tabela 6.3)
        if self.CM0 < 0:
            res = -1000
        res += 1*func_erro(self.CMa * 180/pi, -0.3, -1.5)
        res += 1*func_erro(self.res0['CMq'] * 180/pi, -5, -40)
        res += 1*func_erro(self.res0['Cnb'] * 180/pi, 0.05, 0.4)
        res += 1*func_erro(self.res0['Cnr'] * 180/pi, -0.1, -1)
        res += 10*func_erro(self.ME*100, 5, 15)

        res += func_erro(self.VH, 0.3, 0.5)
        res += 0.3*func_erro(self.VV, 0.03, 0.05)
        res += 2*func_erro(self.atrim, 0, 6)
        res += 5*func_erro(self.CL_CD, 5, 20)
        res += func_erro(self.x_decolagem, 48, 50)
        res += -10*self.peso_vazio
        res += 10*self.carga_paga
        self.nota = res

def func_erro(valor, bot, top):
    weight = 4/((bot-top)**2)
    return -weight*(valor - bot)*(valor - top)

def tracao(v):
    return 46.439 - 0.935*v - 0.0144*v*v