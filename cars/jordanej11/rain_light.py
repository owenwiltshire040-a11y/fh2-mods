"""Single central rear tail/brake light; no invisible donor headlights or indicators."""
import struct,numpy as np

def apply(d,lamps):
 o=8;n=struct.unpack_from('<I',d,o)[0];o+=4;paths=[]
 for _ in range(n):
  length=struct.unpack_from('<I',d,o)[0];paths.append(d[o+4:o+4+length]);o+=6+length
 count=struct.unpack_from('<I',d,o)[0];body=d[o+4:]
 record=next(body[76*i:76*(i+1)] for i in range(count) if struct.unpack_from('<I',body,76*i)[0]==7)
 path=next(p for p in paths if p.lower().endswith(b'taillightl_a.modelbin'))
 V=lamps['tail'][0];centre=(V.min(0)+V.max(0))/2+[0,0,-.004]
 out=bytearray(d[:8])+struct.pack('<II',1,len(path))+path+struct.pack('<HI',1,2)
 for flags in [0x20045,0x45]:
  r=bytearray(record);struct.pack_into('<Ii',r,4,flags,0);struct.pack_into('<3f',r,12,*centre);struct.pack_into('<3f',r,44,*centre);out+=r
 return bytes(out)
