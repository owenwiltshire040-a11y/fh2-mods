"""Package finalizer for the Porsche 919 (Claude 7 Nov): native livery decals (livery_decals.py), then the source
Michelin sidewall on the car's own library tyre (tyre_lettering.py), then the high-speed wheel face (speed_rims.py),
then the driver animations' steering-wheel track (cockpit.py), then the live wheel screen (screen.py).   python3 cars/porsche919/finish.py PKG_DIR"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import livery_decals,tyre_lettering,speed_rims,cockpit,screen
pkg=Path(sys.argv[1]);livery_decals.apply(pkg);tyre_lettering.apply(pkg);speed_rims.apply(pkg);cockpit.apply(pkg);screen.apply(pkg)
