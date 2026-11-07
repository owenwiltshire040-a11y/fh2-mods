"""Package finalizer (Claude 7 Nov, v0.1.2): the source decals drawn with FH2's native transparent livery shader.

As Codex's cars/redbullrb22/restore_decals.py: the decal materials named in source-analysis.json 'decals' get the
'carpaint_livery' MatI (template livery_decal_mati.bin, taken from the approved RB22 0.1.7 body, originally the
Williams FW24 wing livery), their swatches are rewritten WITH the source alpha, and their meshes use the 0x38 pass.
  python3 cars/porsche919/livery_decals.py PKG_DIR
"""
from pathlib import Path
import sys,json,re,struct,zipfile,uuid
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'f1'),str(ROOT/'tex')]
from geometry import Part
from body_swap import material_names
import fhmat,swatch
MEDIA='POR_Porsche919_17_'
def apply(pkg):
 A=json.loads((HERE/'source-analysis.json').read_text());tpl=(HERE/'livery_decal_mati.bin').read_bytes()
 archive=pkg/'media'/'cars'/f'{MEDIA}.zip'
 with zipfile.ZipFile(archive) as z:infos=z.infolist();entries={i.filename:z.read(i) for i in infos}
 low={n.lower():n for n in entries}
 body=next(n for n in entries if n.lower().endswith('/body_a.modelbin'));p=Part(entries[body]);names=material_names(p)
 want={f"{MEDIA.lower()}_{A['mapping'][k][1]}":k for k in A['decals']}
 done={};swatches=set()
 for b in p.b.blobs:
  if b['tag']!='MatI':continue
  nm=p.b.meta(b,'Name').decode()
  if nm not in want:continue
  path=re.findall(rb'[Gg]ame:\\[ -~]+?\.swatchbin',bytes(b['data']))[0].decode()
  entry=low[path.split('\\',4)[4].replace('\\','/').lower()] if False else low['/'.join(path.split('\\')[4:]).lower()]
  if entry not in swatches:
   img=Image.open(HERE/'textures'/A['textures'][want[nm]]).convert('RGBA');size=1024 if max(img.size)>=1024 else 512
   rgba=np.array(img.resize((size,size),Image.Resampling.LANCZOS));tex=bytearray(swatch.write_like(entries[entry],rgba));tex[0x30:0x40]=entries[entry][0x30:0x40]
   entries[entry]=bytes(tex);swatches.add(entry)
  b['data']=bytearray(fhmat.retexture(tpl,[path]));done[nm]=done.get(nm,0)+1
 meshes=0
 for r in p.render:
  if names[id(r['blob'])] in want:struct.pack_into('<I',r['blob']['data'],8,0x38);meshes+=1
 assert set(done)==set(want),('missing decal materials',set(want)-set(done))
 entries[body]=p.build();check=Part(entries[body]);assert struct.unpack_from('<H',next(b for b in check.b.blobs if b['tag']=='Modl')['data'],0)[0]==len(check.meshes)
 temp=archive.with_suffix('.tmp')
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
  for i in infos:z.writestr(i,entries[i.filename])
 temp.replace(archive)
 report=dict(valid=True,native_shader='carpaint_livery',alpha_preserved=True,materials=len(done),matis=sum(done.values()),meshes=meshes,swatches=len(swatches),runtime_status='Pending renderer view')
 (pkg/'decal-check.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':apply(Path(sys.argv[1]))
