"""Read native RTTI/vtables from the pinned binary; never executes game code."""
import disassemble as d,struct,sys

def main_vtable(name):
 p=d.raw.index(name.encode()+b'\0')-16
 start,size,physical=next(x for x in d.sections if x[2]<=p<x[2]+x[1]);td=start+p-physical
 for start,size,physical in d.sections:
  if start<0x1dcc000:continue
  data=d.read(start,size);at=0
  while (at:=data.find(struct.pack('<I',td),at))>=0:
   col=start+at-12;at+=1
   if d.read(col,8)!=b'\1\0\0\0\0\0\0\0':continue
   for s,sz,ph in d.sections:
    hit=d.read(s,sz).find(struct.pack('<Q',d.image_base+col))
    if hit>=0:return s+hit+8
 raise ValueError('No primary vtable')
if __name__=='__main__':
 vt=main_vtable(sys.argv[1]);print('VTABLE',hex(vt))
 for off in range(0,int(sys.argv[2],16) if len(sys.argv)>2 else 0x100,8):print(hex(off),hex(struct.unpack('<Q',d.read(vt+off,8))[0]-d.image_base))
