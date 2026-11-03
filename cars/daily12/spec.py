"""Volkswagen Polo Mk4 — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='VW_daily12_2003___'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t466bc8ce']=(Image.open(os.path.join(HERE,'textures','t466bc8ce.png')),512,False)
TEXTURES['tcfa582c0']=(Image.open(os.path.join(HERE,'textures','tcfa582c0.png')),512,False)
TEXTURES['tfe709db9']=(Image.open(os.path.join(HERE,'textures','tfe709db9.png')),512,False)
TEXTURES['t658b1748']=(Image.open(os.path.join(HERE,'textures','t658b1748.png')),512,False)
TEXTURES['t907f98ef']=(Image.open(os.path.join(HERE,'textures','t907f98ef.png')),512,False)
TEXTURES['t105cbb12']=(Image.open(os.path.join(HERE,'textures','t105cbb12.png')),512,False)
TEXTURES['t7bb34cc6']=(Image.open(os.path.join(HERE,'textures','t7bb34cc6.png')),512,False)
TEXTURES['t98f74575']=(Image.open(os.path.join(HERE,'textures','t98f74575.png')),512,False)
TEXTURES['te93388d5']=(Image.open(os.path.join(HERE,'textures','te93388d5.png')),512,False)
MATERIALS={'chrome': ('plain', 'chrome'), 'black': ('textured', 't466bc8ce'), 'windowglass': ('plain', 'glass'), 'interior': ('textured', 'tcfa582c0'), 'mirror': ('plain', 'chrome'), 'clearglass': ('textured', 'tfe709db9'), 'orangeglass': ('textured', 't658b1748'), 'redglass': ('textured', 't907f98ef'), 'carpaint': ('plain', 'paint'), 'Material__4': ('textured', 't105cbb12'), 'Material__3': ('textured', 't7bb34cc6'), 'Material__2': ('textured', 't98f74575'), 'Material__1': ('textured', 'te93388d5')}
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
STEER=(-0.34, 0.5988970287099334, 0.4)
HIPS=(-0.34, 0.29496690208533577, -0.05)
EYE=(-0.34, 1.0467940574198669, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (52, '_&857938517')}
PHYSICS={'car_id': 5012, 'make_offset': 111, 'make': 'Volkswagen', 'make_profile': 'Volkswagen', 'make_code': 'VW', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65233, 'colour_offset': 2600, 'name': 'Polo Mk4', 'short_name': 'Polo Mk4', 'engine': {'name': '1.4L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1390, 'peak_hp': 74, 'peak_nm': 126, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 37.8), (1000, 63.0), (2000, 100.80000000000001), (3500, 126), (4500, 119.69999999999999), (5500, 95.80860066503752), (6000, 87.8245506096177), (6500, 69.30000000000001)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 250}, 'body': {'mass': 1050, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (2.054869625408671, 1.630689472770042, 3.9429291278387453), 'height': 1.630689472770042, 'length': 3.9429291278387453, 'width': 2.054869625408671, 'wheelbase': 2.46, 'model_wheelbase': 2.46, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-1.0274348127043356, 1.0274348127043356, 0.05598843979542523, 1.6866779125654672, -1.7870492394177215, 2.1558798884210235)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 17, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (49.91938144329896, 3.5724896907216497, 5.358788659793814), 'rear': (31.915670103092783, 2.2841288659793815, 3.426139175257731), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2003, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['carpaint']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.21589999999999998
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 225, 'width_rear': 225, 'aspect_front': 45, 'aspect_rear': 45, 'rim_in': 17, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
