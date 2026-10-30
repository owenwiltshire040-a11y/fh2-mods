"""High-speed stability for the STR1 (Owen 30 Oct: 'stability at high speed isn't' fine), using the ZS/MSF Williams
FW24 add-on's values as the reference for an FH2 F1 car (numbers only):
  TireModelName a -> OW_F1 (FH2's open-wheel F1 tyre), FixListingRearFricScale 1.35 -> 2.5,
  Lat/Long*ScalarMax 0.99 -> 1.2 and *ScalarClamp 4.95 -> 6.0, WeightDistribution 0.418 -> 0.45,
  wing aero front DF 60-120 -> 187.5-312.5 (lateral drag 11.5), rear DF 90-150 -> 450-750 (lateral drag 27),
  rear static toe -0.5 / camber -1.5, front camber -2.0. Power, drag, gearing and dimensions unchanged.
usage: python3 f1/str1_stability.py database.json   (edits the STR1 mod's database.json in place)
"""
import json, sys
p = sys.argv[1]; d = json.load(open(p)); T = d['tables']
car = T['Data_Car']['insert'][0]
car.update(FixListingRearFricScale=2.5, WeightDistribution=0.45)
for k in list(car):
    if k.endswith('ScalarMax'): car[k] = 1.2
    if k.endswith('ScalarClamp'): car[k] = 6.0
for r in T['List_UpgradeTireCompound']['insert']: r['TireModelName'] = 'OW_F1'
aero = sorted(T['List_AeroPhysics']['insert'], key=lambda r: r['Downforce1'])   # front (smaller), rear
aero[0].update(Downforce0=187.5, Downforce1=312.5, LateralDrag=11.5)
aero[-1].update(Downforce0=450.0, Downforce1=750.0, LateralDrag=27.0)
sp = T['List_SpringDamperPhysics']['insert']
# which spring rows are front/rear: List_UpgradeSpringDamper links them; fall back to 'rear = the second of each pair'
ups = T.get('List_UpgradeSpringDamper', {}).get('insert', [])
rear_ids = {u.get('RearSpringDamperPhysicsID') for u in ups if u.get('RearSpringDamperPhysicsID')}
front_ids = {u.get('FrontSpringDamperPhysicsID') for u in ups if u.get('FrontSpringDamperPhysicsID')}
for r in sp:
    if r['SpringDamperPhysicsID'] in rear_ids: r.update(StaticToe=-0.5, StaticCamber=-1.5)
    elif r['SpringDamperPhysicsID'] in front_ids: r.update(StaticCamber=-2.0)
print('front springs', sorted(front_ids), 'rear springs', sorted(rear_ids))
print('aero', [(a['AeroPhysicsID'], a['Downforce0'], a['Downforce1']) for a in aero])
json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False); print('updated', p)
