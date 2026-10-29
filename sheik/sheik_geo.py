"""Community 207 5-door (BeamNG mod by 'sheik', personal use only) -> FH2 categories, fitted to Owen's scan.

Source space: Z up, front at -Y, metres. FH2: X across (left = -X), Y up, Z forward.
Output scan_sheik.npz: for each category (paint, trim, glass, head, lens, tail) P, N, UV, I double-sided,
ready to drop into the body build in place of the PazMedia geometry.
"""
import pickle, json, numpy as np
from scipy.spatial import cKDTree

ex = pickle.load(open('exterior.pkl', 'rb'))
ex.pop('bumper_f_very_high.009')
ex['bumper_f_prefacelift'] = pickle.load(open('bumpers.pkl', 'rb'))['Mesh.012']     # stored in place, unlike the other
# black rubbing strips: each door has three strip variants on top of it; Owen's car has the all-black ones
_de = pickle.load(open('door_extras.pkl', 'rb'))
for _n in ('door_dside_f_very_high.037', 'door_pside_f_very_high', 'door_dside_r_very_high.003', 'door_pside_r_very_high.001'):   # black strips, body-colour handles
    ex['strip_' + _n] = _de[_n]

# door handle grips: the model has each handle's recess and its two mounting slots, but no grip. Build a
# body-colour grip spanning each pair of slots (positions found from the slot holes in the door meshes).
def grip(side, y0, y1, z, x_mid=0.852, half_d=0.010, half_h=0.0135, segs=18, ring=14):
    V, F = [], []
    ys = np.linspace(y0 - 0.02, y1 + 0.025, segs + 1)
    for i, y in enumerate(ys):
        t = i / segs
        taper = np.sqrt(np.clip(np.sin(np.pi * t) * 1.6, 0.15, 1.0))       # rounded ends
        bow = 0.004 * np.sin(np.pi * t)                                    # bowed slightly outward
        for k in range(ring):
            a = 2 * np.pi * k / ring
            V.append([side * (x_mid + bow + half_d * taper * np.cos(a)), y, z + half_h * taper * np.sin(a)])
    for i in range(segs):
        for k in range(ring):
            a, b = i * ring + k, i * ring + (k + 1) % ring
            F += [[a, b, b + ring], [a, b + ring, a + ring]]
    for end, sgn in ((0, -1), (segs, 1)):                                  # caps
        c = len(V); V.append(list(np.mean(V[end * ring:(end + 1) * ring], 0)))
        for k in range(ring):
            a, b = end * ring + k, end * ring + (k + 1) % ring
            F.append([c, b, a] if sgn < 0 else [c, a, b])
    V = np.array(V); F = np.array(F)
    T = V[F].reshape(-1, 3)
    g = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    cen = V[F].mean(1); axis = np.stack([np.full(len(cen), side * x_mid), cen[:, 1], np.full(len(cen), z)], 1)
    out_dir = cen - axis
    flip = np.einsum('ij,ij->i', g, out_dir) < 0
    F[flip] = F[flip][:, [0, 2, 1]]
    T = V[F].reshape(-1, 3)
    # smooth normals: radial from the grip's centre line
    Nn = T - np.stack([np.full(len(T), side * x_mid), T[:, 1], np.full(len(T), z)], 1)
    Nn[:, 1] *= 0.3
    return dict(mat='p207_body', V=T, N=Nn / np.linalg.norm(Nn, axis=1, keepdims=True), UV=np.zeros((len(T), 2)))
_unused_handles = [grip(s_, y0, y1, z) for s_ in (1, -1) for (y0, y1, z) in ((-0.154, 0.025, 0.832), (0.788, 0.967, 0.858))]
# the tail-lamp internals exist only on one side in place (misc_c .009 at -x); mirror a copy across for the other side
ex['misc_c_mirrored'] = [dict(p, V=p['V'].reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3) * [-1, 1, 1],
                              N=None if p['N'] is None else p['N'].reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3) * [-1, 1, 1],
                              UV=None if p['UV'] is None else p['UV'].reshape(-1, 3, 2)[:, ::-1].reshape(-1, 2))
                         for p in ex['misc_c_very_high.009']]
atlas = np.load('atlas.npy').astype(np.float32) / 255
AH, AW = atlas.shape[:2]

DROP_PARTS = {'taillights_very_high', 'misc_c_very_high.002',            # stray copies parked beside the car
              'Mesh.011', 'Mesh.024'}                                    # 2009-on facelift LED rear lamps (Owen's is a 2008)
DROP_MATS = {'interior_lod0', 'interior_lod02', 'interior_lod05', 'p207_headliner', 'p207_doorcloth', 'p207_carpet',
             'p207_int1'}
CAT = {'p207_body': 'paint',
       'vivace_glass': 'glass', 'vehicle_generic_glasswindows2': 'glass',
       'p207_glasshead': 'lens',
       'p207_redrear': 'tail', 'p207_taillightred': 'tail', 'p207_redglass': 'tail', 'p207_taillight_L': 'tail',
       'p207_chmsl': 'tail', 'p207_chmslled': 'tail', 'p207_framerearlights': 'tail', 'p207_taillight_Lframe': 'tail',
       'noir': 'trim', 'vehicle_generic_smallspecmap': 'trim', 'undercarriage': 'trim', 'undercarriage.002': 'trim',
       'p207_hardplastic': 'trim', 'p207_plastic': 'trim',
       'p207_foglights': 'head'}
FOG_GLASS = {'bumper_f_prefacelift'}      # its 'vivace_glass' is the fog-lamp lenses
ATLAS = {'nodamage_lod0', 'nodamage_lod002', 'nodamage_lod002.001'}
# everything else (lamp reflectors, frames, bulbs, indicators, mirror glass, chrome) -> 'head' (chrome)

# ---- working lamps: the parts of each lamp that light up, by what lights them (the game lights a lamp material
# by its channel: brake, head, reverse, turn). Front units are 'indicators_very_high.*', rear 'misc_c_*'.
LIT = {('indicators', 'p207_lowbeam'): 'L_low', ('indicators', 'p207_lights'): 'L_low', ('indicators', 'p207_OI'): 'L_low',
       ('indicators', 'p207_highbeam'): 'L_high',
       ('indicators', 'p207_signal_L'): 'L_turnf', ('indicators', 'p207_signal_R'): 'L_turnf',
       ('misc_c', 'p207_chmsl'): 'L_brake', ('misc_c', 'p207_taillight_L'): 'L_brake',     # the round tail/brake element
       ('misc_c', 'p207_reverselight'): 'L_rev', ('misc_c', 'p207_signal_RR'): 'L_turnr', ('misc_c', 'p207_signal_RL'): 'L_turnr',
       ('boot', 'p207_chmsl'): 'L_brake', ('boot', 'lights_lod0.001'): 'tail'}             # third brake light on the tailgate
# the rear cluster's reflector and outer lens span all three sections: each triangle goes with its nearest element
REAR_SPLIT = {'p207_framerearlights': {'L_brake': 'L_brake', 'L_rev': 'L_rev', 'L_turnr': 'L_turnr'},
              'p207_redglass': {'L_brake': 'tail', 'L_rev': 'clear', 'L_turnr': 'tail'}}

def to_fh2(V): return np.stack([-V[:, 0], V[:, 2], -V[:, 1]], 1)

tris = {k: [] for k in ('paint', 'trim', 'glass', 'head', 'lens', 'tail', 'clear', 'L_low', 'L_high', 'L_turnf', 'L_brake', 'L_rev', 'L_turnr')}
bumper = []
counts = {}
for part, prims in ex.items():
    if part in DROP_PARTS: continue
    for p in prims:
        m = p['mat']
        if m in DROP_MATS: continue
        V = to_fh2(p['V'].astype(np.float64)); N = to_fh2(p['N'].astype(np.float64)) if p['N'] is not None else None
        UV = p['UV'] if p['UV'] is not None else np.zeros((len(V), 2))
        n = len(V) // 3
        if m in ATLAS:
            c = UV.reshape(n, 3, 2).mean(1)
            px = atlas[np.clip(((1 - c[:, 1] % 1) * AH).astype(int), 0, AH - 1), np.clip((c[:, 0] % 1 * AW).astype(int), 0, AW - 1)]
            lum = px @ [0.299, 0.587, 0.114]; sat = px.max(1) - px.min(1)
            cat = np.where(lum < 0.35, 'trim', np.where(lum > 0.97, 'paint', 'head'))   # black / blank (body colour) / chrome
        else:
            cat = np.full(n, 'lens' if (part in FOG_GLASS and m == 'vivace_glass') else CAT.get(m, 'head'), dtype=object)
            fam = part.split('_very_high')[0].replace('_mirrored', '')
            if (fam, m) in LIT: cat[:] = LIT[(fam, m)]
            if part == 'bodyshell_very_high.163' and m == 'vehicle_generic_smallspecmap': cat[:] = 'head'   # exhaust tip: metal
            if fam == 'misc_c' and m in REAR_SPLIT:
                el = {k: np.concatenate([to_fh2(q['V'].astype(np.float64)) for q in prims if LIT.get((fam, q['mat'])) == k])
                      for k in ('L_brake', 'L_rev', 'L_turnr')}
                c = V.reshape(n, 3, 3).mean(1)
                d = np.stack([np.min(np.linalg.norm(c[:, None, [0, 1]] - e[None, ::3, [0, 1]], axis=2), 1) for e in el.values()], 1)
                cat = np.array([REAR_SPLIT[m][k] for k in el])[d.argmin(1)]
        for k in tris:
            sel = cat == k
            if not sel.any(): continue
            idx = np.repeat(sel, 3)
            tris[k].append(dict(V=V[idx], N=None if N is None else N[idx], UV=UV[idx], part=part))
            counts[(k, m)] = counts.get((k, m), 0) + int(sel.sum())
for (k, m), c in sorted(counts.items()): print(f'{k:6s} {m:32s} {c}')

# ---- straight placement (no scan): the model is true scale (wheelbase 2.54 m, measured from its arches:
# front axle at source y = -1.290, rear at +1.252, ground at z = 0). Put the axle midpoint on the donor's
# (Z = 0, axles at +-1.263) and the ground at the donor's (wheel centre 0.124 - tyre radius 0.3105).
MID_Y = (-1.290 + 1.252) / 2
MID_Y -= 0.0085   # arch circles fitted on the placed body: front +1.273, rear -1.256 -> centre them on Z = 0
GROUND = 0.124 - 0.3105
GROUND -= 0.08    # BeamNG meshes are stored unladen (the car settles ~8 cm on its springs): arch gap 13 -> 5 cm, sills ~15 cm
for k in tris:
    for tt in tris[k]:
        tt['V'] = tt['V'] + np.array([0.0, GROUND, MID_Y])      # FH2 Z = -y, so +MID_Y centres it
# ---- assemble double-sided geometry, winding agreeing with the authored normals
out = {}
for k, lst in tris.items():
    if not lst: continue
    V = np.concatenate([t['V'] for t in lst]); UV = np.concatenate([t['UV'] for t in lst])
    Nsrc = np.concatenate([t['N'] if t['N'] is not None else np.zeros_like(t['V']) for t in lst])
    T = np.arange(len(V)).reshape(-1, 3)
    g = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    flip = np.einsum('ij,ij->i', g, Nsrc[T].sum(1)) < 0
    T[flip] = T[flip][:, [0, 2, 1]]
    # weld for smooth normals: merge identical positions within the category
    key = np.round(V / 2e-4).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.reshape(-1)
    Nv = Nsrc.copy()
    bad = np.linalg.norm(Nv, axis=1) < 0.5
    if bad.any():
        acc = np.zeros((len(first), 3))
        g = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
        for j in range(3): np.add.at(acc, inv[T[:, j]], g)
        Nv[bad] = acc[inv[bad]]
    Nv /= np.maximum(np.linalg.norm(Nv, axis=1, keepdims=True), 1e-12)
    n = len(V)
    out[f'{k}_P'] = np.r_[V, V]; out[f'{k}_N'] = np.r_[Nv, -Nv]; out[f'{k}_UV'] = np.r_[UV, UV]
    out[f'{k}_I'] = np.r_[T, T[:, [0, 2, 1]] + n].reshape(-1)
    print(f'{k:6s} {len(T):7d} tris  bounds {V.min(0).round(2)} {V.max(0).round(2)}')
np.savez('scan_sheik.npz', **out)
