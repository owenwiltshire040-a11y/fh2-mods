"""AMD GCN (Xbox One) 2D macro-tiled surface addressing, after AMD's addrlib (SI/CI), vectorised.
Elements are pixels, or 4x4 blocks for BC formats. Returns the byte offset of every element (x, y)."""
import numpy as np

MICRO = {   # element index bits within an 8x8 micro tile (non-displayable / thin), by element size in bits
    8:   ['x0', 'x1', 'x2', 'y1', 'y0', 'y2'],
    16:  ['x0', 'x1', 'x2', 'y0', 'y1', 'y2'],
    32:  ['x0', 'x1', 'y0', 'x2', 'y1', 'y2'],
    64:  ['x0', 'y0', 'x1', 'y1', 'x2', 'y2'],     # found by search on a BC4 livery mask (Xbox One)
    128: ['y0', 'x0', 'x1', 'x2', 'y1', 'y2'],
}

def bit(v, n): return (v >> n) & 1

def pipe_of(x, y, cfg):
    if cfg == 'P2': return bit(x, 3) ^ bit(y, 3)
    if cfg == 'P4_8x16': return (bit(x, 4) ^ bit(y, 3)) | ((bit(x, 3) ^ bit(y, 4)) << 1)
    if cfg == 'P4_16x16': return (bit(x, 3) ^ bit(y, 3) ^ bit(x, 4)) | ((bit(x, 4) ^ bit(y, 4)) << 1)
    if cfg == 'P8_16x16_8x16': return (bit(x, 4) ^ bit(y, 3)) | ((bit(x, 3) ^ bit(y, 4)) << 1) | ((bit(x, 5) ^ bit(y, 5)) << 2)
    if cfg == 'P8_16x32_8x16': return (bit(x, 4) ^ bit(y, 3)) | ((bit(x, 3) ^ bit(y, 4)) << 1) | ((bit(x, 5) ^ bit(y, 6)) << 2)
    if cfg == 'P8_32x32_8x16': return (bit(x, 4) ^ bit(y, 3) ^ bit(x, 5)) | ((bit(x, 3) ^ bit(y, 4)) << 1) | ((bit(x, 5) ^ bit(y, 5)) << 2)
    if cfg == 'P8_16x32_16x16': return (bit(x, 3) ^ bit(y, 3) ^ bit(x, 4)) | ((bit(x, 4) ^ bit(y, 4)) << 1) | ((bit(x, 5) ^ bit(y, 6)) << 2)
    if cfg == 'P8_32x32_16x16': return (bit(x, 3) ^ bit(y, 3) ^ bit(x, 4)) | ((bit(x, 4) ^ bit(y, 4)) << 1) | ((bit(x, 5) ^ bit(y, 5)) << 2)
    if cfg == 'P8_32x64_32x32': return (bit(x, 3) ^ bit(y, 3) ^ bit(x, 5)) | ((bit(x, 4) ^ bit(y, 4) ^ bit(x, 5)) << 1) | ((bit(x, 5) ^ bit(y, 5)) << 2) # approx
    raise ValueError(cfg)

NPIPES = lambda cfg: int(cfg[1])

def bank_of(x, y, banks, bw, bh, pipes, mar):
    tx = x // (8 * bw * pipes); ty = y // (8 * bh)
    x3, x4, x5, x6 = (bit(tx, i) for i in range(4)); y3, y4, y5, y6 = (bit(ty, i) for i in range(4))
    if banks == 16: return (x3 ^ y6) | ((x4 ^ y5 ^ y6) << 1) | ((x5 ^ y4) << 2) | ((x6 ^ y3) << 3)
    if banks == 8: return (x3 ^ y5) | ((x4 ^ y4 ^ y5) << 1) | ((x5 ^ y3) << 2)
    if banks == 4: return (x3 ^ y4) | ((x4 ^ y3) << 1)
    if banks == 2: return x3 ^ y3
    raise ValueError(banks)

def offsets(w, h, bpp, cfg, banks, bw, bh, mar, pitch=None):
    """byte offset of each element; arrays (h, w)"""
    pipes = NPIPES(cfg)
    y, x = np.mgrid[0:h, 0:w]
    eb = bpp // 8
    # micro tile element index
    idx = np.zeros_like(x)
    for i, b in enumerate(MICRO[bpp]):
        v = x if b[0] == 'x' else y
        idx |= bit(v, int(b[1])) << i
    elem = idx * eb
    micro_bytes = 64 * eb
    mtp = 8 * bw * pipes * mar                  # macro tile pitch (elements)
    mth = 8 * bh * banks // mar                 # macro tile height
    pitch = pitch or max(w, mtp); pitch = -(-pitch // mtp) * mtp
    macro_bytes = (mtp // 8) * (mth // 8) * micro_bytes // (pipes * banks)
    mtx = x // mtp; mty = y // mth
    macro_off = (mty * (pitch // mtp) + mtx) * macro_bytes
    tile_row = (y // 8) % bh
    tile_col = ((x // 8) // pipes) % bw
    tile_off = (tile_row * bw + tile_col) * micro_bytes
    total = macro_off + tile_off + elem
    pipe = pipe_of(x, y, cfg)
    bank = bank_of(x, y, banks, bw, bh, pipes, mar)
    pb, bb = pipes.bit_length() - 1, banks.bit_length() - 1
    return (total & 255) | (pipe << 8) | (bank << (8 + pb)) | ((total >> 8) << (8 + pb + bb))
