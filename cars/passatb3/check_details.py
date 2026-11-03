"""Validate built lamp parts, cabin textures and retained engine safety fields."""
from pathlib import Path
import json,zipfile,sys,struct
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'fh2re'))
from geometry import Part
from body_swap import material_names
from carbin import read_carbin
p=r/'output/Volkswagen Passat B3';z=zipfile.ZipFile(p/'media/cars/VW_PassatB3_1990_A.zip');assert z.testzip() is None;names={n.lower():n for n in z.namelist()}
for suffix in ['headlightl_a.modelbin','headlightr_a.modelbin','taillightl_a.modelbin']:
 n=next(n for n in z.namelist() if n.lower().endswith(suffix));part=Part(z.read(n));assert len(part.render)>0;print('Lamp part decoded:',suffix)
for tag in ['cloth','dash','trim','gauges','needle']:assert any(n.split('/')[-1].startswith(tag+'_') for n in z.namelist()),tag
car=read_carbin(z.read(names['vw_passatb3_1990_a.carbin']));loaded={m['path'].lower().split('\\')[-1] for p in car['parts'] for m in p['part']['models']}
assert {'headlightl_a.modelbin','headlightr_a.modelbin','taillightl_a.modelbin'}<=loaded
for c in json.loads((p/'database.json').read_text())['tables']['List_TorqueCurve']['insert']:assert c['ZeroThrottleTorqueScale']>0
print('Lamp loading, cabin textures, archive integrity and idle fields passed')
