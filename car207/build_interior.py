"""207 interior (community BeamNG 207 by sheik, personal use) into the donor Fiesta interior parts.

  * static trim (dash, door cards, seats, rear bench, headliner/pillars, carpet) replaces the Fiesta's
  * Fiesta-only pieces (dash structure, centre console + shifter, radio stack, vents, speakers, front door cards,
    distant-LOD interior) are hidden (their triangles collapsed; buffers untouched)
  * working parts are kept and moved into the 207's places: steering wheel (bone), steering column, gauge
    cluster + needles (bones), rear-view mirror
  * skeleton bones (car skeleton + every part's copy) and Locators.xml (cockpit camera etc.) move to match
usage: build_interior.py in.zip out.zip
"""
import sys, zipfile, struct, pickle, re, numpy as np
sys.path.insert(0, '../fh2re')
from geometry import Part
from body_swap import set_group, blank_group, group_materials, material_names
from gltf_bridge import decode_group

SRC, OUT = sys.argv[1], sys.argv[2]
GROUND = 0.124 - 0.3105 - 0.08
MID = (-1.290 + 1.252) / 2 - 0.0085
def to_fh2(V): return np.stack([-V[:, 0], V[:, 2] + GROUND, -V[:, 1] + MID], 1)

# ---- targets measured from the 207 model (see conversation notes)
# the 207 wheel's own placement in the BeamNG model (node p207_steering_wheel: scale 1.1, tilted on the column)
SW_M = np.array([1.100747, 0, 0, 0.3668526, 0, 0.4300958, 1.013242, -0.5207138, 0, -1.013242, 0.4300958, 0.9084429, 0, 0, 0, 1]).reshape(4, 4)
WHEEL_OLD, WHEEL_NEW = np.array([-0.342, 0.775, 0.270]), np.array([-0.367, 0.664, 0.429])   # the 207 rim's centre
D_WHEEL = WHEEL_NEW - WHEEL_OLD
GAUGE_FACE_207 = np.array([-0.366, 0.678, 0.698])
EYE_OLD, EYE_NEW = np.array([-0.353, 0.992, -0.267]), to_fh2(np.array([[0.368, 0.2, 1.205]]))[0]
SHIFT_NEW, HBRAKE_NEW = to_fh2(np.array([[0.0, -0.31, 0.60]]))[0], to_fh2(np.array([[0.0, -0.18, 0.59]]))[0]

# ---- 207 interior geometry, sorted into buckets
it = pickle.load(open('../sheik/interior.pkl', 'rb'))
atlas = np.load('../sheik/int_atlas.npy').astype(np.float32) / 255
AH, AW = atlas.shape[:2]
ext_atlas = np.load('../sheik/atlas.npy').astype(np.float32) / 255

def lum_of(UV, n, img):
    c = UV.reshape(n, 3, 2).mean(1); h, w = img.shape[:2]
    px = img[np.clip(((1 - c[:, 1] % 1) * h).astype(int), 0, h - 1), np.clip((c[:, 0] % 1 * w).astype(int), 0, w - 1)]
    return px @ [0.299, 0.587, 0.114]

# ---- the 207's instrument binnacle: three chrome rings (rev counter, fuel/temp, speedo) on a plane tilted back
RING_N = np.array([0.0, -0.522, 0.853]); RING_N /= np.linalg.norm(RING_N)        # into the dash
RING_E1 = np.array([1.0, 0, 0]); RING_E2 = np.cross(RING_N, RING_E1)
def _rings():
    from sklearn.cluster import KMeans
    ch = np.concatenate([to_fh2(q['V'].astype(np.float64)) for q in it['tableau_de_bord_very_high.242'] if q['mat'] == 'p207_chrome'])
    ch = ch[(ch[:, 0] < 0) & (ch[:, 0] > -0.6)]
    uv = np.c_[ch @ RING_E1, ch @ RING_E2]; lab = KMeans(3, n_init=10, random_state=0).fit(uv).labels_
    out = []
    for j in range(3):
        Q = uv[lab == j]; A = np.c_[2 * Q, np.ones(len(Q))]
        cu, cv, c = np.linalg.lstsq(A, (Q ** 2).sum(1), rcond=None)[0]; out.append((cu, cv, np.sqrt(c + cu ** 2 + cv ** 2)))
    return sorted(out)                                                            # left to right: tacho, centre, speedo
RINGS = _rings()
print('  207 dial rings (u, v, r):', np.round(RINGS, 4).tolist())

buckets = {}
def put(key, V, N, UV, sel=None):
    if sel is not None:
        idx = np.repeat(sel, 3); V, N, UV = V[idx], (None if N is None else N[idx]), UV[idx]
    if len(V): buckets.setdefault(key, []).append((V, N, UV))

for part, prims in it.items():
    if part.startswith('tripo'): continue                        # 90k-triangle AI panel; the low-poly one is used
    if part == 'Interieur_5p_very_high.018': continue            # mirror: the Fiesta's working one is moved instead
    for p in prims:
        m = p['mat']; V = to_fh2(p['V'].astype(np.float64)); n = len(V) // 3
        N = to_fh2(p['N'].astype(np.float64)) - np.array([0, GROUND, MID]) if p['N'] is not None else None
        UV = p['UV'] if p['UV'] is not None else np.zeros((len(V), 2))
        seat = part in ('lib:dash.026', 'lib:dash.029')
        door = part.startswith('door_')
        shell = part.startswith('bodyshell') or part == 'boot_very_high'
        rear = part.startswith('Banquette')
        if seat:
            put({'p207_seatmain': 'seat_main', 'p207_seatinner': 'seat_inner'}.get(m, 'seat_plastic'), V, N, UV); continue
        if rear:
            l = lum_of(UV, n, atlas); put('rear_seat', V, N, UV, l < 0.75); continue
        if m == 'p207_headliner' or part.startswith('bodyshell_very_high.16') and part != 'bodyshell_very_high.163':
            put('visors' if part != 'bodyshell_very_high.163' else 'headliner', V, N, UV); continue
        if m == 'p207_carpet': put('carpet', V, N, UV); continue
        if m == 'p207_doorcloth': put('door_fabric', V, N, UV); continue
        if m in ('p207_hardplastic', 'p207_trim'): put('door_textured' if door else 'dash_textured', V, N, UV); continue
        if m in ('p207_int1', 'p207_plastic', 'interior_lod0.004'): put('door_dark' if door else 'dash_dark', V, N, UV); continue
        if m == 'p207_chrome': put('door_chrome' if door else 'dash_chrome', V, N, UV); continue
        if m in ('p207_screens', 'p207_gaugeslowbeam', 'p207_platehold', 'undercarriage'): continue
        if part == 'tableau_de_bord_very_high.242' and m.startswith('interior_lod0'):
            c = V.reshape(n, 3, 3).mean(1); front = np.zeros(n, bool)   # printed dial bits standing proud of the dial
            for (u, v, r) in RINGS:                                    # plane would cover the working faces
                front |= (np.hypot(c @ RING_E1 - u, c @ RING_E2 - v) < r) & (c @ RING_N < 0.218)
            put('dash_dark', V, N, UV, (lum_of(UV, n, atlas) < 0.5) & ~front); continue
        if m.startswith('interior_lod0') or m == 'nodamage_lod0':
            l = lum_of(UV, n, ext_atlas if m == 'nodamage_lod0' else atlas)
            dark = l < 0.5
            if shell:
                put('pillars' if part != 'boot_very_high' else 'rear_dark', V, N, UV, dark)
                put('headliner', V, N, UV, ~dark)
            elif door: put('door_dark', V, N, UV, dark)
            else:      put('dash_dark', V, N, UV, dark)               # white dial faces / symbols dropped
            continue
        put('dash_dark', V, N, UV)

def geo(keys):
    """double-sided geometry for a list of buckets; winding follows the authored normals"""
    Vs, Ns, UVs = [], [], []
    for k in keys:
        for V, N, UV in buckets.get(k, []):
            if N is None:
                T = V.reshape(-1, 3, 3); g = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N = np.repeat(g, 3, 0)
            Vs.append(V); Ns.append(N); UVs.append(UV)
    if not Vs: return None
    V = np.concatenate(Vs); N = np.concatenate(Ns); UV = np.concatenate(UVs)
    N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    T = np.arange(len(V)).reshape(-1, 3)
    g = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    flip = np.einsum('ij,ij->i', g, N[T].sum(1)) < 0
    T[flip] = T[flip][:, [0, 2, 1]]
    n = len(V)
    return dict(P=np.r_[V, V], N=np.r_[N, -N], UV=np.r_[UV, UV]), np.r_[T, T[:, [0, 2, 1]] + n].reshape(-1)
for k, v in sorted(buckets.items()): print(f'  bucket {k:14s} {sum(len(x[0]) // 3 for x in v):6d} tris')

# ---- donor files
src = zipfile.ZipFile(SRC)
names = {n.lower(): n for n in src.namelist()}
def P_(path): return Part(src.read(names[path.lower()]))
INT = 'scene/interior/'

def bright_uv(p):
    best, uv = -9, None
    for gid in p.group_order:
        d, _ = decode_group(p, gid)
        if 'NORMAL0' not in d or not any(f'TEXCOORD{j}' in d for j in (1, 2, 3, 4)): continue
        sc = d['NORMAL0'][:, 1]                                   # an upward-facing, unshadowed texel
        k = int(np.argmax(sc))
        if sc[k] > best: best, uv = sc[k], {j: d[f'TEXCOORD{j}'][k] for j in (1, 2, 3, 4) if f'TEXCOORD{j}' in d}
    return uv

def replace(path, plan, keep=None):
    """plan: {gid: {material: [bucket keys]}}; keep: {gid: [materials kept from the donor]}"""
    p = P_(path); uvc = bright_uv(p); nm = material_names(p); keep = keep or {}
    for gid in p.group_order:
        mats = plan.get(gid)
        if not mats and gid not in keep: blank_group(p, gid); continue
        if not mats: continue
        parts, by_mat, base = [], {}, 0
        for mat, keys in mats.items():
            gg = geo(keys)
            if gg is None: continue
            g, idx = gg; parts.append(g); by_mat[mat] = idx + base; base += len(g['P'])
        kept_uv = {}
        if gid in keep:                                           # donor triangles kept as they are
            d, _ = decode_group(p, gid)
            for r in p.render:
                if r['group'] != gid or nm[id(r['blob'])] not in keep[gid] or not struct.unpack_from('<H', r['blob']['data'], 4)[0] & 1: continue
                ix = np.array(r['indices']); u = np.unique(ix); rm = {o: i + base for i, o in enumerate(u)}
                parts.append(dict(P=d['POSITION'][u], N=d['NORMAL0'][u][:, :3], UV=d['TEXCOORD0'][u] if 'TEXCOORD0' in d else np.zeros((len(u), 2))))
                by_mat[nm[id(r['blob'])]] = np.array([rm[i] for i in ix]); base += len(u)
        if not parts: blank_group(p, gid); continue
        G = {k: np.concatenate([q[k] for q in parts]) for k in ('P', 'N', 'UV')}
        G['UVconst'] = uvc
        set_group(p, gid, G, by_mat)
    out = p.build(); Part(out); return out

def edit(path, hide=lambda mat, bone: False, move=None):
    """collapse hidden render meshes; translate vertices of meshes selected by move(mat, bone) -> delta"""
    p = P_(path); nm = material_names(p)
    moved = {}
    for r in p.render:
        mat = nm[id(r['blob'])]; bone = struct.unpack_from('<h', r['blob']['data'], 2)[0]
        if hide(mat, bone):
            i = r['indices'][0] if r['indices'] else 0; r['indices'] = [i, i, i]; continue
        dlt = move(mat, bone) if move else None
        if dlt is not None:
            for i in r['indices']: moved[(r['group'], i)] = dlt
    for (gid, i), dlt in moved.items():
        g = p.groups[gid]; x, y, z = g['positions'][i]; g['positions'][i] = (x + dlt[0], y + dlt[1], z + dlt[2])
    out = p.build(); Part(out); return out

replaced = {}
R = lambda f: INT + f
replaced[R('dash/dashpad_a.modelbin')] = replace(R('dash/dashpad_a.modelbin'), {
    0: {'blkplastic_lgl': ['dash_dark', 'dash_textured']},        # plain black: the textured plastic came out beige
    1: {'chrome_polishedsatin': ['dash_chrome']}})
replaced[R('doors/doorcardlr_a.modelbin')] = replace(R('doors/doorcardlr_a.modelbin'), {
    0: {'blkplastic_lgl': ['door_dark', 'door_textured'], 'fabric_008': ['door_fabric']},
    1: {'chrome_satin': ['door_chrome']}})
replaced[R('pillar/overheadconsole_a.modelbin')] = replace(R('pillar/overheadconsole_a.modelbin'), {
    0: {'fabric_008|pillarTrim_a': ['headliner'], 'blkplastic_lgl': ['pillars'], 'blkplastic_mgl|visors_a': ['visors']}})
replaced[R('seats/parcelshelf_a.modelbin')] = replace(R('seats/parcelshelf_a.modelbin'), {
    0: {'blkleather_bump_mgl_003|rearSeats_a': ['rear_seat'], 'blkplastic_lgl|rearSeats_a': ['rear_dark']}})
replaced[R('seats/seatbeltl_a.modelbin')] = replace(R('seats/seatbeltl_a.modelbin'), {
    0: {'blkleather_bump_mgl_003|seatL_a': ['seat_main'], 'blkplastic_lgl': ['seat_plastic']},
    1: {'blkleather_lgl_002|seatL_a': ['seat_inner']}})
replaced[R('floor/floor_a.modelbin')] = replace(R('floor/floor_a.modelbin'), {
    0: {'fabric_008': ['carpet']}}, keep={0: ['aluminum_rgh_dirty|pedals_a'], 1: ['rivetpainted_002|pedals_a', 'frame']})

# ---- seat upholstery: the 207 SE's grey cloth. The Fiesta's seat-insert material is the game's embossed plastic
# with a woven-fabric normal map and a near-black colour; material instances can override the colour, so the
# bolsters (black leather in the Fiesta) become a copy of that fabric instance, and both get the 207's greys.
COL_HASH = bytes.fromhex('be3916f5')          # the colour parameter of plastic_embossed (vec4, linear RGB + 0)
def fabric_template():
    from modelbin import Bundle
    b = Bundle.read(src.read(names[R('seats/seatbeltl_a.modelbin')]))
    return next(bytes(bl['data']) for bl in b.blobs if bl['tag'] == 'MatI' and b.meta(bl, 'Name') == b'blkleather_lgl_002|seatL_a')
def recolour(data, insts, rgb):
    from modelbin import Bundle
    b = Bundle.read(data); tpl = fabric_template(); done = []
    for bl in b.blobs:
        nm = b.meta(bl, 'Name')
        if bl['tag'] == 'MatI' and nm is not None and nm.decode() in insts:
            d = bytearray(tpl); k = d.index(COL_HASH) + 5          # hash, type byte (1 = vec4), then 4 floats
            struct.pack_into('<4f', d, k, *rgb, 0.0); bl['data'] = d; done.append(nm.decode())
    assert len(done) == len(insts), (insts, done)
    return b.write()
SEAT_BOLSTER, SEAT_INSERT = (0.060, 0.062, 0.066), (0.095, 0.098, 0.104)    # dark grey cloth, lighter patterned centre
for inst, rgb in (('blkleather_bump_mgl_003|seatL_a', SEAT_BOLSTER), ('blkleather_lgl_002|seatL_a', SEAT_INSERT)):
    replaced[R('seats/seatbeltl_a.modelbin')] = recolour(replaced[R('seats/seatbeltl_a.modelbin')], {inst}, rgb)
replaced[R('seats/parcelshelf_a.modelbin')] = recolour(replaced[R('seats/parcelshelf_a.modelbin')], {'blkleather_bump_mgl_003|rearSeats_a'}, SEAT_BOLSTER)
print('seats: grey cloth')

for f in ('doors/doorcardlf_a.modelbin', 'details/speakerdoorlf_a.modelbin', 'centerconsole/centerconsolebezels_a.modelbin',
          'centerstack/centerstackstructure_a.modelbin', 'centerstack/centerstackbezels_a.modelbin', 'centerstack/nav_a.modelbin',
          ):
    replaced[R(f)] = edit(R(f), hide=lambda m, b: True)

# distant/exterior-view interior: the game swaps the detailed cabin for this one model from outside, so it gets a
# simplified copy of the whole 207 interior (single-sided, authored orientation), sampling one donor texel
def lod_interior(target=2400):
    import trimesh, fast_simplification
    Vs = []
    for k, lst in buckets.items():
        for V, N, UV in lst:
            T = V.reshape(-1, 3, 3)
            if N is not None:
                g = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n = N.reshape(-1, 3, 3).sum(1)
                flip = np.einsum('ij,ij->i', g, n) < 0; T = T.copy(); T[flip] = T[flip][:, [0, 2, 1]]
            Vs.append(T.reshape(-1, 3))
    V = np.concatenate(Vs); m = trimesh.Trimesh(V, np.arange(len(V)).reshape(-1, 3), process=False); m.merge_vertices()
    P, F = fast_simplification.simplify(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.int32),
                                        target_reduction=max(0.0, 1 - target / len(m.faces)))
    P = P.astype(np.float64); g = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    N = np.zeros_like(P)
    for k in range(3): np.add.at(N, F[:, k], g)
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    p = P_(R('interiorlod/interior_a.modelbin'))
    d, _ = decode_group(p, 0)
    uv0 = np.median(d['TEXCOORD0'], 0)
    G = dict(P=P, N=N, UV=np.tile(uv0, (len(P), 1)), UVtan=np.stack([P[:, 2], P[:, 1]], 1),
             UVconst={2: np.median(d['TEXCOORD2'], 0)} if 'TEXCOORD2' in d else None)
    set_group(p, 0, G, {'LOD': F.reshape(-1)})
    print(f'  exterior-view interior: {len(F)} tris (from {len(m.faces)})')
    out = p.build(); Part(out); return out
replaced[R('interiorlod/interior_a.modelbin')] = lod_interior()

# Fiesta dash structure: keep only the needles (bones 16-18) and the steering column (moved with the wheel)
# (dashstructurebezels: built after the dial placement below, the needles scale with their dials)
# steering wheel: the 207's own, placed exactly as the BeamNG model has it (node transform SW_M: 1.1x scale, column
# tilt), then expressed in the wheel bone's frame. The bone (boneSteeringWheelSpindle) keeps its Fiesta orientation,
# within ~1 degree of the 207 column's, and its origin moves to the rim centre so the wheel turns about its own axis.
def steering_wheel():
    sw = it['lib:steeringwheel_very_high']
    B3 = np.load('wheel_bone.npy')[:3, :3]           # bone axes (rows) in world; only its origin moves (to WHEEL_NEW)
    world = lambda V: to_fh2(V @ SW_M[:3, :3].T + SW_M[:3, 3])
    lin = lambda N: to_fh2(N @ SW_M[:3, :3].T) - to_fh2(np.zeros((1, 3)))
    MAT = {'p207_wheelleth': 'blkleather_bump_mgl', 'p207_perfleth': 'blkleather_bump_mgl',
           'vehicle_generic_smallspecmap': 'aluminum_brushed', 'interior_lod0': 'blkplastic_lgl'}
    by = {}
    for p in sw:
        V = (world(p['V'].astype(np.float64)) - WHEEL_NEW) @ B3.T     # exactly where the 207 has it, in bone space
        N = lin(p['N'].astype(np.float64)) @ B3.T
        UV = p['UV'] if p['UV'] is not None else np.zeros((len(V), 2))
        by.setdefault(MAT.get(p['mat'], 'blkplastic_textured_002'), []).append((V, N, UV))
    p = P_(R('dash/steeringwheel_a.modelbin')); nm = material_names(p); uvc = bright_uv(p)
    G_parts, by_idx, base = [], {}, 0
    for mat, lst in by.items():
        V = np.concatenate([x[0] for x in lst]); N = np.concatenate([x[1] for x in lst]); UV = np.concatenate([x[2] for x in lst])
        T = np.arange(len(V)).reshape(-1, 3)
        g = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
        flip = np.einsum('ij,ij->i', g, N[T].sum(1)) < 0; T[flip] = T[flip][:, [0, 2, 1]]
        N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        G_parts.append(dict(P=V, N=N, UV=UV)); by_idx[mat] = T.reshape(-1) + base; base += len(V)
    G = {k: np.concatenate([q[k] for q in G_parts]) for k in ('P', 'N', 'UV')}; G['UVconst'] = uvc
    gid = next(r['group'] for r in p.render if nm[id(r['blob'])] == 'blkleather_bump_mgl')
    set_group(p, gid, G, by_idx)
    for r in p.render:                               # everything else: hidden (other groups, and root-bone meshes)
        b = struct.unpack_from('<h', r['blob']['data'], 2)[0]
        if r['group'] != gid or b != 19:
            i = r['indices'][0] if r['indices'] else 0; r['indices'] = [i, i, i]
    print(f'  207 steering wheel: {sum(len(v) for v in by_idx.values()) // 3} tris, centre {G["P"].mean(0).round(3)} (bone space)')
    out = p.build(); Part(out); return out
replaced[R('dash/steeringwheel_a.modelbin')] = steering_wheel()

# gauge cluster: each Fiesta dial (face + needle bone) into its 207 ring, tilted to the ring plane; the Fiesta's
# housing, glass and bezels hidden (the 207's own are there). Faces sit 2 mm in front of the 207's dial backing.
gp = P_(R('gauges/gaugecluster_a.modelbin')); gnm = material_names(gp)
def _bones(data):
    from modelbin import Bundle
    b = Bundle.read(data); out = {}
    for bl in b.blobs:
        if bl['tag'] != 'Skel': continue
        d = bl['data']; n = struct.unpack_from('<H', d, 0)[0]; o = 2
        for _ in range(n):
            L = struct.unpack_from('<I', d, o)[0]; o += 4; bn = bytes(d[o:o + L]).decode(); o += L + 6
            out[bn] = np.array(struct.unpack_from('<16f', d, o)).reshape(4, 4); o += 64
        break
    return out
FB = _bones(src.read(names[R('gauges/gaugecluster_a.modelbin')]))
dash_lod = np.concatenate([to_fh2(q['V'].astype(np.float64)) for q in it['tableau_de_bord_very_high.242'] if q['mat'].startswith('interior_lod0')])
dash_c = dash_lod.reshape(-1, 3, 3).mean(1)
def ring_target(u, v, r):
    near = np.hypot(dash_c @ RING_E1 - u, dash_c @ RING_E2 - v) < r
    d = np.median(dash_c[near] @ RING_N) - 0.002
    return u * RING_E1 + v * RING_E2 + d * RING_N
DIALS = {'boneTach': ring_target(*RINGS[0]), 'boneFuel': ring_target(*RINGS[1]), 'boneSpeed': ring_target(*RINGS[2])}
# rotation taking the Fiesta dial normal (bone x row, towards the driver) onto the 207's (-RING_N)
def _rot(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
ROT = _rot(FB['boneTach'][0, :3], -RING_N)
DIAL_SRC = {k: FB[k][3, :3] for k in DIALS}
print('  dials: Fiesta', {k: v.round(3).tolist() for k, v in DIAL_SRC.items()}, '-> 207', {k: v.round(3).tolist() for k, v in DIALS.items()})
# the Fiesta's dials are smaller than the 207's: scale each about its centre so its graduations fill the 207 ring
# (Fiesta rev/speed scale radius ~34 mm, needle 31 mm; 207 rings 57 mm; fuel arc ~16 mm into the 44 mm centre ring)
DIAL_SCALE = {'boneTach': 1.45, 'boneSpeed': 1.45, 'boneFuel': 2.0}
def gauge_cluster():
    p = P_(R('gauges/gaugecluster_a.modelbin')); nm = material_names(p)
    keys = list(DIALS); src = np.array([DIAL_SRC[k] for k in keys])
    for r in p.render:
        if nm[id(r['blob'])] != 'gauge_001':          # housing, glass, bezels, digital display: hidden
            i = r['indices'][0] if r['indices'] else 0; r['indices'] = [i, i, i]; continue
        g = p.groups[r['group']]; T = np.array(r['indices']).reshape(-1, 3)
        # triangle islands (each dial's face is one): place each with the dial it belongs to
        parent = {}
        def find(a):
            while parent.setdefault(a, a) != a: parent[a] = parent[parent[a]]; a = parent[a]
            return a
        for t in T: find(t[0]); parent[find(t[1])] = find(t[0]); parent[find(t[2])] = find(t[0])
        comp = {}
        for v in np.unique(T): comp.setdefault(find(v), []).append(v)
        for vs in comp.values():
            P = np.array([g['positions'][v] for v in vs], np.float64); c = P.mean(0)
            d = np.linalg.norm(src[:, :2] - c[:2], axis=1); k = keys[int(np.argmin(d))]
            if d.min() > 0.03:                         # bits between the dials (warning-light strip): folded away
                newP = np.tile(DIALS['boneFuel'], (len(vs), 1))
            else:
                newP = DIALS[k] + DIAL_SCALE[k] * np.einsum('ij,nj->ni', ROT, P - DIAL_SRC[k])
            for v, q in zip(vs, newP): g['positions'][v] = tuple(map(float, q))
    out = p.build(); Part(out); return out
replaced[R('gauges/gaugecluster_a.modelbin')] = gauge_cluster()
def needles():
    p = P_(R('dash/dashstructurebezels_a.modelbin')); nm = material_names(p); bones = {16: 'boneFuel', 17: 'boneSpeed', 18: 'boneTach'}
    todo = {}
    for r in p.render:
        mat = nm[id(r['blob'])]; b = struct.unpack_from('<h', r['blob']['data'], 2)[0]
        if b in (0, 1) and 'steeringColumn' not in mat:
            i = r['indices'][0] if r['indices'] else 0; r['indices'] = [i, i, i]; continue
        for i in r['indices']:
            todo[(r['group'], i)] = ('col', None) if 'steeringColumn' in mat else ('needle', bones.get(b))
    for (gid, i), (kind, bn) in todo.items():
        g = p.groups[gid]; q = np.array(g['positions'][i])
        if kind == 'col': q = q + D_WHEEL
        elif bn: q = q * DIAL_SCALE[bn]                 # bone-local: scale about the needle's pivot
        g['positions'][i] = tuple(map(float, q))
    out = p.build(); Part(out); return out
replaced[R('dash/dashstructurebezels_a.modelbin')] = needles()
D_GAUGE = DIALS['boneTach'] - DIAL_SRC['boneTach']          # (only for the reporting below)
print('gauge cluster: dials placed in the 207 rings', ' steering wheel move', D_WHEEL.round(3))

# rear-view mirror: to where the 207's sits
mir207 = to_fh2(np.concatenate([p['V'] for p in it['Interieur_5p_very_high.018']]).astype(np.float64))
mp = P_(R('pillar/rearviewmirror_a.modelbin'))
mP = np.concatenate([np.array(g['positions']) for g in mp.groups.values()])
D_MIRROR = (mir207.min(0) + mir207.max(0)) / 2 - (mP.min(0) + mP.max(0)) / 2
replaced[R('pillar/rearviewmirror_a.modelbin')] = edit(R('pillar/rearviewmirror_a.modelbin'), move=lambda m, b: D_MIRROR)
print('mirror move', D_MIRROR.round(3))

# ---- bones: the steering wheel and the three needles move with their parts, in every skeleton copy
BONE_MOVES = {'boneSteeringWheelSpindle': D_WHEEL}
BONE_SET = {}
for k in DIALS:                                     # needle bones: on the ring centre, axes tilted with the face
    M = FB[k].copy(); M[:3, :3] = M[:3, :3] @ ROT.T; M[3, :3] = DIALS[k]; BONE_SET[k] = M
def patch_skel(data):
    from modelbin import Bundle
    b = Bundle.read(data); changed = False
    for bl in b.blobs:
        if bl['tag'] != 'Skel': continue
        d = bytearray(bl['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2
        for _ in range(n):
            L = struct.unpack_from('<I', d, o)[0]; o += 4; bn = bytes(d[o:o + L]).decode(); o += L + 6
            if bn in BONE_MOVES:
                t = np.array(struct.unpack_from('<3f', d, o + 48)) + BONE_MOVES[bn]
                struct.pack_into('<3f', d, o + 48, *t); changed = True
            if bn in BONE_SET:
                struct.pack_into('<16f', d, o, *BONE_SET[bn].reshape(-1)); changed = True
            o += 64
        bl['data'] = d
    return b.write() if changed else data

# ---- locators: cockpit camera and the interior points
loc = src.read('Locators.xml').decode('utf-8')
LOC = {'carLocator_steeringWheel': WHEEL_NEW, 'carLocator_gauges': np.mean(list(DIALS.values()), 0), 'stickShift': SHIFT_NEW,
       'carLocator_drivetrain': SHIFT_NEW, 'Handbrake': HBRAKE_NEW,
       'carLocator_seatCamLF': EYE_NEW, 'carLocator_seatCamRF': EYE_NEW * [-1, 1, 1]}
D_EYE = EYE_NEW - EYE_OLD
for nmx in ('carLocator_seatCamLR', 'carLocator_seatCamRR'):
    LOC[nmx] = ('delta', np.array([0, D_EYE[1], 0]))
def set_loc(xml, name, val):
    blk = re.search(r'(<Locator Version="3">(?:(?!</Locator>).)*?<Name value="%s"/>.*?</Locator>)' % re.escape(name), xml, re.S)
    if not blk: print('  locator not found', name); return xml
    b = blk.group(1)
    cur = np.array([float(x) for x in re.search(r'value\._41="([^"]+)" value\._42="([^"]+)" value\._43="([^"]+)"', b).groups()])
    new = cur + val[1] if isinstance(val, tuple) else val
    nb = re.sub(r'value\._41="[^"]+" value\._42="[^"]+" value\._43="[^"]+"',
                'value._41="%.6f" value._42="%.6f" value._43="%.6f"' % tuple(new), b)
    print(f'  {name:28s} {cur.round(3)} -> {np.round(new, 3)}')
    return xml.replace(b, nb)
for k, v in LOC.items(): loc = set_loc(loc, k, v)

# ---- write
out = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6)
for info in src.infolist():
    key = info.filename.lower(); data = src.read(info.filename)
    if key in replaced: data = replaced[key]
    elif key == 'locators.xml': data = loc.encode('utf-8')
    if key.endswith('.modelbin'):
        try: data = patch_skel(data)
        except Exception as e: pass
    out.writestr(zipfile.ZipInfo(info.filename, date_time=info.date_time), data, compress_type=zipfile.ZIP_DEFLATED)
out.close()
print('wrote', OUT)
