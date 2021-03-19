from tools import avaliar_geometria, cla, a0l, constantes_perfil
import random
from avl import resultados_avl

n = 1
MTOW_projeto = 16
g = 9.81

nomes = ['arara', 'papagaio', 'pavao', 'pomba', 'avestruz', 'galinha', 'galo', 'aguia', 'gaviao', 'harpia', 'tucano', 'pinguim']
class Monoplano:
    geometria_asa = [] # Tuples de formato semelhante ao do XFLR5 (y, corda, offset, perfil)
    geometria_eh = []
    geometria_ev = []
    posicoes = {} # Referência: centro do bordo de ataque da asa
    
    def __init__(self, asa, perfil_asa, iw, eh, perfil_eh, ih, ev, perfil_ev, posicoes):
        self.geometria_asa = asa.copy()
        self.geometria_eh = eh.copy()
        self.geometria_ev = ev.copy()
        self.posicoes = posicoes.copy()
        self.atualizar_geometria()
        self.xcg, self.carga_paga, self.peso_vazio = self.estimar_cg()
        self.iw = iw
        self.ih = ih
        #self.atualizar_constantes()
        self.perfil_asa = perfil_asa
        self.perfil_eh = perfil_eh
        self.perfil_ev = perfil_ev
        self.nome = random.choice(nomes) + '-' + random.choice(nomes) + '-' + str(random.randint(1000, 9999))
        self.CM0, self.CL0, self.CD0, self.CLa, self.CMa, self.Xnp = resultados_avl(self)
        self.atrim = -self.CM0/self.CMa
    
    def atualizar_geometria(self):
        self.Sw, self.bw, self.cw, self.ARw, self.Xacw = avaliar_geometria(self.geometria_asa)
        self.Sh, self.bh, self.ch, self.ARh, self.Xach = avaliar_geometria(self.geometria_eh)
        self.Sv, self.bv, self.cv, self.ARv, self.Xacv = avaliar_geometria(self.geometria_ev)
        self.lh = self.posicoes["eh"][0] - 0.25*(self.cw - self.ch)
        self.lv = self.posicoes["ev"][0] - 0.25*(self.cw - self.cv)
        self.VH = (self.lh*self.Sh)/(self.cw*self.Sw)
        self.VV = (self.Sv*self.lv)/(self.Sw*self.bw)

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

        massaEV2021 = self.Sv * (massaEV2019 / areaEV2019)
        bracoEV2021 = 0.25 + self.Xacw + self.lv + 0.1 * self.cv
        momentoEV = g * massaEV2021 * bracoEV2021

        massaASA2019 = 0.73368
        areaASA2019 = 0.9

        massaASA2021 = self.Sw * (massaASA2019 / areaASA2019)
        bracoASA2021 = 0.25 + 0.4 * self.cw  # considerando que o berco do motor tera 0.25 e o CG da asa sera em 40 % da cma #
        momentoASA = g * massaASA2021 * bracoASA2021

        carga_paga = MTOW_projeto - (massaHELICE2021 + massaMOTOR2021 + massaTANQUEVAZIO2021 + massaCAIXAELETRICO2019 + massaFUSELAGEM2019 + massaASA2021 + massaEH2021 + massaEV2021)

        massaCARGAPAGA = carga_paga  # ajustar #
        bracoCARGAPAGA2019 = 0.35
        momentoCARGAPAGA = g * massaCARGAPAGA * bracoCARGAPAGA2019

        SomaMomentos = momentoHELICE + momentoMOTOR + momentoTANQUEVAZIO + momentoCAIXAELETRICO + momentoFUSELAGEM + \
                        momentoASA + momentoEH + momentoEV + momentoCARGAPAGA
        SomaPesos = g * MTOW_projeto

        XCG = SomaMomentos / SomaPesos

        PosXCG = XCG - 0.25
        peso_vazio = MTOW_projeto - carga_paga
        return PosXCG, carga_paga, peso_vazio
