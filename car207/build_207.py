"""Build the "Peugeot 207" database edits on a copy of the game database.

Donor: 2014 Ford Fiesta ST (car 2011, engine 2139, drivetrain 2086). The clone gets car 3207, engine 3207,
drivetrain 3207 and a new Peugeot make, with real 2008 207 SE Premium 1.6 HDi 90 (5-door, 5-speed) figures.
"""
import sqlite3, shutil, math

SRC, DST = 'vanilla.slt', 'custom.slt'
CAR_OLD, CAR = 2011, 3207
ENG_OLD, ENG = 2139, 3207
DT_OLD, DT = 2086, 3207
MEDIA = 'PEU_207SEHDi_08'   # same length as FOR_FiestaST_14, so embedded paths can be renamed in place

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

# ---------------------------------------------------------------- make: Peugeot
make_id = q('select max(ID) from List_CarMake')[0][0] + 1
mk_hash = int(q("select MakeName from Data_Car where Id=2011")[0][0][2:]) >> 16
car_hash = int(q("select DisplayName from Data_Car where Id=2011")[0][0][2:]) >> 16
mk_table_hash = int(q("select DisplayName from List_CarMake where ID=41")[0][0][2:]) >> 16
S_MAKE, S_MAKE_PROFILE, S_CARMAKE = 64207, 64208, 64209
S_NAME, S_SHORT = 64207, 64208
ren = dict(zip(cols('List_CarMake'), q('select * from List_CarMake where ID=41')[0]))
ren.update(ID=make_id, DisplayName=f'_&{(mk_table_hash << 16) | S_MAKE}', ManufacturerCode='PEU', CountryID=2,
           IconPathBase='Peugeot', Profile=f'_&{(mk_table_hash << 16) | S_MAKE_PROFILE}')
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

# stock engine and drivetrain only (no engine/drivetrain swaps for the 207)
clone('List_UpgradeEngine', 'Ordinal=? and IsStock=1', [CAR_OLD],
      lambda r: (car_remap(r), r.update(EngineID=ENG, ManufacturerID=make_id)))
clone('List_UpgradeDrivetrain', 'Ordinal=? and IsStock=1', [CAR_OLD],
      lambda r: (car_remap(r), r.update(DrivetrainID=DT, ManufacturerId=make_id)))

# paint colours (each needs a fresh ID)
next_col = q('select max(ID) from Combo_Colors')[0][0] + 1
def col_remap(r):
    global next_col
    r['Ordinal'] = CAR; r['ID'] = next_col; next_col += 1
clone('Combo_Colors', 'Ordinal=?', [CAR_OLD], col_remap)

# ---------------------------------------------------------------- engine 1.6 HDi 90 (DV6)
def eng_remap(r):
    for k, v in r.items():
        if k == 'EngineID' or isinstance(v, int) and ENG_OLD * 1000 <= v <= ENG_OLD * 1000 + 999:
            r[k] = shift(v, ENG_OLD, ENG)
clone('Data_Engine', 'EngineID=?', [ENG_OLD], eng_remap)
for t in [n for (n,) in q("select name from sqlite_master where type='table' and name like 'List_UpgradeEngine%' and name<>'List_UpgradeEngine'")]:
    if 'EngineID' in cols(t):
        clone(t, 'EngineID=?', [ENG_OLD], eng_remap)
clone('List_TorqueCurve', 'TorqueCurveID between ? and ?', [ENG_OLD * 1000, ENG_OLD * 1000 + 999], eng_remap)

c.execute('''update Data_Engine set "EngineMass-kg"=150, Compression=18.0, "StockBoost-bar"=1.0, GasTankSize=50,
             EngineGraphingMaxTorque=?, EngineGraphingMaxPower=66.0, EngineName='1.6L I4 HDi', Diesel=1,
             TorqueSteerLeftSpeedScale=0.4 where EngineID=?''', (473.8088 * 215 / 240, ENG))

# torque curves: 81 values at 100 rpm steps; the real DV6 90 makes 215 Nm at 1,750 rpm and 90 PS at 4,000 rpm.
# Beyond ~5,000 rpm the donor's curve uses -2.63 as its fuel-cut marker; we copy that convention.
pts = [(0, 0.40), (800, 0.48), (1000, 0.56), (1250, 0.72), (1500, 0.88), (1750, 1.0), (2250, 1.0), (2750, 0.95),
       (3250, 0.86), (3750, 0.78), (4000, 0.733), (4500, 0.60), (4900, 0.42), (5000, 0.30)]
def curve(scale):
    v = []
    for i in range(81):
        rpm = i * 100
        if rpm > 5000:
            v.append(-2.63 if rpm == 5100 else 0.0); continue
        for (r0, a0), (r1, a1) in zip(pts, pts[1:]):
            if r0 <= rpm <= r1:
                v.append(a0 + (a1 - a0) * (rpm - r0) / (r1 - r0)); break
    return v
donor_scale = q('select TorqueScale from List_TorqueCurve where TorqueCurveID=?', ENG_OLD * 1000)[0][0]
base = donor_scale * 215 / 240          # the Fiesta ST's stock 240 Nm maps to the donor scale
for cid, mult in q('select TorqueCurveID, 1.0 from List_TorqueCurve where TorqueCurveID between ? and ?',
                   ENG * 1000, ENG * 1000 + 999):
    lvl = cid - ENG * 1000
    m = {0: 1.0, 2: 1.06, 3: 1.12}.get(lvl, 1.0)    # mild camshaft/remap upgrades
    vals = curve(1.0)
    sets = ', '.join(f'v{i}=?' for i in range(81))
    c.execute(f'update List_TorqueCurve set TorqueScale=?, NumTorqueValues=52, ZeroThrottleTorqueScale=?, {sets} where TorqueCurveID=?',
              [base * m, 120.0] + vals + [cid])

# ---------------------------------------------------------------- drivetrain: 5-speed manual, FWD
def dt_remap(r):
    for k, v in r.items():
        if k.lower() == 'drivetrainid' or isinstance(v, int) and DT_OLD * 1000 <= v <= DT_OLD * 1000 + 999:
            r[k] = shift(v, DT_OLD, DT)
clone('Data_Drivetrain', 'DrivetrainID=?', [DT_OLD], dt_remap)
for t in ('List_UpgradeDrivetrainClutch', 'List_UpgradeDrivetrainDifferential', 'List_UpgradeDrivetrainDriveline',
          'List_UpgradeDrivetrainTransmission'):
    key = 'DrivetrainId' if 'DrivetrainId' in cols(t) else 'DrivetrainID'
    clone(t, f'"{key}"=?', [DT_OLD], dt_remap)
# stock BE4 5-speed (1.6 HDi 90); the race gearbox upgrades keep 5 forward ratios, spaced closer
c.execute('''update List_UpgradeDrivetrainTransmission set NumGears=6, FinalDriveRatio=3.765, GearRatio0=-3.333,
             GearRatio1=3.455, GearRatio2=1.870, GearRatio3=1.148, GearRatio4=0.822, GearRatio5=0.660,
             GearRatio6=-1.0, GearRatio7=-1.0, GearRatio8=-1.0 where DrivetrainID=? and Level<=2''', (DT,))
c.execute('''update List_UpgradeDrivetrainTransmission set NumGears=6, GearRatio0=-3.333, GearRatio1=3.0,
             GearRatio2=1.95, GearRatio3=1.40, GearRatio4=1.07, GearRatio5=0.86, GearRatio6=-1.0 where DrivetrainID=? and Level>2''', (DT,))

# ---------------------------------------------------------------- the car itself
rpm = lambda r: r * 2 * math.pi / 60
c.execute(f'''update Data_Car set Year=2008, MakeID=?, DisplayName=?, ModelShort=?, MediaName=?, MakeName=?,
   ClassID=0, CurbWeight=12.50, WeightDistribution=0.62, NumGears=5, Displacement=1560,
   FrontTireWidthMM=195, FrontTireAspect=55, FrontWheelDiameterIN=16,
   RearTireWidthMM=195, RearTireAspect=55, RearWheelDiameterIN=16,
   "Time:0-60-sec"=11.3, "Time:0-100-sec"=45.0, "TopSpeed-mph"=113.0, BaseCost=6000, PerformanceIndex=0.245,
   SimPeakPower=660.0, SimPeakAngVel=?, SimPeakTorque=2.15, SimPeakTorqueAngVel=?, SimRedlineAngVel=?,
   SimTimeTo60MPH=11.3, SimTimeTo100MPH=45.0, SimTimeQuarterMile=18.2, SimTopSpeed=50.5, SimSpeedQuarterMile=33.5,
   SimBrakeDistance60MPH=44.5, SimBrakeDistance100MPH=124.0, SimLatGees60MPH=0.80, SimLatGees120MPH=0.80,
   SpeedRating=4.05, HandlingRating=5.62, AccelerationRating=4.55, BrakingRating=6.30, LaunchRating=4.85,
   MaxUpgradeWizardPerfRating=0.62, CountryID=2, RegionID=2,
   Thumbnail='game:\\Media\\Stripped\\RC0\\Thumbnail_{CAR}.png' where Id=?''',
          (make_id, f'_&{(car_hash << 16) | S_NAME}', f'_&{(car_hash << 16) | S_SHORT}', MEDIA,
           f'_&{(mk_hash << 16) | S_CARMAKE}', rpm(4000), rpm(1750), rpm(5000), CAR))

# the engine's rev range lives in the camshaft rows: redline, curve length (rpm) and number of curve points.
# Donor: redline 6,800 / 7,200 / 7,500 rpm, curve to 8,000 rpm in 81 points (100 rpm steps).
# 207 HDi: redline 4,800 rpm (fuel cut just above 5,000), mild cams 4,900 / 5,000; curve to 5,100 rpm in 52 points.
for lvl, red in ((0, 4800.0), (2, 4900.0), (3, 5000.0)):   # all below the 5,100 rpm fuel cut
    c.execute('''update List_UpgradeEngineCamshaft set RedlineRPM=?, StartRPM=2000.0, TorqueCurveMaxRPM=5100.0,
                 NumRPMEntriesArray=52 where Id=?''', (red, ENG * 1000 + lvl))
c.execute('update Data_Car set SimRedlineAngVel=? where Id=?', (4800 * 2 * math.pi / 60, CAR))
c.execute('update Data_Car_Buckets set CarBucket=23 where CarId=?', (CAR,))   # the hatchback category (Civic Type R, Corsa VXR, 500 Abarth)
c.commit()

STRINGS = {'format_version': 1, 'fallback_language': 'EN', 'languages': {'EN': {
    'Data_Car': {str(S_NAME): '207 SE Premium HDi', str(S_SHORT): '207'},
    'List_CarMake': {str(S_MAKE): 'Peugeot', str(S_MAKE_PROFILE): 'Peugeot', str(S_CARMAKE): 'Peugeot'}}}}
# the car row also names its make through a Data_Car-family key (MakeName); give it a string too
mk_table = 'Data_Car' if mk_hash == car_hash else None
print('make id', make_id, 'car hash', car_hash, 'make-name hash', mk_hash, 'carmake table hash', mk_table_hash)
import json
json.dump({'strings': STRINGS, 'mk_hash': mk_hash, 'car_hash': car_hash, 'mk_table_hash': mk_table_hash,
           'S_CARMAKE': S_CARMAKE}, open('build_info.json', 'w'), indent=1)
for t in car_tables + ['List_UpgradeEngine', 'List_UpgradeDrivetrain', 'Combo_Colors']:
    print(t, q(f'select count(*) from "{t}"')[0][0] - sqlite3.connect(SRC).execute(f'select count(*) from "{t}"').fetchone()[0], 'rows added')
