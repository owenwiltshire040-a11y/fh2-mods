"""Passat handling progression based on stock FH2 Golf Mk2 GTI records."""
import sqlite3

def apply(c,S):
 c.row_factory=sqlite3.Row
 car=S.PHYSICS['car_id']; body=car*1000
 def rows(t,key,val):return [dict(r) for r in c.execute(f'SELECT * FROM "{t}" WHERE "{key}"=?',(val,))]
 def insert(t,r):c.execute(f'INSERT INTO "{t}" ({",".join(chr(34)+k+chr(34) for k in r)}) VALUES ({",".join("?" for _ in r)})',list(r.values()))
 def copy(t,key,old,new):
  source=rows(t,key,old);c.execute(f'DELETE FROM "{t}" WHERE "{key}"=?',(new,));result=[]
  for r in source:
   for k,v in list(r.items()):
    if isinstance(v,int) and old//1000==353 and old==353000:
     if 353000<=v<354000:r[k]=body+v-353000
    elif isinstance(v,int) and 353000<=v<354000:r[k]=body+v-353000
   r[key]=new
   if key=='DrivetrainID':r['Id']=body+(r['Id']-old*1000)
   if 'Ordinal' in r:r['Ordinal']=car
   insert(t,r);result.append(r)
  return result
 # Restore tyres and rim diameter choices using stock game's FWD hatch structure.
 for t,key in [('List_UpgradeTireCompound','Ordinal'),('List_UpgradeCarBodyTireWidthFront','CarBodyId'),('List_UpgradeCarBodyTireWidthRear','CarBodyId'),('List_UpgradeRimSizeFront','Ordinal'),('List_UpgradeRimSizeRear','Ordinal')]:
  rr=copy(t,key,353000 if key=='CarBodyId' else 353,body if key=='CarBodyId' else car)
  for i,r in enumerate(rr):
   if t=='List_UpgradeTireCompound':
    if r['IsStock']:c.execute(f'UPDATE {t} SET TireCompoundID=4 WHERE Id=?',(r['Id'],))
   else:
    col=('FrontTireWidth' if 'Front' in t else 'RearTireWidth') if 'TireWidth' in t else ('FrontWheelDiameter' if 'Front' in t else 'RearWheelDiameter')
    value=195+10*i if 'TireWidth' in t else 14+i
    c.execute(f'UPDATE {t} SET "{col}"=?,RequiresGraphics=0 WHERE Id=?',(value,r['Id']))
 # Use Golf's proportional weight reductions; retain Passat mass distribution and dimensions.
 rr=copy('List_UpgradeCarBodyWeight','CarBodyId',353000,body)
 for r in rr:
  level=r['Level'];mass=round(1230*r['Mass']/1100,1)
  c.execute('UPDATE List_UpgradeCarBodyWeight SET Mass=?,InitialMass=1230,CMHeight=?,CMBackFront=?,BlockDimX=1.705,BlockDimY=1.1,BlockDimZ=4.57,RequiresGraphics=0 WHERE Id=?',(mass,.52-.008*level,.61-.005*level,r['Id']))
 # Golf brakes provide stock/street/sport/race tiers, with stock 256/226 mm retained.
 copy('List_UpgradeBrakes','Ordinal',353,car)
 c.execute('UPDATE List_UpgradeBrakes SET RequiresGraphics=0 WHERE Ordinal=?',(car,))
 # Differential records must apply to the driven FRONT axle.
 copy('List_UpgradeDrivetrainDifferential','DrivetrainID',106,car)
 c.execute('UPDATE List_UpgradeDrivetrainDifferential SET RearLimitedSlipTorqueAccel=0,RearLimitedSlipTorqueDecel=0,CenterLimitedSlipTorqueAccel=0,CenterLimitedSlipTorqueDecel=0,RearToqueSplit=0 WHERE DrivetrainID=?',(car,))
 # Preserve baseline suspension feel, while restoring Golf's relative stage gains and tuning ranges.
 old_spring=rows('List_SpringDamperPhysics','Ordinal',car)
 baseline={True:next(r for r in old_spring if r['SpringDamperPhysicsID']==body),False:next(r for r in old_spring if r['SpringDamperPhysicsID']==body+100)}
 c.execute('DELETE FROM List_SpringDamperPhysics WHERE Ordinal=?',(car,))
 source=rows('List_SpringDamperPhysics','Ordinal',353)
 baseids=rows('List_UpgradeSpringDamper','Ordinal',353);stock=next(r for r in baseids if r['IsStock'])
 for original in source:
  r=original.copy()
  front=r['SpringDamperPhysicsID']<353100;srcbase=next(x for x in source if x['SpringDamperPhysicsID']==stock['FrontSpringDamperPhysicsID' if front else 'RearSpringDamperPhysicsID']);b=baseline[front]
  for k in ('DefRideHeight','MinRideHeight','MaxRideHeight','MaxCompressHeight'):r[k]=round(max(.04,b[k]+r[k]-srcbase[k]),5)
  for prefix,default in [('SpringRate','DefSpringRate'),('DampenBumpRate','DefDampenBumpRate'),('DampenReboundRate','DefDampenReboundRate')]:
   for tag in ('Def','Min','Max'):
    k=tag+prefix;r[k]=b[default]*r[k]/srcbase[default]
  r['SpringDamperPhysicsID']=body+r['SpringDamperPhysicsID']-353000;r['Ordinal']=car;insert('List_SpringDamperPhysics',r)
 copy('List_UpgradeSpringDamper','Ordinal',353,car)
 # Restore anti-roll-bar progression and ranges relative to the existing stock rates.
 for side in ('Front','Rear'):
  t='List_UpgradeAntiSway'+side;existing=rows(t,'Ordinal',car);base=next(r for r in existing if r['IsStock']);current=rows('List_AntiSwayPhysics','AntiSwayPhysicsID',base['AntiSwayPhysicsID'])[0]
  src=rows(t,'Ordinal',353);stockr=next(r for r in src if r['IsStock']);srcbase=rows('List_AntiSwayPhysics','AntiSwayPhysicsID',stockr['AntiSwayPhysicsID'])[0]
  for r in src:
   physics=rows('List_AntiSwayPhysics','AntiSwayPhysicsID',r['AntiSwayPhysicsID'])[0];newid=body+physics['AntiSwayPhysicsID']-353000
   c.execute('DELETE FROM List_AntiSwayPhysics WHERE AntiSwayPhysicsID=?',(newid,))
   for k in ('DefSwaybarStiffness','MinSwaybarStiffness','MaxSwaybarStiffness'):physics[k]=current['DefSwaybarStiffness']*physics[k]/srcbase['DefSwaybarStiffness']
   physics['AntiSwayPhysicsID']=newid
   if 'Ordinal' in physics:physics['Ordinal']=car
   insert('List_AntiSwayPhysics',physics)
  copy(t,'Ordinal',353,car)
 # Correct erroneous V8 displacement entries, preserving relative upgrade increments.
 for r in rows('List_UpgradeEngineDisplacement','EngineID',car):
  c.execute('UPDATE List_UpgradeEngineDisplacement SET Disp=? WHERE Id=?',(round(1984*r['Disp']/6424),r['Id']))
 import runpy,os
 runpy.run_path(os.path.join(S.HERE,'powertrain.py'))['apply'](c,S)
 c.row_factory=None
 print('Passat handling upgrade profile applied')
