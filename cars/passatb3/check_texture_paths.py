from pathlib import Path
import sys,zipfile,re,struct,zlib
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'fh2re'));from modelbin import Bundle
z=zipfile.ZipFile(r/'output/Volkswagen Passat B3/media/cars/VW_PassatB3_1990_A.zip');names={n.lower() for n in z.namelist()};count=0
for n in z.namelist():
 if not n.lower().endswith('.modelbin'):continue
 b=Bundle.read(z.read(n));tref=set()
 for bl in b.blobs:
  if bl['tag']=='Modl':
   for m in bl['meta']:
    if m['tag']=='TRef':
     nn=struct.unpack_from('<I',m['data'])[0];tref.update(struct.unpack_from('<%dI'%nn,m['data'],4))
 for bl in b.blobs:
  if bl['tag']!='MatI':continue
  raw=bytes(bl['data'])
  for match in re.finditer(rb'[Gg]ame:\\[ -~]+?\.swatchbin',raw):
   path=match.group().decode('latin1')
   if '\\Textures\\custom\\' not in path:continue
   assert len(path)<120,path
   crc=zlib.crc32(path.lower().encode('latin1'));assert struct.unpack_from('<I',raw,match.end())[0]==crc
   assert crc in tref
   entry=path.split('\\',4)[-1].replace('\\','/').lower();assert entry in names,(entry,n)
   count+=1
assert count>=10
assert z.testzip() is None
print('Validated',count,'generated texture references, CRCs, TRef membership and archive targets')
