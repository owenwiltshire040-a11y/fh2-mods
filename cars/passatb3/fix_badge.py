from pathlib import Path
import json,struct
p=Path(__file__).resolve().parent
b=(p/'stock.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n])
a=(p/'model.glb').read_bytes();an=struct.unpack_from('<I',a,12)[0];orig=json.loads(a[20:20+an])
# The source lays out alternate trim badges at different heights. Use GL at its base height.
d['nodes'][321]=orig['nodes'][321].copy();d['nodes'][321]['matrix']=list(d['nodes'][321]['matrix']);d['nodes'][321]['matrix'][14]=0.0
d['nodes'][325]['children']=[]
j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);rest=b[20+n:]
(p/'stock.glb').write_bytes(struct.pack('<4sII',b'glTF',2,20+len(j)+len(rest))+struct.pack('<I4s',len(j),b'JSON')+j+rest)
print('GL badge restored at boot-lid height; floating alternate GT badge removed')
