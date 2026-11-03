import importlib.util,tempfile,unittest,zipfile,xml.etree.ElementTree as E,re,json
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('renderer',R/'renderer.py');app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
class IsolationTests(unittest.TestCase):
 def test_modes_keep_native_archives_original_and_select_only_private_dll(self):
  for showroom in [False,True]:
   with self.subTest(showroom=showroom),tempfile.TemporaryDirectory() as td:
    t=Path(td);assets=t/'assets';assets.mkdir();run=t/'run';run.mkdir()
    with patch.object(app,'MOD',t/'mod'),patch.object(app,'RUN',run),patch.object(app,'private_mount',return_value=assets):app.mode(showroom)
    for n in ['stateflow.zip','zipmanifest.xml']:self.assertEqual((assets/n).read_bytes(),(app.GAME/'media'/n).read_bytes())
    expected=R/'build/winmm-renderer.dll' if showroom else app.SOURCE/'winmm.dll';self.assertEqual((run/'winmm.dll').read_bytes(),expected.read_bytes())
 def test_actual_c_entry_uses_native_pause_context_and_existing_view_route(self):
  source=(R/'src/extra-options/features/garage.c').read_text();section=source.split('static const char injection[]=')[1].split(';')[0];xml=''.join(json.loads(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"',section));entry=E.fromstring(xml);self.assertEqual(entry.get('target'),'autoshow')
  with zipfile.ZipFile(app.GAME/'media/stateflow.zip') as z:root=E.fromstring(z.read('pause.xml'))
  flow=next(n for n in root if n.get('id')=='pause_menu_flow');self.assertTrue(any(n.get('id')=='UIContextWrapper' and n.get('flag_name')=='InPauseMenu' for n in flow.findall('behavior')));picker=next(n for n in flow.findall('node') if n.get('id')=='_car_select_garage_pause_menu');self.assertEqual(picker.get('state'),'ui_screens.car_select_garage_pause_menu');view=next(n for n in flow.findall('node') if n.get('id')=='view_car');self.assertEqual(view.get('state'),'garage.view_car_in_homespace');self.assertTrue(any(n.get('id')=='car_view' and n.get('target')=='view_car' for n in picker.findall('exit')))
 def test_stop_matches_exact_private_executable_with_macos_escaping(self):
  own='Z:'+str(app.RUN/'azimuth.exe').replace('/','\\');escaped=own.replace('\\','\\\\');lines='15 C:\\\\azimuth-windows\\\\azimuth.exe\n16 '+escaped+'\n17 '+escaped+'.other\n'
  with patch.object(app.subprocess,'check_output',return_value=lines),patch.object(app.os,'kill') as kill:app.stop();kill.assert_called_once_with(16,app.signal.SIGTERM)
class RefreshSessionTests(unittest.TestCase):
 def test_previous_requests_are_archived_without_touching_revisions(self):
  with tempfile.TemporaryDirectory() as td,patch.object(app,'RUN',Path(td)):
   q=Path(td)/'refresh';g=q/'generations';g.mkdir(parents=True);(g/'keep.zip').write_bytes(b'unchanged');(q/'request.bin').write_bytes(b'request');(q/'ack.bin').write_bytes(b'ack');app.archive_refresh_requests();self.assertFalse((q/'request.bin').exists());self.assertFalse((q/'ack.bin').exists());history=list((q/'history').iterdir());self.assertEqual(len(history),1);self.assertEqual((history[0]/'request.bin').read_bytes(),b'request');self.assertEqual((g/'keep.zip').read_bytes(),b'unchanged')

if __name__=='__main__':unittest.main()
