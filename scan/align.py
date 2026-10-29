import trimesh, numpy as np
from scipy.spatial import cKDTree
car=trimesh.load('car_raw.glb',force='mesh',process=False)
A=np.load('carax.npz'); c,ax,n,d=A['c'],A['ax'],A['n'],A['d']
T=np.load('../car207/fitted_207.npz')
tpl=np.concatenate([T['paint_P'],T['glass_P'],T['tail_P'],T['head_P'],T['lens_P'],T['trim_P']])
S=4.030/1.9962221257566428
up=n; f3=np.array([-ax[0],0,-ax[1]]); f3-=up*(f3@up); f3/=np.linalg.norm(f3); r3=np.cross(f3,up)
P=car.vertices
Q=np.stack([S*(P@r3), S*(P@up+d), S*(P@f3)],1)
Q[:,0]-=(Q[:,0].max()+Q[:,0].min())/2  # rough centring
Q[:,2]+= (tpl[:,2].max()+tpl[:,2].min())/2-(np.percentile(Q[:,2],99.8)+np.percentile(Q[:,2],0.2))/2
tree=cKDTree(tpl)
sample=Q[np.random.default_rng(1).choice(len(Q),20000,replace=False)]
R=np.eye(3); t=np.zeros(3); sc=1.0
def icp(scale):
    global R,t,sc
    for it in range(60):
        X=sc*sample@R.T+t; dist,idx=tree.query(X); m=dist<np.percentile(dist,80)
        a=sample[m]; b=tpl[idx[m]]
        ma,mb=a.mean(0),b.mean(0); A0=a-ma; B0=b-mb
        U,Sg,Vt=np.linalg.svd(A0.T@B0); D=np.diag([1,1,np.sign(np.linalg.det(Vt.T@U.T))])
        R=Vt.T@D@U.T
        sc=(Sg*np.diag(D)).sum()/(A0**2).sum() if scale else 1.0
        t=mb-sc*R@ma
    X=sc*sample@R.T+t; dist,_=tree.query(X)
    return np.median(dist), np.percentile(dist,90)
print('rigid  median/90%', icp(False), 'angle deg', np.degrees(np.arccos((np.trace(R)-1)/2)))
Rr,tr=R.copy(),t.copy()
print('scaled median/90%', icp(True), 'scale', sc)
np.savez('align.npz',S=S,r3=r3,up=up,f3=f3,d=d,R=Rr,t=tr,x0=0)
QQ=Q@Rr.T+tr
np.save('Q_fh2.npy',QQ)
print('scan bounds FH2', QQ.min(0).round(3), QQ.max(0).round(3)); print('template', tpl.min(0).round(3), tpl.max(0).round(3))
