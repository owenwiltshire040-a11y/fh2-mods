"""Put new geometry into an existing FH2 part, material by material.

A vertex group can serve several materials (e.g. the body's paint and its 'frame' parts share one buffer), so
geometry is assigned per material: give each material name the triangles it should draw; every other
material in that group draws one zero-area triangle (invisible) so no mesh is left empty.
"""
import struct
import numpy as np
from gltf_bridge import encode_group, tangents, O_UVT


def material_names(part):
    mats = {}
    for bl in part.b.blobs:
        if bl['tag'] == 'MatI':
            mats[struct.unpack('<i', part.b.meta(bl, 'Id  '))[0]] = part.b.meta(bl, 'Name').decode()
    return {id(r['blob']): mats.get(struct.unpack_from('<h', r['blob']['data'], 0)[0]) for r in part.render}


def set_group(part, gid, geo, by_material):
    """geo: dict P (n,3), N (n,3), UV (n,2) in FH2 space. by_material: {material name: triangle index array}.
    Materials of the group not named get a degenerate triangle."""
    P = np.asarray(geo['P'], np.float32); N = np.asarray(geo['N'], np.float32); UV = np.asarray(geo['UV'], np.float32)
    if len(P) == 0:   # nothing for this group: one invisible point
        P = np.zeros((1, 3), np.float32); N = np.array([[0, 1, 0]], np.float32); UV = np.zeros((1, 2), np.float32)
    deg = len(P)
    P = np.vstack([P, P[:1]]); N = np.vstack([N, N[:1]]); UV = np.vstack([UV, UV[:1]])
    every = np.concatenate([np.asarray(v, np.int64) for v in by_material.values()]) if by_material else np.zeros(0, np.int64)
    attrs = {'POSITION': P, 'NORMAL0': N}
    for k in range(5):
        attrs[f'TEXCOORD{k}'] = UV
    for k, v in (geo.get('UVconst') or {}).items():   # e.g. AO lookups: one fixed, unshadowed texel, or per-vertex values
        v = np.asarray(v, np.float32)
        attrs[f'TEXCOORD{k}'] = np.vstack([v, v[:1]]) if v.ndim == 2 else np.tile(v, (len(P), 1))
    attrs['COLOR0'] = np.ones((len(P), 4), np.float32)
    tidx = every if len(every) else np.array([deg, deg, deg])
    UVt = np.vstack([np.asarray(geo['UVtan'], np.float32), np.asarray(geo['UVtan'], np.float32)[:1]]) if geo.get('UVtan') is not None else UV
    attrs['TANGENT0'] = tangents(P.astype(np.float64), N.astype(np.float64), UVt.astype(np.float64), tidx).astype(np.float32)
    for k in range(1, 8):
        attrs[f'TANGENT{k}'] = attrs['TANGENT0']
    for k in range(5, 8):
        attrs[f'TEXCOORD{k}'] = UV
    rows, uvt = encode_group(part, gid, attrs)
    g = part.groups[gid]
    g['positions'] = [tuple(map(float, p)) for p in P]
    g['attrs'] = rows
    if g['morph'] is not None:
        stride = len(g['morph'][0]) if g['morph'] else 16
        g['morph'] = [bytes(stride)] * len(P)
    names = material_names(part)
    used = set()
    for r in part.render:
        if r['group'] != gid:
            continue
        m = names[id(r['blob'])]
        tri = by_material.get(m)
        if tri is not None and len(tri):
            r['indices'] = [int(i) for i in tri]; used.add(m)
        else:
            r['indices'] = [deg, deg, deg]
        struct.pack_into('<20f', r['blob']['data'], O_UVT, *uvt)
    missing = set(by_material) - used
    if missing:
        raise ValueError(f'group {gid}: no mesh uses material(s) {missing}')


def blank_group(part, gid):
    set_group(part, gid, {'P': [], 'N': [], 'UV': []}, {})


def group_materials(part):
    names = material_names(part)
    out = {}
    for r in part.render:
        out.setdefault(r['group'], set()).add(names[id(r['blob'])])
    return out
