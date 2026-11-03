"""Read-only native-code inspection against the pinned game binary."""
from pathlib import Path
import struct,sys,bisect
sys.path.insert(0,str(Path(__file__).resolve().parent/'python'))
import capstone
P=Path(__file__).resolve().parents[1]/'game/Anthem/Mount/forza_durango_release_final.exe';raw=P.read_bytes();u16=lambda n:struct.unpack_from('<H',raw,n)[0];u32=lambda n:struct.unpack_from('<I',raw,n)[0];nt=u32(0x3c);opt=nt+24;image_base=struct.unpack_from('<Q',raw,opt+24)[0];sections=[]
for i in range(u16(nt+6)):
 p=opt+u16(nt+20)+40*i;sections.append((u32(p+12),max(u32(p+8),u32(p+16)),u32(p+20)))
def offset(rva):
 for start,size,physical in sections:
  if start<=rva<start+size:return physical+rva-start
 raise ValueError(hex(rva))
def read(rva,n):return raw[offset(rva):offset(rva)+n]
exc,size=struct.unpack_from('<II',raw,opt+112+3*8);functions=[struct.unpack('<III',read(exc+i,12)) for i in range(0,size,12)];starts=[x[0] for x in functions]
def bounds(rva):
 i=bisect.bisect_right(starts,rva)-1
 if i>=0 and functions[i][0]<=rva<functions[i][1]:return functions[i][:2]
 return rva,rva+128
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_64);md.detail=True
def dis(rva,limit=500):
 start,end=bounds(rva);print('FUNCTION',hex(start),hex(end),'base',hex(image_base))
 for i,ins in enumerate(md.disasm(read(start,end-start),start)):
  if i>=limit:print('...');break
  notes=[]
  for op in ins.operands:
   if op.type==capstone.x86.X86_OP_MEM and op.mem.base==capstone.x86.X86_REG_RIP:
    addr=ins.address+ins.size+op.mem.disp
    try:
     data=read(addr,120).split(b'\0')[0]
     if len(data)>3 and all(31<c<127 for c in data):notes.append(repr(data.decode()))
    except ValueError:pass
  print(f'{ins.address:08x} {ins.mnemonic:8} {ins.op_str:50}',*notes)
if __name__=='__main__':
 for arg in sys.argv[1:]:dis(int(arg,16))
