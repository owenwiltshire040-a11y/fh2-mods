import json,re,unittest,zipfile,xml.etree.ElementTree as E
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class LeanBootTests(unittest.TestCase):
 def flow(self):
  s=(R/'src/extra-options/features/renderer_lean_flow.h').read_text().split('renderer_lean_flow[]=')[1]
  return E.fromstring(''.join(json.loads(m) for m in re.findall(r'"(?:[^"\\]|\\.)*"',s)))
 def test_lean_boot_keeps_native_player_setup_without_enabling_city_streaming(self):
  root=self.flow();self.assertEqual(root.get('id'),'cold_boot');states=[n.get('state') for n in root.findall('node')]
  for state in ['global.wait_for_loading_complete','global.load_player_car','global.setup_game_players','global.start_driving','global.unblock_pause_entry']:self.assertIn(state,states)
  for word in ['enable_track_streaming','traffic','festival_cars','place_car_at_restore_point','pause_menu']:self.assertFalse(any(word in s for s in states))
  self.assertEqual(next(n for n in root.findall('node') if n.get('state')=='global.load_player_car').get('set_focus_car'),'false')
 def test_every_bootstrap_state_reference_exists_in_original_archives(self):
  with zipfile.ZipFile(R/'game/Anthem/Mount/media/stateflow.zip') as z:
   groups={n[:-4]:{c.get('id') for c in E.fromstring(z.read(n))} for n in z.namelist() if n.endswith('.xml')}
  for node in self.flow().findall('node'):
   group,state=node.get('state').split('.',1);self.assertIn(state,groups[group],node.get('state'))
if __name__=='__main__':unittest.main()
