from tools import avaliar_geometria

class Monoplano:
    geometria_asa = [] # Tuples de formato semelhante ao do XFLR5 (y, corda, offset, diedro, twist, perfil)
    geometria_eh = []
    geometria_ev = []
    posicoes = {} # Referência: centro do bordo de ataque da asa
    
    def __init__(self, asa, iw, eh, ih, ev, posicoes):
        self.geometria_asa = asa.copy()
        self.geometria_eh = eh.copy()
        self.geometria_ev = ev.copy()
        self.posicoes = posicoes.copy()
        self.Sw, self.bw, self.cw, self.ARw = avaliar_geometria(self.geometria_asa)
        self.Sh, self.bh, self.ch, self.ARh = avaliar_geometria(self.geometria_eh)
        self.Sv, self.bv, self.cv, self.ARv = avaliar_geometria(self.geometria_ev)
        self.iw = iw
        self.ih = ih
        self.lh = self.posicoes["eh"][0] - 0.25*(self.cw - self.ch)
        self.lv = self.posicoes["ev"][0] - 0.25*(self.cw - self.cv)
        self.VH = (self.lh*self.Sh)/(self.cw*self.Sw)
        self.VV = (self.Sv*self.lv)/(self.Sw*self.bw)
        self.nome = self.geometria_asa[0][5] + "-" + "%.3f" % self.Sw + "-" + "%.3f" % self.ARw