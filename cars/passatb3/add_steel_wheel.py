"""Merge the supplied steel rim into the car geometry; run after regenerating geo.pkl."""
from pathlib import Path
import pickle,shutil
import numpy as np,trimesh
here=Path(__file__).resolve().parent
src=here/'steel-wheel.glb'
G=pickle.load(open(here/'geo.pkl','rb'));s=trimesh.load(src,force='scene');parts=[];centre=G['wheels']['HUB_LF']['centre']
for node in s.graph.nodes_geometry:
 t,g=s.graph[node];m=s.geometry[g]
 if not isinstance(m,trimesh.Trimesh):continue
 v=trimesh.transform_points(m.vertices,t);n=m.vertex_normals@t[:3,:3].T;n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-9)
 # Model face points +X; FH2 left wheel face points -X.
 v=v*np.array([-1,1,1])+centre;n=n*np.array([-1,1,1]);f=m.faces[:,::-1]
 parts.append(dict(node=node,mat='PASSAT_STEEL_RIM',V=v[f].reshape(-1,3),N=n[f].reshape(-1,3),UV=np.zeros((len(f)*3,2))))
G['parts']['PASSAT_STEEL_RIM']=parts;G['materials']=sorted(G['parts']);pickle.dump(G,open(here/'geo.pkl','wb'))
print('Added',sum(len(p['V'])//3 for p in parts),'steel-wheel triangles')
