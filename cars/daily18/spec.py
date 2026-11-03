"""Fiat Punto Mk2 — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='FIA_daily18_2002__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['te4ea8b36']=(Image.open(os.path.join(HERE,'textures','te4ea8b36.png')),512,False)
TEXTURES['taba15e9b']=(Image.open(os.path.join(HERE,'textures','taba15e9b.png')),512,False)
TEXTURES['t9a343f4e']=(Image.open(os.path.join(HERE,'textures','t9a343f4e.png')),512,False)
TEXTURES['ta94d315f']=(Image.open(os.path.join(HERE,'textures','ta94d315f.png')),512,False)
TEXTURES['t9e32521d']=(Image.open(os.path.join(HERE,'textures','t9e32521d.png')),512,False)
MATERIALS={'rgba_153_153_153_255': ('textured', 'te4ea8b36'), 'rgba_242_242_242_255': ('textured', 'taba15e9b'), 'rgba_0_0_0_255': ('textured', 't9a343f4e'), 'rgba_0_1_0_255': ('textured', 'ta94d315f'), 'car': ('textured', 't9e32521d'), 'rgba_0_57_0_38': ('plain', 'glass'), 'FIT_ARCH': None}
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
STEER=(-0.34, 0.5702589978828511, 0.4)
HIPS=(-0.34, 0.2857618207480593, -0.05)
EYE=(-0.34, 0.9895179957657021, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (57, '_&857938133')}
PHYSICS={'car_id': 5018, 'make_offset': 117, 'make': 'Fiat', 'make_profile': 'Fiat', 'make_code': 'FIA', 'make_country': 8, 'make_icon': 'ARI', 'string_base': 65251, 'colour_offset': 3200, 'name': 'Punto Mk2', 'short_name': 'Punto Mk2', 'engine': {'name': '1.2L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1242, 'peak_hp': 59, 'peak_nm': 102, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 30.599999999999998], [1000, 51.0], [2000, 81.60000000000001], [3500, 102], [4500, 96.89999999999999], [5500, 76.38793836807045], [6000, 70.0222768373979], [6500, 56.1]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 250}, 'body': {'mass': 935, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [1.9055768597184894, 1.4631193400943623, 3.8198739639368373], 'height': 1.4631193400943623, 'length': 3.8198739639368373, 'width': 1.9055768597184894, 'wheelbase': 2.46, 'model_wheelbase': 2.46, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-0.9527884815979272, 0.9527883781205623, 0.00763229095111384, 1.4707516310454762, -1.712918351857428, 2.106955612079409]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 15, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [44.4520206185567, 3.1812170103092785, 4.771873711340206], 'rear': [28.420144329896903, 2.0339623711340207, 3.0508953608247413], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2002, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['rgba_153_153_153_255', 'rgba_242_242_242_255', 'rgba_0_0_0_255', 'rgba_0_1_0_255', 'car']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.17779999999999999
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 185, 'width_rear': 185, 'aspect_front': 65, 'aspect_rear': 65, 'rim_in': 14, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
