"""Loopback-only car browser for the private engine viewer."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
import hashlib,json,mimetypes,os,secrets,subprocess,sys,threading,time
import catalog,renderer,refresh,capture
R=Path(__file__).resolve().parent;TOKEN=secrets.token_urlsafe(32);lock=threading.Lock();operation='';message='';catalog_cache=(0,[])
def cars():
 global catalog_cache
 if time.monotonic()-catalog_cache[0]>3:catalog_cache=(time.monotonic(),catalog.scan())
 return catalog_cache[1]
def running():
 expected='Z:'+str(renderer.RUN/'azimuth.exe').replace('/',chr(92))
 try:rows=subprocess.check_output(['ps','-axo','comm='],text=True)
 except (OSError,subprocess.CalledProcessError):return False
 return any(l.strip().replace(chr(92)*2,chr(92))==expected for l in rows.splitlines())
def state():
 active=running();log=(renderer.RUN/'FH2_ExtraOptions.log');text=log.read_text(errors='replace') if active and log.exists() else ''
 available='RENDERER_CATALOG: native Autoshow XML parsed successfully' in text
 target=catalog.load_json(renderer.RUN/'refresh/selection-target.json',{}) or {};ack=catalog.read_ack();result=refresh.read_ack()
 automatic=active and (renderer.RUN/'refresh/autostart.enabled').exists()
 help_text='Continue at the title screen, then press Pause once in the viewer. Car choices here will open automatically.'
 if automatic and 'automatic startup timed out' not in text:
  help_text='The private viewer is opening your car automatically.'
  if (renderer.RUN/'refresh/leanboot.enabled').exists():help_text='The private viewer is opening your car with faster preview startup.'
 if 'native viewer reached automatically' in text:help_text='Choose another car here to switch without restarting the viewer.'
 return {'engine':('ready' if available else 'starting') if active else 'closed','browser_ready':available,'selection':ack,'target':target,'refresh':result,'operation':operation,'message':message,'automatic_startup':automatic,'help':help_text,'latest_capture_id':next((c['id'] for c in capture.recent()),None)}
def start(force=False):
 global catalog_cache
 if running():
  if not force and renderer.digest(renderer.RUN/'winmm.dll')==renderer.digest(R/'build/winmm-renderer.dll'):return
  renderer.stop();until=time.monotonic()+12
  while running() and time.monotonic()<until:time.sleep(.2)
  if running():raise ValueError('Close the private viewer window, then try again')
 catalog.sync_builds()
 catalog_cache=(0,[])
 renderer.launch(True,lean=True)
def public_car(c):
 thumb=Path(c['thumbnail']) if c['thumbnail'] else None;stamp=thumb.stat().st_mtime_ns if thumb and thumb.is_file() else 0
 return {k:c[k] for k in ['id','name','package_name','year','version']}|{'thumbnail':'/thumb/'+c['id']+'?v='+str(stamp),'restart_required':not c['installed'] or c['needs_restart'],'editable':any((p.parent/'media/cars'/(c['media']+'.zip')).exists() for p in (R.parent/'Passat B3 Build/output').glob('**/mod.json') if (catalog.load_json(p,{}) or {}).get('id')==c['mod_id'])}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def respond(self,data,status=200,kind='application/json'):
  raw=json.dumps(data).encode() if kind=='application/json' else data
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store' if kind!='image/png' else 'public, max-age=3600');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'");self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if self.headers.get('Host') not in ['127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port)]:return self.respond({'error':'Invalid host'},403)
  path=urlsplit(self.path).path
  if path=='/':return self.respond((R/'ui/index.html').read_bytes(),kind='text/html; charset=utf-8')
  if path=='/app.js':return self.respond((R/'ui/app.js').read_bytes(),kind='text/javascript; charset=utf-8')
  if path=='/style.css':return self.respond((R/'ui/style.css').read_bytes(),kind='text/css; charset=utf-8')
  if path=='/api/identity':return self.respond({'root':str(R)})
  if path=='/api/session':return self.respond({'token':TOKEN})
  if path=='/api/cars':return self.respond({'cars':[public_car(c) for c in cars()]})
  if path=='/api/state':return self.respond(state())
  if path=='/api/captures':return self.respond({'captures':capture.recent()})
  if path.startswith('/capture/'):
   parts=path.split('/')
   file=capture.image_path(parts[2],parts[3]) if len(parts)==4 else None
   if file:return self.respond(file.read_bytes(),kind='image/png')
   return self.respond({'error':'Capture not found'},404)
  if path.startswith('/thumb/'):
   key=path.removeprefix('/thumb/');entry=next((c for c in cars() if c['id']==key),None)
   if entry and entry['thumbnail'] and Path(entry['thumbnail']).is_file():return self.respond(Path(entry['thumbnail']).read_bytes(),kind='image/png')
   return self.respond((R/'ui/car.svg').read_bytes(),kind='image/svg+xml')
  self.respond({'error':'Not found'},404)
 def do_POST(self):
  global operation,message
  if self.headers.get('Host') not in ['127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port)]:return self.respond({'error':'Invalid host'},403)
  # A page from another origin cannot read the session token or authorize writes.
  if self.headers.get('X-Renderer-Token')!=TOKEN:return self.respond({'error':'Invalid session'},403)
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=4096:raise ValueError('Invalid request size')
   body=json.loads(self.rfile.read(size))
   if not isinstance(body,dict):raise ValueError('Invalid request')
   path=urlsplit(self.path).path
   if not lock.acquire(blocking=False):raise ValueError('The viewer is already handling another action')
   try:
    operation='Working';message=''
    if path=='/api/start':start();result={'message':'Viewer started. Automatic preview startup is enabled.'}
    elif path=='/api/select':
     selected=next((c for c in cars() if c['id']==str(body.get('id',''))),None)
     if not selected:raise ValueError('Choose an installed mod car')
     if not running() or not selected['installed'] or selected['needs_restart'] or renderer.digest(renderer.RUN/'winmm.dll')!=renderer.digest(R/'build/winmm-renderer.dll'):start(force=True)
     current=catalog.read_ack()
     if current and current['code'] in [1,2,3]:raise ValueError('The previous car is still opening')
     result=catalog.select(str(body.get('id','')))
    elif path=='/api/refresh':
     target=catalog.load_json(R/'refresh-target.json',{}) or {}
     current=catalog.read_ack()
     if current and current['code'] in [1,2,3]:raise ValueError('Wait until the selected car has opened')
     result=refresh.stage(Path(target['package']))
    elif path=='/api/capture':
     operation='Capturing inspection';result=capture.inspection()|{'message':'Inspection captured'}
    elif path=='/api/capture-current':result=capture.current()|{'message':'Current view captured'}
    elif path=='/api/stop':renderer.stop();result={'message':'Viewer closed'}
    else:raise ValueError('Unknown action')
    message=result.get('message','Revision staged');self.respond(result)
   finally:operation='';lock.release()
  except (ValueError,KeyError,OSError,subprocess.CalledProcessError,SystemExit) as error:message=str(error);self.respond({'error':str(error)},400)
def main():
 port=int(sys.argv[sys.argv.index('--port')+1]) if '--port' in sys.argv else 0
 server=ThreadingHTTPServer(('127.0.0.1',port),Handler);url='http://127.0.0.1:'+str(server.server_port)
 (R/'logs/browser-session.json').write_text(json.dumps({'url':url,'pid':os.getpid()},indent=2)+'\n');print(url,flush=True)
 if '--open' in sys.argv:subprocess.Popen(['open',url])
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
