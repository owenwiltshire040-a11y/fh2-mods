"""Install new batch folders without replacing any existing mod; preserve the load order."""
from pathlib import Path
import json,subprocess,shutil,hashlib,datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'cars/daily_batch';OUT=ROOT/'output/Daily Drivers';mods=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods')
manifest=json.loads((BASE/'build-manifest.json').read_text());reports={r['name']:r for r in json.loads((BASE/'validation.json').read_text())};assert len(reports)==18
assert 'PASS 1 packages' in (BASE/'astra-final-validation.log').read_text()
plan=[]
for item in manifest:
 name=item['name'];src=OUT/name;dst=mods/('Daily - '+name);meta=json.loads((src/'mod.json').read_text());assert reports[name]['mod_id']==meta['id'];assert not dst.exists(),f'Existing destination left untouched: {dst}'
 fit=json.loads((src/'wheel-fit.json').read_text());assert fit['valid'] and fit['database_checked'];plan.append((item,src,dst))
loadorder=mods/'loadorder.txt';original=loadorder.read_bytes();stamp=datetime.datetime.now(ZoneInfo('Europe/London')).strftime('%Y%m%d-%H%M%S');backup=ROOT/'backups'/('daily-batch-install-'+stamp);backup.mkdir(parents=True);(backup/'loadorder.txt').write_bytes(original)
record=dict(timestamp=stamp,loadorder_backup=str(backup/'loadorder.txt'),installed=[])
for item,src,dst in plan:
 # APFS copy-on-write clones preserve independent files without duplicating the large media archives.
 subprocess.run(['/bin/cp','-cR',str(src),str(dst)],check=True)
 for p in src.rglob('*'):
  if not p.is_file():continue
  q=dst/p.relative_to(src);assert q.is_file() and q.stat().st_size==p.stat().st_size
  assert hashlib.sha256(q.read_bytes()).digest()==hashlib.sha256(p.read_bytes()).digest(),str(q)
 record['installed'].append(dict(name=item['name'],folder=str(dst),mod_id=json.loads((dst/'mod.json').read_text())['id']))
 item['status']='installed';item['installed_folder']=str(dst);print('Installed and verified',item['name'],flush=True)
# Corsa defines the Opel make; it is earlier than the dependent Opel entries in the manifest.
names=[dst.name for _,_,dst in plan];current=original.decode('utf-8');suffix=('' if current.endswith(('\n','\r')) else '\r\n')+'\r\n'.join(n for n in names if n not in current.splitlines())+'\r\n';loadorder.write_bytes(original+suffix.encode('utf-8'))
new=loadorder.read_text();assert all(new.splitlines().count(n)==1 for n in names);assert new.splitlines().index('Daily - Opel Corsa C')<new.splitlines().index('Daily - Opel Astra H')
(BASE/'install-record.json').write_text(json.dumps(record,indent=2));(OUT/'install-record.json').write_text(json.dumps(record,indent=2));(BASE/'build-manifest.json').write_text(json.dumps(manifest,indent=2));print('Verified',len(plan),'new mods and saved load-order backup:',backup)
