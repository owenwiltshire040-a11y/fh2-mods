"""Passat B3 2.0 16V, first build. Model Driving501, CC BY 4.0.
Mass, gearing, suspension, driver placement and performance are provisional tuning values.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='VW_PassatB3_1990_A'
DONOR_ZIP=f'{HERE}/donor_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
TEXTURES={'red':(Image.new('RGB',(64,64),(180,8,8)),512,False),'amber':(Image.new('RGB',(64,64),(230,105,5)),512,False)}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
RIM_MATERIALS=['PASSAT_STEEL_RIM']
RIM_TRUST_NORMALS=True
RIM_R_REF=0.1778
LIP_GAP=0.04
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
STEER=(-.386,.60,.59)
HIPS=(-.35,.34,-.04)
EYE=(-.35,.98,.02)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT=dict(paint='284e69',use_make=(52,'_&857938517'))
MATERIALS={'Matte__D6BCA76D__spec_trans': ('plain', 'black'),
 'Matte__FF000000__spec': ('plain', 'black'),
 'Matte__FF1B1B1B__spec': ('plain', 'black'),
 'Matte__FF1B1B1B__spec_.005': ('plain', 'black'),
 'Matte__FF1F1F1F': ('plain', 'black'),
 'Matte__FF1F1F1F__env_3_spec': ('plain', 'black'),
 'Matte__FF252525__spec': ('plain', 'black'),
 'Matte__FF272727__spec': ('plain', 'black'),
 'Matte__FF282828__spec': ('plain', 'black'),
 'Matte__FF292929__spec': ('plain', 'black'),
 'Matte__FF3A3A3A__spec': ('plain', 'black'),
 'Matte__FF484848__spec': ('plain', 'black'),
 'Matte__FF515151__env_14_spec': ('plain', 'black'),
 'Matte__FF595959__spec': ('plain', 'black'),
 'Matte__FF707070__spec': ('plain', 'black'),
 'Matte__FF888888__spec': ('plain', 'black'),
 'Matte__FFFFFFF9__spec': ('plain', 'black'),
 'Matte__FFFFFFFF__spec': ('plain', 'black'),
 'YotaDigiClock': ('plain', 'black'),
 'aluminium__spec': ('plain', 'chrome'),
 'battery': ('plain', 'black'),
 'chassis.1': ('plain', 'black'),
 'checkengine': ('plain', 'black'),
 'chromeb3': ('plain', 'chrome'),
 'fotel__spec': ('plain', 'black'),
 'highbeam': ('plain', 'black'),
 'interior_lod0__spec': ('plain', 'black'),
 'lampa__spec_trans': ('plain', 'black'),
 'lowpressure': ('plain', 'black'),
 'material_0': ('plain', 'black'),
 'motor.010': ('plain', 'black'),
 'pasB3': ('plain', 'paint'),
 'pasB3_decals_gauges': ('plain', 'black'),
 'pasB3_fdpovL1': ('textured', 'amber'),
 'pasB3_fdpovR': ('textured', 'amber'),
 'pasB3_fdpovR1': ('textured', 'amber'),
 'pasB3_fog': ('plain', 'black'),
 'pasB3_gaby': ('textured', 'red'),
 'pasB3_povL': ('textured', 'amber'),
 'pasB3_povL.008': ('textured', 'amber'),
 'pasB3_povR': ('textured', 'amber'),
 'pasB3_priborka': ('plain', 'black'),
 'pasB3_revers': ('plain', 'chrome'),
 'pasB3_stop': ('textured', 'red'),
 'pasb3glass': ('plain', 'glass'),
 'pessima': ('plain', 'black'),
 'pessima_engine': ('plain', 'black'),
 'pessima_foglight': ('plain', 'chrome'),
 'pessima_glass': ('plain', 'glass'),
 'pessima_headlight': ('plain', 'chrome'),
 'rallyparts': ('plain', 'black'),
 'rollcage_01a': None,
 'rollcage_01b': None,
 'signal_L': ('plain', 'black'),
 'signal_R': ('plain', 'black'),
 'spec': ('plain', 'black'),
 'tonerB3': None}
PHYSICS={'car_id': 3803,
 'make_offset': 8,
 'make': 'Volkswagen',
 'make_profile': 'Volkswagen',
 'make_code': 'VW',
 'make_country': 3,
 'make_icon': 'ARI',
 'string_base': 64820,
 'colour_offset': 240,
 'name': 'Passat B3 2.0 16V',
 'short_name': 'Passat B3',
 'engine': {'name': '2.0L I4 - 16V',
            'sound': 'VW_GolfGTi16vMk2_92',
            'mass': 140.0,
            'compression': 10.8,
            'config': 3,
            'cylinders': 1,
            'aspiration': 1,
            'boost': 0.0,
            'inertia': 0.14,
            'tank': 70,
            'displacement': 1984,
            'peak_hp': 134.1,
            'peak_nm': 180,
            'redline': 6800,
            'stall': 800.0,
            'start': 3000.0,
            'curve': [(0, 70),
                      (1000, 110),
                      (2000, 145),
                      (3000, 165),
                      (4400, 180),
                      (5800, 164.65),
                      (6500, 140),
                      (6800, 120)]},
 'drivetrain': {'drivetype': 1,
                'mounting': 2,
                'shift_system': 1,
                'gears': [3.455, 1.944, 1.286, 0.969, 0.805],
                'final_drive': 3.684,
                'reverse': -3.0,
                'shift_time': 0.25,
                'lsd': (0.0, 0.0, 0.0, 0.0),
                'clutch_nm': 350.0},
 'body': {'mass': 1230.0,
          'weight_front': 0.61,
          'cm_height': 0.52,
          'block': (1.705, 1.1, 4.57),
          'height': 1.45,
          'length': 4.57,
          'width': 1.705,
          'wheelbase': 2.625,
          'model_wheelbase': 2.625,
          'track_front': 'auto',
          'track_rear': 'auto',
          'ride_height': 0.1625,
          'bbox': (-0.89, 0.89, -0.173, 1.277, -2.3, 2.3)},
 'tyres': {'width_front': 195,
           'width_rear': 195,
           'aspect_front': 60,
           'aspect_rear': 60,
           'rim_in': 14,
           'compound': 4},
 'brakes': {'front_mm': 256.0,
            'front_type': 2,
            'front_pistons': 1,
            'rear_mm': 226.0,
            'rear_type': 2,
            'rear_pistons': 1,
            'friction': 1.0},
 'suspension': {'front': (58.47698969072165,
                          4.184916494845361,
                          6.277438144329897),
                'rear': (37.38692783505155,
                         2.6756938144329903,
                         4.013477319587628),
                'swaybar_front': 9.202936082474228,
                'swaybar_rear': 6.135290721649485},
 'aero_front': (5.0, 5.0, 0.0, 0.0),
 'aero_rear': (0.0, 0.0, 0.0, 0.0),
 'car': {'year': 1990,
         't60': 9.9,
         't100': 29.0,
         'top_mph': 128.0,
         'price': 15000,
         'pi': 0.35,
         'drag': 180.0,
         'downforce_front': 0.0,
         'downforce_rear': -1.0,
         'wi_force': 0.45,
         'ratings': (4.0, 4.0, 4.5, 4.0, 4.0),
         'steer_deg': 35.0,
         'class': 1,
         'family_model': 1,
         'family_body': 1,
         'family_special': 1,
         'engine_placement': 1,
         'powertrain': 0,
         'material': 1,
         'open_cockpit': 0,
         'open_wheel': 0,
         'thumbnail_of': 1086}}

UPGRADE_PROFILE='upgrades.py'

# Functional lamp surfaces; fog lamps remain decorative.
LIGHTS={
 'head':dict(mats=['pessima_headlight']),
 'tail':dict(mats=['pasB3_stop','pasB3_gaby']),
 'reverse':dict(mats=['pasB3_revers']),
 'turn_f':dict(mats=['pasB3_povL','pasB3_povR','pasB3_fdpovR1','pasB3_fdpovL1']),
 'turn_r':dict(mats=['pasB3_povL.008','pasB3_fdpovR']),
}
import runpy
TEXTURES.update(runpy.run_path(os.path.join(HERE,'cabin_materials.py'))['textures']())
for _group,_texture in [('CABIN_CLOTH','cloth'),('CABIN_DASH','dash'),('CABIN_TRIM','trim'),('CABIN_GAUGES','gauges'),('CABIN_NEEDLE','needle')]:
 MATERIALS[_group]=('textured',_texture)
# Inactive warning lights should not appear illuminated continuously.
for _m in ['checkengine','battery','highbeam','lowpressure','signal_L','signal_R','YotaDigiClock']:
 MATERIALS[_m]=('textured','dash')

# Lamp cover meshes were opaque and occluded the functional emitter surfaces.
MATERIALS["lampa__spec_trans"]=None
LAMP_CLEANUP="lamp_cleanup.py"

# Put reverse/turn emission on the visible upper lens faces, ahead of the rear trim.
LIGHTS['reverse']=dict(mats=['REVERSE_OUTER'])
LIGHTS['turn_r']=dict(mats=['TURN_REAR_OUTER'])
MATERIALS['pasB3_revers']=None
MATERIALS['pasB3_povL.008']=None
MATERIALS['pasB3_fdpovR']=None
MATERIALS['REVERSE_OUTER']=None
MATERIALS['TURN_REAR_OUTER']=None

WHEEL_FIT=dict(profile='charger_legacy')
