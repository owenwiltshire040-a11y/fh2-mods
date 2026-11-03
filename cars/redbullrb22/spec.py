"""Red Bull RB22 (2026) - personal conversion of Owen's supplied model (cars/jordanej11 workflow + finish_car).

Model: Owen's model.glb (from Downloads/2026-redbull-rb22; source page, author and licence not in the file).
Measured: wheelbase 3.403 m (2026 maximum 3.4 m), tyre radius 0.354 m, tyre widths 0.346 / 0.40 m, 18-inch rims.
Real car (Wikipedia, Red Bull): Red Bull Ford DM01 1.6 L V6 turbo hybrid, 15,000 rpm limit, 770 kg with driver,
8 gears, rear-wheel drive; 2026 rules ~1,000 hp combined (400 kW ICE + 350 kW MGU-K). Curve, ratios and handling
are game settings, not team data. Sound: the Williams FW24's BMW P83 V10 bank (placeholder, as on the Jordan/Toro).
"""
import os, json, pickle
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MEDIA = 'RBR_RedBullRB22_26'                      # 18 characters
DONOR_ZIP = f'{HERE}/donor_{MEDIA}.zip'
GEO = f'{HERE}/geo.pkl'
_A = json.load(open(f'{HERE}/source-analysis.json'))
_G = pickle.load(open(GEO, 'rb'))

# ---------------------------------------------------------------- materials (all the model's own textures)
TEXTURES, MATERIALS = {}, {}
LIVERY = {'redbull_paint.007', 'redbull_decals.005', 'redbull_detail.007', 'generics2.007'}
for mat, plan in _A['mapping'].items():
    MATERIALS[mat] = plan
    if plan and plan[0] == 'textured':
        fn = _A['textures'][mat]
        TEXTURES[plan[1]] = (Image.open(f'{HERE}/textures/{fn}').convert('RGB'), 1024 if mat in LIVERY else 512, False)
TEXTURES['source_rim'] = (Image.open(f'{HERE}/textures/{_A["textures"]["rim_front"]}').convert('RGB'), 1024, False)
BODY_PLAIN = {'paint': (0, 'carpaint'), 'chrome': (0, 'frame'), 'black': (1, 'blkplastic_hgl')}
BODY_TEXTURED_LIKE = {0: 'carpaint', 3: 'carpaint'}
GLASS_PLAIN = {'glass': (0, 'gls_windsheild')}
ONE_SIDED = True
PRESERVE_UV_SEAMS = True

# ---------------------------------------------------------------- wheels: the model's own front rim, 18 inch
RIM_MATERIALS = ['SOURCE_RIM']
RIM_SOURCE_TEXTURE = 'source_rim'
RIM_CLEAR_DONOR = True
REQUIRE_SOURCE_WHEELS = True
RIM_R_REF = 0.2315         # 18 in (0.2286) + 2.4 mm: the front rim's flange reaches 0.2555 (the fit check allows 25 mm over)
RIM_REFERENCE_MATERIALS = ['rim_front', 'rim_rear']
RIM_TRUST_NORMALS = True
TRACK_REFERENCE = 'rim_face'
RIM_FACE_GAP = 0.
WHEEL_FIT = dict(profile='charger_rim_face', geometry='open_wheel')
OPEN_WHEEL_RIM_MATERIALS = {'F': ['rim_front'], 'R': ['rim_rear']}

# ---------------------------------------------------------------- cockpit
STEERING_MATERIALS = [m for m in MATERIALS if m.startswith('sw_')]
_sw = np.concatenate([p['V'] for m in STEERING_MATERIALS for p in _G['parts'][m]])
STEER = tuple(((_sw.min(0) + _sw.max(0)) / 2).round(4))
HIPS = (0.0, round(STEER[1] - 0.28, 4), round(STEER[2] - 0.492, 4))      # the Jordan's steer -> hips offset (same STR1 pose)
EYE = (0.0, round(HIPS[1] + 0.56, 4), round(HIPS[2] - 0.06, 4))
KEEP_PARTS = {'body_a.modelbin', 'steeringwheel_a.modelbin'}        # no windscreen: an open cockpit (the donor's glass stayed otherwise)
_toro = [p for p in (os.path.join(REPO, 'f1', 'in', 'STR_ToroRosso_1_06.zip'),
                     '/mnt/user-data/uploads/FH2Manager-1/fh2re/_parts/Toro_Rosso_STR1_v0.6.2_1545/media/cars/STR_ToroRosso_1_06.zip',
                     '/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods/Toro Rosso STR1/media/cars/STR_ToroRosso_1_06.zip')
         if os.path.exists(p)]
DRIVER_ANIMS_ZIP = _toro[0] if _toro else None                         # the STR1's low race-car driver pose
AVPINS_TEMPLATE = 'LMP_OpenCockpit'
COLLISION_HULL = dict(half_width=.95, floor_y=-.12, materials=['redbull_paint.007', 'redbull_carbon2.007', 'redbull_carbon3.007', 'redbull_detail.007'])
UPGRADE_PROFILE = 'race_setup.py'
LAMP_CLEANUP = 'rain_light.py'
LIGHTS = {'tail': dict(mats=['rain_light'])}
PRESENT = dict(paint='1e2a5a', logo_text='RED BULL', icon_base='RedBull', depends='zs-williams-fw24')

# ---------------------------------------------------------------- physics
_V = np.concatenate([p['V'] for m, v in _G['parts'].items() if not m.startswith('rim_') and m != 'SOURCE_RIM' for p in v])
_lo, _hi = _V.min(0), _V.max(0)
PHYSICS = {
    'car_id': 4401, 'make_offset': 120, 'make': 'Red Bull', 'make_profile': 'Red Bull Racing', 'make_code': 'RBR', 'make_country': 16,
    'make_icon': 'RedBull', 'string_base': 65300, 'colour_offset': 3300, 'name': 'RB22', 'short_name': 'RB22',
    'engine': {'name': 'Red Bull Ford DM01 1.6L V6 Turbo Hybrid', 'sound': 'BMW_P83_03', 'mass': 150.0, 'compression': 18.0,
               'config': 1, 'cylinders': 3, 'aspiration': 2, 'boost': 3.5, 'inertia': 0.03, 'tank': 75, 'displacement': 1600,
               'peak_hp': 1000.0, 'peak_nm': 640.0, 'redline': 15000, 'stall': 2000.0, 'start': 6000.0,
               'curve': [(0, 350), (2000, 400), (4000, 470), (6000, 540), (8000, 600), (10000, 640), (11000, 640),
                         (12000, 600), (13000, 545), (14000, 495), (15000, 450)]},
    'drivetrain': {'drivetype': 2, 'mounting': 1, 'shift_system': 6, 'gears': [2.75, 2.2, 1.82, 1.56, 1.37, 1.22, 1.1, 1.0],
                   'final_drive': 5.9, 'reverse': -3.0, 'shift_time': 0.03, 'lsd': (0.0, 0.0, 1400.0, 600.0), 'clutch_nm': 1200.0},
    'body': {'mass': 700.0, 'weight_front': 0.45, 'cm_height': 0.2, 'block': (1.9, 0.75, 5.39),
             'height': round(float(_hi[1] - (_G['ground'])), 3), 'length': round(float(_hi[2] - _lo[2]), 3), 'width': 1.9,
             'wheelbase': round(float(_G['wheelbase']), 4), 'model_wheelbase': round(float(_G['wheelbase']), 4),
             'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.1625,
             'bbox': tuple(round(float(x), 3) for x in (_lo[0], _hi[0], _G['ground'], _hi[1], _lo[2], _hi[2]))},
    'tyres': {'width_front': 350, 'width_rear': 400, 'aspect_front': 36, 'aspect_rear': 31, 'rim_in': 18, 'compound': 8},
    'brakes': {'front_mm': 328.0, 'front_type': 5, 'front_pistons': 6, 'rear_mm': 280.0, 'rear_type': 5, 'rear_pistons': 4, 'friction': 1.15},
    'suspension': {'front': (160.0, 8.0, 11.0), 'rear': (160.0, 8.0, 11.0), 'swaybar_front': 70.0, 'swaybar_rear': 55.0},
    'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0),
    'car': {'year': 2026, 't60': 2.4, 't100': 4.3, 'top_mph': 211.0, 'price': 2500000, 'pi': 0.999, 'drag': 200.0,
            'downforce_front': 300.0, 'downforce_rear': 500.0, 'wi_force': 0.55, 'ratings': (10.0, 10.0, 10.0, 10.0, 9.5),
            'steer_deg': 24.0, 'class': 6, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 2,
            'powertrain': 0, 'material': 3, 'open_cockpit': 1, 'open_wheel': 1, 'thumbnail_of': 2018, 'bucket': 26},
}
