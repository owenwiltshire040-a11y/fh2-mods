"""Put the STR1 model's own rims into an already built STR1 car zip (the 208's rimbuild route).

python3 f1/str1_rims.py str1_geo.pkl in_car.zip out_car.zip
The model's rims are anthracite (MCLRIM lip, MCLSPOKES_OP spokes) with an MCLHUB centre: spokes + lip go to the
wheel part's 'black' material, the hub to 'rim'. Motion-blur copies (*_BLUR) and the see-through MCLSPOKES duplicate
are left out. The game sizes the rim to the DB's 13" and draws the tyre itself.
"""
import sys, os, pickle, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'fh2re'))
import rimbuild

SILVER = ['MCLHUB']
BLACK = ['MCLRIM', 'MCLSPOKES_OP']

geo = pickle.load(open(sys.argv[1], 'rb'))
hub = geo['parts']['HUB_LF']; centre = geo['wheels']['HUB_LF']['centre']
parts = {}
for p in hub: parts.setdefault(p['mat'], []).append(p)
src = zipfile.ZipFile(sys.argv[2])
wheel = [n for n in src.namelist() if n.lower().endswith('wheellf.modelbin')]
assert len(wheel) == 1, wheel
new, _ = rimbuild.build_rim(src.read(wheel[0]), parts, SILVER, centre, black_materials=BLACK)
with zipfile.ZipFile(sys.argv[3], 'w', zipfile.ZIP_DEFLATED) as out:
    for i in src.infolist():
        out.writestr(i, new if i.filename == wheel[0] else src.read(i.filename))
print('replaced', wheel[0])
