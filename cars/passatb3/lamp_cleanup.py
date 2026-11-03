"""Remove donor-only centre lamp and align large rear light points to Passat emitters."""
import struct,numpy as np

def apply(d,lamps):
 o=12
 for _ in range(struct.unpack_from('<I',d,8)[0]):n=struct.unpack_from('<I',d,o)[0];o+=6+n
 count=struct.unpack_from('<I',d,o)[0];start=o+4;out=[];removed=0
 for i in range(count):
  row=bytearray(d[start+76*i:start+76*(i+1)]);typ=struct.unpack_from('<I',row)[0];p=np.array(struct.unpack_from('<3f',row,12))
  if typ==0:removed+=1;continue
  fn='tail' if typ==7 else 'reverse' if typ==10 else None
  if fn in lamps and p[2]<0:
   v=lamps[fn][0];v=v[(v[:,0]<0) if p[0]<0 else (v[:,0]>0)]
   if len(v):
    centre=v.mean(0);centre[2]-=.005
    for at in (12,44):struct.pack_into('<3f',row,at,*centre)
  out.append(row)
 print('Lamp cleanup:',removed,'unmatched centre-light rows removed')
 return d[:o]+struct.pack('<I',len(out))+b''.join(out)+d[start+76*count:]
