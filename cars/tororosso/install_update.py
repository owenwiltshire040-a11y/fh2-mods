"""Install the reviewed candidate only after every Azimuth session is closed."""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys,os,datetime,uuid
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SOURCE=ROOT/'output/Toro Rosso STR1';GAME=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows');TARGET=GAME/'mods/Toro Rosso STR1'
def hashes(folder):return {str(f.relative_to(folder)):hashlib.sha256(f.read_bytes()).hexdigest() for f in folder.rglob('*') if f.is_file()}
def validate():
 if (P/'build/quarantined.json').exists():raise SystemExit('Toro update 0.7.0 is quarantined after a startup freeze. Keep the restored 0.6.2 version; this installer is disabled until the update is fixed.')
 expected=json.loads((P/'build/package-checksums.json').read_text());actual=hashes(SOURCE)
 if actual!=expected:raise SystemExit('The staged package changed after validation. Revalidate it before installing.')
 baseline=json.loads((P/'input/installed-baseline.json').read_text())
 if hashes(TARGET)!=baseline:raise SystemExit('The installed Toro has changed since this update was prepared. Nothing was replaced.')
 dep=GAME/'mods/Williams FW24/mod.json'
 if not dep.is_file() or json.loads(dep.read_text())['id']!='zs-williams-fw24':raise SystemExit('The Williams FW24 sound dependency is missing.')
 order=(GAME/'mods/loadorder.txt').read_text();enabled=[line.strip() for line in order.splitlines() if line.strip() and not line.lstrip().startswith('#')]
 if not all(n in enabled for n in ['Williams FW24','Toro Rosso STR1']):raise SystemExit('Enable Williams FW24 and Toro Rosso STR1 in the existing load order first.')
 if enabled.index('Williams FW24')>enabled.index('Toro Rosso STR1'):raise SystemExit('Move Williams FW24 before Toro Rosso STR1 in loadorder.txt so the sound dependency loads first.')
 return expected
def running():
 text=subprocess.check_output(['ps','-axo','comm='],text=True)
 return any(line.strip().lower().replace('\\','/').endswith('/azimuth.exe') for line in text.splitlines())
def main():
 expected=validate();active=running()
 if '--check' in sys.argv:
  print('Package and installed baseline verified. '+('Azimuth is still open: close it before installation.' if active else 'Azimuth is closed; installation is ready.'));return
 if active:raise SystemExit('Close the game and the private viewer first, then run this installer again. Nothing was changed.')
 stage=TARGET.parent/('.toro-update-'+uuid.uuid4().hex);backup=GAME/'mod-backups'/('Toro Rosso STR1 '+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
 def clone(a,b):
  subprocess.run(['/bin/cp','-c',a,b],check=True);return b
 try:
  shutil.copytree(SOURCE,stage,copy_function=clone)
  if hashes(stage)!=expected:raise RuntimeError('The staged copy did not verify')
  if running():raise RuntimeError('Azimuth started during preparation; installation cancelled')
  # Validate again immediately before swapping the folder.
  validate();backup.parent.mkdir(parents=True,exist_ok=True);os.rename(TARGET,backup)
  try:os.rename(stage,TARGET)
  except BaseException:os.rename(backup,TARGET);raise
  if hashes(TARGET)!=expected:
   failed=TARGET.with_name('.toro-unverified-'+uuid.uuid4().hex);os.rename(TARGET,failed);os.rename(backup,TARGET);raise RuntimeError('Verification failed; the previous version was restored')
  print('Toro Rosso STR1 0.7.0 installed and verified. You can now restart Azimuth.');print('Previous version:',backup)
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':main()
