"""Read an Assetto Corsa .kn5 model (unencrypted, versions 5-6): embedded textures, materials, node tree, meshes.

  python3 tools/kn5.py car.kn5            # summary: textures, materials, meshes (world bounds, LOD range)

Layout (little endian; strings are int32 length + bytes):
  'sc6969', int32 version, [int32 extra if version > 5]
  textures:  int32 n; each int32 type, string name, int32 size, bytes (DDS / PNG)
  materials: int32 n; each string name, string shader, u8 blend, u8 alpha_tested, [int32 depth if version > 4],
             int32 nprops (string, 1+2+3+4 floats), int32 nres (string slot name, int32 slot, string texture)
  nodes (recursive from one root): int32 class, string name, int32 nchildren, u8 active, then
    class 1 (dummy):   16 floats (row-major, translation in the last row)
    class 2 (mesh):    u8 cast_shadows, u8 visible, u8 transparent, int32 nv, nv x (pos3 normal3 uv2 tangent3),
                       int32 ni, ni x u16, int32 material, uint32 layer, float lod_in, float lod_out,
                       float3 sphere centre, float radius, u8 renderable
    class 3 (skinned): u8 x3, int32 nbones (string, 16 floats), int32 nv, nv x (44 bytes + 4 weights + 4 indices),
                       int32 ni, u16 indices, int32 material, uint32 layer, 8 bytes
"""
import struct, sys
import numpy as np


class R:
    def __init__(self, d): self.d = d; self.o = 0
    def i(self): v = struct.unpack_from('<i', self.d, self.o)[0]; self.o += 4; return v
    def u(self): v = struct.unpack_from('<I', self.d, self.o)[0]; self.o += 4; return v
    def f(self, n=1):
        v = struct.unpack_from(f'<{n}f', self.d, self.o); self.o += 4 * n; return v if n > 1 else v[0]
    def b(self): v = self.d[self.o]; self.o += 1; return v
    def s(self):
        n = self.i(); v = self.d[self.o:self.o + n].decode('latin1'); self.o += n; return v
    def raw(self, n): v = self.d[self.o:self.o + n]; self.o += n; return v


def read(path_or_bytes):
    d = open(path_or_bytes, 'rb').read() if isinstance(path_or_bytes, str) else path_or_bytes
    r = R(d); assert r.raw(6) == b'sc6969', 'not a kn5'
    ver = r.i(); extra = r.i() if ver > 5 else None
    tex = {}
    for _ in range(r.i()):
        typ = r.i(); name = r.s(); tex[name] = bytes(r.raw(r.i()))
    mats = []
    for _ in range(r.i()):
        m = dict(name=r.s(), shader=r.s(), blend=r.b(), alpha_tested=r.b())
        if ver > 4: m['depth'] = r.i()
        m['props'] = {}
        for _ in range(r.i()):
            n = r.s(); a = r.f(); b = r.f(2); c = r.f(3); dd = r.f(4); m['props'][n] = (a, b, c, dd)
        m['tex'] = {}
        for _ in range(r.i()):
            slot = r.s(); r.i(); m['tex'][slot] = r.s()
        mats.append(m)
    meshes = []

    def node(parent_m, path):
        cls = r.i(); name = r.s(); nch = r.i(); active = r.b()
        n = dict(cls=cls, name=name, active=active, path=path + [name])
        M = parent_m
        if cls == 1:
            local = np.array(r.f(16), np.float64).reshape(4, 4); M = local @ parent_m; n['local'] = local
        elif cls in (2, 3):
            n['cast_shadows'], n['visible'], n['transparent'] = r.b(), r.b(), r.b()
            if cls == 3:
                n['bones'] = [(r.s(), np.array(r.f(16)).reshape(4, 4)) for _ in range(r.i())]
            nv = r.i(); stride = 44 if cls == 2 else 76
            v = np.frombuffer(r.raw(nv * stride), np.float32).reshape(nv, stride // 4)
            ni = r.i(); idx = np.frombuffer(r.raw(ni * 2), '<u2').astype(np.int64)
            n['material'] = r.i(); n['layer'] = r.u()
            if cls == 2:
                n['lod_in'], n['lod_out'] = r.f(), r.f(); n['sphere'] = r.f(4); n['renderable'] = r.b()
            else:
                r.raw(8)
            P = v[:, 0:3].astype(np.float64); N = v[:, 3:6].astype(np.float64)
            n['P_local'] = P; n['N_local'] = N; n['UV'] = v[:, 6:8].copy(); n['T'] = idx.reshape(-1, 3)
            Pw = np.c_[P, np.ones(len(P))] @ M; n['P'] = Pw[:, :3]
            n['N'] = N @ M[:3, :3]; n['world'] = M
            meshes.append(n)
        n['children'] = [node(M, n['path']) for _ in range(nch)]
        return n

    root = node(np.eye(4), [])
    assert r.o == len(d), f'trailing bytes {len(d) - r.o}'
    return dict(version=ver, extra=extra, textures=tex, materials=mats, root=root, meshes=meshes)


def walk(n, depth=0):
    yield n, depth
    for c in n['children']: yield from walk(c, depth + 1)


if __name__ == '__main__':
    k = read(sys.argv[1])
    print('version', k['version'], 'textures', len(k['textures']), 'materials', len(k['materials']), 'meshes', len(k['meshes']))
    for m in k['meshes']:
        P = m['P']
        print(f"{'/'.join(m['path'][-3:]):60s} v{len(P):6d} t{len(m['T']):6d} mat {k['materials'][m['material']]['name'][:28]:28s} "
              f"lod {m.get('lod_in', 0):.0f}-{m.get('lod_out', 0):.0f} x[{P[:,0].min():.2f},{P[:,0].max():.2f}] "
              f"y[{P[:,1].min():.2f},{P[:,1].max():.2f}] z[{P[:,2].min():.2f},{P[:,2].max():.2f}]")
