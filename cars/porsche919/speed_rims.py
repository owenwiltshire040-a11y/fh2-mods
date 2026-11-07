"""Step 8 (Claude 7 Nov, v0.1.4): the Porsche's high-speed wheel pass, after Codex's RB22 opaque_speed_rims.py +
rim_spin_texture.py. (1) The source rim, built only at LODs 3/4/8/16, is cloned to LODs 32/64 so it stays drawn at
a distance. (2) An opaque dished face is added in the native spin pass (0x1c) at every LOD; its profile follows the
source rim's own outer surface (outermost depth per radial band, 1 mm behind it). (3) Its texture is the source rim
projected face-on and rotationally blurred (+-33 deg Gaussian), material 'p919_opaque_spin' (the source_rim MatI
retextured). The blur_lip placeholders stay single triangles.   python3 cars/porsche919/speed_rims.py PKG_DIR
"""
from pathlib import Path
import sys,json,struct,zipfile,uuid,hashlib
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'f1'),str(ROOT/'tex')]
from geometry import Part
from body_swap import material_names
from gltf_bridge import encode_group,decode_group,O_UVT
from fhmat import add_mesh,add_material,retexture
from swatch import DATA,decode_level,write_like
MEDIA='POR_Porsche919_17_';CAR=Path(f'media/cars/{MEDIA}.zip')
LODS=[3,4,8,16,32,64];EXTRA=[(32,4),(64,5)];SPIN=0x1c;SIZE=1024;SEG=64
SWATCH='Textures/custom/Swatches/p919_spin_face.swatchbin'
lod=lambda r:struct.unpack_from('<H',r['blob']['data'],4)[0]
mpass=lambda r:struct.unpack_from('<I',r['blob']['data'],8)[0]

def all_lods(part):
 nm=material_names(part);rims=[r for r in part.render if nm[id(r['blob'])]=='source_rim']
 have=sorted(lod(r) for r in rims)
 if have==LODS:return 0
 assert have==[3,4,8,16],have
 ref=next(r for r in rims if lod(r)==16);mid=struct.unpack_from('<h',ref['blob']['data'])[0]
 for mask,idx in EXTRA:
  n=add_mesh(part,ref,mid);n['indices']=list(ref['indices']);d=n['blob']['data'];struct.pack_into('<H',d,4,mask)
  if len(d)>6:d[6]=idx
 return len(EXTRA)

def profile(P,R):
 r=np.hypot(P[:,1],P[:,2]);fr=np.array([0,.06,.12,.2,.3,.42,.55,.68,.8,.9,.96,.995])
 depth=[]
 for a,b in zip(np.r_[0,fr[:-1]],fr):
  s=(r>=a*R-1e-6)&(r<=max(b,.02)*R+1e-6)
  depth.append(P[s,0].min() if s.any() else np.nan)
 depth=np.array(depth);depth=np.where(np.isnan(depth),np.nanmin(depth),depth)+.001
 return list(zip(depth,fr))

def speed_face(prof,R):
 depth,radial=np.array(prof).T;radial=radial*R;ang=np.arange(SEG)*2*np.pi/SEG
 pts=[(depth[0],0.,0.)];nrm=[(-1.,0.,0.)];tan=[(0.,0.,1.,1.)];slope=np.gradient(depth,np.maximum(radial,1e-6))
 for x,r,s in zip(depth[1:],radial[1:],slope[1:]):
  for a in ang:
   c,sn=np.cos(a),np.sin(a);pts.append((x,r*c,r*sn));nrm.append((-1.,s*c,s*sn));tan.append((0.,-sn,c,1.))
 tri=[]
 for i in range(SEG):
  j=(i+1)%SEG;tri.append((0,1+j,1+i))
  for ring in range(len(prof)-2):
   inner=1+ring*SEG;outer=inner+SEG;tri+= [(inner+i,inner+j,outer+i),(inner+j,outer+j,outer+i)]
 pts,nrm,tri=map(np.asarray,(pts,nrm,tri));nrm=nrm/np.linalg.norm(nrm,axis=1,keepdims=True)
 f=pts[tri];assert np.all(np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0])[:,0]<0)
 return pts,nrm,np.asarray(tan,float),tri

def add_face(raw):
 part=Part(raw);n_lod=all_lods(part);nm=material_names(part)
 rims=sorted([r for r in part.render if nm[id(r['blob'])]=='source_rim'],key=lod);assert [lod(r) for r in rims]==LODS
 assert not any(mpass(r)==SPIN and len(r['indices'])>3 for r in part.render)
 g=part.groups[0];ids=np.unique(rims[0]['indices']);src=np.asarray(g['positions'])[ids];R=float(np.hypot(src[:,1],src[:,2]).max())
 prof=profile(src,R);pts,nrm,tan,tri=speed_face(prof,R*.995)
 uv=pts[:,1:3]/(2*R)+.5;attrs=dict(POSITION=pts,NORMAL0=nrm,TANGENT0=tan,TANGENT1=tan);attrs.update({f'TEXCOORD{i}':uv for i in range(4)})
 rows,transform=encode_group(part,0,attrs);off=len(g['positions'])
 g['positions'].extend(map(tuple,pts));g['attrs'].extend(rows)
 mo=np.zeros((len(pts),4,4),'<f2');mo[:,0,3]=mo[:,2,3]=1;mo[:,1,1:3]=1.3247*pts[:,1:3];g['morph'].extend(r.tobytes() for r in mo)
 mid=struct.unpack_from('<h',rims[0]['blob']['data'])[0]
 for rim in rims:
  fast=add_mesh(part,rim,mid);fast['indices']=(tri+off).ravel().tolist();d=fast['blob']['data']
  struct.pack_into('<I',d,8,SPIN);struct.pack_into('<20f',d,O_UVT,*transform)
 out=part.build();q=Part(out);qn=material_names(q)
 assert sorted(lod(r) for r in q.render if mpass(r)==SPIN and len(r['indices'])>3)==LODS
 assert sorted(lod(r) for r in q.render if qn[id(r['blob'])]=='source_rim' and mpass(r)==0x11)==LODS
 return out,dict(added_far_lods=n_lod,face_triangles_per_lod=len(tri),source_radius=R,profile=[(round(float(a),4),b) for a,b in prof])

def bake(wheel_raw,template):
 w=Part(wheel_raw);nm=material_names(w);face=next(r for r in w.render if nm[id(r['blob'])]=='source_rim')
 V,_=decode_group(w,0);T=np.asarray(face['indices']).reshape(-1,3);P=V['POSITION'];ids=np.unique(T)
 R=np.hypot(P[ids,1],P[ids,2]).max();proj=(P[:,1:3]/(2*R)+.5)*(SIZE-1)
 src=decode_level(template,DATA,SIZE,SIZE,'2d');tx=(V['TEXCOORD0'][T].mean(1)%1*SIZE).astype(int).clip(0,SIZE-1)
 col=src[tx[:,1],tx[:,0],:3].astype(float);depth=P[T,0].mean(1)
 # draw back to front: deepest (largest x) first, the outer face last. The BBS base texture is black (the
 # spokes read from lighting), so the face is also shaded by depth: spoke faces dark grey, openings near black.
 img=Image.new('RGB',(SIZE,SIZE),(12,12,13));dr=ImageDraw.Draw(img)
 for i in np.argsort(-depth):dr.polygon([tuple(p) for p in proj[T[i]]],fill=tuple(np.clip(10+34*(1-np.clip(depth[i]/.12,0,1))+.85*col[i],0,255).astype(int)))
 ang=np.linspace(-33,33,23);wt=np.exp(-.5*(ang/21)**2);wt/=wt.sum();acc=np.zeros((SIZE,SIZE,3),np.float32)
 for a,k in zip(ang,wt):acc+=np.asarray(img.rotate(float(a),resample=Image.Resampling.BILINEAR,fillcolor=(12,12,13)))*k
 rgba=np.full((SIZE,SIZE,4),255,np.uint8);rgba[...,:3]=np.rint(acc).astype(np.uint8);assert np.ptp(rgba[...,0])>6   # black BBS rims: low contrast is correct
 sw=bytearray(write_like(template,rgba));sw[0x30:0x40]=uuid.UUID('a9190017-5e1d-4a11-8c3e-7a1fe00d1e03').bytes_le
 return bytes(sw),Image.fromarray(rgba[...,:3])

def set_material(raw,paths):
 p=Part(raw);tpl=next(b['data'] for b in p.b.blobs if b['tag']=='MatI' and p.b.meta(b,'Name')==b'source_rim')
 mid=add_material(p,'p919_opaque_spin',retexture(tpl,paths),paths)
 fast=[r for r in p.render if mpass(r)==SPIN and len(r['indices'])>3];assert sorted(lod(r) for r in fast)==LODS
 for r in fast:struct.pack_into('<h',r['blob']['data'],0,mid)
 return p.build()

def apply(pkg,preview=None):
 arc=pkg/CAR
 with zipfile.ZipFile(arc) as z:infos=z.infolist();E={i.filename:z.read(i) for i in infos}
 wheels=[n for n in E if n.lower().endswith(('_wheellf.modelbin','_wheellr.modelbin'))];assert wheels
 rim=next(n for n in E if '/source_rim_' in n.lower());gloss=next(n for n in E if '/gloss_' in n.lower())
 pre=f'Game:\\Media\\cars\\{MEDIA}\\';paths=[pre+SWATCH.replace('/','\\'),pre+gloss.replace('/','\\')]
 rep={}
 for n in wheels:
  E[n],rep[n]=add_face(E[n])
 tex,img=bake(E[wheels[0]],E[rim])
 if preview:img.save(preview)
 for n in wheels:E[n]=set_material(E[n],paths);rep[n]['mesh_sha256']=hashlib.sha256(E[n]).hexdigest()
 E[SWATCH]=tex
 tmp=arc.with_suffix('.tmp')
 with zipfile.ZipFile(tmp,'w') as z:
  for i in infos:z.writestr(i,E[i.filename])
  zi=zipfile.ZipInfo(SWATCH,date_time=(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,tex)
 tmp.replace(arc)
 with zipfile.ZipFile(arc) as z:assert z.testzip() is None
 report=dict(valid=True,wheels=rep,spin_artwork='source rim face, angular blur, opaque',runtime_status='Pending driving check')
 (pkg/'rim-speed-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report)[:600])
if __name__=='__main__':apply(Path(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else None)
