"""Database for a car on the Charger generic donor: clone the donor's rows (car 1422, engine 882, drivetrain 830)
to new ids and overwrite them from the spec's PHYSICS dict. Then:
  python3 eo/tools/mod_diff.py database car207/vanilla.slt <out.slt> -o database.json --updates override --force
and set policy.id_conflicts to "nearest".
usage: build_car_db.py cars/<car>/spec.py out.slt strings.json
"""
import sys, os, sqlite3, shutil, math, json, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec_path, DST, STRINGS_OUT = sys.argv[1:4]
_s = importlib.util.spec_from_file_location('carspec', spec_path); S = importlib.util.module_from_spec(_s); _s.loader.exec_module(S)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fh2re')); import autotrack; autotrack.apply(S)   # track_front/rear = 'auto'
P = S.PHYSICS; MEDIA = S.MEDIA
SRC = f'{HERE}/car207/vanilla.slt'
CAR_OLD, CAR = 1422, P['car_id']; ENG_OLD, ENG = 882, P['car_id']; DT_OLD, DT = 830, P['car_id']

shutil.copy(SRC, DST); c = sqlite3.connect(DST); q = lambda s, *a: c.execute(s, a).fetchall()
def cols(t): return [r[1] for r in c.execute(f'pragma table_info("{t}")')]
def clone(table, where, args, remap):
    cs = cols(table); rows = [dict(zip(cs, r)) for r in q(f'select * from "{table}" where {where}', *args)]
    for r in rows:
        remap(r); c.execute(f'insert into "{table}" ({",".join(chr(34)+x+chr(34) for x in cs)}) values ({",".join("?"*len(cs))})', [r[x] for x in cs])
    return rows
def shift(v, old, new):
    if isinstance(v, int):
        if v == old: return new
        if old * 1000 <= v <= old * 1000 + 999: return new * 1000 + (v - old * 1000)
    return v
def car_remap(r):
    for k, v in r.items():
        if k.lower() in ('id', 'ordinal', 'carid', 'modelid') or isinstance(v, int) and CAR_OLD * 1000 <= v <= CAR_OLD * 1000 + 999: r[k] = shift(v, CAR_OLD, CAR)

# ---------------------------------------------------------------- make
make_id = q('select max(ID) from List_CarMake')[0][0] + P['make_offset']
mk_hash = int(q("select MakeName from Data_Car where Id=?", CAR_OLD)[0][0][2:]) >> 16
car_hash = int(q("select DisplayName from Data_Car where Id=?", CAR_OLD)[0][0][2:]) >> 16
mk_table_hash = int(q("select DisplayName from List_CarMake where ID=107")[0][0][2:]) >> 16
S_MAKE, S_MAKE_PROFILE, S_CARMAKE = P['string_base'], P['string_base'] + 1, P['string_base'] + 2
S_NAME, S_SHORT = P['string_base'], P['string_base'] + 1
ren = dict(zip(cols('List_CarMake'), q('select * from List_CarMake where ID=107')[0]))
ren.update(ID=make_id, DisplayName=f'_&{(mk_table_hash << 16) | S_MAKE}', ManufacturerCode=P['make_code'], CountryID=P['make_country'],
           IconPathBase=P['make_icon'], Profile=f'_&{(mk_table_hash << 16) | S_MAKE_PROFILE}')
c.execute(f'insert into List_CarMake values ({",".join("?"*len(ren))})', list(ren.values()))

# ---------------------------------------------------------------- car-level tables
car_tables = ['Data_Car', 'Data_CarBody', 'CameraOverrides', 'CarPartPositions', 'Data_Car_Buckets', 'List_AntiSwayPhysics',
              'List_SpringDamperPhysics', 'List_UpgradeAntiSwayFront', 'List_UpgradeAntiSwayRear', 'List_UpgradeBrakes', 'List_UpgradeCarBody',
              'List_UpgradeCarBodyChassisStiffness', 'List_UpgradeCarBodyFrontBumper', 'List_UpgradeCarBodyHood', 'List_UpgradeCarBodyRearBumper',
              'List_UpgradeCarBodySideSkirt', 'List_UpgradeCarBodyTireWidthFront', 'List_UpgradeCarBodyTireWidthRear', 'List_UpgradeCarBodyWeight',
              'List_UpgradeRearWing', 'List_UpgradeRimSizeFront', 'List_UpgradeRimSizeRear', 'List_UpgradeSpringDamper', 'List_UpgradeTireCompound']
for t in car_tables:
    cs = cols(t); where, a = [], []
    for k in cs:
        if k.lower() in ('id', 'ordinal', 'carid', 'modelid'):
            where.append(f'"{k}"=?'); a.append(CAR_OLD); where.append(f'"{k}" between ? and ?'); a += [CAR_OLD * 1000, CAR_OLD * 1000 + 999]
    rows = q(f'select rowid from "{t}" where ' + ' or '.join(where), *a)
    clone(t, 'rowid in (%s)' % ','.join(str(r[0]) for r in rows), [], car_remap)
# Autoshow category (Data_Car_Buckets.CarBucket; the Charger's 31 = Modern Muscle): 23 Hot Hatch, 25 Super Hot Hatch,
# 19 Super Saloons, 38 Unlimited Off-road (Raptor, Ram Runner), 39 SUVs (X5 M, Cayenne), 40 Off-road (H1, Gurkha)
if P['car'].get('bucket'): c.execute('update Data_Car_Buckets set CarBucket=?, BucketHero=0 where CarId=?', (P['car']['bucket'], CAR))
clone('List_UpgradeEngine', 'Ordinal=? and IsStock=1', [CAR_OLD], lambda r: (car_remap(r), r.update(EngineID=ENG, ManufacturerID=make_id)))
clone('List_UpgradeDrivetrain', 'Ordinal=? and IsStock=1', [CAR_OLD], lambda r: (car_remap(r), r.update(DrivetrainID=DT, ManufacturerId=make_id)))
next_col = q('select max(ID) from Combo_Colors')[0][0] + P['colour_offset']
def col_remap(r):
    global next_col
    r['Ordinal'] = CAR; r['ID'] = next_col; next_col += 1
clone('Combo_Colors', 'Ordinal=?', [CAR_OLD], col_remap)

# aero rows of our own (the donor's are shared ids), no aftermarket kits
next_aero = q('select max(AeroPhysicsID) from List_AeroPhysics')[0][0] + 1
def own_aero(table, key, val, front):
    global next_aero
    cs = cols('List_AeroPhysics'); a = P['aero_front' if front else 'aero_rear']
    for rid, aid in q(f'select Id, AeroPhysicsID from "{table}" where "{key}"=? and IsStock=1', val):
        src_row = q('select * from List_AeroPhysics where AeroPhysicsID=?', aid) or q('select * from List_AeroPhysics where AeroPhysicsID=?', aid - (CAR - CAR_OLD) * 1000)
        row = dict(zip(cs, src_row[0])); row.update(AeroPhysicsID=next_aero, Drag0=a[0], Drag1=a[1], Downforce0=a[2], Downforce1=a[3], DefaultTuneSlider=0.5)
        c.execute(f'insert into List_AeroPhysics values ({",".join("?" * len(cs))})', [row[x] for x in cs])
        c.execute(f'update "{table}" set AeroPhysicsID=? where Id=?', (next_aero, rid)); next_aero += 1
    c.execute(f'delete from "{table}" where "{key}"=? and IsStock=0', (val,))
own_aero('List_UpgradeCarBodyFrontBumper', 'CarBodyID', CAR * 1000, True); own_aero('List_UpgradeRearWing', 'Ordinal', CAR, False)

# ---------------------------------------------------------------- engine
def eng_remap(r):
    for k, v in r.items():
        if k == 'EngineID' or isinstance(v, int) and ENG_OLD * 1000 <= v <= ENG_OLD * 1000 + 999: r[k] = shift(v, ENG_OLD, ENG)
clone('Data_Engine', 'EngineID=?', [ENG_OLD], eng_remap)
for t in [n for (n,) in q("select name from sqlite_master where type='table' and name like 'List_UpgradeEngine%' and name<>'List_UpgradeEngine'")]:
    if 'EngineID' in cols(t): clone(t, 'EngineID=?', [ENG_OLD], eng_remap)
clone('List_TorqueCurve', 'TorqueCurveID between ? and ?', [ENG_OLD * 1000, ENG_OLD * 1000 + 999], eng_remap)
E = P['engine']
c.execute('''update Data_Engine set MediaName=?, "EngineMass-kg"=?, Compression=?, ConfigID=?, CylinderID=?, AspirationID_Stock=?, "StockBoost-bar"=?,
             MomentInertia=?, GasTankSize=?, EngineGraphingMaxTorque=?, EngineGraphingMaxPower=?, EngineName=? where EngineID=?''',
          (E['sound'], E['mass'], E['compression'], E['config'], E['cylinders'], E['aspiration'], E['boost'], E['inertia'], E['tank'],
           E['peak_nm'] * 1.1, E['peak_hp'] * 1.1, E['name'], ENG))
# torque curve: 121 points of 100 rpm, values normalised to the peak, -2.63 = the game's fuel-cut marker
NPTS, STEP = 121, 100; LIMIT = E['redline']; curve = E['curve']                     # [(rpm, Nm)...]
xs, ys = zip(*curve); PEAK = max(ys)
vals = []
for i in range(NPTS):
    rpm = i * STEP
    if rpm <= LIMIT: vals.append(max(float(np.interp(rpm, xs, ys)), 0.0) / PEAK)
    elif rpm == LIMIT + 100: vals.append(-2.63)
    else: vals.append(0.0)
vals[0] = vals[1] = max(vals[10], 0.05)
sets = ', '.join(f'v{i}=?' for i in range(NPTS))
for (cid,) in q('select TorqueCurveID from List_TorqueCurve where TorqueCurveID between ? and ?', ENG * 1000, ENG * 1000 + 999):
    c.execute(f'update List_TorqueCurve set TorqueScale=?, NumTorqueValues=?, {sets} where TorqueCurveID=?', [float(PEAK), NPTS] + vals + [cid])
c.execute('''update List_UpgradeEngineCamshaft set RedlineRPM=?, StallRPM=?, StartRPM=?, TorqueCurveMaxRPM=?, NumRPMEntriesArray=? where EngineID=?''',
          (float(LIMIT), E['stall'], E['start'], float((NPTS - 1) * STEP), NPTS, ENG))
c.execute('update List_UpgradeEngine set ManufacturerID=? where EngineID=?', (make_id, ENG))

# ---------------------------------------------------------------- drivetrain
def dt_remap(r):
    for k, v in r.items():
        if k.lower() == 'drivetrainid' or isinstance(v, int) and DT_OLD * 1000 <= v <= DT_OLD * 1000 + 999: r[k] = shift(v, DT_OLD, DT)
clone('Data_Drivetrain', 'DrivetrainID=?', [DT_OLD], dt_remap)
for t in ('List_UpgradeDrivetrainClutch', 'List_UpgradeDrivetrainDifferential', 'List_UpgradeDrivetrainDriveline', 'List_UpgradeDrivetrainTransmission'):
    key = 'DrivetrainId' if 'DrivetrainId' in cols(t) else 'DrivetrainID'; clone(t, f'"{key}"=?', [DT_OLD], dt_remap)
D = P['drivetrain']; gears = D['gears']
c.execute('update Data_Drivetrain set DrivetypeID=?, EngineMountingDirection=?, ShiftSystemID=? where DrivetrainID=?', (D['drivetype'], D['mounting'], D['shift_system'], DT))
gr = {f'GearRatio{i}': (gears[i - 1] if i <= len(gears) else -1.0) for i in range(1, 9)}
c.execute(f'''update List_UpgradeDrivetrainTransmission set NumGears=?, FinalDriveRatio=?, GearShiftTime=?, GearRatio0=?, {", ".join(f"{k}=?" for k in gr)} where DrivetrainID=?''',
          [len(gears) + 1, D['final_drive'], D['shift_time'], D['reverse']] + list(gr.values()) + [DT])
c.execute('''update List_UpgradeDrivetrainDifferential set FrontLimitedSlipTorqueAccel=?, FrontLimitedSlipTorqueDecel=?, RearLimitedSlipTorqueAccel=?,
             RearLimitedSlipTorqueDecel=?, CenterLimitedSlipTorqueAccel=0, CenterLimitedSlipTorqueDecel=0 where DrivetrainID=?''', (*D['lsd'], DT))
c.execute('update List_UpgradeDrivetrainClutch set ClutchMaxTorque=? where DrivetrainID=?', (D['clutch_nm'], DT))

# ---------------------------------------------------------------- chassis
B = P['body']
c.execute('''update List_UpgradeCarBodyWeight set Mass=?, InitialMass=?, CMHeight=?, CMBackFront=?, BlockDimX=?, BlockDimY=?, BlockDimZ=? where CarBodyId=?''',
          (B['mass'], B['mass'], B['cm_height'], B['weight_front'], *B['block'], CAR * 1000))
c.execute('''update Data_CarBody set Height=?, Length=?, Width=?, Wheelbase=?, ModelWheelbase=?, ModelFrontTrackOuter=?, ModelRearTrackOuter=?,
             ModelFrontStockRideHeight=?, ModelRearStockRideHeight=?, PristineBoundingBoxMinX=?, PristineBoundingBoxMaxX=?, PristineBoundingBoxMinY=?,
             PristineBoundingBoxMaxY=?, PristineBoundingBoxMinZ=?, PristineBoundingBoxMaxZ=? where Id=?''',
          (B['height'], B['length'], B['width'], B['wheelbase'], B['model_wheelbase'], B['track_front'] * 1.012, B['track_rear'] * 1.012,
           B['ride_height'], B['ride_height'], *B['bbox'], CAR * 1000))
T = P['tyres']
for t, col, w in (('List_UpgradeCarBodyTireWidthFront', 'FrontTireWidth', T['width_front']), ('List_UpgradeCarBodyTireWidthRear', 'RearTireWidth', T['width_rear'])):
    c.execute(f'update "{t}" set "{col}"=? where CarBodyId=? and IsStock=1', (w, CAR * 1000)); c.execute(f'delete from "{t}" where CarBodyId=? and IsStock=0', (CAR * 1000,))
for t, col in (('List_UpgradeRimSizeFront', 'FrontWheelDiameter'), ('List_UpgradeRimSizeRear', 'RearWheelDiameter')):
    c.execute(f'update "{t}" set "{col}"=? where Ordinal=? and IsStock=1', (T['rim_in'], CAR)); c.execute(f'delete from "{t}" where Ordinal=? and IsStock=0', (CAR,))
c.execute('update List_UpgradeTireCompound set TireCompoundID=? where Ordinal=? and IsStock=1', (T['compound'], CAR))
c.execute('delete from List_UpgradeTireCompound where Ordinal=? and IsStock=0', (CAR,))
K = P['brakes']
c.execute('''update List_UpgradeBrakes set FrontBrakeSizeMM=?, FrontBrakeTypeID=?, FrontCaliperPistons=?, RearBrakeSizeMM=?, RearBrakeTypeID=?, RearCaliperPistons=?,
             GameFrictionScaleBraking=? where Ordinal=?''', (K['front_mm'], K['front_type'], K['front_pistons'], K['rear_mm'], K['rear_type'], K['rear_pistons'], K['friction'], CAR))
# every stock car has Model*StockRideHeight == its springs' DefRideHeight; a different model value draws the body
# lower/higher on its wheels (DAF at 0.30 vs the Charger springs' 0.1625 sat ~14 cm down, Owen 30 Oct)
for (rh,) in q('select s.DefRideHeight from List_UpgradeSpringDamper u join List_SpringDamperPhysics s on s.SpringDamperPhysicsID=u.FrontSpringDamperPhysicsID where u.Ordinal=? and u.IsStock=1', CAR):
    if abs(rh - B['ride_height']) > 0.005: print(f'  WARNING ride_height {B["ride_height"]} != the springs\' DefRideHeight {rh:.4f}: the body will be drawn offset')
Su = P['suspension']
for sid, front in q('''select s.SpringDamperPhysicsID, s.SpringDamperPhysicsID=u.FrontSpringDamperPhysicsID from List_UpgradeSpringDamper u join List_SpringDamperPhysics s
                       on s.SpringDamperPhysicsID in (u.FrontSpringDamperPhysicsID, u.RearSpringDamperPhysicsID) where u.Ordinal=?''', CAR):
    sp, bump, reb = Su['front' if front else 'rear']
    c.execute('''update List_SpringDamperPhysics set DefSpringRate=?, MinSpringRate=?, MaxSpringRate=?, DefDampenBumpRate=?, DefDampenReboundRate=?,
                 MaxDampenBumpRate=?, MaxDampenReboundRate=? where SpringDamperPhysicsID=?''', (sp, sp * 0.6, sp * 1.6, bump, reb, bump * 2.5, reb * 2.5, sid))
for side, val in (('Front', Su['swaybar_front']), ('Rear', Su['swaybar_rear'])):
    for (aid,) in q(f'select AntiSwayPhysicsID from List_UpgradeAntiSway{side} where Ordinal=?', CAR):
        c.execute('update List_AntiSwayPhysics set DefSwaybarStiffness=?, MinSwaybarStiffness=?, MaxSwaybarStiffness=? where AntiSwayPhysicsID=?', (val, val * 0.5, val * 2.0, aid))

# ---------------------------------------------------------------- the car
rpm = lambda r: r * 2 * math.pi / 60; Cr = P['car']
peak_t_rpm = max(curve, key=lambda p: p[1])[0]; peak_p_rpm = max(curve, key=lambda p: p[0] * p[1])[0]
c.execute(f'''update Data_Car set Year=?, MakeID=?, DisplayName=?, ModelShort=?, MediaName=?, MakeName=?, CurbWeight=?, WeightDistribution=?, NumGears=?,
   Displacement=?, CylinderID=?, EngineConfigID=?, FrontTireWidthMM=?, FrontTireAspect=?, FrontWheelDiameterIN=?, RearTireWidthMM=?, RearTireAspect=?, RearWheelDiameterIN=?,
   "Time:0-60-sec"=?, "Time:0-100-sec"=?, "TopSpeed-mph"=?, BaseCost=?, PerformanceIndex=?, BodyAeroLongitudinalDrag=?, GameTorqueScale=1.0, BodyAeroForwardDownforceFront=?,
   BodyAeroForwardDownforceRear=?, BodyAeroWIForceScale=?, SimPeakPower=?, SimPeakAngVel=?, SimPeakTorque=?, SimPeakTorqueAngVel=?, SimRedlineAngVel=?, SimTimeTo60MPH=?,
   SimTimeTo100MPH=?, SimTopSpeed=?, SpeedRating=?, HandlingRating=?, AccelerationRating=?, BrakingRating=?, LaunchRating=?, MaxUpgradeWizardPerfRating=?,
   SteerMaxAngle=?, SteerMaxAngleFiltered=?, ClassID=?, FamilyModelID=?, FamilyBodyID=?, FamilySpecialID=?, EnginePlacementID=?, PowertrainID=?, MaterialTypeID=?,
   IsOpenCockpit=?, IsOpenWheel=?, FrontStockRideHeight=?, RearStockRideHeight=?, Thumbnail=? where Id=?''',
   (Cr['year'], make_id, f'_&{(car_hash << 16) | S_NAME}', f'_&{(car_hash << 16) | S_SHORT}', MEDIA, f'_&{(mk_hash << 16) | S_CARMAKE}', B['mass'] / 100, B['weight_front'],
    len(gears), E['displacement'], E['cylinders'], E['config'], T['width_front'], T['aspect_front'], T['rim_in'], T['width_rear'], T['aspect_rear'], T['rim_in'],
    Cr['t60'], Cr['t100'], Cr['top_mph'], Cr['price'], Cr['pi'], Cr['drag'], Cr['downforce_front'], Cr['downforce_rear'], Cr['wi_force'],
    E['peak_hp'] * 7.457, rpm(peak_p_rpm), PEAK / 100, rpm(peak_t_rpm), rpm(LIMIT), Cr['t60'], Cr['t100'], Cr['top_mph'] * 0.44704,
    *Cr['ratings'], Cr['pi'], Cr['steer_deg'], Cr['steer_deg'] * 0.75, Cr['class'], Cr['family_model'], Cr['family_body'], Cr['family_special'],
    Cr['engine_placement'], Cr['powertrain'], Cr['material'], Cr['open_cockpit'], Cr['open_wheel'], B['ride_height'], B['ride_height'],
    f'game:\\Media\\Stripped\\RC0\\Thumbnail_{Cr["thumbnail_of"]}.png', CAR))
c.commit()
json.dump({'format_version': 1, 'fallback_language': 'EN', 'languages': {'EN': {
    'Data_Car': {str(S_NAME): P['name'], str(S_SHORT): P['short_name']},
    'List_CarMake': {str(S_MAKE): P['make'], str(S_MAKE_PROFILE): P['make_profile'], str(S_CARMAKE): P['make']}}}}, open(STRINGS_OUT, 'w'), indent=1)
print(f'car {CAR} make {make_id} ({P["make"]}) engine peak {PEAK:.0f} Nm, {E["peak_hp"]} hp, limiter {LIMIT}; wrote {DST}, {STRINGS_OUT}')
