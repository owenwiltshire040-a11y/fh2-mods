"""Ford Ka — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='FOR_daily13_2000__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t7cf199b4']=(Image.open(os.path.join(HERE,'textures','t7cf199b4.png')),512,False)
TEXTURES['t150ccb3d']=(Image.open(os.path.join(HERE,'textures','t150ccb3d.png')),512,False)
TEXTURES['t9cadf23a']=(Image.open(os.path.join(HERE,'textures','t9cadf23a.png')),512,False)
TEXTURES['t0b7a6438']=(Image.open(os.path.join(HERE,'textures','t0b7a6438.png')),512,False)
TEXTURES['t86149464']=(Image.open(os.path.join(HERE,'textures','t86149464.png')),512,False)
TEXTURES['t13464f79']=(Image.open(os.path.join(HERE,'textures','t13464f79.png')),512,False)
MATERIALS={'aiStandardSurface1SG': ('plain', 'glass'), 'lambert6SG': ('textured', 't7cf199b4'), 'phong1SG': ('plain', 'paint'), 'lambert2SG': ('plain', 'glass'), 'lambert7SG': ('textured', 't150ccb3d'), 'aiStandardSurface3SG': ('textured', 't9cadf23a'), 'aiStandardSurface6SG': ('textured', 't0b7a6438'), 'initialShadingGroup': ('textured', 't86149464'), 'aiStandardSurface2SG': ('textured', 't13464f79')}
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
STEER=(-0.34, 0.5312366863905325, 0.4)
HIPS=(-0.34, 0.2732189349112426, -0.05)
EYE=(-0.34, 0.911473372781065, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (14, '_&857938260')}
PHYSICS={'car_id': 5013, 'make_offset': 112, 'make': 'Ford', 'make_profile': 'Ford', 'make_code': 'FOR', 'make_country': 2, 'make_icon': 'ARI', 'string_base': 65236, 'colour_offset': 2700, 'name': 'Ka', 'short_name': 'Ka', 'engine': {'name': '1.3L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1299, 'peak_hp': 59, 'peak_nm': 105, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 31.5], [1000, 52.5], [2000, 84.0], [3500, 105], [4500, 99.75], [5500, 76.38793836807045], [6000, 70.0222768373979], [6500, 57.75000000000001]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 250}, 'body': {'mass': 890, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [1.8856175731605864, 1.2508287977607981, 3.621301775147929], 'height': 1.2508287977607981, 'length': 3.621301775147929, 'width': 1.8856175731605864, 'wheelbase': 2.448, 'model_wheelbase': 2.448, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-0.9428087865802931, 0.9428087865802932, -0.12059763313609465, 1.1302311646247034, -1.6225544378698225, 1.9987473372781062]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 13, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [42.312618556701025, 3.0281103092783503, 4.542211340206186], 'rear': [27.052329896907214, 1.9360711340206187, 2.9040608247422672], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2000, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['phong1SG']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.1651
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 13, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
