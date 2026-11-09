"""Prepare the supplied 919 KN5 conversion, separating glass, lamps, steering and source wheels."""
from pathlib import Path
import hashlib,json,pickle
import numpy as np
from PIL import Image
import trimesh

HERE=Path(__file__).resolve().parent
scene=trimesh.load(HERE/'source/gtp_porsche_919_2017.glb',force='scene',process=False)
raw={}
for node in scene.graph.nodes_geometry:
 transform,key=scene.graph[node];mesh=scene.geometry[key]
 V=trimesh.transform_points(mesh.vertices,transform)
 N=mesh.vertex_normals@np.linalg.inv(transform[:3,:3]);N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9)
 ancestors=[];name=node
 while name is not None:
  ancestors.append(name);name=scene.graph.transforms.parents.get(name)
 raw[node]=dict(mesh=mesh,V=V,N=N,ancestors=ancestors)
wheels={}
for corner in ('LF','RF','LR','RR'):
 row=raw['TYRE_'+corner+'_1'];P=row['V'];lo,hi=P.min(0),P.max(0)
 wheels['HUB_'+corner]=dict(centre=(lo+hi)/2,radius=float((hi[1]-lo[1]+hi[2]-lo[2])/4),width=float(hi[0]-lo[0]))
mid=np.mean([w['centre'] for w in wheels.values()],axis=0)
offset=np.array([-mid[0],.151-mid[1],.05+mid[2]])
parts={};textures={};mapping={};images={};alpha={};paint=[];steering=[];rim=[];rear=[]
for node,row in raw.items():
 mesh=row['mesh'];material=mesh.visual.material;mat=material.name
 if node.startswith(('TYRE_','CALIPER_','DISK_')):continue
 if node.startswith(('WIND_IN','glassfint_')):continue
 if 'blackglass' in mat.lower() and node.lower().startswith(('glassf','glassl','wind')):continue
 if node.startswith('HGLOB'):continue
 # Claude 7 Nov (step 3): the headlight glow card (an AC flare sprite). NUMBERS_LIT is the number panels themselves.
 if node.startswith('HGLOW'):continue
 V=row['V']*[1,1,-1]+offset;N=row['N']*[1,1,-1];F=mesh.faces[:,::-1]
 UV=mesh.visual.uv.copy() if mesh.visual.uv is not None else np.zeros((len(V),2))
 if node.startswith('RIM_'):
  axle='F' if node.startswith(('RIM_LF','RIM_RF')) else 'R'
  tag='RIM_REF_'+axle
  frag=dict(node=node,mat=tag,V=V[F].reshape(-1,3),N=N[F].reshape(-1,3),UV=UV[F].reshape(-1,2))
  parts.setdefault(tag,[]).append(frag)
  if node.startswith(('RIM_LF','RIM_LR')):
   atlasUV=UV[F].reshape(-1,2).copy()
   atlasUV=np.clip(atlasUV,0,1)
   if mat=='EXT_Rims_Base':atlasUV[:,1]=.5+.5*atlasUV[:,1]
   else:atlasUV*=.5
   frag=dict(frag,mat='SOURCE_RIM' if axle=='F' else 'SOURCE_RIM_REAR',UV=atlasUV)
   (rim if axle=='F' else rear).append(frag)
  continue
 is_steering='STEER_HR' in row['ancestors']
 # Claude 7 Nov (step 10): the wheel's LCD (SW_LIT2) is kept as SW_SCREEN; screen.py makes it the live page
 if is_steering and any(a in node for a in ('SW_LIT','LIT8','TAG_')) and not node.startswith('SW_LIT2'):continue
 # Claude 9 Nov (step 10): the opaque blackglass layer behind the clear headlight cover hid the whole lamp
 if node=='headlightl_a_SUB5':continue
 key=('SW_' if is_steering else '')+mat
 if node=='headlightl_a_SUB3':key='HEAD_EMIT'
 elif node.startswith('SW_LIT2'):key='SW_SCREEN'
 elif node=='GLOW_1':key='TAIL_EMIT'
 image=material.baseColorTexture
 if image is None:image=Image.new('RGBA',(16,16),(255,255,255,255))
 image=image.convert('RGBA')
 # the reflector and lamp were textured with the conversion's dark RIM_BLUR.DDS: plain silver / near-white
 if key=='HEAD_EMIT':image=Image.new('RGBA',(16,16),(238,240,245,255))
 if node=='headlightl_a_SUB2':key='HEAD_CHROME';image=Image.new('RGBA',(16,16),(205,207,212,255))
 factor=np.asarray(material.baseColorFactor if material.baseColorFactor is not None else [255]*4)/255
 pixels=np.array(image).astype(float)*factor
 image=Image.fromarray(np.rint(pixels).astype('uint8'))
 filename=hashlib.sha1(image.tobytes()+str(image.size).encode()).hexdigest()[:12]+'.png'
 image.save(HERE/'textures'/filename)
 textures[key]=filename;images[key]=dict(size=image.size,alpha=material.alphaMode)
 plan=('textured','t'+Path(filename).stem)
 if any(s in mat.lower() for s in ('gls_','_glass','lcovers_')) and not is_steering:
  plan=('plain','glass')
 if mat.lower().startswith('digitalgauge') and not is_steering:
  # The source cabin screens retain their artwork until assigned a live native page.
  pass
 mapping[key]=plan
 if 'carpaint' in mat.lower():paint.append(key)
 if material.alphaMode in ('BLEND','MASK'):alpha[key]=filename
 if is_steering and key not in steering:steering.append(key)
 parts.setdefault(key,[]).append(dict(node=node,mat=key,V=V[F].reshape(-1,3),N=N[F].reshape(-1,3),UV=UV[F].reshape(-1,2)))
# Claude 7 Nov (steps 3-4): FH2 draws these materials opaque, so decals with a real alpha channel (rivets, screws,
# labels, livery cut-outs) are clipped to their alpha, lifted 1.5 mm, and their texture colours bled past the edges.
from scipy.ndimage import distance_transform_edt
def clip_alpha(V,N,UV,mask):
 """keep only the parts of each triangle over opaque texels (UV in image space: u right, v down)"""
 out=[];h,w=mask.shape
 def walk(v,n,u,depth=0):
  lo=np.floor(u.min(0)*[w-1,h-1]).astype(int);hi=np.ceil(u.max(0)*[w-1,h-1]).astype(int)
  lo=np.maximum(lo,0);hi=np.minimum(hi,[w-1,h-1])
  if np.any(hi<lo):return
  patch=mask[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
  if not patch.any():return
  if patch.mean()>.97:out.append((v,n,u));return
  if depth>=6 or max(hi-lo)<=16:
   c=np.clip(np.round(u.mean(0)*[w-1,h-1]).astype(int),0,[w-1,h-1])
   if mask[c[1],c[0]]:out.append((v,n,u))
   return
  vv=np.vstack([v,(v+np.roll(v,-1,axis=0))/2]);nn=np.vstack([n,(n+np.roll(n,-1,axis=0))/2]);uu=np.vstack([u,(u+np.roll(u,-1,axis=0))/2])
  for ix in [[0,3,5],[3,1,4],[5,4,2],[3,4,5]]:walk(vv[ix],nn[ix],uu[ix],depth+1)
 for v,n,u in zip(V.reshape(-1,3,3),N.reshape(-1,3,3),UV.reshape(-1,3,2)):walk(v,n,u)
 if not out:return np.zeros((0,3)),np.zeros((0,3)),np.zeros((0,2))
 return tuple(np.concatenate([o[i] for o in out]) for i in range(3))
clipped={};decals=[]
for key in sorted(alpha):
 if key not in parts or mapping.get(key)==('plain','glass') or key=='TAIL_EMIT':continue
 img=Image.open(HERE/'textures'/textures[key]).convert('RGBA')
 if max(img.size)<=64:continue
 rgba=np.array(img);mask=rgba[:,:,3]>100
 if (~mask).mean()<=.01:continue
 idx=distance_transform_edt(~mask,return_distances=False,return_indices=True)
 bled=rgba.copy();bled[:,:,:3]=rgba[idx[0],idx[1],:3]
 if key not in steering:
  # Claude 7 Nov v0.1.2: body decals keep their source geometry and alpha; livery_decals.py (package finalizer)
  # draws them with the game's carpaint_livery transparent pass (Codex's RB22 restore_decals method).
  for f in parts[key]:f['V']=f['V']+f['N']*.0015
  out=Image.fromarray(bled);filename=hashlib.sha1(out.tobytes()+b'livery').hexdigest()[:12]+'.png';out.save(HERE/'textures'/filename)
  textures[key]=filename;mapping[key]=('textured','t'+Path(filename).stem);decals.append(key);continue
 # steering-wheel decals (bone-attached part): clipped to their alpha, as before
 kept=[];before=sum(len(f['V'])//3 for f in parts[key])
 for f in parts[key]:
  iu=np.c_[f['UV'][:,0],1-f['UV'][:,1]].reshape(-1,3,2);iu=(iu-np.floor(iu.mean(1,keepdims=True))).reshape(-1,2)
  V,N,iu=clip_alpha(f['V'],f['N'],iu,mask)
  if len(V):kept.append(dict(f,V=V+N*.0015,N=N,UV=np.c_[iu[:,0],1-iu[:,1]]))
 bled[:,:,3]=255;out=Image.fromarray(bled)
 filename=hashlib.sha1(out.tobytes()+b'decal').hexdigest()[:12]+'.png';out.save(HERE/'textures'/filename)
 textures[key]=filename;mapping[key]=('textured','t'+Path(filename).stem)
 clipped[key]=(before,sum(len(f['V'])//3 for f in kept))
 if kept:parts[key]=kept
 else:
  del parts[key];mapping[key]=None
  if key in steering:steering.remove(key)
print('livery decals',len(decals),'clipped steering decals',clipped)
# An atlas keeps both the BBS face and its source decals, including their alpha.
base_mat=scene.geometry[scene.graph['RIM_LF_SUB0'][1]].visual.material.baseColorTexture.convert('RGBA')
decal_mat=scene.geometry[scene.graph['RIM_LF_SUB1'][1]].visual.material.baseColorTexture.convert('RGBA')
atlas=Image.new('RGBA',(1024,1024),(16,16,16,255))
atlas.paste(base_mat.resize((1024,512)),(0,0))
atlas.paste(decal_mat.resize((512,512)),(0,512))
atlas.save(HERE/'textures/source_rim.png')
for name,fragments,axle in [('SOURCE_RIM',rim,'F'),('SOURCE_RIM_REAR',rear,'R')]:
 V=np.concatenate([f['V'] for f in fragments]);outer=V[:,0].min();depth=np.ptp(V[:,0])
 # Fit the supplied barrel inside the 310 mm tyre, preserving its outer face.
 for f in fragments:f['V'][:,0]=outer+(f['V'][:,0]-outer)*(.30/depth)
 parts[name]=fragments;mapping[name]=None
for key in ('RIM_REF_F','RIM_REF_R'):mapping[key]=None
W={k:dict(centre=w['centre']*[1,1,-1]+offset,radius=w['radius']) for k,w in wheels.items()}
wb=float(np.mean([w['centre'][2] for k,w in W.items() if k.endswith('F')])-np.mean([w['centre'][2] for k,w in W.items() if k.endswith('R')]))
P=np.concatenate([f['V'] for f in parts['SOURCE_RIM']]);c=W['HUB_LF']['centre']
report=dict(nominal_rim_in=18,outer_lip_radius=float(np.hypot(P[:,1]-c[1],P[:,2]-c[2]).max()),fitted_depth=float(np.ptp(P[:,0])),triangles=len(P)//3,source='Porsche 919 BBS front rim and original decals')
(HERE/'source-wheel.json').write_text(json.dumps(report,indent=2)+'\n')
pickle.dump(dict(parts=parts,wheels=W,wheelbase=wb,ground=.151-np.mean([w['radius'] for w in W.values()]),materials=sorted(parts)),open(HERE/'geo.pkl','wb'))
a=dict(decals=decals,offset=offset.tolist(),wheelbase=wb,textures=textures,mapping=mapping,alpha=alpha,paint=sorted(set(paint)),steering=steering,wheels={k:dict(centre=w['centre'].tolist(),radius=w['radius'],width=w['width']) for k,w in wheels.items()})
(HERE/'source-analysis.json').write_text(json.dumps(a,indent=2)+'\n')
print('Measured wheelbase',wb,'texture files',len(set(textures.values())),'steering materials',len(steering),'source rim',report)
