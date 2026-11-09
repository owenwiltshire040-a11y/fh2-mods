"""Porsche 919 Hybrid 2017, No. 2 Le Mans. Combined-power AWD approximation for FH2."""
import copy,json,runpy
from pathlib import Path
from PIL import Image
import numpy as np
HERE=str(Path(__file__).resolve().parent)
ROOT=Path(HERE).parents[1]
MEDIA='POR_Porsche919_17_'
DONOR_ZIP=f'{HERE}/donor_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
A=json.loads(Path(HERE,'source-analysis.json').read_text())
MATERIALS=A['mapping']
TEXTURES={}
for mat,filename in A['textures'].items():
 key='t'+Path(filename).stem
 if key not in TEXTURES:
  image=Image.open(Path(HERE,'textures',filename)).convert('RGB')
  size=1024 if max(image.size)>=1024 else 512
  TEXTURES[key]=(image,size,False)
TEXTURES['source_rim']=(Image.open(Path(HERE,'textures/source_rim.png')).convert('RGB'),1024,False)
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
ONE_SIDED=True
PRESERVE_UV_SEAMS=True
RIM_MATERIALS=['SOURCE_RIM']
RIM_SOURCE_TEXTURE='source_rim'
RIM_REFERENCE_MATERIALS=['SOURCE_RIM']
RIM_R_REF=.2286
RIM_TRUST_NORMALS=True
REQUIRE_SOURCE_WHEELS=True
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=0.
WHEEL_FIT=dict(profile='charger_rim_face',geometry='open_wheel')
OPEN_WHEEL_RIM_MATERIALS={'F':['RIM_REF_F'],'R':['RIM_REF_R']}
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin','steeringwheel_a.modelbin'}
DRIVER_ANIMS_ZIP=str(ROOT/'output/Renault R26 2006/media/cars/REN_RenaultR26_06_.zip')
STEERING_MATERIALS=A['steering']
o=A['offset']
STEER=(-.156,.622+o[1],.498+o[2])
EYE=(STEER[0],STEER[1]+.235,STEER[2]-.52)
HIPS=(STEER[0],STEER[1]-.28,STEER[2]-.49)
COLLISION_HULL=dict(half_width=.91,floor_y=-.17,materials=A['paint'])
UPGRADE_PROFILE='race_setup.py'
PRESENT=dict(paint='ececec',use_make=(39,'_&857972692'))  # Claude 7 Nov: make 39 is the base game's Porsche; no dependency needed
PHYSICS=copy.deepcopy(runpy.run_path(str(ROOT/'cars/jordanej11/spec.py'))['PHYSICS'])
PHYSICS.update(car_id=4701,make_offset=18,make='Porsche',make_profile='Porsche',make_code='POR',make_country=7,string_base=65370,colour_offset=3300,name='919 Hybrid',short_name='919 Hybrid')
PHYSICS['engine'].update(name='2.0L V4 Turbo Hybrid',sound='POR_919_2017_',mass=110.,config=1,cylinders=1,
 displacement=1995,aspiration=2,boost=1.8,compression=12.,inertia=.07,tank=62.3,
 peak_hp=900.,peak_nm=800.,redline=9000,stall=900.,start=3500.,
 curve=[(0,140),(1000,260),(2000,460),(3500,690),(5000,775),(6500,800),(7500,800),(8000,795),(8500,754),(9000,700)])
PHYSICS['drivetrain'].update(drivetype=3,gears=[3.15,2.35,1.85,1.52,1.28,1.105,.98],final_drive=3.65,  # Claude 9 Nov (step 11): 4.4 hit the 9000 limiter at ~174 mph in 7th; 3.65 -> ~209 mph (Le Mans ~210)
 
 shift_time=.05,clutch_nm=1400.,lsd=(350.,150.,1250.,500.))
PHYSICS['body'].update(mass=875.,weight_front=.44,cm_height=.30,block=(1.9,1.05,4.65),height=1.05,length=4.65,width=1.9,
 wheelbase=A['wheelbase'],model_wheelbase=A['wheelbase'],track_front='auto',track_rear='auto',ride_height=.1625,
 bbox=(-.967,.967,-.20,1.21,-2.166,2.479))
PHYSICS['tyres'].update(width_front=310,width_rear=310,aspect_front=41,aspect_rear=41,rim_in=18)
PHYSICS['brakes'].update(front_mm=360.,rear_mm=340.,front_pistons=6,rear_pistons=6,friction=1.15)
PHYSICS['suspension'].update(front=(140.,9.,12.),rear=(160.,10.,13.),swaybar_front=65.,swaybar_rear=60.)
PHYSICS['aero_front']=(20.,45.,300.,600.)
PHYSICS['aero_rear']=(35.,80.,600.,1000.)
PHYSICS['car'].update(year=2017,top_mph=210.,t60=2.2,t100=4.3,price=2000000,drag=250.,downforce_front=450.,downforce_rear=800.,wi_force=.85,open_cockpit=0,open_wheel=0)
LIGHTS={'head':dict(mats=['HEAD_EMIT']),'tail':dict(mats=['TAIL_EMIT'])}
EXTRA_MEDIA_FILES={'audio/fmodanthem/durango/PG_POR_919_2017_.bank':str(Path(HERE)/'audio/build/PG_POR_919_2017_.bank')}
PACKAGE_FINALIZER='cars/porsche919/finish.py'   # Claude 7 Nov: native livery decals + source Michelin sidewalls
