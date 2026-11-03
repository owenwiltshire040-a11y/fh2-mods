"""Volvo S60R — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='VOL_daily16_2004__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t1b697770']=(Image.open(os.path.join(HERE,'textures','t1b697770.png')),512,False)
TEXTURES['t9367742c']=(Image.open(os.path.join(HERE,'textures','t9367742c.png')),512,False)
TEXTURES['tc98e1aec']=(Image.open(os.path.join(HERE,'textures','tc98e1aec.png')),512,False)
TEXTURES['tc445f5e9']=(Image.open(os.path.join(HERE,'textures','tc445f5e9.png')),512,False)
TEXTURES['t807bf0a6']=(Image.open(os.path.join(HERE,'textures','t807bf0a6.png')),512,False)
TEXTURES['t97434b6f']=(Image.open(os.path.join(HERE,'textures','t97434b6f.png')),512,False)
TEXTURES['tf5aeeacc']=(Image.open(os.path.join(HERE,'textures','tf5aeeacc.png')),512,False)
TEXTURES['t19a1012d']=(Image.open(os.path.join(HERE,'textures','t19a1012d.png')),512,False)
TEXTURES['tc0cfe5b6']=(Image.open(os.path.join(HERE,'textures','tc0cfe5b6.png')),512,False)
TEXTURES['t44c02fe7']=(Image.open(os.path.join(HERE,'textures','t44c02fe7.png')),512,False)
TEXTURES['t0cec1b8a']=(Image.open(os.path.join(HERE,'textures','t0cec1b8a.png')),512,False)
TEXTURES['tc13383ad']=(Image.open(os.path.join(HERE,'textures','tc13383ad.png')),512,False)
MATERIALS={'emzone_stiklai': ('textured', 't1b697770'), 'lights': ('textured', 't9367742c'), 'emzone_aliumas': ('textured', 'tc98e1aec'), 'nodamage': ('textured', 'tc445f5e9'), 'interior_lod0': ('textured', 't807bf0a6'), 'emzone_plasmase': ('textured', 't97434b6f'), 'paint': ('plain', 'paint'), 'rgba_204_204_204_255': ('textured', 'tf5aeeacc'), 'numeriu_bg': ('textured', 't19a1012d'), 'carplate': ('textured', 'tc0cfe5b6'), 'vehiclelights128': ('textured', 't44c02fe7'), 'emzone_detales': ('textured', 't0cec1b8a'), 'emzone_juoda': ('textured', 'tc13383ad')}
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
STEER=(-0.34, 0.6046677419354838, 0.4)
HIPS=(-0.34, 0.2968217741935484, -0.05)
EYE=(-0.34, 1.0583354838709675, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (53, '_&857938645')}
PHYSICS={'car_id': 5016, 'make_offset': 115, 'make': 'Volvo', 'make_profile': 'Volvo', 'make_code': 'VOL', 'make_country': 11, 'make_icon': 'ARI', 'string_base': 65245, 'colour_offset': 3000, 'name': 'S60R', 'short_name': 'S60R', 'engine': {'name': '2.5L I5 Turbo', 'sound': 'FOR_FocusRS_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 2, 'aspiration': 2, 'boost': 1.0, 'inertia': 0.16, 'tank': 35, 'displacement': 2521, 'peak_hp': 296, 'peak_nm': 400, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 120.0], [1000, 200.0], [2000, 320.0], [3500, 400], [4500, 380.0], [5500, 360.0], [6000, 320.0], [6500, 220.00000000000003]]}, 'drivetrain': {'drivetype': 3, 'mounting': 2, 'shift_system': 1, 'gears': [3.231, 1.952, 1.321, 1.029, 0.821, 0.685], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.1, 0.05, 0.1, 0.05], 'clutch_nm': 600.0}, 'body': {'mass': 1620, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [2.0660975506228785, 1.3444054709326836, 4.659849244548428], 'height': 1.3444054709326836, 'length': 4.659849244548428, 'width': 2.0660975506228785, 'wheelbase': 2.715, 'model_wheelbase': 2.715, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-1.0330487753114392, 1.0330487753114392, -0.13612220225795624, 1.2082832686747274, -2.3232617669659272, 2.336587477582501]}, 'tyres': {'width_front': 225, 'width_rear': 225, 'aspect_front': 50, 'aspect_rear': 50, 'rim_in': 17, 'compound': 3}, 'brakes': {'front_mm': 320, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 280, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [77.01847422680412, 5.511841237113401, 8.267845360824742], 'rear': [49.241319587628865, 3.524084536082474, 5.286043298969071], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2004, 't60': 6.5, 't100': 50.0, 'top_mph': 145.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['paint']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.2286
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 235, 'width_rear': 235, 'aspect_front': 40, 'aspect_rear': 40, 'rim_in': 18, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
