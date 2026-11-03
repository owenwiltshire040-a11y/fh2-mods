"""Renault Laguna II — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='REN_daily14_2003__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['tf7f60056']=(Image.open(os.path.join(HERE,'textures','tf7f60056.png')),512,False)
TEXTURES['t5f6bba15']=(Image.open(os.path.join(HERE,'textures','t5f6bba15.png')),512,False)
TEXTURES['t0781c14d']=(Image.open(os.path.join(HERE,'textures','t0781c14d.png')),512,False)
TEXTURES['te95eff38']=(Image.open(os.path.join(HERE,'textures','te95eff38.png')),512,False)
TEXTURES['te68b0723']=(Image.open(os.path.join(HERE,'textures','te68b0723.png')),512,False)
TEXTURES['t15d6c7b6']=(Image.open(os.path.join(HERE,'textures','t15d6c7b6.png')),512,False)
TEXTURES['t7aa840c8']=(Image.open(os.path.join(HERE,'textures','t7aa840c8.png')),512,False)
TEXTURES['tf5aeeacc']=(Image.open(os.path.join(HERE,'textures','tf5aeeacc.png')),512,False)
TEXTURES['td5c09bcb']=(Image.open(os.path.join(HERE,'textures','td5c09bcb.png')),512,False)
TEXTURES['t49dbd890']=(Image.open(os.path.join(HERE,'textures','t49dbd890.png')),512,False)
TEXTURES['t9a72a2ae']=(Image.open(os.path.join(HERE,'textures','t9a72a2ae.png')),512,False)
TEXTURES['t61633002']=(Image.open(os.path.join(HERE,'textures','t61633002.png')),512,False)
TEXTURES['t67ff9a05']=(Image.open(os.path.join(HERE,'textures','t67ff9a05.png')),512,False)
TEXTURES['tb0b60441']=(Image.open(os.path.join(HERE,'textures','tb0b60441.png')),512,False)
TEXTURES['t67b6efc0']=(Image.open(os.path.join(HERE,'textures','t67b6efc0.png')),512,False)
TEXTURES['t741a87da']=(Image.open(os.path.join(HERE,'textures','t741a87da.png')),512,False)
TEXTURES['t594e3584']=(Image.open(os.path.join(HERE,'textures','t594e3584.png')),512,False)
TEXTURES['t8d60fcaa']=(Image.open(os.path.join(HERE,'textures','t8d60fcaa.png')),512,False)
TEXTURES['tb6b6776f']=(Image.open(os.path.join(HERE,'textures','tb6b6776f.png')),512,False)
TEXTURES['td77a9edc']=(Image.open(os.path.join(HERE,'textures','td77a9edc.png')),512,False)
TEXTURES['t4fed93cd']=(Image.open(os.path.join(HERE,'textures','t4fed93cd.png')),512,False)
TEXTURES['te8e636eb']=(Image.open(os.path.join(HERE,'textures','te8e636eb.png')),512,False)
TEXTURES['ta9e9dd7b']=(Image.open(os.path.join(HERE,'textures','ta9e9dd7b.png')),512,False)
TEXTURES['ta3429817']=(Image.open(os.path.join(HERE,'textures','ta3429817.png')),512,False)
TEXTURES['t3224a033']=(Image.open(os.path.join(HERE,'textures','t3224a033.png')),512,False)
TEXTURES['t8c079cbb']=(Image.open(os.path.join(HERE,'textures','t8c079cbb.png')),512,False)
TEXTURES['t44c02fe7']=(Image.open(os.path.join(HERE,'textures','t44c02fe7.png')),512,False)
MATERIALS={'compteurs': ('textured', 'tf7f60056'), 'vitres': ('textured', 't5f6bba15'), 'rgba_30_30_30_255': ('textured', 't0781c14d'), 'rgba_255_253_253_179': ('plain', 'glass'), 'paint': ('plain', 'paint'), 'plastique': ('textured', 'te95eff38'), 'hp': ('textured', 'te68b0723'), 'seattex': ('textured', 't15d6c7b6'), 'interieur': ('textured', 't7aa840c8'), 'rgba_204_204_204_255': ('textured', 'tf5aeeacc'), 'rgba_31_31_31_255': ('textured', 'td5c09bcb'), 'vitres_2': ('textured', 't49dbd890'), 'moteur': ('textured', 't9a72a2ae'), 'rgba_255_255_255_255': ('textured', 't61633002'), 'moquette': ('textured', 't67ff9a05'), 'beige-haut': ('textured', 'tb0b60441'), 'rgba_176_176_176_255': ('textured', 't67b6efc0'), 'exterieur': ('textured', 't741a87da'), 'rgba_35_35_35_255': ('textured', 't594e3584'), 'cuirbv': ('textured', 't8d60fcaa'), 'plastique 2': ('textured', 'tb6b6776f'), 'cuir 2': ('textured', 'td77a9edc'), 'cuir 3': ('textured', 't4fed93cd'), 'rgba_192_192_192_255': ('textured', 'te8e636eb'), 'rgba_255_255_255_179': ('plain', 'glass'), 'plastique3': ('textured', 'ta9e9dd7b'), 'rgba_201_201_201_255': ('textured', 'ta3429817'), 'plaque': ('textured', 't3224a033'), 'vehicleenvmap128': ('textured', 't8c079cbb'), 'vehiclelights128': ('textured', 't44c02fe7')}
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
STEER=(-0.34, 0.5931908629441625, 0.4)
HIPS=(-0.34, 0.2931327773749094, -0.05)
EYE=(-0.34, 1.0353817258883249, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (41, '_&857955285')}
PHYSICS={'car_id': 5014, 'make_offset': 113, 'make': 'Renault', 'make_profile': 'Renault', 'make_code': 'REN', 'make_country': 4, 'make_icon': 'ARI', 'string_base': 65239, 'colour_offset': 2800, 'name': 'Laguna II', 'short_name': 'Laguna II', 'engine': {'name': '2.0L I4 Turbo', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 2, 'boost': 1.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1998, 'peak_hp': 163, 'peak_nm': 270, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 81.0], [1000, 135.0], [2000, 216.0], [3500, 270], [4500, 256.5], [5500, 211.0378636270421], [6000, 193.4513749914552], [6500, 148.5]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.231, 1.952, 1.321, 1.029, 0.821, 0.685], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 405.0}, 'body': {'mass': 1395, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [2.1250917269234386, 1.248302998017193, 4.559202045180644], 'height': 1.248302998017193, 'length': 4.559202045180644, 'width': 2.1250917269234386, 'wheelbase': 2.748, 'model_wheelbase': 2.748, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-1.0625458634617193, 1.0625458634617193, -0.008270371913564167, 1.2400326261036287, -2.153747979178094, 2.4054540660025507]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 17, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [66.32146391752576, 4.746307731958763, 7.119533505154639], 'rear': [42.40224742268041, 3.034628350515464, 4.5518706185567], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2003, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['paint']
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
