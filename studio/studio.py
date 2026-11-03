#!/usr/bin/env python3
"""FH2 Car Studio — upload a 3D model, set it up in the browser, build and install a Forza Horizon 2 car mod.

    python3 studio/studio.py            (then http://localhost:8770 opens)

Runs the repo's own pipeline (fh2re/glbgeo.py, f1/make_media.py, build_car.py, fh2re/carpreview.py, package_car.py)
on cars/<slug>/ projects described by project.json (studio/projectspec.py turns that into the builder's spec).
Standard library only for the server; numpy / scipy / Pillow / trimesh for the pipeline (the Setup page installs them).
"""
import os, sys, json, re, shutil, subprocess, threading, time, webbrowser, traceback, sqlite3, glob, urllib.request, io, tarfile
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

STUDIO = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(STUDIO)
sys.path.insert(0, STUDIO)
CARS = os.path.join(REPO, 'cars'); UI = os.path.join(STUDIO, 'ui'); VIEWER = os.path.join(REPO, 'scan', 'viewer')
SETTINGS = os.path.join(STUDIO, 'settings.json')
DEFAULT_MODS = os.path.expanduser('~/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods')
PORT = int(os.environ.get('STUDIO_PORT', 8770))
CHARGER = os.path.join(REPO, 'f1', 'in', 'DOD_ChargerSRT8_12.zip'); VANILLA = os.path.join(REPO, 'car207', 'vanilla.slt')
JOBS = {}


def settings():
    s = dict(mods_dir=DEFAULT_MODS, author='Owen')
    try: s.update(json.load(open(SETTINGS)))
    except Exception: pass
    return s


def slugify(name): return re.sub(r'[^a-z0-9]+', '', name.lower())[:24] or 'car'


def pdir(slug):
    d = os.path.join(CARS, slug)
    if not re.fullmatch(r'[a-z0-9_]+', slug) or not os.path.isdir(d): raise KeyError(slug)
    return d


def load_project(slug): return json.load(open(os.path.join(pdir(slug), 'project.json')))


def save_project(slug, J):
    p = os.path.join(pdir(slug), 'project.json'); tmp = p + '.tmp'
    json.dump(J, open(tmp, 'w'), indent=1); os.replace(tmp, p)


# ---------------------------------------------------------------- setup checks
def have_module(m):
    import importlib.util
    return importlib.util.find_spec(m) is not None


def find_file(name, roots, depth=6):
    for root in roots:
        root = os.path.expanduser(root)
        if not os.path.isdir(root): continue
        base = root.rstrip(os.sep).count(os.sep)
        for d, dirs, files in os.walk(root):
            if d.count(os.sep) - base >= depth: dirs[:] = []
            dirs[:] = [x for x in dirs if not x.startswith('.') and x not in ('node_modules', 'Photos Library.photoslibrary')]
            if name in files: return os.path.join(d, name)
    return None


def setup_status():
    S = settings(); items = []
    miss = [m for m in ('numpy', 'scipy', 'PIL', 'trimesh') if not have_module(m)]
    items.append(dict(id='python', name='Python packages (numpy, scipy, Pillow, trimesh)', ok=not miss,
                      detail='all installed' if not miss else 'missing: ' + ', '.join(miss), fix='Install'))
    items.append(dict(id='three', name='3D viewer library (three.js)', ok=os.path.exists(os.path.join(VIEWER, 'node_modules', 'three', 'build', 'three.module.js')),
                      detail='scan/viewer/node_modules/three', fix='Download'))
    items.append(dict(id='eo', name='Extra Options database tool (mod_diff.py)', ok=os.path.exists(os.path.join(REPO, 'eo', 'tools', 'mod_diff.py')),
                      detail='eo/tools/mod_diff.py', fix='Download'))
    items.append(dict(id='charger', name='Donor car: DOD_ChargerSRT8_12.zip (from the game)', ok=os.path.exists(CHARGER),
                      detail='f1/in/DOD_ChargerSRT8_12.zip', fix='Find it', path=True))
    items.append(dict(id='vanilla', name='Stock game database (vanilla.slt)', ok=os.path.exists(VANILLA), detail='car207/vanilla.slt', fix='Choose file', path=True))
    lamps = [os.path.join(REPO, 'f1', f) for f in ('lamp_tail_part.modelbin', 'lamp_brake.bin', 'lamp_reverse.bin', 'lamp_turn.bin', 'lamp_redlens.bin', 'matI_lod1.bin')]
    tex = glob.glob(os.path.join(REPO, 'tex', 'PEU_207SEHDi_08_*.swatchbin'))
    items.append(dict(id='lamps', name='Lamp + texture templates (from your Peugeot 207 mod)', ok=all(map(os.path.exists, lamps)) and len(tex) >= 2,
                      detail='f1/lamp_*.bin, f1/matI_lod1.bin, tex/PEU_207SEHDi_08_*.swatchbin', fix='Extract from 207 mod'))
    items.append(dict(id='mods', name='Game mods folder', ok=os.path.isdir(S['mods_dir']), detail=S['mods_dir'], fix='Set path', path=True))
    return items


def setup_fix(item, path=None):
    log = []
    if item == 'python':
        r = subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy', 'scipy', 'pillow', 'trimesh'], capture_output=True, text=True)
        log.append(r.stdout[-3000:] + r.stderr[-3000:])
        if r.returncode: raise RuntimeError('pip failed:\n' + log[-1])
        log.append('Installed. Restart the studio (close the Terminal window and double-click Start Studio again).')
    elif item == 'three':
        data = urllib.request.urlopen('https://registry.npmjs.org/three/-/three-0.160.0.tgz', timeout=120).read()
        dst = os.path.join(VIEWER, 'node_modules', 'three'); os.makedirs(dst, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            for m in t.getmembers():
                if not m.isfile() or not m.name.startswith('package/'): continue
                rel = m.name[len('package/'):]
                if not (rel.startswith('build/') or rel.startswith('examples/jsm/')): continue
                out = os.path.normpath(os.path.join(dst, rel))
                if not out.startswith(dst): continue
                os.makedirs(os.path.dirname(out), exist_ok=True); open(out, 'wb').write(t.extractfile(m).read())
        log.append('three.js 0.160.0 downloaded')
    elif item == 'eo':
        url = 'https://raw.githubusercontent.com/RokkuDayo/ForzaHorizon2_ExtraOptions/main/tools/mod_diff.py'
        os.makedirs(os.path.join(REPO, 'eo', 'tools'), exist_ok=True)
        open(os.path.join(REPO, 'eo', 'tools', 'mod_diff.py'), 'wb').write(urllib.request.urlopen(url, timeout=60).read()); log.append('downloaded ' + url)
    elif item == 'charger':
        src = path or find_file('DOD_ChargerSRT8_12.zip', ['~/Downloads', '~/Desktop', '~/Documents',
                                                          '~/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c'])
        if not src or not os.path.exists(os.path.expanduser(src)): raise RuntimeError('DOD_ChargerSRT8_12.zip not found - paste its full path (it is in the game\'s media/cars folder, or ~/Downloads/FH2Manager-1)')
        os.makedirs(os.path.dirname(CHARGER), exist_ok=True); shutil.copy(os.path.expanduser(src), CHARGER); log.append('copied ' + src)
    elif item == 'vanilla':
        if not path or not os.path.exists(os.path.expanduser(path)): raise RuntimeError('paste the full path of the stock gamedb .slt')
        shutil.copy(os.path.expanduser(path), VANILLA); log.append('copied ' + path)
    elif item == 'lamps':
        mods = settings()['mods_dir']; z = path or next(iter(glob.glob(os.path.join(mods, '*', 'media', 'cars', 'PEU_207*.zip'))), None)
        if not z: raise RuntimeError('no PEU_207*.zip found in the mods folder - paste the path of your 207 car zip')
        import zipfile
        r = subprocess.run([sys.executable, 'f1/extract_lamp_mati.py', z], cwd=REPO, capture_output=True, text=True); log.append(r.stdout + r.stderr)
        zf = zipfile.ZipFile(z); names = zf.namelist()
        sb = [n for n in names if n.lower().endswith('modelbin') and 'seatbelt' in n.lower()]
        if sb:
            r = subprocess.run([sys.executable, 'extract_mati.py', z], cwd=os.path.join(REPO, 'f1'), capture_output=True, text=True); log.append(r.stdout + r.stderr)
        for want in ('Interior_DIFF', 'DiffuseFrontReflector'):
            n = next((n for n in names if want in n and n.endswith('.swatchbin')), None)
            if n: open(os.path.join(REPO, 'tex', os.path.basename(n)), 'wb').write(zf.read(n)); log.append('extracted ' + os.path.basename(n))
    elif item == 'mods':
        if not path or not os.path.isdir(os.path.expanduser(path)): raise RuntimeError('that folder does not exist')
        S = settings(); S['mods_dir'] = os.path.expanduser(path); json.dump(S, open(SETTINGS, 'w'), indent=1); log.append('mods folder set')
    return '\n'.join(log)


# ---------------------------------------------------------------- game lists (makes, countries, sounds, categories)
BUCKETS = {11: 'Modern Supercars', 12: 'Retro Supercars', 13: 'Hypercars', 14: 'Retro Super Saloons', 16: 'Modern Sports Cars',
           17: "Retro Sports Cars ('90s)", 18: 'Sports Cars', 19: 'Super Saloons', 20: 'Classic Racers', 21: 'Classic Sports Cars',
           22: 'Rare Classics', 23: 'Hot Hatch', 24: 'Retro Hot Hatch', 25: 'Super Hot Hatch', 26: 'Track Toys', 28: "Classic Muscle ('70s)",
           29: 'Classic Muscle', 30: 'Retro Muscle', 31: 'Modern Muscle', 32: 'Retro Rally', 33: 'Classic Rally', 34: 'Rally Monsters',
           35: 'Modern Rally', 36: 'GT Cars', 37: 'Super GT', 38: 'Unlimited Off-road', 39: 'Sports Utility Heroes', 40: 'Off-road'}
_lists = None


def lists():
    global _lists
    if _lists: return _lists
    c = sqlite3.connect(f'file:{VANILLA}?mode=ro', uri=True)
    nice = lambda s: re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    makes = [dict(id=i, ref=ref, code=code, country=cty, icon=icon, name=nice(icon)) for i, ref, code, cty, icon in
             c.execute('select ID, DisplayName, ManufacturerCode, CountryID, IconPathBase from List_CarMake order by IconPathBase')]
    makes.append(dict(id=201, ref='_&857995983', code='PEU', country=2, icon='Peugeot', name='Peugeot (from your 207 mod)', depends='owen-peugeot-207'))
    makes.sort(key=lambda m: m['name'].lower())
    countries = [dict(id=i, name=nice(re.search(r'Flag_(\w+)\.', p).group(1))) for i, p in c.execute('select CountryID, IconPath from List_Country')]
    sounds = []
    for media, en, hp in c.execute('''select e.MediaName, e.EngineName, max(d.SimPeakPower) from Data_Engine e join List_UpgradeEngine u on u.EngineID=e.EngineID
                                      join Data_Car d on d.Id=u.Ordinal where u.IsStock=1 group by e.MediaName order by e.MediaName'''):
        en = re.sub(r'\s+', ' ', en or '').strip(' -'); sounds.append(dict(id=media, name=f'{media} {("- " + en) if en else ""} ({round(hp / 7.457)} hp)'))
    buckets = []
    for b in sorted({r[0] for r in c.execute('select CarBucket from Data_Car_Buckets')}):
        ex = [m for (m,) in c.execute('select d.MediaName from Data_Car d join Data_Car_Buckets x on x.CarId=d.Id where x.CarBucket=? limit 3', (b,))]
        buckets.append(dict(id=b, name=f"{BUCKETS.get(b, 'Category ' + str(b))} (e.g. {', '.join(ex)})"))
    _lists = dict(makes=makes, countries=countries, sounds=sounds, buckets=buckets)
    return _lists


# ---------------------------------------------------------------- projects
def used_ids():
    U = dict(car_id={3207, 3208, 3305, 3410, 3651, 3700}, string_base={64207, 64218, 64305, 64410, 64651, 64700}, colour_offset={50, 180, 240, 300},
             make_offset={3, 4, 5, 6}, media=set())
    for sp in glob.glob(os.path.join(CARS, '*', 'spec.py')):
        t = open(sp).read()
        for k in ('car_id', 'string_base', 'colour_offset', 'make_offset'):
            for m in re.findall(rf'{k}=(\d+)', t): U[k].add(int(m))
        m = re.search(r"MEDIA = '(\w+)'", t)
        if m: U['media'].add(m.group(1))
    for pj in glob.glob(os.path.join(CARS, '*', 'project.json')):
        ids = json.load(open(pj)).get('ids', {})
        for k in U:
            if k in ids: U[k].add(ids[k])
    return U


def alloc_ids():
    U = used_ids(); cid = 3500
    while cid in U['car_id'] or any(abs(64000 + cid - 3000 - b) < 3 for b in U['string_base']): cid += 1
    return dict(car_id=cid, string_base=64000 + cid - 3000, colour_offset=max(U['colour_offset']) + 60, make_offset=max(U['make_offset']) + 1)


def media_name(code, model, year, slug):
    U = used_ids()['media']
    for n in range(10):
        core = re.sub(r'[^A-Za-z0-9]', '', model) or 'Car'; yy = f'{int(year) % 100:02d}'
        tail = f'_{yy}' if n == 0 else f'{n}_{yy}'
        m = f'{code.upper()[:3]}_{core}'[:18 - len(tail)] + tail
        m = m.ljust(18, '_') if len(m) < 18 else m
        if len(m) != 18: m = (m + '_' * 18)[:18]
        if m not in U: return m
    return m


def default_car(A, name):
    words = name.split(); make = words[0] if words else 'Custom'
    return dict(make_mode='new', make_name=make, make_code=re.sub(r'[^A-Z]', '', make.upper())[:3].ljust(3, 'X'), make_country=9,
                model_name=' '.join(words[1:]) or name, short_name=' '.join(words[1:]) or name, year=2020, price=30000, bucket=23,
                sound='FOR_FocusST_12', hp=180, nm=250, rpm_power=6000, rpm_torque=2500, redline=6800, displacement_l=1.6, cylinders=4, layout='I',
                aspiration='turbo', fuel='petrol', gears=[3.6, 2.1, 1.4, 1.0, 0.8, 0.65], final_drive=3.9, drive='FWD', engine_pos='front',
                transmission='manual', mass=1300, weight_front=0.60, width=None, cd=0.32, t60=None, top_mph=None, tyre_fw=225, tyre_fa=45,
                tyre_rw=225, tyre_ra=45, rim_in=18, brake_f=320, brake_r=280, steer_deg=35, paint='#b0b0b4', compound=4, class_override='auto')


def new_project(name, data):
    import analyze
    slug = slugify(name); base = slug; n = 2
    while os.path.exists(os.path.join(CARS, slug)): slug = f'{base}{n}'; n += 1
    d = os.path.join(CARS, slug); os.makedirs(os.path.join(d, 'src'))
    open(os.path.join(d, 'src', 'model.glb'), 'wb').write(data)
    try:
        A = analyze.analyze(os.path.join(d, 'src', 'model.glb'))
    except Exception as e:
        shutil.move(d, os.path.join(CARS, '_failed_' + slug + '_' + str(int(time.time()))))
        raise RuntimeError(f'could not read that model as a glb: {e}')
    json.dump(A, open(os.path.join(d, 'analysis.json'), 'w'), indent=1)
    Wg = analyze.guess_wheels(os.path.join(d, 'src', 'model.glb'), A['front'], A['up'])
    car = default_car(A, name); ids = alloc_ids(); ids['media'] = media_name(car['make_code'], car['model_name'], car['year'], slug)
    mats = {m['name']: dict(role=m['role'] if m['role'] != 'tyre' else 'drop', colour=m['colour']) for m in A['materials']}
    J = dict(slug=slug, name=name, model='src/model.glb', credits=dict(title='', author='', licence='', url=''),
             orient=dict(front=A['front'], up=A['up']), wheels={k: Wg[k] for k in ('zf', 'zr', 'yc', 'xh', 'r')}, wheels_found=Wg['found'],
             real_wheelbase=2.6, track_mode='auto', lip_gap=0.04, one_sided=True, collision=True, materials=mats,
             wheel_materials={}, lights={k: v for k, v in A['lamps'].items()}, driver=dict(side='L', steer=None), car=car, ids=ids,
             created=time.strftime('%Y-%m-%d %H:%M'))
    json.dump(J, open(os.path.join(d, 'project.json'), 'w'), indent=1)
    return slug


def project_list():
    out = []
    for pj in sorted(glob.glob(os.path.join(CARS, '*', 'project.json'))):
        try:
            J = json.load(open(pj)); d = os.path.dirname(pj)
            out.append(dict(slug=J['slug'], name=J['name'], created=J.get('created'), built=os.path.exists(os.path.join(d, 'build', 'thumb.png')),
                            installed=J.get('installed')))
        except Exception: pass
    return out


def scale_of(J): return J['real_wheelbase'] / (J['wheels']['zf'] - J['wheels']['zr'])


def run_geometry(slug, log=None):
    """glbgeo with the project's orientation and wheels -> geo.pkl; returns the material split and FH2 dimensions"""
    import analyze, pickle
    import numpy as np
    J = load_project(slug); d = pdir(slug); W = J['wheels']; s = scale_of(J); r = W['r'] * s
    _, fr = analyze.frame(J['orient']['front'], J['orient']['up'])
    cmd = [sys.executable, 'fh2re/glbgeo.py', os.path.join(d, 'src', 'model.glb'), os.path.join(d, 'geo.pkl'), f'--frame={fr}', '--scale', f'{s:.6f}',
           f"--wheels={W['zf']:.5f},{W['zr']:.5f},{W['yc']:.5f},{W['xh']:.5f}", '--tyre-radius', f"{W['r']:.5f}",
           f'--ground={analyze.HUB_Y - r:.5f}', '--axle-mid', str(analyze.AXLE_MID), '--wheel-tag']
    r_ = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if log is not None: log.append(' '.join(cmd[1:3]) + '\n' + r_.stdout + r_.stderr)
    if r_.returncode: raise RuntimeError('geometry conversion failed:\n' + r_.stderr[-2000:])
    G = pickle.load(open(os.path.join(d, 'geo.pkl'), 'rb'))
    counts = {k: int(sum(len(p['V']) for p in v) // 3) for k, v in G['parts'].items()}
    V = np.concatenate([p['V'] for k, v in G['parts'].items() if not k.startswith('RIM_') for p in v])
    lo, hi = V.min(0), V.max(0)
    WM = J.get('wheel_materials', {}); changed = False
    for k in counts:
        if k.startswith('RIM_') and k not in WM:
            base = k[4:]; role = J['materials'].get(base, {}).get('role')
            WM[k] = 'drop' if re.search(r'tyre|tire|rubber|pneu|reifen', base.lower()) or role == 'drop' else \
                    'silver' if role in ('chrome', 'paint') else 'black' if role == 'black' else 'silver'; changed = True
    for k in list(WM):
        if k not in counts: del WM[k]; changed = True
    J['wheel_materials'] = WM
    J['geometry'] = dict(counts=counts, lo=lo.round(3).tolist(), hi=hi.round(3).tolist(), scale=s, tyre_r=r, wheels_fh2={k: v['centre'].round(3).tolist() for k, v in G['wheels'].items()})
    if J['driver'].get('steer') is None:
        fz = J['geometry']['wheels_fh2']['HUB_LF'][2]; wd = (hi[0] - lo[0]) * 0.93
        J['driver']['steer'] = [round(-0.2 * wd, 3), round(analyze.HUB_Y + 0.53 * (hi[1] - analyze.HUB_Y), 3), round(fz - 0.95, 3)]
    if not J['car'].get('width'): J['car']['width'] = round(float(hi[0] - lo[0]) * 0.93, 2)
    save_project(slug, J)
    return J


def estimates(slug):
    import importlib
    import projectspec; importlib.reload(projectspec)
    return projectspec.load(os.path.join(pdir(slug), 'spec.py'))['ESTIMATES']


SPEC_STUB = '''"""FH2 Car Studio project: everything comes from project.json (studio/projectspec.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'studio'))
from projectspec import load
globals().update(load(__file__))
'''


def write_pkg(slug, J):
    d = pdir(slug); c = J['car']; cr = J['credits']
    name = re.sub(r'[\\/:*?"<>|]+', '', J['name']).strip() or slug
    pk = os.path.join(d, 'pkg')
    if os.path.isdir(pk): shutil.rmtree(pk)
    os.makedirs(os.path.join(pk, name))
    full = f"{c['make_name']} {c['model_name']} ({c['year']})"
    model = f"\"{cr.get('title') or 'model'}\" by {cr.get('author') or 'unknown author'}" + (f" ({cr['licence']})" if cr.get('licence') else '')
    mod = dict(format_version=1, id='owen-' + slug, name=full, author=settings().get('author', 'Owen'), version=time.strftime('0.%y%m%d.%H%M'),
               description=f'{full} for personal use, made with FH2 Car Studio. 3D model {model}.', database='database.json', strings='strings.json',
               media='media', dependencies=[c['make_depends']] if c['make_mode'] == 'existing' and c.get('make_depends') else [])
    json.dump(mod, open(os.path.join(pk, name, 'mod.json'), 'w'), indent=1)
    open(os.path.join(pk, name, 'CREDITS.txt'), 'w').write(
        f"{full} - Forza Horizon 2 add-on, personal use.\n3D model: {model}\n" + (f"  {cr['url']}\n" if cr.get('url') else '') +
        "  Changes: converted to FH2's formats, scaled to the real wheelbase, lamps and wheels re-mapped onto the game's parts.\n"
        "Built on the 2012 Dodge Charger SRT8 from the game (game files, not included).\n")
    return name


def job(slug, phase):
    J_ = JOBS.setdefault(slug, {}); J_.update(state='running', phase=phase, log=[], error=None, started=time.time())
    log = J_['log']

    def sh(*cmd, cwd=REPO):
        log.append('$ ' + ' '.join(os.path.relpath(c, REPO) if os.path.isabs(str(c)) and str(c).startswith(REPO) else str(c) for c in cmd))
        p = subprocess.Popen([sys.executable, *cmd], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout: log.append(line.rstrip())
        if p.wait(): raise RuntimeError(f'{os.path.basename(str(cmd[0]))} failed (see the log)')

    def work():
        try:
            d = pdir(slug); J = load_project(slug)
            if phase == 'build':
                import analyze
                log.append('== geometry'); J = run_geometry(slug, log)
                J['ids']['media'] = J['ids'].get('media') or media_name(J['car']['make_code'], J['car']['model_name'], J['car']['year'], slug)
                MEDIA = J['ids']['media']
                log.append('== textures')
                sc = None
                for m, v in J['materials'].items():
                    if v['role'] != 'texture': continue
                    if sc is None: sc = analyze.load_scene(os.path.join(d, 'src', 'model.glb'))
                    img = None
                    for node, mat, V, F, mesh in analyze.pieces(sc):
                        if mat == m: img = analyze.mat_texture(mesh); break
                    from projectspec import safe
                    if img is not None: img.convert('RGB').save(os.path.join(d, 'src', f'tex_{safe(m)}.png')); log.append(f'  texture {m}')
                    else: log.append(f'  {m}: no texture found, drawn black')
                donor = os.path.join(d, f'donor_{MEDIA}.zip')
                if not os.path.exists(donor):
                    for old in glob.glob(os.path.join(d, 'donor_*.zip')): os.remove(old)
                    log.append('== donor'); sh('make_media.py', 'in/DOD_ChargerSRT8_12.zip', donor, MEDIA, cwd=os.path.join(REPO, 'f1'))
                open(os.path.join(d, 'spec.py'), 'w').write(SPEC_STUB); write_pkg(slug, J)
                os.makedirs(os.path.join(d, 'build'), exist_ok=True)
                log.append('== car'); sh('build_car.py', os.path.join(d, 'spec.py'), os.path.join(d, 'build', f'{MEDIA}.zip'))
                c = J['car']
                log.append('== preview'); sh('fh2re/carpreview.py', os.path.join(d, 'build', f'{MEDIA}.zip'), os.path.join(d, 'build', 'preview.glb'),
                                             '--paint', c.get('paint', '#b0b0b4').lstrip('#'), '--tyres', f"{c['tyre_fw']},{c['rim_in']},{c['tyre_rw']},{c['rim_in']}")
                J_.update(state='need_thumb', preview=f'/cars/{slug}/build/preview.glb?t={int(time.time())}')
                log.append('== rendering the thumbnail in your browser...')
            elif phase == 'package':
                out = os.path.join(d, 'dist'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
                sh('package_car.py', os.path.join(d, 'spec.py'), out, '--skip-build', '--thumb', os.path.join(d, 'build', 'thumb.png'))
                J_.update(state='done', folder=glob.glob(os.path.join(out, '*'))[0]); log.append('== ready to install')
        except Exception as e:
            J_.update(state='error', error=str(e)); log.append('ERROR: ' + str(e)); log.append(traceback.format_exc()[-1500:])
    threading.Thread(target=work, daemon=True).start()


def install(slug):
    st = JOBS.get(slug, {}); d = pdir(slug)
    src = st.get('folder') or next(iter(glob.glob(os.path.join(d, 'dist', '*'))), None)
    if not src: raise RuntimeError('build the car first')
    mods = settings()['mods_dir']
    if not os.path.isdir(mods): raise RuntimeError(f'mods folder not found: {mods} (set it on the Setup page)')
    dst = os.path.join(mods, os.path.basename(src)); note = ''
    if os.path.exists(dst):
        bk = os.path.join(d, 'backups', time.strftime('%Y%m%d-%H%M%S')); os.makedirs(bk)
        shutil.move(dst, os.path.join(bk, os.path.basename(src))); note = f' (the previous version was moved to cars/{slug}/backups)'
    shutil.copytree(src, dst)
    J = load_project(slug); J['installed'] = time.strftime('%Y-%m-%d %H:%M'); save_project(slug, J)
    return f'Installed to {dst}{note}. Restart the game to load it.'


# ---------------------------------------------------------------- HTTP
TYPES = {'.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.glb': 'model/gltf-binary',
         '.json': 'application/json', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg'}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send(self, code, body, ctype='application/json'):
        if not isinstance(body, (bytes, bytearray)): body = json.dumps(body).encode()
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(body)

    def file(self, path):
        if not os.path.isfile(path): return self.send(404, {'error': 'not found'})
        self.send(200, open(path, 'rb').read(), TYPES.get(os.path.splitext(path)[1].lower(), 'application/octet-stream'))

    def safe_join(self, root, rel):
        p = os.path.normpath(os.path.join(root, unquote(rel)))
        if not p.startswith(os.path.normpath(root) + os.sep) and p != os.path.normpath(root): raise KeyError(rel)
        return p

    def body(self):
        n = int(self.headers.get('Content-Length') or 0); return self.rfile.read(n) if n else b''

    def do_GET(self):
        u = urlparse(self.path); p = u.path
        try:
            if p in ('/', '/index.html'): return self.file(os.path.join(UI, 'index.html'))
            if p.startswith('/ui/'): return self.file(self.safe_join(UI, p[4:]))
            if p.startswith('/viewer/'): return self.file(self.safe_join(VIEWER, p[8:]))
            if p.startswith('/cars/'):
                slug, rel = p[6:].split('/', 1); pdir(slug)
                if not (rel.startswith('src/') or rel.startswith('build/')): raise KeyError(rel)
                return self.file(self.safe_join(os.path.join(CARS, slug), rel))
            if p == '/api/setup': return self.send(200, dict(items=setup_status(), settings=settings()))
            if p == '/api/lists': return self.send(200, lists())
            if p == '/api/projects': return self.send(200, project_list())
            m = re.fullmatch(r'/api/project/(\w+)', p)
            if m:
                J = load_project(m.group(1)); A = json.load(open(os.path.join(pdir(m.group(1)), 'analysis.json')))
                return self.send(200, dict(project=J, analysis=A, job={k: v for k, v in JOBS.get(m.group(1), {}).items() if k != 'log'}))
            m = re.fullmatch(r'/api/project/(\w+)/job', p)
            if m:
                st = JOBS.get(m.group(1), {}); since = int(parse_qs(u.query).get('since', ['0'])[0])
                return self.send(200, dict({k: v for k, v in st.items() if k != 'log'}, log=st.get('log', [])[since:], n=len(st.get('log', []))))
            m = re.fullmatch(r'/api/project/(\w+)/estimates', p)
            if m: return self.send(200, estimates(m.group(1)))
            self.send(404, {'error': 'not found'})
        except KeyError as e: self.send(404, {'error': f'not found: {e}'})
        except Exception as e: self.send(500, {'error': str(e), 'trace': traceback.format_exc()[-1500:]})

    def do_POST(self):
        u = urlparse(self.path); p = u.path; q = parse_qs(u.query)
        try:
            if p == '/api/setup/fix':
                b = json.loads(self.body() or b'{}'); return self.send(200, dict(log=setup_fix(b['id'], b.get('path')), items=setup_status()))
            if p == '/api/settings':
                S = settings(); S.update(json.loads(self.body())); json.dump(S, open(SETTINGS, 'w'), indent=1); return self.send(200, S)
            if p == '/api/projects':
                name = q.get('name', ['New car'])[0]; data = self.body()
                if data[:4] != b'glTF': return self.send(400, {'error': 'that is not a .glb file (export or download the model as glTF binary, .glb)'})
                return self.send(200, dict(slug=new_project(name, data)))
            m = re.fullmatch(r'/api/project/(\w+)/(\w+)', p)
            if m:
                slug, act = m.groups(); pdir(slug)
                if act == 'save':
                    J = load_project(slug); new = json.loads(self.body())
                    for k in ('slug', 'ids', 'geometry', 'model', 'created', 'installed'): new.pop(k, None)
                    J.update(new); save_project(slug, J); return self.send(200, dict(ok=True))
                if act == 'geometry': return self.send(200, dict(project=run_geometry(slug)))
                if act == 'guesswheels':
                    import analyze
                    J = load_project(slug); Wg = analyze.guess_wheels(os.path.join(pdir(slug), 'src', 'model.glb'), J['orient']['front'], J['orient']['up'])
                    J['wheels'] = {k: Wg[k] for k in ('zf', 'zr', 'yc', 'xh', 'r')}; J['wheels_found'] = Wg['found']; save_project(slug, J)
                    return self.send(200, dict(project=J))
                if act == 'logo':
                    from PIL import Image
                    Image.open(io.BytesIO(self.body())).convert('RGBA').save(os.path.join(pdir(slug), 'src', 'logo.png')); return self.send(200, dict(ok=True))
                if act == 'nologo':
                    lp = os.path.join(pdir(slug), 'src', 'logo.png')
                    if os.path.exists(lp): os.replace(lp, lp + '.old')
                    return self.send(200, dict(ok=True))
                if act == 'build':
                    if JOBS.get(slug, {}).get('state') == 'running': return self.send(409, {'error': 'already building'})
                    miss = [i['name'] for i in setup_status() if not i['ok'] and i['id'] != 'mods']
                    if miss: return self.send(400, {'error': 'finish Setup first: ' + '; '.join(miss)})
                    job(slug, 'build'); return self.send(200, dict(ok=True))
                if act == 'thumb':
                    open(os.path.join(pdir(slug), 'build', 'thumb.png'), 'wb').write(self.body()); job(slug, 'package'); return self.send(200, dict(ok=True))
                if act == 'install': return self.send(200, dict(message=install(slug)))
            self.send(404, {'error': 'not found'})
        except KeyError as e: self.send(404, {'error': f'not found: {e}'})
        except Exception as e: self.send(500, {'error': str(e), 'trace': traceback.format_exc()[-1500:]})


if __name__ == '__main__':
    os.makedirs(CARS, exist_ok=True)
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), H)
    url = f'http://localhost:{PORT}/'
    print(f'FH2 Car Studio running at {url}  (leave this window open; Ctrl+C to stop)')
    if not os.environ.get('STUDIO_NO_BROWSER'): threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
