import os, sys
os.environ.setdefault('PYOPENGL_PLATFORM','egl')
import trimesh, numpy as np, pyrender
from PIL import Image
def look_at(eye, target, up=(0,1,0)):
    eye=np.array(eye,float); f=np.array(target,float)-eye; f/=np.linalg.norm(f)
    r=np.cross(f,up); r/=np.linalg.norm(r); u=np.cross(r,f)
    M=np.eye(4); M[:3,0]=r; M[:3,1]=u; M[:3,2]=-f; M[:3,3]=eye; return M
def render(mesh, views, out, size=600, target=(0,0.6,0)):
    sc=pyrender.Scene(ambient_light=[1,1,1], bg_color=[255,255,255])
    sc.add(pyrender.Mesh.from_trimesh(mesh, smooth=False))
    cam=pyrender.PerspectiveCamera(yfov=0.6)
    r=pyrender.OffscreenRenderer(size,size)
    imgs=[]
    for eye in views:
        n=sc.add(cam, pose=look_at(eye,target)); c,_=r.render(sc, flags=pyrender.RenderFlags.FLAT); sc.remove_node(n); imgs.append(c)
    rows=[np.hstack(imgs[i:i+3]) for i in range(0,len(imgs),3)]
    Image.fromarray(np.vstack(rows)).save(out)
if __name__=='__main__':
    m=trimesh.load(sys.argv[1],process=False)
    d=float(sys.argv[3]) if len(sys.argv)>3 else 6
    views=[(d,2,0),(-d,2,0),(0,2,d),(0,2,-d),(d*.7,3,d*.7),(0,d*1.3,0.01)]
    render(m,views,sys.argv[2])
