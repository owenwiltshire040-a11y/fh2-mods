"""Database edits for the Toro Rosso STR1 (2006) on a copy of the game database.

Donor: 2012 Dodge Charger SRT8 (car 1422, engine 882, drivetrain 830; wheelbase 3.052 m, which the game's wheel
animations fix, so it matches the STR1's 3.05 m). The clone gets car 3651, engine 3651,
drivetrain 3651 and a new Toro Rosso make. Physics from CTDP's STR1 setup files (personal use, with CTDP's
permission): 605 kg with driver, 41.8 % front, 3.05 m wheelbase, Cosworth TJ2005 3.0 V10 (317 Nm at 15,500,
~723 hp at 16,750, limiter 16,700), 7-speed, carbon brakes, grooved slicks on 13" rims.
"""
import sqlite3, shutil, math

SRC, DST = '../car207/vanilla.slt', 'custom_str1.slt'
CAR_OLD, CAR = 1422, 3651
ENG_OLD, ENG = 882, 3651
DT_OLD, DT = 830, 3651
MEDIA = 'STR_ToroRosso_1_06'       # same length as DOD_ChargerSRT8_12, so embedded paths can be renamed in place

shutil.copy(SRC, DST)
c = sqlite3.connect(DST)
q = lambda s, *a: c.execute(s, a).fetchall()

def cols(t): return [r[1] for r in c.execute(f'pragma table_info("{t}")')]

def clone(table, where, args, remap):
    """copy rows matching `where`, passing each row dict through remap(row) (which edits it in place)"""
    cs = cols(table)
    rows = [dict(zip(cs, r)) for r in q(f'select * from "{table}" where {where}', *args)]
    for r in rows:
        remap(r)
        c.execute(f'insert into "{table}" ({",".join(chr(34)+x+chr(34) for x in cs)}) values ({",".join("?"*len(cs))})',
                  [r[x] for x in cs])
    return rows

def shift(v, old, new):
    """2011 -> 3207 and 2011xxx -> 3207xxx for integer ids"""
    if isinstance(v, int):
        if v == old: return new
        if old * 1000 <= v <= old * 1000 + 999: return new * 1000 + (v - old * 1000)
    return v

def car_remap(r):
    for k, v in r.items():
        if k.lower() in ('id', 'ordinal', 'carid', 'modelid') or isinstance(v, int) and CAR_OLD * 1000 <= v <= CAR_OLD * 1000 + 999:
            r[k] = shift(v, CAR_OLD, CAR)

# ---------------------------------------------------------------- make: Toro Rosso
make_id = q('select max(ID) from List_CarMake')[0][0] + 2      # (+1 is the Peugeot make of Owen's 207 mod)
mk_hash = int(q("select MakeName from Data_Car where Id=?", CAR_OLD)[0][0][2:]) >> 16
car_hash = int(q("select DisplayName from Data_Car where Id=?", CAR_OLD)[0][0][2:]) >> 16
mk_table_hash = int(q("select DisplayName from List_CarMake where ID=107")[0][0][2:]) >> 16
S_MAKE, S_MAKE_PROFILE, S_CARMAKE = 64651, 64652, 64653
S_NAME, S_SHORT = 64651, 64652
ren = dict(zip(cols('List_CarMake'), q('select * from List_CarMake where ID=107')[0]))
ren.update(ID=make_id, DisplayName=f'_&{(mk_table_hash << 16) | S_MAKE}', ManufacturerCode='STR', CountryID=4,
           IconPathBase='ARI', Profile=f'_&{(mk_table_hash << 16) | S_MAKE_PROFILE}')
c.execute(f'insert into List_CarMake values ({",".join("?"*len(ren))})', list(ren.values()))

# ---------------------------------------------------------------- car-level tables
car_tables = ['Data_Car', 'Data_CarBody', 'CameraOverrides', 'CarPartPositions', 'Data_Car_Buckets',
              'List_AntiSwayPhysics', 'List_SpringDamperPhysics', 'List_UpgradeAntiSwayFront',
              'List_UpgradeAntiSwayRear', 'List_UpgradeBrakes', 'List_UpgradeCarBody',
              'List_UpgradeCarBodyChassisStiffness', 'List_UpgradeCarBodyFrontBumper', 'List_UpgradeCarBodyHood',
              'List_UpgradeCarBodyRearBumper', 'List_UpgradeCarBodySideSkirt', 'List_UpgradeCarBodyTireWidthFront',
              'List_UpgradeCarBodyTireWidthRear', 'List_UpgradeCarBodyWeight', 'List_UpgradeRearWing',
              'List_UpgradeRimSizeFront', 'List_UpgradeRimSizeRear', 'List_UpgradeSpringDamper',
              'List_UpgradeTireCompound']
for t in car_tables:
    cs = cols(t)
    conds = [f'"{k}"=?' for k in cs if k.lower() in ('id', 'ordinal', 'carid', 'modelid')]
    conds += [f'"{k}" between ? and ?' for k in cs if k.lower() in ('id', 'carbodyid', 'antiswayphysicsid', 'springdamperphysicsid')]
    args = [CAR_OLD if '=' in x else None for x in conds]
    where, a = [], []
    for k in cs:
        if k.lower() in ('id', 'ordinal', 'carid', 'modelid'):
            where.append(f'"{k}"=?'); a.append(CAR_OLD)
            where.append(f'"{k}" between ? and ?'); a += [CAR_OLD * 1000, CAR_OLD * 1000 + 999]
    rows = q(f'select rowid from "{t}" where ' + ' or '.join(where), *a)
    clone(t, 'rowid in (%s)' % ','.join(str(r[0]) for r in rows), [], car_remap)

# stock engine and drivetrain only (no engine/drivetrain swaps)
clone('List_UpgradeEngine', 'Ordinal=? and IsStock=1', [CAR_OLD],
      lambda r: (car_remap(r), r.update(EngineID=ENG, ManufacturerID=make_id)))
clone('List_UpgradeDrivetrain', 'Ordinal=? and IsStock=1', [CAR_OLD],
      lambda r: (car_remap(r), r.update(DrivetrainID=DT, ManufacturerId=make_id)))

# paint colours (each needs a fresh ID)
next_col = q('select max(ID) from Combo_Colors')[0][0] + 50   # clear of the 207 mod's colours
def col_remap(r):
    global next_col
    r['Ordinal'] = CAR; r['ID'] = next_col; next_col += 1
clone('Combo_Colors', 'Ordinal=?', [CAR_OLD], col_remap)

# ---------------------------------------------------------------- aero: the donor's wing/bumper aero rows are shared ids;
# give the STR1 its own (front wing + rear wing ranges, in the game's units: Atom 23-45 front, 34-91 rear)
next_aero = q('select max(AeroPhysicsID) from List_AeroPhysics')[0][0] + 1
def own_aero(table, key, val, front):
    global next_aero
    cs = cols('List_AeroPhysics')
    if not q(f'select 1 from "{table}" where "{key}"=? and IsStock=1', val): print('  no stock aero row in', table)
    for rid, aid in q(f'select Id, AeroPhysicsID from "{table}" where "{key}"=? and IsStock=1', val):
        src_row = q('select * from List_AeroPhysics where AeroPhysicsID=?', aid) or \
                  q('select * from List_AeroPhysics where AeroPhysicsID=?', aid - (CAR - CAR_OLD) * 1000)   # (id shifted by the clone)
        row = dict(zip(cs, src_row[0]))
        row.update(AeroPhysicsID=next_aero, Drag0=30.0 if front else 70.0, Drag1=60.0 if front else 160.0,
                   Downforce0=150.0 if front else 250.0, Downforce1=250.0 if front else 400.0, DefaultTuneSlider=0.5)
        c.execute(f'insert into List_AeroPhysics values ({",".join("?" * len(cs))})', [row[x] for x in cs])
        c.execute(f'update "{table}" set AeroPhysicsID=? where Id=?', (next_aero, rid)); next_aero += 1
    c.execute(f'delete from "{table}" where "{key}"=? and IsStock=0', (val,))     # no aftermarket aero kits
own_aero('List_UpgradeCarBodyFrontBumper', 'CarBodyID', CAR * 1000, True)
own_aero('List_UpgradeRearWing', 'Ordinal', CAR, False)

# ---------------------------------------------------------------- engine: Cosworth TJ2005 3.0 V10 (2006 spec, restricted)
def eng_remap(r):
    for k, v in r.items():
        if k == 'EngineID' or isinstance(v, int) and ENG_OLD * 1000 <= v <= ENG_OLD * 1000 + 999:
            r[k] = shift(v, ENG_OLD, ENG)
clone('Data_Engine', 'EngineID=?', [ENG_OLD], eng_remap)
for t in [n for (n,) in q("select name from sqlite_master where type='table' and name like 'List_UpgradeEngine%' and name<>'List_UpgradeEngine'")]:
    if 'EngineID' in cols(t):
        clone(t, 'EngineID=?', [ENG_OLD], eng_remap)
clone('List_TorqueCurve', 'TorqueCurveID between ? and ?', [ENG_OLD * 1000, ENG_OLD * 1000 + 999], eng_remap)
# engine sound: the Porsche Carrera GT's V10 (an engine first drawn up for racing); the donor's V8 has no V10 shriek
c.execute('''update Data_Engine set MediaName='POR_CarreraGT_03', "EngineMass-kg"=95, Compression=13.5, ConfigID=1,
             CylinderID=5, MomentInertia=0.049, GasTankSize=95, EngineGraphingMaxTorque=330, EngineGraphingMaxPower=540,
             EngineName='Cosworth TJ2005 3.0L V10' where EngineID=?''', (ENG,))
import re as _re
_t = _re.sub(r'//.*', '', open('in/TJ2005_engine.ini', encoding='latin1').read())
RPMT = [tuple(map(float, m)) for m in _re.findall(r'RPMTorque=\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)', _t)]
# The game's rev tables stop at 12,000 rpm (121 points of 100 rpm; past that the engine is cut), so the V10 is
# mapped into that range: rpm x K, torque / K (same power at every road speed), gear ratios x K (same speed per gear).
K = 11900.0 / 16700.0
PEAK = max(r[2] for r in RPMT) / K; LIMIT = 11900; STEP = 100; NPTS = 121
def full(rpm):
    xs = [r[0] * K for r in RPMT]; ys = [r[2] / K for r in RPMT]
    return float(np.interp(rpm, xs, ys))
import numpy as np
vals = []
for i in range(NPTS):
    rpm = i * STEP
    if rpm <= LIMIT: vals.append(max(full(rpm), 0.0) / PEAK)
    elif rpm == LIMIT + 100: vals.append(-2.63)                # the game's fuel-cut marker
    else: vals.append(0.0)
vals[0] = vals[1] = max(vals[10], 0.05)                       # (pull-away torque below 1,000 rpm)
donor_peak = 637.0                                            # Charger SRT8 6.4 HEMI peak torque (470 lb-ft); its TorqueScale maps to that
donor_scale = q('select TorqueScale from List_TorqueCurve where TorqueCurveID=?', ENG_OLD * 1000)[0][0]
sets = ', '.join(f'v{i}=?' for i in range(NPTS))
for (cid,) in q('select TorqueCurveID from List_TorqueCurve where TorqueCurveID between ? and ?', ENG * 1000, ENG * 1000 + 999):
    c.execute(f'update List_TorqueCurve set TorqueScale=?, NumTorqueValues=?, {sets} where TorqueCurveID=?',
              [donor_scale * PEAK / donor_peak, NPTS] + vals + [cid])
c.execute('''update List_UpgradeEngineCamshaft set RedlineRPM=?, StallRPM=2100.0, StartRPM=7550.0, TorqueCurveMaxRPM=?,
             NumRPMEntriesArray=? where EngineID=?''', (float(LIMIT), float((NPTS - 1) * STEP), NPTS, ENG))
c.execute('update List_UpgradeEngine set ManufacturerID=? where EngineID=?', (make_id, ENG))

# ---------------------------------------------------------------- drivetrain: 7-speed seamless-ish, RWD
def dt_remap(r):
    for k, v in r.items():
        if k.lower() == 'drivetrainid' or isinstance(v, int) and DT_OLD * 1000 <= v <= DT_OLD * 1000 + 999:
            r[k] = shift(v, DT_OLD, DT)
clone('Data_Drivetrain', 'DrivetrainID=?', [DT_OLD], dt_remap)
for t in ('List_UpgradeDrivetrainClutch', 'List_UpgradeDrivetrainDifferential', 'List_UpgradeDrivetrainDriveline',
          'List_UpgradeDrivetrainTransmission'):
    key = 'DrivetrainId' if 'DrivetrainId' in cols(t) else 'DrivetrainID'
    clone(t, f'"{key}"=?', [DT_OLD], dt_remap)
# CTDP default: gears 3.200 2.267 1.800 1.529 1.333 1.200 1.091, final 5.909 x bevel 24/23
c.execute('''update List_UpgradeDrivetrainTransmission set NumGears=8, FinalDriveRatio=?, GearShiftTime=0.03,
             GearRatio0=-3.0, GearRatio1=3.200, GearRatio2=2.267, GearRatio3=1.800, GearRatio4=1.529, GearRatio5=1.333,
             GearRatio6=1.200, GearRatio7=1.091, GearRatio8=-1.0 where DrivetrainID=?''', (5.909 * 24 / 23 * K, DT))
c.execute('''update List_UpgradeDrivetrainDifferential set RearLimitedSlipTorqueAccel=1400, RearLimitedSlipTorqueDecel=600
             where DrivetrainID=?''', (DT,))

# ---------------------------------------------------------------- chassis
MASS = 530.0                              # 605 kg minimum with driver; the game's masses are driverless
c.execute('''update List_UpgradeCarBodyWeight set Mass=?, InitialMass=?, CMHeight=0.27, CMBackFront=0.418,
             BlockDimX=1.80, BlockDimY=0.80, BlockDimZ=4.55 where CarBodyId=?''', (MASS, MASS, CAR * 1000))
c.execute('''update Data_CarBody set Height=0.95, Length=4.60, Width=1.80, Wheelbase=3.05, ModelWheelbase=3.05, 
             ModelFrontTrackOuter=?, ModelRearTrackOuter=? where Id=?''', (1.486 * 1.012, 1.422 * 1.012, CAR * 1000))   # game value ~ centre-to-centre track (Atom: 1.805 for 1.784)
# grooved slicks, 13" rims only
for t, col, w in (('List_UpgradeCarBodyTireWidthFront', 'FrontTireWidth', 280), ('List_UpgradeCarBodyTireWidthRear', 'RearTireWidth', 340)):
    c.execute(f'update "{t}" set "{col}"=? where CarBodyId=?', (w, CAR * 1000))
    c.execute(f'delete from "{t}" where CarBodyId=? and IsStock=0', (CAR * 1000,))
for t, col in (('List_UpgradeRimSizeFront', 'FrontWheelDiameter'), ('List_UpgradeRimSizeRear', 'RearWheelDiameter')):
    c.execute(f'update "{t}" set "{col}"=13 where Ordinal=? and IsStock=1', (CAR,))
    c.execute(f'delete from "{t}" where Ordinal=? and IsStock=0', (CAR,))
c.execute("update List_UpgradeTireCompound set TireCompoundID=8 where Ordinal=? and IsStock=1", (CAR,))
c.execute('delete from List_UpgradeTireCompound where Ordinal=? and IsStock=0', (CAR,))
# carbon brakes, 278 mm, 6-piston calipers
c.execute('''update List_UpgradeBrakes set FrontBrakeSize=11, FrontBrakeSizeMM=278.0, FrontBrakeTypeID=5, FrontCaliperPistons=6,
             RearBrakeSize=11, RearBrakeSizeMM=278.0, RearBrakeTypeID=5, RearCaliperPistons=4, GameFrictionScaleBraking=1.15
             where Ordinal=?''', (CAR,))
# springs/dampers: F1-stiff (the Atom's 46 front; now 160/140), damping up with them
for sid, rate in q('''select s.SpringDamperPhysicsID, case when s.SpringDamperPhysicsID=u.FrontSpringDamperPhysicsID then 160.0 else 140.0 end
                      from List_UpgradeSpringDamper u join List_SpringDamperPhysics s
                      on s.SpringDamperPhysicsID in (u.FrontSpringDamperPhysicsID, u.RearSpringDamperPhysicsID) where u.Ordinal=?''', CAR):
    c.execute('''update List_SpringDamperPhysics set DefSpringRate=?, MinSpringRate=?, MaxSpringRate=?, DefDampenBumpRate=8.0,
                 DefDampenReboundRate=11.0, MaxDampenBumpRate=20.0, MaxDampenReboundRate=20.0 where SpringDamperPhysicsID=?''',
              (rate, rate * 0.6, rate * 1.6, sid))

# ---------------------------------------------------------------- the car itself
# drag: sized against the Atom (game top speed 194.5 mph on 500 hp x its 0.744 game torque scale, drag ~215 units)
# so 723 hp at full torque scale tops out near 190 mph: total ~390 units (body 230, wings ~45 + ~115 at mid setting)
rpm = lambda r: r * 2 * math.pi / 60
c.execute(f'''update Data_Car set Year=2006, MakeID=?, DisplayName=?, ModelShort=?, MediaName=?, MakeName=?,
   CurbWeight=?, WeightDistribution=0.418, NumGears=7, Displacement=2998, CylinderID=5, EngineConfigID=1,
   FrontTireWidthMM=280, FrontTireAspect=59, FrontWheelDiameterIN=13, RearTireWidthMM=340, RearTireAspect=48, RearWheelDiameterIN=13,
   "Time:0-60-sec"=2.6, "Time:0-100-sec"=4.6, "TopSpeed-mph"=196.0, BaseCost=1, PerformanceIndex=0.999,
   BodyAeroLongitudinalDrag=230.0, GameTorqueScale=1.0, BodyAeroForwardDownforceFront=420.0, BodyAeroForwardDownforceRear=640.0,
   SimPeakPower=5390.0, SimPeakAngVel=?, SimPeakTorque=?, SimPeakTorqueAngVel=?, SimRedlineAngVel=?,
   SimTimeTo60MPH=2.6, SimTimeTo100MPH=4.6, SimTopSpeed=87.0, SimLatGees60MPH=2.0, SimLatGees120MPH=3.5,
   SimBrakeDistance60MPH=22.0, SimBrakeDistance100MPH=50.0,
   SpeedRating=10.0, HandlingRating=10.0, AccelerationRating=10.0, BrakingRating=10.0, LaunchRating=10.0,
   MaxUpgradeWizardPerfRating=1.0, SteerMaxAngle=24.0, SteerMaxAngleFiltered=18.0,
   Thumbnail='game:\\Media\\Stripped\\RC0\\Thumbnail_1651.png' where Id=?''',
          (make_id, f'_&{(car_hash << 16) | S_NAME}', f'_&{(car_hash << 16) | S_SHORT}', MEDIA,
           f'_&{(mk_hash << 16) | S_CARMAKE}', MASS / 100, rpm(16750 * K), PEAK / 100, rpm(15500 * K), rpm(LIMIT), CAR))
# the Charger's sedan-only flags -> open-wheel single seater (values from the Atom / Caterham / KTM X-Bow rows):
# IsOpenCockpit picks the open-car driver (helmet, reclined), IsOpenWheel the open-wheel handling of wheel contacts
c.execute('''update Data_Car set IsOpenCockpit=1, IsOpenWheel=1, ClassID=5, FamilyBodyID=45, FamilySpecialID=1,
   EnginePlacementID=2, PowertrainID=2, MaterialTypeID=2, BodyAeroWIForceScale=0.55,
   FrontStockRideHeight=0.10, RearStockRideHeight=0.10 where Id=?''', (CAR,))
# ride height the model was built at (= stock, so the body is not shifted) and the STR1's own bounding box
c.execute('''update Data_CarBody set ModelFrontStockRideHeight=0.10, ModelRearStockRideHeight=0.10,
   PristineBoundingBoxMinX=-1.05, PristineBoundingBoxMaxX=1.05, PristineBoundingBoxMinY=-0.18, PristineBoundingBoxMaxY=0.94,
   PristineBoundingBoxMinZ=-2.09, PristineBoundingBoxMaxZ=2.58 where Id=?''', (CAR * 1000,))
c.commit()

STRINGS = {'format_version': 1, 'fallback_language': 'EN', 'languages': {'EN': {
    'Data_Car': {str(S_NAME): 'STR1', str(S_SHORT): 'STR1'},
    'List_CarMake': {str(S_MAKE): 'Toro Rosso', str(S_MAKE_PROFILE): 'Scuderia Toro Rosso', str(S_CARMAKE): 'Toro Rosso'}}}}
import json
json.dump(STRINGS, open('strings_str1.json', 'w'), indent=1)
print('donor TorqueScale', donor_scale, '-> STR1', donor_scale * PEAK / donor_peak)
print('make id', make_id, 'car hash', car_hash, 'make hash', mk_hash)
for t in car_tables + ['List_UpgradeEngine', 'List_UpgradeDrivetrain', 'Combo_Colors', 'List_AeroPhysics', 'List_TorqueCurve']:
    print(t, q(f'select count(*) from "{t}"')[0][0] - sqlite3.connect(SRC).execute(f'select count(*) from "{t}"').fetchone()[0], 'rows added')
