"""Working lamps on the Charger generic donor (the 207's method, generalised).

The game lights a lamp by MATERIAL: each donor light part carries emitter materials that switch on with a light
function, and Lights.bin puts the light points (beams, glow sprites) on those parts:
  headlightl_a / headlightr_a  group 0 (near LODs): 'hl_hb' = low+high beam emitter, 'drl'; group 1: 'turnSignal'
                               group 2/3 = LOD64 copies
  taillightl_a / taillightr_a  group 0: 'lbk_led_001' = tail lamp, brighter on the brakes; group 2 = LOD64
(taillightc_a, the Charger's centre reverse lamp, is skinned to a bone, so it is not used.)
A model's lamp triangles go into those groups drawn with the emitter material; every vertex samples the spot of the
donor texture that material itself uses (median donor UV), so the game lights it like the donor's lamp. The lamp
triangles are taken OUT of the body so the two don't z-fight. Lights.bin: every light is re-tied to the four kept
parts and moved by (model lamp centre - donor emitter centre) per side.

spec LIGHTS = {'head': dict(mats=[...], box=((x0,y0,z0),(x1,y1,z1)) optional),
               'tail': dict(...), 'drl': ..., 'turn_f': ...}   (front functions need z > 0, rear z < 0)
"""
import struct
import numpy as np
from geometry import Part
from body_swap import set_group, blank_group, material_names
from gltf_bridge import decode_group

ROOT_SUB = {'head': 'primarylights', 'tail': 'secondarylights'}
EMIT = {  # function -> (part kind, group near, group far, material, added material blob or None)
    'head': ('head', 0, 2, 'hl_hb', None), 'drl': ('head', 0, 2, 'drl', None), 'turn_f': ('head', 1, 3, 'turnSignal', None),
    # rear: the 207's lamp materials (f1/extract_lamp_mati.py), installed into the Charger tail parts. Their light mask
    # (param 0x493073a0) matches the Charger's Lights.bin flags: tail+brake 0x45 (type 7 = 0x20045), reverse 0x1 (type 10).
    # The Charger's own lbk_led_001 has mask 0x20, which no light drives: no brake glow by day.
    'tail': ('tail', 0, 2, 'LBK_smoothChrome_custom_brake', 'brake'),
    'reverse': ('tail', 0, 2, 'LBK_standardCH1_003_custom_reverse', 'reverse'),
    'turn_r': ('tail', 0, 2, 'LBK_standardCH1_003_custom_turn', 'turn'),
}
import os
LAMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'f1')
FAR_MAT = {}
LENS = 'gls_patternCH1_009_custom_red'


def _tex_paths(blob):
    """texture paths referenced by a MatI blob (for the model's TRef list)"""
    import re
    return [m.decode('latin1') for m in re.findall(rb'[Gg]ame:\\[ -~]+?\.swatchbin', blob)]


def centre_of(parts, spec):
    """centre of the triangles of spec['mats'] inside spec['box'] (|x|, y, z), without removing them"""
    lo, hi = np.array(spec['box'][0]), np.array(spec['box'][1]); C = []
    for m in spec['mats']:
        for p in parts.get(m, []):
            c = p['V'].reshape(-1, 3, 3).mean(1); a = np.c_[np.abs(c[:, 0]), c[:, 1:]]
            C.append(c[np.all((a >= lo) & (a <= hi), 1)])
    C = np.concatenate(C); return np.array([0.0, C[:, 1].mean(), C[:, 2].mean()])


def take_lamps(parts, lights):
    """{function: (V, N) per corner} for each function; those triangles are removed from `parts` (the body)."""
    out = {}
    for fn, spec in lights.items():
        if fn not in EMIT: continue
        front = EMIT[fn][0] == 'head'
        Vs, Ns = [], []
        for m in spec['mats']:
            for p in parts.get(m, []):
                V = p['V'].reshape(-1, 3, 3); c = V.mean(1)
                k = (c[:, 2] > 0) if front else (c[:, 2] < 0)
                if spec.get('box') is not None:
                    lo, hi = np.array(spec['box'][0]), np.array(spec['box'][1])
                    k &= np.all((np.abs(c) * [1, 0, 0] + c * [0, 1, 1] >= lo) & (np.abs(c) * [1, 0, 0] + c * [0, 1, 1] <= hi), 1)
                if not k.any(): continue
                Vs.append(V[k].reshape(-1, 3)); Ns.append(p['N'].reshape(-1, 3, 3)[k].reshape(-1, 3))
                keep = ~k
                p['V'] = V[keep].reshape(-1, 3); p['N'] = p['N'].reshape(-1, 3, 3)[keep].reshape(-1, 3)
                if 'UV' in p: p['UV'] = p['UV'].reshape(-1, 3, 2)[keep].reshape(-1, 2)
        if Vs: out[fn] = (np.concatenate(Vs), np.concatenate(Ns))
        print(f'  lamps: {fn}: {sum(len(v) for v in Vs) // 3} tris from {spec["mats"]}')
    return out


def _two_sided(V, N):
    n = len(V); T = np.arange(n).reshape(-1, 3)
    return np.r_[V, V], np.r_[N, -N], np.r_[T, T[:, [0, 2, 1]] + n].reshape(-1)


def _donor_uv(p, nm, gid, mat):
    d, _ = decode_group(p, gid)
    ix = [r['indices'] for r in p.render if r['group'] == gid and nm[id(r['blob'])] == mat]
    if not ix or 'TEXCOORD0' not in d: return None, None
    ix = np.unique(np.concatenate(ix))
    const = {j: np.median(d[f'TEXCOORD{j}'][ix], 0) for j in (1, 2, 3, 4) if f'TEXCOORD{j}' in d}
    return np.median(d['TEXCOORD0'][ix], 0), const


def build_part(data, side, kind, lamps):
    """one donor light part (side 'l'/'r', kind 'head'/'tail') filled with the model's lamps of that side"""
    import fhmat
    p = Part(data); nm = material_names(p)
    plan = {}; added = {}
    for fn, (V, N) in lamps.items():
        k, gnear, gfar, mat, blob = EMIT[fn]
        if k == kind and blob and mat not in added and mat not in nm.values():
            mid = fhmat.add_material(p, mat, open(os.path.join(LAMP_DIR, f'lamp_{blob}.bin'), 'rb').read())
            for gid in (gnear, gfar):
                like = next((r for r in p.render if r['group'] == gid), None)
                if like is not None: fhmat.add_mesh(p, like, mid)
            added[mat] = mid; nm = material_names(p)
        if k != kind: continue
        s = V.reshape(-1, 3, 3).mean(1)[:, 0]; sel = (s < 0) if side == 'l' else (s > 0)
        if not sel.any(): continue
        Vs = V.reshape(-1, 3, 3)[sel].reshape(-1, 3); Ns = N.reshape(-1, 3, 3)[sel].reshape(-1, 3)
        layers = [(Vs, mat)]
        if fn == 'tail':   # red glass outside, the glowing layer 3 mm behind it (off = red lamp, on = glow through red)
            layers = [(Vs - Ns * 0.003, mat), (Vs, LENS)]
            if LENS not in added and LENS not in nm.values():
                blob_d = open(os.path.join(LAMP_DIR, 'lamp_redlens.bin'), 'rb').read()
                mid = fhmat.add_material(p, LENS, blob_d, _tex_paths(blob_d))
                for gid in (gnear, gfar):
                    like = next((r for r in p.render if r['group'] == gid), None)
                    if like is not None: fhmat.add_mesh(p, like, mid)
                added[LENS] = mid; nm = material_names(p)
        for Vl, m in layers:
            for gid, mm in ((gnear, m), (gfar, FAR_MAT.get((kind, gfar), m))):
                if gid in p.groups: plan.setdefault(gid, []).append((Vl, Ns, mm))
    for gid in p.group_order:
        if gid not in plan: blank_group(p, gid); continue
        Ps, Nn, UVs, by, base, const = [], [], [], {}, 0, None
        for V, N, m in plan[gid]:
            uv, c = _donor_uv(p, nm, gid, m)
            if uv is None:                               # an added material: no donor UVs of its own; the AO/mask sets from any donor lamp mesh
                uv, c = next(((u, cc) for u, cc in (_donor_uv(p, nm, gid, x) for x in ('lbk_led_001', 'chrome', 'reflector_003', 'lbk_smoothchrome')) if u is not None), (None, None))
            if uv is None: print(f'    {kind}{side} group {gid}: no UVs for {m}, skipped'); continue
            P2, N2, I = _two_sided(V, N)
            Ps.append(P2); Nn.append(N2); UVs.append(np.tile(uv, (len(P2), 1)))
            by[m] = np.concatenate([by[m], I + base]) if m in by else I + base; base += len(P2); const = const or c
        if not Ps: blank_group(p, gid); continue
        P = np.concatenate(Ps)
        set_group(p, gid, dict(P=P, N=np.concatenate(Nn), UV=np.concatenate(UVs), UVconst=const,
                               UVtan=np.stack([P[:, 2] * 0.5, P[:, 1] * 0.5], 1)), by)
        print(f'    {kind}light{side} group {gid}: ' + ', '.join(f'{m} {len(i) // 6}' for m, i in by.items()))
    out = p.build(); Part(out); return out


def donor_centres(src, names):
    """emitter centres of the donor's left lamps (car space; the light parts sit at the car origin)"""
    out = {}
    for kind, mat in (('head', 'hl_hb'), ('tail', 'lbk_led_001')):
        key = next(n for n in names if n.endswith(f'{kind}lightl_a.modelbin'))
        p = Part(src.read(names[key])); nm = material_names(p); d, _ = decode_group(p, 0)
        ix = np.unique(np.concatenate([r['indices'] for r in p.render if r['group'] == 0 and nm[id(r['blob'])] == mat]))
        out[kind] = d['POSITION'][ix, :3].astype(float).mean(0)
    return out


def lights_bin(d, model_c, donor_c, media_root, chmsl=None):
    """re-tie every light to head/taillight l/r and move it from the donor's lamp to the model's.
    model_c / donor_c: {'head': left centre, 'tail': left centre} (right side = mirrored x)."""
    o = 8; n = struct.unpack_from('<I', d, o)[0]; o += 4; paths = []
    for _ in range(n):
        L = struct.unpack_from('<I', d, o)[0]; paths.append((d[o + 4:o + 4 + L].decode(), d[o + 4 + L:o + 6 + L])); o += 6 + L
    cnt = struct.unpack_from('<I', d, o)[0]; o += 4; body = bytearray(d[o:])
    moved = []
    if chmsl is not None:   # where the donor's CHMSL row ends up after the generic rear move, to re-centre it
        rows = [np.array(struct.unpack_from('<3f', body, 76 * i + 12)) for i in range(cnt) if struct.unpack_from('<I', body, 76 * i)[0] == 0]
        chmsl_from = np.mean(rows, 0) + (model_c['tail'] - donor_c['tail']) * [0, 1, 1]
    for i in range(cnt):
        e = 76 * i; t = struct.unpack_from('<I', body, e)[0]
        for k in range(2):
            p = np.array(struct.unpack_from('<3f', body, e + 12 + 32 * k))
            kind = 'head' if p[2] > 0 else 'tail'
            if kind not in model_c: continue
            mirror = np.array([1.0 if p[0] < 0 else -1.0, 1, 1])     # centres are the LEFT lamps; right side = mirrored
            delta = (model_c[kind] - donor_c[kind]) * mirror
            if abs(p[0]) < 0.05: delta[0] = 0           # centre lights (CHMSL, centre reverse) stay on the centre line
            struct.pack_into('<3f', body, e + 12 + 32 * k, *(p + delta))
        if t == 0 and chmsl is not None:               # third brake light: the row of LEDs re-centred on the model's
            for k in range(2):                          # CHMSL (its geometry stays in the body)
                p = np.array(struct.unpack_from('<3f', body, e + 12 + 32 * k)); struct.pack_into('<3f', body, e + 12 + 32 * k, *(p - chmsl_from + chmsl))
        moved.append(t)

    def retie(path):
        name = path.split('\\')[-1].lower(); side = 'r' if ('r_a' in name or 'rhl' in name) and 'ctl' not in name else 'l'
        kind = 'head' if ('head' in name or 'fog' in name or 'hl_' in name or 'rhl' in name or 'lhl' in name) else 'tail'
        if kind not in model_c: return path
        return f'{media_root}scene\\exterior\\{ROOT_SUB[kind]}\\{kind}light{side}_a.modelbin'
    out = bytearray(d[:12])
    for pth, tail in paths:
        q = retie(pth).encode(); out += struct.pack('<I', len(q)) + q + tail
    out += struct.pack('<I', cnt) + body
    print('  Lights.bin:', cnt, 'lights re-tied to', sorted({retie(p).split('\\')[-1] for p, _ in paths}))
    return bytes(out)
