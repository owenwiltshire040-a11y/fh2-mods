"""A model's own rim into the donor wheel part, the way wheel/build_wheel.py did the 207's.

The game's wheel part is a normalised rim: x is depth (outward = -x, the face around x 0..0.05, the barrel back at
x = 1), y/z the wheel plane, face radius R = 0.1397; the game scales it to the car's rim diameter through per-vertex
size morphs (4 x half4: (width: -0.9 on barrel-back vertices else 0, 0, 0, 1), (0, 1.3247 y, 1.3247 z, 0),
(0, 0, 0, 1), one unknown row left at zero — copying the donor's displaced small details). Wheels draw without back-face culling, so the
new geometry is single-sided, wound by the model's own normals. AO/mask UV sets are borrowed from the nearest
front-facing donor rim vertex, as the 207 build did.
"""
import struct
import numpy as np
from geometry import Part
from body_swap import set_group, material_names
from gltf_bridge import decode_group

R = 0.1397
DIAM = 1.3247

def rim_soup(parts, materials, centre, zone=0.36):
    """triangles (FH2 space) of the given materials within `zone` of the wheel centre: (V, N) per corner"""
    Vs, Ns = [], []
    for m in materials:
        for p in parts.get(m, []):
            V = p['V'].reshape(-1, 3, 3); N = p['N'].reshape(-1, 3, 3); c = V.mean(1)
            keep = (np.abs(c[:, 1] - centre[1]) < zone) & (np.abs(c[:, 2] - centre[2]) < zone) & (np.abs(c[:, 0] - centre[0]) < 0.45)
            if keep.any(): Vs.append(V[keep].reshape(-1, 3)); Ns.append(N[keep].reshape(-1, 3))
    return np.concatenate(Vs), np.concatenate(Ns)

def build_rim(wheel_bytes, parts, materials, centre, keep_donor=('inner_rim',), black_materials=()):
    """wheel_bytes: the donor's wheelLF modelbin. parts/materials/centre: the model's rim geometry (FH2 space) and
    the wheel centre it sits on (the car's left wheel: outward = -x, as in the wheel part). Returns the new modelbin."""
    Vall, _ = rim_soup(parts, list(materials) + list(black_materials), centre)
    x_outer = Vall[:, 0].min(); rmax = np.hypot(Vall[:, 1] - centre[1], Vall[:, 2] - centre[2]).max(); scale = R / rmax
    def prep(mats):
        V, N = rim_soup(parts, mats, centre)
        return orient(np.stack([(V[:, 0] - x_outer) * scale, (V[:, 1] - centre[1]) * scale, (V[:, 2] - centre[2]) * scale], 1), N)
    sP, sN, sT = prep(materials)
    print(f'  rim: {len(sT)} silver tris, model rim radius {rmax:.3f} m -> R {R}')
    p = Part(wheel_bytes); names = material_names(p)
    out_bytes = _fill_group(p, names, 0, 'rim', keep_donor, sP, sN, sT, planar=True)
    if black_materials:
        bP, bN, bT = prep(black_materials); print(f'  rim: {len(bT)} black tris')
        _fill_group(p, names, 1, 'black', ('black',), bP, bN, bT, planar=True)
    out = p.build(); Part(out)
    return out, (np.concatenate([sP] + ([bP] if black_materials else [])), np.concatenate([sT] + ([bT + len(sP)] if black_materials else [])))

def orient(P, N):
    """single-sided triangles with smoothed normals; returns (per-corner P, N, T)"""
    T = np.arange(len(P)).reshape(-1, 3)
    T = np.arange(len(P)).reshape(-1, 3)
    g = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); nn = N.reshape(-1, 3, 3).mean(1); nn[:, 0] *= 1   # FH2 -> model: same axes
    flip = np.einsum('ij,ij->i', g, nn) < 0; T[flip] = T[flip][:, [0, 2, 1]]
    g = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); fn = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)
    # the model's normals are not to be trusted on the face planes (SketchUp back faces): anything facing +/-x near
    # the front of the wheel faces OUT (-x), anything facing +/-x deeper in faces the barrel (+x); walls keep theirs
    cx = P[T].mean(1)[:, 0]; facey = np.abs(fn[:, 0]) > 0.6
    want_out = facey & (cx < 0.03); want_in = facey & (cx >= 0.03)
    bad = (want_out & (fn[:, 0] > 0)) | (want_in & (fn[:, 0] < 0)); T[bad] = T[bad][:, [0, 2, 1]]
    g = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); fn = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)
    print(f'  rim: re-wound {bad.sum()} face triangles by position (model normals disagreed)')
    # weld + smooth normals within 50 degrees
    key = np.round(P, 5); _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.reshape(-1)
    Pw = P[first]; Tw = inv[T]
    acc = np.zeros((len(Pw), 3))
    for k in range(3): np.add.at(acc, Tw[:, k], g)
    Nw = np.zeros((len(Tw) * 3, 3)); Pv = Pw[Tw].reshape(-1, 3); cosc = np.cos(np.radians(50)); Tv = np.arange(len(Pv)).reshape(-1, 3)
    for k in range(3):
        sm = acc[Tw[:, k]]; sm /= np.maximum(np.linalg.norm(sm, axis=1, keepdims=True), 1e-12)
        use = np.einsum('ij,ij->i', sm, fn) > cosc; Nw[Tv[:, k]] = np.where(use[:, None], sm, fn)
    return Pv, Nw, Tv


def _fill_group(p, names, gid, mat, keep_donor, sP, sN, sT, planar=False):
    """replace material `mat` of group `gid` with the triangles sP/sN/sT, keeping the donor's `keep_donor` materials
    (LOD-0 triangles) with their own attributes and morphs; AO UVs for the new vertices from the nearest front-facing
    donor vertex of `mat`"""
    d, _ = decode_group(p, gid); morph = list(p.groups[gid]['morph'])
    keepP, keepN, keepUV, keepT, keepAO, keepM = [], [], [], {}, [], []; base = 0
    for rr in p.render:
        m_ = names[id(rr['blob'])]
        if rr['group'] != gid or m_ not in keep_donor or struct.unpack_from('<H', rr['blob']['data'], 4)[0] != 0b11: continue
        idx = np.array(rr['indices']); used = np.unique(idx); remap = {o: i + base for i, o in enumerate(used)}
        keepP.append(d['POSITION'][used][:, :3]); keepN.append(d['NORMAL0'][used][:, :3]); keepUV.append(d['TEXCOORD0'][used] if 'TEXCOORD0' in d else np.zeros((len(used), 2)))
        keepAO.append({j: d[f'TEXCOORD{j}'][used] for j in (1, 2, 3) if f'TEXCOORD{j}' in d}); keepM += [morph[i] for i in used]
        keepT[m_] = np.concatenate([keepT.get(m_, np.zeros(0, int)), np.array([remap[i] for i in idx])]); base += len(used)
    rim_ix = np.unique(np.concatenate([rr['indices'] for rr in p.render if rr['group'] == gid and names[id(rr['blob'])] == mat]))
    front = rim_ix[(d['NORMAL0'][rim_ix, 0] < -0.8) & (d['POSITION'][rim_ix, 0] < 0.03)]
    if len(front) < 8: front = rim_ix                       # (the black barrel ring has no front-facing vertices)
    from scipy.spatial import cKDTree
    _, nn_ = cKDTree(d['POSITION'][front][:, :3]).query(sP); src = front[nn_]
    have = [j for j in (1, 2, 3) if f'TEXCOORD{j}' in d]
    uvc = {j: np.concatenate([a[j] for a in keepAO] + [d[f'TEXCOORD{j}'][src]]) for j in have if j != 3}
    if 3 in have:
        allPos = d['POSITION'][:, :3]; A = np.c_[allPos[:, 1], allPos[:, 2], np.ones(len(allPos))]
        co = [np.linalg.lstsq(A, d['TEXCOORD3'][:, c], rcond=None)[0] for c in (0, 1)]
        uvc[3] = np.concatenate([a[3] for a in keepAO] + [np.stack([np.c_[sP[:, 1], sP[:, 2], np.ones(len(sP))] @ co[c] for c in (0, 1)], 1)])
    allP = np.concatenate(keepP + [sP]); allN = np.concatenate(keepN + [sN]); allUV = np.concatenate(keepUV + [d['TEXCOORD0'][src] if 'TEXCOORD0' in d else np.zeros((len(sP), 2))])
    by_mat = dict(keepT); by_mat[mat] = (sT + base).reshape(-1)
    planar = np.stack([allP[:, 2] / (2 * R) + 0.5, allP[:, 1] / (2 * R) + 0.5], 1)
    set_group(p, gid, {'P': allP, 'N': allN, 'UV': allUV, 'UVconst': uvc, 'UVtan': planar}, by_mat)
    M0 = np.frombuffer(b''.join(morph), '<f2').reshape(len(morph), 4, 4)
    nm = np.zeros((len(sP), 4, 4), np.float16)
    nm[:, 0, 0] = np.where(sP[:, 0] > 0.5, -0.9, 0.0); nm[:, 0, 3] = 1
    nm[:, 1, 1] = DIAM * sP[:, 1]; nm[:, 1, 2] = DIAM * sP[:, 2]; nm[:, 2, 3] = 1
    nm[:, 3] = 0            # the unknown row: the donor's values (up to +/-0.037) shoved the 208's nut bosses off the face (v0.1.2)
    rows = keepM + [nm[i].tobytes() for i in range(len(nm))]
    p.groups[gid]['morph'] = rows + rows[:1]
