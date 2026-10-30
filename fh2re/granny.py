"""Granny 2 (.gr2) files as FH2 ships them: version 7, little-endian, 64-bit pointers, sections Oodle1-compressed
(compression 2) or raw (0). Read-only type-tree walker plus an uncompressed writer for small edits.

Oodle1 decoder: a port of LunaticInAHat/liboodle (public domain, https://github.com/LunaticInAHat/liboodle).
File layout from Norbyte/LSLib (MIT) and liboodle's demo: 32-byte magic (signature, headersSize), 72-byte header
(version, fileSize, crc32 of everything after byte 104, sectionsOffset, numSections, rootType, rootNode, tag...),
8 x 44-byte section headers, section data, then per section its relocation table (12-byte entries: offset in
section -> section:offset) and mixed-marshalling table (16-byte entries), all raw even when the data is compressed.

usage: granny.py info FILE.gr2            list the file's structure (skeleton bones with their local positions)
       granny.py decompress IN.gr2 OUT.gr2   rewrite with every section raw (round-trips a raw file byte for byte)
       granny.py movebone IN.gr2 OUT.gr2 BONE dx dy dz   shift one bone's local position, write OUT raw
"""
import struct, sys, zlib

MAGIC_LE64 = bytes([0xE5, 0x9B, 0x49, 0x5E, 0x6F, 0x63, 0x1F, 0x14, 0x1E, 0x13, 0xEB, 0xA9, 0x90, 0xBE, 0xED, 0xC4])
HEADER_END = 32 + 72                       # magic + v7 header; the CRC covers everything after this

# ---------------------------------------------------------------- Oodle1 (liboodle port)
ONE = 0x4000
REPEAT_LEN = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
              31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
              59, 60, 61, 128, 192, 256, 512]

class Bitstream:
    def __init__(self, data, pos):
        self.d = data; b = data[pos]; self.i = pos + 1
        self.sr = b >> 1; self.lsb = b & 1; self.mod = 0x80
    def ingest(self):
        while self.mod <= 0x800000:
            b = self.d[self.i] if self.i < len(self.d) else 0; self.i += 1
            self.sr = ((self.sr << 1) | self.lsb) & 0xFFFFFFFF
            self.sr = ((self.sr << 7) | (b >> 1)) & 0xFFFFFFFF
            self.lsb = b & 1; self.mod = (self.mod << 8) & 0xFFFFFFFF
    def peek(self, one):
        self.ingest(); scale = self.mod // one
        return min(self.sr // scale, one - 1)
    def consume(self, min_z, span, one):
        scale = self.mod // one; self.sr -= min_z * scale
        if min_z < one - span: self.mod = span * scale
        else: self.mod -= min_z * scale
    def get(self, one):
        self.ingest(); scale = self.mod // one; z = min(self.sr // scale, one - 1)
        self.sr -= z * scale
        if z < one - 1: self.mod = scale
        else: self.mod -= z * scale
        return z

class Decoder:
    def __init__(self, alphabet, unique):
        self.used = unique; n = alphabet + 2
        self.sym = [0] * n; self.w = [ONE] * n; self.occ = [0] * n
        self.w[0] = 0; self.occ[0] = 4; self.total = 4; self.hls = 0; self.hlsn = 0; self.next_renorm = 8
        self.decay_t = max(256, min((alphabet - 1) * 32, 15160)); self.rri = 4
        self.ri = max(128, min((alphabet - 1) * 2, self.decay_t // 2 - 32))
    def decay(self):
        occ, sym = self.occ, self.sym
        occ[0] //= 2; self.total = occ[0]; hw = hi = 0; idx = 1
        while idx <= self.hls:
            while occ[idx] <= 1:
                if idx >= self.hls: occ[idx] = 0; self.hls -= 1; break
                occ[idx] = occ[self.hls]; occ[self.hls] = 0; sym[idx] = sym[self.hls]; self.hls -= 1
            if not occ[idx]: break
            occ[idx] //= 2; self.total += occ[idx]
            if occ[idx] > hw: hw, hi = occ[idx], idx
            idx += 1
        if hw and hi != self.hls:
            occ[self.hls], occ[hi] = occ[hi], occ[self.hls]; sym[self.hls], sym[hi] = sym[hi], sym[self.hls]
        if self.hls != self.used and not occ[0]: occ[0] = 1; self.total += 1
        for k in range(self.hls + 1, len(self.w)): self.w[k] = ONE
    def renormalize(self):
        q = 0x20000 // self.total; self.w[0] = 0; acc = (self.occ[0] * q) // 8
        for k in range(1, self.hls + 1):
            self.w[k] = acc; acc += (self.occ[k] * q) // 8
        if self.rri * 2 < self.ri: self.rri *= 2; self.next_renorm = self.total + self.rri
        else: self.next_renorm = self.total + self.ri
        self.hlsn = self.hls
        for k in range(self.hls + 1, len(self.w)): self.w[k] = ONE
    def decode(self, bs, alphabet):
        if self.total >= self.next_renorm:
            if self.total >= self.decay_t: self.decay()
            self.renormalize()
        z = bs.peek(ONE); w = self.w; k = 0
        while k <= self.hlsn:
            if w[k + 1] > z: break
            k += 1
        bs.consume(w[k], w[k + 1] - w[k], ONE)
        self.occ[k] += 1; self.total += 1
        if k: return self.sym[k]
        if self.hls != self.hlsn:
            if bs.get(2):
                k = bs.get(self.hls - self.hlsn) + self.hlsn + 1
                self.occ[k] += 2; self.total += 2; return self.sym[k]
        self.hls += 1; s = bs.get(alphabet); self.sym[self.hls] = s; self.occ[self.hls] += 2; self.total += 2
        if self.hls == self.used: self.total -= self.occ[0]; self.occ[0] = 0
        return s

class Oodle1Stream:
    def __init__(self, bs, h0, h1, h2):
        self.bs = bs; self.window = h0 >> 9; self.lit_alpha = h0 & 0x1FF; uniq = h1 & 0x1FF
        self.lit = [Decoder(self.lit_alpha, uniq) for _ in range(4)]
        self.len = []
        for g in range(4):
            self.len += [Decoder(65, (h2 >> (24 - 8 * g)) & 0xFF) for _ in range(16)]
        self.len.append(Decoder(65, 0))
        self.off1_alpha = min(4, self.window + 1); off4_alpha = min(256, self.window // 4 + 1)
        self.off1 = Decoder(self.off1_alpha, self.off1_alpha)
        self.off4 = [Decoder(off4_alpha, off4_alpha) for _ in range(256)]
        self.off1k = Decoder(self.window // 1024 + 1, (h1 >> 19) + 1)
        self.out_n = 0; self.last = 0
    def step(self, out):
        code = self.len[self.last].decode(self.bs, 65); self.last = code
        if not code:
            out.append(self.lit[self.out_n & 3].decode(self.bs, self.lit_alpha)); self.out_n += 1; return
        n = REPEAT_LEN[code]; eff = min(self.window, self.out_n)
        o1 = self.off1.decode(self.bs, self.off1_alpha) + 1
        o1k = self.off1k.decode(self.bs, eff // 1024 + 1)
        o4 = self.off4[o1k].decode(self.bs, min(256, eff // 4 + 1))
        off = o1k * 1024 + o4 * 4 + o1; self.out_n += n
        start = len(out) - off
        for i in range(n): out.append(out[start + i])

def oodle1_decompress(data, size, stop0, stop1):
    """data: the section bytes (3 x 12-byte stream headers, then the bitstream); the three streams end at stop0,
    stop1 and size bytes of output (liboodle's demo / opengr2: Granny splits a section into 32/16/8-bit parts)"""
    hdr = struct.unpack_from('<9I', data, 0); bs = Bitstream(data, 36); out = bytearray()
    for i, end in enumerate((stop0, stop1, size)):
        if len(out) >= size: break
        st = Oodle1Stream(bs, *hdr[3 * i:3 * i + 3])
        while len(out) < end: st.step(out)
    return bytes(out[:size])

# ---------------------------------------------------------------- file
T_NONE, T_INLINE, T_REF, T_REFARRAY, T_ARRAYOFREFS, T_VARIANT, T_REFVARARRAY, T_STRING, T_TRANSFORM = 0, 1, 2, 3, 4, 5, 7, 8, 9
T_REAL32, T_INT8, T_UINT8, T_BINT8, T_NUINT8, T_INT16, T_UINT16, T_BINT16, T_NUINT16, T_INT32, T_UINT32, T_REAL16, T_EMPTYREF = range(10, 23)
SCALAR = {T_REAL32: ('<f', 4), T_INT8: ('<b', 1), T_UINT8: ('<B', 1), T_BINT8: ('<b', 1), T_NUINT8: ('<B', 1), T_INT16: ('<h', 2),
          T_UINT16: ('<H', 2), T_BINT16: ('<h', 2), T_NUINT16: ('<H', 2), T_INT32: ('<i', 4), T_UINT32: ('<I', 4), T_REAL16: ('<H', 2)}

class GR2:
    def __init__(self, data):
        self.raw = data
        assert data[:16] == MAGIC_LE64, 'not a little-endian 64-bit Granny v7 file'
        self.headers_size, self.fmt = struct.unpack_from('<II', data, 16)
        (self.version, self.file_size, self.crc, so, n, rts, rto, rns, rno, self.tag) = struct.unpack_from('<10I', data, 32)
        assert self.version == 7 and self.file_size == len(data), (self.version, self.file_size, len(data))
        self.extra = struct.unpack_from('<4I', data, 72); self.tail = struct.unpack_from('<4I', data, 88)
        self.root_type = (rts, rto); self.root_node = (rns, rno)
        self.sections = []
        for i in range(n):
            h = dict(zip(('comp', 'off', 'csize', 'size', 'align', 'stop0', 'stop1', 'reloc_off', 'nreloc', 'marsh_off', 'nmarsh'),
                         struct.unpack_from('<11I', data, 32 + so + i * 44)))
            blob = data[h['off']:h['off'] + h['csize']]
            if h['size'] == 0: d = b''
            elif h['comp'] == 0: d = blob
            elif h['comp'] == 2: d = oodle1_decompress(blob, h['size'], h['stop0'], h['stop1'])
            else: raise ValueError(f'section {i}: compression {h["comp"]} not supported')
            assert len(d) == h['size'], (i, len(d), h['size'])
            h['data'] = bytearray(d)
            h['reloc'] = data[h['reloc_off']:h['reloc_off'] + h['nreloc'] * 12]
            h['marsh'] = data[h['marsh_off']:h['marsh_off'] + h['nmarsh'] * 16]
            self.sections.append(h)
        self.ptr = {}                                # (section, offset of a pointer field) -> (section, offset) it points at
        for i, h in enumerate(self.sections):
            for k in range(h['nreloc']):
                o, ts, to = struct.unpack_from('<3I', h['reloc'], k * 12); self.ptr[(i, o)] = (ts, to)
        self._defs = {}; self._structs = {}

    # -- low level
    def u32(self, s, o): return struct.unpack_from('<I', self.sections[s]['data'], o)[0]
    def deref(self, s, o): return self.ptr.get((s, o))
    def cstring(self, s, o):
        d = self.sections[s]['data']; e = d.index(b'\0', o); return d[o:e].decode('latin1')

    # -- type tree
    def struct_def(self, s, o):
        """[(type, name, child def (section, offset) or None, array size)] for the definition at (s, o)"""
        if (s, o) in self._defs: return self._defs[(s, o)]
        members = []; p = o
        while True:
            t = self.u32(s, p)
            if t == T_NONE: break
            name = self.cstring(*self.deref(s, p + 4)) if self.deref(s, p + 4) else ''
            members.append((t, name, self.deref(s, p + 12), self.u32(s, p + 20))); p += 44
        self._defs[(s, o)] = members
        return members

    def member_size(self, t, child, n):
        n = n or 1
        if t == T_INLINE: return n * self.struct_size(child)
        if t in SCALAR: return n * SCALAR[t][1]
        return n * {T_REF: 8, T_STRING: 8, T_VARIANT: 16, T_ARRAYOFREFS: 12, T_REFARRAY: 12, T_REFVARARRAY: 20, T_TRANSFORM: 68, T_EMPTYREF: 0}[t]

    def struct_size(self, d): return sum(self.member_size(t, c, n) for t, _, c, n in self.struct_def(*d))

    def read_struct(self, d, s, o, inline=False):
        """the struct of definition d at (s, o) as a dict; '_addr' holds each member's (section, offset)"""
        key = (d, s, o)
        if not inline and key in self._structs: return self._structs[key]
        out = {'_addr': {}, '_def': d}
        if not inline: self._structs[key] = out
        p = o
        for t, name, child, n in self.struct_def(*d):
            out['_addr'][name] = (s, p); cnt = n or 1
            if t == T_INLINE:
                sz = self.struct_size(child); vals = [self.read_struct(child, s, p + k * sz, True) for k in range(cnt)]
            elif t in SCALAR:
                f, sz = SCALAR[t]; vals = [struct.unpack_from(f, self.sections[s]['data'], p + k * sz)[0] for k in range(cnt)]
            elif t == T_TRANSFORM:
                vals = []
                for k in range(cnt):
                    v = struct.unpack_from('<I16f', self.sections[s]['data'], p + k * 68)
                    vals.append({'flags': v[0], 'position': list(v[1:4]), 'orientation': list(v[4:8]), 'scale_shear': list(v[8:17])})
            elif t == T_STRING:
                vals = [self.cstring(*tg) if (tg := self.deref(s, p + k * 8)) else None for k in range(cnt)]
            elif t == T_REF:
                vals = [self.read_struct(child, *tg) if (tg := self.deref(s, p + k * 8)) else None for k in range(cnt)]
            elif t == T_REFARRAY:
                vals = []
                for k in range(cnt):
                    num = self.u32(s, p + k * 12); tg = self.deref(s, p + k * 12 + 4); sz = self.struct_size(child)
                    vals.append([self.read_struct(child, tg[0], tg[1] + j * sz, True) for j in range(num)] if tg else [])
            elif t == T_ARRAYOFREFS:
                vals = []
                for k in range(cnt):
                    num = self.u32(s, p + k * 12); tg = self.deref(s, p + k * 12 + 4); lst = []
                    for j in range(num):
                        e = self.deref(tg[0], tg[1] + j * 8); lst.append(self.read_struct(child, *e) if e else None)
                    vals.append(lst)
            elif t == T_VARIANT:
                vals = []
                for k in range(cnt):
                    td = self.deref(s, p + k * 16); tg = self.deref(s, p + k * 16 + 8)
                    vals.append(self.read_struct(td, *tg) if td and tg else None)
            elif t == T_REFVARARRAY:
                vals = []
                for k in range(cnt):
                    td = self.deref(s, p + k * 20); num = self.u32(s, p + k * 20 + 8); tg = self.deref(s, p + k * 20 + 12)
                    vals.append([self.read_struct(td, tg[0], tg[1] + j * self.struct_size(td), True) for j in range(num)] if td and tg else [])
            elif t == T_EMPTYREF: vals = [None]
            else: raise ValueError(f'member type {t}')
            out[name] = vals if n else vals[0]
            p += self.member_size(t, child, n)
        return out

    def root(self): return self.read_struct(self.root_type, *self.root_node)

    # -- edits
    def set_floats(self, s, o, values):
        struct.pack_into(f'<{len(values)}f', self.sections[s]['data'], o, *values)

    def write(self):
        """the file with every section raw: magic + header + section headers + data + relocation/marshalling tables"""
        hdr_end = 32 + 72 + 44 * len(self.sections); assert hdr_end == self.headers_size
        pos = hdr_end; layout = []
        for h in self.sections:
            pos = (pos + 3) & ~3; layout.append([pos]); pos += len(h['data'])
        for h, lay in zip(self.sections, layout):
            lay.append(pos); pos += len(h['reloc']); lay.append(pos); pos += len(h['marsh'])
        out = bytearray(pos)
        out[:16] = MAGIC_LE64; struct.pack_into('<IIII', out, 16, self.headers_size, self.fmt, 0, 0)
        struct.pack_into('<10I', out, 32, 7, pos, 0, 72, len(self.sections), *self.root_type, *self.root_node, self.tag)
        struct.pack_into('<4I', out, 72, *self.extra); struct.pack_into('<4I', out, 88, *self.tail)
        for i, (h, (doff, roff, moff)) in enumerate(zip(self.sections, layout)):
            struct.pack_into('<11I', out, 104 + i * 44, 0, doff, len(h['data']), len(h['data']), h['align'], h['stop0'], h['stop1'],
                             roff, h['nreloc'], moff, h['nmarsh'])
            out[doff:doff + len(h['data'])] = h['data']; out[roff:roff + len(h['reloc'])] = h['reloc']; out[moff:moff + len(h['marsh'])] = h['marsh']
        struct.pack_into('<I', out, 40, zlib.crc32(bytes(out[HEADER_END:])))
        return bytes(out)

# ---------------------------------------------------------------- helpers for FH2 cars
def bones(g):
    """[(name, parent index, local position, (section, offset of the position floats))] of every skeleton in the file"""
    r = g.root(); out = []
    for sk in r.get('Skeletons') or []:
        for b in sk.get('Bones') or []:
            t = b['Transform']; s, o = b['_addr']['Transform']
            out.append((b['Name'], b['ParentIndex'], t['position'], (s, o + 4)))
    return out

def move_bone(g, name, d):
    """shift bone `name`'s local position by d (3 floats). Its world position and every descendant's move with it,
    so their InverseWorldTransform matrices (row-vector 4x4, translation in row 3) are updated too."""
    import numpy as np
    r = g.root(); moved = []
    for sk in r.get('Skeletons') or []:
        B = sk['Bones']; idx = [i for i, b in enumerate(B) if b['Name'] == name]
        if not idx: continue
        sub = set(idx)
        for i, b in enumerate(B):                       # descendants (bones are listed parents-first)
            if b['ParentIndex'] in sub: sub.add(i)
        for i in idx:
            b = B[i]; s, o = b['_addr']['Transform']; p = b['Transform']['position']
            new = [p[k] + d[k] for k in range(3)]; g.set_floats(s, o + 4, new); moved.append((b['Name'], p, new))
        for i in sub:
            b = B[i]; M = np.array(b['InverseWorldTransform'], dtype=np.float64).reshape(4, 4)
            M[3, :3] -= np.array(d) @ M[:3, :3]          # world' = world + d  ->  inv translation' = inv - d R
            s, o = b['_addr']['InverseWorldTransform']; g.set_floats(s, o, [float(x) for x in M.reshape(-1)])
    assert moved, f'no bone {name!r}; bones: {[b[0] for b in bones(g)]}'
    return moved

def floats_addr(g, st, member):
    """(section, offset) and count of a struct member's float data: inline Real32[n], or a reference-to-array"""
    t, name, child, n = next(m for m in g.struct_def(*st['_def']) if m[1] == member); s, o = st['_addr'][member]
    if t == T_REAL32: return (s, o), n
    if t == T_REFARRAY: return g.deref(s, o + 4), g.u32(s, o)
    raise ValueError(f'{member}: member type {t}')

def set_track_position(g, track_name, target, was):
    """FH2 driver animations keep the seat in the 'Hips' transform track's position curve, an absolute car-space
    position (confirmed 29 Oct). Sets it to `target`: a constant curve (D3Constant32f) is overwritten; a quantised
    keyframe curve (D3K8uC8u, D3I1K8uC8u: ControlScales ~1e-6, ControlOffsets = the seat) has its ControlOffsets
    shifted by target - was, where `was` is the set's seat (the constant from its idle.gr2). Returns what was done."""
    import struct as _st
    done = []
    for tg in g.root().get('TrackGroups') or []:
        for tt in tg.get('TransformTracks') or []:
            if tt['Name'] != track_name: continue
            pc = tt['PositionCurve']['CurveData']; hdr = next(k for k in pc if k.startswith('CurveDataHeader'))
            if 'Constant' in hdr:
                (s, o), n = floats_addr(g, pc, 'Controls'); assert n == 3; g.set_floats(s, o, list(target)); done.append('constant')
            elif 'ControlOffsets' in pc:
                (s, o), n = floats_addr(g, pc, 'ControlOffsets'); assert n == 3
                old = _st.unpack_from('<3f', g.sections[s]['data'], o)
                g.set_floats(s, o, [old[i] + target[i] - was[i] for i in range(3)]); done.append(hdr[16:] + ' offsets')
            else: raise ValueError(f'{track_name}: curve {hdr} not handled')
    return done

def track_position_constant(g, track_name):
    """the constant position of a transform track (None if it is keyframed)"""
    for tg in g.root().get('TrackGroups') or []:
        for tt in tg.get('TransformTracks') or []:
            if tt['Name'] == track_name:
                pc = tt['PositionCurve']['CurveData']; return list(pc['Controls']) if 'Controls' in pc else None

def describe(g):
    r = g.root()
    print(f'granny v{g.version}, {len(g.raw)} bytes, tag {g.tag:08x}, sections', [(h["comp"], h["size"]) for h in g.sections if h["size"]])
    for k, v in r.items():
        if k.startswith('_'): continue
        if isinstance(v, list): print(f'  {k}: {len(v)} items')
        elif isinstance(v, dict): print(f'  {k}: {{{", ".join(x for x in v if not x.startswith("_"))}}}')
        else: print(f'  {k}: {v!r}')
    for sk in r.get('Skeletons') or []:
        print(f'  skeleton {sk["Name"]!r}: {len(sk["Bones"])} bones')
        for b in sk['Bones']:
            t = b['Transform']; print(f'    {b["Name"]:34s} parent {b["ParentIndex"]:3d} pos {[round(x, 4) for x in t["position"]]} flags {t["flags"]}')
    for tg in r.get('TrackGroups') or []:
        print(f'  track group {tg["Name"]!r}: {len(tg.get("TransformTracks") or [])} transform tracks, '
              f'{len(tg.get("VectorTracks") or [])} vector tracks; initial placement pos {[round(x, 4) for x in tg["InitialPlacement"]["position"]]}')
        for tt in tg.get('TransformTracks') or []: print(f'    track {tt["Name"]!r}')

if __name__ == '__main__':
    cmd = sys.argv[1]; g = GR2(open(sys.argv[2], 'rb').read())
    if cmd == 'info': describe(g)
    elif cmd == 'decompress':
        open(sys.argv[3], 'wb').write(g.write()); print('wrote', sys.argv[3])
    elif cmd == 'movebone':
        for bn, old, new in move_bone(g, sys.argv[4], [float(x) for x in sys.argv[5:8]]): print(f'{bn}: {old} -> {new}')
        open(sys.argv[3], 'wb').write(g.write()); print('wrote', sys.argv[3])
