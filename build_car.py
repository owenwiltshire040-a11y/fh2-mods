"""Generic car builder on the Charger template ("generic donor", see NOTES.md): a model's body goes into the
donor's body_a (and its glass into glassF_a), everything else of the donor is dropped, the wheels are placed by the
database (ModelWheelbase / track), the driver by the skeleton gr2's steering bone + the animations' Hips track.

usage: build_car.py cars/<car>/spec.py out.zip
The spec module provides (see cars/peugeot208/spec.py): MEDIA, DONOR_ZIP (donor media renamed with make_media.py),
GEO (pickle from fh2re/objgeo.py or f1/str1_geo.py), MATERIALS {model material: ('textured', key) | ('plain', key) |
None to drop}, TEXTURES {key: (PIL image, size, brighten)}, BODY_PLAIN {plain key: (group, donor material)},
GLASS_PLAIN, BODY_TEXTURED_LIKE, STEER (wheel centre), EYE, HIPS, DRIVER_ANIMS_ZIP (or None), KEEP_PARTS.
"""
import sys, os, zipfile, struct, pickle, uuid, re, io, json, importlib.util
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [f'{HERE}/fh2re', f'{HERE}/tex', f'{HERE}/f1']
from geometry import Part
from body_swap import set_group, blank_group, material_names
from gltf_bridge import decode_group
from carbin import read_carbin, write_carbin
from modelbin import Bundle
import swatch, fhmat, granny

spec_path, OUT = sys.argv[1], sys.argv[2]
_s = importlib.util.spec_from_file_location('carspec', spec_path); S = importlib.util.module_from_spec(_s); _s.loader.exec_module(S)
MEDIA = S.MEDIA
src = zipfile.ZipFile(S.DONOR_ZIP); names = {n.lower(): n for n in src.namelist()}
G = pickle.load(open(S.GEO, 'rb')); parts = G['parts']; model_wheels = G['wheels']
# the wheel positions the game will use: the model's axle points, with x from the spec's track when it gives one
# (the database draws the tyre at +/- track/2; the carbin and gr2 wheel transforms below follow the same point)
wheels = {k: dict(v, centre=v['centre'].copy()) for k, v in model_wheels.items()}
if hasattr(S, 'PHYSICS'):
    for k, w in wheels.items():
        tr = S.PHYSICS['body']['track_front' if k.endswith('F') else 'track_rear']; w['centre'][0] = np.sign(w['centre'][0]) * tr / 2
replaced, added = {}, {}

# ---------------------------------------------------------------- textures (BC7, written on the game's own layouts)
T1024 = open(f'{HERE}/tex/PEU_207SEHDi_08_Interior_DIFF_7b3d1f55-6273-410e-adf0-6ff29a14784f.swatchbin', 'rb').read()
T512 = open(f'{HERE}/tex/PEU_207SEHDi_08_Rad_Fixed_DiffuseFrontReflector_fa6144d2-c78f-41d2-9eaa-2f61cb81d1dc.swatchbin', 'rb').read()
def make_texture(tag, img, size, brighten=False):
    g = uuid.uuid4(); tpl = T1024 if size == 1024 else T512
    img = img.convert('RGB').resize((size, size), Image.LANCZOS)
    if brighten:            # the game's textured material darkens: lift (gamma + gain) to compensate
        a = np.asarray(img).astype(np.float32) / 255; img = Image.fromarray((np.clip((a ** 0.75) * 1.35, 0, 1) * 255).astype(np.uint8))
    rgba = np.dstack([np.array(img), np.full((size, size), 255, np.uint8)])
    data = bytearray(swatch.write_like(tpl, rgba)); data[0x30:0x40] = g.bytes_le
    fn = f'{MEDIA}_{tag}_{g}.swatchbin'; added[f'Textures/{MEDIA.lower()}/Swatches/{fn}'] = bytes(data)
    return f'Game:\\Media\\cars\\{MEDIA}\\Textures\\{MEDIA.lower()}\\Swatches\\{fn}'
PATH = {k: make_texture(k, img, size, br) for k, (img, size, br) in S.TEXTURES.items()}
GLOS = make_texture('gloss', Image.new('RGB', (512, 512), (150, 150, 150)), 512)
print('textures:', len(added))
TPL_MATI = open(f'{HERE}/f1/matI_lod1.bin', 'rb').read()      # the game's textured 'interior_lod1' instance (DIFF + GLOS)

def soup(materials):
    """{texture key or plain key: (V, N, UV)} for the model materials listed (per the spec's MATERIALS map)"""
    by = {}
    for m in materials:
        plan = S.MATERIALS.get(m)
        if plan is None or m not in parts: continue
        kind, key = plan
        for p in parts[m]:
            uv = p['UV'].copy(); uv[:, 1] = 1 - uv[:, 1]
            by.setdefault(key, []).append((p['V'], p['N'], uv))
    return {k: tuple(np.concatenate([x[i] for x in v]) for i in range(3)) for k, v in by.items()}

def weld(V, N, UV):
    """index the soup: identical (position, normal, uv) corners become one vertex (the OBJ shared them anyway)"""
    # on position + normal only: SketchUp writes a fresh uv per face corner, and these parts carry no texture of their own
    key = np.round(np.c_[V, N], 4); _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return V[first], N[first], UV[first], inv.reshape(-1).astype(np.int64)

def two_sided(V, N, UV):
    V, N, UV, I = weld(V, N, UV); n = len(V); T = I.reshape(-1, 3)
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

def fill(path, materials, textured_like, plain, xform=None):
    """put the model materials into the donor part at `path`. textured_like: {group: template material} whose
    meshes (every LOD) are cloned per texture key; plain: {key: (group, donor material)} for untextured bits."""
    p = Part(src.read(names[path])); uvc = bright_uv(p); nm = material_names(p)
    Sp = soup(materials)
    if xform: Sp = {k: (xform(V), xform(N, True), UV) for k, (V, N, UV) in Sp.items()}
    tex_keys = [k for k in Sp if k in PATH]
    plan = {}
    for gid, like_mat in textured_like.items():
        likes = [r for r in p.render if r['group'] == gid and nm[id(r['blob'])] == like_mat]
        for k in tex_keys:
            mname = f'{MEDIA.lower()}_{k}'
            if not any(nm.get(id(r['blob'])) == mname for r in p.render):
                mid = fhmat.add_material(p, mname, fhmat.retexture(TPL_MATI, [PATH[k], GLOS]), [PATH[k], GLOS])
            else:
                mid = next(struct.unpack_from('<h', r['blob']['data'], 0)[0] for r in p.render if nm.get(id(r['blob'])) == mname)
            for r in likes: fhmat.add_mesh(p, r, mid)
            plan.setdefault(gid, {})[mname] = k
    for k, (gid, mat) in plain.items():
        if k in Sp: plan.setdefault(gid, {})[mat] = k
    for gid in p.group_order:
        if gid not in plan: blank_group(p, gid); continue
        Ps, Ns, UVs, by, base = [], [], [], {}, 0
        for mname, k in plan[gid].items():
            V, N, UV, I = two_sided(*Sp[k])
            Ps.append(V); Ns.append(N); UVs.append(UV); by[mname] = I + base; base += len(V)
        set_group(p, gid, dict(P=np.concatenate(Ps), N=np.concatenate(Ns), UV=np.concatenate(UVs), UVconst=uvc), by)
    out = p.build(); Part(out)
    print(f'  {path.split("/")[-1]}: ' + ', '.join(f'{k} {len(v[0]) // 3}' for k, v in Sp.items()))
    return out

# ---------------------------------------------------------------- lamps (taken out of the body, into the donor's light parts)
LIGHT_PARTS = set()
if getattr(S, 'LIGHTS', None):
    import lightbuild
    chmsl = lightbuild.centre_of(parts, S.LIGHTS['chmsl']) if 'chmsl' in S.LIGHTS else None
    lamps = lightbuild.take_lamps(parts, S.LIGHTS)
    for kind in ('head', 'tail'):
        if not any(lightbuild.EMIT[f][0] == kind for f in lamps): continue
        for side in ('l', 'r'):
            key = next(n for n in names if n.endswith(f'/{kind}light{side}_a.modelbin'))
            replaced[key] = lightbuild.build_part(src.read(names[key]), side, kind, lamps)
            LIGHT_PARTS.add(f'{kind}light{side}_a.modelbin')
    model_c = {k: lamps[f][0][lamps[f][0][:, 0] < 0].mean(0) for k, f in (('head', 'head'), ('tail', 'tail')) if f in lamps}
    replaced['lights.bin'] = lightbuild.lights_bin(src.read(names['lights.bin']), model_c, lightbuild.donor_centres(src, names),
                                                   f'game:\\media\\cars\\{MEDIA.lower()}\\', chmsl)
    print('  lamp centres (left):', {k: np.round(v, 3).tolist() for k, v in model_c.items()})

# ---------------------------------------------------------------- body and glass
body_mats = [m for m, plan in S.MATERIALS.items() if plan and plan[1] in S.BODY_PLAIN or (plan and plan[0] == 'textured')]
glass_mats = [m for m, plan in S.MATERIALS.items() if plan and plan[1] in S.GLASS_PLAIN]
replaced['scene/exterior/platform/body_a.modelbin'] = fill('scene/exterior/platform/body_a.modelbin', body_mats, S.BODY_TEXTURED_LIKE, S.BODY_PLAIN)
if glass_mats:
    replaced['scene/exterior/windows/glassf_a.modelbin'] = fill('scene/exterior/windows/glassf_a.modelbin', glass_mats, {}, S.GLASS_PLAIN)

# ---------------------------------------------------------------- the model's own rim into the donor wheel part (spins, scales with the tyre)
if getattr(S, 'RIM_MATERIALS', None):
    import rimbuild
    wpath = next(n for n in names if n.endswith('_wheellf.modelbin'))
    replaced[wpath], rim_prev = rimbuild.build_rim(src.read(names[wpath]), parts, S.RIM_MATERIALS, model_wheels['HUB_LF']['centre'],
                                                   black_materials=getattr(S, 'RIM_BLACK_MATERIALS', ()))
    try:
        import trimesh; trimesh.Trimesh(rim_prev[0] * [1, 1, 1], rim_prev[1], process=False).export(os.path.splitext(OUT)[0] + '_rim.glb')
    except Exception as e: print('  (rim preview skipped:', e, ')')

# ---------------------------------------------------------------- skeleton (modelbin copies): steering spindle to the model's wheel
SW_CENTRE = np.array(S.STEER, float)
def patch_skel(data):
    b = Bundle.read(data); changed = False
    for bl in b.blobs:
        if bl['tag'] != 'Skel': continue
        d = bytearray(bl['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2
        for _ in range(n):
            L = struct.unpack_from('<I', d, o)[0]; o += 4; bn = bytes(d[o:o + L]).decode(); o += L + 6
            if bn == 'boneSteeringWheelSpindle': struct.pack_into('<3f', d, o + 48, *SW_CENTRE); changed = True
            o += 64
        bl['data'] = d
    return b.write() if changed else data

# ---------------------------------------------------------------- skeleton .gr2: the driver's hands follow boneSteeringWheel
def patch_skel_gr2(data):
    g = granny.GR2(data); B = g.root()['Skeletons'][0]['Bones']
    sw = next(b for b in B if b['Name'] == 'boneSteeringWheel')
    M = np.array(sw['InverseWorldTransform']).reshape(4, 4); world = -M[3, :3] @ np.linalg.inv(M[:3, :3])
    granny.move_bone(g, 'boneSteeringWheel', list(SW_CENTRE - world)); print('gr2 skeleton: boneSteeringWheel', world.round(3), '->', SW_CENTRE.round(3))
    # wheel bones to the car's wheel centres (the tyre is placed by the database; the rim/brake bones should agree)
    for c in ('LF', 'RF', 'LR', 'RR'):
        tgt = wheels[f'HUB_{c}']['centre']
        for bn in (f'hub{c}', f'controlArm_{c}'):
            b = next((x for x in B if x['Name'] == bn), None)
            if b is None: continue
            M = np.array(b['InverseWorldTransform']).reshape(4, 4); w = -M[3, :3] @ np.linalg.inv(M[:3, :3])
            granny.move_bone(g, bn, list(tgt - w))
        print(f'gr2 skeleton: hub{c}/controlArm_{c} -> {np.round(tgt, 3)}')
    return g.write()
replaced[f'scene/{MEDIA.lower()}_skeleton.gr2'] = patch_skel_gr2(src.read(names[f'scene/{MEDIA.lower()}_skeleton.gr2']))

# ---------------------------------------------------------------- driver animations: seat = the Hips track (absolute car space)
drv_zip = zipfile.ZipFile(S.DRIVER_ANIMS_ZIP) if S.DRIVER_ANIMS_ZIP and os.path.exists(S.DRIVER_ANIMS_ZIP) else src
drv_names = {n.lower(): n for n in drv_zip.namelist() if n.lower().startswith('scene/drivers/')}
was = granny.track_position_constant(granny.GR2(drv_zip.read(drv_names['scene/drivers/default/idle.gr2'])), 'Hips')
print('driver animations: seat', np.round(was, 3), '->', S.HIPS, f'({len(drv_names)} files, {"donor set" if drv_zip is src else S.DRIVER_ANIMS_ZIP})')
for k, n in drv_names.items():
    g = granny.GR2(drv_zip.read(n)); granny.set_track_position(g, 'Hips', S.HIPS, was); replaced[k] = g.write()
if getattr(S, 'AVPINS_TEMPLATE', None):
    replaced[f'{MEDIA.lower()}.avpins'] = re.sub(rb'Template="[^"]*"', b'Template="' + S.AVPINS_TEMPLATE.encode() + b'"', src.read(names[f'{MEDIA.lower()}.avpins']), count=1)

# ---------------------------------------------------------------- carbin: keep the filled parts, wheels and brakes; drop the rest
carb = read_carbin(src.read(names[f'{MEDIA.lower()}.carbin']))
KEEP = set(S.KEEP_PARTS) | LIGHT_PARTS; removed = []
# wheel (43) and brake (4) model transforms: from the donor's wheel centres to this car's, per corner
donor_w = {}
for pt in carb['parts']:
    if pt['part']['type'] == 43:
        for m in pt['part']['models']: donor_w[m['bone_name'].lower()[-2:]] = np.array(m['transform'][12:15], float)
for pt in carb['parts']:
    keep = []
    for m in pt['part']['models']:
        fn = m['path'].lower().split('\\')[-1]
        if pt['part']['type'] in (4, 43):
            c = m['bone_name'].lower()[-2:]
            if c in donor_w:
                t = list(m['transform']); d = wheels[f'HUB_{c.upper()}']['centre'] - donor_w[c]; t[12] += d[0]; t[13] += d[1]; t[14] += d[2]; m['transform'] = t
            keep.append(m)
        elif fn in KEEP: keep.append(m)
        else: removed.append(fn)
    pt['part']['models'] = keep
for up in carb['upgradable_parts']:
    removed += [sm['model']['path'].lower().split('\\')[-1] for sm in up.get('shared_models', [])]; up['shared_models'] = []
print('removed', len(removed), 'donor parts; kept', sorted(KEEP))
replaced[f'{MEDIA.lower()}.carbin'] = write_carbin(carb)

# ---------------------------------------------------------------- locators: cameras and the wheel corners
loc = src.read(names['locators.xml']).decode('utf-8')
EYE = np.array(S.EYE, float); CORNER = {c: wheels[f'HUB_{c.upper()}']['centre'] for c in ('lf', 'rf', 'lr', 'rr')}
LOC = {'carLocator_seatCamLF': EYE, 'carLocator_seatCamRF': EYE * [-1, 1, 1], 'carLocator_steeringWheel': SW_CENTRE,
       'carLocator_gauges': SW_CENTRE + [0, 0.03, 0.02], 'carLocator_dashboard': SW_CENTRE + [0, 0.05, 0.10],
       'carLocator_lookCloseCenter': EYE + [0, 0, 0.3], 'carLocator_lookLeft': EYE + [-0.3, 0, 0.3], 'carLocator_lookRight': EYE + [0.3, 0, 0.3],
       'carLocator_lookCloseLeft': EYE + [-0.3, 0, 0.2], 'carLocator_lookCloseRight': EYE + [0.3, 0, 0.2],
       'paddleShiftDown': SW_CENTRE + [-0.12, 0, 0.02], 'paddleShiftUp': SW_CENTRE + [0.12, 0, 0.02],
       'carLocator_wheelLF': CORNER['lf'], 'carLocator_wheelRF': CORNER['rf'], 'carLocator_wheelLR': CORNER['lr'], 'carLocator_wheelRR': CORNER['rr']}
def set_loc(xml, name, val):
    blk = re.search(r'(<Locator Version="3">(?:(?!</Locator>).)*?<Name value="%s"/>.*?</Locator>)' % re.escape(name), xml, re.S)
    if not blk: print('  locator not found', name); return xml
    b = blk.group(1); nb = re.sub(r'value\._41="[^"]+" value\._42="[^"]+" value\._43="[^"]+"', 'value._41="%.6f" value._42="%.6f" value._43="%.6f"' % tuple(val), b)
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
for k, v in replaced.items():
    if k not in names: out.writestr(zipfile.ZipInfo(k, date_time=(2026, 10, 29, 0, 0, 0)), v, compress_type=zipfile.ZIP_DEFLATED)
for k, v in added.items(): out.writestr(zipfile.ZipInfo(k, date_time=(2026, 10, 29, 0, 0, 0)), v, compress_type=zipfile.ZIP_DEFLATED)
out.close(); print('wrote', OUT)
