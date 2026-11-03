"""Build the downloaded daily-driver collection as individually reviewable prototypes."""
from pathlib import Path
import sys,json,pickle,copy,hashlib,re,subprocess,importlib.util
import numpy as np,trimesh
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'cars/daily_batch';sys.path.insert(0,str(ROOT/'fh2re'))
# Explicit source measurements: x lateral, y vertical, z forward after the axis map.
CONFIG=[
# name, frame, source front/rear, source height, source half track, tyre radius, target wheelbase, mass, hp, Nm, year
('Ford Fiesta 2002','x,y,-z',1.075,-1.28,-.307,.66,.29,2.486,1040,79,124,2002),
('Ford Focus Mk1','-x,z,-y',1.35,-1.27,.31,.75,.30,2.615,1150,99,145,2001),
('Ford Focus Mk2 ST','-x,y,z',.01323,-.01323,.001805,.0077,.00318,2.640,1362,222,320,2006),
('Ford Mondeo Mk3','-x,y,z',143.35,-134.42,34.03,74.27,34.03,2.754,1375,143,190,2003),
('Opel Corsa C','-x,y,z',1.25,-1.25,.26,.739,.25,2.491,980,74,110,2003),
('Opel Astra G','-x,y,z',13.199,-14.279,3.172,7.572,3.172,2.606,1120,99,150,2001),
('Opel Astra H','-x,y,z',.407,.103,-.095,.084,.034,2.614,1230,104,150,2005),
('Opel Vectra B','-x,y,z',1.45,-1.33,.33,.78,.321,2.637,1290,134,188,2001),
('Opel Vectra C','-x,y,z',1.30,-1.35,.30,.76,.30,2.700,1400,120,167,2003),
('Opel Zafira A','-x,y,z',1.357,-1.355,.30524,.69,.30524,2.694,1393,123,170,2002),
('Volkswagen Polo Mk3','-x,y,z',1.474,-1.294,.334,.81,.332,2.407,980,74,135,1996),
('Volkswagen Polo Mk4','x,z,-y',.11014,-.12915,.03113,.07342,.03112,2.460,1050,74,126,2003),
('Ford Ka','pca',1.0,-1.0,.0,.7,.29,2.448,890,59,105,2000),
('Renault Laguna II','-x,z,y',1.363,-1.395,-.17,.765,.317,2.748,1395,163,270,2003),
('Citroen Xsara','-x,z,y',1.45,-1.518,-.26,.889,.332,2.540,1130,108,147,2004),
('Volvo S60R','-x,z,y',1.55,-1.55,-.335,.9,.37,2.715,1620,296,400,2004),
('Volkswagen Passat B5.5','-x,z,y',1.675,-1.383,-.2,.865,.341,2.703,1390,148,210,2003),
('Fiat Punto Mk2','-x,z,y',1.359,-1.475,-.666,.857,.345,2.460,935,59,102,2002),
]
PAINT={'Ford Fiesta 2002':['primary'],'Ford Focus Mk1':['body'],'Ford Focus Mk2 ST':['Paint'],'Ford Mondeo Mk3':['carpaint.001'],'Opel Corsa C':['body'],'Opel Astra G':['body'],'Opel Astra H':['956_0'],'Opel Vectra B':['vectra'],'Opel Vectra C':['htvectrac_body'],'Opel Zafira A':['Carro_Pintura'],'Volkswagen Polo Mk3':['body_amarelo','body_vermelho','body_verde','body_azul_escuro'],'Volkswagen Polo Mk4':['carpaint']}
MAKES={'Ford':(14,'_&857938260','FOR',2),'Volkswagen':(52,'_&857938517','VW',7),'Renault':(41,'_&857955285','REN',4),'Volvo':(53,'_&857938645','VOL',11),'Fiat':(57,'_&857938133','FIA',8)}

def load_source(name):
 cat=json.loads((ROOT.parent/'Car Model Downloads/catalogue.json').read_text());c=next(c for c in cat if c['name']==name)
 p=ROOT.parent/'Car Model Downloads'/c['file']
 return (p if p.suffix=='.glb' else BASE/name/'source.glb'),c

def prepare(index):
 name,frame,zf,zr,yc,xh,rad,wb,mass,hp,nm,year=CONFIG[index];slug='daily'+str(index+1).zfill(2);folder=ROOT/'cars'/slug;folder.mkdir(exist_ok=True);(folder/'textures').mkdir(exist_ok=True)
 source,credits=load_source(name);sc=trimesh.load(source,force='scene');parts={};textures={};maps={};chosen=[];dropped=[];seen=set();s=wb/(zf-zr);raw=[]
 if frame=='pca':
  # Draft includes four enormous presentation-plane triangles. Fit horizontal PCA to car vertices only.
  pts=np.concatenate([m.vertices for m in sc.geometry.values() if isinstance(m,trimesh.Trimesh) and len(m.faces)>20]);q=pts[:,[0,2]];centre=q.mean(0);_,_,vh=np.linalg.svd(q-centre,full_matrices=False);long=vh[0];long*=1 if long[0]>0 else -1;across=np.array([-long[1],long[0]]);rot=np.array([[across[0],0,across[1]],[0,1,0],[long[0],0,long[1]]]);sourcecentre=np.array([centre[0],0,centre[1]]);rot[2]*=-1
 else:
  axes=frame.split(',');rot=np.zeros((3,3))
  for j,a in enumerate(axes):rot[j,'xyz'.index(a[-1])]=-1 if a.startswith('-') else 1
  sourcecentre=np.zeros(3)
 for node in sc.graph.nodes_geometry:
  T,key=sc.graph[node];m=sc.geometry[key]
  if not isinstance(m,trimesh.Trimesh):continue
  mat=getattr(m.visual.material,'name',None) or node
  V=trimesh.transform_points(m.vertices,T);N=m.vertex_normals@np.linalg.inv(T[:3,:3]);N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9);F=m.faces.copy();uv=getattr(m.visual,'uv',None);uv=np.asarray(uv) if uv is not None else np.zeros((len(V),2));V=(V-sourcecentre)@rot.T;N=N@rot.T
  if np.linalg.det(rot@T[:3,:3])<0:F=F[:,::-1]
  if name=='Ford Focus Mk1' and (abs((V[:,0].min()+V[:,0].max())/2+4.55249)>1.2 or V[:,2].min() < -2.35 or V[:,2].max()>2.35):dropped.append(node);continue
  if name=='Ford Fiesta 2002' and (np.abs(V[:,0]).max()>1.05 or np.abs(V[:,2]).max()>2.15):dropped.append(node);continue
  if name=='Ford Focus Mk1' and (node in ['7','252','138','91_9082f4','92_5bdd36'] or mat.startswith('neon_')):dropped.append(node);continue
  if name=='Ford Ka' and (len(F)<10 or node in ['lambert5SG','lambert4SG','blinn1SG']):dropped.append(node);continue
  if name=='Opel Astra H' and (V[:,1].max()>.09 or V[:,1].min()<-.14):dropped.append(node);continue
  # Remove exact duplicates, including duplicate wheel/trim exports.
  sig=(mat,hashlib.sha256(np.round(V[F],5).tobytes()).hexdigest())
  if sig in seen:dropped.append(node);continue
  seen.add(sig);raw.append([node,mat,V,N,F,uv,m.visual.material])
 if name=='Ford Ka':
  verts=np.concatenate([r[2] for r in raw]);lo,hi=verts.min(0),verts.max(0);length=hi[2]-lo[2];zf=lo[2]+length*.81;zr=lo[2]+length*.134;yc=lo[1]+length*.075;xh=(hi[0]-lo[0])*.40;rad=length*.075;s=wb/(zf-zr)
 # Centre body from selected paint rather than mirrors/accessory bounding boxes.
 paintverts=[r[2] for r in raw if r[1] in PAINT.get(name,['paint'])]
 if not paintverts:paintverts=[r[2] for r in raw if len(r[4])>1000 and not r[0].lower().startswith('wheel')]
 vv=np.concatenate(paintverts);cx=(vv[:,0].min()+vv[:,0].max())/2
 shift=np.array([-cx*s,.151-yc*s,.0867-(zf+zr)/2*s]);wheels={key:dict(centre=np.array([side*xh*s,.151,z*s+shift[2]]),radius=rad*s) for key,side,z in [('HUB_LF',-1,zf),('HUB_RF',1,zf),('HUB_LR',-1,zr),('HUB_RR',1,zr)]}
 for node,mat,V,N,F,uv,material in raw:
  V=V*s+shift;tri=V[F];c=tri.mean(1);keep=np.ones(len(F),bool)
  # Whole tyre/rim nodes are removed; other materials are cut only within measured wheel envelopes.
  wheelnode=any(t in (node+' '+mat).lower() for t in ['tire','tyre','carro_pneu','carro_roda','teker','wheel','ratas','jante','rim_high','brakedisc','brakedisk'])
  if wheelnode:keep[:]=False
  else:
   for w in wheels.values():
    ctr=w['centre'];near=(np.abs(c[:,0]-ctr[0])<max(.19,rad*s*.7))&(np.hypot(c[:,1]-ctr[1],c[:,2]-ctr[2])<rad*s*1.00)
    keep&=~near
   # Shared BeamNG exports include a loose wheel below the chassis at the origin.
   if name in ['Opel Corsa C','Opel Vectra C'] and V[:,1].max()<.15 and np.max(np.abs(V[:,2]-.0867))<.35:keep[:]=False
  if not keep.any():dropped.append(node);continue
  F=F[keep];chosen.append(node);parts.setdefault(mat,[]).append(dict(node=node,mat=mat,V=V[F].reshape(-1,3),N=N[F].reshape(-1,3),UV=uv[F].reshape(-1,2)))
  if mat in maps:continue
  low=mat.lower();paint=mat in PAINT.get(name,['paint'])
  # Only true window surfaces use the windscreen shader. Light lenses retain source colours.
  glass=(any(t in low for t in ['windowglass','windscreen','vectra_glass','hatch_glass','htvectrac_glass','carro_vidros','vidro_ext','vidro_int']) and not any(t in low for t in ['lights','vermel','lantern'])) or low in ['glass','glass1','rgba_255_255_255_64']
  if 'glass' in low and not any(t in low for t in ['red','orange','black_glass','invisible']):glass=True
  if low.startswith('rgba_') and int(low.split('_')[-1])<240:glass=True
  if name=='Ford Ka':paint=mat=='phong1SG';glass=mat in ['lambert2SG','aiStandardSurface1SG']
  if paint:maps[mat]=('plain','paint')
  elif glass:maps[mat]=('plain','glass')
  elif 'chrome' in low or low=='mirror':maps[mat]=('plain','chrome')
  else:
   image=getattr(material,'baseColorTexture',None)
   if image is None:image=getattr(material,'image',None)
   if image is None:
    factor=getattr(material,'baseColorFactor',None)
    if factor is None:factor=getattr(material,'diffuse',None)
    rgb=tuple(int(x) for x in factor[:3]) if factor is not None else (65,65,70)
    if 'black' in low:rgb=(25,25,28)
    image=Image.new('RGB',(8,8),rgb)
   key='t'+hashlib.sha1(mat.encode()).hexdigest()[:8];fn=key+'.png';image.convert('RGB').thumbnail((1024,1024)) if False else None
   image=image.convert('RGB');image.thumbnail((1024,1024));image.save(folder/'textures'/fn);textures[key]=fn;maps[mat]=('textured',key)
 if not any(p==('plain','paint') for p in maps.values()):
  # Keep fixed-colour source body where no reliable paint material was supplied, with arch measurements on all body surfaces.
  arch=[]
  for pl in parts.values():arch.extend(pl)
  parts['FIT_ARCH']=arch;maps['FIT_ARCH']=None
 allv=np.concatenate([p['V'] for mat,ps in parts.items() if mat!='FIT_ARCH' for p in ps]);lo,hi=allv.min(0),allv.max(0)
 # The axle reference uses the measured source geometry, aligned to the donor's runtime height.
 G=dict(parts=parts,wheels=wheels,ground=.151-rad*s,wheelbase=wb,materials=sorted(parts));pickle.dump(G,open(folder/'geo.pkl','wb'))
 q=importlib.util.spec_from_file_location('base_spec',ROOT/'cars/peugeot107/spec.py');B=importlib.util.module_from_spec(q);q.loader.exec_module(B);P=copy.deepcopy(B.PHYSICS)
 make=name.split()[0];makeinfo=MAKES.get(make);modelname=name[len(make)+1:];code=makeinfo[2] if makeinfo else ('OPE' if make=='Opel' else 'CIT');media=(code+'_'+slug+'_'+str(year)).ljust(18,'_');assert len(media)==18
 P.update(car_id=5001+index,make_offset=100+index,make=make,make_profile=make,make_code=code,make_country=makeinfo[3] if makeinfo else 7 if make=='Opel' else 4,make_icon='ARI',string_base=65200+index*3,colour_offset=1500+index*100,name=modelname,short_name=modelname)
 E=P['engine'];E.update(name=('2.5L I5 Turbo' if name=='Volvo S60R' else '2.5L I5 Turbo' if 'Mk2 ST' in name else 'Prototype road engine'),sound='FOR_FocusST_12' if name in ['Volvo S60R','Ford Focus Mk2 ST'] else 'FOR_FiestaST_14',mass=110.,peak_hp=hp,peak_nm=nm,redline=6500,displacement=2521 if name in ['Volvo S60R','Ford Focus Mk2 ST'] else 1600,inertia=.16,stall=750.,start=3000.)
 capacities=[1388,1596,2521,1999,1199,1598,1598,1998,1796,1796,1598,1390,1299,1998,1587,2521,1781,1242]
 E.update(name=f'{capacities[index]/1000:.1f}L I'+('5 Turbo' if index in [2,15] else '4 Turbo' if index in [13,16] else '4'),displacement=capacities[index],cylinders=2 if index in [2,15] else 1,sound='FOR_FocusRS_09' if index in [2,15] else 'FOR_Fiesta_09',aspiration=2 if index in [2,13,15,16] else 1,boost=1.0 if index in [2,13,15,16] else 0.)
 E['curve']=[(0,nm*.30),(1000,nm*.50),(2000,nm*.80),(3500,nm),(4500,nm*.95),(5500,min(nm*.90,hp*745.6999/(5500*np.pi/30))),(6000,min(nm*.80,hp*745.6999/(6000*np.pi/30))),(6500,nm*.55)]
 P['drivetrain'].update(gears=[3.545,1.904,1.281,.951,.756],final_drive=3.70,clutch_nm=max(250,nm*1.5))
 if index in [2,13,15]:P['drivetrain']['gears']=[3.231,1.952,1.321,1.029,.821,.685]
 if index==15:P['drivetrain']['drivetype']=3;P['drivetrain']['lsd']=(.1,.05,.1,.05)
 for key in ['front','rear']:P['suspension'][key]=tuple(v*mass/790 for v in P['suspension'][key])
 P['brakes'].update(front_mm=320 if hp>180 else 280 if mass>1200 else 256,rear_mm=280 if hp>180 else 230,rear_type=2 if mass>1200 else 1)
 P['body'].update(mass=mass,weight_front=.60,block=tuple([float(hi[0]-lo[0]),float(hi[1]-lo[1]),float(hi[2]-lo[2])]),height=float(hi[1]-lo[1]),length=float(hi[2]-lo[2]),width=float(hi[0]-lo[0]),wheelbase=wb,model_wheelbase=wb,track_front='auto',track_rear='auto',ride_height=.16,bbox=tuple([float(lo[0]),float(hi[0]),float(lo[1]),float(hi[1]),float(lo[2]),float(hi[2])]))
 radius=rad*s;rim=max(13,min(19,round((radius-.105)*2/.0254)));width=225 if hp>180 else 185;aspect=round((radius-rim*.0254/2)/(width/1000)*20)*5
 P['tyres'].update(width_front=width,width_rear=width,aspect_front=aspect,aspect_rear=aspect,rim_in=rim)
 P['car'].update(year=year,price=10000,top_mph=145. if hp>180 else 110.,t60=6.5 if hp>180 else 12.,bucket=23)
 PR=dict(paint='6b92b1')
 if makeinfo:PR['use_make']=makeinfo[:2]
 elif make=='Opel' and index!=4:PR.update(use_make=(304,'_&'+str((857977229>>16<<16)|65212)),depends='owen-daily05')
 else:PR.update(logo_text=make.upper(),icon_base=make)
 steer=(-.34,.151+radius*1.4,.4);hips=(-.34,.151+radius*.45,-.05);eye=(-.34,.151+radius*2.8,.0)
 lines=['"""'+name+' — personal prototype. Dimensions based on source axle measurements.','Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.','"""','import os','from PIL import Image','HERE=os.path.dirname(os.path.abspath(__file__))',f'MEDIA={media!r}',"DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')","GEO=os.path.join(HERE,'geo.pkl')","TEXTURES={}"]
 for k,fn in textures.items():lines.append(f"TEXTURES[{k!r}]=(Image.open(os.path.join(HERE,'textures',{fn!r})),512,False)")
 lines+=['MATERIALS='+repr(maps),"BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}","GLASS_PLAIN={'glass':(0,'gls_windsheild')}","BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}","KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}","RIM_MATERIALS=[]","ONE_SIDED=True","PRESERVE_UV_SEAMS=True","RIM_TRUST_NORMALS=True","TRACK_REFERENCE='rim_face'","RIM_FACE_GAP=.01","WHEEL_FIT=dict(profile='charger_rim_face')",'STEER='+repr(tuple(map(float,steer))),'HIPS='+repr(tuple(map(float,hips))),'EYE='+repr(tuple(map(float,eye))),'DRIVER_ANIMS_ZIP=None','AVPINS_TEMPLATE=None','PRESENT='+repr(PR),'PHYSICS='+repr(json.loads(json.dumps(P)))]
 # When source paint is fixed or textured, measure arches without modifying the visible materials.
 lines += ["ARCH_MATERIALS="+repr([m for m,plan in maps.items() if plan==('plain','paint')] or [m for m,plan in maps.items() if plan and plan!=('plain','glass')])]
 lines.append("UPGRADE_PROFILE='../daily_batch/upgrade_profile.py'")
 (folder/'spec.py').write_text('\n'.join(lines)+'\n');pkg=folder/'pkg'/name;pkg.mkdir(parents=True,exist_ok=True)
 meta=dict(format_version=1,id='owen-'+slug,name=name+' (prototype)',author='Owen',version='0.1.0',description='Personal source-model conversion. Provisional handling/cockpit; generic donor wheels; source measured fit. See BUILD-NOTES.txt.',database='database.json',strings='strings.json',media='media')
 (pkg/'mod.json').write_text(json.dumps(meta,indent=2));(pkg/'CREDITS.txt').write_text((ROOT.parent/'Car Model Downloads'/credits['file']).parent.joinpath('CREDITS.txt').read_text()+'\nConversion uses DragonFF (GPL-3.0) format readers where applicable: https://github.com/Parik27/DragonFF\n')
 notes=f'{name}\nPersonal prototype v0.1.0. Not in-game validated. Generic donor rims are used in this first pass. Source lamps are decorative until individually mapped. Interior retains available source geometry; camera/driver positions are provisional.\nSource: {credits["url"]}\nScale {s:.8f}; source axle spacing {zf-zr:.6f}; target axle spacing {wb:.3f}m. Source wheel radius {radius:.4f}m.\nHandling is a provisional road-car setup, not a verified factory specification.\n'
 (folder/'BUILD-NOTES.txt').write_text(notes);(pkg/'BUILD-NOTES.txt').write_text(notes);(folder/'selection.json').write_text(json.dumps(dict(source=str(source),chosen=chosen,dropped=dropped,frame=frame,scale=s,source_front=zf,source_rear=zr,source_y=yc,bounds=[lo.tolist(),hi.tolist()]),indent=2))
 return dict(name=name,slug=slug,spec=str(folder/'spec.py'),media=media,source=str(source),status='prepared',bounds=[lo.tolist(),hi.tolist()],wheelbase=wb)

if __name__=='__main__':
 manifest=[]
 for i in range(len(CONFIG)):
  try:r=prepare(i);manifest.append(r);print(r['name'],'prepared',np.round(np.diff(r['bounds'],axis=0)[0],3),flush=True)
  except Exception as e:manifest.append(dict(name=CONFIG[i][0],status='failed',error=str(e)));print(CONFIG[i][0],str(e),flush=True)
 (BASE/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
