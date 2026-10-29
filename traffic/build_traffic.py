"""Buyable copies of FH2's traffic cars.

Each traffic car gets a clone with id 3000+old, sharing the original's model (MediaName), engine, drivetrain,
thumbnail and name. The originals stay on the TrafficCars list so the roads keep their traffic.
usage: build_traffic.py vanilla.slt out.slt <car ids...>
"""
import sqlite3, shutil, sys

SRC, DST = sys.argv[1], sys.argv[2]
IDS = [int(x) for x in sys.argv[3:]]
OFFSET = 3000

# Autoshow category per car (Data_Car_Buckets.CarBucket) and a sensible price where the stock one is odd
BUCKET = {283: 25, 286: 19, 379: 19, 414: 21, 428: 19, 631: 21, 1047: 23, 1082: 23, 1089: 23, 1127: 18,
          1257: 23, 1358: 23, 1363: 23, 1364: 23, 1383: 24, 1393: 14, 1674: 21}
PRICE = {631: 18000, 414: 45000, 1674: 55000}

shutil.copy(SRC, DST)
c = sqlite3.connect(DST)
q = lambda s, *a: c.execute(s, a).fetchall()
cols = lambda t: [r[1] for r in c.execute(f'pragma table_info("{t}")')]

CAR_TABLES = ['Data_Car', 'Data_CarBody', 'CameraOverrides', 'CarPartPositions', 'CarExceptions',
              'List_AntiSwayPhysics', 'List_SpringDamperPhysics', 'List_UpgradeAntiSwayFront',
              'List_UpgradeAntiSwayRear', 'List_UpgradeBrakes', 'List_UpgradeCarBody',
              'List_UpgradeCarBodyChassisStiffness', 'List_UpgradeCarBodyFrontBumper', 'List_UpgradeCarBodyHood',
              'List_UpgradeCarBodyRearBumper', 'List_UpgradeCarBodySideSkirt', 'List_UpgradeCarBodyTireWidthFront',
              'List_UpgradeCarBodyTireWidthRear', 'List_UpgradeCarBodyWeight', 'List_UpgradeRearWing',
              'List_UpgradeRimSizeFront', 'List_UpgradeRimSizeRear', 'List_UpgradeSpringDamper',
              'List_UpgradeTireCompound', 'List_UpgradeEngine', 'List_UpgradeDrivetrain']
KEYS = ('id', 'ordinal', 'carid', 'modelid')


def insert(t, row):
    cs = list(row)
    c.execute(f'insert into "{t}" ({",".join(chr(34) + x + chr(34) for x in cs)}) values ({",".join("?" * len(cs))})',
              [row[x] for x in cs])


next_col = q('select max(ID) from Combo_Colors')[0][0] + 1
for old in IDS:
    new = old + OFFSET
    assert not q('select 1 from Data_Car where Id=?', new), new

    def shift(v):
        if isinstance(v, int):
            if v == old: return new
            if old * 1000 <= v <= old * 1000 + 999: return new * 1000 + (v - old * 1000)
        return v

    for t in CAR_TABLES:
        cs = cols(t)
        where, a = [], []
        for k in cs:
            if k.lower() in KEYS:
                where += [f'"{k}"=?', f'"{k}" between ? and ?']; a += [old, old * 1000, old * 1000 + 999]
        if not where:
            continue
        for r in q(f'select * from "{t}" where ' + ' or '.join(where), *a):
            row = dict(zip(cs, r))
            for k, v in row.items():
                # car keys and the car's own 1363xxx-style sub-ids; engine/drivetrain ids are left shared
                if k.lower() in KEYS or (isinstance(v, int) and old * 1000 <= v <= old * 1000 + 999
                                         and k.lower() not in ('engineid', 'drivetrainid')):
                    row[k] = shift(v)
            insert(t, row)

    for r in q('select * from Combo_Colors where Ordinal=?', old):
        row = dict(zip(cols('Combo_Colors'), r)); row.update(Ordinal=new, ID=next_col); next_col += 1
        insert('Combo_Colors', row)

    insert('Data_Car_Buckets', {'CarId': new, 'CarBucket': BUCKET[old], 'BucketHero': 0})
    c.execute('update Data_Car set IsPurchased=1, IsDrivable=1 where Id=?', (new,))
    if old in PRICE:
        c.execute('update Data_Car set BaseCost=? where Id=?', (PRICE[old], new))
    print(old, '->', new, q('select MediaName, BaseCost from Data_Car where Id=?', new)[0], 'bucket', BUCKET[old])

c.commit()
