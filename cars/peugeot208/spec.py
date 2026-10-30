"""2021 Peugeot 208 (II) 1.2 PureTech 130 GT, EAT8 — on the Charger generic donor.

Model: "2021 Peugeot 208" by tonielpro520 (Sketchfab, CC BY 4.0), SketchUp OBJ in metres, Y up, +Z front, LHD.
Materials (Portuguese): Carro_Pintura paint, Carro_Vidros/Vidros_1/Vidro_R_ glass, Carro_Roda rims, Carro_Pneu1 tyres,
Carro_Freio/Freio_Disco brakes, Carro_Refletor_Farol/Lanterna head/tail reflectors, Carro_Interno interior,
Carro_Cromado chrome, Carro_Espelhos mirror glass, Carro_Plastico(_1) black plastic, Carro_Metal_Preto(_1) black metal,
Carro_Metal_Vermelho(_1) red lamp lenses.
Geometry (fh2re/objgeo.py): wheelbase 2.550, track 1.397, tyre radius 0.315; steering wheel at file (+0.385, 0.88, 0.31)
i.e. FH2 (-0.385, 0.72, 0.40); driver's seat cushion y 0.45-0.57 file -> hips FH2 (-0.33, 0.44, 0.00).
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = 'PEU_208PureTech_21'                          # 18 chars, like DOD_ChargerSRT8_12
DONOR_ZIP = f'{HERE}/donor_{MEDIA}.zip'               # make_media.py in/DOD_ChargerSRT8_12.zip <this> PEU_208PureTech_21
GEO = f'{HERE}/geo.pkl'                               # objgeo.py <obj> geo.pkl Carro_Pneu1 --ground -0.159 --axle-mid 0.0867
TEXTURES = {'red': (Image.new('RGB', (64, 64), (200, 10, 10)), 512, False)}
MATERIALS = {                                         # model material -> ('plain', key) | ('textured', key) | None (drop)
    'Carro_Pintura': ('plain', 'paint'),
    'Carro_Cromado': ('plain', 'chrome'), 'Carro_Espelhos': ('plain', 'chrome'),
    'Carro_Refletor_Farol': ('plain', 'chrome'), 'Carro_Refletor_Farol_1': ('plain', 'chrome'),
    'Carro_Refletor_Lanterna': ('plain', 'chrome'), 'Carro_Refletor_Lanterna_1': ('plain', 'chrome'),
    'Carro_Plastico': ('plain', 'black'), 'Carro_Plastico_1': ('plain', 'black'),
    'Carro_Metal_Preto': None, 'Carro_Metal_Preto_1': ('plain', 'black'), 'Carro_Interno': ('plain', 'black'),   # Metal_Preto = the rim spokes
    'Carro_Metal_Vermelho': ('textured', 'red'), 'Carro_Metal_Vermelho_1': ('textured', 'red'),
    'Carro_Vidros': ('plain', 'glass'), 'Carro_Vidros_1': ('plain', 'glass'), 'Carro_Vidro_R_': ('plain', 'glass'),
    'Carro_Pneu1': None, 'Carro_Roda': None, 'Carro_Roda_1': None, 'Carro_Freio': None, 'Carro_Freio_Disco': None,
}
# Charger body_a: group 0 = carpaint + frame (LODs 3..32), 1 = blkplastic_hgl, 3 = LOD64 carpaint; glassF_a group 0 = gls_windsheild
BODY_PLAIN = {'paint': (0, 'carpaint'), 'chrome': (0, 'frame'), 'black': (1, 'blkplastic_hgl')}
BODY_TEXTURED_LIKE = {0: 'carpaint', 3: 'carpaint'}
GLASS_PLAIN = {'glass': (0, 'gls_windsheild')}
RIM_MATERIALS = ['Carro_Roda', 'Carro_Roda_1', 'Carro_Cromado']    # the 208's wheel -> the game's wheel part: machined faces + cap
RIM_BLACK_MATERIALS = ['Carro_Metal_Preto']                            # the black spokes -> the wheel part's black material
KEEP_PARTS = {'body_a.modelbin', 'glassf_a.modelbin'}  # the 208's own interior (steering wheel, seats) is in the body
STEER = (-0.385, 0.72, 0.40)
HIPS = (-0.33, 0.44, 0.00)
EYE = (-0.33, 1.05, 0.08)
DRIVER_ANIMS_ZIP = None                               # the Charger's sedan pose suits a hatchback
AVPINS_TEMPLATE = None

# ---------------------------------------------------------------- physics (build_car_db.py)
# 208 II 1.2 PureTech 130 GT EAT8 (2021): 1,199 cc I3 turbo, 130 hp at 5,500, 230 Nm at 1,750, 8-speed auto, FWD;
# kerb 1,165 kg EC (-75 kg driver = 1,090), 4,055 x 1,745 x 1,430 mm, wheelbase 2,540; 205/45 R17; discs 283 / 249 mm;
# 0-62 8.7 s, 129 mph; Cd ~0.29. Track: 1.55 / 1.54 by eye in game (real 1.496 / 1.483 still looked inboard; the model has 1.397). Suspension/anti-roll: the game's Fiesta Mk7 (970 kg) scaled by mass, as the 207 mod did.
_K = 1090 / 970
PHYSICS = dict(
    car_id=3208, make_offset=3, make='Peugeot', make_profile='Automobiles Peugeot', make_code='PEU', make_country=4, make_icon='ARI',
    string_base=64218, colour_offset=120, name='208 PureTech 130', short_name='208',  # string_base 64208 clashed with the 207 mod (30 Oct)
    engine=dict(name='1.2L I3 - Turbo', sound='FIA_500AbarthSS_10', mass=95.0, compression=10.5, config=3, cylinders=11, aspiration=2, boost=1.2,
                inertia=0.11, tank=44, displacement=1199, peak_hp=130, peak_nm=230, redline=6200, stall=750.0, start=3000.0,
                curve=[(0, 110), (1000, 150), (1500, 205), (1750, 230), (3500, 230), (4500, 205), (5500, 169), (6000, 150), (6200, 140)]),
    drivetrain=dict(drivetype=1, mounting=2, shift_system=4, gears=[5.25, 3.03, 1.95, 1.46, 1.22, 1.00, 0.81, 0.67], final_drive=3.56,
                    reverse=-4.0, shift_time=0.2, lsd=(0.0, 0.0, 0.0, 0.0), clutch_nm=700.0),
    body=dict(mass=1090.0, weight_front=0.62, cm_height=0.52, block=(1.75, 1.10, 4.06), height=1.43, length=4.055, width=1.745, wheelbase=2.54,
              model_wheelbase=2.55, track_front=1.55, track_rear=1.54, ride_height=0.16, bbox=(-0.95, 0.95, -0.17, 1.42, -1.87, 2.19)),
    tyres=dict(width_front=205, width_rear=205, aspect_front=45, aspect_rear=45, rim_in=17, compound=4),
    brakes=dict(front_mm=283.0, front_type=2, front_pistons=1, rear_mm=249.0, rear_type=2, rear_pistons=1, friction=1.0),
    suspension=dict(front=(46.116 * _K, 3.3003 * _K, 4.9505 * _K), rear=(29.484 * _K, 2.1101 * _K, 3.1651 * _K), swaybar_front=7.2576 * _K, swaybar_rear=4.8384 * _K),
    aero_front=(5.0, 5.0, 0.0, 0.0), aero_rear=(0.0, 0.0, 0.0, 0.0),
    car=dict(year=2021, t60=8.3, t100=24.0, top_mph=129.0, price=25000, pi=0.42, drag=186.1 * 0.29 / 0.33, downforce_front=0.0, downforce_rear=-1.0, wi_force=0.45,
             ratings=(4.0, 5.5, 4.0, 5.0, 4.0), steer_deg=35.0, **{'class': 0}, family_model=1, family_body=1, family_special=3, engine_placement=1, powertrain=0,
             material=1, open_cockpit=0, open_wheel=0, thumbnail_of=1082),
)

# working lamps (fh2re/lightbuild.py): box = ((|x|, y, z) min, max) in FH2 space
LIGHTS = {
    'head': dict(mats=['Carro_Refletor_Farol_1'], box=((0.0, 0.40, 1.50), (1.2, 0.75, 2.2))),            # headlamp units (not the wing repeaters / fog bits)
    'tail': dict(mats=['Carro_Metal_Vermelho', 'Carro_Refletor_Lanterna_1'], box=((0.0, 0.60, -1.80), (1.2, 0.90, -1.40))),  # rear corner lamps (not the spoiler CHMSL)
    'reverse': dict(mats=['Carro_Refletor_Lanterna'], box=((0.0, 0.10, -1.90), (0.2, 0.25, -1.70))),  # the low centre strip in the bumper
    'chmsl': dict(mats=['Carro_Metal_Vermelho'], box=((0.0, 0.95, -1.45), (1.2, 1.25, -1.25))),   # third brake light in the spoiler (light points only)
}
