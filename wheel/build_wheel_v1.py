"""Owen's 207 rim: 16" seven-spoke alloy (photos 29 Oct), built in code into the donor wheel's 'rim' material.

Wheel model space (donor Fiesta rim): x is depth (outward = -x, face around x 0..0.045, barrel back at x=1),
y/z the wheel plane, rim face radius R = 0.1397 (the game scales the model to the car's wheel size).
The donor's lip, barrel, wheel nuts (also 4 x 108 mm), valve, centre badge and motion-blur discs are kept.
"""
import sys, struct, numpy as np
sys.path.insert(0, '../fh2re')
from geometry import Part
from body_swap import set_group, group_materials, material_names
from gltf_bridge import decode_group

R = 0.1397
NSPOKE = 7
SRC = 'wheel_orig.modelbin'

# ---- proportions measured from the straight-on photo (fractions of R)
HUB_IN, HUB_OUT = 0.125, 0.34        # centre face: from the badge out to the spoke roots / window inner edge
SP_R0, SP_R1 = 0.30, 0.90            # spokes
W0, W1 = 0.17, 0.30                  # spoke width at root and tip (chord, fractions of R)
RING_IN, RING_OUT = 0.86, 0.925      # flat ring between window outer edge and the donor lip
X_HUB = 0.016                        # hub face depth (wheel nuts' tops are at 0.010, so they stand proud)
X_SP0, X_SP1 = 0.000, 0.006          # spoke face depth at root and tip (slightly dished)
RIDGE = -0.005                       # each spoke has a groove down its centre (Owen: recessed, not raised)
X_RING = 0.006
X_BACK = 0.045                       # walls run back to here


class Mesh:
    def __init__(self): self.P, self.T = [], []
    def quad(self, a, b, c, d):      # a-b-c-d around; winding fixed later
        i = len(self.P); self.P += [a, b, c, d]; self.T += [[i, i + 1, i + 2], [i, i + 2, i + 3]]
    def tri(self, a, b, c):
        i = len(self.P); self.P += [a, b, c]; self.T += [[i, i + 1, i + 2]]


def pt(r, ang, x):   # polar (fractions of R) -> model space
    return [x, r * R * np.sin(ang), r * R * np.cos(ang)]


def build():
    m = Mesh()
    # hub face: annulus, with its outer wall between spokes
    n = NSPOKE * 12
    for k in range(n):
        a0, a1 = 2 * np.pi * k / n, 2 * np.pi * (k + 1) / n
        m.quad(pt(HUB_IN, a0, X_HUB), pt(HUB_OUT, a0, X_HUB), pt(HUB_OUT, a1, X_HUB), pt(HUB_IN, a1, X_HUB))
        m.quad(pt(HUB_OUT, a0, X_HUB), pt(HUB_OUT, a0, X_BACK), pt(HUB_OUT, a1, X_BACK), pt(HUB_OUT, a1, X_HUB))
        m.quad(pt(HUB_IN, a0, X_HUB - 0.006), pt(HUB_IN, a0, X_HUB), pt(HUB_IN, a1, X_HUB), pt(HUB_IN, a1, X_HUB - 0.006))  # lip round the badge
        # outer ring and its inner wall (the windows' outer edge)
        m.quad(pt(RING_IN, a0, X_RING), pt(RING_OUT, a0, X_RING), pt(RING_OUT, a1, X_RING), pt(RING_IN, a1, X_RING))
        m.quad(pt(RING_IN, a0, X_RING), pt(RING_IN, a0, X_BACK), pt(RING_IN, a1, X_BACK), pt(RING_IN, a1, X_RING))
    # spokes: tapered, faceted (raised centre crease), with side walls
    seg = 14
    for s in range(NSPOKE):
        th = 2 * np.pi * s / NSPOKE
        rows = []
        for j in range(seg + 1):
            t = j / seg
            r = SP_R0 + (SP_R1 - SP_R0) * t
            w = W0 + (W1 - W0) * t
            half = (w / 2) / r                        # half-angle of the chord
            x = X_SP0 + (X_SP1 - X_SP0) * t
            rows.append((pt(r, th - half, x), pt(r, th, x - RIDGE), pt(r, th + half, x),
                         pt(r, th - half, X_BACK), pt(r, th + half, X_BACK)))
        for j in range(seg):
            a, b = rows[j], rows[j + 1]
            m.quad(a[0], a[1], b[1], b[0]); m.quad(a[1], a[2], b[2], b[1])          # two facets
            m.quad(a[0], b[0], b[3], a[3]); m.quad(a[2], a[4], b[4], b[2])          # side walls
        a = rows[0]   # root end: face down to the hub
        m.quad(a[0], a[1], pt(SP_R0, th, X_HUB), pt(SP_R0, th - (W0 / 2) / SP_R0, X_HUB))
        m.quad(a[1], a[2], pt(SP_R0, th + (W0 / 2) / SP_R0, X_HUB), pt(SP_R0, th, X_HUB))
    P = np.array(m.P, float); T = np.array(m.T)
    # wind every face outward (towards -x for faces, and away from the wheel axis / spoke centre for walls):
    # use the direction from a point slightly inside the metal; simplest robust choice for an open shell:
    g = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    c = P[T].mean(1)
    face = np.abs(g[:, 0]) >= np.linalg.norm(g[:, 1:], axis=1)
    want = np.where(face, -1.0, 0.0)[:, None] * np.array([1, 0, 0])
    radial = np.c_[np.zeros(len(c)), c[:, 1:]]
    want[~face] = radial[~face]
    flip = np.sum(g * want, 1) < 0
    T[flip] = T[flip][:, [0, 2, 1]]
    return P, T


def double_sided(P, T):
    g = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    N = np.zeros_like(P)
    for k in range(3): np.add.at(N, T[:, k], g)
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    n = len(P)
    UV = np.stack([P[:, 2] / (2 * R) + 0.5, P[:, 1] / (2 * R) + 0.5], 1)
    return np.r_[P, P], np.r_[N, -N], np.r_[UV, UV], np.r_[T, T[:, [0, 2, 1]] + n]


if __name__ == '__main__':
    raw = open(SRC, 'rb').read()
    p = Part(raw)
    names = material_names(p)
    gm = group_materials(p)
    gid = next(g for g, ms in gm.items() if 'rim' in ms)
    print('rim group', gid, sorted(gm[gid]))
    d, _ = decode_group(p, gid)
    d_morph = list(p.groups[gid]['morph'])
    # keep the donor's other materials in this group (LOD0 triangles), with their own normals and UVs
    keepP, keepN, keepUV, keepT, keepAO, keepM = [], [], [], {}, [], []
    base = 0
    for r in p.render:
        m_ = names[id(r['blob'])]
        if r['group'] != gid or m_ == 'rim' or struct.unpack_from('<H', r['blob']['data'], 4)[0] != 0b11: continue
        idx = np.array(r['indices']); used = np.unique(idx)
        remap = {o: i + base for i, o in enumerate(used)}
        keepP.append(d['POSITION'][used]); keepN.append(d['NORMAL0'][used][:, :3]); keepUV.append(d['TEXCOORD0'][used])
        keepAO.append({j: d[f'TEXCOORD{j}'][used] for j in (1, 2, 3)})
        keepM += [p.groups[gid]['morph'][i] for i in used]
        keepT[m_] = np.array([remap[i] for i in idx]); base += len(used)
    P, T = build()
    sP, sN, sUV, sT = double_sided(P, T)
    allP = np.concatenate(keepP + [sP]); allN = np.concatenate(keepN + [sN])
    by_mat = {k: v for k, v in keepT.items()}
    by_mat['rim'] = (sT + base).reshape(-1)
    # AO/mask lookups: one bright donor texel (front-facing rim vertex)
    # AO/mask lookups for the new rim: copied from the nearest front-facing face vertex of the donor's own rim
    # (front faces of its spokes and centre are lit; the donor's recesses and windows are what came out black)
    rim_ix = np.unique(np.concatenate([r['indices'] for r in p.render if r['group'] == gid and names[id(r['blob'])] == 'rim']))
    front = rim_ix[(d['NORMAL0'][rim_ix, 0] < -0.8) & (d['POSITION'][rim_ix, 0] < 0.03)]
    from scipy.spatial import cKDTree
    _, nn = cKDTree(d['POSITION'][front]).query(sP)
    src = front[nn]
    uvc = {j: np.concatenate([a[j] for a in keepAO] + [d[f'TEXCOORD{j}'][src]]) for j in (1, 2)}
    # TEXCOORD3 is a flat projection of the face (the AO map): use the donor's exact projection
    allPos = d['POSITION']; A = np.c_[allPos[:, 1], allPos[:, 2], np.ones(len(allPos))]
    co = [np.linalg.lstsq(A, d['TEXCOORD3'][:, c], rcond=None)[0] for c in (0, 1)]
    t3 = np.stack([np.c_[sP[:, 1], sP[:, 2], np.ones(len(sP))] @ co[c] for c in (0, 1)], 1)
    uvc[3] = np.concatenate([a[3] for a in keepAO] + [t3])
    # TEXCOORD0 points into the rim's unwrapped texture sheet: borrow it from the nearest donor spoke face too
    sUV = d['TEXCOORD0'][src]
    allUV = np.concatenate(keepUV + [sUV])
    print('AO source vertices:', len(front), 'front-facing donor rim vertices')
    print('rim triangles', len(T), '(x2 sides); kept', {k: len(v) // 3 for k, v in keepT.items()})
    planar = np.stack([allP[:, 2] / (2 * R) + 0.5, allP[:, 1] / (2 * R) + 0.5], 1)   # smooth frame for tangents
    set_group(p, gid, {'P': allP, 'N': allN, 'UV': allUV, 'UVconst': uvc, 'UVtan': planar}, by_mat)
    # size morphs: the game grows the rim to the car's wheel size by blending these per-vertex offsets in.
    # Per vertex, four half4s: (width: -0.9 on barrel-back verts, else 0; 0; 0; 1), (0, 1.3175*y, 1.3175*z, 0)
    # (diameter), (0, 0, 0, 1), and a fourth whose meaning is unknown (copied from the nearest donor vertex).
    M0 = np.frombuffer(b''.join(d_morph), '<f2').reshape(len(d_morph), 4, 4)
    nm = np.zeros((len(sP), 4, 4), np.float16)
    nm[:, 0, 0] = np.where(sP[:, 0] > 0.5, -0.9, 0.0); nm[:, 0, 3] = 1
    nm[:, 1, 1] = 1.3175 * sP[:, 1]; nm[:, 1, 2] = 1.3175 * sP[:, 2]
    nm[:, 2, 3] = 1
    nm[:, 3] = M0[src, 3]
    rows = keepM + [nm[i].tobytes() for i in range(len(nm))]
    p.groups[gid]['morph'] = rows + rows[:1]          # set_group appended one spare (degenerate) vertex
    out = p.build(); Part(out)
    open('wheel_207.modelbin', 'wb').write(out)
    np.savez('wheel_preview.npz', P=P, T=T)
    print('wrote wheel_207.modelbin', len(out))
