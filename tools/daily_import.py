"""Personal batch import: archive assets are data only; no bundled code is executed."""
from pathlib import Path
import sys,json,subprocess,zipfile,hashlib
import numpy as np,trimesh
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/vendor/dragonff'))
from gtaLib import dff,txd

def convert_dff(model,texture,out):
 d=dff.dff();d.load_file(str(model));textures={}
 if texture:
  t=txd.txd();t.load_file(str(texture))
  for tex in t.native_textures:
   try:textures[tex.name.lower()]=Image.frombytes('RGBA',(tex.width,tex.height),bytes(tex.to_rgba()))
   except Exception as e: print('texture failed',tex.name,str(e))
 scene=trimesh.Scene();manifest=[]
 for clump in d.clumps:
  frames=clump.frame_list;world={}
  def transform(i):
   if i in world:return world[i]
   f=frames[i];m=np.eye(4);m[:3,:3]=np.array(f.rotation_matrix).T;m[:3,3]=f.position
   world[i]=transform(f.parent)@m if f.parent>=0 else m
   return world[i]
  for atomic_index,a in enumerate(clump.atomic_list):
   f=frames[a.frame];name=f.name or f'frame{a.frame}'
   ancestry=[];ancestor=a.frame
   while ancestor>=0:
    ancestry.append((frames[ancestor].name or '').lower());ancestor=frames[ancestor].parent
   if any(any(token in label for token in ['_dam','_vlo','extra']) for label in ancestry):continue
   g=clump.geometry_list[a.geometry]
   if not g.vertices:continue
   verts=np.array(g.vertices,float);T=transform(a.frame)
   faces=np.array([[x.a,x.b,x.c] for x in g.triangles]);ids=np.array([x.material for x in g.triangles])
   for j,mat in enumerate(g.materials):
    F=faces[ids==j]
    if not len(F):continue
    texname=mat.textures[0].name if mat.textures else '';colour=list(mat.color);paint=tuple(colour[:3]) in [(60,255,0),(255,0,175),(0,255,0),(255,0,255)]
    key='paint' if paint else texname or 'rgba_'+'_'.join(map(str,colour))
    image=textures.get(texname.lower());pbr=trimesh.visual.material.PBRMaterial(name=key,baseColorFactor=([180,180,185,255] if paint else colour),baseColorTexture=image,metallicFactor=.0,roughnessFactor=.6,alphaMode='BLEND' if colour[3]<250 else 'OPAQUE')
    uv=np.array(g.uv_layers[0]) if g.uv_layers else np.zeros((len(verts),2));uv[:,1]=1-uv[:,1]
    m=trimesh.Trimesh(verts,F,process=False,visual=trimesh.visual.TextureVisuals(uv=uv,material=pbr))
    if g.normals:m.vertex_normals=np.array(g.normals)
    m.remove_unreferenced_vertices()
    scene.add_geometry(m,node_name=f'{name}__a{atomic_index}m{j}',transform=T)
    manifest.append(dict(node=name,material=key,colour=colour,texture=texname,vertices=len(verts),faces=len(F)))
 # GTA wheel geometry is often instanced at only one dummy. Make copies at all four dummies.
 for clump in d.clumps:
  wheels=[(i,f) for i,f in enumerate(clump.frame_list) if f.name and f.name.lower() in ['wheel_lf_dummy','wheel_rf_dummy','wheel_lb_dummy','wheel_rb_dummy']]
  existing=[n for n in scene.graph.nodes_geometry if n.startswith('wheel')]
  if existing and wheels:
   # Any missing dummy inherits its opposite/front wheel's local mesh.
   for i,f in wheels:
    prefix=f.name.replace('_dummy','')
    if any(n.startswith(prefix+'__') or n.startswith(f.name+'__') for n in existing):continue
    src=[n for n in existing if 'rf' in n] or existing
    for n in src:
     st,key=scene.graph[n];geom=scene.geometry[key].copy();dest=transform(i)
     # Geometry transforms are relative to source dummy; retain its local atomic offset.
     sourceframe=next((k for k,x in enumerate(clump.frame_list) if x.name and n.startswith(x.name+'__')),None)
     rel=np.linalg.inv(transform(sourceframe))@st if sourceframe is not None else np.eye(4)
     if '_l' in f.name:rel[:3,:3]=rel[:3,:3]@np.diag([-1,-1,1])
     scene.add_geometry(geom,node_name=f.name+'__copy_'+n,transform=dest@rel)
 scene.export(out);return manifest

if __name__=='__main__':
 catalogue=json.loads((ROOT.parent/'Car Model Downloads/catalogue.json').read_text());base=ROOT/'cars/daily_batch'
 for c in catalogue:
  if c['status']!='downloaded':continue
  p=ROOT.parent/'Car Model Downloads'/c['file'];folder=base/c['name'];folder.mkdir(parents=True,exist_ok=True)
  if p.suffix=='.glb' or (folder/'source.glb').exists() and not list((folder/'raw').rglob('*.dff')):continue
  raw=folder/'raw';raw.mkdir(exist_ok=True)
  if p.suffix in ['.rar','.zip']:
   subprocess.run(['unar','-q','-s','-D','-o',str(raw),str(p),'*.dff','*.txd','*.obj','*.mtl'],check=True)
  ds=sorted(raw.rglob('*.dff'),key=lambda x:(len(x.parts),str(x)))
  if ds:
   tex=next(iter(raw.rglob('*.txd')),None)
   try:
    manifest=convert_dff(ds[0],tex,folder/'source.glb');(folder/'conversion.json').write_text(json.dumps(manifest,indent=2));print(c['name'],'DFF converted',len(manifest),flush=True)
   except Exception as e:print(c['name'],'conversion blocked:',str(e),flush=True)
  else:
   objs=list(raw.rglob('*.obj'))
   if objs:trimesh.load(objs[0],force='scene').export(folder/'source.glb');print(c['name'],'OBJ converted',flush=True)
   else:print(c['name'],'no supported geometry in archive',flush=True)
