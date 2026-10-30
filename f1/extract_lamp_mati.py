"""Lamp material instances that light by day, taken from Owen's built 207 (its Fiesta-derived tail lamp):
f1/lamp_brake.bin (LBK_smoothChrome_custom_brake, mask 0x45 = tail + brake), f1/lamp_reverse.bin (mask 0x1),
f1/lamp_turn.bin (mask 0x15, amber). The mask (param 0x493073a0) must match the low bits of the Lights.bin flags of
the light that drives it; the Charger's own tail LED material has mask 0x20, which no Charger light carries, so it
never brightens by day.   usage: python3 f1/extract_lamp_mati.py PEU_207SEHDi_08.zip
"""
import sys, os, zipfile, struct
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'fh2re'))
from geometry import Part
from body_swap import material_names
z = zipfile.ZipFile(sys.argv[1]); n = next(x for x in z.namelist() if x.lower().endswith('taillightl_a.modelbin'))
p = Part(z.read(n))
WANT = {'LBK_smoothChrome_custom_brake': 'brake', 'LBK_standardCH1_003_custom_reverse': 'reverse', 'LBK_standardCH1_003_custom_turn': 'turn',
        'gls_patternCH1_009_custom_red': 'redlens'}   # red lamp glass (no light mask): the tail lamps' outer layer
open(os.path.join(HERE, 'lamp_tail_part.modelbin'), 'wb').write(z.read(n)); print('wrote lamp_tail_part.modelbin (the 207 tail-lamp part, both sides)')
for bl in p.b.blobs:
    if bl['tag'] != 'MatI': continue
    name = p.b.meta(bl, 'Name').decode('latin1')
    if name in WANT:
        open(os.path.join(HERE, f'lamp_{WANT[name]}.bin'), 'wb').write(bytes(bl['data'])); print('wrote', f'lamp_{WANT[name]}.bin', name)
