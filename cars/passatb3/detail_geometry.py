"""Tag cabin surfaces by source node ancestry; retain source geometry."""
from pathlib import Path
import pickle,numpy as np,trimesh
p=Path(__file__).resolve().parent;s=trimesh.load(p/'stock.glb',force='scene');parents=s.graph.transforms.parents;g=pickle.load(open(p/'geo.pkl','rb'));out={}
for mat,frags in g['parts'].items():
 for frag in frags:
  node=frag['node'];anc=[];cur=node
  while cur in parents:cur=parents[cur];anc.append(cur)
  group=mat
  if any(x.startswith(('pasB3_seat','pasB3_seats')) for x in anc) and mat!='chromeb3':group='CABIN_CLOTH'
  elif any(x.startswith('pasB3_needle') for x in anc):group='CABIN_NEEDLE'
  elif 'pasB3_dash' in anc and mat=='pasB3_priborka':group='CABIN_GAUGES'
  elif any(x in anc for x in ['pasB3_dash','pasB3_steer']) and mat in ['interior_lod0__spec','Matte__FF1B1B1B__spec']:group='CABIN_DASH'
  elif mat=='interior_lod0__spec':group='CABIN_TRIM'
  f=dict(frag,mat=group)
  if group=='CABIN_GAUGES':
   v=f['V'];f['UV']=np.stack([1-(v[:,0]+.55)/.331,1-(v[:,1]-.578)/.105],axis=1).clip(0,1)
  out.setdefault(group,[]).append(f)
g['parts']=out;g['materials']=sorted(out);pickle.dump(g,open(p/'geo.pkl','wb'));print('Cabin groups:',{k:sum(len(x['V'])//3 for x in v) for k,v in out.items() if k.startswith('CABIN')})
