"""Fit PazMedia's Peugeot 207 (Sketchfab, CC-BY 4.0) onto the 207 mod's donor parts.

Model space: X along the car (front is -X), Y up, Z across; ground at Y=0. FH2 space: X across, Y up,
Z forward, left-handed. Scale and offset come from matching the model's wheel centres to the donor's.
"""
import json, struct, sys, zipfile
import numpy as np
sys.path.insert(0, '../fh2re')
from geometry import Part
from carbin import read_carbin, write_carbin
from body_swap import set_group, blank_group, group_materials

GLB = '/mnt/user-data/attachments/5255ebaf-8dd4-5d3c-a76b-73339c095745/5440d4e8-peugeot_207.glb'
SRC_ZIP = 'mod/media/cars/PEU_207SEHDi_08.zip'
OUT_ZIP = 'out_sheik/PEU_207SEHDi_08.zip'

# ---- part classification (indices into the model's primitive list, see parts_views.png)
PAINT = [0, 1, 4, 5, 7, 9, 10, 11, 36, 37]
GLASS = [3, 15, 17, 35, 38]
TRIM = [2, 6, 8, 12, 13, 14, 16, 18, 19, 20, 21, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 39, 50, 51]
HEAD = [22, 52, 53, 49]   # 22 and 53: lens and housing of the same lamp, ~9 cm apart (split below)
TAIL = [24]
DROP = [40, 41, 42, 43, 44, 45, 46, 47, 48]     # wheels, tyres, brakes, the 50k-triangle lion emblem


def load_glb(path):
    d = open(path, 'rb').read()
    jl = struct.unpack_from('<I', d, 12)[0]; gl = json.loads(d[20:20 + jl])
    bl = struct.unpack_from('<I', d, 20 + jl)[0]; blob = d[28 + jl:28 + jl + bl]
    def acc(i):
        a = gl['accessors'][i]; v = gl['bufferViews'][a['bufferView']]
        dt = np.dtype({5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']])
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        off = v.get('byteOffset', 0) + a.get('byteOffset', 0); st = v.get('byteStride') or n * dt.itemsize
        if st == n * dt.itemsize:
            arr = np.frombuffer(blob, dt, a['count'] * n, off)
        else:
            arr = np.array([np.frombuffer(blob, dt, n, off + j * st) for j in range(a['count'])])
        return arr.reshape(a['count'], n) if n > 1 else arr.reshape(-1)
    def local(node):
        if 'matrix' in node: return np.array(node['matrix']).reshape(4, 4).T
        x, y, z, w = node.get('rotation', [0, 0, 0, 1]); s = np.array(node.get('scale', [1, 1, 1]))
        R = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                      [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
        M = np.eye(4); M[:3, :3] = R * s; M[:3, 3] = node.get('translation', [0, 0, 0]); return M
    prims = []
    def walk(i, M):
        n = gl['nodes'][i]; M2 = M @ local(n)
        if 'mesh' in n:
            for p in gl['meshes'][n['mesh']]['primitives']:
                P = acc(p['attributes']['POSITION']).astype(np.float64)
                N = acc(p['attributes']['NORMAL']).astype(np.float64)
                UV = acc(p['attributes']['TEXCOORD_0']).astype(np.float64) if 'TEXCOORD_0' in p['attributes'] else np.zeros((len(P), 2))
                I = acc(p['indices']).astype(np.int64)
                Pw = (np.c_[P, np.ones(len(P))] @ M2.T)[:, :3]
                Nw = N @ np.linalg.inv(M2[:3, :3]).T
                Nw /= np.maximum(np.linalg.norm(Nw, axis=1, keepdims=True), 1e-12)
                prims.append(dict(P=Pw, N=Nw, UV=UV, I=I))
        for c in n.get('children', []): walk(c, M2)
    for r in gl['scenes'][0]['nodes']: walk(r, np.eye(4))
    return prims


prims = load_glb(GLB)
assert len(prims) == 54

# ---- alignment: model wheel centres -> donor wheel centres
def centre(ids):
    P = np.concatenate([prims[i]['P'] for i in ids]); return (P.min(0) + P.max(0)) / 2
front_c, rear_c = centre([45]), centre([40])            # tyre/wheel sets: front at -X, rear at +X
carb = read_carbin(zipfile.ZipFile(SRC_ZIP).read('PEU_207SEHDi_08.carbin'))
wheel_t = [m['transform'] for p in carb['parts'] if p['part']['type'] == 43 for m in p['part']['models']]
donor_front_z = max(t[14] for t in wheel_t); donor_rear_z = min(t[14] for t in wheel_t); donor_y = wheel_t[0][13]
s = (donor_front_z - donor_rear_z) / (rear_c[0] - front_c[0])
mid_x = (front_c[0] + rear_c[0]) / 2
wheel_y = (front_c[1] + rear_c[1]) / 2
print(f'scale {s:.4f}, model wheelbase {rear_c[0]-front_c[0]:.3f} -> {s*(rear_c[0]-front_c[0]):.3f} m, '
      f'length {s*2.358:.2f} m, wheel radius {s*wheel_y:.3f} m')

# Scaling by wheelbase leaves the model about 6 cm too low for a real 207 (1,472 mm tall), so stretch height
# about the ground plane; the wheel arches rise about 1 cm, well inside the tyre clearance.
ground = donor_y - s * wheel_y
roof = max(pr['P'][:, 1].max() for i, pr in enumerate(prims) if i not in (33,) and i < 40)   # no aerial
ky = 1.472 / (s * roof)
print(f'height {s*roof:.3f} m -> 1.472 m (x{ky:.3f})')

def to_fh2(P, N):
    """model -> FH2: X_fh2 = -s*z, Y = ground + ky*s*y, Z = -s*(x - mid_x). det(-1): reverse winding."""
    Q = np.stack([-s * P[:, 2], ground + ky * s * P[:, 1], -s * (P[:, 0] - mid_x)], 1)
    M = np.stack([-N[:, 2], N[:, 1] / ky, -N[:, 0]], 1)
    M /= np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-12)
    return Q, M

AXIS_Y = 0.45   # model-space height of the car's centre line, used to tell outside from inside

def orient(P, N, I):
    """The model's winding and normals are inconsistent (it relied on double-sided rendering). Make every
    triangle face away from the car's centre line, and turn each vertex normal to agree with its faces
    while keeping the author's smoothing."""
    tri = I.reshape(-1, 3).copy()
    g = np.cross(P[tri[:, 1]] - P[tri[:, 0]], P[tri[:, 2]] - P[tri[:, 0]])
    c = P[tri].mean(1)
    away = c - np.stack([c[:, 0], np.full(len(c), AXIS_Y), np.zeros(len(c))], 1)
    flip = np.sum(g * away, 1) < 0
    tri[flip] = tri[flip][:, [0, 2, 1]]; g[flip] = -g[flip]
    acc = np.zeros_like(N)
    for k in range(3): np.add.at(acc, tri[:, k], g)
    s = np.where(np.sum(acc * N, 1) < 0, -1.0, 1.0)[:, None]
    return N * s, tri.reshape(-1)

def gather(ids, double_sided=False):
    """Every face is drawn from both sides (the model relies on it; a one-sided shell leaves holes wherever
    'outward' is ambiguous), and each side carries a normal that matches its own winding, so whichever side
    faces the camera is lit correctly. orient() first makes the winding and normals of each part agree."""
    Ps, Ns, UVs, Is, base = [], [], [], [], 0
    for i in ids:
        pr = prims[i]
        N0, I0 = orient(pr['P'], pr['N'], pr['I'])
        P, N = to_fh2(pr['P'], N0)
        I = I0.reshape(-1, 3)[:, [0, 2, 1]]           # winding reversed with the handedness change
        Ps.append(P); Ns.append(N); UVs.append(pr['UV']); Is.append(I + base); base += len(P)
        if double_sided:
            Ps.append(P); Ns.append(-N); UVs.append(pr['UV']); Is.append(I[:, [0, 2, 1]] + base); base += len(P)
    return {'P': np.concatenate(Ps), 'N': np.concatenate(Ns), 'UV': np.concatenate(UVs)}, np.concatenate(Is).reshape(-1)

outer, inner = sorted((22, 53), key=lambda i: prims[i]['P'][:, 0].mean())    # front of the car is -X
print(f'headlight lens = part {outer}, housing = part {inner}')
# ---- community 5-door 207 body (BeamNG mod by sheik; personal use), fitted to Owen's scan: ../sheik/sheik_geo.py
_S = np.load('../sheik/scan_sheik.npz')
geo = {k: ({'P': _S[k + '_P'], 'N': _S[k + '_N'], 'UV': _S[k + '_UV']}, _S[k + '_I'])
       for k in ('paint', 'glass', 'trim', 'head', 'lens', 'tail', 'clear', 'L_low', 'L_high', 'L_turnf', 'L_brake', 'L_rev', 'L_turnr')}
# straight swap: no reshaping to the scan (Owen, 29 Oct)
def merge(a, b):
    (ga, ia), (gb, ib) = geo[a], geo[b]
    return {k: np.concatenate([ga[k], gb[k]]) for k in ('P', 'N', 'UV')}, ia, ib + len(ga['P'])
head_geo, head_idx, lens_idx = merge('head', 'lens')
for k, (g, i) in geo.items():
    print(f'{k:6s} {len(g["P"]):7d} verts {len(i)//3:7d} tris  bounds {g["P"].min(0).round(2)} {g["P"].max(0).round(2)}')
(lambda *a, **k: None)('fitted_207.npz', **{f'{k}_P': g['P'] for k, (g, i) in geo.items()}, **{f'{k}_I': i for k, (g, i) in geo.items()})


# ---- write parts
src = zipfile.ZipFile(SRC_ZIP)
names = {n.lower(): n for n in src.namelist()}
ROOT = 'game:\\media\\cars\\peu_207sehdi_08\\'
def rel(path): return path.lower().replace(ROOT, '').replace('\\', '/')

from gltf_bridge import decode_group
def bright_uv1(p, direction):
    """UV sets 1-3 (AO and mask lookups) of the donor vertex facing most along `direction`: an unshadowed spot."""
    best, uv = -9, None
    for gid in p.group_order:
        d, _ = decode_group(p, gid)
        if 'NORMAL0' not in d or not any(f'TEXCOORD{j}' in d for j in (1, 2, 3, 4)): continue
        if direction == 'centre':                   # glass: the middle of the pane, away from the dark edge band
            sc = -np.linalg.norm(d['POSITION'] - d['POSITION'].mean(0), axis=1)
        else:
            sc = d['NORMAL0'][:, :3] @ np.array(direction) + 0.2 * (d['POSITION'] @ np.array(direction))
        k = int(np.argmax(sc))
        if sc[k] > best: best, uv = sc[k], {j: d[f'TEXCOORD{j}'][k] for j in (1, 2, 3, 4) if f'TEXCOORD{j}' in d}
    return uv

AO_DIR = {'scene/exterior/platform/body_a.modelbin': (0, 1, 0),
          'scene/exterior/windows/glassf_a.modelbin': 'centre',
          'scene/exterior/primarylights/headlightl_a.modelbin': (0, 0, 1),
          'scene/exterior/secondarylights/taillightl_a.modelbin': (0, 0, -1)}

def build(path, plan):
    """plan: {group id: (geo key or None, {material: True})}"""
    p = Part(src.read(names[path]))
    uv1 = bright_uv1(p, AO_DIR[path]) if path in AO_DIR else None
    if uv1 is not None: print(f'  {path.split("/")[-1]}: fixed UVs { {k: np.round(v, 3).tolist() for k, v in uv1.items()} }')
    gm = group_materials(p)
    # lamps: the new model's UVs point at random spots of the donor's lamp textures (amber indicator areas
    # included), so every vertex samples one spot the donor itself uses for that lamp's lens material
    def donor_uv(gid, mat):
        from body_swap import material_names as _mn
        nm = _mn(p); d, _ = decode_group(p, gid)
        ix = np.unique(np.concatenate([r['indices'] for r in p.render if r['group'] == gid and nm[id(r['blob'])] == mat] or [[0]]))
        return np.median(d['TEXCOORD0'][ix], 0) if 'TEXCOORD0' in d else None
    def lamp(g, gid):
        mat = LAMP_UV.get((path, gid))
        if mat is None: return g
        uv = donor_uv(gid, mat)
        if uv is None: return g
        print(f'  {path.split("/")[-1]} group {gid}: lamp UV from donor {mat} -> {np.round(uv, 3).tolist()}')
        P = g['P']
        return dict(g, UV=np.tile(uv, (len(P), 1)), UVtan=np.stack([P[:, 2] * 0.5, P[:, 1] * 0.5], 1))
    donor_morph = {}                                # crash deformation: kept per vertex, moved onto the new surface
    for gid in p.group_order:
        g0 = p.groups[gid]
        if g0['morph'] and path == 'scene/exterior/platform/body_a.modelbin':
            dd, _ = decode_group(p, gid)
            donor_morph[gid] = (dd['POSITION'][:, :3].astype(np.float64), dd['NORMAL0'][:, :3].astype(np.float64),
                                np.frombuffer(b''.join(g0['morph']), np.uint8).reshape(len(g0['morph']), -1).copy())
    for gid in p.group_order:
        key, mats = plan.get(gid, (None, None))
        if key is None:
            blank_group(p, gid)
        elif isinstance(key, list):                 # working lamps: [(geo key, donor material), ...]
            set_group(p, gid, *compose(key, gid, uv1, donor_uv))
        elif isinstance(key, dict):                 # explicit geometry with per-material triangles
            set_group(p, gid, lamp(dict(key, UVconst=uv1), gid), mats)
        else:
            g, idx = geo[key]
            g = lamp(dict(g, UVconst=uv1), gid)
            set_group(p, gid, g, {m: idx for m in mats})
    for gid, (dP, dN, dM) in donor_morph.items():
        g = p.groups[gid]
        if g['morph'] is None or not len(g['positions']): continue
        nP = np.array(g['positions'], np.float64)
        dd, _ = decode_group(p, gid); nN = dd['NORMAL0'][:, :3].astype(np.float64)
        # map the Fiesta's panel box onto the 207's, then each new vertex takes the dent data of the nearest
        # Fiesta vertex facing the same way
        lo, hi, nlo, nhi = dP.min(0), dP.max(0), nP.min(0), nP.max(0)
        q = (dP - lo) / np.maximum(hi - lo, 1e-6) * (nhi - nlo) + nlo
        from scipy.spatial import cKDTree
        dist, idx = cKDTree(q).query(nP, k=8)
        agree = np.einsum('nkj,nj->nk', dN[idx], nN)
        pick = idx[np.arange(len(nP)), np.argmin(dist * (1.5 - np.clip(agree, -1, 1)), 1)]
        g['morph'] = [bytes(r) for r in dM[pick]]
        print(f'  {path.split("/")[-1]} group {gid}: crash deformation from {len(dP)} Fiesta vertices onto {len(nP)}')
    out = p.build(); Part(out)            # re-read our own output as a check
    print(f'built {path}: groups {[(gid, sorted(gm[gid])) for gid in p.group_order]}')
    return out

def compose(pairs, gid, uv1, donor_uv):
    """one vertex buffer holding several categories, each drawn with a donor lamp material. Every vertex samples
    the spot of the donor's texture that material itself uses, so the game lights it as the donor's lamp:
    head/high beam with the headlights, brake with the brakes (and dimly as a tail lamp), reverse, indicators."""
    Ps, Ns, UVs, by, base = [], [], [], {}, 0
    for k, mat in pairs:
        g, idx = geo[k]
        uv = donor_uv(gid, mat)
        Ps.append(g['P']); Ns.append(g['N']); UVs.append(np.tile(uv, (len(g['P']), 1)) if uv is not None else g['UV'])
        by[mat] = np.concatenate([by[mat], idx + base]) if mat in by else idx + base; base += len(g['P'])
        print(f'    group {gid}: {k:8s} -> {mat}  ({len(idx) // 3} tris)')
    P = np.concatenate(Ps)
    G = dict(P=P, N=np.concatenate(Ns), UV=np.concatenate(UVs), UVconst=uv1, UVtan=np.stack([P[:, 2] * 0.5, P[:, 1] * 0.5], 1))
    return G, by

LAMP_UV = {('scene/exterior/primarylights/headlightl_a.modelbin', 0): 'gls_patternCH1_009',
           ('scene/exterior/primarylights/headlightl_a.modelbin', 2): 'chrome',
           ('scene/exterior/secondarylights/taillightl_a.modelbin', 0): 'gls_patternCH1_009_custom_red',
           ('scene/exterior/secondarylights/taillightl_a.modelbin', 2): 'gls_patternCH1_009_custom_red'}
replaced = {}
replaced['scene/exterior/platform/body_a.modelbin'] = build('scene/exterior/platform/body_a.modelbin', {
    0: ('paint', ['carpaint']), 4: ('paint', ['carpaint']), 1: ('trim', ['blkplastic_mgl']), 5: ('trim', ['blkplastic_mgl'])})
_gl, _gi, _li = merge('glass', 'lens')        # headlight lenses as clear window glass (the donor's lamp-lens
replaced['scene/exterior/windows/glassf_a.modelbin'] = build('scene/exterior/windows/glassf_a.modelbin', {   # texture tints them amber)
    0: (_gl, {'gls_window': np.concatenate([_gi, _li])})})
HL, TL = 'scene/exterior/primarylights/headlightl_a.modelbin', 'scene/exterior/secondarylights/taillightl_a.modelbin'
replaced[HL] = build(HL, {      # groups 0 (near LODs) and 2 (far LOD); 1 and 3 (black housings) left empty
    0: ([('head', 'chrome'), ('L_low', 'hl_hb'), ('L_high', 'hb'), ('L_turnf', 'hl_turn')], None),
    2: ([('head', 'chrome'), ('L_low', 'hl_hb'), ('L_high', 'hl_hb'), ('L_turnf', 'hl_turn')], None)})
replaced[TL] = build(TL, {      # brake has its own groups (1 and 3) in the donor
    0: ([('tail', 'gls_patternCH1_009_custom_red'), ('clear', 'gls_ridgesCH1_003_custom_clear'),
         ('L_rev', 'LBK_standardCH1_003_custom_reverse'), ('L_turnr', 'LBK_standardCH1_003_custom_turn')], None),
    2: ([('tail', 'gls_patternCH1_009_custom_red'), ('clear', 'chrome'),
         ('L_rev', 'LBK_standardCH1_003_custom_reverse'), ('L_turnr', 'LBK_standardCH1_003_custom_turn')], None),
    1: ([('L_brake', 'LBK_smoothChrome_custom_brake')], None),
    3: ([('L_brake', 'LBK_smoothChrome_custom_brake')], None)})

# ---- Lights.bin: the light sources (beams on the road, glow sprites). Each is tied to a lamp part and goes out
# when that part isn't on the car, and the Fiesta's bulb / lamp-glass parts aren't: re-tie them to the 207 lamp
# parts and move them from the Fiesta's lamps into the 207's.
def lights_bin(d):
    import struct
    o = 8; n = struct.unpack_from('<I', d, o)[0]; o += 4; paths = []
    for i in range(n):
        L = struct.unpack_from('<I', d, o)[0]; paths.append((d[o + 4:o + 4 + L].decode(), d[o + 4 + L:o + 6 + L])); o += 6 + L
    cnt = struct.unpack_from('<I', d, o)[0]; o += 4; body = bytearray(d[o:])
    S = np.load('../sheik/scan_sheik.npz')
    def c(k, side, sel=lambda P: np.ones(len(P), bool)):
        P = S[k + '_P']; P = P[(P[:, 0] * side > 0.2) & sel(P)]; return P.mean(0)
    rear = lambda P: P[:, 1] < 1.0                    # rear cluster without the tailgate's third brake light
    FRONT_F, REAR_F, CHMSL_F = np.array([0.648, 0.61, 1.576]), np.array([0.634, 0.844, -1.659]), np.array([0, 1.17, -1.731])
    moves = []
    for i in range(cnt):
        e = 76 * i; t, f, m = struct.unpack_from('<IIi', body, e)
        for k in range(2):
            p = np.array(struct.unpack_from('<3f', body, e + 12 + 32 * k)); side = 1 if p[0] > 0 else -1
            if t == 11:   new = p + (S['L_brake_P'][S['L_brake_P'][:, 1] > 1.0].mean(0) - CHMSL_F)
            elif t == 0:  new = np.array([0.687 * side, 0.203, 1.836]) + (p - np.array([0.667 * side, 0.186, 1.825]))
            elif p[2] > 0: new = p + (c('L_low', side) - FRONT_F * [side, 1, 1])
            else:         new = p + (c('L_brake', side, rear) - REAR_F * [side, 1, 1])
            struct.pack_into('<3f', body, e + 12 + 32 * k, *new)
        moves.append((t, np.round(new, 3).tolist()))
    def retie(path):
        name = path.split('\\')[-1]
        if name in ('headlightl_a.modelbin', 'taillightl_a.modelbin'): return path
        to = 'headlightl_a.modelbin' if ('head' in name or 'fog' in name or 'glasslhl' in name) else 'taillightl_a.modelbin'
        sub = 'primarylights' if to.startswith('head') else 'secondarylights'
        return ROOT + 'scene\\exterior\\' + sub + '\\' + to
    out = bytearray(d[:12])
    for pth, tail in paths:
        q = retie(pth).encode(); out += struct.pack('<I', len(q)) + q + tail
    out += struct.pack('<I', cnt) + body
    print('lights re-tied:', sorted(set(retie(p).split('\\')[-1] for p, _ in paths)), '\n  moved:', moves)
    return bytes(out)
replaced['lights.bin'] = lights_bin(src.read('Lights.bin'))

# ---- carbin: keep the new body parts, interior, wheels, brakes, suspension, chassis; drop Fiesta panels
KEEP_EXTERIOR = {rel(ROOT + p.replace('/', '\\')) for p in replaced} | {
    'scene/exterior/chassis/undercarriage.modelbin'}   # (Fiesta engine bay dropped: it pokes through the 207's lower bonnet;
                                                       #  Fiesta exhaust dropped: the 207 body has its own tailpipe)
def keep(m):
    r = rel(m['path'])
    if r.startswith('scene/interior/') and 'interiorwindows' not in r: return True
    if r.startswith('scene/_library/'): return True
    return r in KEEP_EXTERIOR
removed = []
for p in carb['parts']:
    ms = p['part']['models']
    removed += [rel(m['path']) for m in ms if not keep(m)]
    p['part']['models'] = [m for m in ms if keep(m)]
for up in carb['upgradable_parts']:
    if up['type'] in (9, 34):           # Fiesta wing / third brake light, front bumpers and fog lights
        removed += [rel(sm['model']['path']) for sm in up.get('shared_models', [])]
        up['shared_models'] = []
# donor AO maps stay: the new panels sample one unshadowed texel of them (see bright_uv1)
# wheel positions: the 207's own 2.540 m wheelbase (donor Fiesta parts sat at +-1.263). Wheels, brake discs and
# calipers move fore/aft together; the physics wheelbase is set to match in Data_CarBody (database.json).
HALF_WB_OLD, HALF_WB_NEW = 1.263, 1.270
moved = []
for p in carb['parts']:
    for m in p['part']['models']:
        t = list(m['transform'])
        if p['part']['type'] in (4, 43) and abs(t[14]) > 1.0:
            t[14] += (HALF_WB_NEW - HALF_WB_OLD) * (1 if t[14] > 0 else -1)
            m['transform'] = t; moved.append((m['path'].split(chr(92))[-1], round(t[14], 3)))
print('moved to the 207 wheelbase:', moved)
new_carbin = write_carbin(carb); read_carbin(new_carbin)
print('removed from carbin:', len(removed), sorted(set(x.split('/')[-1] for x in removed)))

import os
os.makedirs('out_sheik', exist_ok=True)
out = zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED)
for info in src.infolist():
    key = info.filename.lower()
    data = replaced.get(key)
    if info.filename == 'PEU_207SEHDi_08.carbin':
        data = new_carbin
    out.writestr(zipfile.ZipInfo(info.filename, date_time=info.date_time),
                 data if data is not None else src.read(info.filename), compress_type=zipfile.ZIP_DEFLATED)
out.close()
print('wrote', OUT_ZIP, os.path.getsize(OUT_ZIP))
