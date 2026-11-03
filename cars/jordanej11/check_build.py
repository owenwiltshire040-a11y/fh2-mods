"""Validate the EJ11 package before touching the installed mods."""
from pathlib import Path
import sys,sqlite3,json,zipfile,math,re,struct,zlib,pickle
import numpy as np
p=Path(__file__).resolve().parent;r=p.parents[1];sys.path.insert(0,str(r/'fh2re'))
from modelbin import Bundle
from geometry import Part
from carbin import read_carbin
from body_swap import material_names
from gltf_bridge import decode_group
c=sqlite3.connect(p/'build/custom.slt');c.row_factory=sqlite3.Row
assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
car=c.execute('select * from Data_Car where Id=4201').fetchone()
assert car['CylinderID']==5 and car['Displacement']==2994 and car['NumGears']==7 and car['IsOpenWheel']==1 and car['IsOpenCockpit']==1
assert c.execute('select ShiftSystemID from Data_Drivetrain where DrivetrainID=4201').fetchone()[0]==6
cam=c.execute('select * from List_UpgradeEngineCamshaft where EngineID=4201 and IsStock=1').fetchone();curve=c.execute('select * from List_TorqueCurve where TorqueCurveID=?',(cam['TorqueCurveFullThrottleID'],)).fetchone()
assert cam['RedlineRPM']==17300 and cam['NumRPMEntriesArray']==175 and curve['NumTorqueValues']==175
assert curve['ZeroThrottleTorqueScale']>0 and all(v is not None for v in curve) and curve['v174']==-2.63 and curve['v173']>0
hp=max(i*100*math.pi/30*curve['TorqueScale']*curve['v'+str(i)]/745.6999 for i in range(174));assert 780<hp<800
assert c.execute('select Mass from List_UpgradeCarBodyWeight where CarBodyId=4201000 and IsStock=1').fetchone()[0]==600
assert c.execute('select TireModelName from List_UpgradeTireCompound where Ordinal=4201 and IsStock=1').fetchone()[0]=='OW_F1'
assert c.execute('select CarBucket from Data_Car_Buckets where CarId=4201').fetchone()[0]==26
out=r/'output/Jordan EJ11 2001';fit=json.loads((out/'wheel-fit.json').read_text());assert fit['valid'] and fit['database_checked']
assert abs(fit['model_wheelbase']-3.12933269)<.00001
for corner,row in fit['corners'].items():assert abs(row['tyre_centre'][0]-row['source_axle'][0])<.03 and abs(row['height_error'])<.005
meta=json.loads((out/'mod.json').read_text());assert meta['id']=='owen-jordan-ej11' and 'zs-williams-fw24' in meta['dependencies']
z=zipfile.ZipFile(out/'media/cars/JOR_JordanEJ11_01_.zip');assert z.testzip() is None;names={n.lower() for n in z.namelist()};count=0
for name in z.namelist():
 if not name.lower().endswith('.modelbin'):continue
 b=Bundle.read(z.read(name))
 if any(bl['tag']=='IndB' for bl in b.blobs):Part(z.read(name))
 for bl in b.blobs:
  if bl['tag']!='MatI':continue
  raw=bytes(bl['data'])
  for m in re.finditer(rb'[Gg]ame:\\[ -~]+?\.swatchbin',raw):
   path=m.group().decode()
   if '\\Textures\\custom\\' not in path:continue
   assert len(path)<120 and struct.unpack_from('<I',raw,m.end())[0]==zlib.crc32(path.lower().encode())
   assert path.split('\\',4)[-1].replace('\\','/').lower() in names;count+=1
assert count>30
lights=z.read('Lights.bin');assert struct.unpack_from('<I',lights,8)[0]==1;length=struct.unpack_from('<I',lights,12)[0];off=18+length;assert struct.unpack_from('<I',lights,off)[0]==2
assert len(z.read('physicsdefinition.bin'))==2244 and struct.unpack_from('<f',z.read('physicsdefinition.bin'),92)[0]<.73
cname=next(n for n in z.namelist() if n.lower().endswith('.carbin'));carbin=read_carbin(z.read(cname));kept=[m['path'].lower() for pt in carbin['parts'] for m in pt['part']['models']]
assert any(n.endswith('steeringwheel_a.modelbin') for n in kept) and not any('headlight' in n for n in kept)
# The animated wheel's geometry is local to the moved spindle, not left in body space.
n=next(n for n in z.namelist() if n.lower().endswith('/steeringwheel_a.modelbin'));part=Part(z.read(n));v=decode_group(part,0)[0]['POSITION'][:,:3];assert np.ptp(v,axis=0).max()<.6
print('PASS: 17,300 rpm V10, complete idle/cutoff curve (~'+str(round(hp))+' bhp), 7 gears, race tyres, exposed-wheel fit, animated steering geometry, collision hull, rear light, archive and',count,'texture references')
