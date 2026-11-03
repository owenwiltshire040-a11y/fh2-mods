"""Red Bull RB22 (2026) source -> geo.pkl in FH2 space, measured wheels, cut-out decals (after cars/jordanej11).

Source: Owen's model.glb (27 nodes, metres, y up, nose +z, the car's left +x). Wheels: 'sidewall.007' tyres (two meshes,
measured per corner), 'redbull_wheel_hub.007' rims (split into front/rear by z), 'discs.007' skipped. Decal materials
with alpha are clipped against their alpha mask (no opaque rectangles) and moved 2 mm proud. UVs are moved per triangle
into the 0..1 tile (the source repeats tiles up to +-200; half-float packing would blur them). The steering wheel's own
instances get their own material names so only they move with the steering spindle. The central rain light is split
from the other rear lamp details.
"""
from pathlib import Path
import json, pickle, hashlib
import numpy as np, trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.ndimage import distance_transform_edt
from PIL import Image

p = Path(__file__).resolve().parent; (p / 'textures').mkdir(exist_ok=True)
s = trimesh.load(p / 'model.glb', force='scene')
HUB_Y, MID_Z = .1511658, .05                     # the confirmed Codex/Jordan convention for open-wheel cars
SKIP = {'sidewall.007', 'discs.007'}
DECALS = {'redbull_decals.005', 'redbull_number_3.005', 'sw_decals.004', 'clearled.003'}
STEERING_NODES_Z = (.6, .85)                     # steering wheel instances: |x| < .14, y .49-.67, z .64-.80

# ---- wheels from the tyres: connected components per corner
raw = {}
for node in s.graph.nodes_geometry:
    T, key = s.graph[node]; m = s.geometry[key]
    if m.visual.material.name != 'sidewall.007': continue
    mm = trimesh.Trimesh(trimesh.transform_points(m.vertices, T), m.faces, process=True); a = mm.edges_unique
    n, lab = connected_components(coo_matrix((np.ones(len(a)), a.T), shape=(len(mm.vertices),) * 2), directed=False)
    for i in range(n):
        v = mm.vertices[lab == i]; c = v.mean(0); k = 'HUB_' + ('L' if c[0] > 0 else 'R') + ('F' if c[2] > 0 else 'R')
        raw.setdefault(k, []).append(v)
wheels_src = {}
for k, vs in raw.items():
    v = np.concatenate(vs); lo, hi = v.min(0), v.max(0)
    wheels_src[k] = dict(centre=(lo + hi) / 2, radius=float((hi[1] - lo[1] + hi[2] - lo[2]) / 4), width=float(hi[0] - lo[0]))
assert len(wheels_src) == 4, wheels_src.keys()
mid = np.mean([w['centre'] for w in wheels_src.values()], axis=0)
off = np.array([mid[0], HUB_Y - mid[1], MID_Z - mid[2]])


def clip_alpha(V, N, UV, mask):
    """keep only the parts of each triangle over opaque texels (UV in image space: u right, v down)"""
    out = []; h, w = mask.shape
    def walk(v, n, u, depth=0):
        lo = np.floor(u.min(0) * [w - 1, h - 1]).astype(int); hi = np.ceil(u.max(0) * [w - 1, h - 1]).astype(int)
        lo = np.maximum(lo, 0); hi = np.minimum(hi, [w - 1, h - 1])
        if np.any(hi < lo): return
        patch = mask[lo[1]:hi[1] + 1, lo[0]:hi[0] + 1]
        if not patch.any(): return
        if patch.mean() > .97: out.append((v, n, u)); return
        if depth >= 6 or max(hi - lo) <= 16:
            c = np.clip(np.round(u.mean(0) * [w - 1, h - 1]).astype(int), 0, [w - 1, h - 1])
            if mask[c[1], c[0]]: out.append((v, n, u))
            return
        vv = np.vstack([v, (v + np.roll(v, -1, axis=0)) / 2]); nn = np.vstack([n, (n + np.roll(n, -1, axis=0)) / 2]); uu = np.vstack([u, (u + np.roll(u, -1, axis=0)) / 2])
        for ix in [[0, 3, 5], [3, 1, 4], [5, 4, 2], [3, 4, 5]]: walk(vv[ix], nn[ix], uu[ix], depth + 1)
    for v, n, u in zip(V.reshape(-1, 3, 3), N.reshape(-1, 3, 3), UV.reshape(-1, 3, 2)): walk(v, n, u)
    if not out: return np.zeros((0, 3)), np.zeros((0, 3)), np.zeros((0, 2))
    return tuple(np.concatenate([o[i] for o in out]) for i in range(3))


parts, textures, mapping, counts = {}, {}, {}, {}
def add(mat, node, V, N, UV, image, solid=None):
    parts.setdefault(mat, []).append(dict(node=node, mat=mat, V=V, N=N, UV=UV)); counts[mat] = counts.get(mat, 0) + len(V) // 3
    if mat in textures: return
    img = Image.new('RGB', (64, 64), solid) if solid else image.convert('RGB')
    fn = hashlib.sha1(mat.encode()).hexdigest()[:10] + '.png'; img.save(p / 'textures' / fn); textures[mat] = fn
    mapping[mat] = ('textured', 't' + fn[:-4])

for node in s.graph.nodes_geometry:
    T, key = s.graph[node]; m = s.geometry[key]; mat = m.visual.material.name
    if mat in SKIP: continue
    V = trimesh.transform_points(m.vertices, T); N = m.vertex_normals @ T[:3, :3].T
    V = V * [-1, 1, 1] + off; N = N * [-1, 1, 1]; F = m.faces[:, ::-1]           # mirror x: FH2 -x is the car's left
    UV = m.visual.uv if m.visual.uv is not None else np.zeros((len(m.vertices), 2))
    V, N, UV = V[F].reshape(-1, 3), N[F].reshape(-1, 3), UV[F].reshape(-1, 2).astype(np.float64)
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
    # every triangle's UVs into the 0..1 tile (whole-tile shift: the texture repeats, so nothing changes visually)
    t = UV.reshape(-1, 3, 2); t -= np.floor(t.mean(1, keepdims=True)); UV = t.reshape(-1, 2)
    image = getattr(m.visual.material, 'baseColorTexture', None)
    image = (image or Image.new('RGB', (64, 64), (60, 60, 60))).convert('RGBA')
    c = V.reshape(-1, 3, 3).mean(1)
    # names by role
    if mat == 'redbull_wheel_hub.007':
        for tag, k in (('rim_front', c[:, 2] > MID_Z), ('rim_rear', c[:, 2] <= MID_Z)):
            sel = np.repeat(k, 3); add(tag, node, V[sel], N[sel], UV[sel], image); mapping[tag] = None
        continue
    if mat == 'redbull_carbon1.007':      # its source UVs are corrupt (+-3.5e6): a plain dark carbon colour instead
        add(mat, node, V, N, UV * 0, image, solid=(28, 28, 30)); continue
    in_wheel = (np.abs(c[:, 0]) < .14) & (c[:, 1] > .49 + off[1]) & (c[:, 1] < .67 + off[1]) & (c[:, 2] > .64 + off[2]) & (c[:, 2] < .80 + off[2])
    if mat == 'rear_light_2.007':
        rain = (np.abs(c[:, 0]) < .1) & (c[:, 1] < .5 + off[1]) & (c[:, 2] < -2.3 + off[2])
        for tag, k in (('rain_light', rain), (mat, ~rain)):
            sel = np.repeat(k, 3)
            if sel.any(): add(tag, node, V[sel], N[sel], UV[sel], image)
        continue
    if mat in DECALS:
        rgba = np.array(image.resize((1024, 1024), Image.Resampling.LANCZOS)); alpha = rgba[:, :, 3] > 100
        img_uv = UV * [1, -1] + [0, 1]                         # glTF-flipped v -> image rows
        img_uv -= np.floor(img_uv.reshape(-1, 3, 2).mean(1, keepdims=True)).repeat(3, 1).reshape(-1, 2)
        V, N, img_uv = clip_alpha(V, N, img_uv, alpha)
        UV = img_uv * [1, -1] + [0, 1]
        V = V + N * .002
        idx = distance_transform_edt(~alpha, return_distances=False, return_indices=True)
        rgba[:, :, :3] = rgba[idx[0], idx[1], :3]; image = Image.fromarray(rgba[:, :, :3])
        print(f'{mat}: {len(V) // 3} cut-out decal triangles', flush=True)
        if not len(V): continue
        c = V.reshape(-1, 3, 3).mean(1)
        in_wheel = (np.abs(c[:, 0]) < .14) & (c[:, 1] > .49 + off[1]) & (c[:, 1] < .67 + off[1]) & (c[:, 2] > .64 + off[2]) & (c[:, 2] < .80 + off[2])
    WHEEL_ONLY = ('redbull_steeringwheel.004', 'sw_decals.004', 'gp21_LCD.003', 'clearled.003', 'kers_blue.003')
    sw = np.repeat(in_wheel, 3) if mat in ('redbull_carbon2.007', 'black_s.006') else np.full(len(V), mat in WHEEL_ONLY)
    if sw.any():
        tag = 'sw_' + mat
        if sw.any(): add(tag, node, V[sw], N[sw], UV[sw], image)
        V, N, UV = V[~sw], N[~sw], UV[~sw]
        if not len(V): continue
    add(mat, node, V, N, UV, image)
    if mat in ('redbull_mirror_right.005', 'glass.005'): mapping[mat] = ('plain', 'chrome') if mat == 'glass.005' else mapping[mat]

wheels = {k: dict(centre=w['centre'] * [-1, 1, 1] + off, radius=w['radius']) for k, w in wheels_src.items()}
wb = float(np.mean([wheels[k]['centre'][2] for k in ('HUB_LF', 'HUB_RF')]) - np.mean([wheels[k]['centre'][2] for k in ('HUB_LR', 'HUB_RR')]))
r = float(np.mean([w['radius'] for w in wheels.values()]))
# the textured source rim: the left-front wheel's own rim only (rimbuild centres it on HUB_LF)
lf = wheels['HUB_LF']['centre']; src_rim = []
for fr in parts['rim_front']:
    k = np.repeat(np.sign(fr['V'].reshape(-1, 3, 3).mean(1)[:, 0]) == np.sign(lf[0]), 3)
    if k.any(): src_rim.append(dict(fr, mat='SOURCE_RIM', V=fr['V'][k], N=fr['N'][k], UV=fr['UV'][k]))
parts['SOURCE_RIM'] = src_rim; mapping['SOURCE_RIM'] = None
pickle.dump(dict(parts=parts, wheels=wheels, ground=HUB_Y - r, wheelbase=wb, materials=sorted(parts)), open(p / 'geo.pkl', 'wb'))
(p / 'source-analysis.json').write_text(json.dumps(dict(offset=off.tolist(), wheelbase=wb, tyre_radius=r,
    wheels={k: {'centre': w['centre'].tolist(), 'radius': w['radius'], 'width': w['width']} for k, w in wheels_src.items()},
    textures=textures, mapping=mapping, triangles=counts), indent=2))
print('wheelbase', round(wb, 4), 'tyre radius', round(r, 4), 'offset', off.round(4), 'triangles', sum(counts.values()))
for k, w in sorted(wheels.items()): print(' ', k, w['centre'].round(4))
