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
OUT_ZIP = 'out/PEU_207SEHDi_08.zip'

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
geo = {'paint': gather(PAINT, True), 'glass': gather(GLASS, True), 'trim': gather(TRIM, True),
       'head': gather([inner, 52, 49], True), 'lens': gather([outer], True), 'tail': gather(TAIL, True)}
def merge(a, b):
    (ga, ia), (gb, ib) = geo[a], geo[b]
    return {k: np.concatenate([ga[k], gb[k]]) for k in ('P', 'N', 'UV')}, ia, ib + len(ga['P'])
head_geo, head_idx, lens_idx = merge('head', 'lens')
for k, (g, i) in geo.items():
    print(f'{k:6s} {len(g["P"]):7d} verts {len(i)//3:7d} tris  bounds {g["P"].min(0).round(2)} {g["P"].max(0).round(2)}')
np.savez('fitted_207.npz', **{f'{k}_P': g['P'] for k, (g, i) in geo.items()}, **{f'{k}_I': i for k, (g, i) in geo.items()})


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
    for gid in p.group_order:
        key, mats = plan.get(gid, (None, None))
        if key is None:
            blank_group(p, gid)
        elif isinstance(key, dict):                 # explicit geometry with per-material triangles
            set_group(p, gid, dict(key, UVconst=uv1), mats)
        else:
            g, idx = geo[key]
            g = dict(g, UVconst=uv1)
            set_group(p, gid, g, {m: idx for m in mats})
    out = p.build(); Part(out)            # re-read our own output as a check
    print(f'built {path}: groups {[(gid, sorted(gm[gid])) for gid in p.group_order]}')
    return out

replaced = {}
replaced['scene/exterior/platform/body_a.modelbin'] = build('scene/exterior/platform/body_a.modelbin', {
    0: ('paint', ['carpaint']), 4: ('paint', ['carpaint']), 1: ('trim', ['blkplastic_mgl']), 5: ('trim', ['blkplastic_mgl'])})
replaced['scene/exterior/windows/glassf_a.modelbin'] = build('scene/exterior/windows/glassf_a.modelbin', {
    0: ('glass', ['gls_window'])})
replaced['scene/exterior/primarylights/headlightl_a.modelbin'] = build('scene/exterior/primarylights/headlightl_a.modelbin', {
    0: (head_geo, {'chrome': head_idx, 'gls_patternCH1_009': lens_idx}),
    2: (head_geo, {'chrome': np.concatenate([head_idx, lens_idx])})})
replaced['scene/exterior/secondarylights/taillightl_a.modelbin'] = build('scene/exterior/secondarylights/taillightl_a.modelbin', {
    0: ('tail', ['gls_patternCH1_009_custom_red']), 2: ('tail', ['gls_patternCH1_009_custom_red'])})

# ---- carbin: keep the new body parts, interior, wheels, brakes, suspension, chassis; drop Fiesta panels
KEEP_EXTERIOR = {rel(ROOT + p.replace('/', '\\')) for p in replaced} | {
    'scene/exterior/engine/enginebay_a.modelbin', 'scene/exterior/chassis/undercarriage.modelbin',
    'scene/exterior/chassis/exhaust_a.modelbin'}
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
new_carbin = write_carbin(carb); read_carbin(new_carbin)
print('removed from carbin:', len(removed), sorted(set(x.split('/')[-1] for x in removed)))

import os
os.makedirs('out', exist_ok=True)
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
