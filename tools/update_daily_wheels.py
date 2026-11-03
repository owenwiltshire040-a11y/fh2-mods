"""Replace only the 18 existing daily prototypes, preserving all originals and load order."""
from pathlib import Path
import json,subprocess,hashlib,datetime,os
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];B=R/'cars/daily_batch';O=R/'output/Daily Drivers'
mods=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods')
m=json.loads((B/'build-manifest.json').read_text());reports={x['name']:x for x in json.loads((B/'validation.json').read_text())};wheels={x['name']:x for x in json.loads((B/'wheel-validation.json').read_text())};assert len(m)==len(reports)==len(wheels)==18
review={x['name']:x for x in json.loads((B/'source-wheel-visual-review.json').read_text())['cars']}
stamp=datetime.datetime.now(ZoneInfo('Europe/London')).strftime('%Y%m%d-%H%M%S');backup=R/'backups/daily-source-wheels-v1'/('installed-'+stamp);stage=mods/('.source-wheels-stage-'+stamp)
def hashes(p):return {str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file()}
plan=[]
for item in m:
 src=O/item['name'];dst=mods/('Daily - '+item['name']);meta=json.loads((src/'mod.json').read_text());old=json.loads((dst/'mod.json').read_text());w=wheels[item['name']]
 assert meta['id']==old['id']==reports[item['name']]['mod_id'];assert meta['version']=='0.1.1';assert w['valid'] and w['generated_open_barrel'];assert json.loads((src/'wheel-fit.json').read_text())['valid']
 assert json.loads((src/'wheel-build.json').read_text())['face_sha256']==w['face_sha256'];plan.append((src,dst,hashes(src)))
 assert review[item['name']]['wheel_reviewed'] and review[item['name']]['face_sha256']==w['face_sha256']
backup.mkdir(parents=True);loadorder=mods/'loadorder.txt';original=loadorder.read_bytes();(backup/'loadorder.txt').write_bytes(original);stage.mkdir()
for src,dst,expected in plan:
 new=stage/dst.name;subprocess.run(['/bin/cp','-cR',str(src),str(new)],check=True);assert hashes(new)==expected
record={'timestamp':stamp,'backup':str(backup),'installed':[]};swapped=[]
try:
 for src,dst,expected in plan:
  old=backup/dst.name;os.rename(dst,old)
  try:os.rename(stage/dst.name,dst)
  except BaseException:os.rename(old,dst);raise
  swapped.append((dst,old));assert hashes(dst)==expected
  record['installed'].append(dict(name=src.name,folder=str(dst),sha256=expected));print('Updated and verified',src.name,flush=True)
 assert loadorder.read_bytes()==original
except BaseException:
 for dst,old in reversed(swapped):os.rename(dst,stage/dst.name);os.rename(old,dst)
 raise
stage.rmdir();(B/'source-wheel-install-record.json').write_text(json.dumps(record,indent=2)+'\n');(O/'source-wheel-install-record.json').write_text(json.dumps(record,indent=2)+'\n');print('All 18 updated; originals preserved at',backup)
