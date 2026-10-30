"""Donor car media renamed for the new car: DOD_ChargerSRT8_12 -> STR_ToroRosso_1_06 (same length, so every embedded path
can be renamed in place). Texture references (crc32 of the lower-case path) are recomputed for renamed paths."""
import sys, zipfile, re, struct, zlib
sys.path.insert(0, '../fh2re'); sys.path.insert(0, '.')
from modelbin import Bundle
import fhmat
OLD, NEW = 'DOD_ChargerSRT8_12', (sys.argv[3] if len(sys.argv) > 3 else 'STR_ToroRosso_1_06')
VARIANTS = [(OLD, NEW), (OLD.lower(), NEW.lower()), (OLD.upper(), NEW.upper())]
def ren_bytes(d):
    for a, b in VARIANTS: d = d.replace(a.encode(), b.encode())
    return d
def ren_name(n):
    return re.sub(re.escape(OLD), NEW, n, flags=re.I)
def fix_model(raw):
    """every renamed texture path in a MatI is followed by crc32(lower path): recompute it (and the Modl TRef list)"""
    b = Bundle.read(raw); remap = {}
    for bl in b.blobs:
        if bl['tag'] != 'MatI' or not len(bl['data']): continue        # (ErrorShader instances are empty)
        d = bytearray(bl['data']); hit = False
        for m in re.finditer(rb'[Gg]ame:\\[ -~]+?\.swatchbin', bytes(d)):
            p = m.group().decode('latin1')
            if NEW.lower() not in p.lower(): continue
            old = re.sub(re.escape(NEW), OLD, p, flags=re.I)
            oc, nc = fhmat.crc(old), fhmat.crc(p)
            assert struct.unpack_from('<I', d, m.end())[0] == oc, (p, 'crc not where expected')
            struct.pack_into('<I', d, m.end(), nc); remap[oc] = nc; hit = True
        if hit: bl['data'] = d
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
