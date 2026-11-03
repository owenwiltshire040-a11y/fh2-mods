from pathlib import Path
import sqlite3,json,zipfile,math,pickle
p=Path(__file__).resolve().parent;r=p.parents[1];c=sqlite3.connect(p/'build/custom.slt');c.row_factory=sqlite3.Row
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
car=c.execute('SELECT * FROM Data_Car WHERE Id=3905').fetchone();assert car['EngineConfigID']==6 and car['NumGears']==1 and car['Displacement']==0
assert c.execute('SELECT COUNT(*) FROM Data_Engine WHERE EngineID=3905').fetchone()[0]==0
assert c.execute('SELECT COUNT(*) FROM List_UpgradeEngine WHERE Ordinal=3905').fetchone()[0]==0
motor=c.execute('SELECT * FROM Data_Motor WHERE MotorID=3905').fetchone();link=c.execute('SELECT * FROM List_UpgradeMotor WHERE Ordinal=3905 AND IsStock=1').fetchone();assert link['MotorID']==motor['MotorID']
curve=c.execute('SELECT * FROM List_TorqueCurve WHERE TorqueCurveID=?',(motor['TorqueCurveFullThrottleID'],)).fetchone();assert curve['ZeroThrottleTorqueScale']>0 and all(v is not None for v in curve)
assert curve['v161']==-2.63
hp=max(i*100*math.pi/30*curve['TorqueScale']*curve['v'+str(i)]/745.6999 for i in range(161));assert 390<hp<400
for row in c.execute('SELECT * FROM List_UpgradeDrivetrainTransmission WHERE DrivetrainID=3905'):assert row['NumGears']==2 and row['GearRatio2']==-1
assert c.execute('SELECT DrivetypeID FROM Data_Drivetrain WHERE DrivetrainID=3905').fetchone()[0]==3
G=pickle.load(open(p/'geo.pkl','rb'));assert abs(G['wheelbase']-2.89)<.001
for m in ['TESLA_RIM','TESLA_RIM_BLACK']:assert G['parts'][m]
out=r/'output/Tesla Model Y 2025';d=json.loads((out/'database.json').read_text());assert d['tables']['Data_Car']['insert'][0]['MakeID']==81
assert d['tables']['List_UpgradeMotor']['insert'][0]['MotorID']==3905
assert zipfile.ZipFile(out/'media/cars/TES_ModelY_2025_A_.zip').testzip() is None
meta=json.loads((out/'mod.json').read_text());assert meta['format_version']==1
for k in ['database','strings','media']:assert (out/meta[k]).exists()
print('Native EV links, complete torque curve, AWD/single-speed gearing, wheelbase, manifest and archive checks passed; estimated peak',round(hp,1),'bhp')
