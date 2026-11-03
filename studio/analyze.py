"""Model analysis for FH2 Car Studio: materials, orientation, wheel guess, textures.

Frames: the "model frame" is the glb's world space. The "oriented frame" is the model rotated so +y is up, +z is the
car's nose and -x is the car's left (FH2's axes), still in model units. FH2 space = oriented * scale + offset
(fh2re/glbgeo.py), with the hubs at y 0.156 (the Charger's spindle height, so the stock ride height fits).
"""
import re
import numpy as np

HUB_Y = 0.156          # FH2 y of the wheel centres (the Charger donor's spindles; ride height 0.1625 matches it)
AXLE_MID = 0.0867      # FH2 z of the wheelbase centre (= -BottomCenterWheelbasePosZ of the donor)
AXES = {'+x': (0, 1.0), '-x': (0, -1.0), '+y': (1, 1.0), '-y': (1, -1.0), '+z': (2, 1.0), '-z': (2, -1.0)}


def vec(a):
    i, s = AXES[a]; v = np.zeros(3); v[i] = s; return v


def frame(front='+z', up='+y'):
    """(3x3 matrix M with oriented = M @ model, glbgeo --frame string)"""
    f, u = vec(front), vec(up)
    if abs(f @ u) > 0.5: raise ValueError('front and up must be different axes')
    right = np.cross(f, u)                     # +z nose, +y up -> cross = car's +x (its right; FH2 -x is the left)
    M = np.array([right, u, f])
    toks = []
    for row in M:
        i = int(np.argmax(np.abs(row))); toks.append(('-' if row[i] < 0 else '') + 'xyz'[i])
    return M, ','.join(toks)


def load_scene(path):
    import trimesh
    return trimesh.load(path, force='scene')


def pieces(sc):
    """[(node, material name, world vertices (n,3), faces, mesh)]"""
    import trimesh
    out = []
    for node in sc.graph.nodes_geometry:
        T, geom = sc.graph[node]; m = sc.geometry[geom]
        if not hasattr(m, 'faces') or len(m.faces) == 0: continue
        mat = getattr(getattr(m.visual, 'material', None), 'name', None) or 'unnamed'
        out.append((node, mat, trimesh.transform_points(m.vertices, T), m.faces, m))
    return out


def mat_colour(m):
    mt = getattr(m.visual, 'material', None)
    c = getattr(mt, 'baseColorFactor', None)
    if c is None: c = getattr(mt, 'main_color', None)
    if c is None: return '#999999'
    c = np.asarray(c, float)
    if c.max() > 1.0: c = c / 255.0
    return '#%02x%02x%02x' % tuple(int(round(min(max(x, 0), 1) * 255)) for x in c[:3])


def mat_texture(m):
    mt = getattr(m.visual, 'material', None)
    for a in ('baseColorTexture', 'image'):
        t = getattr(mt, a, None)
        if t is not None: return t
    return None


KEYS = [  # (regex on the lower-cased material name, role)
    (r'tyre|tire|pneu|reifen|rubber_tire', 'tyre'),
    (r'glass|window|windscreen|windshield|wind_shield|glas|gls|vidrio|cristal', 'glass'),
    (r'black|schwarz|negro|dark|carbon|chassis|under', 'black'),
    (r'chrome|chrom|silver|polished|\balu', 'chrome'),
    (r'plastic|trim|rubber|grill|grille|matte|interior|seat|dash', 'black'),
    (r'paint|body|carpaint|car_paint|exterior|lack|shell', 'paint'),
]
LAMP_KEYS = [
    ('head', r'head|hl_|_hl|headlight|front_light|frontlight|projector|high_beam|highbeam|lowbeam|low_beam'),
    ('drl', r'drl|daytime|running'),
    ('turn_f', r'indicator|turn|blinker|signal|orange|amber'),
    ('tail', r'tail|brake|stop|rear_light|rearlight|backlight|red_l|red_glass|rear_lamp'),
    ('reverse', r'reverse|backup|rev_'),
    ('turn_r', r'indicator|turn|blinker|signal|orange|amber'),
    ('chmsl', r'chmsl|third_brake|3rd|high_brake|brake_top'),
]


def guess_role(name, textured, colour):
    n = name.lower()
    if textured and not re.search(r'tyre|tire', n): return 'texture'
    rgb = np.array([int(colour[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0
    dark, grey = rgb.max() < 0.08, rgb.max() - rgb.min() < 0.12
    lampish = re.search(r'light|lamp|led|lens|indicator|signal|beam|blinker', n)
    if lampish and not re.search(r'glass|lens|gls', n): return 'black' if dark else 'colour'
    if (lampish or re.search(r'red|orange|amber', n)) and not grey: return 'colour'          # tinted lamp glass keeps its tint
    for rx, role in KEYS:
        if re.search(rx, n): return role
    if re.search(r'metal', n): return 'black' if dark else 'chrome' if grey else 'colour'
    return 'black' if dark else 'colour'


def analyze(path):
    sc = load_scene(path); P = pieces(sc)
    allV = np.concatenate([p[2] for p in P]); lo, hi = allV.min(0), allV.max(0)
    mats = {}
    for node, mat, V, F, m in P:
        d = mats.setdefault(mat, dict(name=mat, tris=0, colour=mat_colour(m), textured=mat_texture(m) is not None, nodes=[]))
        d['tris'] += int(len(F)); d['nodes'].append(node)
        d['centre'] = V.mean(0).tolist()
    for d in mats.values():
        d['role'] = guess_role(d['name'], d['textured'], d['colour']); d['nodes'] = sorted(set(d['nodes']))[:6]
    # the biggest untextured, unnamed-role material is most likely the paint
    if not any(d['role'] == 'paint' for d in mats.values()):
        cand = [d for d in mats.values() if d['role'] in ('colour',)]
        if cand: max(cand, key=lambda d: d['tris'])['role'] = 'paint'
    # orientation: glTF is y-up; the long horizontal axis is the length; the nose is where the head lamps are
    ext = hi - lo; long_ax = 'x' if ext[0] > ext[2] else 'z'; i = 'xyz'.index(long_ax)
    c = (lo + hi) / 2; sign = '+'
    heads = [d['centre'][i] for d in mats.values() if re.search(LAMP_KEYS[0][1], d['name'].lower())]
    tails = [d['centre'][i] for d in mats.values() if re.search(LAMP_KEYS[3][1], d['name'].lower())]
    if heads and tails: sign = '+' if np.mean(heads) > np.mean(tails) else '-'
    elif heads: sign = '+' if np.mean(heads) > c[i] else '-'
    elif tails: sign = '-' if np.mean(tails) > c[i] else '+'
    lamps = {k: sorted(n for n, d in mats.items() if re.search(rx, n.lower())) for k, rx in LAMP_KEYS}
    return dict(materials=sorted(mats.values(), key=lambda d: -d['tris']), bbox=[lo.tolist(), hi.tolist()],
                front=sign + long_ax, up='+y', lamps=lamps, tris=int(sum(d['tris'] for d in mats.values())))


def oriented_points(path, front, up, select=None):
    M, _ = frame(front, up); sc = load_scene(path); out = []
    for node, mat, V, F, m in pieces(sc):
        if select is None or select(node, mat): out.append(V @ M.T)
    return np.concatenate(out) if out else np.zeros((0, 3))


def guess_wheels(path, front, up):
    """wheel centres and tyre radius in the oriented frame: from tyre/wheel-named geometry when there is some,
    otherwise from typical car proportions"""
    A = oriented_points(path, front, up); lo, hi = A.min(0), A.max(0)
    rx = re.compile(r'tyre|tire|wheel|rim|hub|pneu|rad\b|felge|reifen|disc|brake_disc')
    M, _ = frame(front, up); Ws = []
    for node, mat, V, F, m in pieces(load_scene(path)):
        O = V @ M.T; ol, oh = O.min(0), O.max(0); e = oh - ol
        roundish = abs(e[1] - e[2]) < 0.15 * max(e[1], e[2]) and ol[1] < lo[1] + 0.08 * (hi[1] - lo[1]) and e[1] < 0.5 * (hi[1] - lo[1]) and e[2] < 0.6 * (hi[2] - lo[2])
        pair = e[1] < 0.5 * (hi[1] - lo[1]) and ol[1] < lo[1] + 0.08 * (hi[1] - lo[1]) and abs(e[1] - e[2]) < 0.15 * e[1]
        if rx.search(mat.lower()) or rx.search(str(node).lower()) or roundish or pair: Ws.append(O)
    W = np.concatenate(Ws) if Ws else np.zeros((0, 3))
    mid_z = (lo[2] + hi[2]) / 2
    if len(W) > 50:
        quads = []
        for sz in (1, -1):
            for sx in (1, -1):
                Q = W[(np.sign(W[:, 2] - mid_z) == sz) & (np.sign(W[:, 0]) == sx) & (W[:, 1] < lo[1] + (hi[1] - lo[1]) * 0.6)]
                if len(Q) > 10:
                    ql, qh = Q.min(0), Q.max(0); quads.append((sz, (ql + qh) / 2, (qh[1] - ql[1]) / 2))
        if len(quads) >= 2 and {q[0] for q in quads} == {1, -1}:
            zf = float(np.mean([q[1][2] for q in quads if q[0] == 1])); zr = float(np.mean([q[1][2] for q in quads if q[0] == -1]))
            yc = float(np.mean([q[1][1] for q in quads])); r = float(np.mean([q[2] for q in quads]))
            xh = float(np.mean([abs(q[1][0]) for q in quads]))
            if r > 0.02 * (hi[2] - lo[2]): return dict(zf=zf, zr=zr, yc=yc, xh=xh, r=r, found=True)
    L = hi[2] - lo[2]; Wd = hi[0] - lo[0]; r = 0.077 * L
    return dict(zf=float(mid_z + 0.30 * L), zr=float(mid_z - 0.30 * L), yc=float(lo[1] + r), xh=float(0.40 * Wd), r=float(r), found=False)
