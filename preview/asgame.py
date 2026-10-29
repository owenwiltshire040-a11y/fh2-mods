"""As-game preview of a built car: places everything the way FH2 does, prints PASS/FAIL checks, writes a glb
(and PNGs through scan/viewer if a server is up on :8765).

usage: asgame.py built_car.zip database.json --donor DONOR.zip [--geo f1/str1_geo.pkl] [--out DIR] [--media NAME]

Placement rules (each confirmed against an in-game screenshot, see NOTES.md "GENERIC DONOR"):
 1. wheel fore/aft (z): the database — z = +/- ModelWheelbase/2 - BottomCenterWheelbasePosZ (Data_CarBody).
    Confirmed 29 Oct on the Charger donor: ModelWheelbase 3.05 -> 3.65 moved both axles 30 cm; Wheelbase alone, the
    carbin spindle transforms and the gr2 skeleton moved nothing (cars WITH Animations/suspension*.gr2, like the
    Atom, follow those animations instead and ignore all of this).
    wheel height (y): the UNMODIFIED donor's carbin wheel-spindle transforms (part type 43) — source not yet proven,
    read from the donor zip, never from the built car.
 2. wheel x: the database's ModelFront/RearTrackOuter = centre-to-centre track x 1.012.
 3. body and steering wheel: the built carbin's transforms (type 2 parts) as-is.
 4. tyre size: Data_Car rim diameter, tyre width and aspect.
"""
import sys, os, re, io, json, struct, zipfile, argparse, subprocess, pickle
import numpy as np, trimesh
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [f'{ROOT}/fh2re', f'{ROOT}/tex']
from geometry import Part
from body_swap import material_names
from gltf_bridge import decode_group
from carbin import read_carbin
import swatch

TRACK_K = 1.012                     # ModelTrackOuter / centre-to-centre track (Atom 1.805 for 1.784, 207 confirmed)
TOL_WHEEL = 0.03                    # m, wheel centre vs the body's intended axle point

ap = argparse.ArgumentParser()
ap.add_argument('car'); ap.add_argument('database'); ap.add_argument('--donor', required=True)
ap.add_argument('--geo', default=f'{ROOT}/f1/str1_geo.pkl', help='str1_geo.pkl with the intended wheel centres')
ap.add_argument('--out', default=None); ap.add_argument('--media', default=None)
ap.add_argument('--no-render', action='store_true')
A = ap.parse_args()
out_dir = os.path.abspath(A.out or os.path.dirname(os.path.abspath(A.car))); os.makedirs(out_dir, exist_ok=True)

fails = []
def check(name, ok, detail=''):
    print(f'  [{"PASS" if ok else "FAIL"}] {name}' + (f': {detail}' if detail else ''))
    if not ok: fails.append(name)
def warn(msg): print(f'  [WARN] {msg}')

def carbin_of(z):
    n = next(n for n in z.namelist() if n.lower().endswith('.carbin'))
    return read_carbin(z.read(n)), re.sub(r'\.carbin$', '', n.split('/')[-1], flags=re.I)

def spindles(carb):
    """{corner: (x, y, z)} from the wheel parts' model transforms (type 43), corner = lf/rf/lr/rr"""
    S = {}
    for pt in carb['parts']:
        if pt['part']['type'] != 43: continue
        for m in pt['part']['models']:
            S[m['bone_name'].lower()[-2:]] = np.array(m['transform'][12:15], float)
    return S

car = zipfile.ZipFile(A.car); names = {n.lower(): n for n in car.namelist()}
donor = zipfile.ZipFile(A.donor)
carb, media = carbin_of(car); dcarb, dmedia = carbin_of(donor)
MEDIA = A.media or media
db = json.load(open(A.database))
print(f'car {media} (donor {dmedia}), database {os.path.basename(A.database)}')

# ---------------------------------------------------------------- donor spindles: wheel y, and a reference for z
W_DONOR = spindles(dcarb); W_BUILT = spindles(carb)
for c in ('lf', 'rf', 'lr', 'rr'):
    if c in W_BUILT and np.abs(W_BUILT[c] - W_DONOR[c]).max() > 1e-3:
        warn(f'build changed the {c.upper()} spindle transform {W_BUILT[c].round(3)} (donor {W_DONOR[c].round(3)}): '
             'the game does not read it (tested 29 Oct); the preview uses the donor values for y')
dzf = (W_DONOR['lf'][2] + W_DONOR['rf'][2]) / 2; dzr = (W_DONOR['lr'][2] + W_DONOR['rr'][2]) / 2
print(f'  donor spindles: front z {dzf:.3f} y {(W_DONOR["lf"][1] + W_DONOR["rf"][1]) / 2:.3f}, '
      f'rear z {dzr:.3f} y {(W_DONOR["lr"][1] + W_DONOR["rr"][1]) / 2:.3f}  (wheelbase {dzf - dzr:.3f}, for reference only)')

# ---------------------------------------------------------------- rules 1 + 2: wheelbase and track from the database
def db_row(table, key, val):
    t = db['tables'].get(table, {})
    for r in t.get('insert', []):
        if r.get(key) == val: return r
    for u in t.get('update', []):
        if u.get('where', {}).get(key) == val: return u.get('set', {})
    return None
car_row = next((r for r in db['tables']['Data_Car']['insert'] if r.get('MediaName', '').lower() == MEDIA.lower()), None)
check('database has the car', car_row is not None, MEDIA)
body = db_row('Data_CarBody', 'Id', car_row['Id'] * 1000) if car_row else None
check('database has the car body', body is not None and 'ModelFrontTrackOuter' in body)
tf = body['ModelFrontTrackOuter'] / TRACK_K; tr = body['ModelRearTrackOuter'] / TRACK_K
mid = -body.get('BottomCenterWheelbasePosZ', 0.0); zf = mid + body['ModelWheelbase'] / 2; zr = mid - body['ModelWheelbase'] / 2
print(f'  from DB: ModelWheelbase {body["ModelWheelbase"]:.3f} about z {mid:+.3f} -> front z {zf:.3f} rear z {zr:.3f}; '
      f'track front {tf:.3f} rear {tr:.3f} (centre-to-centre); physics Wheelbase {body["Wheelbase"]:.3f}')
if abs(body['Wheelbase'] - body['ModelWheelbase']) > 0.02: warn('Wheelbase (physics) and ModelWheelbase (drawn) differ')
GAME = {'lf': np.array([-tf / 2, W_DONOR['lf'][1], zf]), 'rf': np.array([tf / 2, W_DONOR['rf'][1], zf]),
        'lr': np.array([-tr / 2, W_DONOR['lr'][1], zr]), 'rr': np.array([tr / 2, W_DONOR['rr'][1], zr])}

# ---------------------------------------------------------------- checks against the body's intended axle points
G = pickle.load(open(A.geo, 'rb')) if os.path.exists(A.geo) else None
if G:
    want = {'lf': G['wheels']['HUB_LF'], 'rf': G['wheels']['HUB_RF'], 'lr': G['wheels']['HUB_LR'], 'rr': G['wheels']['HUB_RR']}
    for c in ('lf', 'rf', 'lr', 'rr'):
        d = GAME[c] - want[c]['centre']
        check(f'wheel {c.upper()} on the body axle point', np.abs(d).max() <= TOL_WHEEL,
              f'game {GAME[c].round(3)} intended {want[c]["centre"].round(3)} delta {d.round(3)}')
    ground = G['ground']
    for c in ('lf', 'rr'):
        bottom = GAME[c][1] - want[c]['radius']
        check(f'tyre {c.upper()} bottom on the ground', abs(bottom - ground) <= 0.02, f'tyre bottom {bottom:.3f} body ground {ground:.3f}')
    V = np.concatenate([p['V'] for ps in G['parts'].values() for p in ps])
    check('body floor not below the tyres', V[:, 1].min() >= ground - 0.02, f'floor {V[:, 1].min():.3f} ground {ground:.3f}')
    # the uprights (the HUB_* parts' disc, hub and caliper; the rest of each HUB is the STR1's own wheel) must reach
    # the wheel the game draws: upright end x vs the wheel's inner face
    UPRIGHT = {'DISK', 'FW15C_MECANICS', 'Material_98', 'MCLHUB'}
    for c, hub in (('lf', 'HUB_LF'), ('rf', 'HUB_RF'), ('lr', 'HUB_LR'), ('rr', 'HUB_RR')):
        hv = np.concatenate([p['V'] for p in G['parts'][hub] if p['mat'] in UPRIGHT])
        inner = GAME[c][0] - np.sign(GAME[c][0]) * 0.15        # ~half an F1 tyre width inboard of the centre
        reach = hv[:, 0].max() if GAME[c][0] > 0 else hv[:, 0].min()
        ok = (reach >= inner - 0.05) if GAME[c][0] > 0 else (reach <= inner + 0.05)
        check(f'upright {hub} reaches the wheel', ok, f'arm end x {reach:.3f} wheel inner face {inner:.3f}')
else:
    warn('no geometry pickle: wheel-vs-body checks skipped')

# ---------------------------------------------------------------- render: body/steering as built, wheels per the rules
if not A.no_render:
    texcache = {}
    def tex_of(mat_blob):
        s = bytes(mat_blob['data']).lower()
        m = re.search(rb'game:\\media\\cars\\' + MEDIA.lower().encode() + rb'\\textures\\[ -~]+?\\swatches\\([ -~]+?)\.swatchbin', s)
        if not m: return None
        key = next((n for n in names if n.endswith(m.group(1).decode() + '.swatchbin')), None)
        if key is None: return None
        if key not in texcache:
            d = car.read(names[key]); w = struct.unpack_from('<H', d, 0x40)[0]
            try: texcache[key] = Image.fromarray(swatch.decode_level(d[0x53:], 0, w, w, '2d')[..., :3])
            except Exception: texcache[key] = None
        return texcache[key]
    def skel_world(p):
        sk = [b for b in p.b.blobs if b['tag'] == 'Skel'][0]; d = bytes(sk['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2; M, par = [], []
        for _ in range(n):
            L = struct.unpack_from('<I', d, o)[0]; o += 4; pa = struct.unpack_from('<h', d, o + L)[0]; o += L + 6
            M.append(np.frombuffer(d[o:o + 64], '<f4').reshape(4, 4).astype(float)); par.append(pa); o += 64
        W = []
        for i in range(n): W.append(M[i] @ W[par[i]] if par[i] >= 0 else M[i])
        return W
    def add_model(scene, path, T, colour=(90, 90, 96), use_bones=False):
        rel = re.sub(r'^game:\\media\\cars\\[^\\]+\\', '', path.lower()).replace('\\', '/')
        if rel not in names: return 0
        p = Part(car.read(names[rel])); nm = material_names(p)
        mats = {struct.unpack('<i', p.b.meta(bl, 'Id  '))[0]: bl for bl in p.b.blobs if bl['tag'] == 'MatI'}
        try: W = skel_world(p)
        except Exception: W = None
        n = 0
        for r in p.render:
            if not struct.unpack_from('<H', r['blob']['data'], 4)[0] & 1 or len(set(r['indices'])) < 4: continue
            d, _ = decode_group(p, r['group']); P = d['POSITION'][:, :3].astype(float)
            b = struct.unpack_from('<h', r['blob']['data'], 2)[0]
            if use_bones and W is not None and b > 1: P = P @ W[b][:3, :3] + W[b][3, :3]
            P = P @ T[:3, :3] + T[3, :3]
            mm = trimesh.Trimesh(P * [-1, 1, 1], np.array(r['indices']).reshape(-1, 3)[:, ::-1], process=False)
            img = tex_of(mats[struct.unpack_from('<h', r['blob']['data'], 0)[0]])
            if img is not None and 'TEXCOORD0' in d:
                uv = d['TEXCOORD0'].copy(); uv[:, 1] = 1 - uv[:, 1]; mm.visual = trimesh.visual.TextureVisuals(uv=uv, image=img)
            else:
                mname = nm.get(id(r['blob'])) or ''
                mm.visual.face_colors = list(colour) + [255] if 'tire' not in mname and 'rubber' not in mname else [30, 30, 32, 255]
            scene.add_geometry(mm); n += 1
        return n
    sc = trimesh.Scene(); n_body = n_wheel = 0
    for pt in carb['parts']:
        typ = pt['part']['type']
        for m in pt['part']['models']:
            T = np.array(m['transform'], float).reshape(4, 4)
            if typ == 43: continue                                   # rule 4: the game draws the tyre itself (below)
            if typ == 4:                                             # brakes: at the game's wheel position
                c = m['bone_name'].lower()[-2:]
                if c in GAME: T = T.copy(); T[3, :3] += GAME[c] - W_BUILT.get(c, GAME[c])
                n_wheel += add_model(sc, m['path'], T, (150, 150, 155))
            else:
                n_body += add_model(sc, m['path'], T, use_bones='steering' in m['path'].lower())
    # rule 4 (to confirm against a side-on screenshot): tyre size from Data_Car — radius = rim/2 + width x aspect,
    # width from the DB; the car zip's wheel modelbin is only a normalised rim the game scales to the rim diameter
    for c in GAME:
        f = c.endswith('f'); pre = 'Front' if f else 'Rear'
        rim_in, w_mm, asp = car_row[f'{pre}WheelDiameterIN'], car_row[f'{pre}TireWidthMM'], car_row[f'{pre}TireAspect']
        R = rim_in * 0.0254 / 2 + w_mm * asp / 100 / 1000; Wd = w_mm / 1000
        tyre = trimesh.creation.cylinder(radius=R, height=Wd, sections=48)
        tyre.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))     # axis along x
        tyre.apply_translation(GAME[c] * [-1, 1, 1]); tyre.visual.face_colors = [40, 40, 42, 255]
        rim = trimesh.creation.cylinder(radius=rim_in * 0.0254 / 2, height=Wd + 0.004, sections=48)
        rim.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
        rim.apply_translation(GAME[c] * [-1, 1, 1]); rim.visual.face_colors = [170, 170, 175, 255]
        sc.add_geometry(tyre); sc.add_geometry(rim); n_wheel += 2
        if c == 'lf': print(f'  tyres from DB: front R {R:.3f} W {Wd:.3f}', end='')
        if c == 'lr': print(f', rear R {R:.3f} W {Wd:.3f}')
    glb = os.path.join(out_dir, f'{MEDIA}_asgame.glb'); sc.export(glb)
    print(f'  rendered {n_body} body + {n_wheel} wheel/brake meshes -> {glb}')
    viewer = f'{ROOT}/scan/viewer'
    try:
        import shutil; shutil.copy(glb, f'{viewer}/asgame.glb')
        png = os.path.join(out_dir, f'{MEDIA}_asgame.png')
        subprocess.run(['node', 'shot.js', 'asgame.glb', png, json.dumps([[0, 9, 0.01], [7, 1.5, 0.1], [4.5, 2, 5]]),
                        json.dumps([0, 0.4, float((zf + zr) / 2)])], cwd=viewer, check=True, timeout=240, capture_output=True)
        print(f'  shots -> {png}')
    except Exception as e:
        warn(f'no PNG (viewer server on :8765 needed: cd scan/viewer && python3 -m http.server 8765): {str(e)[:80]}')

print('RESULT', 'FAIL ' + ', '.join(fails) if fails else 'PASS')
sys.exit(1 if fails else 0)
