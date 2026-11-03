"""Extract explicit source wheel selections; never silently retain the donor face."""
from pathlib import Path
import json,pickle,sys,re,hashlib,math
import numpy as np,trimesh
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'tools')]
from wheelfit import load_spec
from daily_batch import CONFIG
BASE=ROOT/'cars/daily_batch';BACK=ROOT/'backups/daily-source-wheels-v1'
# A deliberate node/material selection and nominal rim diameter for every source.
CHOICES={
1:dict(nodes=['teker_0-material'],rim=14,loose=True),
2:dict(nodes=['138'],rim=17,loose=True,reverse_face=True),
3:dict(mats=['Fphong14SG1'],rim=18,corner=True),
4:dict(mats=['rim.001'],rim=17,corner=True),
5:dict(nodes=['gray-material_1'],rim=14,loose=True),
6:dict(nodes=['Object_25'],rim=17),
7:dict(nodes=['Object_611'],rim=16,loose=True,reverse_face=True),
8:dict(nodes=['alloy15-material_1'],rim=15),
9:dict(nodes=['htvectrac_metal-material_1','htvectrac_chrome-material_7'],rim=16,loose=True,reverse_face=True),
10:dict(nodes=['Object_30'],rim=16),
11:dict(nodes=['Object_55'],rim=16),
12:dict(nodes=['desirefx.me_038_rim_0'],rim=17),
13:dict(nodes=['blinn1SG'],rim=13,corner=True,pca=True,reverse_face=True),
14:dict(nodes=['wheel_2__a0m1','wheel_2__a0m2'],rim=17),
15:dict(nodes=['wheel__a0m2'],rim=17),
16:dict(nodes=['Volvo_Ratas __a22m0'],rim=18),
17:dict(nodes=['wheel__a0m1'],rim=20),
18:dict(nodes=['wheel__a6m0'],rim=14,crop_tyre=True),
}

def read_selection(item,choice):
 scene=trimesh.load(item['source'],force='scene');config=CONFIG[int(item['slug'][-2:])-1];frame=config[1]
 if frame=='pca':
  pts=np.concatenate([m.vertices for m in scene.geometry.values() if isinstance(m,trimesh.Trimesh) and len(m.faces)>20]);q=pts[:,[0,2]];_,_,vh=np.linalg.svd(q-q.mean(0),full_matrices=False);long=vh[0];long*=1 if long[0]>0 else -1;across=np.array([-long[1],long[0]]);rot=np.array([[across[0],0,across[1]],[0,1,0],[-long[0],0,-long[1]]])
 else:
  rot=np.zeros((3,3))
  for j,a in enumerate(frame.split(',')):rot[j,'xyz'.index(a[-1])]=-1 if a.startswith('-') else 1
 selected=[]
 for node in scene.graph.nodes_geometry:
  T,key=scene.graph[node];m=scene.geometry[key]
  if not isinstance(m,trimesh.Trimesh):continue
  mat=m.visual.material;name=mat.name or node
  if node not in choice.get('nodes',[]) and name not in choice.get('mats',[]):continue
  v=trimesh.transform_points(m.vertices,T)@rot.T;n=m.vertex_normals@np.linalg.inv(T[:3,:3])@rot.T;n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12);f=m.faces.copy();uv=getattr(m.visual,'uv',None);uv=np.array(uv) if uv is not None else np.zeros((len(v),2))
  if np.linalg.det(rot@T[:3,:3])<0:f=f[:,::-1]
  if len(f):selected.append(dict(node=node,material=name,V=v[f].reshape(-1,3),N=n[f].reshape(-1,3),UV=uv[f].reshape(-1,2),pbr=mat))
 if not selected:raise ValueError('No wheel meshes matched the reviewed selection')
 if choice.get('corner'):
  allv=np.concatenate([a['V'] for a in selected]);cx=(allv[:,0].min()+allv[:,0].max())/2;cz=(allv[:,2].min()+allv[:,2].max())/2
  for a in selected:
   c=a['V'].reshape(-1,3,3).mean(1);keep=(c[:,0]>cx)&(c[:,2]>cz)
   for key,dim in [('V',3),('N',3),('UV',2)]:a[key]=a[key].reshape(-1,3,dim)[keep].reshape(-1,dim)
  selected=[a for a in selected if len(a['V'])]
 return selected

def prepare(item,choice):
 p=Path(item['spec']).parent;S=load_spec(p/'spec.py');G=pickle.load(open(BACK/item['slug']/'geo.pkl','rb'));chunks=read_selection(item,choice);V=np.concatenate([x['V'] for x in chunks]);centre=(V.min(0)+V.max(0))/2
 # Determine the actual spindle direction and remove baked source camber/toe.
 cov=np.cov((V-centre).T);values,vec=np.linalg.eigh(cov);ax=vec[:,np.argmin(values)]
 if ax[0]<0:ax=-ax
 if abs(ax[0])<.85:raise ValueError('Selected geometry is not one wheel around the lateral axis')
 outward=(1 if choice.get('loose') or centre[0]>=0 else -1)*ax
 if choice.get('reverse_face'):outward=-outward
 x=-outward;up=np.array([0.,1.,0.]);y=up-x*np.dot(up,x);y/=np.linalg.norm(y);z=np.cross(x,y);basis=np.stack([x,y,z]);
 transformed=[(a['V']-centre)@basis.T for a in chunks];VV=np.concatenate(transformed);radialcentre=(VV[:,1:].min(0)+VV[:,1:].max(0))/2
 for a,v in zip(chunks,transformed):a['V']=v-np.r_[0,radialcentre];a['N']=a['N']@basis.T
 if choice.get('crop_tyre'):
  # This GTA source puts tyre and wheel in one material. Keep only the inner metal face.
  rr=np.hypot(VV[:,1]-radialcentre[0],VV[:,2]-radialcentre[1]);limit=rr.max()*.72
  for a in chunks:
   tri=a['V'].reshape(-1,3,3);k=np.hypot(tri[:,:,1],tri[:,:,2]).max(1)<limit
   for key,dim in [('V',3),('N',3),('UV',2)]:a[key]=a[key].reshape(-1,3,dim)[k].reshape(-1,dim)
  chunks=[a for a in chunks if len(a['V'])]
 VV=np.concatenate([a['V'] for a in chunks]);sourceR=float(np.hypot(VV[:,1],VV[:,2]).max());ref=choice['rim']*.0254/2
 # A source outer lip is distinct from the nominal bead-seat radius. Preserve the shape at an explicit size.
 desired_outer=ref+.012;scale=desired_outer/sourceR;xout=float(VV[:,0].min());wheelcentre=np.array(G['wheels']['HUB_LF']['centre']);verts=[];normals=[];uvs=[]
 tile=512;n=len(chunks);cols=math.ceil(math.sqrt(n));rows=math.ceil(n/cols);atlas=Image.new('RGB',(cols*tile,rows*tile),(170,170,175));sources=[]
 for j,a in enumerate(chunks):
  v=a['V']*scale;v[:,0]-=xout*scale;v+=wheelcentre
  uv=a['UV'].copy();mat=a['pbr'];img=getattr(mat,'baseColorTexture',None)
  if img is None:img=getattr(mat,'image',None)
  if img is None:
   colour=getattr(mat,'baseColorFactor',None)
   if colour is None:colour=getattr(mat,'diffuse',None)
   rgb=tuple(int(c) for c in colour[:3]) if colour is not None else (175,178,180);img=Image.new('RGB',(8,8),rgb)
  img=img.convert('RGB')
  pixels=np.asarray(img)
  if ('chrome' in a['material'].lower() or 'silv' in a['material'].lower()) and np.ptp(pixels.reshape(-1,3),axis=0).max()<4:
   grey=int(np.mean(pixels));img=Image.new('RGB',img.size,(grey,grey,grey))
  if item['slug']=='daily13':
   pixels=np.asarray(img)
   if np.ptp(pixels.reshape(-1,3),axis=0).max()<4:img=Image.new('RGB',img.size,(170,172,175))
  img=img.resize((tile,tile),Image.Resampling.LANCZOS);atlas.paste(img,((j%cols)*tile,(j//cols)*tile))
  # Source UV is bottom-up. Atlas rows are top-down; keep a two-pixel border away from neighbouring tiles.
  uv=np.mod(uv,1.0000001);uv[:,0]=(j%cols+(2/tile+uv[:,0]*(1-4/tile)))/cols;uv[:,1]=(rows-1-j//cols+(2/tile+uv[:,1]*(1-4/tile)))/rows
  verts.append(v);normals.append(a['N']);uvs.append(uv);sources.append(dict(node=a['node'],material=a['material'],triangles=len(v)//3))
 atlas=atlas.resize((1024,1024),Image.Resampling.LANCZOS);(p/'textures').mkdir(exist_ok=True);atlas.save(p/'textures/source_rim.png')
 part=dict(node='source_rim',mat='SOURCE_RIM',V=np.concatenate(verts),N=np.concatenate(normals),UV=np.concatenate(uvs));G['parts']['SOURCE_RIM']=[part];G['materials']=sorted(G['parts'])
 t=dict(S.PHYSICS['tyres']);radius=G['wheels']['HUB_LF']['radius'];width=235 if choice['rim']>=20 or item['slug']=='daily16' else 225 if choice['rim']>=18 else 205 if choice['rim']>=17 else 195 if choice['rim']>=16 else 185
 if item['slug'] in ['daily04','daily12','daily14']:width=225
 aspect=max(20,round((radius-ref)/(width/1000)*20)*5);t.update(width_front=width,width_rear=width,aspect_front=aspect,aspect_rear=aspect,rim_in=choice['rim'])
 actual=ref+width/1000*aspect/100
 if abs(actual-radius)>.03:raise ValueError('Chosen nominal rim cannot fit the measured tyre radius')
 depth=float(np.ptp(part['V'][:,0]));maxdepth=width/1000+.008
 if depth>maxdepth:
  compression=maxdepth/depth;part['V'][:,0]=wheelcentre[0]+(part['V'][:,0]-wheelcentre[0])*compression;part['N'][:,0]/=compression;part['N']/=np.linalg.norm(part['N'],axis=1,keepdims=True)
 pickle.dump(G,open(p/'geo.pkl','wb'))
 spec=(BACK/item['slug']/'spec.py').read_text();spec=re.sub(r"UPGRADE_PROFILE='../daily_batch/upgrade_profile.py'","UPGRADE_PROFILE='upgrade_profile.py'",spec)
 spec+='\n# Reviewed source wheel; mandatory custom geometry, no shared Charger face.\n'
 spec+="RIM_MATERIALS=['SOURCE_RIM']\nRIM_R_REF="+repr(ref)+"\nRIM_SOURCE_TEXTURE='source_rim'\nRIM_CLEAR_DONOR=True\nMATERIALS['SOURCE_RIM']=None\nTEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)\nPHYSICS['tyres']="+repr(t)+"\nREQUIRE_SOURCE_WHEELS=True\n"
 (p/'spec.py').write_text(spec)
 report=dict(name=item['name'],slug=item['slug'],source=item['source'],selected=sources,spindle_axis=ax.tolist(),nominal_rim_in=choice['rim'],nominal_radius=ref,outer_lip_radius=desired_outer,source_outer_radius=sourceR,normalisation_scale=scale,source_depth=float(np.ptp(VV[:,0])),fitted_depth=float(np.ptp(part['V'][:,0])),tyres=t,tyre_radius=actual,source_tyre_radius=float(radius),triangles=len(part['V'])//3,geometry_sha256=hashlib.sha256(part['V'].tobytes()+part['UV'].tobytes()).hexdigest(),status='source geometry selected; built validation pending')
 (p/'source-wheel.json').write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':
 manifest=json.loads((BASE/'build-manifest.json').read_text());reports=[]
 for i,item in enumerate(manifest,1):
  if len(sys.argv)>1 and i not in list(map(int,sys.argv[1:])):continue
  try:r=prepare(item,CHOICES[i]);reports.append(r);print(i,item['name'],r['triangles'],'triangles',r['nominal_rim_in'],'inch',round(r['fitted_depth'],3),'m depth',flush=True)
  except Exception as e:print(i,item['name'],'FAILED',repr(e),flush=True)
 (BASE/'source-wheel-selections.json').write_text(json.dumps(reports,indent=2))
