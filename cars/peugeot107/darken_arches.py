"""Separate inward-facing arch cavity faces from exterior paint."""
from pathlib import Path
import pickle,numpy as np
p=Path(__file__).resolve().parent;g=pickle.loads((p/'geo.pkl').read_bytes());kept=[];liners=[]
for frag in g['parts'].get('c1_paint',[]):
 V=frag['V'].reshape(-1,3,3);C=V.mean(1);N=frag['N'].reshape(-1,3,3).mean(1);select=np.zeros(len(C),bool)
 for z in [1.22,-1.12]:
  dv=C[:,1:]-np.array([.1511658,z]);rad=np.linalg.norm(dv,axis=1);dot=(N[:,1:]*dv).sum(1)
  select|=(abs(C[:,0])>.64)&(abs(C[:,0])<.85)&(C[:,1]>.08)&(C[:,1]<.65)&(abs(C[:,2]-z)<.40)&(dot<-.25*rad)
 for mask,dest,mat in [(select,liners,'ARCH_LINER'),(~select,kept,'c1_paint')]:
  if mask.any():dest.append(dict(frag,mat=mat,V=V[mask].reshape(-1,3),N=frag['N'].reshape(-1,3,3)[mask].reshape(-1,3),UV=frag['UV'].reshape(-1,3,2)[mask].reshape(-1,2)))
g['parts']['c1_paint']=kept;g['parts'].setdefault('ARCH_LINER',[]).extend(liners);g['materials']=sorted(g['parts']);(p/'geo.pkl').write_bytes(pickle.dumps(g));print('Mapped',sum(len(f['V'])//3 for f in liners),'inward arch faces to dark liners')
