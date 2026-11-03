"""Open or reuse this renderer's local browser service."""
from pathlib import Path
import json,subprocess,sys,time,urllib.request
R=Path(__file__).resolve().parent

def existing():
 try:
  saved=json.loads((R/'logs/browser-session.json').read_text());url=saved['url']
  if not url.startswith('http://127.0.0.1:') or not url.removeprefix('http://127.0.0.1:').isdigit():return None
  with urllib.request.urlopen(url+'/api/identity',timeout=1) as response:
   if json.load(response).get('root')==str(R):return url
 except (OSError,ValueError,KeyError):pass

def main():
 url=existing()
 if not url:
  with (R/'logs/browser.log').open('a') as out:
   process=subprocess.Popen([sys.executable,str(R/'browser.py')],cwd=R,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(50):
   if process.poll() is not None:raise SystemExit('Car browser could not start. See logs/browser.log.')
   url=existing()
   if url:break
   time.sleep(.1)
 if not url:raise SystemExit('Car browser did not respond. See logs/browser.log.')
 subprocess.run(['open',url],check=True)
 print('Car browser opened. Choose a car to start the private viewer.')
if __name__=='__main__':main()
