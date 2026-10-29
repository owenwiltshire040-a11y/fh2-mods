import numpy as np, itertools, gcn
from bc import bc4_decode_blocks
d=np.frombuffer(open('Front.swatchbin','rb').read()[0x53:],np.uint8)
nb=256*256; px=bc4_decode_blocks(d[:nb*8].reshape(nb,8)).astype(np.int16)
def score(i):
    img=px[i].transpose(0,2,1,3).reshape(1024,1024)
    return np.abs(np.diff(img,axis=0)).mean()+np.abs(np.diff(img,axis=1)).mean()
res=[]
bits=['x0','x1','x2','y0','y1','y2']
for perm in itertools.permutations(bits):
    gcn.MICRO[64]=list(perm)
    for cfg,banks,mar in [('P4_16x16',8,2),('P4_8x16',8,2),('P4_16x16',8,1),('P2',16,2)]:
        i=gcn.offsets(256,256,64,cfg,banks,1,1,mar)//8
        res.append((score(i),perm,cfg,banks,mar))
res.sort(key=lambda r:r[0])
for r in res[:8]: print(r)
