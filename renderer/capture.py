"""Capture only the verified private renderer window into a local review gallery."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,subprocess,uuid,time,fcntl
import camera
import catalog,renderer,refresh
R=Path(__file__).resolve().parent
class CaptureError(ValueError):pass

def private_pid():
 expected='Z:'+str(renderer.RUN/'azimuth.exe').replace('/',chr(92))
 rows=subprocess.check_output(['ps','-axo','pid=,comm='],text=True)
 matches=[]
 for line in rows.splitlines():
  fields=line.strip().split(maxsplit=1)
  if len(fields)==2 and fields[1].replace(chr(92)*2,chr(92))==expected:matches.append(int(fields[0]))
 if len(matches)!=1:raise CaptureError('Open a car in the private viewer before capturing')
 return matches[0]

def helper(*args):
 try:result=subprocess.run([str(R/'build/Car Studio Capture.app/Contents/MacOS/CapturePreview'),*map(str,args)],capture_output=True,text=True,timeout=25)
 except subprocess.TimeoutExpired:raise CaptureError('The capture helper did not respond. Check for a macOS permission prompt.')
 try:data=json.loads(result.stdout)
 except ValueError:raise CaptureError('The capture helper did not return a valid result: '+result.stderr[:300])
 if result.returncode or 'error' in data:raise CaptureError(data.get('error','Capture failed'))
 return data

def context():
 pid=private_pid();ack=catalog.read_ack();target=catalog.load_json(renderer.RUN/'refresh/selection-target.json',{}) or {}
 if not ack or ack['code']!=4 or ack['serial']!=target.get('serial'):raise CaptureError('Wait until the selected car has opened before capturing')
 revision=refresh.read_ack()
 if revision and revision.get('car_id')==ack.get('car_id') and revision['code'] in [1,2]:raise CaptureError('Wait until the build refresh has finished')
 return {'pid':pid,'selection':ack,'target':target,'revision':revision}

def check_context(expected):
 if private_pid()!=expected['pid'] or catalog.read_ack()!=expected['selection'] or refresh.read_ack()!=expected['revision']:
  raise CaptureError('The viewer, selected car or build changed during capture; please try again')

def permission():
 if not helper('--check').get('screen_capture_allowed',False):raise CaptureError('macOS Screen Recording permission is needed for Car Studio Capture. Use Enable Capture.command once, then capture again.')

def frame(folder,filename,expected,name,pose=None):
 check_context(expected);path=folder/filename;result=helper('--pid',expected['pid'],'--output',path);check_context(expected)
 raw=path.read_bytes()
 if raw[:8]!=b'\x89PNG\r\n\x1a\n':raise CaptureError('The capture is not a valid PNG image')
 return {'name':name,'file':filename,'width':result['width'],'height':result['height'],'sha256':hashlib.sha256(raw).hexdigest(),'camera':pose,'window_id':result['window_id']}

def publish(folder,expected,views,kind):
 report={'id':folder.name,'car':expected['target'].get('name',expected['selection']['media']),'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection':expected['selection'],'visual_revision':expected['revision'],'runtime_dll_sha256':renderer.digest(renderer.RUN/'winmm.dll'),'session':catalog.load_json(R/'logs/session.json',{}),'views':views,'pid':expected['pid'],'kind':kind}
 tmp=folder/'manifest.tmp';tmp.write_text(json.dumps(report,indent=2)+'\n');os.replace(tmp,folder/'manifest.json');return report

def discard(folder):
 # This directory was exclusively created by this capture, never user data.
 for p in folder.iterdir():
  if p.is_file():p.unlink()
 folder.rmdir()

def _current():
 expected=context();permission();pose=camera.command(0,allow_unsupported=True)
 folder=R/'captures'/uuid.uuid4().hex;folder.mkdir(parents=True)
 try:return publish(folder,expected,[frame(folder,'current.png',expected,'Current view',pose)],'Current view')
 except BaseException:discard(folder);raise

def current():
 return locked(_current)

def _inspection():
 expected=context();permission();folder=R/'captures'/uuid.uuid4().hex;folder.mkdir(parents=True);entered=False
 try:
  camera.command(3);entered=True;time.sleep(1);camera.command(0);views=[]
  for name,index in camera.PRESETS.items():
   pose=camera.command(1,index);time.sleep(1)
   views.append(frame(folder,name+'.png',expected,name.replace('-',' ').title(),pose))
  return publish(folder,expected,views,'Exterior inspection')
 except BaseException:discard(folder);raise
 finally:
  if entered:
   try:camera.command(2)
   except (ValueError,OSError):pass

def inspection():
 return locked(_inspection)

def locked(action):
 q=renderer.RUN/'refresh';q.mkdir(parents=True,exist_ok=True)
 with (q/'staging.lock').open('a+b') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise CaptureError('A selection, refresh or capture is in progress')
  try:return action()
  finally:fcntl.flock(lock,fcntl.LOCK_UN)

def recent():
 rows=[]
 for path in (R/'captures').glob('*/manifest.json'):
  data=catalog.load_json(path,{})
  if data and re.fullmatch('[0-9a-f]{32}',path.parent.name):rows.append(data)
 return sorted(rows,key=lambda row:row.get('created',''),reverse=True)[:20]

def image_path(identifier,name):
 if not re.fullmatch('[0-9a-f]{32}',identifier):return None
 folder=R/'captures'/identifier;manifest=catalog.load_json(folder/'manifest.json',{}) or {}
 if name not in [v.get('file') for v in manifest.get('views',[])]:return None
 path=(folder/name).resolve()
 return path if path.is_relative_to(folder.resolve()) and path.is_file() else None

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--list',action='store_true');a.add_argument('--inspection',action='store_true');x=a.parse_args()
 try:print(json.dumps(recent() if x.list else inspection() if x.inspection else current(),indent=2))
 except (CaptureError,OSError,subprocess.CalledProcessError) as error:raise SystemExit(str(error))
