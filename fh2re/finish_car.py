"""Finish a built car package against a reference car of the same kind, so it behaves and presents like a base-game
car instead of the Charger donor it was built from.

  python3 fh2re/finish_car.py CAR_PKG REFERENCE_PKG OUT_PKG [--version 0.7.2] [--price N] [--profile race]

CAR_PKG / REFERENCE_PKG: Extra Options mod folders (mod.json, database.json, media/cars/<MEDIA>.zip). The reference
is a well-made car of the same type (Toro Rosso STR1 <- ZS Williams FW24). What it does, and why (NOTES: FINISHING):

 1. Rotating inertia (engine, flywheel, transmission, driveline) and the clutch / shift timing from the reference.
    The generic builder leaves the Charger's road flywheel (0.345 kg m2 vs an F1's 0.0025): the engine revs and the
    car accelerates like a lorry.
 2. FreeRevOverrides (throttle delay, rev rise rate, throttle cut) from the reference; the donor has none.
 3. Torque curve: never below the reference's curve at the same fraction of the rev range. Game race engines are
    flattened at the bottom (the FW24 has 89% of peak torque from 0 rpm); real dyno data (CTDP's TJ2005: 12% at
    1,600 rpm, 50% at ~4,900) leaves the car unable to pull away the way the game's own cars do.
 4. Shift system, differential locking, aero drag/lateral drag/wind force, steering lock, car type, class, family,
    Autoshow bucket, ratings, Sim* stats, GameTorqueScale: from the reference (engine-specific Sim fields kept).
 5. Upgrades the base-game way for a race car: ONE stock row per upgrade table at the reference's level (3 = race,
    so tuning is open from stock); the car's own stock values are kept (its race row where tuning ranges live:
    suspension, anti-roll bars, brakes, differential, gearbox); upgrade tables the reference doesn't have
    (turbo, twin turbo, intercooler, CSC) are removed; physics/torque/aero rows nothing references are dropped.
    Race tyre and rim-size options are copied from the reference; the car's own wheels are registered in
    List_Wheels and made its StockWheelID (the donor pointed at the Charger's wheel 11038).
 6. Suspension: progressive springs, bump stops, travel and tuning ranges shaped like the reference's; the static
    ride height keeps the car's own spring-minus-model offset (that pair places the body on the wheels: NOTES DAF),
    and the reference's rake (rear minus front ride height) is added to both the rear spring and rear model height.
 7. Hood camera offsets from the reference (cockpit/chase cameras kept).
 8. The car zip is pruned to what its carbin, skeleton, animations and the remaining files reference (the donor's
    doors, boot, wipers, cabin parts, unused textures and shaders go).
"""
import argparse, copy, json, os, re, shutil, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

INERTIA = {'List_UpgradeEngineFlywheel': ['MomentInertia'], 'List_UpgradeDrivetrainTransmission': ['MomentInertia', 'GearShiftTime'],
           'List_UpgradeDrivetrainDriveline': ['MomentInertia'], 'List_UpgradeDrivetrainClutch': ['ClutchInTime', 'ClutchOutTime'],
           'List_UpgradeDrivetrainDifferential': [k for p in ('Front', 'Rear', 'Center') for k in
                                                  (f'{p}LimitedSlipTorqueAccel', f'{p}LimitedSlipTorqueDecel')]}
CAR_COPY = ['CarTypeID', 'ClassID', 'FamilyModelID', 'FamilyBodyID', 'FamilySpecialID', 'PerformanceIndex', 'SteerMaxAngle',
            'SteerMaxAngleFiltered', 'BodyAeroLongitudinalDrag', 'BodyAeroLateralDragFront', 'BodyAeroLateralDragRear',
            'BodyAeroWIForceScale', 'GameTorqueScale', 'SpeedRating', 'HandlingRating', 'AccelerationRating', 'BrakingRating',
            'LaunchRating', 'MaxUpgradeWizardPerfRating', 'SimTimeQuarterMile', 'SimSpeedQuarterMile', 'SimBrakeDistance60MPH',
            'SimBrakeDistance100MPH', 'SimLatGees60MPH', 'SimLatGees120MPH']
TUNING_ROW = {'List_UpgradeSpringDamper', 'List_UpgradeAntiSwayFront', 'List_UpgradeAntiSwayRear', 'List_UpgradeDrivetrainTransmission'}
PHYS = {'SpringDamperPhysicsID': 'List_SpringDamperPhysics', 'AntiSwayPhysicsID': 'List_AntiSwayPhysics'}
EXTRA_OPTIONS = ('List_UpgradeRimSizeFront', 'List_UpgradeRimSizeRear', 'List_UpgradeTireCompound')


def tables(path): return json.load(open(os.path.join(path, 'database.json')))


def ins(D, t): return D['tables'].get(t, {}).get('insert', [])


def stock(D, t):
    r = [x for x in ins(D, t) if x.get('IsStock', 1) == 1]; return r[0] if r else None


def copy_defaults(D, key, stock_id, race_id):
    """the race physics row (tuning ranges) takes the stock row's default values: same car, now adjustable"""
    hit = next(((k, v) for k, v in PHYS.items() if key.endswith(k)), None)
    if not hit or stock_id == race_id: return
    pk, t = hit; rows = {r[pk]: r for r in ins(D, t)}; s, r = rows.get(stock_id), rows.get(race_id)
    if s and r:
        for k, v in s.items():
            if k.startswith('Def'): r[k] = v


def car_ids(D):
    c = ins(D, 'Data_Car')[0]; return c['Id'], c['MediaName']


def remap(row, old, new):
    """move a reference row's ids onto this car: old car id -> new (exact, *1000 ranges, 10000+ wheel ids)"""
    r = dict(row)
    for k, v in r.items():
        if isinstance(v, int) and not isinstance(v, bool):
            if v == old: r[k] = new
            elif old * 1000 <= v < old * 1000 + 1000: r[k] = new * 1000 + v - old * 1000
            elif v == 10000 + old: r[k] = 10000 + new
    return r


def finish(car, ref, out, version, price, log=print, do_prune=True, drop_old_parts=False):
    C, R = tables(car), tables(ref); cid, media = car_ids(C); rid, rmedia = car_ids(R)
    T = C['tables']; car_row = ins(C, 'Data_Car')[0]; ref_row = ins(R, 'Data_Car')[0]

    # 1-2. inertia, clutch/shift timing, diff locking, free-rev behaviour
    eng = ins(C, 'Data_Engine')[0]; reng = ins(R, 'Data_Engine')[0]
    log(f'engine inertia {eng["MomentInertia"]} -> {reng["MomentInertia"]}'); eng['MomentInertia'] = reng['MomentInertia']
    ins(C, 'Data_Drivetrain')[0]['ShiftSystemID'] = ins(R, 'Data_Drivetrain')[0]['ShiftSystemID']
    T['FreeRevOverrides'] = {'key': [], 'insert': [dict(stock(R, 'FreeRevOverrides') or ins(R, 'FreeRevOverrides')[0], Ordinal=cid)]}

    # 3. torque curves: never below the reference's curve at the same fraction of the rev range
    rc = ins(R, 'List_TorqueCurve')[0]; rv = [rc[f'v{i}'] for i in range(rc['NumTorqueValues'])][:-1]
    for tc in ins(C, 'List_TorqueCurve'):
        n = tc['NumTorqueValues']; raised = 0
        for i in range(n - 1):
            j = round(i / (n - 2) * (len(rv) - 1)); r_ = rv[j]
            if tc[f'v{i}'] >= 0 and r_ > tc[f'v{i}']: tc[f'v{i}'] = r_; raised += 1
        log(f'torque curve {tc["TorqueCurveID"]}: {raised} of {n - 1} points raised to the reference shape (low end {tc["v0"]:.2f})')

    # 5. upgrades: one stock row per table, at the reference's level
    for t in [t for t in T if t.startswith('List_Upgrade')]:
        rows = ins(C, t)
        if t in EXTRA_OPTIONS: continue
        if t not in R['tables']:
            if all(r.get('IsStock') == 0 for r in rows): del T[t]; log(f'{t}: removed (the reference has none)'); continue
        rs = stock(R, t)
        if t in TUNING_ROW:      # the race row (the reference's stock level), else the highest
            lv = rs.get('Level') if rs else None
            keep = next((r for r in rows if r.get('Level') == lv), None) or max(rows, key=lambda r: r.get('Level', 0))
        else: keep = stock(C, t) or rows[0]
        st0 = stock(C, t)
        if t in TUNING_ROW and st0 is not None and keep is not st0:      # race row for its tuning ranges, stock defaults
            for k, v in st0.items():
                if k.endswith('PhysicsID'):
                    copy_defaults(C, k, v, keep[k])
        keep = dict(keep, IsStock=1, Price=0)
        if rs is not None and 'Level' in rs: keep['Level'] = rs['Level']
        for f in INERTIA.get(t, []):
            if rs is not None and f in rs: keep[f] = rs[f]
        if t == 'List_UpgradeDrivetrainTransmission':          # race gearbox row, the car's own ratios
            st = stock(C, t)
            for k in st:
                if k.startswith('GearRatio') or k in ('FinalDriveRatio', 'NumGears'): keep[k] = st[k]
        if t == 'List_UpgradeEngineFlywheel': log(f'flywheel inertia {stock(C, t)["MomentInertia"]} -> {keep["MomentInertia"]}')
        if 'Id' in keep: keep['Id'] = (stock(C, t) or keep)['Id']
        T[t]['insert'] = [keep]
    # SAVE SAFETY (3 Nov, found the hard way): a save stores the IDs of the parts fitted to each owned car. A car whose
    # fitted part (or tune) no longer exists hangs the game on the loading screen when it spawns. So the old upgrade
    # rows stay in the database unless --drop-old-parts is given, which is only safe once every saved copy of the car
    # has been set back to stock parts with no tune (or sold).
    if not drop_old_parts:
        orig = tables(car)['tables']; kept = 0
        for t, v in orig.items():
            if not (t.startswith('List_Upgrade') or t in ('List_SpringDamperPhysics', 'List_AntiSwayPhysics', 'List_TorqueCurve', 'List_AeroPhysics')): continue
            ks = v.get('key') or []; T.setdefault(t, {'key': v.get('key'), 'insert': []})
            have = {tuple(r.get(k) for k in ks) for r in T[t]['insert']}
            for r in v.get('insert', []):
                if ks and tuple(r.get(k) for k in ks) not in have: T[t]['insert'].append(r); kept += 1
        log(f'save safety: {kept} old upgrade/physics rows kept so saved cars still find their parts (--drop-old-parts to remove)')

    # race tyres, rim sizes, the car's own wheel as a wheel part
    for t in EXTRA_OPTIONS:
        T[t] = {'key': R['tables'][t]['key'], 'insert': [remap(r, rid, cid) for r in ins(R, t)]}
    wheel = remap(ins(R, 'List_Wheels')[0], rid, cid); wheel.update(MediaName=media, IconPath=media)
    T['List_Wheels'] = {'key': ['ID'], 'insert': [wheel]}; car_row['StockWheelID'] = wheel['ID']
    log(f"tyres {[r['TireModelName'] for r in T['List_UpgradeTireCompound']['insert']]}, rims {[r['FrontWheelDiameter'] for r in T['List_UpgradeRimSizeFront']['insert']]}, StockWheelID {wheel['ID']}")

    # unreferenced physics rows
    used = {v for t, x in T.items() if t.startswith('List_Upgrade') for r in x.get('insert', []) for k, v in r.items() if k.endswith(('PhysicsID', 'FullThrottleID'))}
    for t, key in ((('List_SpringDamperPhysics', 'SpringDamperPhysicsID'), ('List_AntiSwayPhysics', 'AntiSwayPhysicsID'),
                   ('List_AeroPhysics', 'AeroPhysicsID'), ('List_TorqueCurve', 'TorqueCurveID')) if drop_old_parts else ()):
        before = len(ins(C, t)); T[t]['insert'] = [r for r in ins(C, t) if r[key] in used]
        if before != len(ins(C, t)): log(f'{t}: {before} -> {len(ins(C, t))} rows')

    # 6. suspension shape and rake
    sd = stock(C, 'List_UpgradeSpringDamper'); rsd = stock(R, 'List_UpgradeSpringDamper')
    body = ins(C, 'Data_CarBody')[0]; rbody = ins(R, 'Data_CarBody')[0]
    rphys = {r['SpringDamperPhysicsID']: r for r in ins(R, 'List_SpringDamperPhysics')}
    rf, rr = rphys[rsd['FrontSpringDamperPhysicsID']], rphys[rsd['RearSpringDamperPhysicsID']]
    rake = (rr['DefRideHeight'] - rf['DefRideHeight'])
    for end, pid, ref_p in (('Front', sd['FrontSpringDamperPhysicsID'], rf), ('Rear', sd['RearSpringDamperPhysicsID'], rr)):
        p = next(r for r in ins(C, 'List_SpringDamperPhysics') if r['SpringDamperPhysicsID'] == pid)
        if end == 'Rear' and rake:
            p['DefRideHeight'] += rake; body['ModelRearStockRideHeight'] += rake; car_row['RearStockRideHeight'] = body['ModelRearStockRideHeight']
        d = p['DefRideHeight']; s = p['DefSpringRate'] / ref_p['DefSpringRate']
        p.update(UseProgressiveSpring=ref_p['UseProgressiveSpring'], BumpstopStiffness=ref_p['BumpstopStiffness'], BumpstopDamping=ref_p['BumpstopDamping'],
                 MinRideHeight=d, MaxRideHeight=d + ref_p['MaxRideHeight'] - ref_p['DefRideHeight'],
                 MaxCompressHeight=d - (ref_p['DefRideHeight'] - ref_p['MaxCompressHeight']), MaxStretchDeltaFromRideHeight=d,
                 MinSpringRate=round(ref_p['MinSpringRate'] * s, 3), MaxSpringRate=round(ref_p['MaxSpringRate'] * s, 3),
                 MinDampenBumpRate=ref_p['MinDampenBumpRate'], MaxDampenBumpRate=ref_p['MaxDampenBumpRate'],
                 MinDampenReboundRate=ref_p['MinDampenReboundRate'], MaxDampenReboundRate=ref_p['MaxDampenReboundRate'])
        log(f'{end} suspension: ride {d:.4f} (model {body["Model" + end + "StockRideHeight"]:.4f}), travel {d - p["MaxCompressHeight"]:.3f}, '
            f'springs {p["MinSpringRate"]}-{p["MaxSpringRate"]} progressive, bump stop {p["BumpstopStiffness"]}')

    # aero drag of the wings
    aero = {r['AeroPhysicsID']: r for r in ins(C, 'List_AeroPhysics')}; raero = {r['AeroPhysicsID']: r for r in ins(R, 'List_AeroPhysics')}
    for t, k in (('List_UpgradeCarBodyFrontBumper', 'AeroPhysicsID'), ('List_UpgradeRearWing', 'AeroPhysicsID')):
        a, b = aero.get(stock(C, t)[k]), raero.get(stock(R, t)[k])
        if a and b:
            for f in ('Drag0', 'Drag1', 'LateralDrag', 'AngleZeroDownforce'): a[f] = b[f]

    # 4. car-level identity and handling numbers
    for k in CAR_COPY:
        if k in ref_row: car_row[k] = ref_row[k]
    car_row['BaseCost'] = price
    T['Data_Car_Buckets']['insert'][0]['CarBucket'] = ins(R, 'Data_Car_Buckets')[0]['CarBucket']
    log(f"class {car_row['ClassID']} PI {car_row['PerformanceIndex']}, type {car_row['CarTypeID']}, bucket {T['Data_Car_Buckets']['insert'][0]['CarBucket']}, "
        f"steer {car_row['SteerMaxAngle']}, drag {car_row['BodyAeroLongitudinalDrag']}, price {price}")

    # 7. hood camera
    cam, rcam = ins(C, 'CameraOverrides')[0], ins(R, 'CameraOverrides')[0]
    for k in rcam:
        if k.startswith('CamHood'): cam[k] = rcam[k]

    # write the package
    if os.path.exists(out): shutil.rmtree(out)
    shutil.copytree(car, out, ignore=shutil.ignore_patterns('media'))
    json.dump(C, open(os.path.join(out, 'database.json'), 'w'), indent=1)
    m = json.load(open(os.path.join(car, 'mod.json'))); m['version'] = version; json.dump(m, open(os.path.join(out, 'mod.json'), 'w'), indent=1)
    for root, dirs, files in os.walk(os.path.join(car, 'media')):
        for f in files:
            src = os.path.join(root, f); dst = os.path.join(out, os.path.relpath(src, car)); os.makedirs(os.path.dirname(dst), exist_ok=True)
            if do_prune and f.lower() == f'{media.lower()}.zip': prune(src, dst, media, log)
            else: shutil.copy2(src, dst)


def prune(src, dst, media, log=print):
    """drop the donor's part models the carbin no longer uses (doors, boot, cabin parts, lamps...) and the textures that
    only belong to them (their AO maps, the wiper set). Everything else is kept: textures are referenced by CRC as well
    as by name, and the shader folders by directory, so nothing is pruned on a name search alone."""
    from carbin import read_carbin
    Z = zipfile.ZipFile(src); names = Z.namelist()
    carb = read_carbin(Z.read(next(n for n in names if n.lower().endswith('.carbin'))))
    want = {os.path.basename(m['path'].replace('\\', '/')).lower() for pt in carb['parts'] for m in pt['part']['models']}
    skel = {n for n in names if '_skeleton.' in n.lower()}
    dead = [n for n in names if n.lower().startswith('scene/') and n.lower().endswith('.modelbin') and n not in skel
            and '/drivers/' not in n.lower() and os.path.basename(n).lower() not in want]
    stems = [os.path.splitext(os.path.basename(n))[0].lower() for n in dead]
    def orphan_tex(n):
        l = n.lower(); b = os.path.splitext(os.path.basename(l))[0]
        return l.startswith('textures/wiper') or (l.startswith('textures/ao/') or l.endswith('_ao.swatchbin')) and any(b.startswith(st) for st in stems)
    gone = set(dead) | {n for n in names if orphan_tex(n)}
    # anything a kept file still names (carbin AO paths, cinematics, Lights.bin...) stays; SizeReport/carbin_debug are reports
    text = {n: (b'' if n.lower().endswith(('.swatchbin', '.pso', '.vso')) or n.lower().endswith(('sizereport.xml', '.carbin_debug'))
                else Z.read(n).lower()) for n in names}
    while True:
        blob = b'\n'.join(text[n] for n in names if n not in gone)
        back = {g for g in gone if os.path.splitext(os.path.basename(g))[0].lower().encode() in blob}
        if not back: break
        gone -= back
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        for i in Z.infolist():
            if i.filename not in gone: zo.writestr(i, Z.read(i.filename))
    dead = [d for d in dead if d in gone]
    log(f'car zip: {len(names)} -> {len(names) - len(gone)} files, {os.path.getsize(src) / 1e6:.1f} -> {os.path.getsize(dst) / 1e6:.1f} MB; '
        f'dropped {len(dead)} unused part models ({", ".join(sorted(os.path.basename(g) for g in dead)[:8])}...) + {len(gone) - len(dead)} of their textures')
    return sorted(gone)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('car'); ap.add_argument('reference'); ap.add_argument('out')
    ap.add_argument('--version', default=None); ap.add_argument('--price', type=int, default=None); ap.add_argument('--no-prune', action='store_true'); ap.add_argument('--drop-old-parts', action='store_true')
    a = ap.parse_args()
    ref_price = ins(tables(a.reference), 'Data_Car')[0]['BaseCost']
    finish(a.car, a.reference, a.out, a.version or json.load(open(os.path.join(a.car, 'mod.json')))['version'] + '-finished', a.price or ref_price, do_prune=not a.no_prune, drop_old_parts=a.drop_old_parts)
