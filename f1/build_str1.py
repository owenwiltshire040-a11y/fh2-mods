"""Toro Rosso STR1 (2006) on the Ariel Atom 500 V8's media.

Body, wings, cockpit tub, suspension arms and steering wheel: CTDP's STR1 model (via an Assetto Corsa conversion,
Sketchfab upload 'acfl_2006_str'), used for Owen's personal mod with CTDP's permission; textures kept (livery).
The Atom's panels, lights, engine, exhaust, suspension and cabin are dropped; its wheels, brakes and steering
wheel bone stay and move to the STR1's positions.
usage: build_str1.py donor_STR_STR1_06.zip out.zip
"""
import sys, zipfile, struct, pickle, uuid, re, io, json
import numpy as np
from PIL import Image
sys.path.insert(0, '../fh2re'); sys.path.insert(0, '../tex'); sys.path.insert(0, '.')
from geometry import Part
from body_swap import set_group, blank_group, material_names
from gltf_bridge import decode_group
from carbin import read_carbin, write_carbin
from modelbin import Bundle
import swatch, fhmat

SRC, OUT = sys.argv[1], sys.argv[2]
MEDIA = 'STR_STR1_06'
src = zipfile.ZipFile(SRC); names = {n.lower(): n for n in src.namelist()}
G = pickle.load(open('str1_geo.pkl', 'rb')); parts = G['parts']; wheels = G['wheels']
glb = open('src/nefolder.glb', 'rb').read()
_L = struct.unpack_from('<I', glb, 12)[0]; GJ = json.loads(glb[20:20 + _L]); BIN0 = 20 + _L + 8
def glb_image(i):
    bv = GJ['bufferViews'][GJ['images'][i]['bufferView']]; o = BIN0 + bv.get('byteOffset', 0)
    return Image.open(io.BytesIO(glb[o:o + bv['byteLength']])).convert('RGB')
replaced, added = {}, {}

# ---------------------------------------------------------------- textures (BC7, written on the game's own layouts)
T1024 = open('../tex/PEU_207SEHDi_08_Interior_DIFF_7b3d1f55-6273-410e-adf0-6ff29a14784f.swatchbin', 'rb').read()
T512 = open('../tex/PEU_207SEHDi_08_Rad_Fixed_DiffuseFrontReflector_fa6144d2-c78f-41d2-9eaa-2f61cb81d1dc.swatchbin', 'rb').read()
def make_texture(tag, img, size):
    g = uuid.uuid4(); tpl = T1024 if size == 1024 else T512
    img = img.resize((size, size), Image.LANCZOS)
    if tag in BRIGHTEN:     # the game's textured material darkens: lift the livery (gamma + gain) to compensate
        a = np.asarray(img).astype(np.float32) / 255; img = Image.fromarray((np.clip((a ** 0.75) * 1.35, 0, 1) * 255).astype(np.uint8))
    rgba = np.dstack([np.array(img), np.full((size, size), 255, np.uint8)])
    data = bytearray(swatch.write_like(tpl, rgba)); data[0x30:0x40] = g.bytes_le
    fn = f'{MEDIA}_{tag}_{g}.swatchbin'
    added[f'Textures/str1/Swatches/{fn}'] = bytes(data)
    return f'Game:\\Media\\cars\\{MEDIA}\\Textures\\str1\\Swatches\\{fn}'
BRIGHTEN = {'carbody', 'extra0', 'wing', 'cockpit', 'swheel', 'light'}
TEX = {   # name: (glb image, size)
    'carbody': (11, 1024), 'extra0': (12, 1024), 'wing': (9, 1024), 'carbon': (10, 1024), 'cockpit': (15, 1024),
    'mech': (0, 512), 'caliper': (1, 512), 'light': (18, 512), 'swheel': (20, 512)}
PATH = {k: make_texture(k, glb_image(i), s) for k, (i, s) in TEX.items()}
GLOS = make_texture('gloss', Image.new('RGB', (512, 512), (150, 150, 150)), 512)
print('textures:', len(added))
TPL_MATI = open('matI_lod1.bin', 'rb').read()      # the game's textured 'interior_lod1' instance (DIFF + GLOS)

# which STR1 material draws with which texture (None: one of the donor part's own plain materials)
MAT_TEX = {'WCCARBODY': 'carbody', 'WCEXTRA0': 'extra0', 'WCWING': 'wing', 'CARBFBD': 'carbon',
           'CARBFBDNOSPEC': 'carbon', 'COCKPIT': 'cockpit', 'FW15C_MECANICS': 'mech', 'Material_98': 'caliper',
           'REAR_LIGHT': 'light', 'TR06WHEEL0': 'swheel', 'COCKPITSCREWS': 'mech'}

def soup(tops, skip_mats=()):
    """{texture or plain key: (V, N, UV)} for the listed top-level model parts"""
    by = {}
    for t in tops:
        for p in parts[t]:
            m = p['mat']
            if m in skip_mats: continue
            key = MAT_TEX.get(m, 'mirror' if m == 'MIRROR' else 'black')
            uv = p['UV'].copy(); uv[:, 1] = 1 - uv[:, 1]              # glTF -> top-left image origin
            by.setdefault(key, []).append((p['V'], p['N'], uv))
    return {k: tuple(np.concatenate([x[i] for x in v]) for i in range(3)) for k, v in by.items()}

def two_sided(V, N, UV):
    n = len(V); T = np.arange(n).reshape(-1, 3)
    return (np.r_[V, V], np.r_[N, -N], np.r_[UV, UV], np.r_[T, T[:, [0, 2, 1]] + n].reshape(-1))

def bright_uv(p):
    best, uv = -9, None
    for gid in p.group_order:
        d, _ = decode_group(p, gid)
        if 'NORMAL0' not in d: continue
        k = int(np.argmax(d['NORMAL0'][:, 1]))
        if d['NORMAL0'][k, 1] > best:
            best, uv = d['NORMAL0'][k, 1], {j: d[f'TEXCOORD{j}'][k] for j in (1, 2, 3, 4) if f'TEXCOORD{j}' in d}
    return uv

def fill(path, tops, textured_like, plain, skip_mats=(), xform=None):
    """put the parts `tops` into the donor part at `path`. textured_like: {group: template material} whose
    meshes (every LOD) are cloned per texture; plain: {key: (group, donor material)} for untextured bits."""
    p = Part(src.read(names[path])); uvc = bright_uv(p); nm = material_names(p)
    S = soup(tops, skip_mats)
    if xform: S = {k: (xform(V), xform(N, True), UV) for k, (V, N, UV) in S.items()}
    tex_keys = [k for k in S if k in PATH]
    plan = {}                                    # group -> {material name: key}
    for gid, like_mat in textured_like.items():
        likes = [r for r in p.render if r['group'] == gid and nm[id(r['blob'])] == like_mat]
        for k in tex_keys:
            mname = f'str1_{k}'
            if not any(nm.get(id(r['blob'])) == mname for r in p.render):
                mid = fhmat.add_material(p, mname, fhmat.retexture(TPL_MATI, [PATH[k], GLOS]), [PATH[k], GLOS])
            else:
                mid = next(struct.unpack_from('<h', r['blob']['data'], 0)[0] for r in p.render if nm.get(id(r['blob'])) == mname)
            for r in likes: fhmat.add_mesh(p, r, mid)
            plan.setdefault(gid, {})[mname] = k
    for k, (gid, mat) in plain.items():
        if k in S: plan.setdefault(gid, {})[mat] = k
    for gid in p.group_order:
        if gid not in plan: blank_group(p, gid); continue
        Ps, Ns, UVs, by, base = [], [], [], {}, 0
        for mname, k in plan[gid].items():
            V, N, UV, I = two_sided(*S[k])
            Ps.append(V); Ns.append(N); UVs.append(UV); by[mname] = I + base; base += len(V)
        geo = dict(P=np.concatenate(Ps), N=np.concatenate(Ns), UV=np.concatenate(UVs), UVconst=uvc)
        set_group(p, gid, geo, by)
    out = p.build(); Part(out)
    print(f'  {path.split("/")[-1]}: ' + ', '.join(f'{k} {len(v[0]) // 3}' for k, v in S.items()))
    return out

# ---------------------------------------------------------------- body: everything but wheels and steering wheel
BODY_TOPS = [t for t in parts if not t.startswith('HUB_') and t not in ('STEER_HR', 'm_0', 'm_1')]
replaced['scene/exterior/platform/body_a.modelbin'] = fill('scene/exterior/platform/body_a.modelbin', BODY_TOPS,
    textured_like={1: 'carpaint_livery', 3: 'metalpainted_001'},
    plain={'black': (0, 'blkplastic_rgh_mgl'), 'mirror': (0, 'aluminum_satin')})

# ---------------------------------------------------------------- steering wheel, on its bone
SW = parts['STEER_HR']
swP = np.concatenate([p['V'] for p in SW]); SW_CENTRE = (swP.min(0) + swP.max(0)) / 2
skel = Bundle.read(src.read(names[f'scene/{MEDIA.lower()}_skeleton.modelbin']))
def bones(b):
    for bl in b.blobs:
        if bl['tag'] != 'Skel': continue
        d = bl['data']; n = struct.unpack_from('<H', d, 0)[0]; o = 2; out = {}
        for _ in range(n):
            L = struct.unpack_from('<I', d, o)[0]; o += 4; bn = bytes(d[o:o + L]).decode(); o += L + 6
            out[bn] = (o, np.array(struct.unpack_from('<16f', d, o)).reshape(4, 4)); o += 64
        return out
B_SW = bones(skel)['boneSteeringWheelSpindle'][1]
print('steering bone was at', B_SW[3, :3].round(3), ' STR1 wheel centre', SW_CENTRE.round(3))
B3 = B_SW[:3, :3]
def to_bone(V, is_normal=False):
    return V @ B3.T if is_normal else (V - SW_CENTRE) @ B3.T
replaced['scene/interior/dash/steeringwheel_a.modelbin'] = fill('scene/interior/dash/steeringwheel_a.modelbin', ['STEER_HR'],
    textured_like={0: 'carpet_001'}, plain={'black': (0, 'metalpainted_001'), 'mirror': (0, 'metalpainted_001')},
    xform=to_bone)

# ---------------------------------------------------------------- skeleton: steering spindle to the STR1 wheel (every copy)
# Seen in game: the wheels follow the suspension bones and the database's wheelbase doesn't move them. So the four
# top-level suspension bones (children of root) move to the STR1's axles: front +0.343 m, rear -0.363 m.
AXLE_SHIFT = {'boneSuspensionLF': wheels['HUB_LF']['centre'][2] - 1.186, 'boneSuspensionRF': wheels['HUB_RF']['centre'][2] - 1.186,
              'boneSuspensionLR': wheels['HUB_LR']['centre'][2] + 1.158, 'boneSuspensionRR': wheels['HUB_RR']['centre'][2] + 1.158}
print('axle shifts', {k: round(float(v), 3) for k, v in AXLE_SHIFT.items()})
def patch_skel(data):
    b = Bundle.read(data); changed = False
    for bl in b.blobs:
        if bl['tag'] != 'Skel': continue
        d = bytearray(bl['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2
        for _ in range(n):
            L = struct.unpack_from('<I', d, o)[0]; o += 4; bn = bytes(d[o:o + L]).decode(); o += L + 6
            if bn == 'boneSteeringWheelSpindle':
                struct.pack_into('<3f', d, o + 48, *SW_CENTRE); changed = True
            if bn in AXLE_SHIFT:          # the corner's whole suspension chain (and its wheel) moves fore/aft
                t = list(struct.unpack_from('<3f', d, o + 48)); t[2] += AXLE_SHIFT[bn]
                struct.pack_into('<3f', d, o + 48, *t); changed = True
            o += 64
        bl['data'] = d
    return b.write() if changed else data

# ---------------------------------------------------------------- carbin: keep body, steering wheel, wheels, brakes
carb = read_carbin(src.read(f'{MEDIA}.carbin'))
KEEP = {'body_a.modelbin', 'steeringwheel_a.modelbin'}
removed = []
for pt in carb['parts']:
    ms = pt['part']['models']; keep = []
    for m in ms:
        fn = m['path'].lower().split('\\')[-1]
        if pt['part']['type'] in (4, 43) or fn in KEEP: keep.append(m)
        else: removed.append(fn)
    pt['part']['models'] = keep
for up in carb['upgradable_parts']:
    removed += [sm['model']['path'].lower().split('\\')[-1] for sm in up.get('shared_models', [])]
    up['shared_models'] = []
# wheels, rotors and calipers: from the Atom's corners to the STR1's (wheelbase 3.05 m, narrower track)
CORNER = {'lf': wheels['HUB_LF']['centre'], 'rf': wheels['HUB_RF']['centre'], 'lr': wheels['HUB_LR']['centre'], 'rr': wheels['HUB_RR']['centre']}
moved = []
for pt in carb['parts']:
    if pt['part']['type'] not in (4, 43): continue
    for m in pt['part']['models']:
        t = list(m['transform']); bone = m['bone_name'].lower()
        corner = bone[-2:]
        if corner not in CORNER: continue
        atom_wheel = {'lf': (-0.892, 0.182, 1.186), 'rf': (0.888, 0.182, 1.186), 'lr': (-0.907, 0.182, -1.158), 'rr': (0.907, 0.182, -1.158)}[corner]
        # seen in game: the wheels follow the skeleton's suspension bones, not these transforms (moving them changed
        # nothing). The database places the bones: track from ModelFront/RearTrackOuter, wheelbase by stretching the
        # skeleton from ModelWheelbase to Wheelbase. So the models keep the Atom's transforms.
        d = np.zeros(3)
        t[12] += d[0]; t[13] += d[1]; t[14] += d[2]; m['transform'] = t
        moved.append((m['path'].split('\\')[-1], corner, np.round(t[12:15], 3).tolist()))
print('removed', len(removed), 'parts; moved', len(moved), 'wheel/brake models')
replaced[f'{MEDIA}.carbin'.lower()] = write_carbin(carb)

# ---------------------------------------------------------------- locators: centre seat, wheel, wheel corners
loc = src.read('Locators.xml').decode('utf-8')
EYE = np.array([0.0, SW_CENTRE[1] + 0.25, SW_CENTRE[2] - 0.50])
LOC = {'carLocator_seatCamLF': EYE, 'carLocator_seatCamRF': EYE, 'carLocator_steeringWheel': SW_CENTRE,
       'carLocator_gauges': SW_CENTRE + [0, 0.03, 0.02], 'carLocator_dashboard': SW_CENTRE + [0, 0.05, 0.10],
       'carLocator_lookCloseCenter': EYE + [0, 0, 0.3], 'carLocator_lookLeft': EYE + [-0.3, 0, 0.3],
       'carLocator_lookRight': EYE + [0.3, 0, 0.3], 'carLocator_lookCloseLeft': EYE + [-0.3, 0, 0.2],
       'carLocator_lookCloseRight': EYE + [0.3, 0, 0.2],
       'paddleShiftDown': SW_CENTRE + [-0.12, 0, 0.02], 'paddleShiftUp': SW_CENTRE + [0.12, 0, 0.02],
       'carLocator_wheelLF': CORNER['lf'], 'carLocator_wheelRF': CORNER['rf'], 'carLocator_wheelLR': CORNER['lr'],
       'carLocator_wheelRR': CORNER['rr']}
def set_loc(xml, name, val):
    blk = re.search(r'(<Locator Version="3">(?:(?!</Locator>).)*?<Name value="%s"/>.*?</Locator>)' % re.escape(name), xml, re.S)
    if not blk: print('  locator not found', name); return xml
    b = blk.group(1)
    nb = re.sub(r'value\._41="[^"]+" value\._42="[^"]+" value\._43="[^"]+"',
                'value._41="%.6f" value._42="%.6f" value._43="%.6f"' % tuple(val), b)
    return xml.replace(b, nb)
for k, v in LOC.items(): loc = set_loc(loc, k, v)
replaced['locators.xml'] = loc.encode('utf-8')

# ---------------------------------------------------------------- write
out = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6)
for info in src.infolist():
    key = info.filename.lower(); data = replaced.get(key, None)
    if data is None: data = src.read(info.filename)
    if key.endswith('.modelbin'):
        try: data = patch_skel(data)
        except Exception as e: print('  skel patch skipped', key, e)
    out.writestr(zipfile.ZipInfo(info.filename, date_time=info.date_time), data, compress_type=zipfile.ZIP_DEFLATED)
for k, v in added.items():
    out.writestr(zipfile.ZipInfo(k, date_time=(2026, 10, 29, 0, 0, 0)), v, compress_type=zipfile.ZIP_DEFLATED)
out.close(); print('wrote', OUT)
