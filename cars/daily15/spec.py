"""Citroen Xsara — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='CIT_daily15_2004__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t6716c539']=(Image.open(os.path.join(HERE,'textures','t6716c539.png')),512,False)
TEXTURES['te7ea673d']=(Image.open(os.path.join(HERE,'textures','te7ea673d.png')),512,False)
TEXTURES['t998fe1f1']=(Image.open(os.path.join(HERE,'textures','t998fe1f1.png')),512,False)
TEXTURES['t3a524ced']=(Image.open(os.path.join(HERE,'textures','t3a524ced.png')),512,False)
TEXTURES['te4ea8b36']=(Image.open(os.path.join(HERE,'textures','te4ea8b36.png')),512,False)
TEXTURES['tef5a29f1']=(Image.open(os.path.join(HERE,'textures','tef5a29f1.png')),512,False)
TEXTURES['t44c02fe7']=(Image.open(os.path.join(HERE,'textures','t44c02fe7.png')),512,False)
TEXTURES['tc5ea7155']=(Image.open(os.path.join(HERE,'textures','tc5ea7155.png')),512,False)
TEXTURES['td8d24be0']=(Image.open(os.path.join(HERE,'textures','td8d24be0.png')),512,False)
MATERIALS={'siva': ('textured', 't6716c539'), 'tablice2': ('textured', 'te7ea673d'), 'xsa_glass': ('plain', 'glass'), 'paint': ('plain', 'paint'), 'xsa_main3': ('textured', 't998fe1f1'), 'xsa_lights': ('textured', 't3a524ced'), 'rgba_153_153_153_255': ('textured', 'te4ea8b36'), 'kokp': ('textured', 'tef5a29f1'), 'vehiclelights128': ('textured', 't44c02fe7'), 'u1': ('textured', 'tc5ea7155'), 'xsa_susp': ('textured', 'td8d24be0')}
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
STEER=(-0.34, 0.5487735849056604, 0.4)
HIPS=(-0.34, 0.278855795148248, -0.05)
EYE=(-0.34, 0.9465471698113208, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'logo_text': 'CITROEN', 'icon_base': 'Citroen'}
PHYSICS={'car_id': 5015, 'make_offset': 114, 'make': 'Citroen', 'make_profile': 'Citroen', 'make_code': 'CIT', 'make_country': 4, 'make_icon': 'ARI', 'string_base': 65242, 'colour_offset': 2900, 'name': 'Xsara', 'short_name': 'Xsara', 'engine': {'name': '1.6L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1587, 'peak_hp': 108, 'peak_nm': 147, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 44.1], [1000, 73.5], [2000, 117.60000000000001], [3500, 147], [4500, 139.65], [5500, 132.3], [6000, 117.60000000000001], [6500, 80.85000000000001]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 250}, 'body': {'mass': 1130, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [1.921768063162215, 1.4793266986579585, 4.181078413345743], 'height': 1.4793266986579585, 'length': 4.181078413345743, 'width': 1.921768063162215, 'wheelbase': 2.54, 'model_wheelbase': 2.54, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-0.9608840315811075, 0.9608840315811075, -0.059338897091359144, 1.4199878015665994, -1.9425991043550945, 2.238479308990648]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 14, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [53.722762886597934, 3.8446793814432993, 5.767077319587629], 'rear': [34.347340206185564, 2.458157731958763, 3.687178350515463], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2004, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['paint']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.21589999999999998
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 205, 'width_rear': 205, 'aspect_front': 35, 'aspect_rear': 35, 'rim_in': 17, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
