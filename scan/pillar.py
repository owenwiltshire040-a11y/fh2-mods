"""Owen's 207 is a 5-door; the template glass is a 3-door's. Add the 5-door B-pillar: a body-coloured strip lying
on the side glass, at the position and lean of the pillar found in the scan."""
import numpy as np
from scipy.spatial import cKDTree

def pillars(glass_P, scan_npz, half_width=0.055, out=0.008):
    S = np.load(scan_npz); P, F = S['P'], S['F']; C = P[F].mean(1)
    d, _ = cKDTree(glass_P).query(C)
    Ps, Is, base = [], [], 0
    for side in (-1, 1):
        G = glass_P[(np.sign(glass_P[:, 0]) == side) & (np.abs(glass_P[:, 0]) > 0.55)]
        sel = (np.sign(C[:, 0]) == side) & (np.abs(C[:, 0]) > 0.55) & (d < 0.03) & (C[:, 2] > 0.35) & (C[:, 2] < 0.66) & (C[:, 1] > 0.85) & (C[:, 1] < 1.2)
        pc = C[sel]
        A = np.c_[pc[:, 1], np.ones(len(pc))]                     # pillar centre z as a line in y (its lean)
        k, b = np.linalg.lstsq(A, pc[:, 2], rcond=None)[0]
        gt = cKDTree(G[:, 1:])                                    # glass point by (y, z)
        rows = []
        slab = G[np.abs(G[:, 2] - (k * 1.0 + b)) < 0.08]
        y0, y1 = slab[:, 1].min() - 0.01, slab[:, 1].max() + 0.01
        for y in np.linspace(y0, y1, 14):
            zc = k * y + b
            row = []
            for z in (zc - half_width, zc + half_width):
                _, j = gt.query([y, z], k=6)
                x = G[j, 0].mean()
                row.append([x + side * out, y, z])
            rows.append(row)
        R = np.array(rows)                                        # (n, 2, 3)
        n = len(R); V = R.reshape(-1, 3)
        I = []
        for r in range(n - 1):
            a, b_, c, e = 2 * r, 2 * r + 1, 2 * r + 2, 2 * r + 3
            I += [[a, c, b_], [b_, c, e]]
        I = np.array(I)
        # face the outside (+side in x): geometric normal cross(b-a, c-a) should point to side
        g = np.cross(V[I[:, 1]] - V[I[:, 0]], V[I[:, 2]] - V[I[:, 0]])
        if np.mean(g[:, 0] * side) < 0: I = I[:, [0, 2, 1]]
        print(f'B-pillar side {side:+d}: centre z = {k:.3f}*y + {b:.3f}, glass from y {y0:.2f} to {y1:.2f}')
        Ps.append(V); Is.append(I + base); base += len(V)
    V = np.concatenate(Ps); I = np.concatenate(Is)
    N = np.zeros_like(V); g = np.cross(V[I[:, 1]] - V[I[:, 0]], V[I[:, 2]] - V[I[:, 0]])
    for j in range(3): np.add.at(N, I[:, j], g)
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    UV = np.stack([V[:, 2] * 0.25 + 0.5, V[:, 1] * 0.25 + 0.5], 1)
    n = len(V)
    return dict(P=np.r_[V, V], N=np.r_[N, -N], UV=np.r_[UV, UV]), np.r_[I, I[:, [0, 2, 1]] + n].reshape(-1)
