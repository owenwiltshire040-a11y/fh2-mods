"""Passat 16V upgrade profile; game balance values, not claimed real-world hardware specifications."""
import numpy as np

def apply(c,S):
 car=S.PHYSICS['car_id'];base=car*1000
 def rows(t,key,v):return [dict(r) for r in c.execute(f'SELECT * FROM "{t}" WHERE "{key}"=?',(v,))]
 def put(t,r):c.execute(f'INSERT INTO "{t}" ({",".join(chr(34)+k+chr(34) for k in r)}) VALUES ({",".join("?" for _ in r)})',list(r.values()))
 def clone(t,key,old):
  source=rows(t,key,old);c.execute(f'DELETE FROM "{t}" WHERE "{key}"=?',(car,))
  for r in source:
   for k,v in list(r.items()):
    if isinstance(v,int) and old*1000<=v<old*1000+1000:r[k]=base+v-old*1000
   r[key]=car;put(t,r)
 # Replace all Charger-derived engine upgrade records with Golf 16V's component structure.
 tables=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'List_UpgradeEngine%' AND name<>'List_UpgradeEngine'")]
 for t in tables:
  cols=[r[1] for r in c.execute(f'PRAGMA table_info("{t}")')]
  if 'EngineID' in cols:clone(t,'EngineID',107)
 # Moderate cumulative naturally aspirated gains; preserve source tier spacing and prices.
 caps={'Exhaust':1.065,'FuelSystem':1.045,'Ignition':1.025,'Intake':1.05,'Manifold':1.045,'OilCooling':1.01,'PistonsCompression':1.06,'Valves':1.045}
 for suffix,cap in caps.items():
  t='List_UpgradeEngine'+suffix;rr=rows(t,'EngineID',car);maximum=max(r['TorqueScale'] for r in rr)
  for r in rr:
   scale=1.+(r['TorqueScale']-1.)/(maximum-1.)*(cap-1.)
   c.execute(f'UPDATE {t} SET TorqueScale=? WHERE Id=?',(scale,r['Id']))
 # The Passat engine retains its own stock identity, inertia and capacity.
 c.execute('UPDATE Data_Engine SET VariableTimingID=1,TorqueSteerLeftSpeedScale=.4,TorqueSteerRightSpeedScale=1,Carbureted=0,Diesel=0,Rotary=0,EngineGraphingMaxPower=450,EngineGraphingMaxTorque=600 WHERE EngineID=?',(car,))
 # Conservative 2.0 -> 2.1 litre capacity progression rather than transplanting Golf's 1.8L sizes.
 for r in rows('List_UpgradeEngineDisplacement','EngineID',car):
  disp=[1984,2020,2060,2100][r['Level']];c.execute('UPDATE List_UpgradeEngineDisplacement SET Disp=?,TorqueScale=? WHERE Id=?',(disp,disp/1984,r['Id']))
 # Distinct cam profiles: preserve baseline and extend power band progressively.
 curves=[S.PHYSICS['engine']['curve'],[(0,70),(1000,108),(2000,145),(3000,168),(4500,184),(6100,169),(6700,150),(7000,130)],[(0,68),(1000,104),(2000,140),(3000,166),(4700,188),(6500,171),(7100,153),(7400,135)],[(0,65),(1000,98),(2000,133),(3000,160),(5000,193),(7000,173),(7500,160),(7800,140)]]
 limits=[6800,7000,7400,7800]
 c.execute('DELETE FROM List_TorqueCurve WHERE TorqueCurveID BETWEEN ? AND ?',(base,base+999))
 for r in rows('List_UpgradeEngineCamshaft','EngineID',car):
  level=r['Level'];curve=curves[level];limit=limits[level];peak=max(y for x,y in curve);xs,ys=zip(*curve)
  vals=[float(np.interp(i*100,xs,ys))/peak if i*100<=limit else -2.63 if i*100==limit+100 else 0. for i in range(121)]
  vals[0]=vals[1]=vals[10]
  # Preserve every schema field, including zero-throttle engine braking.
  tor=dict(c.execute('SELECT * FROM List_TorqueCurve WHERE TorqueCurveID=882000').fetchone())
  tor.update(TorqueCurveID=base+level,TorqueScale=peak,NumTorqueValues=121)
  for i in range(246):tor['v'+str(i)]=vals[i] if i<len(vals) else 0.
  assert tor['ZeroThrottleTorqueScale'] is not None and tor['ZeroThrottleTorqueScale']>0
  put('List_TorqueCurve',tor)
  c.execute('UPDATE List_UpgradeEngineCamshaft SET RedlineRPM=?,StallRPM=800,StartRPM=3000,TorqueCurveMaxRPM=12000,NumRPMEntriesArray=121,TorqueCurveFullThrottleID=? WHERE Id=?',(limit,base+level,r['Id']))
 # Drivetrain component progression from the same transverse FWD Golf.
 for t in ['List_UpgradeDrivetrainTransmission','List_UpgradeDrivetrainClutch','List_UpgradeDrivetrainDriveline']:clone(t,'DrivetrainId' if t.endswith('Driveline') else 'DrivetrainID',106)
 ratios={0:S.PHYSICS['drivetrain']['gears'],1:S.PHYSICS['drivetrain']['gears'],2:[3.30,1.94,1.31,1.00,.82],3:[3.30,2.13,1.52,1.17,.94,.78],4:[3.30,2.13,1.52,1.17,.94,.78]}
 for r in rows('List_UpgradeDrivetrainTransmission','DrivetrainID',car):
  level=r['Level'];gears=ratios[level];update=dict(NumGears=len(gears)+1,FinalDriveRatio=[3.684,3.684,3.94,4.10,4.40][level],GearShiftTime=[.25,.22,.15,.10,.08][level],GearRatio0=-3.0)
  update.update({'GearRatio'+str(i):gears[i-1] if i<=len(gears) else -1. for i in range(1,9)})
  c.execute('UPDATE List_UpgradeDrivetrainTransmission SET '+','.join('"'+k+'"=?' for k in update)+' WHERE Id=?',list(update.values())+[r['Id']])
 for r in rows('List_UpgradeDrivetrainClutch','DrivetrainID',car):
  capacity={0:350.,1:450.,2:600.,3:800.}[r['Level']];c.execute('UPDATE List_UpgradeDrivetrainClutch SET ClutchMaxTorque=? WHERE Id=?',(capacity,r['Id']))
 # Diagnostic regression fix: restore the pre-0.4.0 flywheel inertia envelope.
 for level,inertia in enumerate([.34525212,.310726908,.25893909,.17262606]):
  c.execute('UPDATE List_UpgradeEngineFlywheel SET MomentInertia=? WHERE EngineID=? AND Level=?',(inertia,car,level))
 print('Passat 16V engine and gearbox progression applied')
