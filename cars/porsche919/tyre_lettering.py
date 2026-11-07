"""Step 7 (Claude 7 Nov, v0.1.3): one consistent tyre at every speed with the source Michelin sidewall art.

Codex's RB22 method (cars/redbullrb22/tyre_sidewall.py + tyre_lettering.py): the game's own OW_F1 library tyre (drawn
at every wheel speed) shipped in the mod as tire_919_17, its 'sidewall' meshes given an interior_lod1 material whose
colour swatch is a flat disc projection (u = .5 -/+ z / 2E, v = .5 - y / 2E, E = .225, mirrored per side), loose in
media/cars/_library/textures/p919/swatches. Here the disc is BAKED from the source tyre (TYRE_LF, EXT_Tyre /
Tyre_D.dds): its outer-face triangles are rasterised into the disc with the source radius range (bead .. face edge)
mapped onto OW_F1's sidewall radius range, seen from outside the car (image right = -z, up = +y).
  python3 cars/porsche919/tyre_lettering.py PKG_DIR [--preview out.png]
"""
from pathlib import Path
import sys,json,struct,zipfile,uuid,argparse
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'f1'),str(ROOT/'tex')]
from geometry import Part
from body_swap import material_names
import fhmat
from swatch import write_like
OW_F1=ROOT.parent/'FH2 Renderer/game/Anthem/Mount/media/cars/_library/scene/tires/tire_OW_F1.zip'
NAME='919_17';MEMBER=f'tireL_{NAME}.modelbin';TYRE=Path(f'media/cars/_library/scene/tires/tire_{NAME}.zip')
SIDES=Path('media/cars/_library/textures/p919/swatches');COLOUR=SIDES/'p919_sidewall.swatchbin';GLOSS=SIDES/'p919_sidewall_gloss.swatchbin'
E=.225;S=1024;RUBBER=(24,23,24);UVT=0x69
game=lambda p:'Game:\\'+str(p).replace('/','\\')

def sidewall_radii(raw):
 p=Part(raw);nm=material_names(p);P=np.array(p.groups[0]['positions'])
 ids=sorted({i for r in p.render if nm[id(r['blob'])]=='sidewall' for i in r['indices']})
 rr=np.hypot(P[ids,1],P[ids,2]);return float(rr.min()),float(rr.max())

def bake(lo,hi):
 import trimesh
 sc=trimesh.load(HERE/'source/gtp_porsche_919_2017.glb',force='scene',process=False)
 T,key=sc.graph['TYRE_LF_1'];m=sc.geometry[key]
 V=trimesh.transform_points(m.vertices,T)*[1,1,-1];F=m.faces;UV=m.visual.uv
 tex=np.array(m.visual.material.baseColorTexture.convert('RGB')).astype(np.float32);th,tw=tex.shape[:2]
 c=(V.max(0)+V.min(0))/2;L=V-c;r=np.hypot(L[:,1],L[:,2]);width=np.ptp(V[:,0])
 tri=L[F];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
 outer=(tri[:,:,0].mean(1)<-width*.2)&(np.abs(n[:,0])>.55)            # left wheel: outward is -x
 r_in,r_out=r[F[outer]].min(),r[F[outer]].max()
 rho=lo+(r-r_in)/(r_out-r_in)*(hi-lo)                                   # source radius -> OW_F1 sidewall radius
 X=-L[:,2]/np.maximum(r,1e-9)*rho;Y=L[:,1]/np.maximum(r,1e-9)*rho       # seen from outside: right = -z, up = +y
 px=np.c_[(X/(2*E)+.5)*S,(.5-Y/(2*E))*S]
 img=np.zeros((S,S,3),np.float32);img[:]=RUBBER;hit=np.zeros((S,S),bool)
 uvimg=np.c_[UV[:,0]*(tw-1),(1-UV[:,1])*(th-1)]
 for f in F[outer]:
  a,b,cc=px[f];x0,y0=np.floor(np.minimum(np.minimum(a,b),cc)).astype(int);x1,y1=np.ceil(np.maximum(np.maximum(a,b),cc)).astype(int)
  x0,y0=max(x0,0),max(y0,0);x1,y1=min(x1,S-1),min(y1,S-1)
  if x1<x0 or y1<y0:continue
  gx,gy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
  d=(b[1]-cc[1])*(a[0]-cc[0])+(cc[0]-b[0])*(a[1]-cc[1])
  if abs(d)<1e-9:continue
  w0=((b[1]-cc[1])*(gx-cc[0])+(cc[0]-b[0])*(gy-cc[1]))/d;w1=((cc[1]-a[1])*(gx-cc[0])+(a[0]-cc[0])*(gy-cc[1]))/d;w2=1-w0-w1
  ins=(w0>=-1e-4)&(w1>=-1e-4)&(w2>=-1e-4)
  if not ins.any():continue
  u=w0*uvimg[f[0],0]+w1*uvimg[f[1],0]+w2*uvimg[f[2],0];v=w0*uvimg[f[0],1]+w1*uvimg[f[1],1]+w2*uvimg[f[2],1]
  u=np.mod(u,tw);v=np.mod(v,th)
  from scipy.ndimage import map_coordinates
  col=np.stack([map_coordinates(tex[...,k],[v[ins],u[ins]],order=1,mode='wrap') for k in range(3)],1)
  yy=(gy[ins]-.5).astype(int);xx=(gx[ins]-.5).astype(int);img[yy,xx]=col;hit[yy,xx]=True
 return np.clip(img,0,255).astype(np.uint8),dict(source_bead=float(r_in),source_face_edge=float(r_out),outer_triangles=int(outer.sum()),covered=float(hit.mean()))

def map_sidewalls(raw,textures):
 p=Part(raw);nm=material_names(p)
 sides=[r for r in p.render if nm[id(r['blob'])]=='sidewall'];assert len(sides)==6 and all(r['group']==0 for r in sides)
 side=set().union(*(set(r['indices']) for r in sides));tread=set().union(*(set(r['indices']) for r in p.render if r not in sides))
 assert side.isdisjoint(tread)
 mid=fhmat.add_material(p,'p919_sidewall',fhmat.retexture((ROOT/'f1/matI_lod1.bin').read_bytes(),textures),textures)
 at=p.bufs[('VerB',0)]
 for s in sides:
  d=s['blob']['data'];lay=[e for e in p.b.vertex_layouts()[struct.unpack_from('<I',d,0x31)[0]] if e['slot']==1]
  assert [(e['name'],e['format']) for e in lay[:2]]==[('NORMAL0',10),('TEXCOORD0',35)]
  struct.pack_into('<h',d,0,mid);struct.pack_into('<4f',d,UVT,0.,1.,0.,1.)
 rows=[bytearray(x) for x in p.groups[0]['attrs']]
 for i in side:
  x,y,z=p.groups[0]['positions'][i];u=.5+(-z if x<.5 else z)/(2*E);v=.5-y/(2*E);assert 0<=u<=1 and 0<=v<=1
  struct.pack_into('<HH',rows[i],8,round(u*65535),round(v*65535))
 p.groups[0]['attrs']=[bytes(r) for r in rows]
 out=p.b.write() if False else p.build();q=Part(out)
 assert q.groups[0]['positions']==Part(raw).groups[0]['positions'] and q.groups[0]['morph']==Part(raw).groups[0]['morph']
 assert sum(1 for r in q.render if material_names(q)[id(r['blob'])]=='p919_sidewall')==6
 return out

def apply(pkg,preview=None):
 raw=zipfile.ZipFile(OW_F1).read('tireL_OW_F1.modelbin');lo,hi=sidewall_radii(raw)
 img,info=bake(lo,hi)
 if preview:Image.fromarray(img).save(preview)
 if pkg is None:print(info,lo,hi);return
 t1024=(ROOT/'tex/PEU_207SEHDi_08_Interior_DIFF_7b3d1f55-6273-410e-adf0-6ff29a14784f.swatchbin').read_bytes()
 t512=(ROOT/'tex/PEU_207SEHDi_08_Rad_Fixed_DiffuseFrontReflector_fa6144d2-c78f-41d2-9eaa-2f61cb81d1dc.swatchbin').read_bytes()
 col=bytearray(write_like(t1024,np.dstack([img,np.full((S,S),255,np.uint8)])));col[0x30:0x40]=uuid.UUID('a9190017-5e1d-4a11-8c3e-7a1fe00d1e01').bytes_le
 gl=bytearray(write_like(t512,np.dstack([np.full((512,512,3),55,np.uint8),np.full((512,512),255,np.uint8)])));gl[0x30:0x40]=uuid.UUID('a9190017-5e1d-4a11-8c3e-7a1fe00d1e02').bytes_le
 model=map_sidewalls(raw,[game(COLOUR),game(GLOSS)])
 (pkg/SIDES).mkdir(parents=True,exist_ok=True);(pkg/COLOUR).write_bytes(bytes(col));(pkg/GLOSS).write_bytes(bytes(gl))
 (pkg/TYRE).parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(pkg/TYRE,'w',zipfile.ZIP_DEFLATED) as z:z.writestr(MEMBER,model)
 dbp=pkg/'database.json';db=json.loads(dbp.read_text());rows=db['tables']['List_UpgradeTireCompound']['insert']
 for r in rows:r['TireModelName']=NAME
 dbp.write_text(json.dumps(db,indent=1)+'\n')
 info.update(valid=True,library_tyre=str(TYRE),base='OW_F1',sidewall_radius=(lo,hi),compound_rows=len(rows),runtime_status='Pending renderer view')
 (pkg/'tyre-check.json').write_text(json.dumps(info,indent=2)+'\n');print(info)

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('pkg',nargs='?');a.add_argument('--preview');x=a.parse_args()
 apply(Path(x.pkg) if x.pkg else None,x.preview)
