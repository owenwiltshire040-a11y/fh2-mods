from pathlib import Path
import json,shutil,html,os
from urllib.parse import quote
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'cars/daily_batch';OUT=ROOT/'output/Daily Drivers';pre=OUT/'_previews';pre.mkdir(exist_ok=True)
m=json.loads((BASE/'build-manifest.json').read_text());cards=[];tiles=[]
notes={
'Opel Astra H':'Source contained detached and alternative panels. Selected bonnet/headlamp parts have been aligned; exterior still needs an in-game review.',
'Ford Focus Mk1':'Uses the intact hatchback variant from the multi-car source scene.',
'Ford Ka':'Untextured draft model. Body and cabin detail are limited by the supplied mesh.',
'Citroen Xsara':'Front wing surfaces retain visible faceting from the source conversion.',
'Volkswagen Passat B5.5':'Original fixed blue body colour retained.',
'Fiat Punto Mk2':'Wheel conversion checked. The converted source body has broken surfaces and a raised roof piece; body repair or a cleaner source is needed before treating this car as ready.',
}
for item in m:
 folder=Path(item['spec']).parent;pkg=OUT/item['name'];assert (pkg/'mod.json').is_file();fn=item['slug']+'.png';shutil.copy2(folder/'build/thumb.png',pre/fn)
 for angle in ['other-side','rear']:
  shutil.copy2(folder/'build/wheel-views'/f'{angle}.png',pre/f'{item["slug"]}-{angle}.png')
 if item['name'] in notes:
  for p in [folder/'BUILD-NOTES.txt',pkg/'BUILD-NOTES.txt']:
   text=p.read_text();extra=notes[item['name']]
   if extra not in text:p.write_text(text+'\nVisual review: '+extra+'\n')
 item['status']='installed' if item.get('installed_folder') else 'packaged';item['package']=str(pkg);item['visual_review']=notes.get(item['name'],'Preview reviewed; final wheel clearance, cockpit and lighting need an in-game check.')
 name=html.escape(item['name']);dirlink=quote(item['name']);cards.append(f'<article><img src="_previews/{fn}" alt="{name}"><div><h2>{name}</h2><p>{html.escape(item["visual_review"])}</p><p><a href="_previews/{item["slug"]}-other-side.png">Other side</a> · <a href="_previews/{item["slug"]}-rear.png">Rear view</a></p><p><a href="{dirlink}/wheel-build.json">Wheel checks</a> · <a href="{dirlink}/BUILD-NOTES.txt">Build notes</a> · <a href="{dirlink}/CREDITS.txt">Credits</a></p></div></article>')
 im=Image.open(folder/'build/thumb.png').convert('RGBA');im.thumbnail((510,287));tile=Image.new('RGB',(510,320),(28,31,36));tile.paste(im,(0,23),im);ImageDraw.Draw(tile).text((12,5),item['name'],fill='white');tiles.append(tile)
montage=Image.new('RGB',(1530,320*6),(28,31,36))
for i,tile in enumerate(tiles):montage.paste(tile,((i%3)*510,(i//3)*320))
montage.save(OUT/'All 18 previews.jpg',quality=90)
blocked=[dict(name='Volvo 850 Estate',status='source conversion blocked',reason='The supplied HQLM file yields no geometry instances in the reader. The IVF file references geometry indices 6–41 but only one geometry is decoded. Needs a compatible RenderWare reader or an standard export from the author.'),dict(name='Volvo 850 Saloon',status='source conversion blocked',reason='The archive contains GTA IV .wft/.wtd assets. The current importer supports GLB, OBJ and GTA SA RenderWare, so this needs a GTA IV geometry/texture conversion first.')]
(BASE/'blocked-sources.json').write_text(json.dumps(blocked,indent=2));(BASE/'build-manifest.json').write_text(json.dumps(m,indent=2))
body=''.join(cards);b=''.join('<li><strong>'+html.escape(x['name'])+'</strong>: '+html.escape(x['reason'])+'</li>' for x in blocked)
(OUT/'index.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Daily drivers — test builds</title><style>body{{background:#15181e;color:#eee;font:16px system-ui;margin:0}}main{{max-width:1250px;margin:auto;padding:42px 24px}}h1{{font-size:36px;margin-bottom:12px}}h2{{font-size:20px}}p{{line-height:1.6;color:#bbc3cf}}.intro{{max-width:900px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px;margin-top:30px}}article{{background:#20262f;border:1px solid #39414e;border-radius:12px;overflow:hidden}}article img{{width:100%;display:block}}article div{{padding:0 22px 16px}}a{{color:#87bbff}}li{{margin:16px 0;line-height:1.6}}.count{{color:#87bbff}}</style><main><h1>Daily drivers</h1><p class="count">18 individual v0.1.1 test packages · 2 source conversions pending</p><div class="intro"><p>Personal first-pass conversions for FH2 / Azimuth. All 18 packages passed database, engine curve, media, unique-ID, wheel-fit, source-wheel and open-barrel checks. They have not been tested in the running game.</p><p>All 18 builds now use their own source wheels, with reviewed geometry and original colour/texture atlases. Source lighting is currently decorative. Handling, cockpit cameras, driver placement and remaining trim details are provisional. The Ka is a rough untextured draft; the Astra needed substantial panel selection. Review individual notes below.</p><p>Fully restart the game after installation. The source-wheel install record lists the updated folders and preserved originals.</p></div><div class="grid">{body}</div><h2>Source files that still need conversion</h2><ul>{b}</ul></main></html>''')
(OUT/'README.md').write_text('# Daily drivers — first test builds\n\n18 separate v0.1.1 packages. Open index.html for the preview gallery.\n\nAll use their own source wheels. Lighting is decorative at this stage. Cockpit placement, source trim, handling and upgrades need an in-game review. These are not finished factory-accurate car mods.\n\n'+ '\n'.join('- '+x['name'] for x in m)+'\n\nNot built:\n'+ '\n'.join('- '+x['name']+': '+x['reason'] for x in blocked)+'\n')
print('Gallery created for',len(cards),'packages')
