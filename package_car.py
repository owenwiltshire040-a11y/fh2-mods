"""One step from a car spec to a finished, installable Extra Options mod folder.

  python3 package_car.py cars/<car>/spec.py OUTDIR [--skip-build]

Runs build_car.py (car zip: body, glass, rims, lamps, driver, wheels) and build_car_db.py (database + strings), turns
the database into the mod's database.json (mod_diff, id_conflicts nearest), checks the string IDs against every other
mod of Owen's, then the Autoshow presentation (fh2re/presentation.py): a thumbnail rendered from the built car, and
either an existing make (spec PRESENT['use_make']) or a wordmark logo for a new make. Writes OUTDIR/<pkg name>/ with
mod.json, CREDITS.txt, database.json, strings.json, media/cars/<MEDIA>.zip, media/stripped/RC0/*.

spec PRESENT = dict(paint='b8121b',                       # thumbnail paint colour
                    use_make=(201, '_&857995983'),          # optional: (List_CarMake ID, its DisplayName ref)
                    depends='owen-peugeot-207',             # optional: the mod that provides that make
                    logo_text='PEUGEOT', logo_png=None, icon_base='Peugeot')   # for a new make
"""
import sys, os, json, shutil, subprocess, importlib.util, glob, socket, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('out'); ap.add_argument('--skip-build', action='store_true')
a = ap.parse_args()
_s = importlib.util.spec_from_file_location('carspec', a.spec); S = importlib.util.module_from_spec(_s); _s.loader.exec_module(S)
CAR_DIR = os.path.dirname(os.path.abspath(a.spec)); P = S.PHYSICS; MEDIA = S.MEDIA; PR = getattr(S, 'PRESENT', {})
work = os.path.join(CAR_DIR, 'build'); os.makedirs(work, exist_ok=True)
run = lambda *c: subprocess.run([sys.executable, *c], check=True, cwd=HERE)

# ---------------------------------------------------------------- string IDs must be unique across ALL of Owen's mods
KNOWN = {'Peugeot 207 mod': range(64207, 64210), 'Toro Rosso STR1 mod': range(64651, 64654)}
for sp in glob.glob(os.path.join(HERE, 'cars', '*', 'spec.py')):
    if os.path.samefile(sp, a.spec): continue
    t = open(sp).read(); import re
    m = re.search(r'string_base=(\d+)', t)
    if m: KNOWN[os.path.basename(os.path.dirname(sp))] = range(int(m.group(1)), int(m.group(1)) + 3)
mine = set(range(P['string_base'], P['string_base'] + 3))
clash = {k: sorted(mine & set(v)) for k, v in KNOWN.items() if mine & set(v)}
if clash: sys.exit(f'string_base {P["string_base"]} clashes with {clash}: pick another (they overwrite each other in game)')

# ---------------------------------------------------------------- build
car_zip = os.path.join(work, f'{MEDIA}.zip')
if not a.skip_build: run('build_car.py', a.spec, car_zip)
slt, strings = os.path.join(work, 'custom.slt'), os.path.join(work, 'strings.json')
run('build_car_db.py', a.spec, slt, strings)
dbj = os.path.join(work, 'database.json')
run('eo/tools/mod_diff.py', 'database', 'car207/vanilla.slt', slt, '-o', dbj, '--updates', 'override', '--force')
d = json.load(open(dbj)); d.setdefault('policy', {})['id_conflicts'] = 'nearest'; json.dump(d, open(dbj, 'w'), indent=1)

# ---------------------------------------------------------------- package folder
pkg_src = glob.glob(os.path.join(CAR_DIR, 'pkg', '*'))[0]; name = os.path.basename(pkg_src)
dst = os.path.join(a.out, name); shutil.rmtree(dst, ignore_errors=True); shutil.copytree(pkg_src, dst)
shutil.copy(dbj, dst); shutil.copy(strings, dst)
os.makedirs(os.path.join(dst, 'media', 'cars'), exist_ok=True); shutil.copy(car_zip, os.path.join(dst, 'media', 'cars', f'{MEDIA}.zip'))

# ---------------------------------------------------------------- thumbnail (needs the viewer server; started here if not running)
viewer = os.path.join(HERE, 'scan', 'viewer'); glb = os.path.join(viewer, f'_{MEDIA}.glb'); png = os.path.join(work, 'thumb.png')
T = P.get('tyres', {}); tyres = PR.get('tyres') or (f"{T['width_front']},{T['rim_in']},{T['width_rear']},{T['rim_in']}" if 'rim_in' in T else None)
cmd = ['fh2re/carpreview.py', car_zip, glb, '--paint', PR.get('paint', 'b0b0b4')] + (['--tyres', tyres] if tyres else [])
run(*cmd)
srv = None
if socket.socket().connect_ex(('127.0.0.1', 8765)) != 0:
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8765'], cwd=viewer, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
env = dict(os.environ); env['NODE_PATH'] = os.pathsep.join(filter(None, [os.path.join(viewer, 'node_modules'),
          subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()]))
subprocess.run(['node', 'thumb.js', os.path.basename(glb), png, '816', '459', '-50', '10'], cwd=viewer, env=env, check=True)
if srv: srv.terminate()
os.remove(glb)

# ---------------------------------------------------------------- presentation: thumbnail + make
pc = ['fh2re/presentation.py', dst, '--thumb', png]
if PR.get('use_make'):
    pc += ['--use-make', str(PR['use_make'][0]), '--make-name-ref', PR['use_make'][1]]
    if PR.get('depends'): pc += ['--dependency', PR['depends']]
elif PR.get('logo_png') or PR.get('logo_text'):
    pc += ['--logo-png', PR['logo_png']] if PR.get('logo_png') else ['--logo-text', PR['logo_text']]
    if PR.get('icon_base'): pc += ['--make-icon-base', PR['icon_base']]
run(*pc)
print('\nmod folder ready:', dst)
