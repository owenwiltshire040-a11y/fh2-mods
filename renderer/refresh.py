"""Stage immutable visual revisions; the private engine consumes the atomic request."""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,sys,uuid,zipfile,time,subprocess,fcntl
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools'))
from modelbin import Bundle
REQUEST=struct.Struct('<8sIII19s19s96s6x');ACK=struct.Struct('<8sIIII19s21x')
assert REQUEST.size==160 and ACK.size==64
TOKEN=re.compile(r'^[A-Za-z0-9_]{3,18}$')
def rename_bytes(raw,old,new):
 for a,b in [(old,new),(old.lower(),new.lower()),(old.upper(),new.upper())]:raw=raw.replace(a.encode('ascii'),b.encode('ascii'))
 return raw
def rename_model(raw,old,new):
 bundle=Bundle.read(rename_bytes(raw,old,new));remap={}
 for blob in bundle.blobs:
  if blob['tag']!='MatI' or not blob['data']:continue
  data=bytearray(blob['data'])
  for match in re.finditer(rb'[Gg]ame:\\[ -~]+?\.swatchbin',bytes(data)):
   path=match.group().decode('ascii')
   if new.lower() not in path.lower():continue
   before=re.sub(re.escape(new),old,path,flags=re.I);was=__import__('zlib').crc32(before.lower().encode());now=__import__('zlib').crc32(path.lower().encode())
   if struct.unpack_from('<I',data,match.end())[0]!=was:raise ValueError('Texture path checksum is not where expected: '+path)
   struct.pack_into('<I',data,match.end(),now);remap[was]=now
  blob['data']=data
 for blob in bundle.blobs:
  if blob['tag']=='Modl':
   for meta in blob['meta']:
    if meta['tag']=='TRef':
     count=struct.unpack_from('<I',meta['data'])[0];values=struct.unpack_from('<'+str(count)+'I',meta['data'],4);meta['data']=struct.pack('<I'+str(count)+'I',count,*[remap.get(x,x) for x in values])
 return bundle.write()
def rename_archive(source,destination,old,new):
 if not TOKEN.fullmatch(old) or not TOKEN.fullmatch(new) or len(old)!=len(new):raise ValueError('Revision names must be safe and have exactly the same length')
 with zipfile.ZipFile(source) as src,zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  if src.testzip() is not None:raise ValueError('Source archive has a CRC failure')
  if sum(x.file_size for x in src.infolist())>512*1024*1024:raise ValueError('Visual revision is larger than the supported staging limit')
  names=set()
  for entry in src.infolist():
   if entry.filename.startswith(('/','\\')) or '..' in Path(entry.filename.replace('\\','/')).parts:raise ValueError('Unsafe archive member')
   name=re.sub(re.escape(old),new,entry.filename,flags=re.I)
   if name.lower() in names:raise ValueError('Duplicate revision archive member')
   names.add(name.lower());raw=src.read(entry)
   raw=rename_model(raw,old,new) if name.lower().endswith('.modelbin') else rename_bytes(raw,old,new)
   # Custom swatch headers are produced by our BC7 builder. Give each revision
   # a new resource GUID as well as a new path; otherwise texture caches may alias.
   if name.lower().startswith('textures/custom/swatches/') and name.lower().endswith('.swatchbin'):
    if len(raw)<0x53:raise ValueError('Custom texture has no supported swatch header')
    data=bytearray(raw);data[0x30:0x40]=uuid.uuid5(uuid.NAMESPACE_URL,new+'/'+name.lower()).bytes_le;raw=bytes(data)
   info=zipfile.ZipInfo(name,date_time=entry.date_time);out.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(destination) as z:
  if z.testzip() is not None:raise ValueError('Staged revision failed its CRC check')
def _stage(package,visual_zip=None):
 package=Path(package).resolve();meta=json.loads((package/'mod.json').read_text());db=json.loads((package/'database.json').read_text());archives=list((package/'media/cars').glob('*.zip'))
 if len(archives)!=1:raise ValueError('Choose one single-car mod package')
 old=archives[0].stem
 if not TOKEN.fullmatch(old):raise ValueError('Unsupported media name')
 rows=[x for x in db['tables']['Data_Car'].get('insert',[]) if x.get('MediaName')==old]
 if len(rows)!=1:raise ValueError('Cannot identify one car record for this package')
 folders=[p for p in (R/'runtime/mods').iterdir() if p.is_dir() and (p/'mod.json').is_file() and json.loads((p/'mod.json').read_text()).get('id')==meta['id']]
 if len(folders)!=1:raise ValueError('The car must already be installed in the private renderer')
 folder=folders[0].name
 if not re.fullmatch(r'[A-Za-z0-9_ ()-]{1,95}',folder):raise ValueError('Unsupported runtime mod folder name')
 queue=R/'runtime/refresh';generations=queue/'generations';generations.mkdir(parents=True,exist_ok=True)
 pending=queue/'request.bin';ack=read_ack()
 if pending.exists():
  old_request=REQUEST.unpack(pending.read_bytes());last=old_request[2]
  if not ack or ack['serial']!=last or ack['code'] in [1,2]:raise ValueError('A refresh is still pending; keep its car view open or restart the renderer before staging another')
 else:last=0
 serial=last+1
 if serial>0xffffffff:raise ValueError('Refresh serial exhausted')
 new='RV'+uuid.uuid4().hex[:len(old)-2].upper();target=generations/(new+'.zip');source=Path(visual_zip).resolve() if visual_zip else archives[0]
 # Supplying another historical build is allowed only for the same visual car.
 with zipfile.ZipFile(source) as z:
  if not any(n.lower().endswith(old.lower()+'.carbin') for n in z.namelist()):raise ValueError('Visual ZIP belongs to a different car')
 try:rename_archive(source,target,old,new)
 except BaseException:target.unlink(missing_ok=True);raise
 report={'serial':serial,'car_id':rows[0]['Id'],'base_media':old,'revision_media':new,'source_mod':folder,'package':str(package),'visual_zip':str(source),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'database_changes':'MediaName only; no handling/upgrade changes','created':time.strftime('%Y-%m-%d %H:%M:%S')}
 (generations/(new+'.json')).write_text(json.dumps(report,indent=2)+'\n')
 payload=REQUEST.pack(b'FH2RFR1',1,serial,rows[0]['Id'],old.encode(),new.encode(),folder.encode());tmp=queue/'request.tmp';tmp.write_bytes(payload);os.replace(tmp,pending)
 print('Revision staged:',new,'for',meta['name']);print('Keep this car in View Car. The private engine will reload it when ready.');return report
def stage(package,visual_zip=None):
 expected='Z:'+str(R/'runtime/azimuth.exe').replace('/',chr(92))
 try:rows=subprocess.check_output(['ps','-axo','comm='],text=True)
 except (OSError,subprocess.CalledProcessError):raise ValueError('Cannot verify the private renderer process')
 active=any(line.strip().replace(chr(92)*2,chr(92))==expected for line in rows.splitlines())
 if not active:raise ValueError('Open the private renderer and its car view before refreshing')
 log=R/'runtime/FH2_ExtraOptions.log'
 if not log.exists() or 'native UI reload transitions registered' not in log.read_text(errors='replace'):raise ValueError('The running renderer has not enabled visual refresh yet')
 queue=R/'runtime/refresh';queue.mkdir(parents=True,exist_ok=True)
 with (queue/'staging.lock').open('a+b') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('Another revision is being staged; let it finish first')
  try:return _stage(package,visual_zip)
  finally:fcntl.flock(lock,fcntl.LOCK_UN)

def read_ack():
 p=R/'runtime/refresh/ack.bin'
 if not p.exists():return None
 data=p.read_bytes()
 if len(data)!=ACK.size:return None
 magic,version,serial,code,car,media=ACK.unpack(data)
 if magic!=b'FH2ACK1\0' or version!=1:return None
 return dict(serial=serial,code=code,car_id=car,media=media.rstrip(b'\0').decode('ascii'),meaning={1:'New archive mounted; MediaName updated',2:'Native reload requested',3:'New car-view instance initialized; verify visible changes',10:'Rejected: car/mod/session limit',11:'Database update failed or rolled back',12:'Fresh archive mount failed',13:'Invalid request'}.get(code,'Unknown result'))
def main():
 a=argparse.ArgumentParser();a.add_argument('--package',type=Path);a.add_argument('--visual-zip',type=Path);a.add_argument('--status',action='store_true');a.add_argument('--configured',action='store_true');x=a.parse_args()
 try:
  if x.status:print(json.dumps(read_ack(),indent=2))
  elif x.configured:stage(Path(json.loads((R/'refresh-target.json').read_text())['package']))
  elif x.package:stage(x.package,x.visual_zip)
  else:a.error('Choose --package or --status')
 except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:raise SystemExit('Refresh not staged: '+str(e))
if __name__=='__main__':main()
