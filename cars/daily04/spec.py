"""Ford Mondeo Mk3 — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='FOR_daily04_2003__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t60aba8a3']=(Image.open(os.path.join(HERE,'textures','t60aba8a3.png')),512,False)
TEXTURES['t58d3765a']=(Image.open(os.path.join(HERE,'textures','t58d3765a.png')),512,False)
TEXTURES['t2608556b']=(Image.open(os.path.join(HERE,'textures','t2608556b.png')),512,False)
TEXTURES['t6b983ea4']=(Image.open(os.path.join(HERE,'textures','t6b983ea4.png')),512,False)
TEXTURES['td38d307e']=(Image.open(os.path.join(HERE,'textures','td38d307e.png')),512,False)
TEXTURES['te7555eeb']=(Image.open(os.path.join(HERE,'textures','te7555eeb.png')),512,False)
TEXTURES['t007595ec']=(Image.open(os.path.join(HERE,'textures','t007595ec.png')),512,False)
TEXTURES['t9cd310dd']=(Image.open(os.path.join(HERE,'textures','t9cd310dd.png')),512,False)
TEXTURES['tbeb40b13']=(Image.open(os.path.join(HERE,'textures','tbeb40b13.png')),512,False)
TEXTURES['t4022b4b2']=(Image.open(os.path.join(HERE,'textures','t4022b4b2.png')),512,False)
TEXTURES['t20c05663']=(Image.open(os.path.join(HERE,'textures','t20c05663.png')),512,False)
TEXTURES['t1f535500']=(Image.open(os.path.join(HERE,'textures','t1f535500.png')),512,False)
MATERIALS={'black.001': ('textured', 't60aba8a3'), 'interior.001': ('textured', 't58d3765a'), 'chrome.001': ('plain', 'chrome'), 'LicPlate_black.001': ('textured', 't2608556b'), 'LicPlate_yellow.001': ('textured', 't6b983ea4'), 'LicPlate_white.001': ('textured', 'td38d307e'), 'LicPlate_blue.001': ('textured', 'te7555eeb'), 'carpaint.001': ('plain', 'paint'), 'mirror.001': ('textured', 't007595ec'), 'windowglass.001': ('plain', 'glass'), 'clearglass.001': ('textured', 't9cd310dd'), 'orangeglass.001': ('textured', 'tbeb40b13'), 'mattemetal.001': ('textured', 't4022b4b2'), 'blue.001': ('textured', 't20c05663'), 'redglass.001': ('textured', 't1f535500')}
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
STEER=(-0.34, 0.6233550707419807, 0.4)
HIPS=(-0.34, 0.30282841559563667, -0.05)
EYE=(-0.34, 1.0957101414839614, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (14, '_&857938260')}
PHYSICS={'car_id': 5004, 'make_offset': 103, 'make': 'Ford', 'make_profile': 'Ford', 'make_code': 'FOR', 'make_country': 2, 'make_icon': 'ARI', 'string_base': 65209, 'colour_offset': 1800, 'name': 'Mondeo Mk3', 'short_name': 'Mondeo Mk3', 'engine': {'name': '2.0L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1999, 'peak_hp': 143, 'peak_nm': 190, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 57.0), (1000, 95.0), (2000, 152.0), (3500, 190), (4500, 180.5), (5500, 171.0), (6000, 152.0), (6500, 104.50000000000001)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 285.0}, 'body': {'mass': 1375, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.9166955634962857, 1.3685932964567562, 4.712111937268412), 'height': 1.3685932964567562, 'length': 4.712111937268412, 'width': 1.9166955634962857, 'wheelbase': 2.754, 'model_wheelbase': 2.754, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.9583477817481428, 0.9583477817481428, -0.016440929751557587, 1.3521523667051987, -2.3141863490379238, 2.397925588230488)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 18, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (65.37061855670102, 4.67826030927835, 7.017461340206185), 'rear': (41.794329896907215, 2.9911211340206183, 4.486610824742267), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2003, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['carpaint.001']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.21589999999999998
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 225, 'width_rear': 225, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 17, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
