"""Early Peugeot 107 Urban 1.0, 3-door, manual — first build.
Original author/licence information was not included in the supplied GLB metadata.
Physics and sound choice are provisional; source textures preserved where available.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='PEU_107Urban_2006_'
DONOR_ZIP=f'{HERE}/donor_front_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
TEXTURES={}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
RIM_MATERIALS=['RIM_CAP']
RIM_R_REF=.1778
RIM_TRUST_NORMALS=True
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
STEER=(-.34,.692616,.43)
HIPS=(-.32,.37845,-.10)
EYE=(-.32,1.02845,-.02)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=-.015
WHEEL_FIT=dict(profile='charger_rim_face')
UPGRADE_PROFILE='upgrades.py'
PRESENT=dict(paint='799ca8',use_make=(201,'_&857995983'),depends='owen-peugeot-207')
TEXTURES['ta86e7dfbb1']=(Image.open(os.path.join(HERE,'textures','a86e7dfbb1.png')).convert('RGB'),512,False)
TEXTURES['t1fb02cb8dc']=(Image.open(os.path.join(HERE,'textures','1fb02cb8dc.png')).convert('RGB'),512,False)
TEXTURES['ta84a5335bb']=(Image.open(os.path.join(HERE,'textures','a84a5335bb.png')).convert('RGB'),512,False)
TEXTURES['t44ec519b22']=(Image.open(os.path.join(HERE,'textures','44ec519b22.png')).convert('RGB'),512,False)
TEXTURES['t65c142122c']=(Image.open(os.path.join(HERE,'textures','65c142122c.png')).convert('RGB'),512,False)
TEXTURES['t67777ca28c']=(Image.open(os.path.join(HERE,'textures','67777ca28c.png')).convert('RGB'),512,False)
TEXTURES['tb2c8b65fa6']=(Image.open(os.path.join(HERE,'textures','b2c8b65fa6.png')).convert('RGB'),512,False)
TEXTURES['t39d88b573c']=(Image.open(os.path.join(HERE,'textures','39d88b573c.png')).convert('RGB'),512,False)
TEXTURES['t1591694991']=(Image.open(os.path.join(HERE,'textures','1591694991.png')).convert('RGB'),512,False)
TEXTURES['t110dd48a1e']=(Image.open(os.path.join(HERE,'textures','110dd48a1e.png')).convert('RGB'),512,False)
TEXTURES['tabe2f17dc3']=(Image.open(os.path.join(HERE,'textures','abe2f17dc3.png')).convert('RGB'),512,False)
TEXTURES['t5a778ae4a8']=(Image.open(os.path.join(HERE,'textures','5a778ae4a8.png')).convert('RGB'),512,False)
TEXTURES['t4b9b989b26']=(Image.open(os.path.join(HERE,'textures','4b9b989b26.png')).convert('RGB'),512,False)
TEXTURES['ta94fb1daf3']=(Image.open(os.path.join(HERE,'textures','a94fb1daf3.png')).convert('RGB'),512,False)
TEXTURES['t84336d6a9b']=(Image.open(os.path.join(HERE,'textures','84336d6a9b.png')).convert('RGB'),512,False)
TEXTURES['t78988010b8']=(Image.open(os.path.join(HERE,'textures','78988010b8.png')).convert('RGB'),512,False)
TEXTURES['t914fbae2a1']=(Image.open(os.path.join(HERE,'textures','914fbae2a1.png')).convert('RGB'),512,False)
TEXTURES['t2e5f2917a7']=(Image.open(os.path.join(HERE,'textures','2e5f2917a7.png')).convert('RGB'),512,False)
TEXTURES['tb9e8500f87']=(Image.open(os.path.join(HERE,'textures','b9e8500f87.png')).convert('RGB'),512,False)
TEXTURES['t21492be4b2']=(Image.open(os.path.join(HERE,'textures','21492be4b2.png')).convert('RGB'),512,False)
TEXTURES['tcaded8160f']=(Image.open(os.path.join(HERE,'textures','caded8160f.png')).convert('RGB'),512,False)
TEXTURES['t01fea78106']=(Image.open(os.path.join(HERE,'textures','01fea78106.png')).convert('RGB'),512,False)
TEXTURES['tec6cb3a378']=(Image.open(os.path.join(HERE,'textures','ec6cb3a378.png')).convert('RGB'),512,False)
TEXTURES['t302f9b5409']=(Image.open(os.path.join(HERE,'textures','302f9b5409.png')).convert('RGB'),512,False)
TEXTURES['t0d25143388']=(Image.open(os.path.join(HERE,'textures','0d25143388.png')).convert('RGB'),512,False)
TEXTURES['t0d0181d615']=(Image.open(os.path.join(HERE,'textures','0d0181d615.png')).convert('RGB'),512,False)
TEXTURES['t4595b363df']=(Image.open(os.path.join(HERE,'textures','4595b363df.png')).convert('RGB'),512,False)
TEXTURES['ta7bddc75d3']=(Image.open(os.path.join(HERE,'textures','a7bddc75d3.png')).convert('RGB'),512,False)
TEXTURES['tfcb207496c']=(Image.open(os.path.join(HERE,'textures','fcb207496c.png')).convert('RGB'),512,False)
TEXTURES['t4fcfc2c39a']=(Image.open(os.path.join(HERE,'textures','4fcfc2c39a.png')).convert('RGB'),512,False)
TEXTURES['ta3a423580b']=(Image.open(os.path.join(HERE,'textures','a3a423580b.png')).convert('RGB'),512,False)
TEXTURES['t35f404b2af']=(Image.open(os.path.join(HERE,'textures','35f404b2af.png')).convert('RGB'),512,False)
TEXTURES['t147a416ee1']=(Image.open(os.path.join(HERE,'textures','147a416ee1.png')).convert('RGB'),512,False)
TEXTURES['t29be5fe8cb']=(Image.open(os.path.join(HERE,'textures','29be5fe8cb.png')).convert('RGB'),512,False)
TEXTURES['tad3058f80c']=(Image.open(os.path.join(HERE,'textures','ad3058f80c.png')).convert('RGB'),512,False)
TEXTURES['t2db294cee8']=(Image.open(os.path.join(HERE,'textures','2db294cee8.png')).convert('RGB'),512,False)
TEXTURES['t49de4fc61e']=(Image.open(os.path.join(HERE,'textures','49de4fc61e.png')).convert('RGB'),512,False)
TEXTURES['t1d4ac3b22c']=(Image.open(os.path.join(HERE,'textures','1d4ac3b22c.png')).convert('RGB'),512,False)
TEXTURES['t2e08928d0e']=(Image.open(os.path.join(HERE,'textures','2e08928d0e.png')).convert('RGB'),512,False)
TEXTURES['ta8d3866ed4']=(Image.open(os.path.join(HERE,'textures','a8d3866ed4.png')).convert('RGB'),512,False)
TEXTURES['t0e9d1dca87']=(Image.open(os.path.join(HERE,'textures','0e9d1dca87.png')).convert('RGB'),512,False)
TEXTURES['ta2e6bf7eab']=(Image.open(os.path.join(HERE,'textures','a2e6bf7eab.png')).convert('RGB'),512,False)
TEXTURES['t0da7db592c']=(Image.open(os.path.join(HERE,'textures','0da7db592c.png')).convert('RGB'),512,False)
TEXTURES['t8ac80f723d']=(Image.open(os.path.join(HERE,'textures','8ac80f723d.png')).convert('RGB'),512,False)
TEXTURES['t695707f05e']=(Image.open(os.path.join(HERE,'textures','695707f05e.png')).convert('RGB'),512,False)
TEXTURES['teed1a44626']=(Image.open(os.path.join(HERE,'textures','eed1a44626.png')).convert('RGB'),512,False)
TEXTURES['t466bc8cef3']=(Image.open(os.path.join(HERE,'textures','466bc8cef3.png')).convert('RGB'),512,False)
TEXTURES['tc4ec83201b']=(Image.open(os.path.join(HERE,'textures','c4ec83201b.png')).convert('RGB'),512,False)
TEXTURES['t0915e29c7b']=(Image.open(os.path.join(HERE,'textures','0915e29c7b.png')).convert('RGB'),512,False)
TEXTURES['tbbacb9602b']=(Image.open(os.path.join(HERE,'textures','bbacb9602b.png')).convert('RGB'),512,False)
MATERIALS={'RIM_CAP': None,
 'RIM_STEEL': None,
 'abs_start': ('textured', 'tfcb207496c'),
 'airbag': ('textured', 't0d25143388'),
 'battery_start': ('textured', 't4595b363df'),
 'black': ('textured', 't466bc8cef3'),
 'bumper_frame': ('textured', 'tc4ec83201b'),
 'c12': ('textured', 't2e5f2917a7'),
 'c1_Int': ('textured', 't67777ca28c'),
 'c1_SYMB': ('textured', 't5a778ae4a8'),
 'c1_carbonplastic': ('textured', 'ta94fb1daf3'),
 'c1_chmsl': ('textured', 't2db294cee8'),
 'c1_exttrim.skin_exttrim.exttrimyes': ('textured', 't65c142122c'),
 'c1_hazard': ('textured', 't21492be4b2'),
 'c1_intplastic': ('textured', 't4b9b989b26'),
 'c1_lowbeam': ('textured', 't44ec519b22'),
 'c1_odomt': ('textured', 'tb9e8500f87'),
 'c1_paint': ('plain', 'paint'),
 'c1_plastic': ('textured', 't1591694991'),
 'c1_signal_L': ('textured', 'ta84a5335bb'),
 'c1_signal_R': ('textured', 'tabe2f17dc3'),
 'c1_sitz': ('textured', 't1d4ac3b22c'),
 'c1_swplastic': ('textured', 'tb2c8b65fa6'),
 'c1_tailglass': None,
 'c1_taillight': ('textured', 't29be5fe8cb'),
 'c1_weiss': ('textured', 't914fbae2a1'),
 'checkengine_start': ('textured', 't0d0181d615'),
 'citroen_odometer': ('textured', 't84336d6a9b'),
 'cloth': ('textured', 'ta8d3866ed4'),
 'covet': ('textured', 't695707f05e'),
 'covet_gauges': ('textured', 'ta2e6bf7eab'),
 'covet_gauges_odo': ('textured', 't147a416ee1'),
 'covet_glass': ('plain', 'glass'),
 'covet_interior': ('textured', 't0e9d1dca87'),
 'covet_mechanical': ('textured', 'teed1a44626'),
 'detail_glass_amber': None,
 'detail_glass_red': None,
 'frame': ('textured', 't39d88b573c'),
 'gauge_needle': ('textured', 't0915e29c7b'),
 'grille': ('textured', 't110dd48a1e'),
 'headliner': ('textured', 't2e08928d0e'),
 'heat_start': ('textured', 'tcaded8160f'),
 'highbeam': ('textured', 'tec6cb3a378'),
 'licenseplate-52-11': ('textured', 't49de4fc61e'),
 'lowbeam': ('textured', 't302f9b5409'),
 'mirror_CE': ('plain', 'chrome'),
 'mirror_CX': ('plain', 'chrome'),
 'mirror_F': ('plain', 'chrome'),
 'oil_start': ('textured', 'ta7bddc75d3'),
 'parkingbrake': ('textured', 'ta3a423580b'),
 'red': ('textured', 't78988010b8'),
 'reflector': ('textured', 't0da7db592c'),
 'reverse_light': ('textured', 'tbbacb9602b'),
 'seatbelt': ('textured', 't35f404b2af'),
 'signal_L': ('textured', 't4fcfc2c39a'),
 'signal_R': ('textured', 't01fea78106'),
 'textured_reflector': ('textured', 'tad3058f80c'),
 'vivace_engine': ('textured', 'ta86e7dfbb1'),
 'vivace_glass': None,
 'vivace_logo': ('textured', 't1fb02cb8dc'),
 'vivace_mechanical': ('textured', 't8ac80f723d')}
PHYSICS={'car_id': 4107,
 'make_offset': 12,
 'make': 'Peugeot',
 'make_profile': 'Automobiles Peugeot',
 'make_code': 'PEU',
 'make_country': 4,
 'make_icon': 'ARI',
 'string_base': 65020,
 'colour_offset': 500,
 'name': '107 Urban 1.0',
 'short_name': '107',
 'engine': {'name': '1.0L I3',
            'sound': 'FIA_595SS_68',
            'mass': 70.0,
            'compression': 10.5,
            'config': 3,
            'cylinders': 11,
            'aspiration': 1,
            'boost': 0.0,
            'inertia': 0.095,
            'tank': 35,
            'displacement': 998,
            'peak_hp': 67.1,
            'peak_nm': 93,
            'redline': 6500,
            'stall': 800.0,
            'start': 3000.0,
            'curve': [(0, 35),
                      (1000, 58),
                      (2000, 78),
                      (3600, 93),
                      (4500, 91),
                      (5000, 88),
                      (6000, 79.58),
                      (6500, 65)]},
 'drivetrain': {'drivetype': 1,
                'mounting': 2,
                'shift_system': 1,
                'gears': [3.545, 1.913, 1.31, 1.027, 0.85],
                'final_drive': 3.55,
                'reverse': -3.214,
                'shift_time': 0.35,
                'lsd': (0.0, 0.0, 0.0, 0.0),
                'clutch_nm': 150.0},
 'body': {'mass': 790.0,
          'weight_front': 0.62,
          'cm_height': 0.48,
          'block': (1.63, 0.95, 3.43),
          'height': 1.47,
          'length': 3.43,
          'width': 1.63,
          'wheelbase': 2.34,
          'model_wheelbase': 2.34,
          'track_front': 'auto',
          'track_rear': 'auto',
          'ride_height': 0.1625,
          'bbox': (-0.86, 0.86, -0.1274, 1.32, -1.6, 1.9)},
 'tyres': {'width_front': 155,
           'width_rear': 155,
           'aspect_front': 65,
           'aspect_rear': 65,
           'rim_in': 14,
           'compound': 3},
 'brakes': {'front_mm': 247.0,
            'front_type': 2,
            'front_pistons': 1,
            'rear_mm': 200.0,
            'rear_type': 1,
            'rear_pistons': 1,
            'friction': 1.0},
 'suspension': {'front': (37.558391752577315,
                          2.6878731958762887,
                          4.031850515463917),
                'rear': (24.012742268041237,
                         1.7185350515463917,
                         2.5777618556701025),
                'swaybar_front': 5.910828865979382,
                'swaybar_rear': 3.9405525773195875},
 'aero_front': (5.0, 5.0, 0.0, 0.0),
 'aero_rear': (0.0, 0.0, 0.0, 0.0),
 'car': {'year': 2006,
         't60': 13.7,
         't100': 50.0,
         'top_mph': 98.0,
         'price': 8000,
         'pi': 0.15,
         'drag': 150.0,
         'downforce_front': 0.0,
         'downforce_rear': -1.0,
         'wi_force': 0.45,
         'ratings': (3.0, 3.5, 3.0, 3.5, 3.0),
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
         'thumbnail_of': 1086,
         'bucket': 23}}

LIGHTS={
 'head':dict(mats=['c1_lowbeam','c1_highbeam']),
 'tail':dict(mats=['c1_taillight','c1_chmsl'],box=((0.,.65,-1.55),(.9,1.1,-.9))),
 'reverse':dict(mats=['reverse_light']),
 'turn_f':dict(mats=['c1_signal_L','c1_signal_R']),
 'turn_r':dict(mats=['c1_signal_L','c1_signal_R']),
 'chmsl':dict(mats=['c1_chmsl'],box=((0.,1.15,-1.3),(.2,1.3,-1.0))),
}

# Untextured donor chassis/arch-liner surfaces should be dark, not default grey.
for _mat in ["covet","covet_mechanical","vivace_mechanical","bumper_frame"]:
 MATERIALS[_mat]=("plain","black")

MATERIALS["ARCH_LINER"]=("plain","black")

# Reflective front housings and badge, with transparent outer headlamp covers.
BODY_PLAIN['front_chrome']=(0,'front_chrome')
GLASS_PLAIN['headlamp_clear']=(0,'headlamp_clear')
MATERIALS['FRONT_REFLECTOR']=('plain','front_chrome')
MATERIALS['BADGE_LION']=('plain','front_chrome')
MATERIALS['BADGE_BACKING']=('plain','black')
MATERIALS['BADGE_INSET']=('plain','black')
MATERIALS['vivace_glass']=('plain','headlamp_clear')
