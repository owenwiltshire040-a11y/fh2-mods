"""Put the STR1 model's own rims into an already built STR1 car zip (the 208's rimbuild route).

python3 f1/str1_rims.py str1_geo.pkl in_car.zip out_car.zip
The model's rims are anthracite (MCLRIM lip, MCLSPOKES_OP spokes) with an MCLHUB centre: spokes + lip go to the
wheel part's 'black' material, the hub to 'rim'. Motion-blur copies (*_BLUR) and the see-through MCLSPOKES duplicate
are left out. The game sizes the rim to the DB's 13" and draws the tyre itself.
"""
import sys, os, pickle, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'fh2re'))
import rimbuild

SILVER = ['MCLHUB']
BLACK = ['MCLRIM', 'MCLSPOKES_OP']

geo = pickle.load(open(sys.argv[1], 'rb'))
hub = geo['parts']['HUB_LF']; centre = geo['wheels']['HUB_LF']['centre']
import numpy as np
parts = {}
for p in hub: parts.setdefault(p['mat'], []).append(dict(p))
# the model's spokes and hub nut are separate meshes ~8 mm off the barrel's axis: centre them on the rim barrel
# (the game spins the wheel part about the barrel centre, so any offset wobbles)
for m in SILVER + ['MCLSPOKES_OP']:
    V = np.concatenate([p['V'] for p in parts[m]]); off = centre - (V.min(0) + V.max(0)) / 2; off[0] = 0
    for p in parts[m]: p['V'] = p['V'] + off
    print(f'  {m}: recentred by {np.round(off * 1000, 1)} mm')
# the rim lip runs ~3 cm under the tyre (to r 0.195); the tyre's inner edge (MICH06 sidewall, r ~0.167) is the
# radius the game's 13" rim size should land on
T = np.concatenate([p['V'] for p in hub if p['mat'] == 'MICH06'])
R_REF = np.hypot(T[:, 1] - centre[1], T[:, 2] - centre[2]).min()
print(f'  scale reference: tyre inner radius {R_REF:.3f} m')
# trim the part of the lip that runs under the tyre, or it pokes through the game's tyre sidewall
for p in parts['MCLRIM']:
    V = p['V'].reshape(-1, 3, 3); r = np.hypot(V[..., 1] - centre[1], V[..., 2] - centre[2]).max(1); k = r <= R_REF * 1.01
    p['V'] = V[k].reshape(-1, 3); p['N'] = p['N'].reshape(-1, 3, 3)[k].reshape(-1, 3)
print(f'  MCLRIM: kept {sum(len(p["V"]) for p in parts["MCLRIM"]) // 3} tris inside the tyre edge')
src = zipfile.ZipFile(sys.argv[2])
wheel = [n for n in src.namelist() if n.lower().endswith('wheellf.modelbin')]
assert len(wheel) == 1, wheel
new, _ = rimbuild.build_rim(src.read(wheel[0]), parts, SILVER, centre, black_materials=BLACK, r_ref=R_REF)
with zipfile.ZipFile(sys.argv[3], 'w', zipfile.ZIP_DEFLATED) as out:
    for i in src.infolist():
        out.writestr(i, new if i.filename == wheel[0] else src.read(i.filename))
print('replaced', wheel[0])
