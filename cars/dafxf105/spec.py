"""DAF XF105.510 4x2 tractor unit — on the Charger generic donor. FH2's first lorry.

Model: "low poly DAF xf105" by Alvin.Woodly (Sketchfab, CC BY 4.0). glb, metres, Y up, +Z front. Low poly, no
textures, no interior (the windscreen is opaque black, kept as gloss black). Wheels baked into the body:
Circle.004 = front pair, Circle.006 = rear twin pairs (tagged RIM_ by glbgeo --tag-nodes Circle.=RIM_).
Geometry: glbgeo.py daf.glb geo.pkl --frame=-x,y,z --scale 1.018 --wheels=0.872,-2.8605,0.4855,1.025
          --tyre-radius 0.497 --ground=-0.35 --axle-mid 0.0867 --tag-nodes Circle.=RIM_
  (scale 1.018 = the real 3,800 mm wheelbase / model 3,733; wheel r 0.506). Front tyres centred at |x| 1.025 (model),
  rear twins span 0.54-1.225 (set centre 0.882).
Tracks are explicit (no wheel arches to measure): the game draws a wheel ~5 cm inboard of track/2, so
track = 2 * (wheel centre + 0.05).
FH2 limits: 8 forward gears, rims <= 24", tyre width <= 450 mm (stock data). The rear twins become one 450 mm tyre.
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = 'DAF_XF105_510_4x2_'                          # 18 chars
DONOR_ZIP = f'{HERE}/donor_{MEDIA}.zip'
GEO = f'{HERE}/geo.pkl'
TEXTURES = {'orange': (Image.new('RGB', (64, 64), (230, 80, 5)), 512, False)}
MATERIALS = {
    'base': ('plain', 'paint'),
    'chrome': ('plain', 'chrome'), 'chrome2': ('plain', 'chrome'), 'chrome_shiny': ('plain', 'chrome'), 'exhaust_tip': ('plain', 'chrome'),
    'grill': ('plain', 'black'), 'rubber': ('plain', 'black'), 'chassis': ('plain', 'black'), 'bottom_black': ('plain', 'black'),
    'deflector_on_windshiwld': ('plain', 'black'), 'windshield': ('plain', 'black'),          # opaque in the model: gloss black reads as tinted glass
    'headlight_glass': ('plain', 'glass'),
    'top_orange_lights': ('textured', 'orange'), 'top_orange_light_glass': ('textured', 'orange'),
    'tail_light_orange': ('textured', 'orange'), 'indicator_light': ('textured', 'orange'),   # side markers (the rear ones go to the lamps)
    'front_indicator': ('plain', 'chrome'), 'headlights': ('plain', 'chrome'), 'high_beams': ('plain', 'chrome'),
    'taillight_glass_red': ('plain', 'black'), 'brake_lights': ('plain', 'black'), 'reverse_light': ('plain', 'chrome'), 'tail_light_white': ('plain', 'chrome'),
    'RIM_chrome': None, 'RIM_grill': None, 'RIM_rubber': None,
}
BODY_PLAIN = {'paint': (0, 'carpaint'), 'chrome': (0, 'frame'), 'black': (1, 'blkplastic_hgl')}
BODY_TEXTURED_LIKE = {0: 'carpaint', 3: 'carpaint'}
GLASS_PLAIN = {'glass': (0, 'gls_windsheild')}
RIM_MATERIALS = ['RIM_chrome']                         # the polished steel wheel
RIM_BLACK_MATERIALS = ['RIM_grill']                    # the black hub centre
RIM_TRUST_NORMALS = True
ONE_SIDED = True
KEEP_PARTS = {'body_a.modelbin', 'glassf_a.modelbin'}
STEER = (-0.55, 2.00, 2.45)                            # LHD cab, ~1.2 m cab floor (no interior in the model; the driver is hidden by the black glass)
HIPS = (-0.55, 1.62, 1.95)
EYE = (-0.55, 2.35, 1.95)
DRIVER_ANIMS_ZIP = None
AVPINS_TEMPLATE = None

# ---------------------------------------------------------------- physics (build_car_db.py)
# XF105.510 FT 4x2 (2012): PACCAR MX-13 12.9 L I6 turbo-diesel, 510 hp at 1,500-1,900 rpm, 2,500 Nm at 1,000-1,410,
# 12-speed ZF AS-Tronic (FH2 max 8: the top 8 of a range-change box), RWD; tractor ~7,200 kg; 6.0 x 2.49 x 3.9 m,
# wheelbase 3,800; 385/65 R22.5 front, 315/80 R22.5 twin rear (-> 450 mm in FH2); 430 mm discs; ~85 mph unloaded,
# no limiter (real ones are limited to 56). Sound: the Terradyne Gurkha's 6.7 turbo-diesel V8 (FH2 has no lorries).
_K = 7200 / 970
PHYSICS = dict(
    car_id=3410, make_offset=6, make='DAF', make_profile='DAF Trucks', make_code='DAF', make_country=12, make_icon='DAF',
    string_base=64410, colour_offset=300, name='XF105.510', short_name='XF105',
    engine=dict(name='12.9L I6 - Turbo Diesel', sound='ARM_GurkhaFF_14', mass=1050.0, compression=17.0, config=3, cylinders=3, aspiration=2, boost=2.5,
                inertia=2.5, tank=430, displacement=12900, peak_hp=510, peak_nm=2500, redline=2300, stall=550.0, start=1200.0,
                curve=[(0, 900), (600, 1500), (800, 2000), (1000, 2500), (1400, 2500), (1700, 2200), (1900, 1890), (2100, 1600), (2300, 1300)]),
    drivetrain=dict(drivetype=2, mounting=1, shift_system=4, gears=[7.44, 5.87, 4.57, 3.47, 2.70, 2.10, 1.29, 1.00], final_drive=2.69,
                    reverse=-6.0, shift_time=0.45, lsd=(0.0, 0.0, 0.0, 0.0), clutch_nm=6000.0),
    body=dict(mass=7200.0, weight_front=0.68, cm_height=1.10, block=(2.49, 3.0, 6.0), height=3.9, length=6.0, width=2.49, wheelbase=3.80,
              model_wheelbase=3.80, track_front=round(2 * (1.025 * 1.018 + 0.05), 3), track_rear=round(2 * (0.882 * 1.018 + 0.05), 3),
              ride_height=0.1625, bbox=(-1.55, 1.55, -0.35, 3.62, -2.77, 3.37)),
    tyres=dict(width_front=385, width_rear=450, aspect_front=60, aspect_rear=50, rim_in=22, compound=1),
    brakes=dict(front_mm=430.0, front_type=2, front_pistons=2, rear_mm=430.0, rear_type=2, rear_pistons=2, friction=0.9),
    suspension=dict(front=(46.116 * _K, 3.3003 * _K, 4.9505 * _K), rear=(29.484 * _K, 2.1101 * _K, 3.1651 * _K), swaybar_front=7.2576 * _K, swaybar_rear=4.8384 * _K),
    aero_front=(5.0, 5.0, 0.0, 0.0), aero_rear=(0.0, 0.0, 0.0, 0.0),
    car=dict(year=2012, t60=14.0, t100=60.0, top_mph=85.0, price=85000, pi=0.15, drag=186.1 * 0.60 / 0.33 * 4.0, downforce_front=0.0, downforce_rear=-1.0, wi_force=1.5,
             ratings=(2.0, 3.0, 2.0, 2.0, 2.0), steer_deg=40.0, **{'class': 0}, bucket=38, family_model=1, family_body=1, family_special=3, engine_placement=1, powertrain=1,
             material=1, open_cockpit=0, open_wheel=0, thumbnail_of=1082),
)

# working lamps (fh2re/lightbuild.py), boxes in FH2 space ((|x|, y, z) min, max)
LIGHTS = {
    'head': dict(mats=['headlights', 'high_beams'], box=((0.80, 0.12, 3.08), (1.10, 0.53, 3.32))),
    'turn_f': dict(mats=['front_indicator'], box=((1.10, 0.45, 3.10), (1.20, 0.53, 3.20))),
    'tail': dict(mats=['taillight_glass_red', 'brake_lights'], box=((0.68, 0.28, -2.60), (1.24, 0.49, -2.44))),
    'reverse': dict(mats=['reverse_light', 'tail_light_white'], box=((0.68, 0.28, -2.60), (0.80, 0.49, -2.44))),
    'turn_r': dict(mats=['tail_light_orange', 'indicator_light'], box=((1.05, 0.28, -2.60), (1.14, 0.49, -2.44))),
}

# Autoshow presentation: new make DAF (Netherlands), wordmark logo, white cab
PRESENT = dict(paint='e8e8ea', logo_text='DAF', icon_base='DAF')

# collision: the cab + chassis (mirrors clipped), floor 35 cm up like the Charger's 20 cm (Owen 30 Oct: drove through a lamp post)
COLLISION_HULL = dict(half_width=1.25, floor_y=0.0)
