import numpy as np
def bc4_block(b):
    e0, e1 = int(b[0]), int(b[1])
    if e0 > e1: pal = [e0, e1] + [((7 - i) * e0 + i * e1) // 7 for i in range(1, 7)]
    else: pal = [e0, e1] + [((5 - i) * e0 + i * e1) // 5 for i in range(1, 5)] + [0, 255]
    bits = int.from_bytes(bytes(b[2:8]), 'little')
    return np.array([pal[(bits >> (3 * i)) & 7] for i in range(16)], np.uint8).reshape(4, 4)
def morton2(n):
    idx = np.arange(n * n); x = np.zeros_like(idx); y = np.zeros_like(idx)
    for b in range(16):
        x |= ((idx >> (2 * b)) & 1) << b; y |= ((idx >> (2 * b + 1)) & 1) << b
    return x, y
def decode_bc4ish(data, w, h, block_bytes, chan_off, order='linear'):
    bw, bh = w // 4, h // 4
    out = np.zeros((h, w), np.uint8)
    if order == 'linear': xs, ys = np.tile(np.arange(bw), bh), np.repeat(np.arange(bh), bw)
    else: xs, ys = morton2(bw)
    for i in range(bw * bh):
        b = data[i * block_bytes + chan_off: i * block_bytes + chan_off + 8]
        out[ys[i] * 4: ys[i] * 4 + 4, xs[i] * 4: xs[i] * 4 + 4] = bc4_block(b)
    return out

def bc4_decode_blocks(blocks):
    """vectorised BC4: blocks (n, 8) uint8 -> (n, 4, 4) uint8"""
    e0 = blocks[:, 0].astype(np.int32); e1 = blocks[:, 1].astype(np.int32)
    i = np.arange(8)
    p7 = np.stack([e0, e1] + [((7 - k) * e0 + k * e1) // 7 for k in range(1, 7)], 1)
    p5 = np.stack([e0, e1] + [((5 - k) * e0 + k * e1) // 5 for k in range(1, 5)] + [np.zeros_like(e0), np.full_like(e0, 255)], 1)
    pal = np.where((e0 > e1)[:, None], p7, p5)
    bits = np.zeros(len(blocks), np.uint64)
    for k in range(6): bits |= blocks[:, 2 + k].astype(np.uint64) << np.uint64(8 * k)
    idx = np.stack([((bits >> np.uint64(3 * j)) & np.uint64(7)).astype(np.int64) for j in range(16)], 1)
    return np.take_along_axis(pal, idx, 1).reshape(-1, 4, 4).astype(np.uint8)
