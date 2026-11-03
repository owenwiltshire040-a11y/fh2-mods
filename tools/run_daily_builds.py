from pathlib import Path
import json,subprocess,sys,time,os,zipfile,zlib
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'cars/daily_batch';manifest=json.loads((base/'build-manifest.json').read_text());donor=Path('/Users/owen/Desktop/untitled folder/DOD_ChargerSRT8_12.zip')
for item in manifest:
 if item['status'] not in ['prepared','build failed']:continue
 folder=Path(item['spec']).parent;log=folder/'build.log';dst=folder/('donor_'+item['media']+'.zip')
 with log.open('w') as out:
  valid_donor=False
  if dst.exists():
   try:
    with zipfile.ZipFile(dst) as z:valid_donor=z.testzip() is None
   except (zipfile.BadZipFile,OSError,zlib.error):pass
  if not valid_donor:
   p=subprocess.run([sys.executable,str(ROOT/'f1/make_media.py'),str(donor),str(dst),item['media']],cwd=ROOT/'f1',stdout=out,stderr=subprocess.STDOUT)
   if p.returncode:item['status']='donor failed';continue
  print('BUILD',item['name'],flush=True)
  p=subprocess.run([sys.executable,'package_car.py',item['spec'],str(ROOT/'output/Daily Drivers')],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
 item['status']='packaged' if p.returncode==0 else 'build failed';item['log']=str(log)
 if p.returncode==0:item['package']=str(ROOT/'output/Daily Drivers'/item['name'])
 else:print(log.read_text()[-1800:],flush=True)
 print(item['name'],item['status'],flush=True);(base/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
