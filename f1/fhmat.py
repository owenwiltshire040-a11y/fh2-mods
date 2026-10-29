"""Add new material instances (textured) and render meshes to an FH2 modelbin Part.

Material instance (MatI) data is itself a Grub bundle: MATI blob (base material path) + MTPR blob (parameter
overrides). A texture override is: u16 2, u32 param hash, u8 6, LEB128 length, path, u32 crc32(lower(path)).
The model's Modl blob counts its meshes (u16 @0), buffers (u16 @2), layouts (u16 @4) and materials (u16 @6)
and lists every texture it uses in its TRef meta as crc32(lower(path)).
"""
import copy, struct, zlib, uuid
from modelbin import Bundle

def crc(path): return zlib.crc32(path.lower().encode('latin1'))

def leb(n):
    out = bytearray()
    while True:
        b = n & 0x7f; n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n: return bytes(out)

def retexture(template_data, paths):
    """copy of a MatI data blob whose texture overrides point at `paths` (same order as in the template)"""
    inner = Bundle.read(bytes(template_data))
    mt = next(b for b in inner.blobs if b['tag'] == 'MTPR'); d = bytes(mt['data'])
    out = bytearray(); o = 0; k = 0
    n = d[0]; out += d[:1]; o = 1
    for _ in range(n):
        head = d[o:o + 7]; typ = d[o + 6]; o += 7; out += head
        if typ == 6:                                   # texture: LEB128 length, path, crc
            ln = 0; sh = 0
            while True:
                b = d[o]; o += 1; ln |= (b & 0x7f) << sh; sh += 7
                if not b & 0x80: break
            o += ln + 4
            p = paths[k].encode('latin1'); k += 1
            out += leb(len(p)) + p + struct.pack('<I', crc(paths[k - 1]))
        elif typ == 1: out += d[o:o + 16]; o += 16     # vec4
        elif typ in (2, 3, 4, 5): out += d[o:o + 4]; o += 4
        else: raise ValueError(f'param type {typ}')
    out += d[o:]
    assert k == len(paths), (k, len(paths))
    mt['data'] = bytearray(out)
    return inner.write()

def modl(part): return next(b for b in part.b.blobs if b['tag'] == 'Modl')

def add_material(part, name, data, textures=()):
    """append a MatI blob; returns its id. textures: paths to add to the model's texture list"""
    b = part.b
    mats = [bl for bl in b.blobs if bl['tag'] == 'MatI']
    new_id = max(struct.unpack('<i', b.meta(bl, 'Id  '))[0] for bl in mats) + 1
    nb = copy.deepcopy(mats[-1])
    nb['data'] = bytearray(data)
    for m in nb['meta']:
        if m['tag'] == 'Name': m['data'] = name.encode('latin1')
        if m['tag'] == 'Id  ': m['data'] = struct.pack('<i', new_id)
    b.blobs.insert(b.blobs.index(mats[-1]) + 1, nb)
    M = modl(part); d = bytearray(M['data']); struct.pack_into('<H', d, 6, struct.unpack_from('<H', d, 6)[0] + 1); M['data'] = d
    for mt in M['meta']:
        if mt['tag'] == 'TRef':
            n = struct.unpack_from('<I', mt['data'], 0)[0]; hs = list(struct.unpack_from(f'<{n}I', mt['data'], 4))
            for t in textures:
                if crc(t) not in hs: hs.append(crc(t))
            mt['data'] = struct.pack(f'<I{len(hs)}I', len(hs), *hs)
    return new_id

def add_mesh(part, like, mat_id):
    """a new render mesh cloned from render entry `like` (same group, LOD flags, bone), drawing material mat_id"""
    b = part.b
    nb = copy.deepcopy(like['blob'])
    struct.pack_into('<h', nb['data'], 0, mat_id)
    last_mesh = max(i for i, bl in enumerate(b.blobs) if bl['tag'] == 'Mesh')
    b.blobs.insert(last_mesh + 1, nb)                 # after every existing mesh, outside the shadow meshes' runs
    r = {'blob': nb, 'group': like['group'], 'start': 1 << 30, 'indices': list(like['indices'][:3])}
    part.render.append(r)
    part.meshes.append(nb)
    M = modl(part); d = bytearray(M['data']); struct.pack_into('<H', d, 0, struct.unpack_from('<H', d, 0)[0] + 1); M['data'] = d
    return r
