"""Raise the sprung body 25mm and match tyre radii to the measured source.
Run after prepare_source/configure/finalize; idempotent on prepared geometry.
"""
from pathlib import Path
import pickle,re,json
p=Path(__file__).resolve().parent;g=pickle.loads((p/'geo.pkl').read_bytes());old=g.get('body_clearance_lift',0.);delta=.025-old
for mat,fragments in g['parts'].items():
 if mat=='SOURCE_RIM':continue
 for f in fragments:f['V'][:,1]+=delta
g['body_clearance_lift']=.025;(p/'geo.pkl').write_bytes(pickle.dumps(g))
s=p/'spec.py';t=s.read_text()
if '# Arch clearance revision' not in t:
 t+='''
# Arch clearance revision: sprung body/cabin +25mm, axles and rim geometry unchanged.
STEER=tuple(v+(.025 if i==1 else 0) for i,v in enumerate(STEER))
HIPS=tuple(v+(.025 if i==1 else 0) for i,v in enumerate(HIPS))
EYE=tuple(v+(.025 if i==1 else 0) for i,v in enumerate(EYE))
PHYSICS['tyres'].update(aspect_front=29,aspect_rear=29)
_b=list(PHYSICS['body']['bbox']);_b[2]+=.025;_b[3]+=.025;PHYSICS['body']['bbox']=tuple(_b)
'''
 s.write_text(t)
e=p/'electric_db.py';t=e.read_text();marker=' # Preserve arch clearance on the lowered suspension upgrades.'
if marker not in t:
 t=t.replace(' c.row_factory=None',marker+'''
 for u in rows('List_UpgradeSpringDamper','Ordinal',car):
  for key in ['FrontSpringDamperPhysicsID','RearSpringDamperPhysicsID']:
   c.execute('UPDATE List_SpringDamperPhysics SET DefRideHeight=MAX(DefRideHeight,.1475),MinRideHeight=MAX(MinRideHeight,.1475),MaxRideHeight=MAX(MaxRideHeight,.1625) WHERE SpringDamperPhysicsID=?',(u[key],))
 c.row_factory=None''')
 e.write_text(t)
meta=p/'pkg/Hyundai N Vision 74/mod.json';m=json.loads(meta.read_text());m['version']='0.1.1';meta.write_text(json.dumps(m,indent=2))
print('Body lift 25mm, source-matched tyre radii, lowered-suspension clearance floor configured')
