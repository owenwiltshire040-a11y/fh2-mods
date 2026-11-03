import sys,json,re,tempfile,unittest,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import catalog

def literal(section,name):
 block=section.split('char '+name+'[]=')[1].split(';')[0]
 return ''.join(json.loads(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"',block))
class CatalogTests(unittest.TestCase):
 def test_stock_preview_replaces_purchase_screen_and_preserves_native_reload_sequence(self):
  source=(R/'src/extra-options/features/garage.c').read_text().split('static void renderer_stock_flow_transform')[1].split('static void renderer_preview_transform')[0]
  with zipfile.ZipFile(R/'game/Anthem/Mount/media/stateflow.zip') as z:original=z.read('autoshow.xml').decode('utf-8-sig')
  view=literal(source,'view');redraw=literal(source,'redraw');stop=literal(source,'stop');reload=literal(source,'reload')
  start=original.index('<state id="root_internal">');end=original.index('</state>',start)+8;block=original[start:end]
  self.assertEqual(block.count(view),1);self.assertEqual(block.count(stop),1)
  at=block.index(view);close=block.index('</node>',at)+7
  changed=block[:at]+redraw+block[close:];changed=changed.replace(stop,reload)
  root=E.fromstring(changed);nodes=root.findall('node');screen=next(n for n in nodes if n.get('id')=='colour_select')
  self.assertEqual(screen.get('state'),'ui_screens.show_view_car_from_pause')
  self.assertEqual({n.get('target') for n in screen.findall('exit')},{'_renderer_stock_reload','car_select_post_colour_select'})
  self.assertNotIn('ui_screens.car_color_select',changed)
  states=[n.get('state') for n in nodes];self.assertLess(states.index('global.unload_ui_car'),states.index('global.load_ui_car'))
 def test_scan_requires_matching_asset_and_decodes_packed_localized_names(self):
  with tempfile.TemporaryDirectory() as td,patch.object(catalog,'R',Path(td)/'viewer'):
   root=catalog.R/'runtime/mods';folder=root/'pack';(folder/'media/cars').mkdir(parents=True)
   (root/'loadorder.txt').write_text('pack\n');(folder/'mod.json').write_text(json.dumps({'id':'test','name':'Pack','database':'db.json','media':'media'}))
   rows=[{'Id':1,'MediaName':'CAR_One','ModelShort':'_&65537'},{'Id':2,'MediaName':'CAR_Two','ModelShort':'_&65538'},{'Id':3,'MediaName':'Unused'}]
   (folder/'db.json').write_text(json.dumps({'tables':{'Data_Car':{'insert':rows}}}));(folder/'strings.json').write_text(json.dumps({'languages':{'EN':{'Data_Car':{'1':'First car','2':'Second car'}}}}))
   for n in ['CAR_One','CAR_Two']:(folder/'media/cars'/(n+'.zip')).write_bytes(b'car')
   cars=catalog.scan();self.assertEqual([c['name'] for c in cars],['First car','Second car']);self.assertTrue(all(c['installed'] for c in cars));self.assertEqual(cars,catalog.scan())
 def test_selection_serializes_request_and_prevents_overlapping_selection(self):
  with tempfile.TemporaryDirectory() as td,patch.object(catalog,'R',Path(td)),patch.object(catalog,'scan',return_value=[{'id':'test','installed':True,'needs_restart':False,'car_id':12,'media':'CAR_One','name':'First','mod_id':'test'}]):
   self.assertEqual(catalog.select('test')['serial'],1)
   q=Path(td)/'runtime/refresh';self.assertEqual(catalog.SELECT.unpack((q/'selection.bin').read_bytes())[2:5],(1,12,b'CAR_One'+bytes(12)))
   with self.assertRaisesRegex(ValueError,'still opening'):catalog.select('test')
   (q/'selection-ack.bin').write_bytes(catalog.ACK.pack(b'FH2SACK',1,1,4,12,b'CAR_One'))
   self.assertEqual(catalog.select('test')['serial'],2)
if __name__=='__main__':unittest.main()
