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

# The spoke FACES: in the source the spokes are only side walls (MCLSPOKES_OP, every triangle edge-on to the
# wheel) plus a textured face disc (MCLSPOKES) whose cut-outs were lost in conversion. The walls outline the 10
# windows between the spokes, so the spoke face = the disc minus those windows, laid on the disc's dish x(r).
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, unary_union
import trimesh
W = np.concatenate([p['V'] for p in parts['MCLSPOKES_OP']]).reshape(-1, 3, 3)
edges = [LineString([tuple(t[a][1:] - centre[1:]), tuple(t[b][1:] - centre[1:])]) for t in W
         for a, b in ((0, 1), (1, 2), (2, 0)) if np.hypot(*(t[a][1:] - t[b][1:])) > 1e-4]
windows = unary_union([q for q in polygonize(unary_union(edges)) if q.area > 1e-3])
D = np.concatenate([p['V'] for p in hub if p['mat'] == 'MCLSPOKES']); Dr = np.hypot(D[:, 1] - centre[1], D[:, 2] - centre[2])
r_out = Dr.max(); r_in = 0.045
Wv = W.reshape(-1, 3); Wr = np.hypot(Wv[:, 1] - centre[1], Wv[:, 2] - centre[2])   # face depth = the walls' FRONT edge (the disc sits 1-2 cm inside)
bins = np.linspace(0, r_out, 30); xr = np.array([Wv[(Wr >= a) & (Wr < b), 0].min() if ((Wr >= a) & (Wr < b)).any() else np.nan for a, b in zip(bins[:-1], bins[1:])])
ok = ~np.isnan(xr); rc = ((bins[:-1] + bins[1:]) / 2)[ok]; xr = xr[ok]
face = Point(0, 0).buffer(r_out, 128).difference(Point(0, 0).buffer(r_in, 64)).difference(windows).segmentize(0.004)
fv, ff = [], []
for poly in getattr(face, 'geoms', [face]):
    v2, f2 = trimesh.creation.triangulate_polygon(poly, engine='earcut')
    ff.append(f2 + sum(len(a) for a in fv)); fv.append(v2)
v2 = np.concatenate(fv); f2 = np.concatenate(ff)
x = np.interp(np.hypot(v2[:, 0], v2[:, 1]), rc, xr) - 0.001        # 1 mm proud of the walls' front edge
v3 = np.stack([x, v2[:, 0] + centre[1], v2[:, 1] + centre[2]], 1)
Vf = v3[f2].reshape(-1, 3); Nf = np.tile([-1.0, 0, 0], (len(Vf), 1))   # faces out (-x on the left wheel)
parts['SPOKE_FACE'] = [dict(V=Vf, N=Nf)]
BLACK = BLACK + ['SPOKE_FACE']
print(f'  spoke faces: {len(f2)} tris, {face.area * 1e4:.0f} cm2 (disc r {r_in}-{r_out:.3f} minus {len(getattr(windows, "geoms", [windows]))} windows)')
src = zipfile.ZipFile(sys.argv[2])
wheel = [n for n in src.namelist() if n.lower().endswith('wheellf.modelbin')]
assert len(wheel) == 1, wheel
new, _ = rimbuild.build_rim(src.read(wheel[0]), parts, SILVER, centre, black_materials=BLACK, r_ref=R_REF, trust_normals=True)
with zipfile.ZipFile(sys.argv[3], 'w', zipfile.ZIP_DEFLATED) as out:
    for i in src.infolist():
        out.writestr(i, new if i.filename == wheel[0] else src.read(i.filename))
print('replaced', wheel[0])
