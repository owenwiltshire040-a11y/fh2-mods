from pathlib import Path
import pickle
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;g=pickle.loads((p/'geo.pkl').read_bytes());mat='Hyundai_NVision74Concept_2023_LightA_Diffuse'
a=np.array(Image.open('/Users/owen/Downloads/2023-hyundai-n-vision-74-concept/textures/Hyundai_NVision74Concept_2023_LightA_Diffuse_10.png').convert('RGB'))
for f in g['parts'][mat]:
 c=f['V'].reshape(-1,3,3).mean(1);uv=f['UV'].reshape(-1,3,2).mean(1);xy=np.clip(np.round((uv*[1,-1]+[0,1])*511).astype(int),0,511);rgb=a[xy[:,1],xy[:,0]]
 mask=(c[:,2]<-2)&(c[:,1]>.4)&(rgb.min(1)>120)
 if mask.any():
  out=dict(f,mat='TAIL_EMITTER')
  for key,d in [('V',3),('N',3),('UV',2)]:out[key]=f[key].reshape(-1,3,d)[mask].reshape(-1,d);f[key]=f[key].reshape(-1,3,d)[~mask].reshape(-1,d)
  g['parts'].setdefault('TAIL_EMITTER',[]).append(out)
(p/'geo.pkl').write_bytes(pickle.dumps(g));s=p/'spec.py';s.write_text(s.read_text().replace("'glassf_a.modelbin','steeringwheel_a.modelbin'","'glassf_a.modelbin'").replace("STEERING_MATERIALS=['STEERING_SOURCE']","STEERING_MATERIALS=[]  # Source cockpit wheel retained static; animation pending."))
print('Rear pixel emitters',sum(len(f['V'])//3 for f in g['parts'].get('TAIL_EMITTER',[])))
