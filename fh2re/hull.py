"""Collision hull (physicsdefinition.bin) from the model, in the Charger donor's layout (NOTES: DONOR ZIP ANATOMY).

Layout (2,244 B, verified 30 Oct): bytes 92-104 = hull half-extents x, y, z + bounding radius; 128/132 = hull centre
y, z; two blocks of 62 points x 16 B (u32 0, x, y, z) at 192 (the hull) and 1240 (the same with y raised to
>= floor + 0.2: the underbody hull). Points only — no faces are stored, so any 62 points whose hull is the shape do.
"""
import struct
import numpy as np
from scipy.spatial import ConvexHull

N = 62


def decimate(P, n=N):
    h = ConvexHull(P); idx = list(h.vertices)
    while len(idx) > n:                                       # drop the point whose loss shrinks the hull least
        Q = P[idx]; base = ConvexHull(Q).volume; best = None
        cand = range(len(idx)) if len(idx) < 160 else np.argsort(np.linalg.norm(Q - Q.mean(0), axis=1))[:len(idx) // 2]
        for i in cand:
            v = ConvexHull(np.delete(Q, i, 0)).volume
            if best is None or base - v < best[0]: best = (base - v, i)
        idx.pop(best[1])
    Q = P[idx]
    while len(Q) < n: Q = np.vstack([Q, Q[:n - len(Q)]])      # pad with repeats (inside the hull, harmless)
    return Q


def build(donor_bin, points, half_width, floor_y, underbody=0.2):
    P = np.asarray(points, float).copy()
    P[:, 0] = np.clip(P[:, 0], -half_width, half_width)       # mirrors etc. out
    P[:, 1] = np.maximum(P[:, 1], floor_y)
    Q = decimate(np.unique(P.round(3), axis=0))
    d = bytearray(donor_bin); assert len(d) == 2244, 'unexpected physicsdefinition.bin'
    lo, hi = Q.min(0), Q.max(0); c = (lo + hi) / 2; half = (hi - lo) / 2
    r = np.linalg.norm(Q - [0, c[1], c[2]], axis=1).max() * (2.6722 / 2.6595)   # the Charger's margin
    struct.pack_into('<4f', d, 92, half[0], half[1], half[2], r)
    struct.pack_into('<2f', d, 128, c[1], c[2])
    U = Q.copy(); U[:, 1] = np.maximum(U[:, 1], lo[1] + underbody)
    for off, X in ((192, Q), (1240, U)):
        for i, v in enumerate(X): struct.pack_into('<I3f', d, off + 16 * i, 0, *v)
    print(f'  collision hull: x +/-{half[0]:.3f}, y {lo[1]:.3f}..{hi[1]:.3f}, z {lo[2]:.3f}..{hi[2]:.3f}, '
          f'{ConvexHull(Q).volume:.2f} m3 ({len(ConvexHull(Q).vertices)} hull points)')
    return bytes(d)
