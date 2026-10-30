"""The STR1's rain light as a working tail/brake lamp, added to an already built STR1 car zip.

python3 f1/str1_lights.py str1_geo.pkl in_car.zip charger_donor.zip out_car.zip
The STR1 build keeps no donor light parts. This puts the model's REAR_LIGHT panel (9 x 12 cm, x 0, y 0.31-0.42,
z -2.088) into the 207's day-working tail-lamp part (f1/lamp_tail_part.modelbin, see fh2re/lightbuild.py) as
taillightl_a, adds that part back to the carbin (the Charger's entry), and writes a Lights.bin with just two lights on
it: the Charger's tail light (type 7, flags 0x20045) and a pure brake light (type 7, flags 0x45), both at the panel.
"""
import sys, os, copy, pickle, zipfile, struct
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'fh2re'), HERE]
import lightbuild
from carbin import read_carbin, write_carbin

geo, src_zip, donor_zip, out_zip = sys.argv[1:5]
G = pickle.load(open(geo, 'rb'))
V = np.concatenate([p['V'] for p in G['parts']['REAR_LIGHT']]); N = np.concatenate([p['N'] for p in G['parts']['REAR_LIGHT']])
V = V + [0, 0, -0.002]                         # 2 mm proud of the body's own copy of the panel
lamps = {'tail': (V, N)}
centre = (V.min(0) + V.max(0)) / 2 + [0, 0, -0.01]
print('rain light centre', centre.round(3), len(V) // 3, 'tris')

src = zipfile.ZipFile(src_zip); names = {n.lower(): n for n in src.namelist()}
media = next(n for n in src.namelist() if n.endswith('.carbin')).split('/')[-1][:-7]
tl_key = next(n for n in names if n.endswith('/taillightl_a.modelbin'))
part = lightbuild.build_tail_from_207(open(os.path.join(HERE, 'lamp_tail_part.modelbin'), 'rb').read(), lamps)

# carbin: the Charger's taillightl_a entry, renamed to this media
dz = zipfile.ZipFile(donor_zip); dcarb = read_carbin(dz.read(next(n for n in dz.namelist() if n.endswith('.carbin'))))
cname = next(n for n in src.namelist() if n.endswith('.carbin')); carb = read_carbin(src.read(cname))
donor_media = next(n for n in dz.namelist() if n.endswith('.carbin')).split('/')[-1][:-7]
entry = None
for pt in dcarb['parts']:
    for m in pt['part']['models']:
        if m['path'].lower().endswith('taillightl_a.modelbin'):
            entry = copy.deepcopy(pt); entry['part']['models'] = [dict(m, path=m['path'].replace(donor_media, media).replace(donor_media.lower(), media.lower()))]
assert entry, 'no taillightl_a in the donor carbin'
if not any(m['path'].lower().endswith('taillightl_a.modelbin') for pt in carb['parts'] for m in pt['part']['models']):
    carb['parts'].append(entry); print('carbin: + taillightl_a', entry['part']['models'][0]['path'])

# Lights.bin: one part, two lights
d = dz.read('Lights.bin'); o = 8; n = struct.unpack_from('<I', d, o)[0]; o += 4
for _ in range(n): L = struct.unpack_from('<I', d, o)[0]; o += 6 + L
cnt = struct.unpack_from('<I', d, o)[0]; body = d[o + 4:]
t7 = next(76 * i for i in range(cnt) if struct.unpack_from('<I', body, 76 * i)[0] == 7)
path = f'game:\\media\\cars\\{media.lower()}\\scene\\exterior\\secondarylights\\taillightl_a.modelbin'.encode()
out = bytearray(d[:8]) + struct.pack('<I', 1) + struct.pack('<I', len(path)) + path + struct.pack('<H', 1) + struct.pack('<I', 2)
for flags in (0x20045, 0x45):
    e = bytearray(body[t7:t7 + 76]); struct.pack_into('<Ii', e, 4, flags, 0)
    struct.pack_into('<3f', e, 12, *centre); struct.pack_into('<3f', e, 44, *centre); out += e
out += body[76 * cnt:]

with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zo:
    for i in src.infolist():
        k = i.filename
        data = part if k == tl_key else write_carbin(carb) if k == cname else bytes(out) if k.lower() == 'lights.bin' else src.read(k)
        zo.writestr(i, data)
print('wrote', out_zip)
