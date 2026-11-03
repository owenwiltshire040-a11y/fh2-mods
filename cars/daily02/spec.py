"""Ford Focus Mk1 — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='FOR_daily02_2001__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['td8169782']=(Image.open(os.path.join(HERE,'textures','td8169782.png')),512,False)
TEXTURES['t466bc8ce']=(Image.open(os.path.join(HERE,'textures','t466bc8ce.png')),512,False)
TEXTURES['td223dbe2']=(Image.open(os.path.join(HERE,'textures','td223dbe2.png')),512,False)
TEXTURES['t422c8a5a']=(Image.open(os.path.join(HERE,'textures','t422c8a5a.png')),512,False)
TEXTURES['t4cecd684']=(Image.open(os.path.join(HERE,'textures','t4cecd684.png')),512,False)
TEXTURES['t557e3c1e']=(Image.open(os.path.join(HERE,'textures','t557e3c1e.png')),512,False)
TEXTURES['t44084217']=(Image.open(os.path.join(HERE,'textures','t44084217.png')),512,False)
TEXTURES['t6f30d6db']=(Image.open(os.path.join(HERE,'textures','t6f30d6db.png')),512,False)
TEXTURES['t302f9b54']=(Image.open(os.path.join(HERE,'textures','t302f9b54.png')),512,False)
TEXTURES['t7e268859']=(Image.open(os.path.join(HERE,'textures','t7e268859.png')),512,False)
TEXTURES['t04cf8409']=(Image.open(os.path.join(HERE,'textures','t04cf8409.png')),512,False)
TEXTURES['t183a349e']=(Image.open(os.path.join(HERE,'textures','t183a349e.png')),512,False)
TEXTURES['ta4665a84']=(Image.open(os.path.join(HERE,'textures','ta4665a84.png')),512,False)
TEXTURES['t7e044c86']=(Image.open(os.path.join(HERE,'textures','t7e044c86.png')),512,False)
TEXTURES['t503d46db']=(Image.open(os.path.join(HERE,'textures','t503d46db.png')),512,False)
TEXTURES['t526f3c57']=(Image.open(os.path.join(HERE,'textures','t526f3c57.png')),512,False)
MATERIALS={'Material': ('textured', 'td8169782'), 'black': ('textured', 't466bc8ce'), 'carbon': ('textured', 'td223dbe2'), 'regray': ('textured', 't422c8a5a'), 'etored': ('textured', 't4cecd684'), 'Rsvet': ('textured', 't557e3c1e'), 'reverselight': ('textured', 't44084217'), 'glass': ('plain', 'glass'), 'chrome': ('plain', 'chrome'), 'signal_FL': ('textured', 't6f30d6db'), 'lowbeam': ('textured', 't302f9b54'), 'highebeam': ('textured', 't7e268859'), 'signal_FR': ('textured', 't04cf8409'), 'body': ('plain', 'paint'), 'zadnia': ('textured', 't183a349e'), 'tblue': ('textured', 'ta4665a84'), 'Leather1': ('textured', 't7e044c86'), 'Buttons': ('textured', 't503d46db'), 'foger': ('textured', 't526f3c57')}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
RIM_MATERIALS=[]
ONE_SIDED=True
PRESERVE_UV_SEAMS=True
RIM_TRUST_NORMALS=True
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=.01
WHEEL_FIT=dict(profile='charger_rim_face')
STEER=(-0.34, 0.5701984732824428, 0.4)
HIPS=(-0.34, 0.28574236641221373, -0.05)
EYE=(-0.34, 0.9893969465648855, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (14, '_&857938260')}
PHYSICS={'car_id': 5002, 'make_offset': 101, 'make': 'Ford', 'make_profile': 'Ford', 'make_code': 'FOR', 'make_country': 2, 'make_icon': 'ARI', 'string_base': 65203, 'colour_offset': 1600, 'name': 'Focus Mk1', 'short_name': 'Focus Mk1', 'engine': {'name': '1.6L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1596, 'peak_hp': 99, 'peak_nm': 145, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 43.5], [1000, 72.5], [2000, 116.0], [3500, 145], [4500, 137.75], [5500, 128.17637115998264], [6000, 116.0], [6500, 79.75]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 250}, 'body': {'mass': 1150, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [2.036645819667641, 1.3326024088070139, 4.256066231327202], 'height': 1.3326024088070139, 'length': 4.256066231327202, 'width': 2.036645819667641, 'wheelbase': 2.615, 'model_wheelbase': 2.615, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-1.0183229098338202, 1.0183229098338207, -0.0015297604364748474, 1.331072648370539, -2.022868369606979, 2.2331978617202233]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 15, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [54.67360824742267, 3.9127268041237113, 5.8691494845360825], 'rear': [34.95525773195877, 2.501664948453608, 3.752438144329896], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2001, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['body']
UPGRADE_PROFILE='upgrade_profile.py'

ARCH_MATERIALS=['Material', 'black', 'carbon', 'regray', 'etored', 'Rsvet', 'reverselight', 'glass', 'chrome', 'signal_FL', 'lowbeam', 'highebeam', 'signal_FR', 'body', 'zadnia', 'tblue', 'Leather1', 'Buttons', 'foger']

MATERIALS['Material']=('plain','paint')

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.21589999999999998
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 205, 'width_rear': 205, 'aspect_front': 40, 'aspect_rear': 40, 'rim_in': 17, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
