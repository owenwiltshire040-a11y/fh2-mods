"""Validate the batch's actual packages, database references, media and source-fit reports."""
from pathlib import Path
import json,zipfile,sys,struct,zlib,re,sqlite3,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'fh2re'))
from modelbin import Bundle
from geometry import Part
from gltf_bridge import decode_group
from wheelfit import load_spec
manifest=json.loads((ROOT/'cars/daily_batch/build-manifest.json').read_text());cars=set();modids=set();stringkeys=set();reports=[]
for item in manifest:
 if len(sys.argv)>1 and item['slug'] not in ['daily'+x.zfill(2) for x in sys.argv[1:]]:continue
 folder=Path(item['spec']).parent;S=load_spec(folder/'spec.py');P=S.PHYSICS;pkg=ROOT/'output/Daily Drivers'/item['name'];meta=json.loads((pkg/'mod.json').read_text());fit=json.loads((pkg/'wheel-fit.json').read_text());db=json.loads((pkg/'database.json').read_text());tables=db['tables'];c=sqlite3.connect(folder/'build/custom.slt');c.row_factory=sqlite3.Row
 assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
 assert fit['valid'] and fit['database_checked'],(item['name'],fit.get('errors'))
 cid=P['car_id'];assert cid not in cars;cars.add(cid);assert meta['id'] not in modids;modids.add(meta['id'])
 for x in range(P['string_base'],P['string_base']+3):assert x not in stringkeys;stringkeys.add(x)
 car=c.execute('SELECT * FROM Data_Car WHERE Id=?',(cid,)).fetchone();assert car['CylinderID']==P['engine']['cylinders']
 drivetrain=c.execute('SELECT * FROM Data_Drivetrain WHERE DrivetrainID=?',(cid,)).fetchone();assert drivetrain['DrivetypeID']==P['drivetrain']['drivetype']
 trans=c.execute('SELECT * FROM List_UpgradeDrivetrainTransmission WHERE DrivetrainID=? AND IsStock=1',(cid,)).fetchone();assert trans['NumGears']==len(P['drivetrain']['gears'])+1
 for cam in c.execute('SELECT * FROM List_UpgradeEngineCamshaft WHERE EngineID=?',(cid,)):
  tor=c.execute('SELECT * FROM List_TorqueCurve WHERE TorqueCurveID=?',(cam['TorqueCurveFullThrottleID'],)).fetchone();assert tor and tor['ZeroThrottleTorqueScale']>0 and tor['NumTorqueValues']==cam['NumRPMEntriesArray']
  v=[tor['v'+str(j)] for j in range(tor['NumTorqueValues'])];assert all(x is not None and math.isfinite(x) for x in v);assert min(v)<-2 and max(v)>0
 zpath=pkg/'media/cars'/(S.MEDIA+'.zip');texcount=0;partcount=0
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None;names={n.lower() for n in z.namelist()}
  for name in z.namelist():
   if not name.lower().endswith('.modelbin'):continue
   raw=z.read(name);bundle=Bundle.read(raw)
   if any(b['tag']=='IndB' for b in bundle.blobs):
    part=Part(raw);partcount+=1
    for gid in part.group_order:
     attrs,_=decode_group(part,gid);assert np.isfinite(attrs['POSITION']).all(),(item['name'],name)
   for blob in bundle.blobs:
    if blob['tag']!='MatI':continue
    data=bytes(blob['data'])
    for m in re.finditer(rb'[Gg]ame:\\[ -~]+?\.swatchbin',data):
     path=m.group().decode()
     if '\\Textures\\custom\\' not in path:continue
     assert len(path)<120
     assert struct.unpack_from('<I',data,m.end())[0]==zlib.crc32(path.lower().encode())
     assert path.split('\\',4)[-1].replace('\\','/').lower() in names,(item['name'],path);texcount+=1
 assert partcount>=2 and texcount>0
 reports.append(dict(name=item['name'],car_id=cid,mod_id=meta['id'],wheel_fit=True,archive=True,model_parts=partcount,texture_refs=texcount,bytes=zpath.stat().st_size))
 print(item['name'],'PASS',partcount,'parts',texcount,'texture references',flush=True)
report_path=ROOT/'cars/daily_batch/validation.json'
if len(sys.argv)>1 and report_path.exists():
 previous={r['name']:r for r in json.loads(report_path.read_text())};previous.update({r['name']:r for r in reports});saved=list(previous.values())
else:saved=reports
report_path.write_text(json.dumps(saved,indent=2));print('PASS',len(reports),'packages, unique IDs/strings, SQLite, engine curves, fit and all media references')
