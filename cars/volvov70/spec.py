"""Volvo V70 (P2) T5 — on the Charger generic donor.

Model: "Volvo V70" by KOElkast1007 (Sketchfab, https://sketchfab.com/3d-models/volvo-v70-61bb5ad577754b8ead80a85e94cbf644),
glb with GTA-style material names. The body nodes are Z-up / Y-forward (+Y = front), the wheel nodes sit in their own
Y-up frame with the rim face at negative local x. Model units are ~1.088 x metres (3.00 between the arches for a
2.755 m wheelbase): --scale 0.9183. Arch centres (body frame) y +2.2 / -0.8, tyre centre height z 0.31 (lip 0.73),
half track 0.86 -> FH2 wheels at z 1.464 / -1.291, x +/-0.79. Materials from the colour pass (materials_preview.png):
vehicle_generic_smallspecmap = paint, detail2 = chrome trim, og_19 = rubber seals/strips, og_5 = arch liners +
exhaust, og_137 = black trim, og_interior, og_glass.002 + windows = glass, og_glass.001 = headlight lenses,
limo_lights_glass = lights, og_mirror = mirror glass, og_mesh = grille, og_volvo.001 = badge, og_rim = rim,
og_volvo.002 = wheel centre badges (wheel frame), tyre + brakes = the game's.
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = 'VOL_V70T5_2005_P2_'                          # 18 chars, like DOD_ChargerSRT8_12
DONOR_ZIP = f'{HERE}/donor_{MEDIA}.zip'
GEO = f'{HERE}/geo.pkl'
TEXTURES = {'red': (Image.new('RGB', (64, 64), (200, 10, 10)), 512, False)}
MATERIALS = {
    'vehicle_generic_smallspecmap.001': ('plain', 'paint'),
    'vehicle_generic_detail2.001': ('plain', 'chrome'), 'og_mirror.001': ('plain', 'chrome'), 'og_volvo.001': ('plain', 'chrome'),
    'og_glass.001': ('plain', 'chrome'), 'limo_lights_glass.001': ('plain', 'chrome'), 'limo_lights_glass.002': ('textured', 'red'),
    'og_19.001': ('plain', 'black'), 'og_5.001': ('plain', 'black'), 'og_137.001': ('plain', 'black'), 'og_interior.001': ('plain', 'black'),
    'og_mesh.001': ('plain', 'black'),
    'og_glass.002': ('plain', 'glass'), 'windows.001': ('plain', 'glass'),
    'og_rim': None, 'vehicle_generic_tyrewallblack.001': None, 'og_brakes': None, 'og_volvo.002': None,
}
BODY_PLAIN = {'paint': (0, 'carpaint'), 'chrome': (0, 'frame'), 'black': (1, 'blkplastic_hgl')}
BODY_TEXTURED_LIKE = {0: 'carpaint', 3: 'carpaint'}
GLASS_PLAIN = {'glass': (0, 'gls_windsheild')}
RIM_MATERIALS = ['og_rim']
KEEP_PARTS = {'body_a.modelbin', 'glassf_a.modelbin'}
# LHD; wheel ~0.95 m above ground, dash ~1.0 m behind the front axle; H-point ~0.55 m up (ground is FH2 y -0.173)
STEER = (-0.38, 0.78, 0.40)
HIPS = (-0.37, 0.36, -0.05)
EYE = (-0.37, 0.98, 0.02)
DRIVER_ANIMS_ZIP = None
AVPINS_TEMPLATE = None

# ---------------------------------------------------------------- physics (build_car_db.py)
# V70 II (P2) T5, 2005: 2,401 cc B5254T4 I5 turbo, 260 hp at 5,500, 350 Nm 1,500-4,800, M66 6-speed manual, FWD;
# kerb ~1,590 kg EC (-75 driver = 1,515), 4,733 x 1,804 x 1,490 mm, wheelbase 2,755, track ~1,580; 235/45 R17;
# discs 316 vented / 288; 0-62 6.8 s; 155 mph (limited); Cd 0.31. Suspension: Fiesta Mk7 scaled by mass.
_K = 1515 / 970
PHYSICS = dict(
    car_id=3700, make_offset=4, make='Volvo', make_profile='Volvo Cars', make_code='VOL', make_country=4, make_icon='ARI',
    string_base=64700, colour_offset=180, name='V70 T5', short_name='V70',
    engine=dict(name='2.4L I5 - Turbo', sound='FOR_FocusRS_09', mass=170.0, compression=8.5, config=3, cylinders=2, aspiration=2, boost=0.9,
                inertia=0.16, tank=70, displacement=2401, peak_hp=260, peak_nm=350, redline=6500, stall=800.0, start=3000.0,
                curve=[(0, 150), (1000, 230), (1500, 350), (4800, 350), (5500, 340), (6000, 310), (6500, 280)]),
    drivetrain=dict(drivetype=1, mounting=2, shift_system=1, gears=[3.077, 1.818, 1.185, 0.886, 0.717, 0.610], final_drive=4.00,
                    reverse=-3.0, shift_time=0.25, lsd=(0.0, 0.0, 0.0, 0.0), clutch_nm=900.0),
    body=dict(mass=1515.0, weight_front=0.61, cm_height=0.55, block=(1.80, 1.15, 4.73), height=1.49, length=4.733, width=1.804, wheelbase=2.755,
              model_wheelbase=2.755, track_front=1.58, track_rear=1.58, ride_height=0.16, bbox=(-1.05, 1.05, -0.18, 1.33, -2.25, 2.47)),
    tyres=dict(width_front=235, width_rear=235, aspect_front=45, aspect_rear=45, rim_in=17, compound=4),
    brakes=dict(front_mm=316.0, front_type=2, front_pistons=1, rear_mm=288.0, rear_type=2, rear_pistons=1, friction=1.0),
    suspension=dict(front=(46.116 * _K, 3.3003 * _K, 4.9505 * _K), rear=(29.484 * _K, 2.1101 * _K, 3.1651 * _K), swaybar_front=7.2576 * _K, swaybar_rear=4.8384 * _K),
    aero_front=(5.0, 5.0, 0.0, 0.0), aero_rear=(0.0, 0.0, 0.0, 0.0),
    car=dict(year=2005, t60=6.5, t100=16.5, top_mph=155.0, price=32000, pi=0.60, drag=187.0, downforce_front=0.0, downforce_rear=-1.0, wi_force=0.45,
             ratings=(6.0, 5.5, 6.5, 6.0, 5.5), steer_deg=35.0, **{'class': 1}, family_model=1, family_body=1, family_special=3, engine_placement=1, powertrain=0,
             material=1, open_cockpit=0, open_wheel=0, thumbnail_of=1086),
)
