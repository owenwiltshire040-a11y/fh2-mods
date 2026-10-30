"""Wavefront OBJ (right-handed, Y up, +Z = car front, metres) -> per-material triangle soups in FH2 car space.

FH2 car space: X across (car's left = -X), Y up, Z forward. The body is placed so the axle midpoint sits at
`axle_mid_z` (= -BottomCenterWheelbasePosZ of the donor's Data_CarBody row, +0.087 for the Charger) and the tyre
contact patch at `ground_y` (the donor's wheel-centre height less the car's tyre radius). Wheel centres come from
the tyre material's vertices, clustered by the sign of x and z.

usage: objgeo.py model.obj out.pkl TYRE_MATERIAL [--ground G] [--axle-mid Z] [--scale S]
"""
import sys, collections, pickle, argparse
import numpy as np

def load_obj(fn, scale=1.0):
    """{material: [(V (n,3), N (n,3), UV (n,2))...]} with one entry per OBJ group, in the file's own space"""
    V, VN, VT = [], [], []; mat = None; grp = None
    prims = collections.defaultdict(lambda: collections.defaultdict(list))      # mat -> group -> [face corner triples]
    with open(fn, 'r', errors='replace') as f:
        for line in f:
            if line.startswith('v '): V.append(line.split()[1:4])
            elif line.startswith('vn '): VN.append(line.split()[1:4])
            elif line.startswith('vt '): VT.append(line.split()[1:3])
            elif line.startswith('usemtl'): mat = line.split(None, 1)[1].strip()
            elif line.startswith('g '): grp = line.split(None, 1)[1].strip()
            elif line.startswith('f '):
                corners = [tuple(int(x) if x else 0 for x in (p.split('/') + ['', ''])[:3]) for p in line.split()[1:]]
                for i in range(1, len(corners) - 1):                            # fan-triangulate polygons
                    prims[mat][grp].append((corners[0], corners[i], corners[i + 1]))
    V = np.array(V, float) * scale; VN = np.array(VN, float) if VN else np.zeros((0, 3)); VT = np.array(VT, float) if VT else np.zeros((0, 2))
    def idx(i, n): return i - 1 if i > 0 else n + i
    out = {}
    for m, groups in prims.items():
        lst = []
        for g, tris in groups.items():
            vi = np.array([[idx(c[0], len(V)) for c in t] for t in tris]); P = V[vi]                     # (t,3,3)
            if len(VN) and all(c[2] for t in tris for c in t):
                N = VN[np.array([[idx(c[2], len(VN)) for c in t] for t in tris])]
            else:
                fn_ = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); fn_ /= np.maximum(np.linalg.norm(fn_, axis=1, keepdims=True), 1e-12)
                N = np.repeat(fn_[:, None, :], 3, axis=1)
            if len(VT) and all(c[1] for t in tris for c in t):
                UV = VT[np.array([[idx(c[1], len(VT)) for c in t] for t in tris])]
            else: UV = np.zeros((len(tris), 3, 2))
            lst.append(dict(node=g, mat=m, V=P.reshape(-1, 3), N=N.reshape(-1, 3), UV=UV.reshape(-1, 2)))
        out[m] = lst
    return out

def wheel_centres(prims, tyre_mat):
    """{HUB_LF, HUB_RF, HUB_LR, HUB_RR: (centre, radius)} in the file's space from the tyre material's vertices"""
    P = np.concatenate([p['V'] for p in prims[tyre_mat]]); cx, cz = np.median(P[:, 0]), np.median(P[:, 2])
    out = {}
    for name, sx, sz in (('L', 1, 1), ('R', -1, 1), ('L', 1, -1), ('R', -1, -1)):      # file space: +x = car's left
        q = P[(np.sign(P[:, 0] - cx) == sx) & (np.sign(P[:, 2] - cz) == sz)]
        c = (q.min(0) + q.max(0)) / 2; r = (q[:, 1].max() - q[:, 1].min()) / 2
        out[f'HUB_{name}{"F" if sz > 0 else "R"}'] = (c, r)
    return out

def to_fh2_space(prims, wheels, ground_y, axle_mid_z):
    """mirror x (right-handed file -> FH2), reverse winding, shift so the axle midpoint is at axle_mid_z and the tyre
    bottoms at ground_y. Returns (parts, wheels_fh2, ground_model)"""
    zf = (wheels['HUB_LF'][0][2] + wheels['HUB_RF'][0][2]) / 2; zr = (wheels['HUB_LR'][0][2] + wheels['HUB_RR'][0][2]) / 2
    gm = np.mean([c[1] - r for c, r in wheels.values()])
    off = np.array([0.0, ground_y - gm, axle_mid_z - (zf + zr) / 2])
    def xf(P): return np.stack([-P[:, 0], P[:, 1], P[:, 2]], 1) + off
    def xn(N): return np.stack([-N[:, 0], N[:, 1], N[:, 2]], 1)
    parts = {}
    for m, lst in prims.items():
        parts[m] = [dict(node=p['node'], mat=m, V=xf(p['V']).reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3),
                         N=xn(p['N']).reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3), UV=p['UV'].reshape(-1, 3, 2)[:, ::-1].reshape(-1, 2)) for p in lst]
    wf = {k: dict(centre=xf(c[None])[0], radius=float(r)) for k, (c, r) in wheels.items()}
    return parts, wf, float(gm)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('obj'); ap.add_argument('out'); ap.add_argument('tyre_mat')
    ap.add_argument('--ground', type=float, required=True, help='FH2 y of the tyre contact patch (donor wheel y - tyre radius)')
    ap.add_argument('--axle-mid', type=float, default=0.0, help='FH2 z of the axle midpoint (-BottomCenterWheelbasePosZ)')
    ap.add_argument('--scale', type=float, default=1.0); A = ap.parse_args()
    prims = load_obj(A.obj, A.scale); W = wheel_centres(prims, A.tyre_mat)
    for k, (c, r) in W.items(): print(f'{k} file-space centre {c.round(3)} radius {r:.3f}')
    parts, wheels, gm = to_fh2_space(prims, W, A.ground, A.axle_mid)
    V = np.concatenate([p['V'] for l in parts.values() for p in l])
    wb = (wheels['HUB_LF']['centre'][2] + wheels['HUB_RF']['centre'][2]) / 2 - (wheels['HUB_LR']['centre'][2] + wheels['HUB_RR']['centre'][2]) / 2
    tr = abs(wheels['HUB_LF']['centre'][0] - wheels['HUB_RF']['centre'][0])
    print(f'wheelbase {wb:.3f} track F {tr:.3f} R {abs(wheels["HUB_LR"]["centre"][0] - wheels["HUB_RR"]["centre"][0]):.3f}; model ground {gm:.3f} -> FH2 {A.ground:.3f}; '
          f'body x {V[:,0].min():.2f}..{V[:,0].max():.2f} y {V[:,1].min():.2f}..{V[:,1].max():.2f} z {V[:,2].min():.2f}..{V[:,2].max():.2f}')
    for k, w in wheels.items(): print(k, 'FH2 centre', w['centre'].round(3))
    pickle.dump(dict(parts=parts, wheels=wheels, ground=A.ground, wheelbase=float(wb), materials=sorted(parts)), open(A.out, 'wb'))
    print('wrote', A.out)
