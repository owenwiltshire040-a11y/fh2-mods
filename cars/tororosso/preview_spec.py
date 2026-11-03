from pathlib import Path
HERE=str(Path(__file__).resolve().parent)
GEO=str(Path(HERE)/'input/source-geometry.pkl')
WHEEL_FIT={'profile':'charger_legacy'}
PHYSICS={'body':{'model_wheelbase':3.05,'wheelbase':3.05,'track_front':1.486,'track_rear':1.422},'tyres':{'width_front':280,'aspect_front':59,'width_rear':340,'aspect_rear':48,'rim_in':13}}
