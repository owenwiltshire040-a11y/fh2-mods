import numpy as np, itertools, gcn, texture2ddecoder as t2d, sys
from PIL import Image
f=sys.argv[1]; W,H=int(sys.argv[2]),int(sys.argv[3]); off0=int(sys.argv[5],0) if len(sys.argv)>5 else 0x53
raw=open(f,'rb').read()[off0:]
bw,bh=W//4,H//4; nb=bw*bh
blocks=np.frombuffer(raw[:nb*16],np.uint8).reshape(nb,16)
img=np.frombuffer(t2d.decode_bc7(blocks.tobytes(),4,nb*4),np.uint8).reshape(nb,4,4,4)[...,:3].astype(np.int16)
L=img.mean(3)  # (nb,4,4)
def score(i):
    b=L[i]   # (bh,bw,4,4)
    s=np.abs(b[:,1:,:,0]-b[:,:-1,:,3]).mean()+np.abs(b[1:,:,0,:]-b[:-1,:,3,:]).mean()
    return s
res=[]
for perm in itertools.permutations(['x0','x1','x2','y0','y1','y2']):
    gcn.MICRO[128]=list(perm)
    for cfg in ['P4_16x16']:
      for banks in (8,16):
        for mar in (1,2):
          for bwi,bhi in ((1,1),):
            try: i=gcn.offsets(bw,bh,128,cfg,banks,bwi,bhi,mar)//16
            except Exception: continue
            if i.max()>=nb or len(np.unique(i))!=nb: continue
            res.append((score(i),perm,cfg,banks,mar,bwi,bhi))
res.sort(key=lambda r:r[0])
for r in res[:8]: print(r)
s,perm,cfg,banks,mar,bwi,bhi=res[0]
gcn.MICRO[128]=list(perm); i=gcn.offsets(bw,bh,128,cfg,banks,bwi,bhi,mar)//16
px=np.frombuffer(t2d.decode_bc7(blocks.tobytes(),4,nb*4),np.uint8).reshape(nb,4,4,4)[i]
out=px.transpose(0,2,1,3,4).reshape(H,W,4)[...,[2,1,0]]
Image.fromarray(out).save(sys.argv[4])
