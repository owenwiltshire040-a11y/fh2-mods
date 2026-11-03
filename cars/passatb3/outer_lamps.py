"""Use visible rear lens surfaces rather than recessed reflector meshes for reverse/turn emitters."""
from pathlib import Path
import pickle,numpy as np
p=Path(__file__).resolve().parent;g=pickle.load(open(p/'geo.pkl','rb'))
for name,inner in [('REVERSE_OUTER',True),('TURN_REAR_OUTER',False)]:
 fragments=[]
 for src in g['parts']['lampa__spec_trans']:
  v=src['V'].reshape(-1,3,3);c=v.mean(1);k=(c[:,2]<0)&(c[:,1]>.47)&((np.abs(c[:,0])<.59) if inner else (np.abs(c[:,0])>=.59))
  if not k.any():continue
  f=dict(src,mat=name);f['V']=v[k].reshape(-1,3).copy();f['V'][:,2]-=.002
  f['N']=src['N'].reshape(-1,3,3)[k].reshape(-1,3);f['UV']=src['UV'].reshape(-1,3,2)[k].reshape(-1,2);fragments.append(f)
 g['parts'][name]=fragments;print(name,sum(len(f['V'])//3 for f in fragments),'triangles')
g['materials']=sorted(g['parts']);pickle.dump(g,open(p/'geo.pkl','wb'))
