"""Donor car media renamed for the new car: ARI_Atom_13 -> STR_STR1_06 (same length, so every embedded path
can be renamed in place). Texture references (crc32 of the lower-case path) are recomputed for renamed paths."""
import sys, zipfile, re, struct, zlib
sys.path.insert(0, '../fh2re'); sys.path.insert(0, '.')
from modelbin import Bundle
import fhmat
OLD, NEW = 'ARI_Atom_13', 'STR_STR1_06'
VARIANTS = [(OLD, NEW), (OLD.lower(), NEW.lower()), (OLD.upper(), NEW.upper())]
def ren_bytes(d):
    for a, b in VARIANTS: d = d.replace(a.encode(), b.encode())
    return d
def ren_name(n):
    return re.sub(re.escape(OLD), NEW, n, flags=re.I)
def fix_model(raw):
    b = Bundle.read(raw); remap = {}
    for bl in b.blobs:
        if bl['tag'] != 'MatI': continue
        inner = Bundle.read(bytes(bl['data']))
        mt = [x for x in inner.blobs if x['tag'] == 'MTPR']
        if not mt: continue
        paths = [p.decode('latin1') for p in re.findall(rb'[Gg]ame:\\[ -~]+?\.swatchbin', bytes(mt[0]['data']))]
        if not any(NEW.lower() in p.lower() for p in paths): continue
        for p in paths:
            remap[zlib.crc32(re.sub(re.escape(NEW), OLD, p, flags=re.I).lower().encode())] = fhmat.crc(p)
        bl['data'] = bytearray(fhmat.retexture(bl['data'], paths))
    if remap:
        for bl in b.blobs:
            if bl['tag'] == 'Modl':
                for mt in bl['meta']:
                    if mt['tag'] == 'TRef':
                        n = struct.unpack_from('<I', mt['data'], 0)[0]; hs = struct.unpack_from(f'<{n}I', mt['data'], 4)
                        mt['data'] = struct.pack(f'<I{n}I', n, *[remap.get(h, h) for h in hs])
    return b.write()
if __name__ == '__main__':
    src = zipfile.ZipFile(sys.argv[1]); out = zipfile.ZipFile(sys.argv[2], 'w', zipfile.ZIP_DEFLATED)
    for i in src.infolist():
        d = ren_bytes(src.read(i))
        if i.filename.lower().endswith('.modelbin'): d = fix_model(d)
        out.writestr(zipfile.ZipInfo(ren_name(i.filename), date_time=i.date_time), d, compress_type=zipfile.ZIP_DEFLATED)
    out.close(); print('wrote', sys.argv[2])
