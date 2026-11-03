"""Give the built carbin its own identity, preserving the donor skeleton/upgrade layout."""
from pathlib import Path
import sys,zipfile,shutil
p=Path(__file__).resolve().parent;root=p.parents[1];sys.path.insert(0,str(root/'fh2re'))
from carbin import read_carbin,write_carbin
q=p/'build/HYU_NVision74_23_A.zip';tmp=q.with_suffix('.tmp')
with zipfile.ZipFile(q) as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
 for n in src.namelist():
  data=src.read(n)
  if n.lower().endswith('.carbin'):
   c=read_carbin(data);c['ordinal']=4301;data=write_carbin(c);assert read_carbin(data)['ordinal']==4301
  out.writestr(n,data)
tmp.replace(q);shutil.copy2(q,root/'output/Hyundai N Vision 74/media/cars'/q.name)
print('Built carbin identity = 4301')
