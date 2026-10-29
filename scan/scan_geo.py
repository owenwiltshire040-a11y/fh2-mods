"""Owen's KIRI scan -> paint and trim geometry in FH2 car space, fitted to the PazMedia template.

The scan supplies the body shape; faces are sorted by which template category they sit nearest
(paint / black trim / glass / lights). Glass and lights come from the template, so scan faces there
(and the interior seen through the windows) are dropped. Wheels and the ragged ground edge are cut off.
"""
import numpy as np, trimesh, fast_simplification
from scipy.spatial import cKDTree

T = np.load('../car207/fitted_207.npz')
car = trimesh.load('car_raw.glb', force='mesh', process=False)
Q = np.load('Q0.npy')                       # scan in FH2 axes, real scale, ground at y=0

# ---- fit: scaled ICP onto the template's outer surfaces
outer = np.concatenate([T['paint_P'], T['glass_P'], T['tail_P'], T['head_P'], T['lens_P']])
tree = cKDTree(outer)
rng = np.random.default_rng(1)
s = Q[rng.choice(len(Q), 30000, replace=False)]
R, t, sc = np.eye(3), np.array([0, -0.19, 0]), 1.0
for it in range(100):
    X = sc * s @ R.T + t; dist, idx = tree.query(X); m = dist < np.percentile(dist, 60)
    a, b = s[m], outer[idx[m]]; ma, mb = a.mean(0), b.mean(0)
    U, Sg, Vt = np.linalg.svd((a - ma).T @ (b - mb)); D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T; sc = (Sg * np.diag(D)).sum() / ((a - ma) ** 2).sum(); t = mb - sc * R @ ma
dist, _ = tree.query(sc * s @ R.T + t)
print(f'fit: scale {sc:.4f}, shift {t.round(3)}, rotation {np.degrees(np.arccos(min(1, (np.trace(R) - 1) / 2))):.2f} deg, '
      f'median gap {np.median(dist) * 100:.1f} cm, 60% within {np.percentile(dist, 60) * 100:.1f} cm')
P = sc * Q @ R.T + t
F = car.faces
# per-face photo colour (median of three samples), used to tell black plastic from paint
img = np.asarray(car.visual.material.baseColorTexture if hasattr(car.visual.material, 'baseColorTexture') and car.visual.material.baseColorTexture is not None else car.visual.material.image).astype(np.float32)[..., :3] / 255
uv = car.visual.uv; H, W = img.shape[:2]
def tex(u): return img[np.clip(((1 - u[:, 1]) * H).astype(int), 0, H - 1), np.clip((u[:, 0] * W).astype(int), 0, W - 1)]
col0 = np.median(np.stack([tex(uv[F[:, k]]) for k in range(3)]), 0)
lum0 = col0 @ [0.299, 0.587, 0.114]
C0 = P[F].mean(1)

# ---- smooth the photogrammetry lumps (Taubin keeps the volume), then thin the mesh
m = trimesh.Trimesh(P, F, process=False)
m.merge_vertices(); m.remove_unreferenced_vertices()
trimesh.smoothing.filter_taubin(m, lamb=0.5, nu=0.53, iterations=25)
Pv, Fv = fast_simplification.simplify(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.int32), target_reduction=0.55)
m = trimesh.Trimesh(Pv, Fv, process=False)
print('scan after smoothing/thinning:', len(m.vertices), 'verts', len(m.faces), 'tris')
P, F = np.asarray(m.vertices, np.float64), np.asarray(m.faces)
np.savez('scan_surface.npz', P=P, F=F)
C = P[F].mean(1)
_, near0 = cKDTree(C0).query(C)
col = col0[near0]; lum = lum0[near0]
np.savez('scan_surface.npz', P=P, F=F, lum=lum)

# ---- cuts: wheels (donor wheel centres) and the ragged bottom edge
WHEELS = [(sx * 0.833, 0.124, sz * 1.263) for sx in (-1, 1) for sz in (-1, 1)]
keep = C[:, 1] > -0.02
for wx, wy, wz in WHEELS:
    r = np.hypot(C[:, 1] - wy, C[:, 2] - wz)
    keep &= ~((r < 0.335) & (np.sign(C[:, 0]) == np.sign(wx)) & (np.abs(C[:, 0]) > 0.5))

# ---- sort faces by nearest template category
cats = ['paint', 'trim', 'glass', 'head', 'lens', 'tail']
pts = np.concatenate([T[c + '_P'] for c in cats]); lab = np.concatenate([np.full(len(T[c + '_P']), i) for i, c in enumerate(cats)])
d, i = cKDTree(pts).query(C)
cat = lab[i]
keep &= (d < 0.15) & (cat <= 1)          # glass/light zones come from the template; >15 cm = interior
dark = (lum < 0.16) & (cat == 1)        # black plastic only where the template has trim (shadows fool colour alone)
paint = keep & ~dark; trim = keep & dark
pc = col[paint]; print('paint colour (photo, median sRGB):', (np.median(pc, 0) * 255).round().astype(int).tolist())
print('faces: paint', paint.sum(), 'trim', trim.sum(), 'dropped', (~(paint | trim)).sum())


def geo(mask):
    f = F[mask]
    used = np.unique(f); remap = -np.ones(len(P), int); remap[used] = np.arange(len(used))
    Pg = P[used]; I = remap[f]
    g = np.cross(Pg[I[:, 1]] - Pg[I[:, 0]], Pg[I[:, 2]] - Pg[I[:, 0]])
    N = np.zeros_like(Pg)
    for k in range(3): np.add.at(N, I[:, k], g)
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    UV = np.stack([Pg[:, 2] * 0.25 + 0.5, Pg[:, 1] * 0.25 + 0.5], 1)     # planar; carpaint has no texture
    n = len(Pg)                                                       # double-sided, each side its own normal
    return dict(P=np.concatenate([Pg, Pg]), N=np.concatenate([N, -N]), UV=np.concatenate([UV, UV]),
                I=np.concatenate([I, I[:, [0, 2, 1]] + n]).reshape(-1))

# the template fills what the scan missed (glass roof surround, sills): its paint faces far from any kept scan paint.
# Black trim comes from the template too: it is cleaner than the scan's speckled dark patches.
sp = cKDTree(C[paint | trim])
TP = T['paint_P']; TI = T['paint_I'].reshape(-1, 3)
far = sp.query(TP[TI].mean(1))[0] > 0.035
print('template paint faces used to fill gaps:', far.sum() // 2, 'of', len(TI) // 2)
out = {}
g = geo(paint)
fill_I = TI[far]; used = np.unique(fill_I); remap = -np.ones(len(TP), int); remap[used] = np.arange(len(used))
fP = TP[used]; fI = remap[fill_I]
fg = np.cross(fP[fI[:, 1]] - fP[fI[:, 0]], fP[fI[:, 2]] - fP[fI[:, 0]])
fN = np.zeros_like(fP)
for k in range(3): np.add.at(fN, fI[:, k], fg)
fN /= np.maximum(np.linalg.norm(fN, axis=1, keepdims=True), 1e-12)
fUV = np.stack([fP[:, 2] * 0.25 + 0.5, fP[:, 1] * 0.25 + 0.5], 1)
n0 = len(g['P'])
out['paint_P'] = np.concatenate([g['P'], fP]); out['paint_N'] = np.concatenate([g['N'], fN])
out['paint_UV'] = np.concatenate([g['UV'], fUV]); out['paint_I'] = np.concatenate([g['I'], (fI + n0).reshape(-1)])
out['fill_P'] = fP; out['fill_I'] = fI.reshape(-1)
g = geo(trim)
for kk, v in g.items(): out[f'trim_{kk}'] = v
np.savez('scan_geo.npz', **out)

# preview mesh (display mirror for a right-handed viewer)
pv = trimesh.Scene()
for k, col in (('paint', [140, 160, 185, 255]), ('trim', [25, 25, 25, 255])):
    mm = trimesh.Trimesh(out[k + '_P'] * [-1, 1, 1], out[k + '_I'].reshape(-1, 3), process=False); mm.visual.face_colors = col
    pv.add_geometry(mm, k)
for k, col in (('trimT', [40, 40, 40, 255]), ('glass', [60, 70, 90, 255]), ('head', [230, 230, 230, 255]), ('lens', [200, 220, 255, 255]), ('tail', [200, 0, 0, 255])):
    kt = k.rstrip('T'); mm = trimesh.Trimesh(T[kt + '_P'] * [-1, 1, 1], T[kt + '_I'].reshape(-1, 3), process=False); mm.visual.face_colors = col
    pv.add_geometry(mm, k)
pv.export('viewer/hybrid.glb')
