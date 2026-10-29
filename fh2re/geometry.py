"""Decode an FH2 car-part .modelbin into editable geometry and rebuild every buffer from it.

Model (as found in FH2 car parts):
  * one float3 position buffer (VerB id -1) holding every vertex of the part, group after group
  * per "group" of vertices: an attribute buffer (normals, 4 UV sets, tangents) and optionally a morph
    buffer (damage deformation), indexed by the vertex's position inside the group
  * one 32-bit index buffer; render meshes (one per LOD x material) own consecutive index ranges, and
    'Shadow' meshes reuse ranges of them
  * index values are global (into the position buffer); a mesh's base_vertex is -(group start), and its
    position view starts at (group start * 12)
"""
import struct
from modelbin import Bundle

# offsets inside a v1.7 Mesh blob
O_MAT, O_BONE, O_LODS = 0x00, 0x02, 0x04
O_IBID, O_START, O_BASE, O_COUNT, O_TRIS = 0x11, 0x19, 0x1D, 0x21, 0x25
O_ACMR, O_UNIQ, O_LAYOUT, O_NVB, O_VB0 = 0x29, 0x2D, 0x31, 0x35, 0x39


def i32(d, o): return struct.unpack_from('<i', d, o)[0]
def u32(d, o): return struct.unpack_from('<I', d, o)[0]


def acmr(indices, cache=32):
    """average cache miss ratio with a FIFO post-transform cache (what the tools report)"""
    fifo, seen, miss = [], set(), 0
    for v in indices:
        if v not in seen:
            miss += 1
            fifo.append(v); seen.add(v)
            if len(fifo) > cache:
                seen.discard(fifo.pop(0))
    return miss / (len(indices) // 3) if indices else 0.0


class Part:
    def __init__(self, raw):
        self.b = Bundle.read(raw)
        b = self.b
        self.meshes = [bl for bl in b.blobs if bl['tag'] == 'Mesh']
        ib = next(bl for bl in b.blobs if bl['tag'] == 'IndB')
        self.ib_blob = ib
        n = u32(ib['data'], 0)
        assert struct.unpack_from('<H', ib['data'], 8)[0] == 4, 'expected 32-bit indices'
        idx = list(struct.unpack_from('<%dI' % n, ib['data'], 16))
        bufs = {}
        for bl in b.blobs:
            if bl['tag'] in ('VerB', 'MBuf'):
                bid = struct.unpack('<i', b.meta(bl, 'Id  '))[0]
                length, size, stride, nel, z, fmt = struct.unpack_from('<IIHBBI', bl['data'], 0)
                bufs[(bl['tag'], bid)] = dict(blob=bl, length=length, stride=stride, nel=nel, z=z, fmt=fmt)
        self.bufs = bufs
        pos = bufs[('VerB', -1)]
        P = [struct.unpack_from('<fff', pos['blob']['data'], 16 + 12 * i) for i in range(pos['length'])]

        # groups: attribute buffer id -> start in the position buffer
        starts = {}
        for m in self.meshes:
            d = m['data']
            for k in range(u32(d, O_NVB)):
                vid, slot, stride, off = struct.unpack_from('<iiii', d, O_VB0 + 16 * k)
                if vid != -1:
                    starts[vid] = -i32(d, O_BASE)
        self.groups = {}
        for gid, s in starts.items():
            a = bufs[('VerB', gid)]
            mb = bufs.get(('MBuf', gid))
            n = a['length']
            g = {'positions': P[s:s + n],
                 'attrs': [bytes(a['blob']['data'][16 + i * a['stride']:16 + (i + 1) * a['stride']]) for i in range(n)],
                 'morph': [bytes(mb['blob']['data'][16 + i * mb['stride']:16 + (i + 1) * mb['stride']]) for i in range(n)] if mb else None,
                 'start': s}
            self.groups[gid] = g
        self.group_order = sorted(self.groups, key=lambda g: self.groups[g]['start'])
        covered = sum(len(self.groups[g]['positions']) for g in self.groups)
        assert covered == len(P), f'position buffer {len(P)} != groups {covered}'

        # render meshes own index ranges (stored group-local); shadows point at those ranges
        self.render, self.shadows = [], []
        owner = {}
        for m in self.meshes:
            d = m['data']
            vb = [struct.unpack_from('<iiii', d, O_VB0 + 16 * k) for k in range(u32(d, O_NVB))]
            start, count = i32(d, O_START), u32(d, O_COUNT)
            gid = next((v[0] for v in vb if v[0] != -1), None)
            if gid is None:
                self.shadows.append({'blob': m, 'start': start, 'count': count})
                continue
            gs = self.groups[gid]['start']
            r = {'blob': m, 'group': gid, 'start': start,
                 'indices': [i - gs for i in idx[start:start + count]]}
            self.render.append(r)
            owner[start] = r
        self.render.sort(key=lambda r: r['start'])
        for s in self.shadows:   # express each shadow as a run of render ranges
            run, pos_, end = [], s['start'], s['start'] + s['count']
            while pos_ < end:
                r = owner[pos_]; run.append(r); pos_ += len(r['indices'])
            assert pos_ == end
            s['run'] = run

    # ------------------------------------------------------------------
    def build(self):
        b = self.b
        # 1. position buffer, group by group (original order)
        P = []
        for gid in self.group_order:
            g = self.groups[gid]; g['start'] = len(P); P += g['positions']
        # 2. index buffer: render ranges in original order
        idx = []
        for r in self.render:
            gs = self.groups[r['group']]['start']
            r['new_start'] = len(idx)
            idx += [i + gs for i in r['indices']]
        # 3. per-mesh fields
        def bbox(points):
            xs, ys, zs = zip(*points)
            return struct.pack('<6f', min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

        def set_fields(blob, start, glob, gid_for_pos, unique):
            d = blob['data']
            gs = self.groups[gid_for_pos]['start'] if gid_for_pos is not None else 0
            struct.pack_into('<iiII', d, O_START, start, -gs, len(glob), len(glob) // 3)
            struct.pack_into('<f', d, O_ACMR, acmr(glob))
            if unique is not None:
                struct.pack_into('<I', d, O_UNIQ, unique)
            for k in range(u32(d, O_NVB)):
                vid = i32(d, O_VB0 + 16 * k)
                if vid == -1:
                    struct.pack_into('<i', d, O_VB0 + 16 * k + 12, gs * 12)
            for mt in blob['meta']:
                if mt['tag'] == 'BBox':
                    mt['data'] = bbox([P[i] for i in set(glob)])

        for r in self.render:
            glob = idx[r['new_start']:r['new_start'] + len(r['indices'])]
            set_fields(r['blob'], r['new_start'], glob, r['group'], len(set(glob)))
        for s in self.shadows:
            st = s['run'][0]['new_start']
            n = sum(len(r['indices']) for r in s['run'])
            glob = idx[st:st + n]
            set_fields(s['blob'], st, glob, s['run'][0]['group'], None)
        # 4. buffers
        def put(key, rows):
            bf = self.bufs[key]; bl = bf['blob']
            body = b''.join(rows)
            bl['data'] = bytearray(struct.pack('<IIHBBI', len(rows), len(body), bf['stride'], bf['nel'], bf['z'], bf['fmt']) + body)
        put(('VerB', -1), [struct.pack('<fff', *p) for p in P])
        for gid, g in self.groups.items():
            put(('VerB', gid), g['attrs'])
            if g['morph'] is not None:
                put(('MBuf', gid), g['morph'])
        ibd = self.ib_blob
        hdr = struct.unpack_from('<IIHBBI', ibd['data'], 0)
        ibd['data'] = bytearray(struct.pack('<IIHBBI', len(idx), 4 * len(idx), 4, hdr[3], hdr[4], hdr[5]) +
                                struct.pack('<%dI' % len(idx), *idx))
        # 5. model bounding box
        for bl in b.blobs:
            if bl['tag'] == 'Modl':
                for mt in bl['meta']:
                    if mt['tag'] == 'BBox':
                        mt['data'] = bbox(P)
        return b.write()


if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        src = open(f, 'rb').read()
        part = Part(src)
        out = part.build()
        same = out == src
        print(f.split('/')[-1], 'groups', {g: len(part.groups[g]['positions']) for g in part.group_order},
              'render meshes', len(part.render), 'shadows', len(part.shadows), '-> rebuilt identical:', same)
        if not same:
            diffs = [i for i, (a, c) in enumerate(zip(src, out)) if a != c]
            print('  size', len(src), len(out), 'differences', len(diffs), [hex(x) for x in diffs[:12]])


def compact(part):
    """Drop vertices no render mesh uses any more and renumber everything (vertex counts change)."""
    for gid, g in part.groups.items():
        used = sorted({i for r in part.render if r['group'] == gid for i in r['indices']})
        remap = {old: new for new, old in enumerate(used)}
        g['positions'] = [g['positions'][i] for i in used]
        g['attrs'] = [g['attrs'][i] for i in used]
        if g['morph'] is not None:
            g['morph'] = [g['morph'][i] for i in used]
        for r in part.render:
            if r['group'] == gid:
                r['indices'] = [remap[i] for i in r['indices']]


def keep_triangles(part, predicate):
    """predicate(p0, p1, p2) -> bool, with positions in car space; applied to every render mesh"""
    for r in part.render:
        P = part.groups[r['group']]['positions']
        ix = r['indices']; out = []
        for t in range(0, len(ix), 3):
            a, b_, c = ix[t:t + 3]
            if predicate(P[a], P[b_], P[c]):
                out += [a, b_, c]
        r['indices'] = out
