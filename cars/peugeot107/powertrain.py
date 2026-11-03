"""Peugeot 107 1.0 12V upgrade profile; game balance values, not claimed real-world hardware specifications."""
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
 # The Peugeot 107 engine retains its own stock identity, inertia and capacity.
 c.execute('UPDATE Data_Engine SET VariableTimingID=1,TorqueSteerLeftSpeedScale=.4,TorqueSteerRightSpeedScale=1,Carbureted=0,Diesel=0,Rotary=0,EngineGraphingMaxPower=250,EngineGraphingMaxTorque=350 WHERE EngineID=?',(car,))
 # Conservative 2.0 -> 2.1 litre capacity progression rather than transplanting Golf's 1.8L sizes.
 for r in rows('List_UpgradeEngineDisplacement','EngineID',car):
  disp=[998,1020,1040,1080][r['Level']];c.execute('UPDATE List_UpgradeEngineDisplacement SET Disp=?,TorqueScale=? WHERE Id=?',(disp,disp/998,r['Id']))
 # Distinct cam profiles: preserve baseline and extend power band progressively.
 curves=[[(rpm*(1+.04*level),torque*(1+.025*level)) for rpm,torque in S.PHYSICS['engine']['curve']] for level in range(4)]
 limits=[6500,6800,7100,7400]
 c.execute('DELETE FROM List_TorqueCurve WHERE TorqueCurveID BETWEEN ? AND ?',(base,base+999))
 for r in rows('List_UpgradeEngineCamshaft','EngineID',car):
  level=r['Level'];curve=curves[level];limit=limits[level];peak=max(y for x,y in curve);xs,ys=zip(*curve)
  vals=[float(np.interp(i*100,xs,ys))/peak if i*100<=limit else -2.63 if i*100==limit+100 else 0. for i in range(121)]
  vals[0]=vals[1]=vals[10]
  # Preserve every schema field, including zero-throttle engine braking.
  tor=dict(c.execute('SELECT * FROM List_TorqueCurve WHERE TorqueCurveID=882000').fetchone())
  tor.update(TorqueCurveID=base+level,TorqueScale=peak,ZeroThrottleTorqueScale=70.,NumTorqueValues=121)
  for i in range(246):tor['v'+str(i)]=vals[i] if i<len(vals) else 0.
  assert tor['ZeroThrottleTorqueScale'] is not None and tor['ZeroThrottleTorqueScale']>0
  put('List_TorqueCurve',tor)
  c.execute('UPDATE List_UpgradeEngineCamshaft SET RedlineRPM=?,StallRPM=800,StartRPM=3000,TorqueCurveMaxRPM=12000,NumRPMEntriesArray=121,TorqueCurveFullThrottleID=? WHERE Id=?',(limit,base+level,r['Id']))
 # Drivetrain component progression from the same transverse FWD Golf.
 for t in ['List_UpgradeDrivetrainTransmission','List_UpgradeDrivetrainClutch','List_UpgradeDrivetrainDriveline']:clone(t,'DrivetrainId' if t.endswith('Driveline') else 'DrivetrainID',106)
 ratios={0:S.PHYSICS['drivetrain']['gears'],1:S.PHYSICS['drivetrain']['gears'],2:[3.30,1.94,1.31,1.00,.82],3:[3.30,2.13,1.52,1.17,.94,.78],4:[3.30,2.13,1.52,1.17,.94,.78]}
 for r in rows('List_UpgradeDrivetrainTransmission','DrivetrainID',car):
  level=r['Level'];gears=ratios[level];update=dict(NumGears=len(gears)+1,FinalDriveRatio=[3.55,3.55,3.882,4.10,4.40][level],GearShiftTime=[.35,.30,.22,.15,.12][level],GearRatio0=-3.0)
  update.update({'GearRatio'+str(i):gears[i-1] if i<=len(gears) else -1. for i in range(1,9)})
  c.execute('UPDATE List_UpgradeDrivetrainTransmission SET '+','.join('"'+k+'"=?' for k in update)+' WHERE Id=?',list(update.values())+[r['Id']])
 for r in rows('List_UpgradeDrivetrainClutch','DrivetrainID',car):
  capacity={0:150.,1:200.,2:250.,3:350.}[r['Level']];c.execute('UPDATE List_UpgradeDrivetrainClutch SET ClutchMaxTorque=? WHERE Id=?',(capacity,r['Id']))
 print('Peugeot 107 1.0 12V engine and gearbox progression applied')
