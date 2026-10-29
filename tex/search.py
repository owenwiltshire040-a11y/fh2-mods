import numpy as np, itertools
from bc import bc4_block
from gcn import offsets
d = np.frombuffer(open('Front.swatchbin', 'rb').read()[0x53:], np.uint8)
W = H = 1024; bw_, bh_ = W // 4, H // 4
nb = bw_ * bh_
blocks = d[:nb * 8].reshape(nb, 8)
# cheap per-block value: the two endpoints' mean (enough to judge coherence)
from bc import bc4_decode_blocks
val = bc4_decode_blocks(blocks).reshape(nb, 16).astype(float).mean(1)
res = []
for cfg in ['P2', 'P4_8x16', 'P4_16x16', 'P8_16x16_8x16', 'P8_16x32_8x16', 'P8_32x32_8x16', 'P8_16x32_16x16', 'P8_32x32_16x16']:
    for banks, bw, bh, mar in itertools.product([2, 4, 8, 16], [1, 2, 4], [1, 2, 4], [1, 2, 4]):
        try: off = offsets(bw_, bh_, 64, cfg, banks, bw, bh, mar)
        except Exception as e: continue
        i = off // 8
        if i.max() >= nb or len(np.unique(i)) != nb: continue
        img = val[i]
        score = np.abs(np.diff(img, axis=0)).mean() + np.abs(np.diff(img, axis=1)).mean()
        res.append((score, cfg, banks, bw, bh, mar))
res.sort()
for r in res[:12]: print(r)
lin = val.reshape(bh_, bw_); print('linear score', np.abs(np.diff(lin, axis=0)).mean() + np.abs(np.diff(lin, axis=1)).mean(), 'candidates', len(res))
