from pathlib import Path
import subprocess,socket,shutil,os,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];viewer=ROOT/'scan/viewer';dst=viewer/'_str1_candidate.glb';shutil.copy2(P/'review/candidate.glb',dst)
server=None
with socket.socket() as s:up=s.connect_ex(('127.0.0.1',8765))==0
if not up:
 server=subprocess.Popen([os.sys.executable,'-m','http.server','8765','--bind','127.0.0.1'],cwd=viewer,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 import time;time.sleep(.5)
try:
 for name,views,target in [('exterior',[[5,2.5,6],[-8.5,1.4,0],[4,2,-6]],[0,.35,0]),('cockpit',[[0,.95,.1],[.4,.65,.2],[-.4,.65,.2]],[0,.38,.69])]:
  subprocess.run(['node','shot.js',dst.name,str(P/'review'/f'{name}.png'),json.dumps(views),json.dumps(target)],cwd=viewer,check=True)
finally:
 if server:server.terminate()
 dst.unlink(missing_ok=True)
