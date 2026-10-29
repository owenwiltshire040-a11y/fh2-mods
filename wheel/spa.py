"""Peugeot 207 'Spa' 16" 6J alloy (part 9686100080), measured from Owen's straight-on photo (polar unwrap).
All radii are fractions of R (the rim's face radius in the wheel model, = the 16" bead seat in game).
Depth x: 0 at the face, positive into the wheel (outward is -x)."""
import numpy as np

R = 0.1397
N = 7
WIN_TIP = 0.37                         # windows: pointed inner tip
WIN_HALF_ANGLE = np.radians(13.75)     # full-width windows are ~27.5 deg
WIN_OUT, WIN_FILLET = 0.955, 0.045     # flat outer end (under the lip's inner edge), big rounded corners
FACE_IN, FACE_OUT = 0.125, 0.96        # face annulus (centre badge inside, donor lip outside)
LUG_R, LUG_POCKET = 0.265, 0.075       # 4 x 108 mm on a 16" rim; pocket radius around each nut
GROOVE = 0.003                         # recessed groove down each spoke (fraction of R in depth units below)
X_BACK = 0.045

def in_window(r, th):
    """True where (r, th) is inside one of the 7 windows (windows centred between spokes; spoke 0 at th = 0).
    Shape measured from the photo: a pointed arch from a tip at 0.37 R, reaching full width (~27.5 deg) by 0.62 R,
    straight radial sides, and a flat outer end at 0.955 R with large rounded corners (the spokes' flared feet)."""
    k = np.round((th - np.pi / N) / (2 * np.pi / N))
    c = np.pi / N + k * 2 * np.pi / N
    v = r * np.sin(th - c); u = r * np.cos(th - c)
    full = u * np.tan(WIN_HALF_ANGLE)
    half = full * np.sqrt(np.clip((u - WIN_TIP) / (0.62 - WIN_TIP), 0, 1))
    inside = (u > WIN_TIP) & (np.abs(v) < half) & (u < WIN_OUT)
    cu = WIN_OUT - WIN_FILLET; cv = full - WIN_FILLET
    corner = (u > cu) & (np.abs(v) > cv)
    inside &= ~corner | ((u - cu) ** 2 + (np.abs(v) - cv) ** 2 < WIN_FILLET ** 2)
    return inside

def in_pocket(r, th):
    y, z = r * np.sin(th), r * np.cos(th)
    out = np.zeros_like(r, bool)
    for a in (0, np.pi / 2, np.pi, 3 * np.pi / 2):
        out |= (y - LUG_R * np.sin(a)) ** 2 + (z - LUG_R * np.cos(a)) ** 2 < LUG_POCKET ** 2
    return out

def depth(r, th):
    """face depth: dished towards the rim, groove down each spoke's centre line"""
    x = 0.004 + 0.008 * np.clip((r - 0.35) / 0.55, 0, 1)
    phi = (th + np.pi / N) % (2 * np.pi / N) - np.pi / N          # angle from nearest spoke centre
    across = r * np.sin(phi)
    x = x + GROOVE * np.exp(-(across / 0.028) ** 2) * (r > 0.40) * (r < 0.88)
    return x

def build(nr=64, nt=7 * 40):
    rs = np.linspace(FACE_IN, FACE_OUT, nr + 1); ts = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    Rg, Tg = np.meshgrid(rs, ts, indexing='ij')
    # a cell is solid if its centre is outside every window and every nut pocket
    rc = (Rg[:-1] + Rg[1:]) / 2; tc = Tg[:-1] + np.pi / nt
    solid = ~(in_window(rc, tc) | in_pocket(rc, tc))
    X = depth(Rg, Tg)
    def P(i, j, x=None):
        r, t = rs[i], ts[j % nt]
        return [X[i, j % nt] if x is None else x, r * R * np.sin(t), r * R * np.cos(t)]
    V, F = [], []
    def quad(a, b, c, d):
        n = len(V); V.extend([a, b, c, d]); F.extend([[n, n + 1, n + 2], [n, n + 2, n + 3]])
    for i in range(nr):
        for j in range(nt):
            if not solid[i, j]: continue
            quad(P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1))
            # walls where a solid cell meets a hole or the inner/outer edge, running back into the wheel
            if j + 1 < nt + 1 and not solid[i, (j + 1) % nt]:
                quad(P(i, j + 1), P(i + 1, j + 1), P(i + 1, j + 1, X_BACK), P(i, j + 1, X_BACK))
            if not solid[i, (j - 1) % nt]:
                quad(P(i, j), P(i, j, X_BACK), P(i + 1, j, X_BACK), P(i + 1, j))
            if i + 1 < nr and not solid[i + 1, j]:
                quad(P(i + 1, j), P(i + 1, j, X_BACK), P(i + 1, j + 1, X_BACK), P(i + 1, j + 1))
            if i > 0 and not solid[i - 1, j]:
                quad(P(i, j), P(i, j + 1), P(i, j + 1, X_BACK), P(i, j, X_BACK))
            if i == 0:
                quad(P(0, j, X[0, j] - 0.004), P(0, j), P(0, j + 1), P(0, j + 1, X[0, (j + 1) % nt] - 0.004))
    for a in (0, np.pi / 2, np.pi, 3 * np.pi / 2):          # floors of the four nut pockets
        cy_, cz_ = LUG_R * R * np.sin(a), LUG_R * R * np.cos(a)
        for k in range(24):
            t0, t1 = 2 * np.pi * k / 24, 2 * np.pi * (k + 1) / 24
            n = len(V); rr = LUG_POCKET * R
            V.extend([[0.020, cy_, cz_], [0.020, cy_ + rr * np.sin(t0), cz_ + rr * np.cos(t0)], [0.020, cy_ + rr * np.sin(t1), cz_ + rr * np.cos(t1)]])
            F.append([n, n + 1, n + 2])
    V = np.array(V, float); F = np.array(F)
    # wind faces outward (-x for the face, away from the hole for walls): use the cell-normal heuristic
    g = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    face = np.abs(g[:, 0]) >= np.linalg.norm(g[:, 1:], axis=1)
    flip = face & (g[:, 0] > 0)
    F[flip] = F[flip][:, [0, 2, 1]]
    return V, F


def window_half_angle(r, iters=40):
    """angle from a window's centre line to its edge at radius r (0 where there is no window)"""
    c = np.pi / N
    lo, hi = 0.0, np.pi / N
    if not in_window(np.array(r), np.array(c)): return 0.0
    for _ in range(iters):
        mid = (lo + hi) / 2
        if in_window(np.array(r), np.array(c + mid)): lo = mid
        else: hi = mid
    return lo


def build_conforming(n_rows=48, seg=10, hub_nr=28, hub_nt=7 * 56):
    """Face mesh whose spoke edges lie exactly on the measured window outline."""
    V, F = [], []
    def add(quadpts):
        n = len(V); V.extend(quadpts); F.extend([[n, n + 1, n + 2], [n, n + 2, n + 3]])
    def P(r, t, x=None):
        return [depth(np.array(r), np.array(t)) if x is None else x, r * R * np.sin(t), r * R * np.cos(t)]
    # rows: dense near the tip (where the arch narrows) and exactly at the window's ends
    r0 = 0.34
    rows = np.unique(np.r_[np.linspace(r0, WIN_TIP, 3), WIN_TIP + (0.62 - WIN_TIP) * np.linspace(0, 1, 16) ** 2,
                           np.linspace(0.62, WIN_OUT - WIN_FILLET, 14), WIN_OUT - WIN_FILLET * np.cos(np.linspace(0, np.pi / 2, 10)),
                           np.linspace(WIN_OUT, FACE_OUT, 3)])
    rows = np.clip(rows, r0, FACE_OUT)
    a = [window_half_angle(r - 1e-6 if abs(r - WIN_OUT) < 1e-9 else r) for r in rows]
    step = 2 * np.pi / N
    for s in range(N):
        for i in range(len(rows) - 1):
            ri, rj = rows[i], rows[i + 1]
            ai, aj = a[i], a[i + 1]
            # spoke s spans from window (s-1)'s right edge to window s's left edge
            ti0, ti1 = (s - 1) * step + np.pi / N + ai, s * step + np.pi / N - ai
            tj0, tj1 = (s - 1) * step + np.pi / N + aj, s * step + np.pi / N - aj
            for k in range(seg):
                f0, f1 = k / seg, (k + 1) / seg
                add([P(ri, ti0 + (ti1 - ti0) * f0), P(rj, tj0 + (tj1 - tj0) * f0), P(rj, tj0 + (tj1 - tj0) * f1), P(ri, ti0 + (ti1 - ti0) * f1)])
            if ai > 0 or aj > 0:      # side walls into the windows
                add([P(ri, ti0), P(ri, ti0, X_BACK), P(rj, tj0, X_BACK), P(rj, tj0)])
                add([P(ri, ti1), P(rj, tj1), P(rj, tj1, X_BACK), P(ri, ti1, X_BACK)])
        # wall across the window's flat outer end
        c = s * step + np.pi / N; aw = window_half_angle(WIN_OUT - 1e-6)
        for k in range(seg):
            t0, t1 = c - aw + 2 * aw * k / seg, c - aw + 2 * aw * (k + 1) / seg
            add([P(WIN_OUT, t0), P(WIN_OUT, t1), P(WIN_OUT, t1, X_BACK), P(WIN_OUT, t0, X_BACK)])
    # hub (badge edge to r0) with the four nut pockets, on a fine polar grid
    rs = np.linspace(FACE_IN, r0, hub_nr + 1); ts = np.linspace(0, 2 * np.pi, hub_nt, endpoint=False)
    Rg, Tg = np.meshgrid(rs, ts, indexing='ij')
    rc = (Rg[:-1] + Rg[1:]) / 2; tc = Tg[:-1] + np.pi / hub_nt
    solid = ~in_pocket(rc, tc)
    for i in range(hub_nr):
        for j in range(hub_nt):
            t0, t1 = ts[j], ts[(j + 1) % hub_nt] + (2 * np.pi if j + 1 == hub_nt else 0)
            if not solid[i, j]: continue
            add([P(rs[i], t0), P(rs[i + 1], t0), P(rs[i + 1], t1), P(rs[i], t1)])
            if not solid[i, (j + 1) % hub_nt]: add([P(rs[i], t1), P(rs[i + 1], t1), P(rs[i + 1], t1, 0.02), P(rs[i], t1, 0.02)])
            if not solid[i, (j - 1) % hub_nt]: add([P(rs[i], t0), P(rs[i], t0, 0.02), P(rs[i + 1], t0, 0.02), P(rs[i + 1], t0)])
            if i + 1 < hub_nr and not solid[i + 1, j]: add([P(rs[i + 1], t0), P(rs[i + 1], t0, 0.02), P(rs[i + 1], t1, 0.02), P(rs[i + 1], t1)])
            if i > 0 and not solid[i - 1, j]: add([P(rs[i], t0), P(rs[i], t1), P(rs[i], t1, 0.02), P(rs[i], t0, 0.02)])
            if i == 0: add([P(rs[0], t0, depth(np.array(rs[0]), np.array(t0)) - 0.004), P(rs[0], t0), P(rs[0], t1), P(rs[0], t1, depth(np.array(rs[0]), np.array(t1)) - 0.004)])
    for ang in (0, np.pi / 2, np.pi, 3 * np.pi / 2):          # pocket floors
        cy_, cz_ = LUG_R * R * np.sin(ang), LUG_R * R * np.cos(ang)
        for k in range(24):
            t0, t1 = 2 * np.pi * k / 24, 2 * np.pi * (k + 1) / 24
            n = len(V); rr = LUG_POCKET * R
            V.extend([[0.020, cy_, cz_], [0.020, cy_ + rr * np.sin(t0), cz_ + rr * np.cos(t0)], [0.020, cy_ + rr * np.sin(t1), cz_ + rr * np.cos(t1)]])
            F.append([n, n + 1, n + 2])
    V = np.array(V, float); F = np.array(F)
    g = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    face = np.abs(g[:, 0]) >= np.linalg.norm(g[:, 1:], axis=1)
    flip = face & (g[:, 0] > 0)
    F[flip] = F[flip][:, [0, 2, 1]]
    return V, F
