"""Regressions for the shared-wheel fallback and lost rim depth found in this batch."""
import unittest,sys,tempfile,subprocess,zipfile,struct
import numpy as np
import trimesh
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'fh2re')]
from wheelfit import load_spec
from wheelcheck import check
from rimbuild import build_source_rim
from geometry import Part
from body_swap import material_names
from gltf_bridge import decode_group
from carpreview import morph_rim
sys.path.insert(0,str(ROOT/'f1'))

class SourceWheelTests(unittest.TestCase):
 def test_unmodified_donor_is_rejected(self):
  s=load_spec(ROOT/'cars/modely2025/spec.py')
  with self.assertRaisesRegex(ValueError,'unmodified Charger'):check(s,s.DONOR_ZIP)
 def test_missing_wheels_block_packaging_before_output(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'spec.py';p.write_text('import runpy\nglobals().update(runpy.run_path('+repr(str(ROOT/'cars/modely2025/spec.py'))+'))\nRIM_MATERIALS=[]\n')
   result=subprocess.run([sys.executable,str(ROOT/'package_car.py'),str(p),str(Path(td)/'out')],capture_output=True,text=True,cwd=ROOT)
   self.assertNotEqual(result.returncode,0);self.assertIn('not an automatic fallback',result.stderr);self.assertFalse((Path(td)/'out').exists())
 def test_built_source_geometry_keeps_nominal_size_and_axial_depth(self):
  s=load_spec(ROOT/'cars/daily09/spec.py');p=ROOT/'cars/daily09/build'/(s.MEDIA+'.zip')
  self.assertTrue(check(s,p)['all_donor_face_lods_removed'])
 def test_builder_preserves_physical_depth_at_nondefault_diameter(self):
  s=load_spec(ROOT/'cars/modely2025/spec.py')
  with zipfile.ZipFile(s.DONOR_ZIP) as z:
   raw=z.read(next(n for n in z.namelist() if n.lower().endswith('_wheellf.modelbin')))
  mesh=trimesh.creation.annulus(r_min=.18,r_max=.24,height=.10,sections=12)
  transform=np.array([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1]],float);mesh.apply_transform(transform)
  V=mesh.vertices[mesh.faces].reshape(-1,3);N=mesh.vertex_normals[mesh.faces].reshape(-1,3)
  uv=V[:,1:]/.5+.5;parts={'test':[dict(V=V,N=N,UV=uv)]}
  out,_=build_source_rim(raw,parts,['test'],np.zeros(3),.2286,'Game:\\test\\face.swatchbin','Game:\\test\\gloss.swatchbin',(ROOT/'f1/matI_lod1.bin').read_bytes())
  p=Part(out);names=material_names(p);r=next(r for r in p.render if names[id(r['blob'])]=='source_rim' and struct.unpack_from('<H',r['blob']['data'],4)[0]==3)
  d,_=decode_group(p,0);v=morph_rim(d['POSITION'][:,:3].astype(float),p.groups[0]['morph'],.2286,.225)[np.unique(r['indices'])]
  self.assertAlmostEqual(float(np.ptp(v[:,0])),.10,places=4)
  self.assertAlmostEqual(float(np.hypot(v[:,1],v[:,2]).max()),.24,places=3)
  barrel=next(r for r in p.render if names[id(r['blob'])]=='inner_rim' and struct.unpack_from('<H',r['blob']['data'],4)[0]==3)
  q=d['POSITION'][:,:3][np.array(barrel['indices']).reshape(-1,3)]
  normals=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
  self.assertEqual(len(q),128)
  self.assertTrue(np.all(np.linalg.norm(normals,axis=1)>1e-10))
  self.assertTrue(np.all(np.abs(normals[:,0])<1e-7),'Barrel must have open ends so it cannot hide spokes')

if __name__=='__main__':unittest.main()
