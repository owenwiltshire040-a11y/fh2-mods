"""Fit regressions for the actual source assets and previously observed failures."""
import unittest,sys,tempfile,pickle,copy,json,subprocess,io,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'fh2re'))
import wheelfit
from carpreview import morph_rim

class WheelFitTests(unittest.TestCase):
 def spec(self,name):return wheelfit.load_spec(ROOT/'cars'/name/'spec.py')
 def test_confirmed_profiles(self):
  for name in ['modely2025','passatb3']:
   d=wheelfit.report(self.spec(name));self.assertTrue(d['valid'],d['errors'])
 def test_tesla_reference_and_tyre(self):
  S=self.spec('modely2025');g=pickle.loads(Path(S.GEO).read_bytes());d=wheelfit.report(S)
  self.assertAlmostEqual(d['corners']['lf']['radius'],.356)
  self.assertAlmostEqual(d['corners']['lf']['reference'][0]-d['corners']['lf']['tyre_centre'][0],-.1275)
  self.assertAlmostEqual(abs(d['corners']['lf']['reference'][0])-d['arch_lips']['F'],.01,places=3)
 def test_source_four_wheels(self):
  d=wheelfit.inspect_model(ROOT/'cars/modely2025/model.glb');self.assertEqual(d['confidence'],'four_tyre_meshes');q=d['suggestion']
  self.assertAlmostEqual(q['wheelbase'],2.90158,places=3);self.assertAlmostEqual(q['centre_x'],-1.765872,places=4);self.assertAlmostEqual(q['tyre_radius'],.3688,places=3)
 def test_single_rim_not_a_full_fit(self):
  d=wheelfit.inspect_model(ROOT/'cars/passatb3/steel-wheel.glb');self.assertIsNone(d['suggestion'])
 def test_open_wheel_uses_exposed_rims(self):
  S=self.spec('jordanej11');d=wheelfit.report(S);self.assertTrue(d['valid'],d['errors'])
  self.assertAlmostEqual(d['model_wheelbase'],3.12933,places=4)
  for ax,corner in [('F','lf'),('R','lr')]:
   self.assertAlmostEqual(abs(d['corners'][corner]['reference'][0]),d['arch_lips'][ax],places=3)
   self.assertLess(abs(d['corners'][corner]['tyre_centre'][0]-d['corners'][corner]['source_axle'][0]),.03)
 def test_open_wheel_wrong_track_rejected(self):
  S=self.spec('jordanej11');S.PHYSICS['body']['track_front']=1.4
  d=wheelfit.report(S);self.assertFalse(d['valid']);self.assertTrue(any('rim-face reference' in e for e in d['errors']))
 def test_old_oversized_rim_reference_rejected(self):
  S=self.spec('modely2025');S.RIM_R_REF=.254;d=wheelfit.report(S);self.assertFalse(d['valid']);self.assertTrue(any('lip/reference' in e for e in d['errors']))
 def test_old_height_rejected(self):
  S=self.spec('modely2025');g=pickle.loads(Path(S.GEO).read_bytes())
  for w in g['wheels'].values():w['centre'][1]+=.04323
  with tempfile.TemporaryDirectory() as td:
   S.GEO=str(Path(td)/'bad.pkl');Path(S.GEO).write_bytes(pickle.dumps(g));self.assertTrue(any('axle height' in e for e in wheelfit.report(S)['errors']))
 def test_wrong_wheelbase_rejected(self):
  S=self.spec('modely2025');S.PHYSICS['body']['model_wheelbase']+=.10;self.assertFalse(wheelfit.report(S)['valid'])
 def test_mismatched_reference_rejected(self):
  S=self.spec('modely2025');S.TRACK_REFERENCE='legacy';self.assertFalse(wheelfit.report(S)['valid'])
 def test_rim_diameter_morph(self):
  p=np.array([[0.,.1397,0.]]);m=np.zeros((1,4,4),dtype='<f2');m[0,1,1]=1.3247*.1397
  out=morph_rim(p,[m.tobytes()],.254,.255);self.assertAlmostEqual(out[0,1],.254,places=4)
 def test_package_blocks_before_build(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'spec.py';path.write_text('import runpy\nglobals().update(runpy.run_path('+repr(str(ROOT/'cars/modely2025/spec.py'))+'))\nRIM_R_REF=.254\n')
   result=subprocess.run([sys.executable,str(ROOT/'package_car.py'),str(path),str(Path(td)/'out')],cwd=ROOT,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('lip/reference',result.stderr);self.assertFalse((Path(td)/'out').exists())
   self.assertFalse(json.loads((Path(td)/'build/wheel-fit.json').read_text())['valid'])
 def test_built_database_cannot_override_fit(self):
  S=self.spec('modely2025');d=wheelfit.report(S);data=json.loads((ROOT/'output/Tesla Model Y 2025/database.json').read_text())
  self.assertTrue(wheelfit.check_database(S,copy.deepcopy(d),data)['valid'])
  bad=copy.deepcopy(data);bad['tables']['List_UpgradeCarBodyTireWidthFront']['insert'][0]['FrontTireWidth']=195
  result=wheelfit.check_database(S,copy.deepcopy(d),bad);self.assertFalse(result['valid']);self.assertTrue(any('Stock upgrade' in e for e in result['errors']))
 def test_upload_analysis_endpoint(self):
  loc=importlib.util.spec_from_file_location('studio',ROOT/'tools/car-studio/studio.py');studio=importlib.util.module_from_spec(loc);loc.loader.exec_module(studio)
  captured=[];studio.response=lambda h,d,*a,**k:captured.append(d)
  import shutil
  with tempfile.TemporaryDirectory() as td:
   studio.WORK=Path(td);(studio.WORK/'demo').mkdir();shutil.copy2(ROOT/'cars/modely2025/model.glb',studio.WORK/'demo/model.glb')
   h=studio.Handler.__new__(studio.Handler);payload=json.dumps({'project':'demo'}).encode();h.path='/api/analyze';h.headers={'Content-Length':str(len(payload))};h.rfile=io.BytesIO(payload);h.do_POST()
   self.assertEqual(captured[0]['wheel_measurements']['confidence'],'four_tyre_meshes')

if __name__=='__main__':unittest.main()
