from pathlib import Path
import sys,subprocess,json
r=Path(__file__).resolve().parents[1]
for number in map(int,sys.argv[1:]):
 p=r/'cars'/f'daily{number:02}';log=p/'review-build.log'
 with log.open('w') as out:result=subprocess.run([sys.executable,'package_car.py',str(p/'spec.py'),str(r/'output/Daily Drivers')],cwd=r,stdout=out,stderr=subprocess.STDOUT)
 print(number,'rebuilt' if result.returncode==0 else 'FAILED '+log.read_text()[-900:],flush=True)
