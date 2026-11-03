"""Dedicated stock race setup (from the Jordan EJ11), full 15,000 rpm curves, and adjustable race components."""
import math
import numpy as np

def apply(c,S):
 car=S.PHYSICS['car_id'];body=car*1000;E=S.PHYSICS['engine']
 # These edits are confined to the newly cloned car and component rows.
 for (table,) in c.execute("select name from sqlite_master where type='table' and name like 'List_Upgrade%'").fetchall():
  cols={r[1] for r in c.execute(f'pragma table_info("{table}")')}
  if 'IsStock' not in cols:continue
  keys=[k for k in cols if k.lower() in ['ordinal','engineid','drivetrainid','carbodyid']]
  for key in keys:c.execute(f'delete from "{table}" where "{key}"=? and IsStock=0',(body if key.lower()=='carbodyid' else car,))
 # The schema has v0..v245: use the full table instead of the old 12k builder limit.
 curve=E['curve'];xs,ys=zip(*curve);peak=max(ys);count=int(E['redline']/100)+2
 for (cid,) in c.execute('select TorqueCurveID from List_TorqueCurve where TorqueCurveID between ? and ?',(body,body+999)).fetchall():
  values=[max(float(np.interp(i*100,xs,ys)),0.)/peak if i*100<=E['redline'] else (-2.63 if i==count-1 else 0.) for i in range(246)]
  c.execute('update List_TorqueCurve set TorqueScale=?,ZeroThrottleTorqueScale=110,NumTorqueValues=?,'+','.join(f'v{i}=?' for i in range(246))+' where TorqueCurveID=?',[peak,count,*values,cid])
 c.execute('update List_UpgradeEngineCamshaft set RedlineRPM=?,TorqueCurveMaxRPM=?,NumRPMEntriesArray=?,StallRPM=?,StartRPM=? where EngineID=?',(E['redline'],(count-1)*100,count,E['stall'],E['start'],car))
 c.execute('update Data_Engine set EngineGraphingMaxPower=1100,EngineGraphingMaxTorque=700 where EngineID=?',(car,))
 c.execute('update List_UpgradeTireCompound set TireModelName="OW_F1" where Ordinal=?',(car,))
 c.execute('update Data_Car set FixListingRearFricScale=2.5 where Id=?',(car,))
 cols=[r[1] for r in c.execute('pragma table_info(Data_Car)')]
 for col in cols:
  if col.endswith('ScalarMax'):c.execute(f'update Data_Car set "{col}"=1.2 where Id=?',(car,))
  if col.endswith('ScalarClamp'):c.execute(f'update Data_Car set "{col}"=6.0 where Id=?',(car,))
 for (sid,front) in c.execute('select s.SpringDamperPhysicsID,s.SpringDamperPhysicsID=u.FrontSpringDamperPhysicsID from List_UpgradeSpringDamper u join List_SpringDamperPhysics s on s.SpringDamperPhysicsID in (u.FrontSpringDamperPhysicsID,u.RearSpringDamperPhysicsID) where u.Ordinal=?',(car,)).fetchall():
  c.execute('update List_SpringDamperPhysics set DefRideHeight=.1625,MinRideHeight=.1325,MaxRideHeight=.1925,StaticCamber=?,StaticToe=? where SpringDamperPhysicsID=?',(-2. if front else -1.5,0. if front else -.5,sid))
 c.execute('update List_UpgradeBrakes set Level=3,BrakeTorqueSlider=1,BrakeBiasSlider=1,RequiresGraphics=0 where Ordinal=?',(car,))
 c.execute('update List_UpgradeSpringDamper set Level=3 where Ordinal=?',(car,))
 c.execute('update List_UpgradeAntiSwayFront set Level=3 where Ordinal=?',(car,));c.execute('update List_UpgradeAntiSwayRear set Level=3 where Ordinal=?',(car,))
 c.execute('update List_UpgradeDrivetrainTransmission set Level=3 where DrivetrainID=?',(car,));c.execute('update List_UpgradeDrivetrainDifferential set Level=3 where DrivetrainID=?',(car,))
 # Remove unused roadcar physics records after non-stock component rows were removed.
 c.execute('delete from List_SpringDamperPhysics where Ordinal=? and SpringDamperPhysicsID not in (select FrontSpringDamperPhysicsID from List_UpgradeSpringDamper where Ordinal=? union select RearSpringDamperPhysicsID from List_UpgradeSpringDamper where Ordinal=?)',(car,car,car))
 print('RB22 full V6 hybrid curve, open-wheel tyres, stock race parts and tuning applied')
