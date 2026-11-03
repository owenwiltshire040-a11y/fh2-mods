"""Opel Vectra B — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='OPE_daily08_2001__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['tce8282ce']=(Image.open(os.path.join(HERE,'textures','tce8282ce.png')),512,False)
TEXTURES['t023772b8']=(Image.open(os.path.join(HERE,'textures','t023772b8.png')),512,False)
TEXTURES['te501eee2']=(Image.open(os.path.join(HERE,'textures','te501eee2.png')),512,False)
TEXTURES['t584ce69f']=(Image.open(os.path.join(HERE,'textures','t584ce69f.png')),512,False)
TEXTURES['t3fcaec4a']=(Image.open(os.path.join(HERE,'textures','t3fcaec4a.png')),512,False)
TEXTURES['t561caf9c']=(Image.open(os.path.join(HERE,'textures','t561caf9c.png')),512,False)
TEXTURES['t05d560fe']=(Image.open(os.path.join(HERE,'textures','t05d560fe.png')),512,False)
TEXTURES['tf3319963']=(Image.open(os.path.join(HERE,'textures','tf3319963.png')),512,False)
TEXTURES['t2ca06e11']=(Image.open(os.path.join(HERE,'textures','t2ca06e11.png')),512,False)
TEXTURES['t1052cde2']=(Image.open(os.path.join(HERE,'textures','t1052cde2.png')),512,False)
TEXTURES['tdd34877a']=(Image.open(os.path.join(HERE,'textures','tdd34877a.png')),512,False)
TEXTURES['tf8248e12']=(Image.open(os.path.join(HERE,'textures','tf8248e12.png')),512,False)
TEXTURES['tbb057c9d']=(Image.open(os.path.join(HERE,'textures','tbb057c9d.png')),512,False)
TEXTURES['t16a20f6d']=(Image.open(os.path.join(HERE,'textures','t16a20f6d.png')),512,False)
TEXTURES['t214cf453']=(Image.open(os.path.join(HERE,'textures','t214cf453.png')),512,False)
TEXTURES['ta29e2c9c']=(Image.open(os.path.join(HERE,'textures','ta29e2c9c.png')),512,False)
TEXTURES['t1b90d469']=(Image.open(os.path.join(HERE,'textures','t1b90d469.png')),512,False)
TEXTURES['t63533c70']=(Image.open(os.path.join(HERE,'textures','t63533c70.png')),512,False)
TEXTURES['t820510e8']=(Image.open(os.path.join(HERE,'textures','t820510e8.png')),512,False)
TEXTURES['t005cbeba']=(Image.open(os.path.join(HERE,'textures','t005cbeba.png')),512,False)
TEXTURES['tfd0aae35']=(Image.open(os.path.join(HERE,'textures','tfd0aae35.png')),512,False)
TEXTURES['t6c89b6f3']=(Image.open(os.path.join(HERE,'textures','t6c89b6f3.png')),512,False)
TEXTURES['t6c3feae4']=(Image.open(os.path.join(HERE,'textures','t6c3feae4.png')),512,False)
TEXTURES['t1bb2e986']=(Image.open(os.path.join(HERE,'textures','t1bb2e986.png')),512,False)
TEXTURES['ta7ce70d0']=(Image.open(os.path.join(HERE,'textures','ta7ce70d0.png')),512,False)
TEXTURES['t52da7846']=(Image.open(os.path.join(HERE,'textures','t52da7846.png')),512,False)
TEXTURES['tbc8db151']=(Image.open(os.path.join(HERE,'textures','tbc8db151.png')),512,False)
TEXTURES['t9efc176a']=(Image.open(os.path.join(HERE,'textures','t9efc176a.png')),512,False)
TEXTURES['tcbb4919b']=(Image.open(os.path.join(HERE,'textures','tcbb4919b.png')),512,False)
TEXTURES['t3b2c14fa']=(Image.open(os.path.join(HERE,'textures','t3b2c14fa.png')),512,False)
TEXTURES['t2ad6945a']=(Image.open(os.path.join(HERE,'textures','t2ad6945a.png')),512,False)
TEXTURES['t976f560b']=(Image.open(os.path.join(HERE,'textures','t976f560b.png')),512,False)
TEXTURES['tc36bc91c']=(Image.open(os.path.join(HERE,'textures','tc36bc91c.png')),512,False)
MATERIALS={'vectra_glass': ('plain', 'glass'), 'blackplastic': ('textured', 'tce8282ce'), 'vectra': ('plain', 'paint'), 'vectra_headlight': ('textured', 't023772b8'), 'numframe': ('textured', 'te501eee2'), 'numplate': ('textured', 't584ce69f'), 'ignoreme': ('textured', 't3fcaec4a'), 'chrome': ('plain', 'chrome'), 'vectra_taillight': ('textured', 't561caf9c'), 'seats': ('textured', 't05d560fe'), 'mirror': ('plain', 'chrome'), 'dash': ('textured', 'tf3319963'), 'enginebayblk': ('textured', 't2ca06e11'), 'doorhandle': ('textured', 't1052cde2'), 'chro': ('textured', 'tdd34877a'), 'silver': ('textured', 'tf8248e12'), 'doorinnerr': ('textured', 'tbb057c9d'), 'doorinnerl': ('textured', 't16a20f6d'), 'enginebaygrey': ('textured', 't214cf453'), 'sideindicator': ('textured', 'ta29e2c9c'), 'exhaust': ('textured', 't1b90d469'), 'enginebayyel': ('textured', 't63533c70'), 'intcarpet': ('textured', 't820510e8'), 'underside': ('textured', 't005cbeba'), 'wipers': ('textured', 'tfd0aae35'), 'mirrorpedals': ('textured', 't6c89b6f3'), 'sunroofinner': ('textured', 't6c3feae4'), 'windowtrim': ('textured', 't1bb2e986'), 'taillightrefl': ('textured', 'ta7ce70d0'), 'mesh': ('textured', 't52da7846'), 'VECTRA_STEERIN01': ('textured', 'tbc8db151'), 'VECTRA_STEERINGW': ('textured', 't9efc176a'), 'hatch': ('textured', 'tcbb4919b'), 'SuspensionTex': ('textured', 't3b2c14fa'), 'fullsize': ('textured', 't2ad6945a'), 'fullsize_001': ('textured', 't976f560b'), 'steering1': ('textured', 'tc36bc91c')}
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
STEER=(-0.34, 0.5772833812949639, 0.4)
HIPS=(-0.34, 0.2880196582733813, -0.05)
EYE=(-0.34, 1.0035667625899278, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (304, '_&857996988'), 'depends': 'owen-daily05'}
PHYSICS={'car_id': 5008, 'make_offset': 107, 'make': 'Opel', 'make_profile': 'Opel', 'make_code': 'OPE', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65221, 'colour_offset': 2200, 'name': 'Vectra B', 'short_name': 'Vectra B', 'engine': {'name': '2.0L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1998, 'peak_hp': 134, 'peak_nm': 188, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 56.4), (1000, 94.0), (2000, 150.4), (3500, 188), (4500, 178.6), (5500, 169.20000000000002), (6000, 150.4), (6500, 103.4)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 282.0}, 'body': {'mass': 1290, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.8447671160637902, 1.3478477369457913, 4.483213969529103), 'height': 1.3478477369457913, 'length': 4.483213969529103, 'width': 1.8447671160637902, 'wheelbase': 2.637, 'model_wheelbase': 2.637, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.9223835580318951, 0.9223835580318952, -0.07697839197720159, 1.2708693449685897, -2.238134307138868, 2.245079662390235)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 16, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (61.32952577319586, 4.389058762886598, 6.583654639175258), 'rear': (39.21068041237113, 2.8062154639175256, 4.2092567010309265), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2001, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['vectra']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.1905
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 185, 'width_rear': 185, 'aspect_front': 60, 'aspect_rear': 60, 'rim_in': 15, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
