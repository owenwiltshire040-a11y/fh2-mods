"""rFactor 1 MAS2 archive reader. Layout (worked out on CTDP's archives): 16-byte scrambled signature, u32 0,
u32 file count, u32 total data size; then per file 256 bytes: u32 flags, name[236], u32 0, u32 size, u32 stored
size, u32 0; then the files' data back to back in table order (zlib when stored size < size)."""
import struct, zlib, sys, os
def read(path):
    d = open(path, 'rb').read()
    n = struct.unpack_from('<I', d, 0x14)[0]
    o = 0x1c; ents = []
    for i in range(n):                 # u32 flags, name[236], u32 0, u32 size, u32 stored size, u32 0
        flags = struct.unpack_from('<I', d, o)[0]; name = d[o + 4:o + 240].split(b'\0')[0].decode('latin1')
        size, stored = struct.unpack_from('<2I', d, o + 244)
        ents.append((name, size, stored, flags)); o += 256
    out = {}
    for name, size, stored, flags in ents:
        raw = d[o:o + stored]; o += stored
        out[name] = zlib.decompress(raw) if stored != size else raw
        assert len(out[name]) == size, (name, len(out[name]), size)
    assert o == len(d), (o, len(d))
    return out
if __name__ == '__main__':
    for p in sys.argv[1:-1]:
        files = read(p); dst = sys.argv[-1]; os.makedirs(dst, exist_ok=True)
        for k, v in files.items(): open(os.path.join(dst, k), 'wb').write(v)
        print(p, len(files), 'files')
