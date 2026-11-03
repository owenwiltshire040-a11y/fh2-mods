"""Inspect the built wheel, not just its spec: reject donor faces and malformed morphs."""
import argparse,hashlib,json,pickle,struct,zipfile
from pathlib import Path
import numpy as np
from geometry import Part
from body_swap import material_names
from gltf_bridge import decode_group
from wheelfit import load_spec,tyre_size
from carpreview import morph_rim

def read_wheel(path):
 with zipfile.ZipFile(path) as z:
  name=next(n for n in z.namelist() if n.lower().endswith('_wheellf.modelbin'))
  return Part(z.read(name))

def face_signature(p):
 names=material_names(p);tri=[]
 for r in p.render:
  if r['group']!=0 or names[id(r['blob'])]=='inner_rim' or struct.unpack_from('<H',r['blob']['data'],4)[0]!=3:continue
  d,_=decode_group(p,0);q=d['POSITION'][:,:3][np.array(r['indices']).reshape(-1,3)]
  area=np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1);tri.append(q[area>1e-10])
 if not tri:raise ValueError('Wheel has no visible custom face')
 a=np.round(np.concatenate(tri).reshape(-1,9),5);a=a[np.lexsort(a.T[::-1])]
 return hashlib.sha256(a.tobytes()).hexdigest()

def check(S,path):
 p=read_wheel(path);sig=face_signature(p)
 if sig==face_signature(read_wheel(S.DONOR_ZIP)):raise ValueError('Built wheel still has the unmodified Charger face')
 result=dict(valid=True,donor_face_removed=True,face_sha256=sig)
 if getattr(S,'REQUIRE_SOURCE_WHEELS',False):
  names=material_names(p);renders=[r for r in p.render if names[id(r['blob'])]=='source_rim' and struct.unpack_from('<H',r['blob']['data'],4)[0]==3]
  if len(renders)!=1:raise ValueError('Expected exactly one source face at LOD 0')
  r=renders[0];d,_=decode_group(p,r['group']);idx=np.unique(r['indices']);positions=d['POSITION'][:,:3];t=tyre_size(S);v=morph_rim(positions,p.groups[0]['morph'],t['rim_radius'],t['width'])[idx]
  if not np.isfinite(v).all():raise ValueError('Non-finite rim positions after diameter/width morphs')
  source=json.loads((Path(S.HERE)/'source-wheel.json').read_text());radius=float(np.hypot(v[:,1],v[:,2]).max());depth=float(np.ptp(v[:,0]))
  if abs(radius-source['outer_lip_radius'])>.002:raise ValueError('Built rim diameter differs from reviewed source by more than 2 mm')
  if abs(depth-source['fitted_depth'])>.002:raise ValueError('Built axial depth differs from reviewed source by more than 2 mm')
  if len(r['indices'])//3!=source['triangles']:raise ValueError('Built wheel lost or gained source faces')
  if depth>t['width']+.010:raise ValueError('Source rim is wider than the selected tyre envelope')
  face=positions[np.array(r['indices']).reshape(-1,3)];centres=face.mean(1)
  normals=np.cross(face[:,1]-face[:,0],face[:,2]-face[:,0]);areas=np.linalg.norm(normals,axis=1)
  interior=(np.hypot(centres[:,1],centres[:,2])<.75*float(np.hypot(positions[idx,1],positions[idx,2]).max()))&(np.abs(normals[:,0])>.6*areas)&(areas>1e-10)
  face_fraction=float((np.average(centres[interior,0],weights=areas[interior])-positions[idx,0].min())/depth) if interior.any() and depth>1e-6 else 0
  if depth>.02 and face_fraction>.65:raise ValueError('Wheel spokes face inward: source wheel orientation needs review')
  barrels=[b for b in p.render if names[id(b['blob'])]=='inner_rim' and struct.unpack_from('<H',b['blob']['data'],4)[0]==3]
  if len(barrels)!=1:raise ValueError('Expected one open inner barrel')
  q=positions[np.array(barrels[0]['indices']).reshape(-1,3)]
  normal=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
  if len(q)!=128 or np.any(np.linalg.norm(normal,axis=1)<1e-10) or np.any(np.abs(normal[:,0])>1e-7):raise ValueError('Inner barrel contains a plate that could hide source spokes')
  for other in p.render:
   if other['group']==0:continue
   a,_=decode_group(p,other['group']);q=a['POSITION'][:,:3][np.array(other['indices']).reshape(-1,3)]
   if np.any(np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)>1e-10):raise ValueError('Donor face detail or blur geometry remains in another group/LOD')
  result.update(source_triangles=source['triangles'],runtime_outer_radius=radius,runtime_axial_depth=depth,nominal_rim_in=S.PHYSICS['tyres']['rim_in'],all_donor_face_lods_removed=True,generated_open_barrel=True,spoke_depth_fraction=face_fraction)
 return result

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('spec');a.add_argument('zip');a.add_argument('--out');x=a.parse_args()
 try:r=check(load_spec(x.spec),x.zip)
 except (ValueError,AssertionError) as e:raise SystemExit('Wheel build blocked: '+str(e))
 if x.out:Path(x.out).write_text(json.dumps(r,indent=2)+'\n')
 print('Built wheel verified:',r)
