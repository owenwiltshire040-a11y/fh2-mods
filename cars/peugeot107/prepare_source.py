"""Select pre-facelift 107 parts, keeping original UVs and embedded texture imagery."""
from pathlib import Path
import trimesh,numpy as np,pickle,hashlib,json
from PIL import Image
p=Path(__file__).resolve().parent
s=trimesh.load(p/'model.glb',force='scene');parts={};textures={};seen=set();chosen=[];dropped=[]
centre_y=.27855;shift=np.array([0.,.1511658-centre_y,.05]);wheel=np.array([-.71,.1511658,1.22])
exclude=('c1_bumper_F107R','c1_bumper_Frest','c1_hoodr107r','c1_hoodrest','c1_headlight_LRS','c1_headlight_RSS','c1_headlight_L_','c1_headlight_R_','c1_bumper_F_','c1_hood_','c1_tailgate_','cit_c1_11_headlight','cit_c1_11_glass','cit_c1_11_taillight','cit_c1_11_mirrorR','c1_F_chr','c1_F_black','lcF','chrome1.','c1steelwheel','c1_hubcap','hubcap_','cit_c1_11_wheel','chassis.','c1_shifter_A','c1_shifterbase_A','c1_steer_','covet_steer','c1_casetophone','vivace_exhaustpipe','c1_trim_door_L2','c1_trim_door_R2','c1_trim_mirror_L2','c1_trim_mirror_R2')
# Chosen overrides take precedence over broad variant prefixes above.
allow=('c1_bumper_F107_','c1_hoodr107_','c1_headlight_L107_','c1_headlight_R107_','c1_tailgate107_','c1_F_black107','c1_shifter_lever_M_','c1_shifter_boot_M','c1_steerpe_','cit_c1_11_taillightR_reverse_light')
p.joinpath('textures').mkdir(exist_ok=True)
for node in s.graph.nodes_geometry:
 T,key=s.graph[node];m=s.geometry[key]
 if not isinstance(m,trimesh.Trimesh):continue
 mat=getattr(m.visual.material,'name','') or 'unnamed';V=trimesh.transform_points(m.vertices,T);N=m.vertex_normals@T[:3,:3].T;N/=np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-9);F=m.faces.copy();UV=getattr(m.visual,'uv',None);UV=UV if UV is not None else np.zeros((len(V),2))
 isrim=node in ['c1steelwheel_16a_16x71','c1_hubcap_01a_107']
 keep=isrim or any(node.startswith(x) for x in allow) or not any(node.startswith(x) for x in exclude)
 if node=='body' or '_jdm_' in node or mat in ['tire','blur_lip','blur_rim'] or np.max(np.abs(V[:,2]))>2.05:keep=False
 if mat=='c1_chmsl' and node.startswith('c1_taillight_R'):keep=False
 if not keep:dropped.append(node);continue
 # Strict duplicate primitive removal, including duplicate early head/tail assemblies.
 sig=(mat,hashlib.sha256(np.round(V[F],5).tobytes()+np.round(UV[F],5).tobytes()).hexdigest())
 if sig in seen:continue
 seen.add(sig)
 if isrim:
  # Face is +X in source. Keep local wheel axis, flip X to the left-hand FH2 face.
  V=V*np.array([-1,1,1])+wheel;N=N*np.array([-1,1,1]);F=F[:,::-1];mat='RIM_CAP' if node=='c1_hubcap_01a_107' else 'RIM_STEEL'
 else:
  if node.startswith('c1_steerpe_'):
   a=np.deg2rad(65);R=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
   V=(V-[0,.06,.015])@R.T+[.34,.82,.38];N=N@R.T
  V=V*np.array([-1,1,1])+shift;N=N*np.array([-1,1,1]);F=F[:,::-1]
  if mat=='reverse_light':V[:,0]-=.37;V[:,2]-=.003
 frag=dict(node=node,mat=mat,V=V[F].reshape(-1,3),N=N[F].reshape(-1,3),UV=UV[F].reshape(-1,2));parts.setdefault(mat,[]).append(frag);chosen.append(node)
 if mat not in textures:
  image=getattr(m.visual.material,'baseColorTexture',None);factor=getattr(m.visual.material,'baseColorFactor',None)
  if image is None:
   rgb=tuple(int(x) for x in factor[:3]) if factor is not None else (60,60,60);image=Image.new('RGB',(64,64),rgb)
  if mat in ['c1_plastic','c1_swplastic']:image=Image.new('RGB',(64,64),(35,37,39))
  fn=hashlib.sha1(mat.encode()).hexdigest()[:10]+'.png';image.convert('RGB').save(p/'textures'/fn);textures[mat]=fn
wheels={k:dict(centre=np.array([x,.1511658,z]),radius=.27855) for k,x,z in [('HUB_LF',-.71,1.22),('HUB_RF',.71,1.22),('HUB_LR',-.705,-1.12),('HUB_RR',.705,-1.12)]}
pickle.dump(dict(parts=parts,wheels=wheels,ground=.1511658-.27855,wheelbase=2.34,materials=sorted(parts)),open(p/'geo.pkl','wb'))
(p/'source-selection.json').write_text(json.dumps(dict(chosen=chosen,dropped=dropped,textures=textures,axles=dict(front_z=1.17,rear_z=-1.17,source_y=.27855),review='Single loose wheel; axle and height setup requires in-game confirmation.'),indent=2))
print('Selected',len(chosen),'fragments; dropped',len(dropped),'variant fragments; textures',len(textures))
