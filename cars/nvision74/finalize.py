"""Retain repeated atlas detail in packed UVs and set the concept's silver paint."""
from pathlib import Path
import pickle,numpy as np
p=Path(__file__).resolve().parent;g=pickle.loads((p/'geo.pkl').read_bytes())
for fragments in g['parts'].values():
 for f in fragments:
  u=f['UV'].reshape(-1,3,2);u-=np.floor(u.mean(1))[:,None,:];f['UV']=u.reshape(-1,2)
(p/'geo.pkl').write_bytes(pickle.dumps(g))
pf=p/'electric_db.py';s=pf.read_text();marker=' # Concept silver default; keep alternate colours available.'
if marker not in s:
 s=s.replace(' c.row_factory=None',marker+"\n c.execute('UPDATE Combo_Colors SET RGB=?,Metallic=1 WHERE Ordinal=? AND Sequence=1',(int('bfc2c6',16),car))\n c.row_factory=None")
pf.write_text(s)
print('Packed atlas UVs normalised; silver paint configured')

sp=p/'spec.py';text=sp.read_text()
if "# Fixed satin silver source finish" not in text:
 text+="\n# Fixed satin silver source finish; body recolouring is not yet supported.\nTEXTURES['silver_finish']=(Image.new('RGB',(64,64),(185,189,194)),512,False)\nMATERIALS['Paint']=('textured','silver_finish')\nARCH_MATERIALS=['Paint']\n"
sp.write_text(text)
