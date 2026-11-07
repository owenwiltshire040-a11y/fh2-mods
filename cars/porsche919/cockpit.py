"""Step 9 (Claude 7 Nov, v0.1.5): the driver animations agree with the Porsche skeleton's steering wheel.
The 13 driver gr2s (scene/drivers/default, borrowed from the R26) each hold a constant boneSteeringWheel position
track, (0.0002, -1.5153, 0.2519) = the R26's centre-line wheel, which overrides the skeleton at runtime (the RB22's
0.1.12 fault: wheel drawn where the animation set's car had it). Set to the skeleton's own local position (the
Porsche's wheel sits 0.156 m to the driver's side). Also checks the steering part stays under 65,536 vertices.
  python3 cars/porsche919/cockpit.py PKG_DIR"""
from pathlib import Path
import sys,json,zipfile
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'f1'),str(ROOT/'tex')]
from geometry import Part
import granny
CAR=Path('media/cars/POR_Porsche919_17_.zip')
def apply(pkg):
 arc=pkg/CAR
 with zipfile.ZipFile(arc) as z:infos=z.infolist();E={i.filename:z.read(i) for i in infos}
 sw=next(n for n in E if n.lower().endswith('steeringwheel_a.modelbin'));verts=sum(len(g['positions']) for g in Part(E[sw]).groups.values());assert verts<65536,verts
 sk=next(n for n in E if n.lower().endswith('_skeleton.gr2'))
 target=next(pos for name,par,pos,_ in granny.bones(granny.GR2(E[sk])) if name=='boneSteeringWheel')
 done={}
 for n in [n for n in E if n.lower().startswith('scene/drivers/') and n.lower().endswith('.gr2')]:
  g=granny.GR2(E[n]);before=granny.track_position_constant(g,'boneSteeringWheel')
  r=granny.set_track_position(g,'boneSteeringWheel',list(target),list(target));assert r==['constant'],(n,r)
  E[n]=g.write();after=granny.track_position_constant(granny.GR2(E[n]),'boneSteeringWheel');assert np.allclose(after,target,atol=1e-5),(n,after)
  done[n.split('/')[-1]]=[round(float(x),4) for x in before]
 assert len(done)>=13,len(done)
 tmp=arc.with_suffix('.tmp')
 with zipfile.ZipFile(tmp,'w') as z:
  for i in infos:z.writestr(i,E[i.filename])
 tmp.replace(arc)
 with zipfile.ZipFile(arc) as z:assert z.testzip() is None
 rep=dict(valid=True,steering_vertices=verts,boneSteeringWheel=[round(float(x),4) for x in target],animations=len(done),previous=sorted({tuple(v) for v in done.values()}),runtime_status='Pending cockpit view')
 (pkg/'cockpit-check.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
if __name__=='__main__':apply(Path(sys.argv[1]))
