"""project.json (FH2 Car Studio) -> the spec module build_car.py / build_car_db.py / package_car.py read.

A studio car's cars/<slug>/spec.py is just:
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'studio'))
    from projectspec import load; globals().update(load(__file__))
Everything the hand-written specs (cars/omoda5/spec.py, cars/dafxf105/spec.py) set by hand is derived here.
"""
import os, json, pickle, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
HUB_Y, AXLE_MID, RIDE_HEIGHT = 0.156, 0.0867, 0.1625

CYL_ID = {3: 11, 4: 1, 5: 2, 6: 3, 8: 4, 10: 5, 12: 6, 16: 7}
CONFIG_ID = {'I': 3, 'V': 1, 'F': 5, 'W': 2, 'R': 4}
ASP_ID = {'na': 1, 'turbo': 2, 'twin': 3, 'super': 5}
ASP_NAME = {'na': '', 'turbo': ' - Turbo', 'twin': ' - Twin Turbo', 'super': ' - Supercharged'}
DRIVE_ID = {'FWD': 1, 'RWD': 2, 'AWD': 3}
PLACEMENT_ID = {'front': 1, 'mid': 2, 'rear': 3}
CLASS_PI = [(0, 0.4345), (1, 0.525628), (2, 0.6179), (3, 0.748432), (4, 0.846368), (5, 0.997086), (6, 9.0)]
CLASS_NAMES = ['D', 'C', 'B', 'A', 'S1', 'S2', 'X']
# least-squares fits over every stock car: [1, ln(hp/kg), ln(top mph), ln(0-60 s), (front+rear tyre mm)/kg]
FITS = {'pi': [1.0387, 0.1761, 0.0442, -0.2309, -0.0725], 'speed': [-14.984, 0.5069, 4.2821, 0.0272, -0.041],
        'handling': [10.5776, 0.3878, -0.3372, -1.4139, 1.4142], 'accel': [11.6317, 1.6582, 0.0086, -0.9898, -0.5416],
        'braking': [13.5845, 0.4864, -0.5456, -1.8521, 1.7228], 'launch': [20.0577, 0.2493, -1.268, -3.1845, -0.956]}


def safe(s): return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_') or 'x'


def torque_curve(hp, nm, rpm_t, rpm_p, redline, aspiration):
    """a plausible curve through the quoted figures: peak torque at rpm_t (held to ~0.75 rpm_p on turbo engines),
    peak power at rpm_p, tailing off to the limiter"""
    Tp = hp * 7120.9 / rpm_p                       # torque at the power peak (Nm)
    T = max(nm, Tp)
    hold = max(rpm_t, 0.75 * rpm_p) if aspiration in ('turbo', 'twin') else rpm_t
    pts = {0: 0.45 * T, int(rpm_t * 0.5): 0.78 * T, int(rpm_t): T}
    if hold > rpm_t + 200: pts[int(hold)] = T * 0.99
    pts[int(rpm_p)] = min(Tp, T); pts[int(redline)] = min(Tp, T) * 0.88
    return sorted(pts.items())


def estimates(c, A):
    """0-60, 0-100, top speed, PI, ratings, class from the specs (fits over the stock cars)"""
    kg, hp = c['mass'], c['hp']
    t60 = c.get('t60') or round(1.18 * (kg / hp) ** 0.95, 1)
    t100 = round(t60 * (2.4 + 0.07 * kg / hp), 1)
    top = c.get('top_mph') or round(19.8 * (hp / (c['cd'] * A)) ** (1 / 3))
    x = np.array([1, np.log(hp / kg), np.log(top), np.log(t60), (c['tyre_fw'] + c['tyre_rw']) / kg])
    f = {k: float(np.dot(v, x)) for k, v in FITS.items()}
    pi = float(np.clip(f['pi'], 0.05, 0.99))
    cls = next(i for i, lim in CLASS_PI if pi <= lim)
    ratings = tuple(round(float(np.clip(f[k], 1.0, 10.0)), 1) for k in ('speed', 'handling', 'accel', 'braking', 'launch'))
    return dict(t60=t60, t100=t100, top_mph=top, pi=round(pi, 3), cls=cls, cls_name=CLASS_NAMES[cls], ratings=ratings)


def geo_dims(geo):
    G = pickle.load(open(geo, 'rb'))
    V = np.concatenate([p['V'] for k, v in G['parts'].items() if not k.startswith('RIM_') for p in v])
    lo, hi = V.min(0), V.max(0)
    return G, lo, hi


def lamp_boxes(G, lights):
    """per lamp: the box (|x|, y, z) around its materials' triangles in the front (head/drl/turn_f) or rear half"""
    out = {}
    for kind, mats in lights.items():
        if not mats: continue
        front = kind in ('head', 'drl', 'turn_f'); C = []
        for m in mats:
            for p in G['parts'].get(m, []):
                c = p['V'].reshape(-1, 3, 3).mean(1); C.append(c[(c[:, 2] > 0) if front else (c[:, 2] < 0)])
        C = np.concatenate(C) if C else np.zeros((0, 3))
        if not len(C): continue
        a = np.c_[np.abs(C[:, 0]), C[:, 1:]]
        out[kind] = dict(mats=list(mats), box=(tuple((a.min(0) - 0.01).round(3)), tuple((a.max(0) + 0.01).round(3))))
    return out


def load(spec_file):
    car_dir = os.path.dirname(os.path.abspath(spec_file))
    J = json.load(open(os.path.join(car_dir, 'project.json')))
    ids = J['ids']; c = J['car']; W = J['wheels']; MEDIA = ids['media']
    s = J['real_wheelbase'] / (W['zf'] - W['zr']); r = W['r'] * s
    geo = os.path.join(car_dir, 'geo.pkl')
    G, lo, hi = geo_dims(geo)
    length, height = float(hi[2] - lo[2]), float(hi[1] - lo[1] + (lo[1] - (HUB_Y - r)))   # height from the ground
    width = float(c.get('width') or (hi[0] - lo[0]) * 0.93)

    # ---------------------------------------------------------------- materials and textures
    tex_dir = os.path.join(car_dir, 'src'); TEXTURES, MATERIALS = {}, {}
    for name, m in J['materials'].items():
        role = m['role']
        if role in ('paint', 'chrome', 'black', 'glass'): MATERIALS[name] = ('plain', role)
        elif role == 'texture':
            fn = os.path.join(tex_dir, f'tex_{safe(name)}.png')
            if os.path.exists(fn): TEXTURES[safe(name)] = (Image.open(fn), 1024, True); MATERIALS[name] = ('textured', safe(name))
            else: MATERIALS[name] = ('plain', 'black')
        elif role == 'colour':
            h = m.get('colour', '#999999').lstrip('#'); rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            key = 'c_' + h; TEXTURES[key] = (Image.new('RGB', (64, 64), rgb), 512, False); MATERIALS[name] = ('textured', key)
        else: MATERIALS[name] = None
    for name in G['parts']:
        if name.startswith('RIM_'): MATERIALS[name] = None
    WM = J.get('wheel_materials', {})
    RIM_MATERIALS = [k for k, v in WM.items() if v == 'silver' and k in G['parts']]
    RIM_BLACK_MATERIALS = [k for k, v in WM.items() if v == 'black' and k in G['parts']]

    # ---------------------------------------------------------------- driver
    D = J['driver']; st = np.array(D['steer'], float)
    hips = st + [-0.015, -0.28, -0.43]; eye = hips + [0, 0.62, 0]

    # ---------------------------------------------------------------- physics
    asp = c['aspiration']; cyl = int(c['cylinders']); diesel = c.get('fuel') == 'diesel'
    curve = torque_curve(c['hp'], c['nm'], c['rpm_torque'], c['rpm_power'], c['redline'], asp)
    A = width * height; est = estimates(c, A)
    if c.get('class_override') not in (None, '', 'auto'): est['cls'] = CLASS_NAMES.index(c['class_override'])
    K = c['mass'] / 970
    drive = c['drive']; place = c.get('engine_pos', 'front')
    mounting = 0 if place == 'mid' else 2 if drive == 'FWD' else 1
    powertrain = {('front', 'FWD'): 0, ('front', 'RWD'): 1, ('mid', 'RWD'): 2, ('rear', 'RWD'): 3, ('front', 'AWD'): 4,
                  ('mid', 'AWD'): 5, ('rear', 'AWD'): 4, ('mid', 'FWD'): 0, ('rear', 'FWD'): 0}[(place, drive)]
    auto_box = c.get('transmission', 'manual') == 'auto'
    track_mode = J.get('track_mode', 'auto')
    if not any(v == ('plain', 'paint') for v in MATERIALS.values()): track_mode = 'tyres'
    tr = lambda: round(2 * (W['xh'] * s + 0.05), 3)
    disp = float(c['displacement_l'])
    eng_name = f"{disp:.1f}L {c['layout']}{cyl}{ASP_NAME[asp]}" + (' Diesel' if diesel else '')
    if c['make_mode'] == 'new':
        make, make_code, country, icon = c['make_name'], c['make_code'].upper()[:3], int(c['make_country']), safe(c['make_name']).replace('_', '')
    else:
        make, make_code, country, icon = c['make_name'], c.get('make_code') or 'XXX', int(c.get('make_country') or 9), c.get('make_icon') or safe(c['make_name'])
    PHYSICS = dict(
        car_id=ids['car_id'], make_offset=ids['make_offset'], make=make, make_profile=c.get('make_profile') or make, make_code=make_code,
        make_country=country, make_icon=icon, string_base=ids['string_base'], colour_offset=ids['colour_offset'],
        name=c['model_name'], short_name=c.get('short_name') or c['model_name'],
        engine=dict(name=eng_name, sound=c['sound'], mass=round(40 * disp + 60, 1), compression=17.0 if diesel else 10.0,
                    config=CONFIG_ID[c['layout']], cylinders=CYL_ID.get(cyl, 1), aspiration=ASP_ID[asp], boost=1.4 if asp != 'na' else 0.0,
                    inertia=round(0.06 * disp + 0.05, 3), tank=c.get('tank', 55), displacement=int(disp * 1000), peak_hp=c['hp'], peak_nm=c['nm'],
                    redline=int(c['redline']), stall=550.0 if diesel else 750.0, start=1200.0 if diesel else 3000.0, curve=curve),
        drivetrain=dict(drivetype=DRIVE_ID[drive], mounting=mounting, shift_system=4 if auto_box else 1, gears=[float(g) for g in c['gears']][:8],
                        final_drive=float(c['final_drive']), reverse=-3.5, shift_time=0.12 if auto_box else 0.25, lsd=(0.0, 0.0, 0.0, 0.0),
                        clutch_nm=round(2.5 * max(c['nm'], 100), 0)),
        body=dict(mass=float(c['mass']), weight_front=float(c['weight_front']), cm_height=round((0.28 if height > 2.5 else 0.37) * height, 3),
                  block=(round(width, 3), round(0.76 * height, 3), round(length, 3)), height=round(height, 3), length=round(length, 3), width=round(width, 3),
                  wheelbase=J['real_wheelbase'], model_wheelbase=J['real_wheelbase'],
                  track_front='auto' if track_mode == 'auto' else tr(), track_rear='auto' if track_mode == 'auto' else tr(),
                  ride_height=RIDE_HEIGHT, bbox=tuple(round(float(v), 2) for v in (lo[0], hi[0], HUB_Y - r, hi[1], lo[2], hi[2]))),
        tyres=dict(width_front=int(c['tyre_fw']), width_rear=int(c['tyre_rw']), aspect_front=int(c['tyre_fa']), aspect_rear=int(c['tyre_ra']),
                   rim_in=int(c['rim_in']), compound=int(c.get('compound', 4))),
        brakes=dict(front_mm=float(c['brake_f']), front_type=2, front_pistons=2 if c['mass'] > 2500 else 1, rear_mm=float(c['brake_r']),
                    rear_type=2 if c['brake_r'] >= 300 else 1, rear_pistons=1, friction=1.0),
        suspension=dict(front=(46.116 * K, 3.3003 * K, 4.9505 * K), rear=(29.484 * K, 2.1101 * K, 3.1651 * K),
                        swaybar_front=7.2576 * K, swaybar_rear=4.8384 * K),
        aero_front=(5.0, 5.0, 0.0, 0.0), aero_rear=(0.0, 0.0, 0.0, 0.0),
        car=dict(year=int(c['year']), t60=est['t60'], t100=est['t100'], top_mph=float(est['top_mph']), price=int(c['price']), pi=est['pi'],
                 drag=round(186.1 * c['cd'] / 0.33 * A / 2.52, 2), downforce_front=0.0, downforce_rear=-1.0, wi_force=round(0.19 * A, 3),
                 ratings=est['ratings'], steer_deg=float(c.get('steer_deg', 35)), **{'class': est['cls']}, bucket=int(c['bucket']),
                 family_model=1, family_body=1, family_special=3, engine_placement=PLACEMENT_ID[place], powertrain=powertrain,
                 material=1, open_cockpit=0, open_wheel=0, thumbnail_of=1082),
    )

    # ---------------------------------------------------------------- presentation
    PRESENT = dict(paint=c.get('paint', 'b0b0b4').lstrip('#'))
    if c['make_mode'] == 'existing':
        PRESENT['use_make'] = (int(c['make_id']), c['make_ref'])
        if c.get('make_depends'): PRESENT['depends'] = c['make_depends']
    else:
        logo = os.path.join(tex_dir, 'logo.png')
        if os.path.exists(logo): PRESENT['logo_png'] = logo
        else: PRESENT['logo_text'] = c['make_name'].upper()
        PRESENT['icon_base'] = icon

    out = dict(
        MEDIA=MEDIA, DONOR_ZIP=os.path.join(car_dir, f'donor_{MEDIA}.zip'), GEO=geo, TEXTURES=TEXTURES, MATERIALS=MATERIALS,
        BODY_PLAIN={'paint': (0, 'carpaint'), 'chrome': (0, 'frame'), 'black': (1, 'blkplastic_hgl')},
        BODY_TEXTURED_LIKE={0: 'carpaint', 3: 'carpaint'}, GLASS_PLAIN={'glass': (0, 'gls_windsheild')},
        RIM_MATERIALS=RIM_MATERIALS, RIM_BLACK_MATERIALS=RIM_BLACK_MATERIALS, RIM_TRUST_NORMALS=True,
        ONE_SIDED=bool(J.get('one_sided', True)), TRANSFER_UV='roof', LIP_GAP=float(J.get('lip_gap', 0.04)),
        KEEP_PARTS={'body_a.modelbin', 'glassf_a.modelbin'},
        STEER=tuple(st.round(3)), HIPS=tuple(hips.round(3)), EYE=tuple(eye.round(3)), DRIVER_ANIMS_ZIP=None, AVPINS_TEMPLATE=None,
        PHYSICS=PHYSICS, PRESENT=PRESENT, ESTIMATES=est,
    )
    L = lamp_boxes(G, {k: v for k, v in J.get('lights', {}).items() if v})
    if L: out['LIGHTS'] = L
    if J.get('collision', True):
        out['COLLISION_HULL'] = dict(half_width=round(width / 2, 3), floor_y=round(HUB_Y - r + float(np.clip(0.13 * height, 0.15, 0.40)), 3))
    return out
