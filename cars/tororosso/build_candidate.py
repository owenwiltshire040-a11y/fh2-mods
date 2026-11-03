"""Build a staged STR1 update. Never writes to an installed game or running viewer."""
from pathlib import Path
import sys,json,zipfile,pickle,re,struct,copy,io,hashlib,shutil,math
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path[:0]=[str(P/'build/deps'),str(ROOT/'fh2re'),str(ROOT/'f1'),str(ROOT/'tex')]
from geometry import Part
from modelbin import Bundle
from body_swap import material_names,set_group,blank_group
from gltf_bridge import decode_group
from carbin import read_carbin,write_carbin
import fhmat,rimbuild,swatch
BASE=P/'input/confirmed-0.6.2';OUT=ROOT/'output/Toro Rosso STR1';WORK=P/'build';OUT.mkdir(exist_ok=True)
for file in BASE.glob('*'):
 if file.is_file():shutil.copy2(file,OUT/file.name)
D=json.loads((BASE/'database.json').read_text());T=D['tables'];CAR=3651;LIMIT=16700;COUNT=169;K=11900/16700
# Retain the confirmed chassis tuning and geometry; replace road-car upgrade paths.
for table,data in T.items():
 if table.startswith('List_Upgrade') and 'insert' in data:data['insert']=[r for r in data['insert'] if r.get('IsStock',1)]
engine=T['Data_Engine']['insert'][0];engine.update(MediaName='BMW_P83_03',EngineGraphingMaxTorque=330.,EngineGraphingMaxPower=540.)
text=(Path('/Users/owen/Desktop/untitled folder/TJ2005_engine.ini')).read_text(encoding='latin1');points=[tuple(map(float,x)) for x in re.findall(r'RPMTorque=\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)',text)];xs=np.array([x[0] for x in points]);ys=np.array([x[2] for x in points]);peak=float(ys.max())
cam=T['List_UpgradeEngineCamshaft']['insert'][0];curve_id=cam['TorqueCurveFullThrottleID'];curve=next(r for r in T['List_TorqueCurve']['insert'] if r['TorqueCurveID']==curve_id)
curve.update(TorqueScale=peak,ZeroThrottleTorqueScale=110.,NumTorqueValues=COUNT)
for i in range(246):curve['v'+str(i)]=max(float(np.interp(i*100,xs,ys)),0.)/peak if i*100<=LIMIT else -2.63 if i==168 else 0.
# Keep positive pull-away torque below idle, following the existing native table convention.
for i in range(11):curve['v'+str(i)]=max(curve['v10'],.05)
T['List_TorqueCurve']['insert']=[curve]
cam.update(RedlineRPM=float(LIMIT),StallRPM=2800.,StartRPM=8500.,TorqueCurveMaxRPM=16800.,NumRPMEntriesArray=COUNT,Level=3)
car=T['Data_Car']['insert'][0];power=max(i*100*math.pi/30*curve['v'+str(i)]*peak for i in range(168));car.update(SimPeakPower=power/100,SimPeakTorque=peak/100,SimPeakAngVel=LIMIT*math.pi/30,SimPeakTorqueAngVel=15500*math.pi/30,SimRedlineAngVel=LIMIT*math.pi/30)
trans=T['List_UpgradeDrivetrainTransmission']['insert'][0];trans.update(FinalDriveRatio=trans['FinalDriveRatio']/K,Level=3,GearShiftTime=.03)
T['Data_Drivetrain']['insert'][0]['ShiftSystemID']=6
for table in ['List_UpgradeBrakes','List_UpgradeSpringDamper','List_UpgradeAntiSwayFront','List_UpgradeAntiSwayRear','List_UpgradeDrivetrainDifferential','List_UpgradeDrivetrainClutch','List_UpgradeDrivetrainDriveline']:
 for row in T[table]['insert']:row['Level']=3
for r in T['List_UpgradeBrakes']['insert']:r.update(BrakeTorqueSlider=1,BrakeBiasSlider=1,FrontBrakeSizeMM=278.,RearBrakeSizeMM=278.,FrontBrakeTypeID=5,RearBrakeTypeID=5,FrontCaliperPistons=6,RearCaliperPistons=6,RequiresGraphics=0)
# Remove orphaned suspension/anti-sway records after the stock-only conversion.
used={r[k] for r in T['List_UpgradeSpringDamper']['insert'] for k in ['FrontSpringDamperPhysicsID','RearSpringDamperPhysicsID']};T['List_SpringDamperPhysics']['insert']=[r for r in T['List_SpringDamperPhysics']['insert'] if r['SpringDamperPhysicsID'] in used]
# F1 sound and free-rev configuration are supplied by the already-installed Williams package.
W=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods/Williams FW24');WD=json.loads((W/'database.json').read_text())['tables'];fr=copy.deepcopy(WD['FreeRevOverrides']['insert'][0]);fr['Ordinal']=CAR;T['FreeRevOverrides']=dict(key=['Ordinal'],insert=[fr]);(OUT/'database.json').write_text(json.dumps(D,indent=1))
meta=json.loads((OUT/'mod.json').read_text());meta.update(version='0.7.0',description='STR1 update: full 16,700-rpm CTDP V10 curve, F1 V10 audio, native digital dashboard, separate source-derived front/rear rims, carbon materials and stock race tuning. Offline-validated candidate; first driving check pending.',dependencies=['zs-williams-fw24']);(OUT/'mod.json').write_text(json.dumps(meta,indent=2))
Z=zipfile.ZipFile(next((BASE/'media/cars').glob('*.zip')));WZ=zipfile.ZipFile(W/'media/cars/WIL_F24_02.zip');names={n.lower():n for n in Z.namelist()};changes={};added={}
def part(suffix,z=Z):return Part(z.read(next(n for n in z.namelist() if n.lower().endswith(suffix.lower()))))
def material(p,name):return next(b for b in p.b.blobs if b['tag']=='MatI' and p.b.meta(b,'Name').decode()==name)
wp=part('/steeringwheel_a.modelbin',WZ);native_carbon=bytes(material(wp,'carbonfiber_004')['data']);native_digital=bytes(material(wp,'digitalGauge')['data'])
# Preserve body buffers, livery UVs and confirmed skeleton. Only the carbon material changes.
bp=part('/body_a.modelbin')
for b in bp.b.blobs:
 if b['tag']=='MatI' and bp.b.meta(b,'Name').decode()=='str1_carbon':b['data']=bytearray(native_carbon)
changes[names['scene/exterior/platform/body_a.modelbin']]=bp.build()
# Add an animated digital screen to the STR1's own steering wheel, on its existing bone.
G=pickle.loads((P/'input/source-geometry.pkl').read_bytes());sp=part('/steeringwheel_a.modelbin');sw=G['parts']['STEER_HR'];allv=np.concatenate([x['V'] for x in sw]);centre=(allv.min(0)+allv.max(0))/2
sb=Bundle.read(Z.read(names['scene/str_tororosso_1_06_skeleton.modelbin']));B3=None
for b in sb.blobs:
 if b['tag']!='Skel':continue
 b=b['data'];n=struct.unpack_from('<H',b)[0];o=2
 for _ in range(n):
  l=struct.unpack_from('<I',b,o)[0];o+=4;name=bytes(b[o:o+l]).decode();o+=l+6
  if name=='boneSteeringWheelSpindle':B3=np.array(struct.unpack_from('<16f',b,o)).reshape(4,4)[:3,:3]
  o+=64
assert B3 is not None
# Source has an explicit rectangular LCD above the wheel controls.
screen=np.concatenate([f['V'] for f in sw if f['mat']=='black']);lo,hi=screen.min(0),screen.max(0);z=float(lo[2]-.004)
V=np.array([[lo[0],lo[1],z],[hi[0],lo[1],z],[hi[0],hi[1],z],[lo[0],hi[1],z]]);VV=(V-centre)@B3.T;NN=np.tile([0,0,-1.],(4,1))@B3.T;UV=np.array([[0,1],[1,1],[1,0],[0,0]],float)
mid=fhmat.add_material(sp,'str1_digitalGauge',native_digital)
oldnames=material_names(sp);source_mesh=next(r for r in sp.render if oldnames[id(r['blob'])]=='str1_swheel');like=next(r for r in sp.render if r['group']==3)
mesh=fhmat.add_mesh(sp,like,mid);struct.pack_into('<h',mesh['blob']['data'],2,struct.unpack_from('<h',source_mesh['blob']['data'],2)[0]);struct.pack_into('<H',mesh['blob']['data'],4,3)
# The old wheel's group has no TEXCOORD0. Put the actual source controls in the UV-capable group.
wheel_mid=struct.unpack_from('<h',source_mesh['blob']['data'],0)[0];wheel_mesh=fhmat.add_mesh(sp,like,wheel_mid);struct.pack_into('<h',wheel_mesh['blob']['data'],2,struct.unpack_from('<h',source_mesh['blob']['data'],2)[0]);struct.pack_into('<H',wheel_mesh['blob']['data'],4,3)
source_mesh['indices']=[source_mesh['indices'][0]]*3
f=next(f for f in sw if f['mat']=='TR06WHEEL0');WV=(f['V']-centre)@B3.T;WN=f['N']@B3.T;WU=f['UV'].copy();WU[:,1]=1-WU[:,1];cnt=len(WV)
const={j:np.tile([.5,.5],(cnt+4,1)) for j in range(1,5)}
set_group(sp,3,dict(P=np.vstack([WV,VV]),N=np.vstack([WN,NN]),UV=np.vstack([WU,UV]),UVconst=const),{'str1_swheel':np.arange(cnt),'str1_digitalGauge':np.array([0,2,1,0,3,2])+cnt})
changes[names['scene/interior/dash/steeringwheel_a.modelbin']]=sp.build()
xaml=WZ.read('UI/WIL_F24_02.xaml').decode('utf-8-sig').replace('WIL_F24_02','STR_ToroRosso_1_06').replace('18200','16700').replace('19200','16700');added['UI/STR_ToroRosso_1_06.xaml']=xaml.encode()
for resource in WZ.namelist():
 if resource.lower().startswith('ui/textures/'):added[resource]=WZ.read(resource)
# Build both axles from the supplied source's wheel parts, preserving original atlas colours.
raw=Path('/Users/owen/Desktop/untitled folder/nefolder.glb').read_bytes();ln=struct.unpack_from('<I',raw,12)[0];J=json.loads(raw[20:20+ln]);B=raw[28+ln:]
def image_for(mat):
 m=next((m for m in J['materials'] if m.get('name')==mat),{});ti=m.get('pbrMetallicRoughness',{}).get('baseColorTexture',{}).get('index')
 if ti is None:return Image.new('RGB',(512,512),(25,25,28) if mat!='MCLHUB' else (150,155,160))
 im=J['images'][J['textures'][ti]['source']];v=J['bufferViews'][im['bufferView']];return Image.open(io.BytesIO(B[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])).convert('RGB')
atlas=Image.new('RGB',(1024,1024));mats=['MCLHUB','MCLRIM','MCLSPOKES_OP','SPOKE_FACE']
for i,m in enumerate(mats):atlas.paste(image_for(m).resize((512,512)),((i%2)*512,(i//2)*512))
atlas.save(P/'review/rim-atlas.png')
tpl=(ROOT/'tex/PEU_207SEHDi_08_Interior_DIFF_7b3d1f55-6273-410e-adf0-6ff29a14784f.swatchbin').read_bytes();rgba=np.dstack([np.array(atlas),np.full((1024,1024),255,np.uint8)]);added['Textures/str1/Swatches/str1_rim_atlas.swatchbin']=swatch.write_like(tpl,rgba)
texpath='Game:\\Media\\cars\\STR_ToroRosso_1_06\\Textures\\str1\\Swatches\\str1_rim_atlas.swatchbin'
# Shorten no paths here: all existing texture references and CRCs remain untouched.
steering_tex=next(b for b in bp.b.blobs if b['tag']=='MatI' and bp.b.meta(b,'Name').decode()=='str1_cockpit');texpaths=[x.decode() for x in re.findall(rb'[Gg]ame:\\[ -~]+?\.swatchbin',bytes(steering_tex['data']))];gloss=texpaths[-1]
# Reuse the proven source spoke reconstruction, separately for each axle.
code=(ROOT/'f1/str1_rims.py').read_text();code=code[code.index("SILVER ="):code.index('src = zipfile.ZipFile')];code=code.replace("geo = pickle.load(open(sys.argv[1], 'rb'))",'geo = SOURCE').replace("geo['parts']['HUB_LF']","geo['parts'][HUB]").replace("geo['wheels']['HUB_LF']","geo['wheels'][HUB]")
code=code.replace("p['N'] = p['N'].reshape(-1, 3, 3)[k].reshape(-1, 3)","p['N'] = p['N'].reshape(-1, 3, 3)[k].reshape(-1, 3); p['UV'] = p['UV'].reshape(-1, 3, 2)[k].reshape(-1, 2)")
reports={};wheelraw=Z.read(next(n for n in Z.namelist() if n.lower().endswith('_wheellf.modelbin')))
for axle,hub,width in [('front','HUB_LF',.280),('rear','HUB_LR',.340)]:
 env=dict(SOURCE=copy.deepcopy(G),HUB=hub,np=np,pickle=pickle,sys=sys);exec(compile(code,'source_spoke_reconstruction','exec'),env);parts=env['parts'];c=np.array(G['wheels'][hub]['centre']);vr=[];nr=[];ur=[];seen=set()
 for i,mat in enumerate(mats):
  for f in parts[mat]:
   sig=hashlib.sha256(f['V'].tobytes()).hexdigest()
   if sig in seen:continue
   seen.add(sig);v=f['V'].copy();n=f['N'].copy();uv=f.get('UV',np.zeros((len(v),2))).copy();uv-=np.floor(uv);uv=(uv*.49+.005)+[i%2,i//2];uv/=2
   vr.append(v);nr.append(n);ur.append(uv)
 V=np.concatenate(vr);N=np.concatenate(nr);U=np.concatenate(ur);rmax=float(np.hypot(V[:,1]-c[1],V[:,2]-c[2]).max());radial=.1651/rmax;V[:,1:]=c[1:]+(V[:,1:]-c[1:])*radial
 # Axial depth must fit the database tyre; keep the spoke face outward.
 depth=float(np.ptp(V[:,0]));depthscale=min(1.,(width-.020)/depth);V[:,0]=c[0]+(V[:,0]-V[:,0].min())*depthscale;N[:,0]/=max(depthscale,1e-6);N[:,1:]/=radial;N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)
 data=dict(parts={'SOURCE_RIM':[dict(V=V,N=N,UV=U)]},wheels={'HUB_LF':dict(centre=c,radius=G['wheels'][hub]['radius'])},ground=G['ground'],wheelbase=3.05)
 (WORK/(axle+'-geometry.pkl')).write_bytes(pickle.dumps(data))
 report=dict(nominal_rim_in=13,nominal_radius=.1651,outer_lip_radius=.1651,fitted_depth=float(np.ptp(V[:,0])),triangles=len(V)//3,source_hub=hub,radial_normalisation=radial,axial_normalisation=depthscale,selected_materials=mats);reports[axle]=report;(WORK/(axle+'-source-wheel.json')).write_text(json.dumps(report,indent=2))
 built,_=rimbuild.build_source_rim(wheelraw,data['parts'],['SOURCE_RIM'],c,.1651,texpath,gloss,(ROOT/'f1/matI_lod1.bin').read_bytes());added['scene/_library/Scene/Wheels/STR_ToroRosso_1_06_wheelL'+('F' if axle=='front' else 'R')+'.modelbin']=built
# Remap the rear wheel references only. Preserve all confirmed transforms/bones.
cn=next(n for n in Z.namelist() if n.lower().endswith('.carbin'));cb=read_carbin(Z.read(cn))
for pt in cb['parts']:
 if pt['part']['type']==43:
  for m in pt['part']['models']:
   if m.get('bone_name','').lower().endswith(('lr','rr')):m['path']=m['path'].replace('wheelLF','wheelLR').replace('wheellf','wheelLR')
changes[cn]=write_carbin(cb)
# Avoid leaving the previous wheel path active alongside the new front path (case-insensitive VFS).
for n in list(added):
 old=names.get(n.lower())
 if old:changes[old]=added.pop(n)
carzip=OUT/'media/cars/STR_ToroRosso_1_06.zip';carzip.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(carzip,'w',zipfile.ZIP_DEFLATED) as out:
 for n in Z.namelist():out.writestr(n,changes.get(n,Z.read(n)))
 for n,b in added.items():out.writestr(n,b)
# Copy existing presentation assets without touching any installed package.
shutil.copytree(BASE/'media/stripped',OUT/'media/stripped',dirs_exist_ok=True)
(WORK/'wheel-source-reports.json').write_text(json.dumps(reports,indent=2))
(WORK/'candidate-summary.json').write_text(json.dumps(dict(version='0.7.0',redline=LIMIT,curve_entries=COUNT,peak_nm=peak,power_hp=power/745.699872,final_drive=trans['FinalDriveRatio'],dependency='zs-williams-fw24',digital_screen_world_bounds=[lo.tolist(),hi.tolist()],runtime_tested=False),indent=2))
print('STAGED',carzip,flush=True)

# Packaging is complete only after the actual wheel/package checks pass.
import subprocess
subprocess.run([sys.executable,str(P/'validate_candidate.py')],cwd=ROOT,check=True)
