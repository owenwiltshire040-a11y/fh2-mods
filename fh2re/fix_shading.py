"""Apply the lighting fix to an already built car zip (cars built before build_car.py's TRANSFER_UV='roof' default).

python3 fh2re/fix_shading.py car.zip donor.zip out.zip [part ...]     (default part: body_a)

Every vertex of each rebuilt group gets TEXCOORD1-4 = the donor's same group's most exposed roof point (the stock
paint's occlusion / sky values). The old builders used one texel for everything, taken from whichever group's vertex
pointed most upward - on the Charger and Fiesta that is the black-plastic trim group - so the whole car was shaded like
matte, shadowed trim: no sky light or reflections, the side away from the sun nearly black. TEXCOORD0 is kept.
"""
import sys, os, zipfile, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geometry import Part
from body_swap import set_group, material_names
from gltf_bridge import decode_group


def roof_values(p, gid):
    d, _ = decode_group(p, gid)
    P = d['POSITION'][:, :3].astype(float); N = d['NORMAL0'][:, :3].astype(float)
    k = int(np.argmax(N[:, 1] * 2 + P[:, 1] - np.abs(P[:, 0]) - np.abs(P[:, 2] - P[:, 2].mean()) * 0.3))
    return {j: d[f'TEXCOORD{j}'][k].astype(np.float32) for j in (1, 2, 3, 4) if f'TEXCOORD{j}' in d}, P[k]


def fix_part(data, donor_data):
    p = Part(data); dp = Part(donor_data); nm = material_names(p)
    for gid in p.group_order:
        if gid not in dp.groups: continue
        d, _ = decode_group(p, gid)
        if len(d['POSITION']) < 2: continue
        const, where = roof_values(dp, gid)
        by = {}
        for r in p.render:
            if r['group'] == gid and nm[id(r['blob'])] not in by: by[nm[id(r['blob'])]] = np.asarray(r['indices'], np.int64)
        real = [t for i in by.values() for t in i.reshape(-1, 3) if len(set(t.tolist())) == 3]
        if not real: continue                                        # a blanked group (one invisible point)
        P = d['POSITION'][:, :3].astype(np.float64); N = d['NORMAL0'][:, :3].astype(np.float64)
        UV0 = d['TEXCOORD0'].astype(np.float64) if 'TEXCOORD0' in d else np.zeros((len(P), 2))
        keep = len(P) - 1 if np.allclose(P[-1], P[0]) and len(P) > 1 else len(P)    # set_group's own trailing degenerate vertex
        set_group(p, gid, dict(P=P[:keep], N=N[:keep], UV=UV0[:keep], UVconst=const),
                  {m: v for m, v in ((m, i.reshape(-1, 3)[(i.reshape(-1, 3) < keep).all(1) & (np.ptp(i.reshape(-1, 3), 1) > 0)].reshape(-1)) for m, i in by.items()) if len(v)})
        print(f'    group {gid}: TEXCOORD1-4 = donor roof point {np.round(where, 2)} ({keep} vertices)')
    out = p.build(); Part(out); return out


if __name__ == '__main__':
    car, donor, out = sys.argv[1:4]; parts = sys.argv[4:] or ['body_a']
    cz, dz = zipfile.ZipFile(car), zipfile.ZipFile(donor)
    dnames = {n.lower().split('/')[-1]: n for n in dz.namelist() if n.lower().endswith('.modelbin')}
    fixed = {}
    for n in cz.namelist():
        fn = n.lower().split('/')[-1]
        if fn.endswith('.modelbin') and fn[:-9] in parts and fn in dnames:
            print(' ', n); fixed[n] = fix_part(cz.read(n), dz.read(dnames[fn]))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
        for i in cz.infolist(): zo.writestr(i, fixed.get(i.filename) or cz.read(i.filename))
    print('wrote', out, '-', len(fixed), 'parts')
