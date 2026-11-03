"""Ford Fiesta 2002 — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='FOR_daily01_2002__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t9541cf38']=(Image.open(os.path.join(HERE,'textures','t9541cf38.png')),512,False)
TEXTURES['t97912524']=(Image.open(os.path.join(HERE,'textures','t97912524.png')),512,False)
MATERIALS={'primary': ('plain', 'paint'), 'glass': ('plain', 'glass'), 'material_4': ('textured', 't9541cf38'), 'material': ('textured', 't97912524')}
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
STEER=(-0.34, 0.579584288747346, 0.4)
HIPS=(-0.34, 0.2887592356687898, -0.05)
EYE=(-0.34, 1.008168577494692, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (14, '_&857938260')}
PHYSICS={'car_id': 5001, 'make_offset': 100, 'make': 'Ford', 'make_profile': 'Ford', 'make_code': 'FOR', 'make_country': 2, 'make_icon': 'ARI', 'string_base': 65200, 'colour_offset': 1500, 'name': 'Fiesta 2002', 'short_name': 'Fiesta 2002', 'engine': {'name': '1.4L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1388, 'peak_hp': 79, 'peak_nm': 124, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 37.199999999999996), (1000, 62.0), (2000, 99.2), (3500, 124), (4500, 117.8), (5500, 102.28215476402654), (6000, 93.75864186702431), (6500, 68.2)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 250}, 'body': {'mass': 1040, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.9186259436947808, 1.2777720269883515, 3.8865543051636653), 'height': 1.2777720269883515, 'length': 3.8865543051636653, 'width': 1.9186259436947808, 'wheelbase': 2.486, 'model_wheelbase': 2.486, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.9593129718473904, 0.9593129718473904, 0.024506717925210808, 1.3022787449135622, -1.7629356991688918, 2.1236186059947735)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 16, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (49.443958762886595, 3.538465979381443, 5.3077525773195875), 'rear': (31.611711340206185, 2.262375257731959, 3.3935092783505145), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2002, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['primary']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.17779999999999999
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 185, 'width_rear': 185, 'aspect_front': 70, 'aspect_rear': 70, 'rim_in': 14, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
