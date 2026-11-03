"""Align source axle height to the generic donor spindle envelope after prepare_geometry.py."""
from pathlib import Path
import pickle
p=Path(__file__).resolve().parent;g=pickle.load(open(p/'geo.pkl','rb'));target=.1511658
shift=target-float(g['wheels']['HUB_LF']['centre'][1])
for pp in g['parts'].values():
 for f in pp:f['V'][:,1]+=shift
for w in g['wheels'].values():w['centre'][1]+=shift
g['ground']+=shift;pickle.dump(g,open(p/'geo.pkl','wb'));print('Body/geometry Y shift',round(shift,5),'new axle Y',target)
