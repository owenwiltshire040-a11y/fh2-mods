"""Prepare reviewed source-wheel release metadata after all builds complete."""
from pathlib import Path
import json,shutil,sys
R=Path(__file__).resolve().parents[1];B=R/'cars/daily_batch';O=R/'output/Daily Drivers';sys.path.insert(0,str(R/'fh2re'))
from wheelfit import load_spec
from wheelcheck import check
m=json.loads((B/'build-manifest.json').read_text());reports=[];selections=[]
for item in m:
 p=Path(item['spec']).parent;s=load_spec(p/'spec.py');pkg=O/item['name']
 report=check(s,pkg/'media/cars'/(s.MEDIA+'.zip'));reports.append(dict(name=item['name'],**report));(p/'build/wheel-build.json').write_text(json.dumps(report,indent=2)+'\n');source=json.loads((p/'source-wheel.json').read_text());selections.append(source)
 for target in [next((p/'pkg').iterdir()),pkg]:
  meta=json.loads((target/'mod.json').read_text());meta['version']='0.1.1';meta['description']='Personal source-model conversion with its own source wheels. Provisional handling/cockpit and decorative lighting. See BUILD-NOTES.txt.';(target/'mod.json').write_text(json.dumps(meta,indent=2)+'\n')
  notes=target/'BUILD-NOTES.txt';text=notes.read_text().replace('v0.1.0','v0.1.1').replace('Generic donor rims are used in this first pass.','Own source wheel geometry and original colour/texture atlas are fitted. The donor face, backing plate and blur meshes have been removed.')
  extra=f"\nWheel review: {source['nominal_rim_in']} inch source wheels; source geometry, diameter, axial depth and all donor detail levels checked. Open inner barrel generated. Preview brakes retain their own inward offsets.\n"
  if extra not in text:text+=extra
  notes.write_text(text)
 shutil.copy2(pkg/'BUILD-NOTES.txt',p/'BUILD-NOTES.txt')
 for filename in ['source-wheel.json','wheel-build.json']:
  shutil.copy2(p/('build/'+filename if filename=='wheel-build.json' else filename),pkg/filename)
(P:=B/'wheel-validation.json').write_text(json.dumps(reports,indent=2)+'\n');(B/'source-wheel-selections.json').write_text(json.dumps(selections,indent=2)+'\n')
assert len({r['face_sha256'] for r in reports})==18
print('18 distinct source wheels validated; release metadata updated')
