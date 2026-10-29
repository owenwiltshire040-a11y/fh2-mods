"""Move FH2 car-part geometry to and from glTF (.glb), which Blender imports and exports natively.

Export: one glTF mesh per vertex group ("g<id>"), built from that group's most detailed meshes, with
normals, four UV sets (TEXCOORD_0..3), the first tangent (TANGENT) and the second (_TANGENT1).
Import: each glTF mesh named "g<id>" replaces that group's vertices; every LOD mesh of the group then
draws the new triangles. Damage-morph data for new vertices is zero (the panel will not dent yet).

Coordinates: FH2 is Y-up, Z-forward, left-handed; glTF is Y-up, right-handed. We mirror X and reverse
the triangle winding in both directions, so the model appears correctly oriented in Blender.
"""
import json, struct
import numpy as np
from geometry import Part

UV_SLOTS = 5      # transform pairs stored per mesh (4 used)
O_UVT = 0x69      # 20 floats: per slot (u_offset, u_scale, v_offset, v_scale)


def layout_of(part, gid):
    r = next(r for r in part.render if r['group'] == gid)
    lid = struct.unpack_from('<I', r['blob']['data'], 0x31)[0]
    return [e for e in part.b.vertex_layouts()[lid] if e['slot'] == 1], r


def decode_group(part, gid):
    els, r0 = layout_of(part, gid)
    uvt = struct.unpack_from('<20f', r0['blob']['data'], O_UVT)
    g = part.groups[gid]
    rows = np.frombuffer(b''.join(g['attrs']), dtype=np.uint8).reshape(len(g['attrs']), -1)
    out, off = {}, 0
    for e in els:
        n = {10: 8, 35: 4, 28: 4}[e['format']]
        chunk = rows[:, off:off + n].copy()
        if e['format'] == 28:
            out[e['name']] = chunk.astype(np.float32) / 255.0
        elif e['format'] == 10:
            out[e['name']] = chunk.view('<f2').astype(np.float32)
        else:
            q = chunk.view('<u2').astype(np.float64) / 65535.0
            k = int(e['name'][-1])
            uo, us, vo, vs = uvt[4 * k:4 * k + 4]
            out[e['name']] = np.stack([q[:, 0] * us + uo, q[:, 1] * vs + vo], 1).astype(np.float32)
        off += n
    out['POSITION'] = np.array(g['positions'], dtype=np.float32)
    return out, els


def encode_group(part, gid, attrs):
    """attrs: dict of float arrays (NORMAL0 (n,3|4), TEXCOORD0..3 (n,2), TANGENT0/1 (n,4)). Returns rows
    and the UV transforms to store on every mesh of the group."""
    els, _ = layout_of(part, gid)
    n = len(attrs['POSITION'])
    cols, uvt = [], [0.0, 1.0, 0.0, 1.0] * UV_SLOTS
    for e in els:
        a = attrs[e['name']]
        if e['format'] == 28:
            cols.append(np.clip(np.round(np.asarray(a, np.float64) * 255), 0, 255).astype(np.uint8).reshape(n, 4))
        elif e['format'] == 10:
            a4 = np.zeros((n, 4), np.float32); a4[:, :a.shape[1]] = a
            cols.append(a4.astype('<f2').view(np.uint8).reshape(n, 8))
        else:
            k = int(e['name'][-1])
            lo, hi = a.min(0).astype(np.float64), a.max(0).astype(np.float64)
            span = np.where(hi - lo > 1e-9, hi - lo, 1.0)
            q = np.clip(np.round((a - lo) / span * 65535.0), 0, 65535).astype('<u2')
            cols.append(q.view(np.uint8).reshape(n, 4))
            uvt[4 * k:4 * k + 4] = [lo[0], span[0], lo[1], span[1]]
    rows = np.concatenate(cols, 1)
    return [bytes(r) for r in rows], uvt


# ---------------------------------------------------------------- glTF writing / reading
def _glb(meshes):
    """meshes: list of (name, {attr: float32 array}, indices uint32 array)"""
    gl = {'asset': {'version': '2.0', 'generator': 'fh2re'}, 'scene': 0, 'scenes': [{'nodes': []}],
          'nodes': [], 'meshes': [], 'buffers': [], 'bufferViews': [], 'accessors': []}
    blob = bytearray()

    def acc(arr, typ, target):
        nonlocal blob
        arr = np.ascontiguousarray(arr)
        while len(blob) % 4: blob.append(0)
        off = len(blob); blob += arr.tobytes()
        gl['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': arr.nbytes, 'target': target})
        a = {'bufferView': len(gl['bufferViews']) - 1, 'componentType': 5125 if arr.dtype == np.uint32 else 5126,
             'count': len(arr), 'type': typ}
        if typ == 'VEC3' and arr.dtype == np.float32:
            a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
        gl['accessors'].append(a)
        return len(gl['accessors']) - 1

    for name, attrs, idx in meshes:
        prim = {'attributes': {}, 'indices': acc(idx.astype(np.uint32), 'SCALAR', 34963), 'mode': 4}
        for k, v in attrs.items():
            prim['attributes'][k] = acc(v.astype(np.float32), {2: 'VEC2', 3: 'VEC3', 4: 'VEC4'}[v.shape[1]], 34962)
        gl['meshes'].append({'name': name, 'primitives': [prim]})
        gl['nodes'].append({'name': name, 'mesh': len(gl['meshes']) - 1})
        gl['scenes'][0]['nodes'].append(len(gl['nodes']) - 1)
    while len(blob) % 4: blob.append(0)
    gl['buffers'].append({'byteLength': len(blob)})
    js = json.dumps(gl).encode()
    js += b' ' * ((-len(js)) % 4)
    return (struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)) +
            struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(blob), 0x004E4942) + bytes(blob))


def _read_glb(data):
    jl = struct.unpack_from('<I', data, 12)[0]
    gl = json.loads(data[20:20 + jl])
    bl = struct.unpack_from('<I', data, 20 + jl)[0]
    blob = data[28 + jl:28 + jl + bl]
    def get(i):
        a = gl['accessors'][i]; v = gl['bufferViews'][a['bufferView']]
        dt = np.dtype({5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']])
        comps = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = v.get('byteStride') or comps * dt.itemsize
        rows = [np.frombuffer(blob, dt, comps, start + j * stride) for j in range(a['count'])] \
            if stride != comps * dt.itemsize else None
        arr = np.array(rows) if rows is not None else np.frombuffer(blob, dt, comps * a['count'], start)
        return arr.reshape(a['count'], comps) if comps > 1 else arr.reshape(-1)
    meshes = {}
    for node in gl['nodes']:
        if 'mesh' not in node: continue
        m = gl['meshes'][node['mesh']]
        name = node.get('name') or m.get('name')
        P, I, base = {}, [], 0
        for prim in m['primitives']:
            attrs = {k: get(v) for k, v in prim['attributes'].items()}
            n = len(attrs['POSITION'])
            for k, v in attrs.items():
                P.setdefault(k, []).append(v)
            I.append(get(prim['indices']).astype(np.int64) + base); base += n
        meshes[name.split('.')[0]] = ({k: np.concatenate(v) for k, v in P.items()}, np.concatenate(I))
    return meshes


def flip(attrs, idx):
    """FH2 <-> glTF: mirror X (positions, normals, tangents) and reverse triangle winding"""
    out = {}
    for k, v in attrs.items():
        v = v.copy()
        if k in ('POSITION', 'NORMAL', 'TANGENT', '_TANGENT1'):
            v[:, 0] = -v[:, 0]
        if k in ('TANGENT', '_TANGENT1'):
            v[:, 3] = -v[:, 3]          # mirroring flips the tangent frame's handedness
        out[k] = v
    t = idx.reshape(-1, 3)[:, [0, 2, 1]].reshape(-1)
    return out, t


def export_glb(part):
    meshes = []
    for gid in part.group_order:
        dec, _ = decode_group(part, gid)
        rs = [r for r in part.render if r['group'] == gid]
        top = min(rs, key=lambda r: struct.unpack_from('<H', r['blob']['data'], 4)[0])
        used = sorted(set(top['indices']))
        remap = {o: i for i, o in enumerate(used)}
        idx = np.array([remap[i] for i in top['indices']], np.uint32)
        a = {'POSITION': dec['POSITION'][used]}
        if 'NORMAL0' in dec: a['NORMAL'] = dec['NORMAL0'][used][:, :3]
        for k in range(4):
            if f'TEXCOORD{k}' in dec: a[f'TEXCOORD_{k}'] = dec[f'TEXCOORD{k}'][used]
        if 'TANGENT0' in dec: a['TANGENT'] = dec['TANGENT0'][used]
        if 'TANGENT1' in dec: a['_TANGENT1'] = dec['TANGENT1'][used]
        a, idx = flip(a, idx)
        meshes.append((f'g{gid}', a, idx))
    return _glb(meshes)


def tangents(P, N, UV, idx):
    """per-vertex tangent frames (Lengyel) for one UV set; w = handedness"""
    t1 = np.zeros_like(P); t2 = np.zeros_like(P)
    tri = idx.reshape(-1, 3)
    p0, p1, p2 = P[tri[:, 0]], P[tri[:, 1]], P[tri[:, 2]]
    w0, w1, w2 = UV[tri[:, 0]], UV[tri[:, 1]], UV[tri[:, 2]]
    e1, e2, d1, d2 = p1 - p0, p2 - p0, w1 - w0, w2 - w0
    r = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(r) < 1e-12, 1e-12, r)
    s = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / r[:, None]
    t = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / r[:, None]
    for k in range(3):
        np.add.at(t1, tri[:, k], s); np.add.at(t2, tri[:, k], t)
    T = t1 - N * np.sum(N * t1, 1, keepdims=True)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    w = np.where(np.sum(np.cross(N, T) * t2, 1) < 0, -1.0, 1.0)
    return np.concatenate([T, w[:, None]], 1).astype(np.float32)


def import_glb(part, data):
    meshes = _read_glb(data)
    for gid in part.group_order:
        key = f'g{gid}'
        if key not in meshes:
            continue
        a, idx = meshes[key]
        a, idx = flip(a, idx.astype(np.uint32))
        P = a['POSITION'].astype(np.float32)
        n = len(P)
        N = a.get('NORMAL')
        if N is None:
            raise ValueError(f'{key}: export normals from Blender')
        attrs = {'POSITION': P, 'NORMAL0': N}
        uv0 = a.get('TEXCOORD_0', np.zeros((n, 2), np.float32))
        for k in range(4):
            attrs[f'TEXCOORD{k}'] = a.get(f'TEXCOORD_{k}', uv0)
        attrs['TANGENT0'] = a['TANGENT'] if 'TANGENT' in a else tangents(P, N, attrs['TEXCOORD0'], idx)
        attrs['TANGENT1'] = a['_TANGENT1'] if '_TANGENT1' in a else tangents(P, N, attrs['TEXCOORD1'], idx)
        rows, uvt = encode_group(part, gid, attrs)
        g = part.groups[gid]
        g['positions'] = [tuple(map(float, p)) for p in P]
        g['attrs'] = rows
        if g['morph'] is not None:
            stride = len(g['morph'][0]) if g['morph'] else 16
            g['morph'] = [bytes(stride)] * n
        il = [int(i) for i in idx]
        for r in part.render:
            if r['group'] == gid:
                r['indices'] = il
                struct.pack_into('<20f', r['blob']['data'], O_UVT, *uvt)
    return part


if __name__ == '__main__':
    import sys
    cmd, src = sys.argv[1], sys.argv[2]
    if cmd == 'export':
        open(sys.argv[3], 'wb').write(export_glb(Part(open(src, 'rb').read())))
    elif cmd == 'import':
        p = import_glb(Part(open(src, 'rb').read()), open(sys.argv[3], 'rb').read())
        open(sys.argv[4], 'wb').write(p.build())


def smooth_normals(P, idx, weld=1e-5):
    """area-weighted vertex normals, welded across UV seams (vertices at the same position share one)"""
    tri = idx.reshape(-1, 3)
    fn = np.cross(P[tri[:, 1]] - P[tri[:, 0]], P[tri[:, 2]] - P[tri[:, 0]])
    key = np.round(P / weld).astype(np.int64)
    _, wid = np.unique(key, axis=0, return_inverse=True)
    wid = wid.reshape(-1)
    acc = np.zeros((wid.max() + 1, 3))
    for k in range(3):
        np.add.at(acc, wid[tri[:, k]], fn)
    N = acc[wid]
    return (N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)).astype(np.float32)
