"""Check the pinned native UI boundary used by startup automation."""
import sys,struct,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import disassemble as native
class StartupBoundaryTests(unittest.TestCase):
 def test_window_singleton_is_the_reference_written_by_native_initializer(self):
  code=native.read(0x1411f2e,7)
  self.assertEqual(code[:3],b'\x48\x89\x05')
  self.assertEqual(0x1411f35+struct.unpack('<i',code[3:])[0],0x3684b88)
  col=struct.unpack('<Q',native.read(0x2ecf920-8,8))[0]-native.image_base
  td=struct.unpack('<I',native.read(col+12,4))[0]
  self.assertEqual(native.read(td+16,100).split(b'\0')[0],b'.?AVWindowLayerManager@@')
 def test_splash_continue_uses_the_registered_key_and_loading_state_callback(self):
  self.assertEqual(native.read(0xe8f9a5,5),b'\xba\x12\x00\x00\x00')
  self.assertEqual(struct.unpack('<Q',native.read(0x2e5a258+16,8))[0]-native.image_base,0xea27a0)
  call=0xea27a8;self.assertEqual(call+5+struct.unpack('<i',native.read(call+1,4))[0],0xea0d40)
  index=native.read(0x14e3f80+0x20-3,1)[0]
  dest=struct.unpack('<I',native.read(0x14e3cd8+index*4,4))[0]
  self.assertEqual(native.read(dest,6),b'\xb8\x12\x00\x00\x00\xc3')
 def test_pause_hook_uses_existing_wait_state_and_native_pause_transition(self):
  self.assertEqual(struct.unpack('<Q',native.read(0x2d2f768,8))[0]-native.image_base,0x964810)
  self.assertEqual(native.read(0x9649c4,5),b'\xba\x86\x00\x00\x00')
  self.assertEqual(native.read(0x9649d5,4),b'\x48\x8d\x57\x28')
  code=native.read(0x96489f,7)
  self.assertEqual(0x9648a6+struct.unpack('<i',code[2:6])[0],0x2cf73f0)
 def test_native_menu_input_dispatch_and_scene_getter_are_pinned(self):
  self.assertEqual(struct.unpack('<Q',native.read(0x2ecf9f8,8))[0]-native.image_base,0x1422de0)
  code=native.read(0x1422e11,22)
  self.assertEqual(code[:4],b'\x48\x8b\x49\x68')
  self.assertIn(b'\xe8',code)
  call=0x1422e22;self.assertEqual(call+5+struct.unpack('<i',native.read(call+1,4))[0],0xb70d30)
if __name__=='__main__':unittest.main()
