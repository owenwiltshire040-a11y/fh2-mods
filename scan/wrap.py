"""Wrap the clean PazMedia body onto Owen's scan: each template vertex moves along its normal toward the scanned
surface (dents, proportions), with the offsets smoothed so photogrammetry noise and holes don't come through.
Glass, lights and trim ride along on the same smoothed field, so nothing separates."""
import numpy as np, trimesh, scipy.sparse as sp
from scipy.spatial import cKDTree

def offsets(geo, scan_npz, valid_keys=('paint', 'trim'), max_d=0.06, radius=0.035, iters=12):
    S = np.load(scan_npz); scan = trimesh.Trimesh(S['P'], S['F'], process=False)
    allP = np.concatenate([g['P'] for g, _ in geo.values()])
    allN = np.concatenate([g['N'] for g, _ in geo.values()])
    valid0 = np.concatenate([np.full(len(g['P']), k in valid_keys) for k, (g, _) in geo.items()])
    key = np.round(allP / 1e-4).astype(np.int64)
    uq, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    U = allP[first]; Nn = allN[first]
    valid = np.zeros(len(U), bool); np.logical_or.at(valid, inv, valid0)
    cp, dist, tid = scan.nearest.on_surface(U)
    off = np.einsum('ij,ij->i', cp - U, Nn)                      # signed offset along the template normal
    agree = np.abs(np.einsum('ij,ij->i', scan.face_normals[tid], Nn)) > 0.6
    w = (valid & (dist < max_d) & agree).astype(float)
    off = np.clip(off, -max_d, max_d) * w
    # normalised smoothing over a spatial neighbourhood (works across separate parts)
    tree = cKDTree(U); pairs = tree.query_pairs(radius, output_type='ndarray')
    n = len(U)
    A = sp.coo_matrix((np.ones(2 * len(pairs)), (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), (n, n)).tocsr() + sp.identity(n)
    deg = np.asarray(A.sum(1)).ravel()
    num, den = off.copy(), w.copy()
    for _ in range(iters):
        num = A @ num / deg; den = A @ den / deg
    field = np.where(den > 1e-6, num / np.maximum(den, 1e-6), 0) * np.clip(den * 3, 0, 1)
    print(f'wrap: {int(w.sum())}/{len(U)} points matched to the scan; offsets mm  p5 {np.percentile(field,5)*1000:.0f}  '
          f'median {np.median(field)*1000:.0f}  p95 {np.percentile(field,95)*1000:.0f}')
    return field[inv]          # per vertex of allP (concatenated in geo order)

def apply(geo, field):
    i = 0
    for k, (g, idx) in geo.items():
        n = len(g['P']); f = field[i:i + n]; i += n
        # move along the normal of the first copy; double-sided copies have -N, so use a consistent direction
        P = g['P']; N = g['N']
        key = np.round(P / 1e-4).astype(np.int64)
        _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
        Nd = N[first][inv.reshape(-1)]
        g['P'] = P + Nd * f[:, None]
        # recompute normals from the moved faces, keeping each copy's side
        tri = idx.reshape(-1, 3); Pn = g['P']
        c = np.cross(Pn[tri[:, 1]] - Pn[tri[:, 0]], Pn[tri[:, 2]] - Pn[tri[:, 0]])
        acc = np.zeros_like(Pn)
        for j in range(3): np.add.at(acc, tri[:, j], c)
        acc /= np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-12)
        sign = np.where(np.einsum('ij,ij->i', acc, N) < 0, -1.0, 1.0)[:, None]
        newN = acc * sign
        bad = np.linalg.norm(acc, axis=1) < 0.5
        newN[bad] = N[bad]
        g['N'] = newN
