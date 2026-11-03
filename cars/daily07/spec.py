"""Opel Astra H — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='OPE_daily07_2005__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t771bb9f1']=(Image.open(os.path.join(HERE,'textures','t771bb9f1.png')),512,False)
TEXTURES['t2b710550']=(Image.open(os.path.join(HERE,'textures','t2b710550.png')),512,False)
TEXTURES['t97912524']=(Image.open(os.path.join(HERE,'textures','t97912524.png')),512,False)
TEXTURES['teef41a0d']=(Image.open(os.path.join(HERE,'textures','teef41a0d.png')),512,False)
TEXTURES['t14029d3e']=(Image.open(os.path.join(HERE,'textures','t14029d3e.png')),512,False)
TEXTURES['t356d7b05']=(Image.open(os.path.join(HERE,'textures','t356d7b05.png')),512,False)
TEXTURES['tee6574ff']=(Image.open(os.path.join(HERE,'textures','tee6574ff.png')),512,False)
TEXTURES['t194fd00b']=(Image.open(os.path.join(HERE,'textures','t194fd00b.png')),512,False)
TEXTURES['t717a9dac']=(Image.open(os.path.join(HERE,'textures','t717a9dac.png')),512,False)
TEXTURES['tb5d22a6c']=(Image.open(os.path.join(HERE,'textures','tb5d22a6c.png')),512,False)
TEXTURES['t44ecea13']=(Image.open(os.path.join(HERE,'textures','t44ecea13.png')),512,False)
TEXTURES['t4b637b0f']=(Image.open(os.path.join(HERE,'textures','t4b637b0f.png')),512,False)
TEXTURES['t5e65acf9']=(Image.open(os.path.join(HERE,'textures','t5e65acf9.png')),512,False)
TEXTURES['t51a14648']=(Image.open(os.path.join(HERE,'textures','t51a14648.png')),512,False)
TEXTURES['tb73e8940']=(Image.open(os.path.join(HERE,'textures','tb73e8940.png')),512,False)
TEXTURES['t9fa47a51']=(Image.open(os.path.join(HERE,'textures','t9fa47a51.png')),512,False)
TEXTURES['tf49e8a8d']=(Image.open(os.path.join(HERE,'textures','tf49e8a8d.png')),512,False)
TEXTURES['ta6b7abab']=(Image.open(os.path.join(HERE,'textures','ta6b7abab.png')),512,False)
TEXTURES['t4c1919dc']=(Image.open(os.path.join(HERE,'textures','t4c1919dc.png')),512,False)
TEXTURES['t4649f06d']=(Image.open(os.path.join(HERE,'textures','t4649f06d.png')),512,False)
TEXTURES['t82481a00']=(Image.open(os.path.join(HERE,'textures','t82481a00.png')),512,False)
TEXTURES['t603af0d9']=(Image.open(os.path.join(HERE,'textures','t603af0d9.png')),512,False)
TEXTURES['tc3a46ede']=(Image.open(os.path.join(HERE,'textures','tc3a46ede.png')),512,False)
MATERIALS={'956_1': ('textured', 't771bb9f1'), '956_3': ('textured', 't2b710550'), '956_0': ('plain', 'paint'), 'material': ('textured', 't97912524'), '956_15': ('textured', 'teef41a0d'), '956_8': ('textured', 't14029d3e'), '956_7': ('textured', 't356d7b05'), '956_17': ('textured', 'tee6574ff'), '956_2': ('textured', 't194fd00b'), '956_26': ('textured', 't717a9dac'), '956_18': ('textured', 'tb5d22a6c'), '956_19': ('textured', 't44ecea13'), '956_10': ('textured', 't4b637b0f'), '956_23': ('textured', 't5e65acf9'), '956_22': ('textured', 't51a14648'), '956_21': ('textured', 'tb73e8940'), '956_4': ('textured', 't9fa47a51'), '956_16': ('textured', 'tf49e8a8d'), '956_14': ('textured', 'ta6b7abab'), '956_12': ('textured', 't4c1919dc'), '956_11': ('textured', 't4649f06d'), '956_9': ('textured', 't82481a00'), '956_6': ('textured', 't603af0d9'), '956_5': ('textured', 'tc3a46ede')}
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
STEER=(-0.34, 0.5602973684210526, 0.4)
HIPS=(-0.34, 0.28255986842105263, -0.05)
EYE=(-0.34, 0.9695947368421052, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (304, '_&857996988'), 'depends': 'owen-daily05'}
PHYSICS={'car_id': 5007, 'make_offset': 106, 'make': 'Opel', 'make_profile': 'Opel', 'make_code': 'OPE', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65218, 'colour_offset': 2100, 'name': 'Astra H', 'short_name': 'Astra H', 'engine': {'name': '1.6L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1598, 'peak_hp': 104, 'peak_nm': 150, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [[0, 45.0], [1000, 75.0], [2000, 120.0], [3500, 150], [4500, 142.5], [5500, 134.64992525897165], [6000, 120.0], [6500, 82.5]]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': [0.0, 0.0, 0.0, 0.0], 'clutch_nm': 250}, 'body': {'mass': 1230, 'weight_front': 0.6, 'cm_height': 0.48, 'block': [2.098281152860075, 1.8647604319991458, 4.402525153369178], 'height': 1.8647604319991458, 'length': 4.402525153369178, 'width': 2.098281152860075, 'wheelbase': 2.614, 'model_wheelbase': 2.614, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': [-1.0490635127669439, 1.0492176400931312, -0.22250526627534317, 1.6422551657238027, -2.105959416119797, 2.296565737249381]}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 15, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': [58.47698969072164, 4.1849164948453605, 6.2774381443298966], 'rear': [37.386927835051544, 2.67569381443299, 4.013477319587627], 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': [5.0, 5.0, 0.0, 0.0], 'aero_rear': [0.0, 0.0, 0.0, 0.0], 'car': {'year': 2005, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': [3.0, 3.5, 3.0, 3.5, 3.0], 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['956_0']
UPGRADE_PROFILE='upgrade_profile.py'

MATERIALS['ASTRA_WINDOWS']=('plain','glass')
MATERIALS['956_2']=('plain','black')
MATERIALS['956_4']=('plain','black')
MATERIALS['956_16']=('plain','black')
MATERIALS['956_22']=('plain','black')
MATERIALS['956_23']=('plain','black')
MATERIALS['956_7']=('plain','paint')
MATERIALS['956_1']=('plain','paint')
ARCH_MATERIALS=['956_0','956_1','956_7']

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.2032
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 195, 'width_rear': 195, 'aspect_front': 45, 'aspect_rear': 45, 'rim_in': 16, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
