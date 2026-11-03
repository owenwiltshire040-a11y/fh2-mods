from pathlib import Path
import pickle,numpy as np
p=Path(__file__).resolve().parent;g=pickle.load(open(p/'geo.pkl','rb'));out={};rim=[];black=[]
for mat,frags in g['parts'].items():
 for f in frags:
  f=dict(f);f['V']=f['V'].copy();f['V'][:,0]+=1.765872*.9962
  if mat in ['Rubber_Rough','Rubber_Rough222','black222','Iron_Clean_Distorted']:continue
  v=f['V'].reshape(-1,3,3);n=f['N'].reshape(-1,3,3);uv=f['UV'].reshape(-1,3,2);c=v.mean(1);near=np.zeros(len(v),bool);leftfront=np.zeros(len(v),bool)
  if mat in ['Material_111','black.001','black.002','Material_2125767099','black_base','black_reflection','chrome']:
   for corner,w in g['wheels'].items():
    centre=w['centre'];k=(np.hypot(c[:,1]-centre[1],c[:,2]-centre[2])<.315)&(np.abs(c[:,0]-centre[0])<.22);near|=k
    if corner=='HUB_LF':leftfront=k
   if leftfront.any():
    key='TESLA_RIM' if mat in ['Material_111','Material_2125767099','chrome'] else 'TESLA_RIM_BLACK';out.setdefault(key,[]).append(dict(f,mat=key,V=v[leftfront].reshape(-1,3),N=n[leftfront].reshape(-1,3),UV=uv[leftfront].reshape(-1,2)))
  keep=~near
  if keep.any():out.setdefault(mat,[]).append(dict(f,V=v[keep].reshape(-1,3),N=n[keep].reshape(-1,3),UV=uv[keep].reshape(-1,2)))
g['parts']=out;g['materials']=sorted(out);pickle.dump(g,open(p/'geo.pkl','wb'))
print('Separated rim triangles',[(k,sum(len(x['V'])//3 for x in out.get(k,[]))) for k in ['TESLA_RIM','TESLA_RIM_BLACK']])
