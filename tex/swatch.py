"""FH2 (Xbox One) swatchbin textures: BC7, GCN 2D macro tiling (P4_16x16, 8 banks, macro aspect 2)."""
import numpy as np, gcn, texture2ddecoder as t2d
gcn.MICRO[128] = ['x0', 'y0', 'x1', 'y1', 'x2', 'y2']
DATA = 0x53
def tile_index(bw, bh, mode):
    """for each block (row-major, bh x bw) the block slot in the stored level"""
    if mode == '2d':
        return gcn.offsets(bw, bh, 128, 'P4_16x16', 8, 1, 1, 2) // 16
    if mode == '1d':    # micro tiles (8x8 blocks) in raster order, pitch padded to 8
        y, x = np.mgrid[0:bh, 0:bw]; p = -(-bw // 8) * 8
        idx = np.zeros_like(x)
        for i, b in enumerate(gcn.MICRO[128]):
            v = x if b[0] == 'x' else y; idx |= ((v >> int(b[1])) & 1) << i
        return ((y // 8) * (p // 8) + x // 8) * 64 + idx
    if mode == 'linear':
        y, x = np.mgrid[0:bh, 0:bw]; return y * bw + x
def decode_level(buf, off, w, h, mode):
    bw, bh = max(1, w // 4), max(1, h // 4)
    i = tile_index(bw, bh, mode)
    n = int(i.max()) + 1
    blk = np.frombuffer(buf[off:off + n * 16], np.uint8)
    if len(blk) < n * 16: return None
    blk = blk.reshape(n, 16)[i.reshape(-1)]
    px = np.frombuffer(t2d.decode_bc7(blk.tobytes(), 4, len(blk) * 4), np.uint8).reshape(bh, bw, 4, 4, 4)
    return px.transpose(0, 2, 1, 3, 4).reshape(bh * 4, bw * 4, 4)[..., [2, 1, 0, 3]]

def encode_level(rgba, mode):
    """rgba (h, w, 4) uint8 -> stored bytes of one level in the given layout"""
    import etcpak
    h, w = rgba.shape[:2]; bw, bh = max(1, w // 4), max(1, h // 4)
    if w < 4 or h < 4:
        rgba = np.pad(rgba, ((0, max(0, 4 - h)), (0, max(0, 4 - w)), (0, 0)), mode='edge'); h, w = rgba.shape[:2]
    raster = np.frombuffer(etcpak.compress_bc7(np.ascontiguousarray(rgba).tobytes(), w, h), np.uint8).reshape(-1, 16)
    i = tile_index(bw, bh, mode).reshape(-1)
    out = np.tile(raster.mean(0).astype(np.uint8)[None], (int(i.max()) + 1, 1)) if False else np.zeros((int(i.max()) + 1, 16), np.uint8)
    out[:] = raster[len(raster) // 2]          # padding slots: a real block from the middle of the image
    out[i] = raster
    return out.tobytes()

# level layout found in the game's own 1024x512 BC7 textures: levels 0-2 2D-tiled, 3-4 1D-tiled, back to back
def write_like(template, rgba):
    """a new swatchbin with the template's header (size, format, GUID) and rgba's pixels, all mip levels"""
    from PIL import Image
    data_size = len(template) - DATA
    h, w = rgba.shape[:2]
    out = bytearray(data_size); off = 0; lvl = 0; img = Image.fromarray(rgba)
    while off < data_size and (w >= 1 or h >= 1):
        a = np.array(img.resize((max(1, w), max(1, h)), Image.LANCZOS if lvl else Image.NEAREST))
        mode = '2d' if (w // 4 >= 64 and h // 4 >= 16) else '1d'
        blob = encode_level(a, mode)
        if off + len(blob) > data_size:      # the tiniest levels: one block of the image's average colour each
            a = np.tile(np.array(img.resize((1, 1), Image.BOX)), (4, 4, 1)); blob = encode_level(a, 'linear')
            while off + 16 <= data_size: out[off:off + 16] = blob[:16]; off += 16
            break
        out[off:off + len(blob)] = blob; off += len(blob); lvl += 1
        if w == 1 and h == 1: break
        w, h = max(1, w // 2), max(1, h // 2)
    while off + 16 <= data_size:              # remaining padding
        out[off:off + 16] = out[off - 16:off]; off += 16
    return bytes(template[:DATA]) + bytes(out)
