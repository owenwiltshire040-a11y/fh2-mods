"""Forza Horizon 2 .modelbin ('Grub' bundle) reader/writer.

Layout (from Doliman100's ForzaTech-extraction-tools, verified here by rebuilding files byte for byte):
  header   'burG' (u32 tag, little-endian), u8 major, u8 minor, u16 blob count, u32 data start, u32 file size
           (v1.1+: u32 blob count follows)
  blobs    per blob, 24 bytes: u32 tag, u8 major, u8 minor, u16 metadata count, u32 metadata offset,
           u32 data offset, u32 data size, u32 unknown
  metadata per entry, 8 bytes: u32 tag, u16 (size << 4 | version), u16 offset (relative to the entry)
  data     blob payloads, each starting on a 4-byte boundary
"""
import struct, sys

def tag_name(t):
    return struct.pack('>I', t).decode('latin1')


class Bundle:
    @classmethod
    def read(cls, b):
        self = cls()
        self.src = b
        tag, self.major, self.minor, count, self.data_start, self.file_size = struct.unpack_from('<IBBHII', b, 0)
        assert tag_name(tag) == 'Grub', tag_name(tag)
        p = 16
        if (self.major, self.minor) >= (1, 1):
            count = struct.unpack_from('<I', b, p)[0]; p += 4
        self.table_start = p
        self.blobs = []
        for i in range(count):
            t, vmaj, vmin, nmeta, moff, doff, dsize, unk = struct.unpack_from('<IBBHIIII', b, p)
            metas = []
            for j in range(nmeta):
                e = moff + j * 8
                mt, vs, mo = struct.unpack_from('<IHH', b, e)
                size, ver = vs >> 4, vs & 0xF
                metas.append({'tag': tag_name(mt), 'version': ver, 'data': b[e + mo:e + mo + size],
                              'rel': mo})
            self.blobs.append({'tag': tag_name(t), 'version': (vmaj, vmin), 'unk': unk, 'meta': metas,
                               'meta_off': moff, 'data_off': doff, 'data': bytearray(b[doff:doff + dsize])})
            p += 24
        return self

    def meta(self, blob, tag):
        for m in blob['meta']:
            if m['tag'] == tag:
                return m['data']
        return None

    def write(self):
        """Rebuild the file from the parsed blobs, recomputing every offset."""
        n = len(self.blobs)
        head = 16 + (4 if (self.major, self.minor) >= (1, 1) else 0)
        table = head + 24 * n
        # metadata entries, then their payloads, laid out as in the original files: all entries for a blob,
        # followed by that blob's metadata payloads, blob after blob
        out = bytearray(table)
        meta_offs = []
        for blob in self.blobs:
            meta_offs.append(len(out))
            entries_at = len(out)
            out += bytes(8 * len(blob['meta']))
            for j, m in enumerate(blob['meta']):
                e = entries_at + j * 8
                rel = len(out) - e
                struct.pack_into('<IHH', out, e, struct.unpack('>I', m['tag'].encode('latin1'))[0],
                                 (len(m['data']) << 4) | m['version'], rel)
                out += m['data']
        data_start = (len(out) + 3) & ~3
        out += bytes(data_start - len(out))
        data_offs = []
        for blob in self.blobs:
            pad = (-len(out)) % 4
            out += bytes(pad)
            data_offs.append(len(out))
            out += blob['data']
        out += bytes((-len(out)) % 4)
        struct.pack_into('<IBBHII', out, 0, struct.unpack('>I', b'Grub')[0], self.major, self.minor,
                         n if (self.major, self.minor) < (1, 1) else 0, data_start, len(out))
        if (self.major, self.minor) >= (1, 1):
            struct.pack_into('<I', out, 16, n)
        for i, blob in enumerate(self.blobs):
            struct.pack_into('<IBBHIIII', out, head + 24 * i, struct.unpack('>I', blob['tag'].encode('latin1'))[0],
                             blob['version'][0], blob['version'][1], len(blob['meta']),
                             meta_offs[i], data_offs[i], len(blob['data']), blob['unk'])
        return bytes(out)

    # ---- geometry ----
    def vertex_layouts(self):
        lays = []
        for blob in self.blobs:
            if blob['tag'] != 'VLay':
                continue
            d = blob['data']; p = 0
            n = struct.unpack_from('<H', d, p)[0]; p += 2
            names = []
            for _ in range(n):
                ln = struct.unpack_from('<I', d, p)[0]; p += 4
                names.append(d[p:p + ln].decode()); p += ln
            ne = struct.unpack_from('<H', d, p)[0]; p += 2
            els = []
            for _ in range(ne):
                ni, si, slot, _u, fmt = struct.unpack_from('<HHHHI', d, p); p += 12; p += 8
                els.append({'name': names[ni] + str(si), 'slot': slot, 'format': fmt})
            lays.append(els)
        return lays

    def vertex_buffers(self):
        bufs = {}
        for blob in self.blobs:
            if blob['tag'] != 'VerB':
                continue
            bid = struct.unpack('<i', self.meta(blob, 'Id  '))[0]
            length, size, stride, _a, _b, fmt = struct.unpack_from('<IIHBBI', blob['data'], 0)
            bufs[bid] = {'blob': blob, 'length': length, 'size': size, 'stride': stride, 'format': fmt}
        return bufs

    def meshes(self):
        out = []
        for blob in self.blobs:
            if blob['tag'] != 'Mesh':
                continue
            d = blob['data']; v = blob['version']; p = 0
            m = {'name': (self.meta(blob, 'Name') or b'').decode('utf-8', 'replace')}
            m['material_id'] = struct.unpack_from('<h', d, p)[0]; p += 2
            m['bone_index'], m['lods'] = struct.unpack_from('<hH', d, p); p += 4
            p += 2; m['render_pass'] = struct.unpack_from('<H', d, p)[0]; p += 2; p += 1
            if v >= (1, 2): p += 2
            if v >= (1, 3): p += 1
            p += 3
            m['index_buffer_id'] = struct.unpack_from('<i', d, p)[0]; p += 4; p += 4
            m['start_index'], m['base_vertex'], m['index_count'] = struct.unpack_from('<iiI', d, p); p += 12; p += 4
            if v >= (1, 6): p += 8
            m['layout_id'], nvb = struct.unpack_from('<II', d, p); p += 8
            m['vb'] = {}
            for _ in range(nvb):
                bid, slot, stride, off = struct.unpack_from('<iiii', d, p); p += 16
                m['vb'][slot] = {'id': bid, 'stride': stride, 'offset': off}
            out.append(m)
        return out

    FORMAT_SIZE = {6: 12, 10: 8, 13: 8, 24: 4, 28: 4, 35: 4, 37: 4}

    def position_streams(self):
        """{vertex buffer id: byte offset of POSITION0 inside each vertex} for float3 positions."""
        lays = self.vertex_layouts()
        res = {}
        for m in self.meshes():
            off = {}
            for el in lays[m['layout_id']]:
                o = off.get(el['slot'], 0)
                if el['name'] == 'POSITION0':
                    assert el['format'] == 6, f"positions are format {el['format']}, expected float3"
                    vb = m['vb'][el['slot']]
                    res[vb['id']] = o  # vb['offset'] is the start of this mesh's slice, not a per-vertex offset
                off[el['slot']] = o + self.FORMAT_SIZE[el['format']]
        return res

    def translate(self, dx, dy, dz):
        bufs = self.vertex_buffers()
        for bid, rel in self.position_streams().items():
            b = bufs[bid]; d = b['blob']['data']
            for i in range(b['length']):
                p = 16 + i * b['stride'] + rel
                x, y, z = struct.unpack_from('<fff', d, p)
                struct.pack_into('<fff', d, p, x + dx, y + dy, z + dz)


if __name__ == '__main__':
    src = open(sys.argv[1], 'rb').read()
    bnd = Bundle.read(src)
    print(f"Grub v{bnd.major}.{bnd.minor}, {len(bnd.blobs)} blobs, data from {bnd.data_start}")
    out = bnd.write()
    print('rebuilt identical:', out == src, len(out), len(src))
    if out != src:
        i = next(i for i, (a, b) in enumerate(zip(out, src)) if a != b)
        print('first difference at', hex(i))


def shift_bboxes(bundle, dx, dy, dz):
    for blob in bundle.blobs:
        for m in blob['meta']:
            if m['tag'] == 'BBox':
                v = list(struct.unpack('<6f', m['data']))
                v = [v[0] + dx, v[1] + dy, v[2] + dz, v[3] + dx, v[4] + dy, v[5] + dz]
                m['data'] = struct.pack('<6f', *v)
