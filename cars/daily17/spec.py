"""Volkswagen Passat B5.5 — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='VW_daily17_2003___'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t44c02fe7']=(Image.open(os.path.join(HERE,'textures','t44c02fe7.png')),512,False)
TEXTURES['tbf96a0d5']=(Image.open(os.path.join(HERE,'textures','tbf96a0d5.png')),512,False)
TEXTURES['tc7a5cd3d']=(Image.open(os.path.join(HERE,'textures','tc7a5cd3d.png')),512,False)
TEXTURES['td4a33198']=(Image.open(os.path.join(HERE,'textures','td4a33198.png')),512,False)
TEXTURES['t50a1c0ee']=(Image.open(os.path.join(HERE,'textures','t50a1c0ee.png')),512,False)
TEXTURES['t8aa4b068']=(Image.open(os.path.join(HERE,'textures','t8aa4b068.png')),512,False)
TEXTURES['t61633002']=(Image.open(os.path.join(HERE,'textures','t61633002.png')),512,False)
TEXTURES['tfa805772']=(Image.open(os.path.join(HERE,'textures','tfa805772.png')),512,False)
TEXTURES['tf5aeeacc']=(Image.open(os.path.join(HERE,'textures','tf5aeeacc.png')),512,False)
TEXTURES['t68c1822a']=(Image.open(os.path.join(HERE,'textures','t68c1822a.png')),512,False)
TEXTURES['t8755dcfd']=(Image.open(os.path.join(HERE,'textures','t8755dcfd.png')),512,False)
TEXTURES['tf23dacf3']=(Image.open(os.path.join(HERE,'textures','tf23dacf3.png')),512,False)
TEXTURES['t594e3584']=(Image.open(os.path.join(HERE,'textures','t594e3584.png')),512,False)
TEXTURES['tfd958542']=(Image.open(os.path.join(HERE,'textures','tfd958542.png')),512,False)
TEXTURES['td5c09bcb']=(Image.open(os.path.join(HERE,'textures','td5c09bcb.png')),512,False)
TEXTURES['te4571b3d']=(Image.open(os.path.join(HERE,'textures','te4571b3d.png')),512,False)
TEXTURES['t7788518e']=(Image.open(os.path.join(HERE,'textures','t7788518e.png')),512,False)
TEXTURES['t384ba64e']=(Image.open(os.path.join(HERE,'textures','t384ba64e.png')),512,False)
TEXTURES['tf31869d0']=(Image.open(os.path.join(HERE,'textures','tf31869d0.png')),512,False)
TEXTURES['t9a343f4e']=(Image.open(os.path.join(HERE,'textures','t9a343f4e.png')),512,False)
TEXTURES['tec1c9bf6']=(Image.open(os.path.join(HERE,'textures','tec1c9bf6.png')),512,False)
TEXTURES['tf51d6e28']=(Image.open(os.path.join(HERE,'textures','tf51d6e28.png')),512,False)
TEXTURES['t32405e88']=(Image.open(os.path.join(HERE,'textures','t32405e88.png')),512,False)
TEXTURES['t737c053d']=(Image.open(os.path.join(HERE,'textures','t737c053d.png')),512,False)
TEXTURES['td66e76b0']=(Image.open(os.path.join(HERE,'textures','td66e76b0.png')),512,False)
TEXTURES['tebebd065']=(Image.open(os.path.join(HERE,'textures','tebebd065.png')),512,False)
TEXTURES['t50af7346']=(Image.open(os.path.join(HERE,'textures','t50af7346.png')),512,False)
TEXTURES['td9e83874']=(Image.open(os.path.join(HERE,'textures','td9e83874.png')),512,False)
TEXTURES['t5462bad6']=(Image.open(os.path.join(HERE,'textures','t5462bad6.png')),512,False)
TEXTURES['t58ba90e2']=(Image.open(os.path.join(HERE,'textures','t58ba90e2.png')),512,False)
TEXTURES['tf630b0b9']=(Image.open(os.path.join(HERE,'textures','tf630b0b9.png')),512,False)
TEXTURES['t5e787feb']=(Image.open(os.path.join(HERE,'textures','t5e787feb.png')),512,False)
TEXTURES['t65405b6b']=(Image.open(os.path.join(HERE,'textures','t65405b6b.png')),512,False)
TEXTURES['t5057c321']=(Image.open(os.path.join(HERE,'textures','t5057c321.png')),512,False)
TEXTURES['ta078d5bd']=(Image.open(os.path.join(HERE,'textures','ta078d5bd.png')),512,False)
TEXTURES['tc4795e47']=(Image.open(os.path.join(HERE,'textures','tc4795e47.png')),512,False)
TEXTURES['t8e95410a']=(Image.open(os.path.join(HERE,'textures','t8e95410a.png')),512,False)
TEXTURES['te5660a3f']=(Image.open(os.path.join(HERE,'textures','te5660a3f.png')),512,False)
TEXTURES['taafb5c3f']=(Image.open(os.path.join(HERE,'textures','taafb5c3f.png')),512,False)
TEXTURES['tf3ea7aa0']=(Image.open(os.path.join(HERE,'textures','tf3ea7aa0.png')),512,False)
TEXTURES['t513fc2b4']=(Image.open(os.path.join(HERE,'textures','t513fc2b4.png')),512,False)
TEXTURES['t3406b944']=(Image.open(os.path.join(HERE,'textures','t3406b944.png')),512,False)
TEXTURES['t08d6e930']=(Image.open(os.path.join(HERE,'textures','t08d6e930.png')),512,False)
TEXTURES['t65783b7e']=(Image.open(os.path.join(HERE,'textures','t65783b7e.png')),512,False)
MATERIALS={'vehiclelights128': ('textured', 't44c02fe7'), 'rgba_121_121_121_255': ('textured', 'tbf96a0d5'), 'dnzstop': ('textured', 'tc7a5cd3d'), 'rgba_86_86_86_255': ('textured', 'td4a33198'), 'rgba_255_0_0_255': ('textured', 't50a1c0ee'), 'dnzfar': ('textured', 't8aa4b068'), 'rgba_200_200_200_130': ('plain', 'glass'), 'rgba_255_255_255_164': ('plain', 'glass'), 'rgba_255_255_255_255': ('textured', 't61633002'), 'rgba_115_115_115_255': ('textured', 'tfa805772'), 'rgba_204_204_204_255': ('textured', 'tf5aeeacc'), 'rgba_0_25_20_180': ('plain', 'glass'), 'diffuse': ('textured', 't68c1822a'), 'rgba_64_64_64_255': ('textured', 't8755dcfd'), 'rgba_198_181_151_255': ('textured', 'tf23dacf3'), 'rgba_35_35_35_255': ('textured', 't594e3584'), 'rgba_0_25_92_255': ('textured', 'tfd958542'), 'rgba_31_31_31_255': ('textured', 'td5c09bcb'), 'rgba_149_149_149_255': ('textured', 'te4571b3d'), 'etiketler': ('textured', 't7788518e'), 'rgba_26_26_255_255': ('textured', 't384ba64e'), 'rgba_21_21_21_255': ('textured', 'tf31869d0'), 'rgba_0_0_0_255': ('textured', 't9a343f4e'), 'rgba_188_188_188_255': ('textured', 'tec1c9bf6'), 'rgba_9_9_9_255': ('textured', 'tf51d6e28'), 'motor': ('textured', 't32405e88'), 'rgba_180_180_180_255': ('textured', 't737c053d'), 'crb39': ('textured', 'td66e76b0'), 'rgba_117_117_117_255': ('textured', 'tebebd065'), 'bosch': ('textured', 't50af7346'), 'tr': ('textured', 'td9e83874'), 'rgba_40_40_40_255': ('textured', 't5462bad6'), 'rgba_255_128_0_255': ('textured', 't58ba90e2'), 'bege': ('textured', 'tf630b0b9'), 'rgba_82_82_82_255': ('textured', 't5e787feb'), 'clima2': ('textured', 't65405b6b'), 'hdm_01_spd2': ('textured', 't5057c321'), 'rgba_114_114_114_255': ('textured', 'ta078d5bd'), 'rgba_58_58_58_255': ('textured', 'tc4795e47'), 'rgba_48_119_186_255': ('textured', 't8e95410a'), 'rgba_17_11_21_255': ('textured', 'te5660a3f'), 'rgba_184_178_180_255': ('textured', 'taafb5c3f'), 'rgba_134_133_138_255': ('textured', 'tf3ea7aa0'), 'rgba_18_11_19_255': ('textured', 't513fc2b4'), '411lvcr4': ('textured', 't3406b944'), 'rgba_153_30_30_255': ('textured', 't08d6e930'), 'hdm_01_rev2': ('textured', 't65783b7e'), 'FIT_ARCH': None}
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
STEER=(-0.34, 0.5729791366906475, 0.4)
HIPS=(-0.34, 0.2866361510791367, -0.05)
EYE=(-0.34, 0.9949582733812949, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (52, '_&857938517')}
PHYSICS={'car_id': 5017, 'make_offset': 116, 'make': 'Volkswagen', 'make_profile': 'Volkswagen', 'make_code': 'VW', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65248, 'colour_offset': 3100, 'name': 'Passat B5.5', 'short_name': 'Passat B5.5', 'engine': {'name': '1.8L I4 Turbo', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 2, 'boost': 1.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1781, 'peak_hp': 148, 'peak_nm': 210, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 63.0], [1000, 105.0], [2000, 168.0], [3500, 210], [4500, 199.5], [5500, 189.0], [6000, 168.0], [6500, 115.50000000000001]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 315.0}, 'body': {'mass': 1390, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [1.9818387838888198, 1.7087593576423166, 4.638361765482287], 'height': 1.7087593576423166, 'length': 4.638361765482287, 'width': 1.9818387838888198, 'wheelbase': 2.703, 'model_wheelbase': 2.703, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-0.99091939194441, 0.9909193919444099, -0.16593853118046975, 1.5428208264618468, -2.253059488363996, 2.3853022771182912]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 15, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [66.08375257731959, 4.72929587628866, 7.094015463917525], 'rear': [42.25026804123711, 3.0237515463917526, 4.535555670103092], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2003, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['vehiclelights128', 'rgba_121_121_121_255', 'dnzstop', 'rgba_86_86_86_255', 'rgba_255_0_0_255', 'dnzfar', 'rgba_255_255_255_255', 'rgba_115_115_115_255', 'rgba_204_204_204_255', 'diffuse', 'rgba_64_64_64_255', 'rgba_198_181_151_255', 'rgba_35_35_35_255', 'rgba_0_25_92_255', 'rgba_31_31_31_255', 'rgba_149_149_149_255', 'etiketler', 'rgba_26_26_255_255', 'rgba_21_21_21_255', 'rgba_0_0_0_255', 'rgba_188_188_188_255', 'rgba_9_9_9_255', 'motor', 'rgba_180_180_180_255', 'crb39', 'rgba_117_117_117_255', 'bosch', 'tr', 'rgba_40_40_40_255', 'rgba_255_128_0_255', 'bege', 'rgba_82_82_82_255', 'clima2', 'hdm_01_spd2', 'rgba_114_114_114_255', 'rgba_58_58_58_255', 'rgba_48_119_186_255', 'rgba_17_11_21_255', 'rgba_184_178_180_255', 'rgba_134_133_138_255', 'rgba_18_11_19_255', '411lvcr4', 'rgba_153_30_30_255', 'hdm_01_rev2']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.254
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 235, 'width_rear': 235, 'aspect_front': 20, 'aspect_rear': 20, 'rim_in': 20, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
