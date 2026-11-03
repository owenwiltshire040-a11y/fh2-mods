"""Prepare Owen's supplied N Vision 74; explicit source-node wheel selection."""
from pathlib import Path
import json,pickle,hashlib,re
import numpy as np,trimesh
from PIL import Image
from scipy.ndimage import distance_transform_edt
p=Path(__file__).resolve().parent;s=trimesh.load(p/'model.glb',force='scene')
def vertices(node):
 t,k=s.graph[node];return trimesh.transform_points(s.geometry[k].vertices,t)
raw={}
for num,corner in [(13,'LF'),(14,'RF'),(16,'LR'),(15,'RR')]:
 v=vertices('컴포넌트#'+str(num));lo,hi=v.min(0),v.max(0);raw[corner]=dict(centre=(lo+hi)/2,radius=float(((hi-lo)[1]+(hi-lo)[2])/4),width=float((hi-lo)[0]))
wb=raw['LF']['centre'][2]-raw['LR']['centre'][2];scale=2.905/wb
mid=np.mean([w['centre'] for w in raw.values()],axis=0);off=np.array([0,.1511658-mid[1]*scale,.05-mid[2]*scale])
parts={};mapping={};textures={};counts={}
# Badge atlas uses real cutouts. Clip transparent texels into geometry, retaining UVs.
def clip(V,N,U,image):
 mask=np.array(image)[:,:,3]>100;h,w=mask.shape;out=[]
 def walk(v,n,u,depth=0):
  lo=np.floor(u.min(0)*[w-1,h-1]).astype(int);hi=np.ceil(u.max(0)*[w-1,h-1]).astype(int)
  lo=np.clip(lo,0,[w-1,h-1]);hi=np.clip(hi,0,[w-1,h-1]);patch=mask[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
  if not patch.any():return
  if patch.all():out.append((v,n,u));return
  if depth>=9 or max(hi-lo)<=3:
   c=np.clip(np.round(u.mean(0)*[w-1,h-1]).astype(int),0,[w-1,h-1])
   if mask[c[1],c[0]]:out.append((v,n,u))
   return
  vv=np.vstack([v,(v+np.roll(v,-1,axis=0))/2]);nn=np.vstack([n,(n+np.roll(n,-1,axis=0))/2]);uu=np.vstack([u,(u+np.roll(u,-1,axis=0))/2])
  for ix in [[0,3,5],[3,1,4],[5,4,2],[3,4,5]]:walk(vv[ix],nn[ix],uu[ix],depth+1)
 for v,n,u in zip(V.reshape(-1,3,3),N.reshape(-1,3,3),U.reshape(-1,3,2)):walk(v,n,u)
 return tuple(np.concatenate([a[i] for a in out]) for i in range(3))
for node in s.graph.nodes_geometry:
 t,k=s.graph[node];m=s.geometry[k];mat=m.visual.material.name
 num=int(node.split('#')[-1]) if node.startswith('컴포넌트#') else 0
 wheel=num>=13
 if wheel and num not in [17,21,25,29,31,33]:continue
 V=trimesh.transform_points(m.vertices,t)*[-1,1,1]*scale+off
 N=m.vertex_normals@np.linalg.inv(t[:3,:3]);N=N*[-1,1,1];N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)
 F=m.faces[:,::-1] if np.linalg.det(t[:3,:3])>0 else m.faces
 U=m.visual.uv if m.visual.uv is not None else np.zeros((len(V),2))
 V,N,U=V[F].reshape(-1,3),N[F].reshape(-1,3),U[F].reshape(-1,2)
 image=getattr(m.visual.material,'baseColorTexture',None)
 if image is None:image=Image.new('RGB',(64,64),(65,65,65))
 image=image.convert('RGBA')
 if 'BadgeA_' in mat:
  U=U.reshape(-1,3,2);U-=np.floor(U.mean(1))[:,None,:];U=U.reshape(-1,2);U=U*[1,-1]+[0,1];V,N,U=clip(V,N,U,image);U=U*[1,-1]+[0,1]
  a=np.array(image);mask=a[:,:,3]>100;idx=distance_transform_edt(~mask,return_distances=False,return_indices=True);a[:,:,:3]=a[idx[0],idx[1],:3];image=Image.fromarray(a)
  V+=N*.001
 name='SOURCE_RIM' if wheel else mat
 if node=='G-Interior01':name='STEERING_SOURCE'
 if mat.endswith('LightA_Diffuse'):
  # Separate luminous white/red pixel faces using their original atlas colours.
  a=np.array(image);uv=U.reshape(-1,3,2).mean(1);xy=np.mod(np.round((uv*[1,-1]+[0,1])*[image.width-1,image.height-1]).astype(int),[image.width,image.height]);rgb=a[xy[:,1],xy[:,0],:3].astype(float);centre=V.reshape(-1,3,3).mean(1)
  front=(centre[:,2]>2)&(rgb.min(1)>120);rear=(centre[:,2]<-2)&(centre[:,1]>.4)&(rgb.min(1)>120)
  for mask,tag in [(front,'HEAD_EMITTER'),(rear,'TAIL_EMITTER'),(~(front|rear),name)]:
   if mask.any():parts.setdefault(tag,[]).append(dict(node=node,mat=tag,V=V.reshape(-1,3,3)[mask].reshape(-1,3),N=N.reshape(-1,3,3)[mask].reshape(-1,3),UV=U.reshape(-1,3,2)[mask].reshape(-1,2)))
 else:parts.setdefault(name,[]).append(dict(node=node,mat=name,V=V,N=N,UV=U))
 fn=hashlib.sha1(mat.encode()).hexdigest()[:10]+'.png';image.convert('RGB').save(p/'textures'/fn);textures[name]=fn;mapping[name]=('textured','t'+fn[:-4]);counts[node]=len(V)//3
 if wheel:mapping[name]=None
 if mat=='Paint':mapping[name]=('plain','paint')
 if mat=='Window':mapping[name]=('plain','glass')
wheels={'HUB_'+k:dict(centre=v['centre']*[-1,1,1]*scale+off,radius=v['radius']*scale) for k,v in raw.items()}
G=dict(parts=parts,wheels=wheels,ground=float(.1511658-np.mean([v['radius']*scale for v in raw.values()])),wheelbase=2.905,materials=sorted(parts))
(p/'geo.pkl').write_bytes(pickle.dumps(G));V=np.concatenate([x['V'] for x in parts['SOURCE_RIM']]);c=wheels['HUB_LF']['centre'];outer=float(np.hypot(V[:,1]-c[1],V[:,2]-c[2]).max())
report=dict(selected=[x['node'] for x in parts['SOURCE_RIM']],nominal_rim_in=21,nominal_radius=.2667,outer_lip_radius=outer,fitted_depth=float(np.ptp(V[:,0])),triangles=len(V)//3,status='source selected; built validation pending')
(p/'source-wheel.json').write_text(json.dumps(report,indent=2));(p/'source-analysis.json').write_text(json.dumps(dict(scale=scale,offset=off.tolist(),source_wheelbase=float(wb),wheelbase=2.905,wheels={k:dict(centre=v['centre'].tolist(),radius=v['radius'],width=v['width']) for k,v in raw.items()},textures=textures,mapping=mapping,triangles=counts),indent=2))
print('Prepared',sum(counts.values()),'triangles; wheel:',report,flush=True)
