"""Render additional angles from the actual built archives' preview geometry."""
from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];B=R/'cars/daily_batch';V=R/'scan/viewer'
jobs=json.loads((B/'wheel-view-jobs.json').read_text())
for job in jobs:
 dst=V/job['file'];dst.unlink(missing_ok=True)
 subprocess.run(['/bin/cp','-c',str(R/'cars'/job['slug']/'build/fit-preview.glb'),str(dst)],check=True)
server=subprocess.Popen([sys.executable,'-m','http.server','8767','--bind','127.0.0.1'],cwd=V,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:subprocess.run(['node','qa-wheels.js',str(B/'wheel-view-jobs.json')],cwd=V,check=True)
finally:server.terminate();server.wait()
m=json.loads((B/'build-manifest.json').read_text())
for page in range(6):
 out=Image.new('RGB',(1224,786),(28,31,36));d=ImageDraw.Draw(out)
 for row,item in enumerate(m[page*3:page*3+3]):
  p=Path(item['spec']).parent/'build';d.text((10,row*262+6),item['name'],fill='white')
  for col,src in enumerate([p/'thumb.png',p/'wheel-views/other-side.png',p/'wheel-views/rear.png']):
   im=Image.open(src).convert('RGBA');im.thumbnail((408,230));out.paste(im,(col*408,row*262+28),im)
 out.save(B/f'wheel-review-{page+1}.jpg',quality=92)
for job in jobs:(V/job['file']).unlink()
