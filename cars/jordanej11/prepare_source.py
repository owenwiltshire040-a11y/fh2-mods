"""Jordan EJ11 source in metre units, measured wheels and cutout sponsor decals."""
from pathlib import Path
import json,pickle,hashlib
import numpy as np,trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.ndimage import distance_transform_edt
from PIL import Image
p=Path(__file__).resolve().parent;s=trimesh.load(p/'model.glb',force='scene')
# Source tyres are one material mesh containing four disconnected, closed tyres.
node=next(n for n in s.graph.nodes_geometry if s.geometry[s.graph[n][1]].visual.material.name=='TYRE.008')
T,key=s.graph[node];tyre=s.geometry[key];V=trimesh.transform_points(tyre.vertices,T);m=trimesh.Trimesh(V,tyre.faces,process=True);a=m.edges_unique
n,labels=connected_components(coo_matrix((np.ones(len(a)),a.T),shape=(len(m.vertices),)*2),directed=False)
raw={}
for i in range(n):
 v=m.vertices[labels==i]
 if len(v)<100:continue
 lo,hi=v.min(0),v.max(0);c=(lo+hi)/2;corner=('L' if c[0]>0 else 'R')+('F' if c[2]>0 else 'R')
 raw['HUB_'+corner]=dict(centre=c,radius=float((hi[1]-lo[1]+hi[2]-lo[2])/4),width=float(hi[0]-lo[0]))
assert len(raw)==4
mid=np.mean([v['centre'] for v in raw.values()],axis=0);off=np.array([mid[0],.1511658-mid[1],.05-mid[2]])
parts={};textures={};mapping={};counts={}

def clip_alpha(V,N,UV,mask):
 # Clip transparent logo planes into opaque geometry; avoid solid RGB billboards.
 out=[];h,w=mask.shape
 def walk(v,n,u,depth=0):
  lo=np.floor(u.min(0)*[w-1,h-1]).astype(int);hi=np.ceil(u.max(0)*[w-1,h-1]).astype(int)
  lo=np.maximum(lo,0);hi=np.minimum(hi,[w-1,h-1])
  if np.any(hi<lo):return
  patch=mask[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
  if not patch.any():return
  if patch.all():out.append((v,n,u));return
  if depth>=12 or max(hi-lo)<=4:
   c=np.clip(np.round(u.mean(0)*[w-1,h-1]).astype(int),0,[w-1,h-1])
   if mask[c[1],c[0]]:out.append((v,n,u))
   return
  vv=np.vstack([v,(v+np.roll(v,-1,axis=0))/2]);nn=np.vstack([n,(n+np.roll(n,-1,axis=0))/2]);uu=np.vstack([u,(u+np.roll(u,-1,axis=0))/2])
  for ix in [[0,3,5],[3,1,4],[5,4,2],[3,4,5]]:walk(vv[ix],nn[ix],uu[ix],depth+1)
 for v,n,u in zip(V.reshape(-1,3,3),N.reshape(-1,3,3),UV.reshape(-1,3,2)):walk(v,n,u)
 return tuple(np.concatenate([a[i] for a in out]) for i in range(3))

for node in s.graph.nodes_geometry:
 T,key=s.graph[node];m=s.geometry[key];mat=m.visual.material.name
 if mat in ['TYRE.008','Brake_Disc.006','Brake_Caliper.006','Material_#113.006','Material_#114.006','Material_#86.002']:continue
 V=trimesh.transform_points(m.vertices,T);N=m.vertex_normals@T[:3,:3].T;N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)
 V=V*[-1,1,1]+off;N=N*[-1,1,1];F=m.faces[:,::-1];UV=m.visual.uv if m.visual.uv is not None else np.zeros((len(V),2))
 V,N,UV=V[F].reshape(-1,3),N[F].reshape(-1,3),UV[F].reshape(-1,2)
 image=getattr(m.visual.material,'baseColorTexture',None)
 if image is None:image=Image.new('RGB',(64,64),(55,55,55))
 image=image.convert('RGBA')
 if mat=='Material_#28.006':
  # Source logo UVs use the repeated V tile 1..2. Move that tile to 0..1.
  UV=UV-[0,1]
  # glTF UVs are bottom-up; mask indexing follows image rows after V is inverted.
  alpha=np.array(image.resize((512,512),Image.Resampling.LANCZOS))[:,:,3]>100
  V,N,UV=clip_alpha(V,N,UV*np.array([1,-1])+[0,1],alpha)
  UV=UV*np.array([1,-1])+[0,1]
  # Keep decals clear of the coincident source skin after game vertex packing.
  V+=N/np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)*.002
  rgb=np.array(image.resize((1024,1024),Image.Resampling.LANCZOS));edge_alpha=rgb[:,:,3]>100;indices=distance_transform_edt(~edge_alpha,return_distances=False,return_indices=True);rgb[:,:,:3]=rgb[indices[0],indices[1],:3];image=Image.fromarray(rgb[:,:,:3])
  print('Sponsor cutouts:',len(V)//3,'triangles',flush=True)
 N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)
 parts.setdefault(mat,[]).append(dict(node=node,mat=mat,V=V,N=N,UV=UV));counts[mat]=len(V)//3
 fn=hashlib.sha1(mat.encode()).hexdigest()[:10]+'.png';image.convert('RGB').save(p/'textures'/fn);textures[mat]=fn
 mapping[mat]=('textured','t'+fn[:-4])
 if mat in ['RIM.002','RIM_REAR.002','Red_Chrome.004','Silver_Chrome.006']:mapping[mat]=None
 if mat=='Mirror.006':mapping[mat]=('plain','chrome')
 if mat=='EXT_Glass.002':mapping[mat]=('plain','glass')
wheels={k:dict(centre=w['centre']*[-1,1,1]+off,radius=w['radius']) for k,w in raw.items()}
wb=float(np.mean([wheels[k]['centre'][2] for k in ['HUB_LF','HUB_RF']])-np.mean([wheels[k]['centre'][2] for k in ['HUB_LR','HUB_RR']]))
pickle.dump(dict(parts=parts,wheels=wheels,ground=.1511658-np.mean([w['radius'] for w in raw.values()]),wheelbase=wb,materials=sorted(parts)),open(p/'geo.pkl','wb'))
(p/'source-analysis.json').write_text(json.dumps(dict(offset=off.tolist(),wheelbase=wb,wheels={k:{'centre':w['centre'].tolist(),'radius':w['radius'],'width':w['width']} for k,w in raw.items()},textures=textures,mapping=mapping,triangles=counts),indent=2))
print('Wheelbase',wb,'offset',off,'selected',sum(counts.values()),'triangles',flush=True)
