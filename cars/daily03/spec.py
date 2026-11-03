"""Ford Focus Mk2 ST — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='FOR_daily03_2006__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t51d98d3e']=(Image.open(os.path.join(HERE,'textures','t51d98d3e.png')),512,False)
TEXTURES['t8f8e8ff5']=(Image.open(os.path.join(HERE,'textures','t8f8e8ff5.png')),512,False)
TEXTURES['tcbb622ab']=(Image.open(os.path.join(HERE,'textures','tcbb622ab.png')),512,False)
TEXTURES['t96d18e7b']=(Image.open(os.path.join(HERE,'textures','t96d18e7b.png')),512,False)
TEXTURES['tca009d90']=(Image.open(os.path.join(HERE,'textures','tca009d90.png')),512,False)
TEXTURES['t6b5e2c52']=(Image.open(os.path.join(HERE,'textures','t6b5e2c52.png')),512,False)
TEXTURES['t4ff8bfc0']=(Image.open(os.path.join(HERE,'textures','t4ff8bfc0.png')),512,False)
MATERIALS={'black_glass': ('textured', 't51d98d3e'), 'Mirror': ('plain', 'chrome'), 'Fphong4SG1': ('textured', 't8f8e8ff5'), 'Paint': ('plain', 'paint'), 'Fphong3SG1': ('textured', 'tcbb622ab'), 'Fphong13SG1': ('textured', 't96d18e7b'), 'Fphong6SG1': ('textured', 'tca009d90'), 'Fphong9SG1': ('textured', 't6b5e2c52'), 'glass': ('plain', 'glass'), 'chrome': ('plain', 'chrome'), 'red_glass': ('textured', 't4ff8bfc0')}
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
STEER=(-0.34, 0.5951904761904762, 0.4)
HIPS=(-0.34, 0.29377551020408166, -0.05)
EYE=(-0.34, 1.0393809523809523, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (14, '_&857938260')}
PHYSICS={'car_id': 5003, 'make_offset': 102, 'make': 'Ford', 'make_profile': 'Ford', 'make_code': 'FOR', 'make_country': 2, 'make_icon': 'ARI', 'string_base': 65206, 'colour_offset': 1700, 'name': 'Focus Mk2 ST', 'short_name': 'Focus Mk2 ST', 'engine': {'name': '2.5L I5 Turbo', 'sound': 'FOR_FocusRS_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 2, 'aspiration': 2, 'boost': 1.0, 'inertia': 0.16, 'tank': 35, 'displacement': 2521, 'peak_hp': 222, 'peak_nm': 320, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 96.0), (1000, 160.0), (2000, 256.0), (3500, 320), (4500, 304.0), (5500, 287.4258019951125), (6000, 256.0), (6500, 176.0)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.231, 1.952, 1.321, 1.029, 0.821, 0.685], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 480.0}, 'body': {'mass': 1362, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.9545418330557542, 1.521010136154969, 4.330002975561957), 'height': 1.521010136154969, 'length': 4.330002975561957, 'width': 1.9545418330557542, 'wheelbase': 2.64, 'model_wheelbase': 2.64, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.9772709165278771, 0.9772709165278771, -0.03401550996088137, 1.4869946261940876, -2.0607633418058375, 2.269239633756119)}, 'tyres': {'width_front': 225, 'width_rear': 225, 'aspect_front': 45, 'aspect_rear': 45, 'rim_in': 17, 'compound': 3}, 'brakes': {'front_mm': 320, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 280, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (64.75256907216493, 4.634029484536082, 6.951114432989691), 'rear': (41.39918350515464, 2.9628414432989687, 4.444191958762886), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2006, 't60': 6.5, 't100': 50.0, 'top_mph': 145.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['Paint']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.2286
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 225, 'width_rear': 225, 'aspect_front': 40, 'aspect_rear': 40, 'rim_in': 18, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
