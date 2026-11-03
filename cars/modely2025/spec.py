"""2025 Tesla Model Y AWD — first-pass electric build.
Model BloxBloger, CC BY-NC 4.0. Physics are provisional game tuning.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='TES_ModelY_2025_A_'
DONOR_ZIP=f'{HERE}/donor_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
TEXTURES={'grey':(Image.new('RGB',(64,64),(55,58,61)),512,False),'white':(Image.new('RGB',(64,64),(175,175,180)),512,False),'red':(Image.new('RGB',(64,64),(175,10,10)),512,False)}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
RIM_MATERIALS=['TESLA_RIM']
RIM_BLACK_MATERIALS=['TESLA_RIM_BLACK']
RIM_R_REF=.2794
RIM_TRUST_NORMALS=True
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
STEER=(-.37,.856767,.55)
HIPS=(-.37,.416767,.02)
EYE=(-.37,1.076767,.12)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT=dict(paint='dddddf',use_make=(81,'_&857955286'))
UPGRADE_PROFILE='electric_db.py'
LIGHTS={'head':dict(mats=['front_white_light']), 'tail':dict(mats=['back_red_Light'])}
LAMP_CLEANUP='lamp_cleanup.py'
MATERIALS={'04_-_Default': ('plain', 'black'),
 'Iron_Clean_Distorted': ('plain', 'black'),
 'Material_111': ('plain', 'black'),
 'Material_2125765635': ('plain', 'paint'),
 'Material_2125767099': ('textured', 'white'),
 'Rubber_Rough': ('plain', 'black'),
 'Rubber_Rough222': ('plain', 'black'),
 'TESLA_RIM': None,
 'TESLA_RIM_BLACK': None,
 'back_red_Light': ('textured', 'red'),
 'black': ('plain', 'black'),
 'black.001': ('plain', 'black'),
 'black.002': ('plain', 'black'),
 'black222': ('plain', 'black'),
 'black_base': ('plain', 'black'),
 'black_reflection': ('plain', 'black'),
 'chrome': ('plain', 'chrome'),
 'front_white_light': ('plain', 'black'),
 'glass_base': ('plain', 'glass'),
 'glass_headlight222': None,
 'glass_roof_panorama': ('plain', 'glass'),
 'material': ('textured', 'red'),
 'mirror': ('plain', 'chrome'),
 'red_plastic': ('textured', 'red')}
PHYSICS={'car_id': 3905,
 'make_offset': 10,
 'make': 'Tesla',
 'make_profile': 'Tesla',
 'make_code': 'TES',
 'make_country': 10,
 'make_icon': 'ARI',
 'string_base': 64920,
 'colour_offset': 400,
 'name': 'Model Y AWD',
 'short_name': 'Model Y',
 'engine': {'name': '2.4L I5 - Turbo',
            'sound': 'FOR_FocusRS_09',
            'mass': 170.0,
            'compression': 8.5,
            'config': 3,
            'cylinders': 2,
            'aspiration': 2,
            'boost': 0.9,
            'inertia': 0.16,
            'tank': 70,
            'displacement': 2401,
            'peak_hp': 260,
            'peak_nm': 350,
            'redline': 6500,
            'stall': 800.0,
            'start': 3000.0,
            'curve': [(0, 150),
                      (1000, 230),
                      (1500, 350),
                      (4800, 350),
                      (5500, 340),
                      (6000, 310),
                      (6500, 280)]},
 'drivetrain': {'drivetype': 3,
                'mounting': 2,
                'shift_system': 5,
                'gears': [1.0],
                'final_drive': 9.0,
                'reverse': -3.0,
                'shift_time': 0.25,
                'lsd': (0.0, 0.0, 0.0, 0.0),
                'clutch_nm': 900.0},
 'body': {'mass': 1992.0,
          'weight_front': 0.5,
          'cm_height': 0.5,
          'block': (1.92, 1.15, 4.79),
          'height': 1.624,
          'length': 4.79,
          'width': 1.92,
          'wheelbase': 2.89,
          'model_wheelbase': 2.89,
          'track_front': 'auto',
          'track_rear': 'auto',
          'ride_height': 0.1625,
          'bbox': (-1.07, 1.07, -0.173, 1.46, -2.43, 2.4)},
 'tyres': {'width_front': 255,
           'width_rear': 255,
           'aspect_front': 40,
           'aspect_rear': 40,
           'rim_in': 20,
           'compound': 4},
 'brakes': {'front_mm': 355.0,
            'front_type': 2,
            'front_pistons': 1,
            'rear_mm': 335.0,
            'rear_type': 2,
            'rear_pistons': 1,
            'friction': 1.0},
 'suspension': {'front': (94.70419793814433,
                          6.777523298969073,
                          10.16638762886598),
                'rear': (60.54858556701031,
                         4.333318762886599,
                         6.499875463917525),
                'swaybar_front': 14.904267216494848,
                'swaybar_rear': 9.936178144329897},
 'aero_front': (5.0, 5.0, 0.0, 0.0),
 'aero_rear': (0.0, 0.0, 0.0, 0.0),
 'car': {'year': 2025,
         't60': 4.6,
         't100': 11.5,
         'top_mph': 125.0,
         'price': 50000,
         'pi': 0.6,
         'drag': 187.0,
         'downforce_front': 0.0,
         'downforce_rear': -1.0,
         'wi_force': 0.45,
         'ratings': (6.0, 5.5, 7.0, 6.0, 7.0),
         'steer_deg': 35.0,
         'class': 1,
         'family_model': 1,
         'family_body': 42,
         'family_special': 3,
         'engine_placement': 3,
         'powertrain': 3,
         'material': 1,
         'open_cockpit': 0,
         'open_wheel': 0,
         'thumbnail_of': 1086,
         'bucket': 39}}

# Fit rendered track to source arch lips using the Passat-tested game offset rule.
LIP_GAP=.07

# Custom wheel mesh local origin is its outer face, not the tyre centre.
TRACK_REFERENCE="rim_face"
RIM_FACE_GAP=.01

WHEEL_FIT=dict(profile='charger_rim_face')
