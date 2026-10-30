"""2023 Chery Omoda 5 290T (1.6 TGDI, 7DCT, FWD) — on the Charger generic donor.

Model: "2023 Chery Omoda 5 290T" by Ddiaz Design (Sketchfab, CC BY-NC-SA 4.0: personal / non-commercial; if shared,
same licence). glb from FBX, metres, Y up, +Z front, LHD (driver seat 'zhujia' at x -0.36 after the flip).
Node names are pinyin: wudeng = the lower (main) headlamp units, front_light = the upper DRL strip, trunk_light = tail
clusters (A = quarters, plain = tailgate), hub_* = the wheels, baked into the body (tagged RIM_ by glbgeo --tag-nodes).
Geometry: glbgeo.py omoda5.glb geo.pkl --frame=-x,y,z --scale 1.023 --wheels=1.2500,-1.3206,0.3428,0.781
          --tyre-radius 0.3376 --ground=-0.189 --axle-mid 0.0867 --tag-nodes hub_=RIM_
  (scale 1.023 = real 2,630 mm wheelbase / model 2,571; tyre r 0.345 = 215/55 R18). Steering wheel ~(-0.345, 0.84, 0.45),
  driver seat centre (-0.358, 0.674, -0.143).
Textures from the glb (src/*.png): Texture_Map (badges, lamp details), door_Map (door cards), inner_map_1 (dash,
headliner, pillars), seats.
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = 'CRY_Omoda5_290T_23'                          # 18 chars; CRY because CHE is Chevrolet's code in FH2
DONOR_ZIP = f'{HERE}/donor_{MEDIA}.zip'               # f1/make_media.py in/DOD_ChargerSRT8_12.zip <this> CRY_Omoda5_290T_23
GEO = f'{HERE}/geo.pkl'
_t = lambda n: Image.open(f'{HERE}/src/{n}.png')
TEXTURES = {
    'texmap': (_t('Texture_Map'), 1024, True), 'doormap': (_t('door_Map'), 1024, True),
    'inner': (_t('inner_map_1'), 1024, True), 'seats': (_t('seats'), 1024, True),
    'orange': (Image.new('RGB', (64, 64), (172, 45, 0)), 512, True), 'red': (Image.new('RGB', (64, 64), (150, 0, 0)), 512, False),
    'white': (Image.new('RGB', (64, 64), (225, 225, 225)), 512, False),
}
MATERIALS = {                                         # model material -> ('plain', key) | ('textured', key) | None (drop)
    'CarPaint': ('plain', 'paint'),
    'Chrome': ('plain', 'chrome'), 'Chrome_R': ('plain', 'chrome'), 'mirror': ('plain', 'chrome'),
    'Black_Paint': ('plain', 'black'), 'Plastic': ('plain', 'black'), 'Plastic_B': ('plain', 'black'), 'chassis': ('plain', 'black'),
    'plastic_chassis': ('plain', 'black'), 'metal_Black': ('plain', 'black'),
    'Texture_Map': ('textured', 'texmap'), 'door_Map': ('textured', 'doormap'), 'inner_map_1': ('textured', 'inner'),
    'seats': ('textured', 'seats'), 'orange': ('textured', 'orange'), 'white': ('textured', 'white'),
    'RED_Metal': ('textured', 'red'), 'Red_L': ('textured', 'red'), 'red_light_plastic': ('textured', 'red'), 'red_glass': ('textured', 'red'),
    'windows': ('plain', 'glass'), 'd_glass': ('plain', 'glass'), 'light_glass': ('plain', 'glass'),
    'tire': None, 'breaks': None,
    'RIM_Plastic_B': None, 'RIM_Chrome': None, 'RIM_orange': None, 'RIM_breaks': None, 'RIM_tire': None,
}
BODY_PLAIN = {'paint': (0, 'carpaint'), 'chrome': (0, 'frame'), 'black': (1, 'blkplastic_hgl')}
BODY_TEXTURED_LIKE = {0: 'carpaint', 3: 'carpaint'}
GLASS_PLAIN = {'glass': (0, 'gls_windsheild')}
RIM_MATERIALS = ['RIM_Chrome']                         # silver centre cap
RIM_BLACK_MATERIALS = ['RIM_Plastic_B', 'RIM_orange']  # black spokes + lip; the orange accent ring drawn black (the wheel part has no colour slot)
RIM_TRUST_NORMALS = True                               # FBX-derived glb: normals are good
KEEP_PARTS = {'body_a.modelbin', 'glassf_a.modelbin'}
STEER = (-0.345, 0.84, 0.45)
HIPS = (-0.36, 0.56, 0.02)                             # the 208's hips-to-wheel offset applied to this wheel; seat x
EYE = (-0.36, 1.18, 0.02)
DRIVER_ANIMS_ZIP = None
AVPINS_TEMPLATE = None

# ---------------------------------------------------------------- physics (build_car_db.py)
# Omoda 5 1.6 TGDI 290T (2023): 1,598 cc I4 turbo, 197 PS (145 kW) at 5,500, 290 Nm at 2,000-4,000, 7-speed DCT, FWD;
# ~1,430 kg kerb (-75 kg driver = 1,355), 4,400 x 1,830 x 1,588 mm, wheelbase 2,630; 215/55 R18; discs ~305 / 292 mm;
# 0-62 ~7.9 s, ~116 mph (186 km/h, limited); Cd ~0.33. Suspension: the 208's (Fiesta Mk7 scaled by mass).
_K = 1355 / 970
PHYSICS = dict(
    car_id=3305, make_offset=5, make='Chery', make_profile='Chery Automobile', make_code='CRY', make_country=9, make_icon='Chery',
    string_base=64305, colour_offset=240, name='Omoda 5 290T', short_name='Omoda 5',
    engine=dict(name='1.6L I4 - Turbo', sound='FOR_FocusST_12', mass=125.0, compression=9.5, config=3, cylinders=11, aspiration=2, boost=1.4,
                inertia=0.14, tank=51, displacement=1598, peak_hp=194, peak_nm=290, redline=6200, stall=750.0, start=3000.0,
                curve=[(0, 120), (1000, 170), (1500, 240), (2000, 290), (4000, 290), (5000, 265), (5500, 252), (6000, 225), (6200, 210)]),
    drivetrain=dict(drivetype=1, mounting=2, shift_system=4, gears=[3.64, 2.37, 1.53, 1.09, 0.89, 0.74, 0.62], final_drive=4.05,
                    reverse=-3.5, shift_time=0.12, lsd=(0.0, 0.0, 0.0, 0.0), clutch_nm=800.0),
    body=dict(mass=1355.0, weight_front=0.60, cm_height=0.58, block=(1.83, 1.20, 4.40), height=1.588, length=4.40, width=1.83, wheelbase=2.63,
              model_wheelbase=2.63, track_front='auto', track_rear='auto', ride_height=0.19, bbox=(-1.06, 1.06, -0.19, 1.42, -2.11, 2.31)),
    tyres=dict(width_front=215, width_rear=215, aspect_front=55, aspect_rear=55, rim_in=18, compound=4),
    brakes=dict(front_mm=305.0, front_type=2, front_pistons=1, rear_mm=292.0, rear_type=1, rear_pistons=1, friction=1.0),
    suspension=dict(front=(46.116 * _K, 3.3003 * _K, 4.9505 * _K), rear=(29.484 * _K, 2.1101 * _K, 3.1651 * _K), swaybar_front=7.2576 * _K, swaybar_rear=4.8384 * _K),
    aero_front=(5.0, 5.0, 0.0, 0.0), aero_rear=(0.0, 0.0, 0.0, 0.0),
    car=dict(year=2023, t60=7.6, t100=21.0, top_mph=116.0, price=27000, pi=0.40, drag=186.1 * 0.33 / 0.33 * 1.15, downforce_front=0.0, downforce_rear=-1.0, wi_force=0.55,
             ratings=(4.0, 5.0, 4.5, 5.0, 4.0), steer_deg=35.0, **{'class': 0}, family_model=1, family_body=1, family_special=3, engine_placement=1, powertrain=0,
             material=1, open_cockpit=0, open_wheel=0, thumbnail_of=1082),
)

# working lamps (fh2re/lightbuild.py): box = ((|x|, y, z) min, max) in FH2 space
LIGHTS = {
    'head': dict(mats=['Chrome', 'Texture_Map'], box=((0.68, 0.35, 1.82), (0.89, 0.65, 2.10))),    # the lower main units (wudeng): reflectors + projector map
    'drl': dict(mats=['Texture_Map'], box=((0.51, 0.70, 1.69), (0.85, 0.80, 2.15))),               # the slim upper strip (front_light)
    'tail': dict(mats=['red_light_plastic', 'Red_L', 'red_glass'], box=((0.0, 0.79, -2.12), (0.86, 0.98, -1.49))),  # quarter + tailgate clusters
    'reverse': dict(mats=['light_glass'], box=((0.33, 0.91, -2.09), (0.84, 0.95, -1.71))),          # the clear patches in the rear clusters
}

# Autoshow presentation (package_car.py): new make Chery with Owen's logo, thumbnail in the model's grey
PRESENT = dict(paint='424749', logo_png=f'{HERE}/src/chery_logo.png', icon_base='Chery')

ONE_SIDED = True     # good glb normals: single-sided like the game's own cars (double-sided twins shade one side dark)

LIP_GAP = 0.08       # 0.04 (the 208 rule) left the wheels too far in on this SUV (Owen 30 Oct)
TRANSFER_UV = 'roof'   # shading channels = the stock paint's roof point per group ('nearest' per-vertex left dark door-jamb blotches)
