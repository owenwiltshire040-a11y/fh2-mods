"""Discover installed mod cars and publish bounded, atomic native-selection requests."""
from pathlib import Path
import ast,hashlib,json,os,re,struct,time,zipfile
R=Path(__file__).resolve().parent
SELECT=struct.Struct('<8sIII19s25x');ACK=struct.Struct('<8sIIII19s21x')
assert SELECT.size==ACK.size==64
SAFE=re.compile(r'^[A-Za-z0-9_]{3,18}$')
def load_json(path,default=None):
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return default

def thumbnail_map():
 result={};project=R.parent/'Passat B3 Build'
 for spec in (project/'cars').glob('*/spec.py'):
  thumb=spec.parent/'build/thumb.png'
  if not thumb.is_file():continue
  try:
   tree=ast.parse(spec.read_text())
   for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MEDIA' for t in node.targets) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):result[node.value.value.lower()]=thumb
  except (OSError,SyntaxError):continue
 return result

def scan():
 thumbs=thumbnail_map();mods=R/'runtime/mods';order=mods/'loadorder.txt'
 active=set(order.read_text().splitlines()) if order.exists() else set();cars=[]
 installed=[p for p in sorted(mods.iterdir()) if p.is_dir() and not p.name.startswith('.') and (not active or p.name in active)]
 built=[p.parent for p in (R.parent/'Passat B3 Build/output').glob('**/mod.json')]
 runtime_ids={load_json(p/'mod.json',{}).get('id'):p for p in installed}
 for folder in installed+built:
  if not folder.is_dir() or folder.name.startswith('.'):continue
  meta=load_json(folder/'mod.json',{})
  if not meta.get('id') or not isinstance(meta.get('database'),str):continue
  db_path=(folder/meta['database']).resolve()
  if not db_path.is_relative_to(folder.resolve()):continue
  database=load_json(db_path,{}) or {};strings=load_json(folder/(meta.get('strings') or 'strings.json'),{}) or {}
  names=strings.get('languages',{}).get('EN',{}).get('Data_Car',{})
  if not isinstance(meta.get('media'),str):continue
  media=folder/meta['media']
  if not media.resolve().is_relative_to(folder.resolve()):continue
  available={p.stem.lower():p for p in (media/'cars').glob('*.zip')}
  rows=database.get('tables',{}).get('Data_Car',{}).get('insert',[])
  for row in rows:
   base=row.get('MediaName','');cid=row.get('Id')
   if not isinstance(base,str) or not SAFE.fullmatch(base) or not isinstance(cid,int) or cid<=0 or base.lower() not in available:continue
   key=hashlib.sha256((meta['id']+'\0'+base.lower()).encode()).hexdigest()[:24]
   def localized(ref):
    try:return names.get(str(int(str(ref).removeprefix('_&'))&65535))
    except ValueError:return None
   real_count=sum(isinstance(x.get('MediaName'),str) and x['MediaName'].lower() in available for x in rows)
   name=meta.get('name') if real_count==1 else localized(row.get('ModelShort')) or localized(row.get('DisplayName'))
   if not name:name=base.replace('_',' ')
   if not isinstance(name,str):name=base
   cached=R/'cache/thumbnails'/(key+'.png')
   if base.lower() not in thumbs and cached.is_file():thumbs[base.lower()]=cached
   private=runtime_ids.get(meta['id']);installed_here=private is not None
   source_package=folder if folder in built else None
   needs_restart=bool(source_package and private and load_json(private/meta['database'],{})!=database)
   cars.append({'installed':installed_here,'needs_restart':needs_restart,'package':str(source_package) if source_package else None,'id':key,'name':name,'package_name':meta.get('name',folder.name),'mod_id':meta['id'],'media':base,'car_id':cid,'year':row.get('Year'),'version':meta.get('version',''),'folder':str(folder),'thumbnail':str(thumbs.get(base.lower(),'')),'native_thumbnail':str(media/'stripped/RC0'/(Path(str(row.get('Thumbnail','')).replace(chr(92),'/')).stem+'_Big.swatchbin')),'source':'installed mod'})
 merged={c['id']:c for c in cars}
 return sorted(merged.values(),key=lambda c:(c['name'].casefold(),c['media'].lower()))

def read_ack():
 p=R/'runtime/refresh/selection-ack.bin'
 if not p.exists():return None
 raw=p.read_bytes()
 if len(raw)!=ACK.size:return None
 magic,version,serial,code,cid,media=ACK.unpack(raw)
 if magic!=b'FH2SACK\0' or version!=1:return None
 labels={1:'Waiting for the car browser',2:'Car selected',3:'Opening car',4:'Car view opened',10:'Car not found in the active viewer',11:'Car not present in the native browser',12:'Native selection unavailable',13:'Invalid selection request'}
 return {'serial':serial,'code':code,'car_id':cid,'media':media.rstrip(b'\0').decode('ascii'),'message':labels.get(code,'Unknown selection state')}

def _select(car_id):
 cars={c['id']:c for c in scan()}
 if car_id not in cars:raise ValueError('This car is no longer installed in the viewer')
 car=cars[car_id]
 if not car['installed'] or car['needs_restart']:raise ValueError('Restart the viewer to install this build first')
 queue=R/'runtime/refresh';queue.mkdir(parents=True,exist_ok=True);pending=queue/'selection.bin';ack=read_ack()
 if pending.exists():
  old=SELECT.unpack(pending.read_bytes());last=old[2]
  if not ack or ack['serial']!=last or ack['code']<4:raise ValueError('The previous car selection is still opening')
 else:last=0
 serial=last+1;payload=SELECT.pack(b'FH2SEL1',1,serial,car['car_id'],car['media'].encode('ascii'));tmp=queue/'selection.tmp';tmp.write_bytes(payload);os.replace(tmp,pending)
 # Keep the one-click refresher pointed at a matching built package if available.
 output=R.parent/'Passat B3 Build/output'
 for path in output.glob('**/mod.json'):
  metadata=load_json(path,{})
  if metadata.get('id')==car['mod_id'] and (path.parent/'media/cars'/(car['media']+'.zip')).is_file():
   (R/'refresh-target.json').write_text(json.dumps({'name':car['name'],'package':str(path.parent.resolve())},indent=2)+'\n');break
 (queue/'selection-target.json').write_text(json.dumps({'serial':serial,'catalog_id':car_id,'name':car['name']},indent=2)+'\n')
 return {'serial':serial,'car':car['name'],'message':'Selection queued'}

def select(car_id):
 import fcntl
 q=R/'runtime/refresh';q.mkdir(parents=True,exist_ok=True)
 with (q/'staging.lock').open('a+b') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('A build refresh is still being staged')
  try:return _select(car_id)
  finally:fcntl.flock(lock,fcntl.LOCK_UN)

def sync_builds():
 import subprocess,uuid
 entries=scan();sources={c['mod_id']:Path(c['package']) for c in entries if c['package']}
 mods=R/'runtime/mods';order=mods/'loadorder.txt';lines=order.read_text().splitlines();known={load_json(p/'mod.json',{}).get('id'):p for p in mods.iterdir() if p.is_dir() and not p.name.startswith('.')}
 completed=set();visiting=set()
 def sync(mod_id):
  if mod_id in completed:return
  if mod_id in visiting:raise ValueError('Build packages have a dependency cycle')
  visiting.add(mod_id);src=sources[mod_id];meta=load_json(src/'mod.json',{})
  for dep in meta.get('dependencies',[]):
   dependency=dep if isinstance(dep,str) else dep.get('id')
   if dependency in sources:sync(dependency)
   elif dependency not in known:raise ValueError('Missing viewer dependency: '+str(dependency))
  dst=known.get(mod_id,mods/src.name)
  if dst.exists() and mod_id not in known:raise ValueError('A different viewer mod already uses the folder '+dst.name)
  def hashes(folder):return {str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
  expected=hashes(src)
  if not dst.exists() or hashes(dst)!=expected:
   stage=mods/('.catalog-stage-'+uuid.uuid4().hex);subprocess.run(['/bin/cp','-cR',str(src),str(stage)],check=True)
   if hashes(stage)!=expected:raise ValueError('Build copy verification failed')
   backup=R/'backups/package-sync'/str(time.time_ns())/dst.name
   if dst.exists():backup.parent.mkdir(parents=True,exist_ok=True);dst.rename(backup)
   try:stage.rename(dst)
   except BaseException:
    if backup.exists():backup.rename(dst)
    raise
  if dst.name not in lines:lines.append(dst.name)
  known[mod_id]=dst;visiting.remove(mod_id);completed.add(mod_id)
 for mid in sources:sync(mid)
 order.write_text('\n'.join(lines)+'\n');return len(completed)

if __name__=='__main__':
 print(json.dumps(scan(),indent=2))
