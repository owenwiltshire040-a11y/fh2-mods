"""Opel Astra G — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='OPE_daily06_2001__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['te316536e']=(Image.open(os.path.join(HERE,'textures','te316536e.png')),512,False)
TEXTURES['t97912524']=(Image.open(os.path.join(HERE,'textures','t97912524.png')),512,False)
TEXTURES['tc8497a2b']=(Image.open(os.path.join(HERE,'textures','tc8497a2b.png')),512,False)
TEXTURES['t9012c45d']=(Image.open(os.path.join(HERE,'textures','t9012c45d.png')),512,False)
TEXTURES['tcfa582c0']=(Image.open(os.path.join(HERE,'textures','tcfa582c0.png')),512,False)
TEXTURES['tc03e9099']=(Image.open(os.path.join(HERE,'textures','tc03e9099.png')),512,False)
MATERIALS={'material_8': ('textured', 'te316536e'), 'material': ('textured', 't97912524'), 'chrome': ('plain', 'chrome'), 'body': ('plain', 'paint'), 'black_m': ('textured', 'tc8497a2b'), 'plate': ('textured', 't9012c45d'), 'interior': ('textured', 'tcfa582c0'), 'glass': ('plain', 'glass'), 'bottom': ('textured', 'tc03e9099')}
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
STEER=(-0.34, 0.5721632869932309, 0.4)
HIPS=(-0.34, 0.28637391367639564, -0.05)
EYE=(-0.34, 0.9933265739864618, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (304, '_&857996988'), 'depends': 'owen-daily05'}
PHYSICS={'car_id': 5006, 'make_offset': 105, 'make': 'Opel', 'make_profile': 'Opel', 'make_code': 'OPE', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65215, 'colour_offset': 2000, 'name': 'Astra G', 'short_name': 'Astra G', 'engine': {'name': '1.6L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1598, 'peak_hp': 99, 'peak_nm': 150, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 45.0), (1000, 75.0), (2000, 120.0), (3500, 150), (4500, 142.5), (5500, 128.17637115998264), (6000, 117.49500689665072), (6500, 82.5)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 250}, 'body': {'mass': 1120, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.7822463565695639, 1.5093077676107325, 4.07763449293148), 'height': 1.5093077676107325, 'length': 4.07763449293148, 'width': 1.7822463565695639, 'wheelbase': 2.606, 'model_wheelbase': 2.606, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.8911231782847819, 0.8911231782847819, -0.1483675457033147, 1.3609402219074178, -1.897031647438423, 2.1806028454930577)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 15, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (53.24734020618556, 3.8106556701030927, 5.716041237113402), 'rear': (34.04338144329897, 2.4364041237113403, 3.6545484536082466), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2001, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['body']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.21589999999999998
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 205, 'width_rear': 205, 'aspect_front': 40, 'aspect_rear': 40, 'rim_in': 17, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
