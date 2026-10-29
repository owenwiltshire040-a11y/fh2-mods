"""STR1 model (glb) -> per-part, per-material triangle soups in FH2 car space.

Model: 'acfl_2006_str' (CTDP's STR1 via an Assetto Corsa conversion, Sketchfab upload by Dave Love; used for
Owen's personal mod with CTDP's permission). Scene units are 1/100 m after Sketchfab's root transforms.
FH2 space: X across (car's left = -X), Y up, Z forward; wheel axle midpoint at Z = 0.
"""
import numpy as np, trimesh, pickle
SC = 100.0
sc = trimesh.load('src/nefolder.glb', force='scene'); g = sc.graph

def top_of(node):
    p = node
    while True:
        par = g.transforms.parents.get(p)
        if par is None or par == 'RootNode': return p
        p = par

raw = {}
for node in g.nodes_geometry:
    T, geom = g[node]; m = sc.geometry[geom]
    V = trimesh.transform_points(m.vertices, T) * SC
    R = T[:3, :3]; N = m.vertex_normals @ R.T; N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
    uv = getattr(m.visual, 'uv', None)
    mat = getattr(getattr(m.visual, 'material', None), 'name', None)
    F = m.faces
    raw.setdefault(top_of(node), []).append(dict(node=node, mat=mat, V=V[F].reshape(-1, 3), N=N[F].reshape(-1, 3),
        UV=(uv[F].reshape(-1, 2) if uv is not None else np.zeros((len(F) * 3, 2)))))

# wheel centres from the tyres (tread + sidewall meshes) of each hub
def tyre_centre(hub):
    P = np.concatenate([p['V'] for p in raw[hub] if p['mat'] in ('TREAD06', 'MICH06')])
    return (P.min(0) + P.max(0)) / 2, (P[:, 1].max() - P[:, 1].min()) / 2
C = {h: tyre_centre(h) for h in ('HUB_LF', 'HUB_RF', 'HUB_LR', 'HUB_RR')}
for h, (c, r) in C.items(): print(f'{h} tyre centre {c.round(3)} radius {r:.3f}')
ZF = (C['HUB_LF'][0][2] + C['HUB_RF'][0][2]) / 2; ZR = (C['HUB_LR'][0][2] + C['HUB_RR'][0][2]) / 2
RF = (C['HUB_LF'][1] + C['HUB_RF'][1]) / 2; RR = (C['HUB_LR'][1] + C['HUB_RR'][1]) / 2
YF = (C['HUB_LF'][0][1] + C['HUB_RF'][0][1]) / 2; YR = (C['HUB_LR'][0][1] + C['HUB_RR'][0][1]) / 2
GROUND_MODEL = ((YF - RF) + (YR - RR)) / 2
print(f'wheelbase {ZF - ZR:.3f}  tyre radius F {RF:.3f} R {RR:.3f}  model ground {GROUND_MODEL:.3f}')

GROUND_FH2 = 0.182 - 0.330           # the game's wheel centres (0.182) less the STR1's tyre radius
# the model sits pitched (front tyre bottoms 4 cm above the rears'): level it about the axle midpoint
TH = -np.arctan2((YF - RF) - (YR - RR), ZF - ZR); print(f'levelling pitch {np.degrees(TH):.2f} deg')
ROT = np.array([[1, 0, 0], [0, np.cos(TH), np.sin(TH)], [0, -np.sin(TH), np.cos(TH)]])
PIV = np.array([0.0, GROUND_MODEL, (ZF + ZR) / 2])
OFF = np.array([0.0, GROUND_FH2 - GROUND_MODEL, -(ZF + ZR) / 2])
def to_fh2(V): V = (V - PIV) @ ROT.T + PIV; return np.stack([-V[:, 0], V[:, 1], V[:, 2]], 1) + OFF
def nrm(N): N = N @ ROT.T; return np.stack([-N[:, 0], N[:, 1], N[:, 2]], 1)
out = {}
for top, prims in raw.items():
    lst = []
    for p in prims:
        V = to_fh2(p['V']).reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3)       # mirror -> reverse winding
        N = nrm(p['N']).reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3)
        UV = p['UV'].reshape(-1, 3, 2)[:, ::-1].reshape(-1, 2)
        lst.append(dict(node=p['node'], mat=p['mat'], V=V, N=N, UV=UV))
    out[top] = lst
wheels = {h: dict(centre=to_fh2(c[None])[0], radius=r) for h, (c, r) in C.items()}
pickle.dump(dict(parts=out, wheels=wheels, ground=GROUND_FH2, wheelbase=ZF - ZR), open('str1_geo.pkl', 'wb'))
for h, w in wheels.items(): print(h, 'FH2 wheel centre', w['centre'].round(3))
