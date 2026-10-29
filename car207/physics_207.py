"""Physics of the 2008 Peugeot 207 SE 1.6 HDi 90 5dr, replacing what car 3207 inherited from the 2014 Fiesta ST.

Published figures (auto-data.net, Top Gear spec page, Brembo catalogue for the 66 kW 1.6 HDi 2006-13):
  wheelbase 2540, track 1475 / 1466, length 4030, width 1720, height 1472 mm; Cd 0.30; kerb weight 1,280 kg
  (EC, incl. 75 kg driver); 195/55 R16 on 16" alloys; MacPherson front, torsion beam rear; front vented discs
  266 mm, rear drums 228.7 mm; open differential; 215 Nm.
Not published (estimated, and said so): springs, dampers, anti-roll bars, centre-of-mass height, inertia box.
These are taken from the game's own non-sport Fiesta Mk7 (car 1082) and scaled by mass (1215 / 970 kg).
"""
import sqlite3
DB = 'custom.slt'
CAR, BODY, DT = 3207, 3207000, 3207
MASS = 1215.0                       # 1,280 kg EC kerb minus the 75 kg driver; the game uses driverless kerb weight
REF_CAR, REF_MASS = 1082, 970.0     # game's Fiesta Mk7 1.6 (non-ST)
K = MASS / REF_MASS

c = sqlite3.connect(DB)
q = lambda s, *a: c.execute(s, a).fetchall()
ex = lambda s, a=(): c.execute(s, a)

# ---- body: size, weight, centre of mass, inertia box
ex('update Data_CarBody set ModelFrontTrackOuter=?, ModelRearTrackOuter=? where Id=?', (1.475 + 0.195, 1.466 + 0.195, BODY))
st = q('select Level, Mass, CMHeight, CMBackFront from List_UpgradeCarBodyWeight where CarBodyId=? order by Level', BODY)
m0, h0, f0 = st[0][1], st[0][2], st[0][3]
for lvl, m, h, f in st:                      # keep the upgrade steps' relative savings / CM shifts
    ex('''update List_UpgradeCarBodyWeight set Mass=?, InitialMass=?, CMHeight=?, CMBackFront=?,
          BlockDimX=1.892, BlockDimY=1.104, BlockDimZ=4.231 where CarBodyId=? and Level=?''',
       (MASS * m / m0, MASS, 0.545 + (h - h0), 0.62 + (f - f0), BODY, lvl))
ex('update Data_Car set CurbWeight=?, WeightDistribution=0.62 where Id=?', (MASS / 100, CAR))

# ---- wheels and tyres: stock 16" / 195 (the Fiesta ST's 17" / 205 were what the physics actually used)
for t in ('List_UpgradeRimSizeFront', 'List_UpgradeRimSizeRear'):
    col = 'FrontWheelDiameter' if 'Front' in t else 'RearWheelDiameter'
    for lvl, d in ((0, 16), (1, 17), (2, 18)):
        ex(f'update "{t}" set "{col}"=? where Ordinal=? and Level=?', (d, CAR, lvl))
for t in ('List_UpgradeCarBodyTireWidthFront', 'List_UpgradeCarBodyTireWidthRear'):
    col = 'FrontTireWidth' if 'Front' in t else 'RearTireWidth'
    for lvl, w in ((0, 195), (2, 205), (3, 225)):
        ex(f'update "{t}" set "{col}"=? where CarBodyId=? and Level=?', (w, BODY, lvl))
ex('update List_UpgradeTireCompound set TireCompoundID=4 where Ordinal=? and IsStock=1', (CAR,))   # road tyre, as Fiesta Mk7

# ---- brakes: 266 mm vented discs front, 228.7 mm drums rear, single-piston calipers
ex('''update List_UpgradeBrakes set FrontBrakeSize=10, FrontBrakeSizeMM=266.0, FrontBrakeTypeID=2, FrontCaliperPistons=1,
      RearBrakeSize=9, RearBrakeSizeMM=228.7, RearBrakeTypeID=1, RearCaliperPistons=0 where Ordinal=? and IsStock=1''', (CAR,))

# ---- suspension (stock level): the game's Fiesta Mk7 setup scaled to the 207's mass
ref_sd = q('select FrontSpringDamperPhysicsID, RearSpringDamperPhysicsID from List_UpgradeSpringDamper where Ordinal=? and IsStock=1', REF_CAR)[0]
my_sd = q('select FrontSpringDamperPhysicsID, RearSpringDamperPhysicsID from List_UpgradeSpringDamper where Ordinal=? and IsStock=1', CAR)[0]
for ref_id, my_id in zip(ref_sd, my_sd):
    s, b, r = q('select DefSpringRate, DefDampenBumpRate, DefDampenReboundRate from List_SpringDamperPhysics where SpringDamperPhysicsID=?', ref_id)[0]
    ex('''update List_SpringDamperPhysics set DefSpringRate=?, MinSpringRate=?, MaxSpringRate=?, DefDampenBumpRate=?, MinDampenBumpRate=?,
          MaxDampenBumpRate=?, DefDampenReboundRate=?, MinDampenReboundRate=?, MaxDampenReboundRate=? where SpringDamperPhysicsID=?''',
       (s * K, s * K, s * K, b * K, b * K, b * K, r * K, r * K, r * K, my_id))
for side in ('Front', 'Rear'):
    ref = q(f'select a.DefSwaybarStiffness from List_UpgradeAntiSway{side} u join List_AntiSwayPhysics a on a.AntiSwayPhysicsID=u.AntiSwayPhysicsID where u.Ordinal=? and u.IsStock=1', REF_CAR)[0][0]
    mine = q(f'select AntiSwayPhysicsID from List_UpgradeAntiSway{side} where Ordinal=? and IsStock=1', CAR)[0][0]
    ex('update List_AntiSwayPhysics set DefSwaybarStiffness=?, MinSwaybarStiffness=?, MaxSwaybarStiffness=? where AntiSwayPhysicsID=?', (ref * K, ref * K, ref * K, mine))

# ---- drivetrain: open differential, clutch sized for 215 Nm (the ST's was sized for 290 Nm overboost)
ex('''update List_UpgradeDrivetrainDifferential set FrontLimitedSlipTorqueAccel=0, FrontLimitedSlipTorqueDecel=0,
      RearLimitedSlipTorqueAccel=0, RearLimitedSlipTorqueDecel=0, CenterLimitedSlipTorqueAccel=0, CenterLimitedSlipTorqueDecel=0
      where DrivetrainID=? and IsStock=1''', (DT,))
ex('update List_UpgradeDrivetrainClutch set ClutchMaxTorque=? where DrivetrainID=? and IsStock=1', (828.937 * 215 / 290, DT))

# ---- aero: Cd 0.30-0.32 vs the Fiesta Mk7's ~0.33 with near-identical frontal area; game drag value scaled from car 1082
ref_drag = q('select BodyAeroLongitudinalDrag from Data_Car where Id=?', REF_CAR)[0][0]
ex('update Data_Car set BodyAeroLongitudinalDrag=? where Id=?', (ref_drag * 0.31 / 0.33, CAR))
c.commit()
print('done')

# ---- upgrade shop: no Fiesta ST body kit (Forza front bumper and rear wing would bring Fiesta panels onto the 207)
c = sqlite3.connect(DB)
c.execute('delete from List_UpgradeRearWing where Ordinal=? and IsStock=0', (CAR,))
c.execute('delete from List_UpgradeCarBodyFrontBumper where CarBodyID=? and IsStock=0', (BODY,))
c.commit()
