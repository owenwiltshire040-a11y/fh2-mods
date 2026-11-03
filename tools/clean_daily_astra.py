"""Select the assembled Astra parts, retaining a record of every dropped source fragment."""
from pathlib import Path
import pickle,json,re,ast,numpy as np
p=Path(__file__).resolve().parents[1]/'cars/daily07';g=pickle.load(open(p/'geo.pkl','rb'));sel=json.load(open(p/'selection.json'));s=sel['scale'];shift=np.array([0,.151-(-.095)*s,.0867-(.407+.103)/2*s]);drop=[];out={}
windows={'Object_737','Object_734','Object_731','Object_91','Object_73','Object_429'}
for mat,ps in g['parts'].items():
 if mat=='FIT_ARCH':continue
 for f in ps:
  source=(f['V']-shift)/s;lo=source.min(0);hi=source.max(0);c=(lo+hi)/2
  keep=hi[1]<.035
  if f['node'] in ['Object_141','Object_139','Object_137','Object_135','Object_133','Object_131','Object_129','Object_127','Object_144','Object_151']:keep=False
  if c[2]>.44 and hi[0]-lo[0]<.10 and (c[1]>-.051 or c[1]<-.095):keep=False
  if not keep:drop.append(f['node']);continue
  key='ASTRA_WINDOWS' if f['node'] in windows else mat;f=dict(f,mat=key);out.setdefault(key,[]).append(f)
g['parts']=out;g['materials']=sorted(out);pickle.dump(g,open(p/'geo.pkl','wb'))
text=(p/'spec.py').read_text();text+="\nMATERIALS['ASTRA_WINDOWS']=('plain','glass')\n"
# These supplied images are normal maps, not diffuse colour maps.
for mat in ['956_2','956_4','956_16','956_22','956_23']:text+=f"MATERIALS[{mat!r}]=('plain','black')\n"
text+="MATERIALS['956_7']=('plain','paint')\nMATERIALS['956_1']=('plain','paint')\nARCH_MATERIALS=['956_0','956_1','956_7']\n"
(p/'spec.py').write_text(text);(p/'astra-selection-review.json').write_text(json.dumps(dict(dropped=drop,windows=sorted(windows)),indent=2));print('Astra detached fragments removed',len(drop))
