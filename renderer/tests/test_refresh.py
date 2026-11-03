import importlib.util,json,re,struct,tempfile,unittest,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('refresh',R/'refresh.py');app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
def c_string(source,name):
 block=source.split('char '+name+'[]=')[1].split(';')[0] if 'char '+name+'[]=' in source else source.split('char '+name+'[] =')[1].split(';')[0]
 return ''.join(json.loads(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"',block))
class RefreshTests(unittest.TestCase):
 def test_revision_namespace_and_guid_are_fresh_and_source_is_untouched(self):
  old='VW_PassatB3_1990_A';new='RV0123456789ABCDEF'
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'old.zip';dst=Path(td)/'new.zip'
   with zipfile.ZipFile(src,'w') as z:
    z.writestr(old+'.carbin',('game:\\media\\cars\\'+old+'\\'+old+'.carbin').encode());z.writestr('Textures/custom/Swatches/test.swatchbin',bytes(0x53+16))
   before=src.read_bytes();app.rename_archive(src,dst,old,new)
   self.assertEqual(before,src.read_bytes())
   with zipfile.ZipFile(dst) as z:self.assertIn(new+'.carbin',z.namelist());self.assertNotIn(old.encode(),z.read(new+'.carbin'));self.assertNotEqual(z.read('Textures/custom/Swatches/test.swatchbin')[0x30:0x40],bytes(16));self.assertIsNone(z.testzip())
   with self.assertRaises(FileExistsError):app.rename_archive(src,dst,old,new)
 def test_malformed_names_and_members_are_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'old.zip'
   with zipfile.ZipFile(src,'w') as z:z.writestr('../escape','bad')
   with self.assertRaises(ValueError):app.rename_archive(src,Path(td)/'new.zip','VW_PassatB3_1990_A','RV0123456789ABCDEF')
   with self.assertRaises(ValueError):app.rename_archive(src,Path(td)/'bad.zip','bad/name','otherone')
 def test_wire_protocol_sizes_and_stale_ack_validation(self):
  self.assertEqual(app.REQUEST.size,160);self.assertEqual(app.ACK.size,64)
  with tempfile.TemporaryDirectory() as td,patch.object(app,'R',Path(td)):
   p=Path(td)/'runtime/refresh';p.mkdir(parents=True);(p/'ack.bin').write_bytes(bytes(64));self.assertIsNone(app.read_ack());(p/'ack.bin').write_bytes(app.ACK.pack(b'FH2ACK1',1,7,3,3803,b'RV0123456789ABCDEF'));self.assertEqual(app.read_ack()['serial'],7)
 def test_actual_native_reload_xml_has_back_exit_and_one_reload_entry(self):
  source=(R/'src/extra-options/features/garage.c').read_text();section=source.split('static void renderer_reload_flow_transform')[1].split('static void renderer_preview_transform')[0]
  view=c_string(section,'view');tail=c_string(section,'tail');redraw=c_string(section,'redraw');finish=c_string(section,'finish');reload=c_string(section,'reload')
  game=R/'game/Anthem/Mount/media/stateflow.zip'
  with zipfile.ZipFile(game) as z:original=z.read('garage.xml').decode('utf-8-sig')
  start=original.index('<state id="view_car_in_homespace">');end=original.index('</state>',start);block=original[start:end];self.assertEqual(block.count(view),1);self.assertEqual(block.count(tail),1);changed=block.replace(view,redraw).replace(tail,finish)+reload+'</state>';root=E.fromstring(changed);ids=[n.get('id') for n in root.findall('node') if n.get('id')];self.assertEqual(len(ids),len(set(ids)));self.assertIn('_renderer_load_again',ids);self.assertIn('_renderer_refreshable_view',ids)
  normal_cleanup=next(n for n in root.findall('node') if n.get('state')=='global.fade_in' and n.find('exit') is not None);self.assertEqual(normal_cleanup.find('exit').get('target'),'.exit')
  refresh_event=next(n for n in root.findall('node') if n.get('id')=='_renderer_refreshable_view');self.assertEqual(refresh_event.find('exit').get('target'),'_renderer_load_again')

class RefreshGuardTests(unittest.TestCase):
 def test_staging_refuses_an_unrelated_game_process(self):
  with patch.object(app.subprocess,'check_output',return_value='C:\\azimuth-windows\\azimuth.exe\n'),patch.object(app,'_stage') as stage:
   with self.assertRaisesRegex(ValueError,'private renderer'):app.stage('unused')
   stage.assert_not_called()
 def test_staging_lock_blocks_a_second_request(self):
  import fcntl
  with tempfile.TemporaryDirectory() as td,patch.object(app,'R',Path(td)):
   r=Path(td);q=r/'runtime/refresh';q.mkdir(parents=True);(r/'runtime/FH2_ExtraOptions.log').write_text('native UI reload transitions registered');expected='Z:'+str(r/'runtime/azimuth.exe').replace('/','\\')
   with (q/'staging.lock').open('a+b') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    with patch.object(app.subprocess,'check_output',return_value=expected+'\n'),patch.object(app,'_stage') as stage:
     with self.assertRaisesRegex(ValueError,'Another revision'):app.stage('unused')
     stage.assert_not_called()

if __name__=='__main__':unittest.main()
