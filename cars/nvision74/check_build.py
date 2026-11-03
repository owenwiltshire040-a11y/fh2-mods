"""Validate the actual N Vision package and native electric stock setup."""
from pathlib import Path
import json,sqlite3,zipfile,math,hashlib
p=Path(__file__).resolve().parent;out=p.parents[1]/'output/Hyundai N Vision 74'
c=sqlite3.connect(p/'build/custom.slt');c.row_factory=sqlite3.Row
assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
car=c.execute('select * from Data_Car where Id=4301').fetchone()
assert car['PowertrainID']==3 and car['NumGears']==1 and car['Displacement']==0
assert c.execute('select count(*) from Data_Engine where EngineID=4301').fetchone()[0]==0
assert c.execute('select DrivetypeID from Data_Drivetrain where DrivetrainID=4301').fetchone()[0]==2
m=c.execute('select * from Data_Motor where MotorID=4301').fetchone();assert m['BatteryCapacity']==62.4
r=c.execute('select * from List_TorqueCurve where TorqueCurveID=?',(m['TorqueCurveFullThrottleID'],)).fetchone()
t=[r['v'+str(i)]*r['TorqueScale'] for i in range(161)];power=max(i*100*math.pi/30*v for i,v in enumerate(t));assert abs(max(t)-900)<.001 and abs(power-500000)<1
assert r['ZeroThrottleTorqueScale']>0 and r['v161']<0
fit=json.loads((out/'wheel-fit.json').read_text());wheel=json.loads((out/'wheel-build.json').read_text());assert fit['valid'] and fit['database_checked'] and wheel['valid'] and wheel['all_donor_face_lods_removed']
assert abs(fit['model_wheelbase']-2.905)<1e-6
zpath=out/'media/cars/HYU_NVision74_23_A.zip'
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
report=dict(valid=True,car_id=4301,power_kw=power/1000,torque_nm=max(t),drivetrain='native electric RWD',wheelbase=2.905,source_wheel_triangles=wheel['source_triangles'],geometry_sha256=hashlib.sha256(zpath.read_bytes()).hexdigest(),source_steering='static',runtime='see runtime-validation.json after capture')
(p/'build-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

# Measure built-source arch sections against actual database tyre envelopes.
import pickle,numpy as np
G=pickle.loads((p/'geo.pkl').read_bytes());paint=np.concatenate([f['V'] for f in G['parts']['Paint']]);clearance={}
for corner in ['lf','rf','lr','rr']:
 row=fit['corners'][corner];centre=np.array(row['tyre_centre']);lip=fit['arch_lips']['F' if corner.endswith('f') else 'R'];side=-1 if corner.startswith('l') else 1
 mask=(np.abs(paint[:,2]-centre[2])<.04)&(paint[:,0]*side>lip-.05)&(paint[:,1]>centre[1]+.2)&(paint[:,1]<centre[1]+.55)
 assert mask.any()
 gap=float(paint[mask,1].min()-centre[1]-row['radius']);assert gap>.020,(corner,gap)
 side_key='FrontSpringDamperPhysicsID' if corner.endswith('f') else 'RearSpringDamperPhysicsID'
 heights=[r[0] for r in c.execute('SELECT s.MinRideHeight FROM List_UpgradeSpringDamper u JOIN List_SpringDamperPhysics s ON s.SpringDamperPhysicsID=u.'+side_key+' WHERE u.Ordinal=4301')]
 lowered=gap+min(heights)-.1625;assert lowered>.010,(corner,lowered)
 clearance[corner]=dict(static_gap_m=gap,minimum_upgrade_gap_m=lowered)
report['arch_clearance']=clearance;(p/'build-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Arch clearance:',clearance)
