"""N Vision 74: supplied model, measured 2.905m wheelbase, native electric RWD.
500kW/900Nm follows Hyundai; mass, handling, gearing and cockpit provisional.
FH2 approximates the hydrogen/fuel-cell system with its battery-electric powertrain.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='HYU_NVision74_23_A'
DONOR_ZIP=f'{HERE}/donor_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
TEXTURES={}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
ONE_SIDED=True
PRESERVE_UV_SEAMS=True
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=.2667
RIM_SOURCE_TEXTURE='source_rim'
REQUIRE_SOURCE_WHEELS=True
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=0.
WHEEL_FIT=dict(profile='charger_rim_face')
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
STEER=(-.38,.67,.31)
HIPS=(-.38,.22,-.2)
EYE=(-.38,.88,-.07)
STEERING_MATERIALS=[]  # Source steering wheel retained static.
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT=dict(paint='bfc2c6',use_make=(17,'_&857938132'))
UPGRADE_PROFILE='electric_db.py'
LIGHTS={'head':dict(mats=['HEAD_EMITTER']),'tail':dict(mats=['TAIL_EMITTER'])}
LAMP_CLEANUP='lamp_cleanup.py'
TEXTURES['tdeee7790f4']=(Image.open(os.path.join(HERE,'textures','deee7790f4.png')).convert('RGB'),512,False)
TEXTURES['td1b79a3a86']=(Image.open(os.path.join(HERE,'textures','d1b79a3a86.png')).convert('RGB'),512,False)
TEXTURES['tf94a4d320f']=(Image.open(os.path.join(HERE,'textures','f94a4d320f.png')).convert('RGB'),512,False)
TEXTURES['tf94a4d320f']=(Image.open(os.path.join(HERE,'textures','f94a4d320f.png')).convert('RGB'),512,False)
TEXTURES['td050f0abb9']=(Image.open(os.path.join(HERE,'textures','d050f0abb9.png')).convert('RGB'),512,False)
TEXTURES['t56d7f824c8']=(Image.open(os.path.join(HERE,'textures','56d7f824c8.png')).convert('RGB'),512,False)
TEXTURES['t41dfc0a6c9']=(Image.open(os.path.join(HERE,'textures','41dfc0a6c9.png')).convert('RGB'),512,False)
TEXTURES['t475dc7879a']=(Image.open(os.path.join(HERE,'textures','475dc7879a.png')).convert('RGB'),512,False)
TEXTURES['t74b5aaa404']=(Image.open(os.path.join(HERE,'textures','74b5aaa404.png')).convert('RGB'),512,False)
TEXTURES['t53dcebe715']=(Image.open(os.path.join(HERE,'textures','53dcebe715.png')).convert('RGB'),512,False)
TEXTURES['td396929a03']=(Image.open(os.path.join(HERE,'textures','d396929a03.png')).convert('RGB'),512,False)
TEXTURES['tbd971f3d22']=(Image.open(os.path.join(HERE,'textures','bd971f3d22.png')).convert('RGB'),512,False)
TEXTURES['t5834a89f47']=(Image.open(os.path.join(HERE,'textures','5834a89f47.png')).convert('RGB'),512,False)
TEXTURES['t686289ec15']=(Image.open(os.path.join(HERE,'textures','686289ec15.png')).convert('RGB'),512,False)
TEXTURES['t57d709e8ec']=(Image.open(os.path.join(HERE,'textures','57d709e8ec.png')).convert('RGB'),512,False)
TEXTURES['t42e0da1aa6']=(Image.open(os.path.join(HERE,'textures','42e0da1aa6.png')).convert('RGB'),512,False)
TEXTURES['source_rim']=TEXTURES['tdeee7790f4']
MATERIALS={'Global_Texture_Carbon1M_Diffuse': ['textured', 't686289ec15'],
 'Global_Texture_Carbon1_Diffuse': ['textured', 't57d709e8ec'],
 'Global_Texture_Coloured_Diffuse': ['textured', 'td050f0abb9'],
 'Hyundai_NVision74Concept_2023_BadgeA_DiffuseAOSO': ['textured', 't42e0da1aa6'],
 'Hyundai_NVision74Concept_2023_Grille1A_DiffuseAOSO': ['textured', 't5834a89f47'],
 'Hyundai_NVision74Concept_2023_Grille2A_DiffuseAOSO': ['textured', 'tbd971f3d22'],
 'Hyundai_NVision74Concept_2023_Grille3A_DiffuseAOSO': ['textured', 'td396929a03'],
 'Hyundai_NVision74Concept_2023_Grille4A_DiffuseAOSO': ['textured', 't53dcebe715'],
 'Hyundai_NVision74Concept_2023_Grille5A_DiffuseAOSO': ['textured', 't74b5aaa404'],
 'Hyundai_NVision74Concept_2023_InteriorA_DiffuseAOSO': ['textured', 'tf94a4d320f'],
 'Hyundai_NVision74Concept_2023_InteriorA_Emissive': ['textured', 't475dc7879a'],
 'Hyundai_NVision74Concept_2023_LightA_Diffuse': ['textured', 'td1b79a3a86'],
 'Paint': ['plain', 'paint'],
 'SOURCE_RIM': None,
 'STEERING_SOURCE': ['textured', 'tf94a4d320f'],
 'Window': ['plain', 'glass']}
MATERIALS['HEAD_EMITTER']=('plain','black')
MATERIALS['TAIL_EMITTER']=('plain','black')
PHYSICS={'aero_front': (5.0, 5.0, 0.0, 0.0),
 'aero_rear': (0.0, 0.0, 0.0, 0.0),
 'body': {'bbox': (-1.08, 1.08, -0.22, 1.12, -2.75, 2.45),
          'block': (1.995, 1.0, 4.952),
          'cm_height': 0.42,
          'height': 1.331,
          'length': 4.952,
          'mass': 2000.0,
          'model_wheelbase': 2.905,
          'ride_height': 0.1625,
          'track_front': 'auto',
          'track_rear': 'auto',
          'weight_front': 0.48,
          'wheelbase': 2.905,
          'width': 1.995},
 'brakes': {'friction': 1.0,
            'front_mm': 390.0,
            'front_pistons': 3,
            'front_type': 2,
            'rear_mm': 380.0,
            'rear_pistons': 2,
            'rear_type': 2},
 'car': {'bucket': 35,
         'class': 1,
         'downforce_front': 30.0,
         'downforce_rear': 90.0,
         'drag': 200.0,
         'engine_placement': 3,
         'family_body': 42,
         'family_model': 1,
         'family_special': 3,
         'material': 1,
         'open_cockpit': 0,
         'open_wheel': 0,
         'pi': 0.75,
         'powertrain': 3,
         'price': 1,
         'ratings': (7.0, 7.0, 8.0, 7.0, 8.0),
         'steer_deg': 35.0,
         't100': 8.5,
         't60': 3.8,
         'thumbnail_of': 1086,
         'top_mph': 155.0,
         'wi_force': 0.45,
         'year': 2023},
 'car_id': 4301,
 'colour_offset': 9000,
 'drivetrain': {'clutch_nm': 900.0,
                'drivetype': 2,
                'final_drive': 9.0,
                'gears': [1.0],
                'lsd': (0.0, 0.0, 0.0, 0.0),
                'mounting': 2,
                'reverse': -3.0,
                'shift_system': 5,
                'shift_time': 0.25},
 'engine': {'aspiration': 2,
            'boost': 0.9,
            'compression': 8.5,
            'config': 3,
            'curve': [(0, 150),
                      (1000, 230),
                      (1500, 350),
                      (4800, 350),
                      (5500, 340),
                      (6000, 310),
                      (6500, 280)],
            'cylinders': 2,
            'displacement': 2401,
            'inertia': 0.16,
            'mass': 170.0,
            'name': '2.4L I5 - Turbo',
            'peak_hp': 260,
            'peak_nm': 350,
            'redline': 6500,
            'sound': 'FOR_FocusRS_09',
            'stall': 800.0,
            'start': 3000.0,
            'tank': 70},
 'make': 'Hyundai',
 'make_code': 'HYU',
 'make_country': 6,
 'make_icon': 'ARI',
 'make_offset': 14,
 'make_profile': 'Hyundai',
 'name': 'N Vision 74',
 'short_name': 'N Vision 74',
 'string_base': 65400,
 'suspension': {'front': (94.70419793814433, 6.777523298969073, 10.16638762886598),
                'rear': (60.54858556701031, 4.333318762886599, 6.499875463917525),
                'swaybar_front': 14.904267216494848,
                'swaybar_rear': 9.936178144329897},
 'tyres': {'aspect_front': 30,
           'aspect_rear': 30,
           'compound': 4,
           'rim_in': 21,
           'width_front': 295,
           'width_rear': 345}}

# Fixed satin silver source finish; body recolouring is not yet supported.
TEXTURES['silver_finish']=(Image.new('RGB',(64,64),(185,189,194)),512,False)
MATERIALS['Paint']=('textured','silver_finish')
ARCH_MATERIALS=['Paint']

# Arch clearance revision: sprung body/cabin +25mm, axles and rim geometry unchanged.
STEER=tuple(v+(.025 if i==1 else 0) for i,v in enumerate(STEER))
HIPS=tuple(v+(.025 if i==1 else 0) for i,v in enumerate(HIPS))
EYE=tuple(v+(.025 if i==1 else 0) for i,v in enumerate(EYE))
PHYSICS['tyres'].update(aspect_front=29,aspect_rear=29)
_b=list(PHYSICS['body']['bbox']);_b[2]+=.025;_b[3]+=.025;PHYSICS['body']['bbox']=tuple(_b)
