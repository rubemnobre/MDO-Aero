from models import Monoplano
from matplotlib import pyplot as plt


gw = [(0, 0.4, 0), (0.96, 0.4, 0), (1.2, 0.3, 0)]
#gw = [(0, 0.4, 0), (1.2, 0.3, 0.1)]
iw = 5.0
gh = [(0, 0.25, 0), (0.4, 0.25, 0)]
ih = -5.0
gv = [(0, 0.3, 0), (0.4, 0.15, 0)]
pos = { "asa" : (0, 0), "eh" : (0.95, 0), "ev" : (0.95, 0), "cg" : (0.12, 0) }

a = Monoplano(gw, 's1223', iw, gh, 'e168', ih, gv, 'naca0009', pos)

print(a.CM0, a.CMa, -a.CM0/a.CMa)