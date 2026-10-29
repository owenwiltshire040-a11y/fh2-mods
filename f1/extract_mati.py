"""matI_lod1.bin: the game's textured 'interior_lod1' material instance (DIFF + GLOS), the template build_str1.py
retextures for every STR1 material. Taken from the built 207's seat belt part (its copy is named 'interior_lod1|seatL_a').
usage: extract_mati.py PEU_207_5door_v14.zip"""
import sys, zipfile
sys.path.insert(0, '../fh2re')
from modelbin import Bundle
b = Bundle.read(zipfile.ZipFile(sys.argv[1]).read('scene/interior/Seats/seatBeltL_a.modelbin'))
bl = next(x for x in b.blobs if x['tag'] == 'MatI' and b.meta(x, 'Name').decode() == 'interior_lod1|seatL_a')
open('matI_lod1.bin', 'wb').write(bytes(bl['data'])); print('wrote matI_lod1.bin', len(bl['data']), 'bytes')
