import json,sys,tempfile,unittest,struct
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));sys.path.insert(0,str(R/'tools'))
import capture,camera,disassemble as native
class CaptureTests(unittest.TestCase):
 def test_pid_guard_matches_only_the_private_executable(self):
  expected='Z:'+str(capture.renderer.RUN/'azimuth.exe').replace('/',chr(92));listing='10 C:\\other\\azimuth.exe\n20 '+expected.replace(chr(92),chr(92)*2)+'\n30 '+expected+'.other\n'
  with patch.object(capture.subprocess,'check_output',return_value=listing):self.assertEqual(capture.private_pid(),20)
 def test_gallery_refuses_unlisted_images_and_path_traversal(self):
  with tempfile.TemporaryDirectory() as td,patch.object(capture,'R',Path(td)):
   folder=Path(td)/'captures'/('a'*32);folder.mkdir(parents=True);(folder/'manifest.json').write_text(json.dumps({'views':[{'file':'current.png'},{'file':'../../secret'}]}));(folder/'current.png').write_bytes(b'PNG')
   self.assertEqual(capture.image_path('a'*32,'current.png'),(folder/'current.png').resolve());self.assertIsNone(capture.image_path('a'*32,'missing.png'));self.assertIsNone(capture.image_path('../outside','current.png'));self.assertIsNone(capture.image_path('a'*32,'../../secret'))
 def test_capture_permission_failure_never_attempts_a_window_capture(self):
  ack={'code':4,'serial':7}
  with patch.object(capture,'private_pid',return_value=20),patch.object(capture.catalog,'read_ack',return_value=ack),patch.object(capture.catalog,'load_json',return_value={'serial':7}),patch.object(capture,'helper',return_value={'screen_capture_allowed':False}) as helper:
   with self.assertRaisesRegex(capture.CaptureError,'permission'):capture.current()
   helper.assert_called_once_with('--check')
 def test_failed_inspection_publishes_no_partial_images_and_restores_camera(self):
  with tempfile.TemporaryDirectory() as td,patch.object(capture,'R',Path(td)),patch.object(capture,'context',return_value={}),patch.object(capture,'permission'),patch.object(capture.camera,'command',return_value={}) as command,patch.object(capture.time,'sleep'),patch.object(capture,'frame',side_effect=[{'name':'first'},capture.CaptureError('view changed')]):
   with self.assertRaisesRegex(capture.CaptureError,'view changed'):capture._inspection()
   self.assertEqual(list((Path(td)/'captures').iterdir()),[])
   self.assertEqual(command.call_args.args,(2,))
 def test_capture_refuses_a_changed_car_or_process(self):
  expected={'pid':20,'selection':{'serial':1},'revision':None}
  with patch.object(capture,'private_pid',return_value=21):
   with self.assertRaisesRegex(capture.CaptureError,'changed'):capture.check_context(expected)
 def test_camera_switch_guard_matches_the_full_native_prologue(self):
  self.assertEqual(native.read(0xcd98b0,7),bytes.fromhex('40 53 57 48 83 ec 38'))
 def test_camera_wire_formats_and_pinned_native_setters(self):
  self.assertEqual(camera.REQUEST.size,64);self.assertEqual(camera.ACK.size,128)
  for slot,fn,offset in [(0x270,0x3976a0,0x1b0),(0x278,0x397770,0x1bc),(0x280,0x397700,0x1b8)]:
   self.assertEqual(struct.unpack('<Q',native.read(0x2d50360+slot,8))[0]-native.image_base,fn)
   self.assertIn('dword ptr [rcx + '+hex(offset)+']',next(native.md.disasm(native.read(fn,8),fn)).op_str)
if __name__=='__main__':unittest.main()
