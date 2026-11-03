"""Jordan EJ11 2001 — personal conversion of Owen's supplied model.
Honda RA001E identity and 17,300 rpm from Honda; curve/gearing/handling provisional.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='JOR_JordanEJ11_01_'
DONOR_ZIP=f'{HERE}/donor_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
TEXTURES={}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
ONE_SIDED=True
PRESERVE_UV_SEAMS=True
RIM_MATERIALS=['Silver_Chrome.006']
RIM_BLACK_MATERIALS=['RIM.002','Red_Chrome.004']
RIM_R_REF=.1651
RIM_REFERENCE_MATERIALS=['RIM.002','Silver_Chrome.006','Red_Chrome.004']
RIM_TRUST_NORMALS=True
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=0.
WHEEL_FIT=dict(profile='charger_rim_face',geometry='open_wheel')
OPEN_WHEEL_RIM_MATERIALS={'F':['RIM.002'],'R':['RIM_REAR.002']}
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin','steeringwheel_a.modelbin'}
DRIVER_ANIMS_ZIP='/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods/Toro Rosso STR1/media/cars/STR_ToroRosso_1_06.zip'
AVPINS_TEMPLATE='LMP_OpenCockpit'
COLLISION_HULL=dict(half_width=.72,floor_y=-.118,materials=['Material_#27.008','Floor.006','Carbon.006','Wings.008'])
UPGRADE_PROFILE='race_setup.py'
LAMP_CLEANUP='rain_light.py'
PRESENT=dict(paint='e6d500',logo_text='JORDAN',icon_base='Jordan',depends='zs-williams-fw24')
STEER=(0.0, 0.33983040070014003, 0.7308913542032242)
HIPS=(0.0, 0.05983040070013998, 0.23889135420322416)
EYE=(0.0, 0.6198304007001401, 0.17889135420322416)
STEERING_MATERIALS=['knob_sw.004', 'plastic_sw.004', 'Material_#87.002', 'Material_#88.004', 'Material_#105.004', 'LCD_sw.004', 'metal_sw.004', 'gold_sw.002']
TEXTURES['te4415c1223']=(Image.open(os.path.join(HERE,'textures','e4415c1223.png')).convert('RGB'),512,False)
TEXTURES['t4105fc3f8a']=(Image.open(os.path.join(HERE,'textures','4105fc3f8a.png')).convert('RGB'),512,False)
TEXTURES['tc7f50464e8']=(Image.open(os.path.join(HERE,'textures','c7f50464e8.png')).convert('RGB'),512,False)
TEXTURES['te01a5d49af']=(Image.open(os.path.join(HERE,'textures','e01a5d49af.png')).convert('RGB'),512,False)
TEXTURES['tfa21588bbd']=(Image.open(os.path.join(HERE,'textures','fa21588bbd.png')).convert('RGB'),512,False)
TEXTURES['tfec7fa6a3a']=(Image.open(os.path.join(HERE,'textures','fec7fa6a3a.png')).convert('RGB'),512,False)
TEXTURES['tf5a76c58b2']=(Image.open(os.path.join(HERE,'textures','f5a76c58b2.png')).convert('RGB'),512,False)
TEXTURES['taa223168df']=(Image.open(os.path.join(HERE,'textures','aa223168df.png')).convert('RGB'),512,False)
TEXTURES['t647a651c94']=(Image.open(os.path.join(HERE,'textures','647a651c94.png')).convert('RGB'),512,False)
TEXTURES['tfff47444f5']=(Image.open(os.path.join(HERE,'textures','fff47444f5.png')).convert('RGB'),512,False)
TEXTURES['td7e282fecb']=(Image.open(os.path.join(HERE,'textures','d7e282fecb.png')).convert('RGB'),512,False)
TEXTURES['t34dc657365']=(Image.open(os.path.join(HERE,'textures','34dc657365.png')).convert('RGB'),512,False)
TEXTURES['t921201e2ae']=(Image.open(os.path.join(HERE,'textures','921201e2ae.png')).convert('RGB'),512,False)
TEXTURES['t37f2fa0c0d']=(Image.open(os.path.join(HERE,'textures','37f2fa0c0d.png')).convert('RGB'),512,False)
TEXTURES['tff6f624a29']=(Image.open(os.path.join(HERE,'textures','ff6f624a29.png')).convert('RGB'),512,False)
TEXTURES['tb43ee06892']=(Image.open(os.path.join(HERE,'textures','b43ee06892.png')).convert('RGB'),512,False)
TEXTURES['t1cde879e02']=(Image.open(os.path.join(HERE,'textures','1cde879e02.png')).convert('RGB'),512,False)
TEXTURES['te33eaa9514']=(Image.open(os.path.join(HERE,'textures','e33eaa9514.png')).convert('RGB'),512,False)
TEXTURES['t65dbc207bb']=(Image.open(os.path.join(HERE,'textures','65dbc207bb.png')).convert('RGB'),512,False)
TEXTURES['t0a490ddf2f']=(Image.open(os.path.join(HERE,'textures','0a490ddf2f.png')).convert('RGB'),512,False)
TEXTURES['t81f3aab5fd']=(Image.open(os.path.join(HERE,'textures','81f3aab5fd.png')).convert('RGB'),512,False)
TEXTURES['tfbec56439f']=(Image.open(os.path.join(HERE,'textures','fbec56439f.png')).convert('RGB'),512,False)
TEXTURES['tfcf3a48af0']=(Image.open(os.path.join(HERE,'textures','fcf3a48af0.png')).convert('RGB'),512,False)
TEXTURES['td7bb8d2c6f']=(Image.open(os.path.join(HERE,'textures','d7bb8d2c6f.png')).convert('RGB'),512,False)
TEXTURES['t2508ddb72a']=(Image.open(os.path.join(HERE,'textures','2508ddb72a.png')).convert('RGB'),512,False)
TEXTURES['t5ba45b2292']=(Image.open(os.path.join(HERE,'textures','5ba45b2292.png')).convert('RGB'),512,False)
TEXTURES['t8b77d91510']=(Image.open(os.path.join(HERE,'textures','8b77d91510.png')).convert('RGB'),1024,False)
TEXTURES['t23d8aa980a']=(Image.open(os.path.join(HERE,'textures','23d8aa980a.png')).convert('RGB'),512,False)
TEXTURES['t7a2641724e']=(Image.open(os.path.join(HERE,'textures','7a2641724e.png')).convert('RGB'),512,False)
TEXTURES['t849ce0e04b']=(Image.open(os.path.join(HERE,'textures','849ce0e04b.png')).convert('RGB'),1024,False)
TEXTURES['t5dd54ce1a3']=(Image.open(os.path.join(HERE,'textures','5dd54ce1a3.png')).convert('RGB'),512,False)
TEXTURES['t45f2a161cb']=(Image.open(os.path.join(HERE,'textures','45f2a161cb.png')).convert('RGB'),512,False)
TEXTURES['tc96ed06f1e']=(Image.open(os.path.join(HERE,'textures','c96ed06f1e.png')).convert('RGB'),512,False)
TEXTURES['t6f3edda2a3']=(Image.open(os.path.join(HERE,'textures','6f3edda2a3.png')).convert('RGB'),512,False)
TEXTURES['t18859fab42']=(Image.open(os.path.join(HERE,'textures','18859fab42.png')).convert('RGB'),512,False)
TEXTURES['tb5baf04338']=(Image.open(os.path.join(HERE,'textures','b5baf04338.png')).convert('RGB'),1024,False)
MATERIALS={'Material_#116.002': ['textured', 'te4415c1223'],
 'Material_#115.006': ['textured', 't4105fc3f8a'],
 'Screw.002': ['textured', 'tc7f50464e8'],
 'Chrome_button.002': ['textured', 'te01a5d49af'],
 'INT_RedButton.002': ['textured', 'tfa21588bbd'],
 'plastic.004': ['textured', 'tfec7fa6a3a'],
 'SeatBelt.002': ['textured', 'tf5a76c58b2'],
 'INT_Rubber.006': ['textured', 'taa223168df'],
 'INT_Plastic.002': ['textured', 't647a651c94'],
 'Material_#110.002': ['textured', 'tfff47444f5'],
 'Material_#111.004': ['textured', 'td7e282fecb'],
 'EXT_FwingHD.006': ['textured', 't34dc657365'],
 'Mirror_FuelCap.006': ['textured', 't921201e2ae'],
 'Material_#106.004': ['textured', 't37f2fa0c0d'],
 'EXT_Glass.002': ['plain', 'glass'],
 'EXT_RearLight.004': ['textured', 'tff6f624a29'],
 'INT_Seat_Carbon.002': ['textured', 'tb43ee06892'],
 'INT_Carbon.006': ['textured', 't1cde879e02'],
 'gold_sw.002': ['textured', 'te33eaa9514'],
 'Chrome.004': ['textured', 't65dbc207bb'],
 'metal_sw.004': ['textured', 't0a490ddf2f'],
 'LCD_sw.004': ['textured', 't81f3aab5fd'],
 'Material_#105.004': ['textured', 'tfbec56439f'],
 'Material_#88.004': ['textured', 'tfcf3a48af0'],
 'Material_#87.002': ['textured', 'td7bb8d2c6f'],
 'plastic_sw.004': ['textured', 't2508ddb72a'],
 'knob_sw.004': ['textured', 't5ba45b2292'],
 'Material_#28.006': ['textured', 't8b77d91510'],
 'RIM_REAR.002': None,
 'RIM.002': None,
 'Silver_Chrome.006': None,
 'Red_Chrome.004': None,
 'exhaust_hole.008': ['textured', 't23d8aa980a'],
 'Radior_grille.008': ['textured', 't7a2641724e'],
 'Mirror.006': ['plain', 'chrome'],
 'Wings.008': ['textured', 't849ce0e04b'],
 'Exhaust_Metal.004': ['textured', 't5dd54ce1a3'],
 'Exhaust.002': ['textured', 't45f2a161cb'],
 'Rubber.002': ['textured', 'tc96ed06f1e'],
 'Carbon.006': ['textured', 't6f3edda2a3'],
 'Floor.006': ['textured', 't18859fab42'],
 'Material_#27.008': ['textured', 'tb5baf04338']}
PHYSICS={'car_id': 4201,
 'make_offset': 13,
 'make': 'Jordan',
 'make_profile': 'Jordan Grand Prix',
 'make_code': 'JOR',
 'make_country': 1,
 'make_icon': 'ARI',
 'string_base': 65100,
 'colour_offset': 600,
 'name': 'EJ11',
 'short_name': 'EJ11',
 'engine': {'name': 'Honda RA001E 3.0L V10',
            'sound': 'BMW_P83_03',
            'mass': 108.0,
            'compression': 13.4,
            'config': 1,
            'cylinders': 5,
            'aspiration': 1,
            'boost': 0.0,
            'inertia': 0.055,
            'tank': 95,
            'displacement': 2994,
            'peak_hp': 788.0,
            'peak_nm': 340.0,
            'redline': 17300,
            'stall': 1800.0,
            'start': 6500.0,
            'curve': [(0, 60),
                      (1000, 70),
                      (3000, 110),
                      (6000, 170),
                      (9000, 230),
                      (12000, 285),
                      (14000, 315),
                      (15500, 334),
                      (16500, 340),
                      (17000, 330),
                      (17300, 315)]},
 'drivetrain': {'drivetype': 2,
                'mounting': 1,
                'shift_system': 6,
                'gears': [3.2, 2.267, 1.8, 1.529, 1.333, 1.2, 1.091],
                'final_drive': 5.3,
                'reverse': -3.0,
                'shift_time': 0.045,
                'lsd': (0.0, 0.0, 1400.0, 600.0),
                'clutch_nm': 700.0},
 'body': {'mass': 600.0,
          'weight_front': 0.45,
          'cm_height': 0.27,
          'block': (1.8, 0.85, 4.64),
          'height': 1.083,
          'length': 4.639,
          'width': 1.805,
          'wheelbase': 3.1293326914310455,
          'model_wheelbase': 3.1293326914310455,
          'track_front': 'auto',
          'track_rear': 'auto',
          'ride_height': 0.1625,
          'bbox': (-0.91, 0.91, -0.176, 0.91, -2.01, 2.64)},
 'tyres': {'width_front': 300,
           'width_rear': 355,
           'aspect_front': 55,
           'aspect_rear': 46,
           'rim_in': 13,
           'compound': 8},
 'brakes': {'front_mm': 278.0,
            'front_type': 5,
            'front_pistons': 6,
            'rear_mm': 278.0,
            'rear_type': 5,
            'rear_pistons': 6,
            'friction': 1.15},
 'suspension': {'front': (160.0, 8.0, 11.0),
                'rear': (160.0, 8.0, 11.0),
                'swaybar_front': 70.0,
                'swaybar_rear': 55.0},
 'aero_front': (15.0, 30.0, 187.5, 312.5),
 'aero_rear': (30.0, 60.0, 450.0, 750.0),
 'car': {'year': 2001,
         't60': 2.7,
         't100': 4.8,
         'top_mph': 205.0,
         'price': 1000000,
         'pi': 0.999,
         'drag': 170.0,
         'downforce_front': 300.0,
         'downforce_rear': 500.0,
         'wi_force': 0.55,
         'ratings': (9.5, 9.7, 9.8, 9.8, 9.0),
         'steer_deg': 24.0,
         'class': 6,
         'family_model': 1,
         'family_body': 1,
         'family_special': 1,
         'engine_placement': 2,
         'powertrain': 0,
         'material': 3,
         'open_cockpit': 1,
         'open_wheel': 1,
         'thumbnail_of': 2018,
         'bucket': 26}}
LIGHTS={'tail':dict(mats=['EXT_RearLight.004'])}
