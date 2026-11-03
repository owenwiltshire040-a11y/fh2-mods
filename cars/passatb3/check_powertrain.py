"""Validate custom upgrade references, curve cutoffs and gearbox progression."""
from pathlib import Path
import sqlite3,math
p=Path(__file__).resolve().parent;c=sqlite3.connect(p/'build/powertrain-check.slt');c.row_factory=sqlite3.Row
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
peaks=[]
for cam in c.execute('SELECT * FROM List_UpgradeEngineCamshaft WHERE EngineID=3803 ORDER BY Level'):
 curve=c.execute('SELECT * FROM List_TorqueCurve WHERE TorqueCurveID=?',(cam['TorqueCurveFullThrottleID'],)).fetchone();assert curve is not None
 assert curve['ZeroThrottleTorqueScale'] is not None and curve['ZeroThrottleTorqueScale']>0
 assert all(v is not None for v in curve)
 n=int(cam['RedlineRPM']/100);assert curve['v'+str(n+1)]==-2.63
 assert curve['NumTorqueValues']==cam['NumRPMEntriesArray']==121
 assert all(curve['v'+str(i)]>=0 for i in range(n+1))
 hp=max(i*100*curve['TorqueScale']*curve['v'+str(i)]/7120.91 for i in range(n+1));peaks.append(hp)
 print('Cam tier',cam['Level'],':',round(hp,1),'bhp /',int(cam['RedlineRPM']),'rpm')
assert all(a<b for a,b in zip(peaks,peaks[1:]))
mult=1.
for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'List_UpgradeEngine%'"):
 cols=[r[1] for r in c.execute(f'PRAGMA table_info({t})')]
 if 'EngineID' in cols:
  rows=list(c.execute(f'SELECT * FROM {t} WHERE EngineID=3803'));ids=[r['Id'] for r in rows];assert len(ids)==len(set(ids));assert all(3803000<=i<3804000 for i in ids)
  if 'TorqueScale' in cols and rows:
   assert all(r['TorqueScale']>=1 for r in rows);assert all(abs(r['TorqueScale']-1)<1e-8 for r in rows if r['IsStock'])
   mult*=max(r['TorqueScale'] for r in rows)
print('Simple stacked NA estimate:',round(peaks[-1]*mult,1),'bhp; actual game calculation pending')
assert 220<peaks[-1]*mult<280
for r in c.execute('SELECT * FROM List_UpgradeDrivetrainTransmission WHERE DrivetrainID=3803 ORDER BY Level'):
 n=r['NumGears']-1;gears=[r['GearRatio'+str(i)] for i in range(1,n+1)];assert all(a>b>0 for a,b in zip(gears,gears[1:]));assert all(r['GearRatio'+str(i)]==-1 for i in range(n+1,9))
 print('Gearbox tier',r['Level'],':',n,'forward gears, final',r['FinalDriveRatio'],'shift',r['GearShiftTime'])
assert [r[0] for r in c.execute('SELECT Mass FROM List_UpgradeCarBodyWeight WHERE CarBodyId=3803000 ORDER BY Level')]==[1230.,1205.4,1131.6,1045.5]
assert abs(c.execute('SELECT BottomCenterWheelbasePosZ FROM Data_CarBody WHERE Id=3803000').fetchone()[0]+.05)<1e-6
print('Powertrain and handling regression checks passed')
