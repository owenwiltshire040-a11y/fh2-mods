"""FH2 UI swatchbins: car thumbnails (Thumbnail_<car>_Big/_Small) and make logos (Manu_Logo_<CODE>, L_Manu_Logo_<CODE>).

Worked out 30 Oct 2026 from a working add-on car's media/stripped/RC0 files (structure only):
  * 84-byte header (car textures use 83): 'burG' bundle + 'BCXT' + 'HCXT' blocks, a 16-byte GUID at 0x30,
    width/height/depth u16 at 0x40 and again at 0x46, mip count 1, format 0x2e (BC7) at 0x4f.
  * u32 @0x08 = 0x54 (header length), u32 @0x0c = 0x54 + data size, u32 @0x20 and @0x24 = data size.
  * Data: ONE BC7 level, GCN 2D-tiled exactly like car textures (tex/swatch.py tile_index '2d'),
    padded with zeros to a multiple of 4096 bytes. Any width/height (816x459, 440x376...).
  * Sizes seen: thumbnails 816x459 (Big) and 192x108 (Small); logos 220x184 (Manu_Logo) and 440x376 (L_Manu_Logo).
    Transparent background (alpha) around the car / logo.
Usage: python3 uiswatch.py decode in.swatchbin out.png | encode in.png out.swatchbin [WxH]
"""
import struct, sys, uuid, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swatch

HDR = 0x54
SIZES = {'big': (816, 459), 'small': (192, 108), 'logo': (220, 184), 'logo_large': (440, 376)}


def _header(w, h, size):
    b = bytearray(HDR)
    b[0:8] = b'burG\x01\x00\x01\x00'
    struct.pack_into('<II', b, 0x08, HDR, HDR + size)
    b[0x10:0x18] = b'BCXT\x02\x00\x01\x00'
    struct.pack_into('<II', b, 0x18, 0x28, HDR)
    struct.pack_into('<II', b, 0x20, size, size)
    b[0x28:0x30] = b'HCXT\x30\x02\x08\x00'
    b[0x30:0x40] = uuid.uuid4().bytes_le
    struct.pack_into('<HHHHHH', b, 0x40, w, h, 1, w, h, 1)
    b[0x4c:0x54] = bytes([0x01, 0x01, 0x00, 0x2e, 0x01, 0x00, 0xb8, 0x00])
    return bytes(b)


def info(d):
    w, h = struct.unpack_from('<HH', d, 0x40)
    return dict(header=struct.unpack_from('<I', d, 8)[0], w=w, h=h, fmt=d[0x4f], mips=d[0x4c])


def decode(d):
    i = info(d)
    assert i['header'] == HDR and i['fmt'] == 0x2e, i
    w, h = i['w'], i['h']
    return swatch.decode_level(d, HDR, -(-w // 4) * 4, -(-h // 4) * 4, '2d')[:h, :w]


def encode(rgba):
    """rgba (h, w, 4) uint8, any size -> UI swatchbin bytes"""
    h, w = rgba.shape[:2]
    ph, pw = -(-h // 4) * 4, -(-w // 4) * 4
    if (ph, pw) != (h, w):
        rgba = np.pad(rgba, ((0, ph - h), (0, pw - w), (0, 0)), mode='edge')
    data = swatch.encode_level(np.ascontiguousarray(rgba), '2d')
    size = -(-len(data) // 4096) * 4096
    data = data + bytes(size - len(data))
    return _header(w, h, size) + data


if __name__ == '__main__':
    from PIL import Image
    cmd, src, dst = sys.argv[1:4]
    if cmd == 'decode':
        Image.fromarray(decode(open(src, 'rb').read())).save(dst)
    else:
        im = Image.open(src).convert('RGBA')
        if len(sys.argv) > 4:
            w, h = SIZES.get(sys.argv[4]) or map(int, sys.argv[4].split('x'))
            im = im.resize((w, h), Image.LANCZOS)
        open(dst, 'wb').write(encode(np.array(im)))
