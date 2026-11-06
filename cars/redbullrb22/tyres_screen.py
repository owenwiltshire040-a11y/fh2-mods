"""RB22: the model's own Pirelli tyres on the wheels, and a live steering-wheel screen (after the Williams FW24's).

Applies to an already built + finished RB22 package (the output of package_car + finish_wheels_cameras):

  python3 cars/redbullrb22/tyres_screen.py PKG --ow-f1 tireL_OW_F1.modelbin

TYRES. FH2 draws every car's tyre from a shared library model chosen by List_UpgradeTireCompound.TireModelName
(media/cars/_library/scene/tires/tire_<name>.zip -> tireL_<name>.modelbin; normalised, sized by morphs from the
database tyre size). The RB22 used 'OW_F1' (plain tread_c / sidewall_c materials, no markings). Here:
  * the model's tyres (body + the 8 PIRELLI / P ZERO sidewall panels per tyre, sidewall.007) go into the car's own
    wheel parts, in the wheel part's space (depth in metres from the rim face, radius normalised to R = 0.1397 with
    the game's diameter morph), scaled so the outer radius equals the physics tyre (front 350/36 R18 = 0.3546 m,
    rear 400/31 R18 = 0.3526 m). Front tyre -> ..._wheelLF.modelbin, rear tyre -> a new ..._wheelLR.modelbin
    (same rim), carbin rear wheels re-pointed to it;
  * TireModelName -> 'RB22_26', a library tyre shipped in the mod's media folder (the mod loader mounts it over
    game:\\media): the OW_F1 tyre with every vertex collapsed to one point and its size morphs zeroed, so the game
    draws nothing over the model's tyres. Physics tyre sizes are unchanged.
SCREEN. A car's digital display is its UI/<MEDIA>.xaml page (1280 x 720), drawn live onto any mesh using the game's
'digitalgauge' base material (UV0 = page position). The model's LCD (sw_gp21_LCD.003, a flat 9.3 x 5.4 cm quad on
the steering spindle) is moved into steering wheel group 2 (layout NORMAL0/TEXCOORD0/TEXCOORD2, the Williams'
digitalGauge layout) with a digitalgauge material and full-page UVs; the page is written here (own LED images).
"""
from pathlib import Path
import sys, struct, zipfile, json, io, pickle, argparse, hashlib, re
import numpy as np
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'fh2re')); sys.path.insert(0, str(REPO / 'f1')); sys.path.insert(0, str(REPO / 'tex'))
from geometry import Part
from body_swap import material_names
from gltf_bridge import decode_group, encode_group, tangents, O_UVT
import fhmat, carbin, swatch, uiswatch

MEDIA = 'RBR_RedBullRB22_26'
TYRE_NAME = 'RB22_26'
WHITEWALL = None
R, RIM = .1397, .2286                       # wheel-part face radius; 18 in rim radius (m)
PHYS = {'F': .2286 + .350 * .36, 'R': .2286 + .400 * .31}     # database tyre outer radii
# the game's digitalgauge MatI (no texture overrides), as used by the Williams FW24 / Dallara DW12 steering wheels
DIGITAL_MATI = bytes.fromhex(
    '627572470100020060000000bc0000004954414d0100020040000000600000004b0000004b0000005250544d020000005d000000ac000000'
    '0d0000000d000000656d614ec000100054535441110014006469676974616c6761756765000000004a47616d653a5c4d656469615c636172'
    '735c5f6c6962726172795c6d6174657269616c735c626173656d6174657269616c735c6469676974616c67617567652e6d6174657269616c'
    '62696e0000000000000000000000000000000000')


# ================================================================== tyres
def source_tyres():
    """{'F': tyre, 'R': tyre} in the left wheel part's space: P (depth m, y, z physical m), N, UV (FH2), T"""
    import trimesh
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    A = json.load(open(HERE / 'source-analysis.json')); off = np.array(A['offset'])
    G = pickle.load(open(HERE / 'geo.pkl', 'rb'))
    s = trimesh.load(HERE / 'model.glb', force='scene')
    pieces = {'F': [], 'R': []}
    for node in s.graph.nodes_geometry:
        T, key = s.graph[node]; m = s.geometry[key]
        if m.visual.material.name != 'sidewall.007': continue
        V = trimesh.transform_points(m.vertices, T) * [-1, 1, 1] + off          # FH2 space (mirror x)
        N = (m.vertex_normals @ T[:3, :3].T) * [-1, 1, 1]
        UV = np.c_[m.visual.uv[:, 0], 1 - m.visual.uv[:, 1]]                   # trimesh (v up) -> FH2 / glTF (v down)
        F = m.faces[:, ::-1]                                                    # mirrored: keep the winding
        e = m.edges_unique
        n, lab = connected_components(coo_matrix((np.ones(len(e)), e.T), shape=(len(V),) * 2), directed=False)
        for i in range(n):
            vi = np.where(lab == i)[0]; c = V[vi].mean(0)
            if c[0] >= 0: continue                                              # left wheels only (FH2 -x)
            fi = F[np.isin(F[:, 0], vi)]
            remap = -np.ones(len(V), int); remap[vi] = np.arange(len(vi))
            pieces['F' if c[2] > 0 else 'R'].append(dict(V=V[vi], N=N[vi], UV=UV[vi], T=remap[fi], body=len(vi) > 1000))
    rims = {'F': np.concatenate([p['V'] for p in G['parts']['SOURCE_RIM']]),
            'R': np.concatenate([p['V'] for p in G['parts']['rim_rear']])}
    rims['R'] = rims['R'][(rims['R'][:, 0] < 0)]
    out = {}
    for k, ps in pieces.items():
        body = [p for p in ps if p['body']]; assert len(body) == 1 and len(ps) == 9, (k, len(body), len(ps))
        B = body[0]['V']; c = B.mean(0)
        w, vec = np.linalg.eigh(np.cov((B - c).T)); axis = vec[:, 0]           # smallest spread = the axle
        a_out = axis if axis[0] < 0 else -axis                                  # left wheel: outward = -x
        a_in = -a_out
        e_y = np.array([0., 1, 0]) - a_in[1] * a_in; e_y /= np.linalg.norm(e_y)
        e_z = np.cross(a_in, e_y)
        s_rim = ((rims[k] - c) @ a_out).max()                                   # the rim's outermost face = depth 0
        V = np.concatenate([p['V'] for p in ps]); N = np.concatenate([p['N'] for p in ps])
        UV = np.concatenate([p['UV'] for p in ps]); base = np.cumsum([0] + [len(p['V']) for p in ps])
        T = np.concatenate([p['T'] + b for p, b in zip(ps, base)])
        d = V - c
        r_src = np.hypot((B - c) @ e_y, (B - c) @ e_z).max(); scale = PHYS[k] / r_src
        P = np.stack([s_rim - scale * (d @ a_out), scale * (d @ e_y), scale * (d @ e_z)], 1)
        Nl = np.stack([N @ a_in, N @ e_y, N @ e_z], 1); Nl /= np.maximum(np.linalg.norm(Nl, axis=1, keepdims=True), 1e-9)
        UV = UV - np.floor(UV.reshape(-1, 1, 2).min(0))                         # whole tiles: the texture repeats
        camber = float(np.degrees(np.arcsin(abs(a_out[1]))))
        out[k] = dict(P=P, N=Nl, UV=UV, T=T, r_src=float(r_src), scale=float(scale), camber_removed_deg=camber,
                      depth=(float(P[:, 0].min()), float(P[:, 0].max())), outer_radius=float(np.hypot(P[:, 1], P[:, 2]).max()))
    return out


BLUR = 0x1c        # mesh flag of the spin-blur pass (normal meshes: 0x11)

def strip_blur(p):
    """remove the spin-blur pass: the game switches a fast-spinning wheel to these meshes, and the RB22's (source rim
    clones, 0.1.4) drew nothing in game (Owen 6 Nov: tyres vanish at speed). The Williams FW24's wheel has no blur pass
    and keeps its normal meshes at every speed."""
    blur = [r for r in p.render if struct.unpack_from('<I', r['blob']['data'], 8)[0] == BLUR]
    # a vertex group drawn only by blur meshes (the donor's blur_lip) keeps one as an empty normal mesh
    keep = {}
    for r in blur:
        if not any(o['group'] == r['group'] and struct.unpack_from('<I', o['blob']['data'], 8)[0] != BLUR for o in p.render):
            keep.setdefault(r['group'], r)
    for r in keep.values():
        struct.pack_into('<I', r['blob']['data'], 8, 0x11); r['indices'] = [r['indices'][0]] * 3
    gone = [r for r in blur if r not in keep.values()]
    ids = {id(r['blob']) for r in gone}
    for s in p.shadows:
        assert not any(id(r['blob']) in ids for r in s['run']), 'a shadow mesh uses a blur mesh'
    p.render = [r for r in p.render if id(r['blob']) not in ids]
    p.meshes = [m for m in p.meshes if id(m) not in ids]
    p.b.blobs = [b for b in p.b.blobs if id(b) not in ids]
    M = fhmat.modl(p); d = bytearray(M['data']); struct.pack_into('<H', d, 0, len(p.meshes)); M['data'] = d
    return len(gone)


def add_tyre(raw, tyre, tex_path, gloss_path, tpl_mati):
    """the source tyre into a wheel part (group 0, beside the source rim), drawn at every LOD; no spin-blur pass"""
    p = Part(raw); strip_blur(p); names = material_names(p)
    rim = [r for r in p.render if names[id(r['blob'])] == 'source_rim']
    assert len(rim) == 6 and all(r['group'] == 0 for r in rim), len(rim)
    A, els = decode_group(p, 0); g = p.groups[0]; n0 = len(g['positions'])
    ref = next(r for r in rim if struct.unpack_from('<H', r['blob']['data'], 4)[0] == 3 and struct.unpack_from('<I', r['blob']['data'], 8)[0] == 17)
    ids = np.array(sorted(set(ref['indices'])))
    P = tyre['P'].copy(); P[:, 1:] *= R / RIM                                   # wheel-part radius units
    X = np.c_[A['POSITION'][ids, 1], A['POSITION'][ids, 2], np.ones(len(ids))]
    Xn = np.c_[P[:, 1], P[:, 2], np.ones(len(P))]
    new = {'POSITION': P.astype(np.float32), 'NORMAL0': np.c_[tyre['N'], np.zeros(len(P))].astype(np.float32),
           'TEXCOORD0': tyre['UV'].astype(np.float32)}
    for k in ('TEXCOORD1', 'TEXCOORD2', 'TEXCOORD3'):                           # AO / mask lookups: the rim's own trend
        co = np.linalg.lstsq(X, A[k][ids].astype(np.float64), rcond=None)[0]; new[k] = (Xn @ co).astype(np.float32)
    tan = tangents(P.astype(np.float64), tyre['N'].astype(np.float64), tyre['UV'].astype(np.float64), tyre['T'].reshape(-1)).astype(np.float32)
    new['TANGENT0'] = new['TANGENT1'] = tan
    allA = {k: np.concatenate([np.asarray(A[k], np.float32), new[k]]) for k in ['POSITION'] + [e['name'] for e in els]}
    rows, uvt = encode_group(p, 0, allA)
    g['positions'] = [tuple(map(float, v)) for v in allA['POSITION']]; g['attrs'] = rows
    m = np.frombuffer(g['morph'][ids[0]], '<f2').reshape(4, 4).astype(np.float32)
    morph = np.tile(m, (len(P), 1, 1)); morph[:, 1, :] = 0; morph[:, 1, 1] = 1.3247 * P[:, 1]; morph[:, 1, 2] = 1.3247 * P[:, 2]
    g['morph'] = list(g['morph']) + [r.tobytes() for r in morph.astype('<f2')]
    for r in p.render:
        if r['group'] == 0: struct.pack_into('<20f', r['blob']['data'], O_UVT, *uvt)
    mid = fhmat.add_material(p, 'source_tyre', fhmat.retexture(tpl_mati, [tex_path, gloss_path]), [tex_path, gloss_path])
    tri = (tyre['T'].reshape(-1) + n0).tolist()
    for r in rim:
        fhmat.add_mesh(p, r, mid); p.render[-1]['indices'] = list(tri)
    out = p.build(); q = Part(out)
    mesh_count = struct.unpack_from('<H', next(b for b in q.b.blobs if b['tag'] == 'Modl')['data'], 0)[0]
    assert mesh_count == len(q.meshes), (mesh_count, len(q.meshes))
    qn = material_names(q); drawn = [r for r in q.render if qn[id(r['blob'])] == 'source_tyre']
    assert len(drawn) == 6 and all(len(r['indices']) == len(tri) for r in drawn)
    assert not any(struct.unpack_from('<I', r['blob']['data'], 8)[0] == BLUR for r in q.render)
    return out


def narrow_library_tyre(ow_f1, width=0.80, radius=0.995):
    """the game's OW_F1 slick, narrower and a touch smaller, as the RB22's library tyre: it sits inside the model's
    Pirelli tyre (Owen 6 Nov 0.1.14: the full-width slick poked out of the sidewalls) and still shows when the
    model's tyre is not drawn at high wheel speed. Linear: the drawn tyre = position + sum(weight * morph offset), so
    scaling the positions and every morph offset (10 half4 targets per vertex: x, y, z, tag) scales the result.
    Width about the tyre's centre line (x = 0.5 in its 0..1 width space), radius about the axle."""
    p = Part(ow_f1)
    for g in p.groups.values():
        P = np.array(g['positions'], np.float64)
        P[:, 0] = 0.5 + width * (P[:, 0] - 0.5); P[:, 1:] *= radius
        g['positions'] = [tuple(map(float, v)) for v in P]
        if g['morph'] is not None:
            m = np.frombuffer(b''.join(g['morph']), '<f2').reshape(len(P), -1, 4).astype(np.float32)
            m[:, :, 0] *= width; m[:, :, 1:3] *= radius
            stride = len(g['morph'][0]); raw = m.astype('<f2').tobytes()
            g['morph'] = [raw[i * stride:(i + 1) * stride] for i in range(len(P))]
    out = p.build(); Part(out)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(f'tireL_{TYRE_NAME}.modelbin', out)
    return buf.getvalue()


PIRELLI_RED = (0.62, 0.015, 0.015, 0.0)     # whitewall band colour param (stock: 0.578 grey = white)

def red_band(raw, colour=PIRELLI_RED):
    """the game's open-wheel whitewall tyre with its band recoloured: at speed a Pirelli sidewall blurs into a red
    ring (Owen 6 Nov: give the plain tyre the red trim). The 'whitewall' MatI's vec4 parameter is the band colour."""
    from modelbin import Bundle
    p = Part(raw); n_done = 0
    for bl in p.b.blobs:
        if bl['tag'] != 'MatI' or p.b.meta(bl, 'Name') != b'whitewall': continue
        inner = Bundle.read(bytes(bl['data'])); mt = next(b for b in inner.blobs if b['tag'] == 'MTPR'); m = bytearray(mt['data'])
        o = 1
        for _ in range(m[0]):
            typ = m[o + 6]; o += 7
            if typ == 1: struct.pack_into('<4f', m, o, *colour); o += 16; n_done += 1
            elif typ in (2, 3, 4, 5): o += 4
            else: raise ValueError(typ)
        mt['data'] = m; bl['data'] = bytearray(inner.write())
    assert n_done == 1, n_done
    return p.build()


def hidden_library_tyre(ow_f1):
    """the OW_F1 library tyre with nothing to draw: every position one point, size morphs zero"""
    p = Part(ow_f1)
    for g in p.groups.values():
        g['positions'] = [(0.5, 0.0, 0.0)] * len(g['positions'])
        if g['morph'] is not None: g['morph'] = [bytes(len(r)) for r in g['morph']]
    out = p.build(); q = Part(out)
    assert all(set(g['positions']) == {(0.5, 0.0, 0.0)} for g in q.groups.values())
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_STORED) as z:
        z.writestr(f'tireL_{TYRE_NAME}.modelbin', out)
    return buf.getvalue()


# ================================================================== screen
LCD_MAT = 'rbr_redbullrb22_26_tdc57e57cd3'      # sw_gp21_LCD.003 ('t' + sha1(name)[:10])

def add_screen(raw):
    p = Part(raw); names = material_names(p)
    A0, _ = decode_group(p, 0)
    lcd = [r for r in p.render if names[id(r['blob'])] == LCD_MAT]
    assert lcd, 'LCD material not found'
    Q = A0['POSITION'][sorted(set(lcd[0]['indices']))]
    # the quad's corners in the steering spindle's space: y across (driver's left = +y), z down the face
    ymin, ymax = Q[:, 1].min(), Q[:, 1].max()
    top = Q[Q[:, 2] < Q[:, 2].mean()].mean(0); bot = Q[Q[:, 2] >= Q[:, 2].mean()].mean(0)
    TL = np.array([top[0], ymax, top[2]]); TR = np.array([top[0], ymin, top[2]])
    BR = np.array([bot[0], ymin, bot[2]]); BL = np.array([bot[0], ymax, bot[2]])
    n = np.cross(TR - TL, BL - TL); n /= np.linalg.norm(n)
    if n[0] > 0: n = -n                                            # faces the driver (-x in the spindle frame)
    corners = np.stack([TL, TR, BR, BL]) + n * 0.0004             # 0.4 mm proud of the old LCD plane
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], np.float32)  # page: u to the driver's right, v down
    tri = np.array([[0, 1, 2], [0, 2, 3]])
    if np.dot(np.cross(corners[1] - corners[0], corners[2] - corners[0]), n) < 0: tri = tri[:, [0, 2, 1]]
    # group 2 (Williams digitalGauge layout): replace its single material's placeholder with the quad
    from body_swap import set_group
    g2mats = sorted({names[id(r['blob'])] for r in p.render if r['group'] == 2})
    assert g2mats == ['stdsymbols_002'], g2mats
    set_group(p, 2, {'P': corners, 'N': np.tile(n, (4, 1)), 'UV': uv, 'UVconst': {2: (0.952, 0.05)}},
              {'stdsymbols_002': tri.reshape(-1)})
    mid = fhmat.add_material(p, 'digitalGauge', DIGITAL_MATI)
    for r in p.render:
        if r['group'] == 2: struct.pack_into('<h', r['blob']['data'], 0, mid)
    for r in lcd:                                                 # the old static LCD: nothing to draw
        r['indices'] = [r['indices'][0]] * 3
    out = p.build(); q = Part(out); qn = material_names(q)
    assert struct.unpack_from('<H', next(b for b in q.b.blobs if b['tag'] == 'Modl')['data'], 0)[0] == len(q.meshes)
    scr = [r for r in q.render if qn[id(r['blob'])] == 'digitalGauge']
    assert scr and all(len(r['indices']) == 6 for r in scr), [len(r['indices']) for r in scr]
    size = (float(np.linalg.norm(TR - TL)), float(np.linalg.norm(BL - TL)))
    return out, dict(screen_m=size, normal=n.tolist(), lods=sorted(r['blob']['data'][4] for r in scr))


def rebuild_steering(raw):
    """The donor-built steering wheel never drew (RB22, Jordan, Toro; Owen 6 Nov): build_car put the textured
    (interior_lod1) materials into the Charger part's group 0, whose vertex layout has no TEXCOORD0 / TANGENT0
    (NORMAL0, TEXCOORD1, TEXCOORD2, TANGENT1), so the shader's inputs were missing and the meshes were dropped.
    Rebuilt here from the source model (geo.pkl sw_* parts, with their UVs) into group 3, the part's full-layout group
    (NORMAL0, TEXCOORD0-3, TANGENT0-1, like every group of the Williams FW24's wheel), plus the live screen quad
    (digitalgauge) in the same group. Groups 0-2 are left empty."""
    from body_swap import set_group
    from geometry import O_LAYOUT, O_VB0
    A = json.load(open(HERE / 'source-analysis.json')); G = pickle.load(open(HERE / 'geo.pkl', 'rb'))
    p = Part(raw); names = material_names(p)
    # the spindle frame, exactly as build_car (local = (V - STEER) @ basis.T)
    from modelbin import Bundle
    basis = None
    for bl in p.b.blobs:
        if bl['tag'] != 'Skel': continue
        d = bl['data']; n = struct.unpack_from('<H', d, 0)[0]; off = 2
        for _ in range(n):
            L = struct.unpack_from('<I', d, off)[0]; off += 4; nm = bytes(d[off:off + L]).decode(); off += L + 6
            if nm == 'boneSteeringWheelSpindle': basis = np.array(struct.unpack_from('<16f', d, off)).reshape(4, 4)[:3, :3]
            off += 64
    sw = [m for m in G['parts'] if m.startswith('sw_')]
    allV = np.concatenate([q['V'] for m in sw for q in G['parts'][m]])
    steer = ((allV.min(0) + allV.max(0)) / 2).round(4)
    old = [r for r in p.render if r['group'] == 0 and len(set(r['indices'])) > 1]
    A0, _ = decode_group(p, 0); used0 = sorted({i for r in old for i in r['indices']})
    lo0, hi0 = A0['POSITION'][used0].min(0), A0['POSITION'][used0].max(0)
    uv1 = np.median(A0['TEXCOORD1'][used0], 0); uv2 = np.median(A0['TEXCOORD2'][used0], 0)
    Ps, Ns, UVs, by, base = [], [], [], {}, 0
    lcd = None
    for m in sw:
        V = np.concatenate([q['V'] for q in G['parts'][m]]); N = np.concatenate([q['N'] for q in G['parts'][m]])
        UV = np.concatenate([q['UV'] for q in G['parts'][m]])
        V = (V - steer) @ basis.T; N = N @ basis.T
        if m == 'sw_gp21_LCD.003': lcd = V; continue
        # weld the triangle soup: a part on a moving bone stays under 65,536 vertices (every working one does:
        # donor wheel 7k, Williams wheel 21k, road wheels 19k; the soup was 200k)
        key = np.round(np.c_[V * 1e4, N * 100, UV * 4096]).astype(np.int64)
        _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
        V, N, UV = V[first], N[first], UV[first]; T = inv.reshape(-1, 3)
        if m in ('sw_sw_decals.004', 'sw_clearled.003'):     # stickers 2 mm proud / LED lenses: front faces only
            V2, N2, UV2, T2 = V, N, UV, T
        else:                                                # two-sided
            V2 = np.concatenate([V, V]); N2 = np.concatenate([N, -N]); UV2 = np.concatenate([UV, UV])
            T2 = np.concatenate([T, T[:, ::-1] + len(V)])
        key = A['mapping'][m][1]; mname = f'{MEDIA.lower()}_{key}'
        assert any(names[id(r['blob'])] == mname for r in old), mname
        Ps.append(V2); Ns.append(N2); UVs.append(UV2); by[mname] = (T2 + base).reshape(-1); base += len(V2)
    P = np.concatenate(Ps)
    assert np.abs(P.min(0) - lo0).max() < 0.003 and np.abs(P.max(0) - hi0).max() < 0.003, (P.min(0), lo0, P.max(0), hi0)
    # the screen: the LCD quad, 0.4 mm proud, facing the driver, page UVs (u right, v down as the driver sees it)
    ymin, ymax = lcd[:, 1].min(), lcd[:, 1].max()
    top = lcd[lcd[:, 2] < lcd[:, 2].mean()].mean(0); bot = lcd[lcd[:, 2] >= lcd[:, 2].mean()].mean(0)
    TL = np.array([top[0], ymax, top[2]]); TR = np.array([top[0], ymin, top[2]])
    BR = np.array([bot[0], ymin, bot[2]]); BL = np.array([bot[0], ymax, bot[2]])
    nrm = np.cross(TR - TL, BL - TL); nrm /= np.linalg.norm(nrm)
    if nrm[0] > 0: nrm = -nrm
    quad = np.stack([TL, TR, BR, BL]) + nrm * 0.0004
    qt = np.array([[0, 1, 2], [0, 2, 3]])
    if np.dot(np.cross(quad[1] - quad[0], quad[2] - quad[0]), nrm) < 0: qt = qt[:, [0, 2, 1]]
    Ps.append(quad); Ns.append(np.tile(nrm, (4, 1))); UVs.append(np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float))
    by['digitalGauge'] = (qt + base).reshape(-1)
    # move the textured meshes to group 3 (layout id + attribute buffer binding), add the screen mesh there
    tpl = next(r for r in p.render if r['group'] == 3)
    t_lay = struct.unpack_from('<i', tpl['blob']['data'], O_LAYOUT)[0]; t_vb = struct.unpack_from('<iiii', tpl['blob']['data'], O_VB0 + 16)
    for r in p.render:
        if r['group'] == 0 and names[id(r['blob'])] in by:
            d = r['blob']['data']; struct.pack_into('<i', d, O_LAYOUT, t_lay); struct.pack_into('<iiii', d, O_VB0 + 16, *t_vb); r['group'] = 3
    mid = fhmat.add_material(p, 'digitalGauge', DIGITAL_MATI)
    fhmat.add_mesh(p, tpl, mid)
    geo = dict(P=np.concatenate(Ps), N=np.concatenate(Ns), UV=np.concatenate(UVs), UVconst={1: uv1, 2: uv2, 3: uv2})
    set_group(p, 3, geo, by)
    for g in (0, 1, 2):
        set_group(p, g, dict(P=np.zeros((0, 3)), N=np.zeros((0, 3)), UV=np.zeros((0, 2))), {})
    out = p.build(); q = Part(out); qn = material_names(q)
    assert struct.unpack_from('<H', next(b for b in q.b.blobs if b['tag'] == 'Modl')['data'], 0)[0] == len(q.meshes)
    nverts = sum(len(g['positions']) for g in q.groups.values()); assert nverts < 65536, nverts
    drawn = [r for r in q.render if len(set(r['indices'])) > 1]
    assert drawn and all(r['group'] == 3 for r in drawn), sorted({r['group'] for r in drawn})
    from gltf_bridge import layout_of
    lay = [e['name'] for e in layout_of(q, 3)[0]]; assert 'TEXCOORD0' in lay and 'TANGENT0' in lay, lay
    return out, dict(group=3, layout=lay, vertices=nverts, triangles=sum(len(r['indices']) for r in drawn) // 3,
                     materials=sorted(qn[id(r['blob'])] for r in drawn), screen_m=(float(np.linalg.norm(TR - TL)), float(np.linalg.norm(BL - TL))))


def driver_wheel_track(entries):
    """The driver animations (scene/drivers/default/*.gr2, from the Toro build) each carry a constant position track for
    boneSteeringWheel, the steering wheel part's parent bone. It overrides the skeleton at runtime, so the wheel was
    drawn at that animation set's old wheel position (Owen 6 Nov 0.1.12: wheel shows, but where the Charger's was).
    Set it to the RB22 skeleton's own local position of that bone (build_car moved only the Hips track)."""
    import granny
    sk = next(n for n in entries if n.lower().endswith('_skeleton.gr2'))
    target = next(pos for name, par, pos, _ in granny.bones(granny.GR2(entries[sk])) if name == 'boneSteeringWheel')
    done = {}
    for n in [n for n in entries if n.lower().startswith('scene/drivers/') and n.lower().endswith('.gr2')]:
        g = granny.GR2(entries[n]); r = granny.set_track_position(g, 'boneSteeringWheel', list(target), list(target))
        assert r == ['constant'], (n, r)
        entries[n] = g.write()
        after = granny.track_position_constant(granny.GR2(entries[n]), 'boneSteeringWheel')
        assert np.allclose(after, target, atol=1e-5), (n, after)
        done[n.split('/')[-1]] = r[0]
    return dict(target=[round(float(x), 4) for x in target], files=len(done))


LOD_SET = [(4, 1), (8, 2), (16, 3), (32, 4), (64, 5)]     # (mask, index) after LOD0 (3, 0/255), as on the Williams FW24

def all_lods(raw):
    """the donor-built steering wheel only had LOD0 meshes (mask 3; Modl LOD mask 3). The game's cockpit camera
    draws another LOD (Owen 6 Nov 0.1.9: still no steering wheel). Every LOD0 mesh is copied into LOD1-5 like the
    Williams FW24's wheel (meshes at 3/4/8/16/32/64, Modl mask 0x3f)."""
    p = Part(raw)
    base = [r for r in p.render if r['blob']['data'][4] == 3]
    assert len(base) == len(p.render), 'steering wheel already has other LODs'
    for r in base:
        mat = struct.unpack_from('<h', r['blob']['data'], 0)[0]
        for mask, index in LOD_SET:
            fhmat.add_mesh(p, r, mat); n = p.render[-1]
            struct.pack_into('<H', n['blob']['data'], 4, mask); struct.pack_into('<BB', n['blob']['data'], 6, index, index)
            n['indices'] = list(r['indices'])
    M = fhmat.modl(p); d = bytearray(M['data']); struct.pack_into('<H', d, len(d) - 2, 0x3f); M['data'] = d
    out = p.build(); q = Part(out)
    assert struct.unpack_from('<H', next(b for b in q.b.blobs if b['tag'] == 'Modl')['data'], 0)[0] == len(q.meshes)
    masks = sorted({r['blob']['data'][4] for r in q.render}); assert masks == [3, 4, 8, 16, 32, 64], masks
    return out


def led_images():
    """84 x 84 LED images (own artwork): a bright lens with a soft halo, for the page's shift lights"""
    yy, xx = np.mgrid[0:84, 0:84]; r = np.hypot(xx - 41.5, yy - 41.5) / 42
    out = {}
    for name, rgb in (('Green', (40, 255, 90)), ('Red', (255, 40, 40)), ('Blue', (60, 140, 255)), ('Off', (70, 70, 76))):
        core = np.clip((0.62 - r) / 0.06, 0, 1); halo = np.clip(1 - r, 0, 1) ** 3 * (0.0 if name == 'Off' else 0.55)
        a = np.clip(core + halo, 0, 1)
        col = np.array(rgb, float)[None, None] * (0.75 + 0.25 * core[..., None]) + 255 * 0.35 * core[..., None] ** 4
        rgba = np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8)
        out[f'UI/Textures/RBR_LED_{name}.swatchbin'] = uiswatch.encode(rgba)
    return out


def page_xaml(max_rpm=15000):
    """the RB22's 1280 x 720 display page (same building blocks as the game's DW12 / Williams FW24 pages)"""
    tex = f'game:/media/cars/{MEDIA}/UI/Textures'
    lights = [('Green', i) for i in range(1, 6)] + [('Red', i) for i in range(1, 6)] + [('Blue', i) for i in range(1, 6)]
    names = [f'{c}{i}' for c, i in lights]
    on_at = np.linspace(0.70, 0.90, 15); flash_at = 0.93
    t = lambda x: f'0:0:{x:.3f}'
    prog = []
    for nm, at in zip(names, on_at):
        prog.append(f'\t\t\t<DoubleAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Opacity)" Storyboard.TargetName="{nm}_On">\n'
                    f'\t\t\t\t<DiscreteDoubleKeyFrame KeyTime="{t(at)}" Value="1"/>\n\t\t\t</DoubleAnimationUsingKeyFrames>')
    for nm, at in zip(names, on_at):
        prog.append(f'\t\t\t<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Visibility)" Storyboard.TargetName="{nm}_On">\n'
                    f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="{t(at)}" Value="{{x:Static Visibility.Visible}}"/>\n'
                    f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="{t(flash_at)}" Value="{{x:Static Visibility.Hidden}}"/>\n\t\t\t</ObjectAnimationUsingKeyFrames>')
    prog.append(f'\t\t\t<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Visibility)" Storyboard.TargetName="FLASHING">\n'
                f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0" Value="{{x:Static Visibility.Hidden}}"/>\n'
                f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="{t(flash_at)}" Value="{{x:Static Visibility.Visible}}"/>\n\t\t\t</ObjectAnimationUsingKeyFrames>')
    flash = []
    for nm in names:
        flash.append(f'\t\t\t<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Visibility)" Storyboard.TargetName="{nm}_Flashing">\n'
                     f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0" Value="{{x:Static Visibility.Visible}}"/>\n'
                     f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0:0:0.08" Value="{{x:Static Visibility.Hidden}}"/>\n'
                     f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0:0:0.16" Value="{{x:Static Visibility.Hidden}}"/>\n\t\t\t</ObjectAnimationUsingKeyFrames>')
    def row(state, opacity, extra=''):
        imgs = []
        for k, (c, i) in enumerate(lights):
            src = f'{tex}/RBR_LED_{"Off" if state == "Off" else c}.png'
            imgs.append(f'\t\t\t\t<Image x:Name="{c}{i}_{state}" Height="76" Width="76" Source="{src}" Stretch="Fill" '
                        f'Canvas.Left="{k * 80}" Canvas.Top="0" Opacity="{opacity}"/>')
        return '\n'.join(imgs)
    text = lambda name, binding, left, top, width, size, align='Center', fg=None: (
        f'\t\t\t<TextBlock x:Name="{name}" TextAlignment="{align}" Canvas.Left="{left}" Canvas.Top="{top}" Width="{width}" '
        f'FontSize="{size}" Style="{{StaticResource TextBlockStyle}}"' + (f' Foreground="{fg}"' if fg else '') +
        (f' Text="{{Binding {binding}}}"/>' if binding else '/>'))
    rpm = '\n'.join(text(f'Text_Rpm_{b}', b, 860, 300, 400, 120) for b in ('Rpm', 'RPM', 'EngineRpm', 'TextTach', 'TachText', 'Revs'))
    label = lambda s, left, top, width, size: (f'\t\t\t<TextBlock TextAlignment="Center" Canvas.Left="{left}" Canvas.Top="{top}" Width="{width}" '
                                               f'FontSize="{size}" Style="{{StaticResource TextBlockStyle}}" Foreground="#FF8A93A8" Text="{s}"/>')
    return f'''<Page
	xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
	xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
	xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
	xmlns:System="clr-namespace:System;assembly=mscorlib"
	xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
	xmlns:local="clr-namespace:ForzaUI"
	mc:Ignorable="d"
	x:Class="DigitalGauge.{MEDIA}"
	DataContext="{{Binding RelativeSource={{x:Static RelativeSource.Self}}}}">

	<Page.Resources>
		<Style x:Key="TextBlockStyle" TargetType="{{x:Type TextBlock}}">
			<Setter Property="FontFamily" Value="DG5_QuartzMS"/>
			<Setter Property="Foreground" Value="White"/>
			<Setter Property="TextWrapping" Value="NoWrap"/>
			<Setter Property="TextAlignment" Value="Right"/>
		</Style>

		<local:DigitalGaugeConfig x:Key="Config" HasClock="False" HasExternalTemp="False" UseDegreesF="True" UseMPH="True" UsePsi="True" MaxBoost="0" MinBoost="0" MaxSpeed="000" HasAbsLight="False" HasStmLight="False" HasTcsLight="False" HasGAccelX="False" HasGAccelY="False" HasShiftLights="True" HasTextTach="True" HasLapPlaceInfo="True" HasTextBoost="False" HasTextGAccel="False" HasTextOdometer="False" HasTextFuel="False" MaxFuel="0" MaxGear="0" MaxRpm="{max_rpm}"></local:DigitalGaugeConfig>

		<Storyboard x:Key="Start Up Animation">
			<DoubleAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Opacity)" Storyboard.TargetName="Start_Up_Mask">
				<EasingDoubleKeyFrame KeyTime="0" Value="1"/>
				<EasingDoubleKeyFrame KeyTime="0:0:1" Value="0"/>
			</DoubleAnimationUsingKeyFrames>
		</Storyboard>
		<Storyboard x:Key="Shift Lights Progress">
{chr(10).join(prog)}
		</Storyboard>
		<Storyboard x:Key="Shift Lights Flash" RepeatBehavior="Forever">
{chr(10).join(flash)}
		</Storyboard>
	</Page.Resources>
	<Page.Triggers>
		<EventTrigger RoutedEvent="FrameworkElement.Loaded" SourceName="LayoutRoot">
			<BeginStoryboard Storyboard="{{StaticResource Shift Lights Flash}}"/>
		</EventTrigger>
	</Page.Triggers>

	<Canvas x:Name="LayoutRoot" Background="Transparent" Width="1280" Height="720">
		<VisualStateManager.VisualStateGroups>
			<VisualStateGroup x:Name="NightDaySplit">
				<VisualState x:Name="Day"/>
				<VisualState x:Name="Night"/>
			</VisualStateGroup>
		</VisualStateManager.VisualStateGroups>
		<Canvas x:Name="Background" Height="720" Width="1280">
			<Rectangle Fill="#FF05060A" Height="720" Canvas.Left="0" Canvas.Top="0" Width="1280"/>
			<Rectangle Fill="#FF1E2A5A" Height="6" Canvas.Left="40" Canvas.Top="128" Width="1200"/>
			<Rectangle Fill="#FF1E2A5A" Height="420" Canvas.Left="438" Canvas.Top="170" Width="6"/>
			<Rectangle Fill="#FF1E2A5A" Height="420" Canvas.Left="836" Canvas.Top="170" Width="6"/>
		</Canvas>
		<Canvas x:Name="Shift_Lights" Height="76" Canvas.Left="42" Canvas.Top="30">
			<Canvas x:Name="OFF" Canvas.Left="0" Canvas.Top="0">
{row("Off", 1)}
			</Canvas>
			<Canvas x:Name="ON" Canvas.Left="0" Canvas.Top="0" Opacity="1">
{row("On", 0)}
			</Canvas>
			<Canvas x:Name="FLASHING" Canvas.Left="0" Canvas.Top="0" Opacity="1" Visibility="Hidden">
{row("Flashing", 1)}
			</Canvas>
		</Canvas>
		<Canvas x:Name="Text" Height="720" Width="1280">
{text("Text_Speed", "Speed", 20, 300, 400, 150)}
{label("MPH", 20, 480, 400, 54)}
{text("Text_Gear", "Gear", 444, 150, 392, 400, fg="#FFFFD200")}
{rpm}
{label("RPM", 860, 480, 400, 54)}
{label("RED BULL RB22", 0, 630, 1280, 46)}
			<TextBlock x:Name="Text_Place_Min" Visibility="Hidden" TextAlignment="Left" Canvas.Left="60" Canvas.Top="630" Width="190" FontSize="60" Style="{{StaticResource TextBlockStyle}}">
				<Run Text="P"/>
				<Run Text="{{Binding CurPlace}}"/>
			</TextBlock>
		</Canvas>
		<Rectangle x:Name="Start_Up_Mask" Fill="Black" Height="720" Width="1280" Canvas.Left="0" Canvas.Top="0" Opacity="0"/>

		<!-- Storyboard binding controllers -->
		<local:StoryboardController SeekPct="{{Binding Tach}}" Target="{{StaticResource Shift Lights Progress}}"/>
	</Canvas>
</Page>
'''


def check_xaml(text):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(text)
    names = set(re.findall(r'x:Name="([^"]+)"', text))
    targets = set(re.findall(r'Storyboard\.TargetName="([^"]+)"', text))
    assert targets <= names, f'storyboard targets without an element: {sorted(targets - names)}'
    keys = set(re.findall(r'x:Key="([^"]+)"', text)); used = set(re.findall(r'StaticResource ([^}]+)\}', text))
    assert used <= keys, sorted(used - keys)
    srcs = sorted(set(re.findall(r'Source="([^"]+)"', text)))
    return dict(elements=len(names), storyboard_targets=len(targets), images=srcs)


# ================================================================== package
def apply(pkg, ow_f1_path, version=None):
    pkg = Path(pkg); report = {}
    archive = pkg / 'media' / 'cars' / f'{MEDIA}.zip'
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist(); entries = {i.filename: z.read(i) for i in infos}
    low = {n.lower(): n for n in entries}
    wheel_lf = next(n for n in entries if n.lower().endswith('_wheellf.modelbin'))
    wheel_lr = wheel_lf[:-len('LF.modelbin')] + 'LR.modelbin'
    assert wheel_lr.lower() not in low, 'already applied'
    # textures: the model's tyre (sidewall.007, 4096 -> 1024) and a rubber gloss (matte)
    import trimesh
    from PIL import Image
    s = trimesh.load(HERE / 'model.glb', force='scene')
    img = next(g.visual.material.baseColorTexture for g in s.geometry.values() if g.visual.material.name == 'sidewall.007')
    T1024 = open(REPO / 'tex' / 'PEU_207SEHDi_08_Interior_DIFF_7b3d1f55-6273-410e-adf0-6ff29a14784f.swatchbin', 'rb').read()
    T512 = open(REPO / 'tex' / 'PEU_207SEHDi_08_Rad_Fixed_DiffuseFrontReflector_fa6144d2-c78f-41d2-9eaa-2f61cb81d1dc.swatchbin', 'rb').read()
    def texture(tag, im, size, tpl):
        import uuid
        g = uuid.UUID(hashlib.md5(f'{MEDIA}/{tag}'.encode()).hexdigest())
        im = im.convert('RGB').resize((size, size), Image.LANCZOS)
        data = bytearray(swatch.write_like(tpl, np.dstack([np.array(im), np.full((size, size), 255, np.uint8)])))
        data[0x30:0x40] = g.bytes_le
        fn = f'{tag}_{g.hex[:12]}.swatchbin'; entries[f'Textures/custom/Swatches/{fn}'] = bytes(data)
        return f'Game:\\Media\\cars\\{MEDIA}\\Textures\\custom\\Swatches\\{fn}'
    tyre_tex = texture('source_tyre', img, 1024, T1024)
    tyre_gloss = texture('tyre_gloss', Image.new('RGB', (512, 512), (55, 55, 55)), 512, T512)
    tpl = open(REPO / 'f1' / 'matI_lod1.bin', 'rb').read()
    tyres = source_tyres()
    base = entries[wheel_lf]
    entries[wheel_lf] = add_tyre(base, tyres['F'], tyre_tex, tyre_gloss, tpl)
    entries[wheel_lr] = add_tyre(base, tyres['R'], tyre_tex, tyre_gloss, tpl)
    report['tyres'] = {k: {kk: v for kk, v in t.items() if kk not in ('P', 'N', 'UV', 'T')} | {'triangles': len(t['T'])} for k, t in tyres.items()}
    # carbin: rear wheels draw the rear wheel part
    cname = next(n for n in entries if n.lower().endswith('.carbin'))
    raw = entries[cname]; c = carbin.read_carbin(raw); assert carbin.write_carbin(c) == raw, 'carbin round trip'
    moved = 0
    for pt in c['parts']:
        for m in pt['part']['models']:
            if m['type'] == 'Wheels' and m['bone_name'] in ('spindleLR', 'spindleRR'):
                assert m['path'].endswith('_wheellf.modelbin'); m['path'] = m['path'][:-len('lf.modelbin')] + 'lr.modelbin'; moved += 1
    assert moved == 2, moved
    # the steering wheel: the cockpit visibility of the Williams FW24's (and its other cabin parts'); the Charger
    # donor's entry left it out of the cockpit view (Owen 6 Nov: steering wheel isn't there)
    sw_models = [m for pt in c['parts'] for m in pt['part']['models'] if m['path'].endswith('steeringwheel_a.modelbin')]
    assert len(sw_models) == 1
    sw_models[0]['draw_groups'] = 31; sw_models[0]['u11'] = '0101' + '00' * 16; sw_models[0]['lods'] = 63
    entries[cname] = carbin.write_carbin(c)
    # steering wheel screen + page + LED images
    sw = next(n for n in entries if n.lower().endswith('interior/dash/steeringwheel_a.modelbin'))
    entries[sw], report['steering'] = rebuild_steering(entries[sw])
    entries[sw] = all_lods(entries[sw])
    report['driver_wheel_track'] = driver_wheel_track(entries)
    xaml = page_xaml(); report['page'] = check_xaml(xaml)
    ui = next(n for n in entries if n.lower() == f'ui/{MEDIA.lower()}.xaml')
    entries[ui] = xaml.encode('utf-8')
    for k, v in led_images().items(): entries[k] = v
    for src in report['page']['images']:
        want = 'UI/Textures/' + src.rsplit('/', 1)[1][:-4] + '.swatchbin'
        assert want in entries, want
    order = [i.filename for i in infos] + [n for n in entries if n not in {i.filename for i in infos}]
    tmp = archive.with_suffix('.tmp')
    with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for n in order:
            info = next((i for i in infos if i.filename == n), None)
            if info is not None: z.writestr(info, entries[n])
            else:
                zi = zipfile.ZipInfo(n, date_time=(1980, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, entries[n])
    tmp.replace(archive)
    # the empty library tyre and the database
    # 0.1.14: the model's tyre (in the wheel part) is not drawn once the wheel spins fast (Owen 6 Nov: only the tyres
    # vanish, rims stay). The game's plain OW_F1 slick stays as the library tyre underneath, so a tyre is always there.
    lib = pkg / 'media' / 'cars' / '_library' / 'scene' / 'tires'; lib.mkdir(parents=True, exist_ok=True)
    base = Path(ow_f1_path).read_bytes()
    if WHITEWALL and Path(WHITEWALL).exists(): base = red_band(Path(WHITEWALL).read_bytes()); report['library_tyre'] = 'OW_whiteWall, red band'
    (lib / f'tire_{TYRE_NAME}.zip').write_bytes(narrow_library_tyre(base))
    dbp = pkg / 'database.json'; db = json.loads(dbp.read_text())
    rows = db['tables']['List_UpgradeTireCompound']['insert']
    for r in rows:
        assert r['TireModelName'] == 'OW_F1', r['TireModelName']; r['TireModelName'] = TYRE_NAME
    # cockpit camera 10 cm lower (Owen 6 Nov: too high); the Williams FW24 uses this field too (+0.06)
    cam = db['tables']['CameraOverrides']['insert'][0]; cam['CamCockpitOffsetY'] = round(cam['CamCockpitOffsetY'] - 0.10, 3)
    report['cockpit_camera_offset_y'] = cam['CamCockpitOffsetY']
    dbp.write_text(json.dumps(db, indent=1) + '\n')
    if version:
        mp = pkg / 'mod.json'; mj = json.loads(mp.read_text()); mj['version'] = version; mp.write_text(json.dumps(mj, indent=1) + '\n')
    report['archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
    (pkg / 'tyres-screen-check.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('pkg'); ap.add_argument('--ow-f1', required=True); ap.add_argument('--version')
    ap.add_argument('--whitewall', help="the game's tireL_OW_whiteWall.modelbin (red-band fallback tyre)")
    a = ap.parse_args(); WHITEWALL = a.whitewall
    print(json.dumps(apply(a.pkg, a.ow_f1, a.version), indent=2))
