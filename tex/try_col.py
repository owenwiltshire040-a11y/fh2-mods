import numpy as np, itertools, gcn, texture2ddecoder as t2d, sys
from PIL import Image
f=sys.argv[1]; W,H=int(sys.argv[2]),int(sys.argv[3])
raw=open(f,'rb').read()[0x53:]
bw,bh=W//4,H//4; nb=bw*bh
blocks=np.frombuffer(raw[:nb*16],np.uint8).reshape(nb,16)
def dec(fmt):
    fn={'bc7':t2d.decode_bc7,'bc3':t2d.decode_bc3,'bc5':None}[fmt]
    img=np.frombuffer(fn(blocks.tobytes(),4,nb*4),np.uint8).reshape(4,nb*4,4)  # decode as a 4 x (nb*4) strip
    return img.reshape(4,nb,4,4).transpose(1,0,2,3)   # (nb,4,4,4) BGRA
res=[]
for fmt in ('bc7','bc3'):
    px=dec(fmt).astype(np.int16); val=px[...,:3].mean((1,2,3))
    for perm in itertools.permutations(['x0','x1','x2','y0','y1','y2']):
        gcn.MICRO[128]=list(perm)
        for cfg,banks,mar in [('P4_16x16',8,2),('P4_16x16',8,1),('P4_16x16',16,2)]:
            try: i=gcn.offsets(bw,bh,128,cfg,banks,1,1,mar)//16
            except Exception: continue
            if i.max()>=nb or len(np.unique(i))!=nb: continue
            im=val[i]
            s=np.abs(np.diff(im,axis=0)).mean()+np.abs(np.diff(im,axis=1)).mean()
            res.append((s,fmt,perm,cfg,banks,mar))
res.sort(key=lambda r:r[0])
for r in res[:6]: print(r)
s,fmt,perm,cfg,banks,mar=res[0]
gcn.MICRO[128]=list(perm); i=gcn.offsets(bw,bh,128,cfg,banks,1,1,mar)//16
px=dec(fmt)[i]   # (bh,bw,4,4,4)
img=px.transpose(0,2,1,3,4).reshape(H,W,4)[...,[2,1,0,3]]
Image.fromarray(img[...,:3]).save(sys.argv[4])
