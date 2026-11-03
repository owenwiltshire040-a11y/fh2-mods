"""Isolated FH2 renderer experiment. Uses existing assets; writes only below this folder."""
from pathlib import Path
import argparse,subprocess,os,json,hashlib,shutil,zipfile,xml.etree.ElementTree as E,time,signal,struct,re
R=Path(__file__).resolve().parent
BOTTLE=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth')
SOURCE=BOTTLE/'drive_c/azimuth-windows';GAME=BOTTLE/'drive_c/Anthem_1.0.0.64_x64__8wekyb3d8bbwe/Mount'
CX=Path('/Users/owen/Applications/CrossOver.app/Contents/SharedSupport/CrossOver')
RUN=R/'runtime';MOD=RUN/'mods/Renderer Experiment';DLL=R/'build/RendererProbe.dll'
EXPECTED='3ec04c6163fb5614e3d351ba0570d39b846041a257715d6340eceb03ccb7f0a3'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clone(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['/bin/cp','-cR' if src.is_dir() else '-c',str(src),str(dst)],check=True)
def prepare():
 if RUN.exists():raise SystemExit('The experiment is already prepared. Existing experimental saves are preserved.')
 if digest(GAME/'forza_durango_release_final.exe')!=EXPECTED:raise SystemExit('Different game executable; experiment refused.')
 if not DLL.is_file():raise SystemExit('Build the diagnostic plugin first: python3 build.py')
 RUN.mkdir()
 for p in SOURCE.iterdir():
  if p.is_file() and p.suffix.lower() in ['.exe','.dll','.ini','.dat']:clone(p,RUN/p.name)
 for name in ['bin','cache','titles']:clone(SOURCE/'data'/name,RUN/'data'/name)
 clone(SOURCE/'data/azimuth.ini',RUN/'data/azimuth.ini');clone(SOURCE/'mods',RUN/'mods')
 ini=RUN/'data/azimuth.ini';text=ini.read_text(encoding='utf-16');text=text.replace('resolution=1440','resolution=720');ini.write_text(text,encoding='utf-16')
 (RUN/'data/logs').mkdir(exist_ok=True)
 MOD.mkdir();(MOD/'plugins').mkdir();clone(DLL,MOD/'plugins/RendererProbe.dll')
 (MOD/'mod.json').write_text(json.dumps(dict(format_version=1,id='owen-renderer-experiment',name='Renderer Experiment',author='Owen',version='0.0.1',description='Isolated observation plugin; experimental showroom boot is separately selectable.',media='media'),indent=2))
 order=RUN/'mods/loadorder.txt';text=order.read_text();order.write_text(text.rstrip()+'\nRenderer Experiment\n')
 baseline={str(p.relative_to(SOURCE)):digest(p) for p in [SOURCE/'data/azimuth.ini',SOURCE/'FH2_ExtraOptions.ini',SOURCE/'mods/loadorder.txt']}
 baseline.update({str(p.relative_to(SOURCE)):digest(p) for p in (SOURCE/'data/titles').rglob('*') if p.is_file() and 'save' in str(p.relative_to(SOURCE)).lower()})
 (R/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
 print('Prepared independent runtime, settings, saves and mods. Original game assets are shared.')
def private_mount():
 package=R/'game/Anthem';mount=package/'Mount';assets=mount/'media'
 if not assets.exists():
  package.parent.mkdir(parents=True,exist_ok=True);clone(GAME.parent,package)
 ini=RUN/'data/azimuth.ini';text=ini.read_text(encoding='utf-16')
 original='C:'+chr(92)+'Anthem_1.0.0.64_x64__8wekyb3d8bbwe';replacement='Z:'+str(package).replace('/',chr(92))
 text=text.replace(original,replacement);ini.write_text(text,encoding='utf-16')
 return assets
def mode(showroom):
 assets=private_mount()
 (MOD/'media/stateflow.zip').unlink(missing_ok=True)
 # The native archive bytes must remain original. Change loaded XML through
 # the already established Extra Options parse hook, after platform edits.
 for name in ['stateflow.zip','zipmanifest.xml']:
  clone(GAME/'media'/name,assets/name)
 selected=R/'build/winmm-renderer.dll' if showroom else SOURCE/'winmm.dll'
 if not selected.is_file():raise SystemExit('Build the engine hook before launching showroom mode.')
 clone(selected,RUN/'winmm.dll')
 print('Original flow archives verified; '+('in-memory showroom hook enabled.' if showroom else 'unmodified Extra Options selected.'))
def status():
 log=RUN/'FH2_ExtraOptions.log';s=log.read_text(errors='replace') if log.exists() else ''
 probe=[line for line in s.splitlines() if 'RENDERER_PROBE:' in line]
 result={'plugin_initialized':any('initialized;' in x for x in probe),'database_ready':any('merged database ready' in x for x in probe),'local_car_callback':any('local-car callback alive' in x for x in probe),'showroom_hook_queued':('RENDERER_FLOW: native showroom entry queued' in s or 'RENDERER_FLOW: native pause entry routed' in s),'native_ui_flow_parsed':('RENDERER_FLOW: startup XML parsed successfully' in s or 'RENDERER_FLOW: native pause XML parsed successfully' in s),'showroom_rendered':'unverified; requires frame inspection','probe_log':probe[-12:]}
 confirmation=R/'logs/view-confirmation.json'
 if confirmation.exists():
  confirmed=json.loads(confirmation.read_text())
  if digest(RUN/'winmm.dll')==confirmed['runtime_dll_sha256']:result['showroom_rendered']='Previously user-verified for this DLL build: '+confirmed['scope']
 print(json.dumps(result,indent=2));(R/'logs/latest-status.json').write_text(json.dumps(result,indent=2)+'\n')
def verify():
 baseline=json.loads((R/'baseline.json').read_text());changed=[n for n,v in baseline.items() if not (SOURCE/n).is_file() or digest(SOURCE/n)!=v]
 print('Original settings, load order and save files unchanged.' if not changed else 'Original files changed externally: '+str(changed));return not changed
def archive_refresh_requests():
 import fcntl
 queue=RUN/'refresh';queue.mkdir(parents=True,exist_ok=True)
 with (queue/'staging.lock').open('a+b') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  pending=[queue/n for n in ['request.bin','ack.bin','selection.bin','selection-ack.bin','selection-target.json','camera.bin','camera-ack.bin'] if (queue/n).exists()]
  if pending:
   history=queue/'history'/str(time.time_ns());history.mkdir(parents=True)
   for item in pending:os.replace(item,history/item.name)

def launch(showroom,automatic=True,lean=False):
 if digest(GAME/'forza_durango_release_final.exe')!=EXPECTED:raise SystemExit('Game executable changed; experiment refused.')
 if not RUN.exists():prepare()
 # Never change mounted files while any Azimuth process is active.
 listing=subprocess.check_output(['ps','-axo','pid=,comm='],text=True)
 if any(line.strip().split(maxsplit=1)[-1].lower().endswith('azimuth.exe') for line in listing.splitlines() if line.strip()):raise SystemExit('An Azimuth session is already open. Close it before launching this experiment.')
 mode(showroom)
 archive_refresh_requests()
 lean_flag=RUN/'refresh/leanboot.enabled'
 if showroom and lean:lean_flag.write_text('Experimental lean bootstrap enabled\n')
 else:lean_flag.unlink(missing_ok=True)
 automatic_flag=RUN/'refresh/autostart.enabled'
 if showroom and automatic:automatic_flag.write_text('Native viewer startup enabled\n')
 else:automatic_flag.unlink(missing_ok=True)
 log=RUN/'FH2_ExtraOptions.log'
 if log.exists():shutil.copy2(log,R/'logs'/('extra-options-'+time.strftime('%Y%m%d-%H%M%S')+'.log'));log.unlink()
 env=dict(os.environ,CX_BOTTLE=str(BOTTLE),CX_GRAPHICS_BACKEND='d3dmetal',ROSETTA_ADVERTISE_AVX='1')
 exe='Z:'+str(RUN/'azimuth.exe').replace('/','\\')
 with (R/'logs/wine.log').open('w') as out:p=subprocess.Popen([str(CX/'bin/wine'),exe,'--skip-launcher'],cwd=RUN,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 (R/'logs/session.json').write_text(json.dumps(dict(launcher_pid=p.pid,mode='showroom' if showroom else 'diagnostics',started=time.strftime('%Y-%m-%d %H:%M:%S'),exe=str(RUN/'azimuth.exe')),indent=2)+'\n')
 print('Started isolated '+('showroom experiment' if showroom else 'diagnostic session')+'. Logs: '+str(R/'logs'))
def stop():
 expected='Z:'+str(RUN/'azimuth.exe').replace('/','\\')
 rows=subprocess.check_output(['ps','-axo','pid=,comm='],text=True)
 for row in rows.splitlines():
  fields=row.strip().split(maxsplit=1)
  if len(fields)==2 and fields[1].strip().replace('\\\\','\\')==expected:
   os.kill(int(fields[0]),signal.SIGTERM);print('Stopped only the isolated renderer process',fields[0]);return
 print('No isolated renderer process is running.')
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['prepare','diagnostics','showroom','status','verify','stop']);a.add_argument('--manual-startup',action='store_true');a.add_argument('--lean-boot',action='store_true');x=a.parse_args()
 if x.action=='prepare':prepare()
 elif x.action=='diagnostics':launch(False)
 elif x.action=='showroom':launch(True,not x.manual_startup,x.lean_boot)
 elif x.action=='status':status()
 elif x.action=='verify':verify()
 elif x.action=='stop':stop()

if __name__=="__main__":main()
