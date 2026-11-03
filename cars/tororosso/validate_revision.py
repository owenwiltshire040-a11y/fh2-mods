"""Offline package, engine, cockpit, wheel and installation-isolation checks."""
from pathlib import Path
import sys,json,zipfile,struct,re,hashlib,math,types,pickle,xml.etree.ElementTree as ET
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'f1')]
from geometry import Part
from modelbin import Bundle
from body_swap import material_names
from gltf_bridge import decode_group
from carbin import read_carbin
from wheelcheck import check
O=ROOT/'output/Toro Rosso STR1';D=json.loads((O/'database.json').read_text())['tables'];B=json.loads((P/'input/confirmed-0.6.2/database.json').read_text())['tables'];C=3651
cam=D['List_UpgradeEngineCamshaft']['insert'][0];curve=D['List_TorqueCurve']['insert'][0];assert cam['RedlineRPM']==16700 and cam['NumRPMEntriesArray']==curve['NumTorqueValues']==169
assert all(curve['v'+str(i)] is not None for i in range(246)) and curve['v168']==-2.63 and curve['v167']>0 and curve['ZeroThrottleTorqueScale']>0
hp=max(i*100*math.pi/30*curve['TorqueScale']*curve['v'+str(i)]/745.699872 for i in range(168));assert 715<hp<730 and 310<curve['TorqueScale']<325
old=B['List_UpgradeDrivetrainTransmission']['insert'][0];new=D['List_UpgradeDrivetrainTransmission']['insert'][0]
assert abs(new['FinalDriveRatio']*11900/16700-old['FinalDriveRatio'])<1e-9
assert all(new['GearRatio'+str(i)]==old['GearRatio'+str(i)] for i in range(8))
assert D['Data_CarBody']==B['Data_CarBody'] and D['CameraOverrides']==B['CameraOverrides']
G=pickle.loads((P/'input/source-geometry.pkl').read_bytes());body=D['Data_CarBody']['insert'][0];assert abs(G['wheelbase']-body['ModelWheelbase'])<.02 and abs(body['Wheelbase']-body['ModelWheelbase'])<.01
for axle,width,aspect in [('HUB_LF',280,59),('HUB_LR',340,48)]:assert abs(G['wheels'][axle]['radius']-(.1651+width/1000*aspect/100))<.01
for table,data in B.items():
 if table.startswith('List_Upgrade'):
  assert {r['Id'] for r in data.get('insert',[])}=={r['Id'] for r in D[table].get('insert',[])},table
assert D['Data_Engine']['insert'][0]['MediaName']=='BMW_P83_03'
assert 'zs-williams-fw24' in json.loads((O/'mod.json').read_text())['dependencies']
zpath=O/'media/cars/STR_ToroRosso_1_06.zip';z=zipfile.ZipFile(zpath);assert z.testzip() is None;names={n.lower():n for n in z.namelist()};count=0
for n in z.namelist():
 if not n.lower().endswith('.modelbin'):continue
 p=Part(z.read(n)) if any(b['tag']=='IndB' for b in Bundle.read(z.read(n)).blobs) else None
 if not p:continue
 for gid in p.groups:
  a,_=decode_group(p,gid);assert np.isfinite(a['POSITION']).all()
 for bl in p.b.blobs:
  if bl['tag']!='MatI':continue
  for path in re.findall(rb'[Gg]ame:\\[ -~]+?\.swatchbin',bytes(bl['data'])):
   text=path.decode().lower().replace('\\','/');prefix='game:/media/cars/str_tororosso_1_06/'
   if text.startswith(prefix):assert text[len(prefix):] in names,(n,text);count+=1
dashboard='ui/str_tororosso_1_06.xaml' in names
if dashboard:
 x=z.read(names['ui/str_tororosso_1_06.xaml']).decode();ET.fromstring(x);assert 'MaxRpm="16700"' in x and 'DigitalGauge.STR_ToroRosso_1_06' in x
 assert '<Image' not in x and '<Storyboard' not in x
sp=Part(z.read(names['scene/interior/dash/steeringwheel_a.modelbin']));nm=material_names(sp);r=next(r for r in sp.render if nm[id(r['blob'])]=='str1_digitalGauge');a,_=decode_group(sp,r['group']);assert 'TEXCOORD0' in a and len(r['indices'])==(6 if dashboard else 3)
source=next(r for r in sp.render if nm[id(r['blob'])]=='str1_swheel' and len(r['indices'])>3);assert source['group']==3
cb=read_carbin(z.read(next(n for n in z.namelist() if n.lower().endswith('.carbin'))));original=zipfile.ZipFile(next((P/'input/confirmed-0.6.2/media/cars').glob('*.zip')));oc=read_carbin(original.read(next(n for n in original.namelist() if n.lower().endswith('.carbin'))))
a=[m for q in cb['parts'] for m in q['part']['models'] if q['part']['type']==43];b=[m for q in oc['parts'] for m in q['part']['models'] if q['part']['type']==43];assert len(a)==len(b)==4
for m,n in zip(a,b):assert m['transform']==n['transform'] and m['bone_name']==n['bone_name']
assert len({m['path'].lower() for m in a})==2
reports={}
for axle,width in [('front',280),('rear',340)]:
 folder=P/'build'/axle;folder.mkdir(exist_ok=True);(folder/'source-wheel.json').write_text((P/'build'/(axle+'-source-wheel.json')).read_text())
 S=types.SimpleNamespace(HERE=str(folder),GEO=str(P/'build'/(axle+'-geometry.pkl')),DONOR_ZIP='/Users/owen/Desktop/untitled folder/DOD_ChargerSRT8_12.zip',PHYSICS={'tyres':dict(width_front=width,width_rear=width,aspect_front=59 if axle=='front' else 48,aspect_rear=48,rim_in=13)},REQUIRE_SOURCE_WHEELS=True,RIM_MATERIALS=['SOURCE_RIM'],RIM_R_REF=.1651)
 file=zpath
 if axle=='rear':
  file=folder/'wheel-check.zip'
  with zipfile.ZipFile(file,'w') as tmp:tmp.writestr('scene/STR_ToroRosso_1_06_wheelLF.modelbin',z.read(names['scene/_library/scene/wheels/str_tororosso_1_06_wheellr.modelbin']))
 reports[axle]=check(S,file)
# An offline check must never alter the installed car.
base=json.loads((P/'input/installed-baseline.json').read_text());installed=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods/Toro Rosso STR1')
assert all(hashlib.sha256((installed/f).read_bytes()).hexdigest()==h for f,h in base.items())
result=dict(valid=True,runtime_tested=False,power_hp=hp,redline=16700,texture_references_checked=count,wheels=reports,live_install_unchanged=True,confirmed_chassis_and_camera_preserved=True,gear_speeds_preserved=True,dashboard_assets_complete=True,legacy_component_ids_preserved=True,dashboard_enabled=dashboard,steering_primary_uvs_present=True)
(P/'build/revision-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
