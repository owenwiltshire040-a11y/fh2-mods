from pathlib import Path
import json,sqlite3,zipfile,sys,struct,re,zlib
r=Path(__file__).resolve().parents[2];p=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'fh2re'))
from geometry import Part
from modelbin import Bundle
c=sqlite3.connect(p/'build/custom.slt');c.row_factory=sqlite3.Row
assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
car=c.execute('select * from Data_Car where Id=4107').fetchone();assert car['CylinderID']==11 and car['Displacement']==998 and car['FrontTireWidthMM']==155 and car['FrontTireAspect']==65
assert c.execute('select FrontTireWidth from List_UpgradeCarBodyTireWidthFront where CarBodyId=4107000 and IsStock=1').fetchone()[0]==155
assert c.execute('select Mass from List_UpgradeCarBodyWeight where CarBodyId=4107000 and IsStock=1').fetchone()[0]==790
for row in c.execute('select * from List_UpgradeEngineCamshaft where EngineID=4107'):
 curve=c.execute('select * from List_TorqueCurve where TorqueCurveID=?',(row['TorqueCurveFullThrottleID'],)).fetchone();assert curve and curve['ZeroThrottleTorqueScale']>0 and all(v is not None for v in curve)
 assert curve['v'+str(int(row['RedlineRPM']/100)+1)]==-2.63
out=r/'output/Peugeot 107 2006';d=json.loads((out/'database.json').read_text());assert d['tables']['Data_Car']['insert'][0]['MakeID']==201
fit=json.loads((out/'wheel-fit.json').read_text());assert fit['valid'] and fit['database_checked']
z=zipfile.ZipFile(out/'media/cars/PEU_107Urban_2006_.zip');assert z.testzip() is None;names={n.lower() for n in z.namelist()};count=0
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
   assert len(path)<120;assert struct.unpack_from('<I',raw,m.end())[0]==zlib.crc32(path.lower().encode());assert path.split('\\',4)[-1].replace('\\','/').lower() in names;count+=1
assert count>20
selection=json.loads((p/'source-selection.json').read_text());assert not any('107R' in n or '_jdm_' in n or n=='body' for n in selection['chosen'])
print('107 engine, tyres, upgrades, fit report, short texture paths/CRCs, mesh decoding and early-body selection passed;',count,'texture references')
