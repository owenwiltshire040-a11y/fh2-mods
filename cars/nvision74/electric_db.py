"""Convert the generic chassis database to FH2's native Model S electric system."""
import sqlite3,math,numpy as np

def apply(c,S):
 c.row_factory=sqlite3.Row;car=S.PHYSICS['car_id'];base=car*1000
 def rows(t,key,v):return [dict(r) for r in c.execute(f'SELECT * FROM "{t}" WHERE "{key}"=?',(v,))]
 def put(t,r):c.execute(f'INSERT INTO "{t}" ({",".join(chr(34)+k+chr(34) for k in r)}) VALUES ({",".join("?" for _ in r)})',list(r.values()))
 # Remove unused cloned combustion engine and curves, so no petrol component path remains.
 for (t,) in list(c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'List_UpgradeEngine%'") ):
  cols=[r[1] for r in c.execute(f'PRAGMA table_info({t})')]
  if 'EngineID' in cols:c.execute(f'DELETE FROM {t} WHERE EngineID=?',(car,))
 c.execute('DELETE FROM Data_Engine WHERE EngineID=?',(car,));c.execute('DELETE FROM List_TorqueCurve WHERE TorqueCurveID BETWEEN ? AND ?',(base,base+999))
 motor=rows('Data_Motor','MotorID',23)[0];motor.update(MotorID=car,MotorName='Hydrogen-electric RWD - provisional',**{'MotorMass-kg':700.},BatteryCapacity=62.4,MotorGraphingMaxTorque=900.,MotorGraphingMaxPower=500.,TorqueCurveFullThrottleID=base+100);put('Data_Motor',motor)
 for t,key,old in [('List_UpgradeMotor','Ordinal',2101),('List_UpgradeMotorParts','MotorID',23)]:
  for r in rows(t,key,old):
   r['Id']=base+(r['Id']-old*1000);r[key]=car;r['MotorID']=car
   if 'ManufacturerID' in r:r['ManufacturerID']=17
   if r['IsStock']:r['Price']=0
   put(t,r)
 curve=rows('List_TorqueCurve','TorqueCurveID',23100)[0];curve.update(TorqueCurveID=base+100,TorqueScale=900.,ZeroThrottleTorqueScale=100.,NumTorqueValues=181)
 for i in range(246):
  rpm=i*100
  curve['v'+str(i)]=(min(900.,500000./max(rpm*math.pi/30,1))/900.) if rpm<=16000 else -2.63 if rpm==16100 else 0.
 put('List_TorqueCurve',curve)
 # Native electric shift logic and single-speed gearing; AWD type 3.
 c.execute('UPDATE Data_Drivetrain SET DrivetypeID=2,EngineMountingDirection=2,ShiftSystemID=5 WHERE DrivetrainID=?',(car,))
 for t in ['List_UpgradeDrivetrainTransmission','List_UpgradeDrivetrainClutch','List_UpgradeDrivetrainDriveline','List_UpgradeDrivetrainDifferential']:
  key='DrivetrainId' if t.endswith('Driveline') else 'DrivetrainID';c.execute(f'DELETE FROM {t} WHERE {key}=?',(car,))
  for r in rows(t,key,2176):
   r['Id']=base+r['Id']-2176000;r[key]=car
   if t.endswith('Transmission'):r.update(FinalDriveRatio=5.0,GearRatio1=1.5,GearRatio0=-9.,GearShiftTime=0.)
   if t.endswith('Differential'):r.update(RearToqueSplit=1.0,FrontLimitedSlipTorqueAccel=150.,RearLimitedSlipTorqueAccel=250.)
   put(t,r)
 c.execute('UPDATE List_UpgradeDrivetrain SET PowertrainId=3 WHERE Ordinal=?',(car,))
 c.execute('UPDATE Data_Car SET EngineConfigID=6,CylinderID=10,Displacement=0,PowertrainID=3,EnginePlacementID=3,NumGears=1,SimPeakPower=?,SimPeakTorque=9.,SimPeakAngVel=?,SimPeakTorqueAngVel=0.,SimRedlineAngVel=? WHERE Id=?',(5000.,6000*math.pi/30,16000*math.pi/30,car))
 # Sensible EV chassis upgrade stages, retaining stock fit.
 for r in rows('List_UpgradeCarBodyWeight','CarBodyId',base):
  c.execute('UPDATE List_UpgradeCarBodyWeight SET Mass=? WHERE Id=?',(round(2000*[1,.98,.95,.90][r['Level']],1),r['Id']))
 for side in ['Front','Rear']:
  for r in rows('List_UpgradeAntiSway'+side,'Ordinal',car):
   factor=1. if r['IsStock'] else 1.2 if r['Level']==2 else 1.5
   c.execute('UPDATE List_AntiSwayPhysics SET DefSwaybarStiffness=DefSwaybarStiffness*? WHERE AntiSwayPhysicsID=?',(factor,r['AntiSwayPhysicsID']))
 for r in rows('List_UpgradeSpringDamper','Ordinal',car):
  factor=1 if r['IsStock'] else 1.15 if r['Level']<3 else 1.35
  for k in ['FrontSpringDamperPhysicsID','RearSpringDamperPhysicsID']:
   c.execute('UPDATE List_SpringDamperPhysics SET DefSpringRate=DefSpringRate*? WHERE SpringDamperPhysicsID=?',(factor,r[k]))
 # Concept silver default; keep alternate colours available.
 c.execute('UPDATE Combo_Colors SET RGB=?,Metallic=1 WHERE Ordinal=? AND Sequence=1',(int('bfc2c6',16),car))
 # Preserve arch clearance on the lowered suspension upgrades.
 for u in rows('List_UpgradeSpringDamper','Ordinal',car):
  for key in ['FrontSpringDamperPhysicsID','RearSpringDamperPhysicsID']:
   c.execute('UPDATE List_SpringDamperPhysics SET DefRideHeight=MAX(DefRideHeight,.1475),MinRideHeight=MAX(MinRideHeight,.1475),MaxRideHeight=MAX(MaxRideHeight,.1625) WHERE SpringDamperPhysicsID=?',(u[key],))
 c.row_factory=None
 print('Native electric motor, single-speed RWD and EV upgrades configured')
