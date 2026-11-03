#!/usr/bin/env python3
"""Local browser UI for the FH2 custom car builder."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, os, re, shutil, subprocess, sys, urllib.parse, zipfile, sqlite3

ROOT = Path(__file__).resolve().parents[2]
WEB = Path(__file__).resolve().parent
WORK = ROOT / 'cars' / '_studio'
MAX_UPLOAD = 1024 * 1024 * 1024
HOME = Path.home()
DESKTOP_ASSETS = HOME / 'Desktop' / 'untitled folder'
DRIVE_C = HOME / 'Library' / 'Application Support' / 'CrossOver' / 'Bottles' / 'Azimuth' / 'drive_c'
GAME_ROOT = DRIVE_C / 'Anthem_1.0.0.64_x64__8wekyb3d8bbwe'
AZIMUTH_ROOT = DRIVE_C / 'azimuth-windows'
FM5_PACKS = DRIVE_C / 'FM5 Addon Packs'

def find_first(paths):
    return next((p for p in paths if p.is_file()), None)

def donor_sources():
    return [ROOT/'f1/in/DOD_ChargerSRT8_12.zip', DESKTOP_ASSETS/'DOD_ChargerSRT8_12.zip',
            GAME_ROOT/'Mount/media/cars/DOD_ChargerSRT8_12.zip', HOME/'Downloads/FH2Manager-1/DOD_ChargerSRT8_12.zip']

def database_sources():
    return [ROOT/'car207/vanilla.slt', DESKTOP_ASSETS/'vanilla.slt', DESKTOP_ASSETS/'gamedbRC.slt',
            GAME_ROOT/'Mount/media/stripped/gamedbRC.slt', HOME/'Downloads/FH2Manager-1/fh2re/gamedbRC.slt']

def p207_sources():
    return [DESKTOP_ASSETS/'PEU_207_5door_v14.zip', HOME/'Downloads/FH2Manager-1/fh2re/PEU_207_5door_v14.zip',
            AZIMUTH_ROOT/'mods/Peugeot 207/media/cars/PEU_207SEHDi_08.zip']

def engine_sound_options():
    found={}
    def record(rows,source,car_names=None):
        car_names=car_names or {}
        for row in rows:
            media=row.get('MediaName')
            if not media: continue
            label=str(row.get('EngineName') or car_names.get(str(media)) or '').strip()
            found.setdefault(str(media),{'media':str(media),'name':label,'source':source})
            if not found[str(media)]['name'] and label: found[str(media)]['name']=label
    db=find_first(database_sources())
    if db:
        try:
            c=sqlite3.connect(f'file:{db}?mode=ro',uri=True); cols=[r[1] for r in c.execute('pragma table_info("Data_Engine")')]
            if 'MediaName' in cols:
                select=[x for x in ('MediaName','EngineName') if x in cols]
                record([dict(zip(select,r)) for r in c.execute('select '+','.join('"'+x+'"' for x in select)+' from Data_Engine')],'FH2 stock')
            c.close()
        except Exception: pass
    def read_mod(raw,source,strings_raw=None):
        try:
            tables=json.loads(raw).get('tables',{}); t=tables.get('Data_Engine',{})
            car_names={}; translations={}
            if strings_raw:
                langs=json.loads(strings_raw).get('languages',{}); lang=langs.get('EN') or next(iter(langs.values()),{})
                translations=lang.get('Data_Car',{})
            cars=tables.get('Data_Car',{})
            for row in cars.get('insert',[])+cars.get('update',[]):
                ref=str(row.get('DisplayName',''))
                if ref.startswith('_&') and ref[2:].isdigit():
                    label=translations.get(str(int(ref[2:])%65536),'')
                    if label and row.get('MediaName'): car_names[str(row['MediaName'])]=label
            record(t.get('insert',[])+t.get('update',[]),source,car_names)
        except Exception: pass
    mods=AZIMUTH_ROOT/'mods'
    if mods.exists():
        for p in mods.glob('*/database.json'):
            strings=p.parent/'strings.json'
            read_mod(p.read_text(errors='replace'),p.parent.name,strings.read_text(errors='replace') if strings.exists() else None)
    if FM5_PACKS.exists():
        for p in FM5_PACKS.glob('*.zip'):
            try:
                with zipfile.ZipFile(p) as z:
                    names=z.namelist()
                    if 'database.json' in names: read_mod(z.read('database.json'),p.stem,z.read('strings.json') if 'strings.json' in names else None)
            except Exception: pass
    return sorted(found.values(),key=lambda x:(x['name'].lower(),x['media'].lower()))

def prepare_stock_inputs():
    """Stage private, user-owned FH2 inputs only into the repo's ignored build-input paths."""
    db_src=find_first(database_sources()); db_dst=ROOT/'car207/vanilla.slt'
    if db_src and db_src.resolve()!=db_dst.resolve():
        db_dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(db_src,db_dst)
    # Stage the stock texture layouts used when writing new custom swatches.
    p207=find_first(p207_sources())
    if p207:
        with zipfile.ZipFile(p207) as z:
            for n in z.namelist():
                if ('PEU_207SEHDi_08_Interior_DIFF_' in n or 'PEU_207SEHDi_08_Rad_Fixed_DiffuseFrontReflector_' in n) and n.endswith('.swatchbin'):
                    target=ROOT/'tex'/Path(n).name
                    if not target.exists(): target.write_bytes(z.read(n))
    mati=ROOT/'f1/matI_lod1.bin'
    if not mati.exists():
        p207=find_first(p207_sources())
        if p207:
            r=subprocess.run([sys.executable,str(ROOT/'f1/extract_mati.py'),str(p207)],cwd=ROOT/'f1',capture_output=True,text=True)
            if r.returncode: return False, (r.stdout+'\n'+r.stderr)[-1800:]
    return bool(db_dst.exists() and mati.exists()), ''

def response(handler, data, status=200, content_type='application/json; charset=utf-8'):
    raw = data if isinstance(data, bytes) else (json.dumps(data).encode() if content_type.startswith('application/json') else data.encode())
    handler.send_response(status); handler.send_header('Content-Type', content_type); handler.send_header('Content-Length', str(len(raw))); handler.send_header('Cache-Control','no-store'); handler.end_headers(); handler.wfile.write(raw)

def check_status():
    py = subprocess.run([sys.executable, '-c', 'import numpy,trimesh,scipy,PIL,texture2ddecoder,etcpak'], capture_output=True, text=True)
    pw = subprocess.run(['node','-e','require("playwright")'], cwd=ROOT/'scan/viewer', capture_output=True, text=True) if shutil.which('node') else None
    ini=AZIMUTH_ROOT/'FH2_ExtraOptions.ini'; ini_text=ini.read_text(errors='replace') if ini.exists() else ''
    files_section=re.search(r'(?ims)^\[Files\]\s*(.*?)(?=^\[|\Z)',ini_text)
    return {'python':sys.version.split()[0], 'python_deps':py.returncode == 0, 'python_error':py.stderr[-1200:],
            'donor':find_first(donor_sources()) is not None or any((ROOT/'cars').glob('*/donor_*.zip')),
            'vanilla_db':find_first(database_sources()) is not None, 'mod_diff':(ROOT/'eo/tools/mod_diff.py').exists(),
            'mati':(ROOT/'f1/matI_lod1.bin').exists() or find_first(p207_sources()) is not None, 'node':shutil.which('node') is not None,
            'three':(ROOT/'scan/viewer/node_modules/three/build/three.module.js').exists(), 'playwright':bool(pw and pw.returncode==0),
            'azimuth':(AZIMUTH_ROOT/'azimuth.exe').exists() and ini.exists(),
            'media_override':bool(files_section and re.search(r'(?im)^\s*EnableMediaOverrides\s*=\s*1\s*$',files_section.group(1))),
            'mods_folder':(AZIMUTH_ROOT/'mods').is_dir()}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print('%s - %s' % (self.address_string(), fmt % args))
    def do_GET(self):
        u=urllib.parse.urlparse(self.path)
        if u.path=='/api/status': return response(self, check_status())
        if u.path=='/api/sounds': return response(self, engine_sound_options())
        if u.path=='/api/projects':
            projects=[]
            if WORK.exists():
                for p in sorted(WORK.iterdir()):
                    state=p/'project.json'
                    if p.is_dir() and (p/'model.glb').exists():
                        data=json.loads(state.read_text()) if state.exists() else {}
                        projects.append({'slug':p.name,'saved':state.exists(),'model':(p/'model.glb').stat().st_size,'mod_name':data.get('mod_name','')})
            return response(self,projects)
        if u.path=='/api/project':
            q=urllib.parse.parse_qs(u.query); slug=q.get('name',[''])[0]
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug): return response(self,{'error':'Invalid project name'},400)
            state=WORK/slug/'project.json'
            if not state.exists(): return response(self,{'error':'No saved setup for this project'},404)
            return response(self,json.loads(state.read_text()))
        if u.path=='/api/templates':
            rows=[]
            for p in sorted((ROOT/'cars').glob('*/spec.py')):
                if p.parent.name.startswith('_'): continue
                pkg=next(iter((p.parent/'pkg').glob('*')),None)
                meta=json.loads((pkg/'mod.json').read_text()) if pkg and (pkg/'mod.json').exists() else {}
                credits=(pkg/'CREDITS.txt').read_text() if pkg and (pkg/'CREDITS.txt').exists() else ''
                rows.append({'id':p.parent.name,'label':p.parent.name.replace('omoda5','Omoda 5').replace('peugeot208','Peugeot 208').replace('dafxf105','DAF XF105').replace('volvov70','Volvo V70'),'spec':p.read_text(),'meta':meta,'credits':credits})
            return response(self, rows)
        if u.path=='/api/file':
            q=urllib.parse.parse_qs(u.query); slug=q.get('project',[''])[0]
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug): return response(self,{'error':'Invalid project name'},400)
            p=WORK/slug/'model.glb'
            if not p.exists(): return response(self,{'error':'Model not found'},404)
            return response(self,p.read_bytes(),content_type='model/gltf-binary')
        if u.path=='/': return response(self,(WEB/'index.html').read_bytes(),content_type='text/html; charset=utf-8')
        if u.path.startswith('/assets/'):
            name=Path(u.path).name
            if name not in ('app.js','style.css'): return response(self,'Not found',404,'text/plain')
            p=WEB/name; return response(self,p.read_bytes(),content_type='text/javascript; charset=utf-8' if name.endswith('.js') else 'text/css; charset=utf-8')
        if u.path=='/api/fit-preview':
            slug=urllib.parse.parse_qs(u.query).get('project',[''])[0]
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug): return response(self,{'error':'Invalid project'},400)
            p=WORK/slug/'build/fit-preview.glb'
            if not p.is_file(): return response(self,{'error':'Build a fit preview first'},404)
            return response(self,p.read_bytes(),content_type='model/gltf-binary')
        if u.path.startswith('/three/'):
            rel=u.path[len('/three/'):]
            p=(ROOT/'scan/viewer/node_modules/three'/rel).resolve()
            if not p.is_relative_to((ROOT/'scan/viewer/node_modules/three').resolve()) or not p.is_file(): return response(self,'Three.js dependency missing. See Setup.',404,'text/plain')
            typ='text/javascript; charset=utf-8' if p.suffix=='.js' else 'application/octet-stream'
            return response(self,p.read_bytes(),content_type=typ)
        return response(self,'Not found',404,'text/plain')
    def do_POST(self):
        u=urllib.parse.urlparse(self.path); length=int(self.headers.get('Content-Length','0'))
        if length<0 or length>MAX_UPLOAD: return response(self,{'error':'Upload exceeds the 1 GB limit'},413)
        if u.path=='/api/upload':
            q=urllib.parse.parse_qs(u.query); slug=q.get('project',[''])[0]; name=q.get('name',['model.glb'])[0]
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug) or Path(name).suffix.lower() not in ('.glb','.gltf'): return response(self,{'error':'Use a project name and a .glb or .gltf file'},400)
            if Path(name).suffix.lower() != '.glb': return response(self,{'error':'For now, upload a single .glb file with its resources embedded.'},400)
            body=self.rfile.read(length)
            if not body: return response(self,{'error':'The uploaded file is empty'},400)
            folder=WORK/slug; folder.mkdir(parents=True,exist_ok=True); dest=folder/('model.glb' if name.lower().endswith('.glb') else 'model.gltf'); dest.write_bytes(body)
            return response(self,{'ok':True,'bytes':len(body),'file':dest.name})
        if u.path=='/api/analyze':
            data=json.loads(self.rfile.read(length)); slug=data.get('project','')
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug): return response(self,{'error':'Invalid project name'},400)
            model=WORK/slug/'model.glb'
            if not model.exists(): return response(self,{'error':'Upload a model first'},404)
            code="""import json,sys,trimesh
sys.path.insert(0,'fh2re')
from wheelfit import inspect_model
s=trimesh.load(sys.argv[1],force='scene');b=s.bounds;mats=set();nodes=[]
for n in s.graph.nodes_geometry:
 T,g=s.graph[n];m=s.geometry[g];nodes.append(n);mats.add(getattr(getattr(getattr(m,'visual',None),'material',None),'name',None) or '(unnamed)')
print(json.dumps(dict(bounds=b.tolist(),size=(b[1]-b[0]).tolist(),materials=sorted(mats),nodes=nodes,geometry_count=len(s.geometry),wheel_measurements=inspect_model(sys.argv[1]))))
"""
            p=subprocess.run([sys.executable,'-c',code,str(model)],capture_output=True,text=True,cwd=ROOT)
            if p.returncode: return response(self,{'error':p.stderr[-1600:] or 'Could not read model'},422)
            return response(self,json.loads(p.stdout))
        if u.path=='/api/save':
            try: data=json.loads(self.rfile.read(length))
            except Exception: return response(self,{'error':'Invalid request'},400)
            slug=data.get('project','')
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug): return response(self,{'error':'Invalid project name'},400)
            folder=WORK/slug
            if not (folder/'model.glb').exists(): return response(self,{'error':'Upload a model before saving'},400)
            data['spec_path']='spec.py'; data['model_file']='model.glb'
            (folder/'spec.py').write_text(data.get('spec',''))
            (folder/'project.json').write_text(json.dumps(data,indent=2)+'\n')
            return response(self,{'ok':True,'project':slug})
        if u.path=='/api/build':
            try: data=json.loads(self.rfile.read(length))
            except Exception: return response(self,{'error':'Invalid request'},400)
            slug=data.get('project',''); spec=data.get('spec',''); cfg=data.get('geometry',{}); template=data.get('template','')
            if not re.fullmatch(r'[a-z0-9-]{2,48}',slug) or len(spec)>150000: return response(self,{'error':'Invalid project or spec'},400)
            model=WORK/slug/'model.glb'; folder=WORK/slug
            if not model.exists(): return response(self,{'error':'Upload a .glb model first'},400)
            if not re.fullmatch(r'[a-z0-9]+',template): return response(self,{'error':'Choose a starting template'},400)
            template_dir=ROOT/'cars'/template
            if not (template_dir/'spec.py').is_file(): return response(self,{'error':'Starting template not found'},400)
            for key in ('frame','wheels','scale','tyre_radius','ground','axle_mid'):
                if key not in cfg: return response(self,{'error':f'Missing geometry field: {key}'},400)
            try:
                frame=','.join(x.strip() for x in cfg['frame'].split(','))
                if not re.fullmatch(r'-?[xyz],-?[xyz],-?[xyz]',frame): raise ValueError('Frame must be e.g. -x,y,z')
                wheels=','.join(str(float(x.strip())) for x in cfg['wheels'].split(','))
                if len(wheels.split(','))!=4: raise ValueError('Wheel inputs need front Z, rear Z, centre height, and half track')
                scale=float(cfg['scale']); radius=float(cfg['tyre_radius']); ground=float(cfg['ground']); axle=float(cfg['axle_mid'])
                if scale<=0 or radius<=0: raise ValueError('Scale and tyre radius must be greater than zero')
            except Exception as e: return response(self,{'error':str(e)},400)
            if not spec.strip().startswith(('"""','\'\'\'')): return response(self,{'error':'Spec must be a Python module based on one of the provided templates'},400)
            spec_path=folder/'spec.py'; geo=folder/'geo.pkl'; spec_path.write_text(spec)
            cmd=[sys.executable,'fh2re/glbgeo.py',str(model),str(geo),'--frame',frame,'--scale',str(scale),'--wheels',wheels,'--tyre-radius',str(radius),'--ground',str(ground),'--axle-mid',str(axle)]
            for opt in ('rim_node','rim_mats','skip_mats','skip_nodes','tag_nodes'):
                if cfg.get(opt): cmd += ['--'+opt.replace('_','-'),str(cfg[opt])]
            cmd += ['--centre-x',str(float(cfg.get('centre_x',0)))]
            geo_run=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT)
            if geo_run.returncode: return response(self,{'error':'Model geometry step failed','details':(geo_run.stdout+'\n'+geo_run.stderr)[-5000:]},422)
            # Keep geometry/spec paths relocatable within this project and bind donor to the repository's checked-in build input.
            raw=spec_path.read_text()
            raw=re.sub(r"^GEO\s*=.*$",f"GEO = os.path.join(HERE, 'geo.pkl')",raw,flags=re.M)
            raw=re.sub(r"^DONOR_ZIP\s*=.*$",f"DONOR_ZIP = os.path.join(HERE, 'donor_' + MEDIA + '.zip')",raw,flags=re.M)
            spec_path.write_text(raw)
            donor=find_first(donor_sources())
            if donor is None:
                candidates=list((ROOT/'cars').glob('*/donor_*.zip')); donor=candidates[0] if candidates else None
            if donor is None: return response(self,{'error':'The Charger donor zip was not found in the known FH2, Desktop, or project locations.','details':'Model geometry was created, but the donor-based build cannot continue.'},422)
            ready, prep_error=prepare_stock_inputs()
            if not ready: return response(self,{'error':'Could not prepare the stock database/material inputs.','details':prep_error or 'Need a stock game database and the Peugeot 207 donor zip.'},422)
            donor_out=folder/('donor_'+re.search(r"^MEDIA\s*=\s*['\"]([^'\"]+)['\"]",raw,re.M).group(1)+'.zip') if re.search(r"^MEDIA\s*=\s*['\"]([^'\"]+)['\"]",raw,re.M) else None
            media_name=donor_out.name[6:-4] if donor_out else ''
            if not re.fullmatch(r'[A-Za-z0-9_]{18}',media_name): return response(self,{'error':'MEDIA must be exactly 18 letters, numbers, or underscores so the donor media can be renamed safely.'},400)
            renamed=subprocess.run([sys.executable,str(ROOT/'f1/make_media.py'),str(donor),str(donor_out),media_name],capture_output=True,text=True,cwd=ROOT/'f1')
            if renamed.returncode: return response(self,{'error':'Could not prepare the donor car media','details':(renamed.stdout+'\n'+renamed.stderr)[-3000:]},422)
            fit_profile=cfg.get('fit_profile')
            if fit_profile:
                if fit_profile not in ('charger_rim_face','charger_legacy'): return response(self,{'error':'Unknown wheel profile'},400)
                # Wheelbase here describes rendered geometry; physical wheelbase stays in the editable spec.
                extra="\nWHEEL_FIT=dict(profile="+repr(fit_profile)+")\nPHYSICS['body']['model_wheelbase']="+repr((float(wheels.split(',')[0])-float(wheels.split(',')[1]))*scale)+"\nPHYSICS['body']['track_front']=PHYSICS['body']['track_rear']='auto'\n"
                if fit_profile=='charger_rim_face':extra+='TRACK_REFERENCE="rim_face"\nRIM_FACE_GAP=.01\n'
                else:extra+='TRACK_REFERENCE="legacy"\nLIP_GAP=.04\n'
                spec_path.write_text(spec_path.read_text()+extra)
            # Specs may import their template's material/upgrade helpers.
            for helper in template_dir.glob('*.py'):
                if helper.name!='spec.py' and not (folder/helper.name).exists(): shutil.copy2(helper,folder/helper.name)
            # package_car.py copies this project's own mod metadata. Seed it from the chosen template, then apply the form values.
            src_pkg=next(iter((template_dir/'pkg').glob('*')),None)
            if src_pkg is None: return response(self,{'error':'The selected template has no package metadata'},422)
            if not pkg_name or Path(pkg_name).name!=pkg_name or pkg_name in ('.','..'): return response(self,{'error':'Package folder name must be a plain folder name.'},400)
            pkg_root=folder/'pkg'
            if pkg_root.exists(): shutil.rmtree(pkg_root)
            pkg_root.mkdir(parents=True); pkg_name=str(data.get('package_name') or 'Custom Car').strip()[:80]
            pkg_src=pkg_root/pkg_name; shutil.copytree(src_pkg,pkg_src)
            meta=json.loads((pkg_src/'mod.json').read_text())
            meta.update({'id':str(data.get('mod_id') or '').strip()[:80], 'name':str(data.get('mod_name') or '').strip()[:120],
                         'author':str(data.get('author') or '').strip()[:100], 'version':str(data.get('version') or '0.1.0').strip()[:30],
                         'description':str(data.get('description') or '').strip()[:1000]})
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,79}',meta['id']): return response(self,{'error':'Mod ID must use lowercase letters, numbers, and hyphens.'},400)
            if not meta['name'] or not meta['author']: return response(self,{'error':'Enter a mod name and author.'},400)
            (pkg_src/'mod.json').write_text(json.dumps(meta,indent=1)+'\n')
            (pkg_src/'CREDITS.txt').write_text(str(data.get('credits') or '').strip()+'\n')
            out=folder/'out'; out.mkdir(exist_ok=True)
            build=subprocess.run([sys.executable,'package_car.py',str(spec_path),str(out)],capture_output=True,text=True,cwd=ROOT)
            result=(build.stdout+'\n'+build.stderr)[-9000:]
            if build.returncode: return response(self,{'error':'Packaging did not finish. Check the missing-input panel and build output.','details':result,'geometry':geo_run.stdout[-2000:]},422)
            fit_report=json.loads((folder/'build/wheel-fit.json').read_text())
            built=list(out.iterdir())
            (folder/'project.json').write_text(json.dumps(data,indent=2)+'\n')
            return response(self,{'ok':True,'folder':str(built[0]) if built else str(out),'log':result,'geometry':geo_run.stdout[-2000:],'fit_report':fit_report})
        if u.path=='/api/install':
            try: d=json.loads(self.rfile.read(length)); src=Path(d['folder']).resolve(); dest=Path(d['mods']).expanduser().resolve()
            except Exception: return response(self,{'error':'Provide the built mod and the mods folder'},400)
            if not src.is_dir() or not (src/'mod.json').exists(): return response(self,{'error':'Choose a built mod folder'},400)
            dest.mkdir(parents=True,exist_ok=True); target=dest/src.name
            if target.exists(): return response(self,{'error':f'{target} already exists. Rename or move it before installing.'},409)
            shutil.copytree(src,target); return response(self,{'ok':True,'installed':str(target)})
        return response(self,{'error':'Unknown action'},404)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description='Open the FH2 Car Studio in your browser'); ap.add_argument('--port',type=int,default=8766); ap.add_argument('--no-open',action='store_true'); a=ap.parse_args()
    if not a.no_open:
        import webbrowser; webbrowser.open(f'http://127.0.0.1:{a.port}')
    print(f'FH2 Car Studio: http://127.0.0.1:{a.port} (Ctrl+C to stop)')
    ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
