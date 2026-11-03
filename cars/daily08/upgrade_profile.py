"""Scale inherited upgrade data to the prototype's own engine and mass."""
def apply(c,S):
 import sqlite3,numpy as np
 c.row_factory=sqlite3.Row;P=S.PHYSICS;car=P['car_id'];base=car*1000;E=P['engine'];D=P['drivetrain'];mass=P['body']['mass']
 for r in c.execute('SELECT Id,Disp FROM List_UpgradeEngineDisplacement WHERE EngineID=?',(car,)).fetchall():
  c.execute('UPDATE List_UpgradeEngineDisplacement SET Disp=? WHERE Id=?',(round(E['displacement']*r['Disp']/6424),r['Id']))
 c.execute('UPDATE Data_Engine SET Diesel=0,Rotary=0,Carbureted=0 WHERE EngineID=?',(car,))
 # Every cam level has a complete engine-braking curve, with bounded baseline torque.
 c.execute('UPDATE List_TorqueCurve SET ZeroThrottleTorqueScale=? WHERE TorqueCurveID BETWEEN ? AND ?',(max(15,E['peak_nm']*.22),base,base+999))
 c.execute('UPDATE List_UpgradeDrivetrainDifferential SET RearToqueSplit=? WHERE DrivetrainID=?',(.5 if D['drivetype']==3 else 0,car))
 for row in c.execute('SELECT * FROM List_UpgradeCarBodyWeight WHERE CarBodyId=?',(base,)).fetchall():
  stock=row['IsStock'];factor=1.0 if stock else [1.,.96,.90,.82][min(3,row['Level'])]
  c.execute('UPDATE List_UpgradeCarBodyWeight SET Mass=?,InitialMass=? WHERE Id=?',(mass*factor,mass,row['Id']))
 c.row_factory=None
