"""Lossless reader/writer for Forza Horizon 2 .carbin files (CarScene v5, CarRenderModel11 v15/16).

Structure follows Doliman100's ForzaTech-extraction-tools (carbin_importer.py), but every byte the importer
skips is kept here as a named raw field, so a parsed file can be written back byte for byte.
"""
import struct, io, json, sys
from dataclasses import dataclass, field, asdict


class R:
    def __init__(self, b): self.b, self.p = b, 0
    def take(self, n):
        if self.p + n > len(self.b): raise EOFError(f"read {n} at {self.p:#x} past end {len(self.b):#x}")
        v = self.b[self.p:self.p + n]; self.p += n; return v
    def u8(self): return self.take(1)[0]
    def u16(self): return struct.unpack('<H', self.take(2))[0]
    def s32(self): return struct.unpack('<i', self.take(4))[0]
    def u32(self): return struct.unpack('<I', self.take(4))[0]
    def f32(self): return struct.unpack('<f', self.take(4))[0]
    def s(self): return self.take(self.u32()).decode('utf-8')
    def raw(self, n): return self.take(n).hex()


class W:
    def __init__(self): self.o = io.BytesIO()
    def u8(self, v): self.o.write(bytes([v]))
    def u16(self, v): self.o.write(struct.pack('<H', v))
    def s32(self, v): self.o.write(struct.pack('<i', v))
    def u32(self, v): self.o.write(struct.pack('<I', v))
    def f32(self, v): self.o.write(struct.pack('<f', v))
    def s(self, v): b = v.encode('utf-8'); self.u32(len(b)); self.o.write(b)
    def raw(self, h): self.o.write(bytes.fromhex(h))
    def bytes(self): return self.o.getvalue()


SERIES = 2  # Forza Horizon


def rd_ao(r):
    a = {"version": r.u16(), "path": r.s(), "u8x2": r.raw(8)}
    a["mid"] = r.raw(16 if a["version"] >= 2 else 3)
    a["u1"] = r.raw(1)
    if a["version"] >= 3: a["u2"] = r.raw(2)
    return a

def wr_ao(w, a):
    w.u16(a["version"]); w.s(a["path"]); w.raw(a["u8x2"]); w.raw(a["mid"]); w.raw(a["u1"])
    if a["version"] >= 3: w.raw(a["u2"])


def rd_model(r):
    m = {"version": r.u16()}
    v = m["version"]
    m["path"] = r.s()
    m["transform"] = [r.f32() for _ in range(16)]
    m["lods"] = r.u16() if v > 5 else r.u32()
    m["bone_name"] = r.s()
    m["bone_index"] = r.u16()
    m["u_after_bone"] = r.raw(1)
    m["draw_groups"] = r.s32()
    if v < 9: m["old_string"] = r.s()
    if v >= 2: m["material_overrides"] = [{"name": r.s(), "bundle": r.raw(r.u32())} for _ in range(r.u32())]
    if v >= 3:
        n = 8 if v >= 20 else 4
        m["material_indices"] = [{"name": r.s(), "data": r.raw(n)} for _ in range(r.u32())]
    if v >= 6:
        f = r.u8(); m["flag6"] = f
        if f: m["flag6_data"] = r.raw(8)
    if v >= 8: m["u8"] = r.raw(4)
    if v >= 9: m["ao_maps"] = [rd_ao(r) for _ in range(r.u32())]
    if v >= 10: m["u10"] = r.raw(1)
    if v >= 11: m["u11"] = r.raw(18)
    if v >= 12: m["type"] = r.s()
    if v >= 13: m["guid"] = r.raw(16)
    if v >= 14: m["u14"] = r.raw(20)
    if v >= 15: m["u15"] = r.raw(4)
    if v >= 16: m["refs16"] = [r.raw(16) for _ in range(r.u32())]
    if v >= 17: m["u17"] = r.raw(1)
    if v >= 18: m["u18"] = r.raw(4)
    if v >= 19: m["u19"] = r.raw(4); m["s19"] = r.s()
    return m

def wr_model(w, m):
    v = m["version"]; w.u16(v); w.s(m["path"])
    for x in m["transform"]: w.f32(x)
    (w.u16 if v > 5 else w.u32)(m["lods"])
    w.s(m["bone_name"]); w.u16(m["bone_index"]); w.raw(m["u_after_bone"]); w.s32(m["draw_groups"])
    if v < 9: w.s(m["old_string"])
    if v >= 2:
        w.u32(len(m["material_overrides"]))
        for o in m["material_overrides"]: w.s(o["name"]); w.u32(len(o["bundle"]) // 2); w.raw(o["bundle"])
    if v >= 3:
        w.u32(len(m["material_indices"]))
        for o in m["material_indices"]: w.s(o["name"]); w.raw(o["data"])
    if v >= 6:
        w.u8(m["flag6"])
        if m["flag6"]: w.raw(m["flag6_data"])
    if v >= 8: w.raw(m["u8"])
    if v >= 9:
        w.u32(len(m["ao_maps"]))
        for a in m["ao_maps"]: wr_ao(w, a)
    if v >= 10: w.raw(m["u10"])
    if v >= 11: w.raw(m["u11"])
    if v >= 12: w.s(m["type"])
    if v >= 13: w.raw(m["guid"])
    if v >= 14: w.raw(m["u14"])
    if v >= 15: w.raw(m["u15"])
    if v >= 16:
        w.u32(len(m["refs16"]))
        for g in m["refs16"]: w.raw(g)
    if v >= 17: w.raw(m["u17"])
    if v >= 18: w.raw(m["u18"])
    if v >= 19: w.raw(m["u19"]); w.s(m["s19"])


def rd_part(r):
    p = {"version": r.u16(), "type": r.u32()}
    p["models"] = [rd_model(r) for _ in range(r.u32())]
    if p["version"] >= 2: p["tail"] = r.raw(32)
    return p

def wr_part(w, p):
    w.u16(p["version"]); w.u32(p["type"]); w.u32(len(p["models"]))
    for m in p["models"]: wr_model(w, m)
    if p["version"] >= 2: w.raw(p["tail"])


def rd_upgrade(r):
    u = {"version": r.u16(), "level": r.u8(), "is_stock": r.u8(), "id": r.s32(), "car_body_id": r.s32(),
         "parent_is_stock": r.u8()}
    if u["version"] >= 2: u["tail"] = r.raw(32)
    return u

def wr_upgrade(w, u):
    w.u16(u["version"]); w.u8(u["level"]); w.u8(u["is_stock"]); w.s32(u["id"]); w.s32(u["car_body_id"])
    w.u8(u["parent_is_stock"])
    if u["version"] >= 2: w.raw(u["tail"])


def rd_upart(r):
    p = {"version": r.u16(), "type": r.u32()}
    p["upgrades"] = [rd_upgrade(r) for _ in range(r.u32())]
    if p["version"] >= 3:
        p["shared_models"] = []
        for _ in range(r.u32()):
            ids = [r.u32() for _ in range(r.u32())]
            p["shared_models"].append({"upgrade_ids": ids, "model": rd_model(r)})
    return p

def wr_upart(w, p):
    w.u16(p["version"]); w.u32(p["type"]); w.u32(len(p["upgrades"]))
    for u in p["upgrades"]: wr_upgrade(w, u)
    if p["version"] >= 3:
        w.u32(len(p["shared_models"]))
        for s in p["shared_models"]:
            w.u32(len(s["upgrade_ids"]))
            for i in s["upgrade_ids"]: w.u32(i)
            wr_model(w, s["model"])


def read_carbin(b):
    r = R(b)
    c = {"version": r.u16()}
    v = c["version"]
    if v >= 3: c["guid"] = r.raw(16)
    if v >= 5: c["u5"] = r.raw(1)
    c["ordinal"] = r.u32(); c["media_name"] = r.s(); c["skeleton_path"] = r.s()
    if v >= 2: c["u2"] = r.raw(2)
    c["parts"] = []
    for _ in range(r.u32()):
        t = r.u8() if v >= 4 else None
        c["parts"].append({"slot_type": t, "part": rd_part(r)})
    c["upgradable_parts"] = [rd_upart(r) for _ in range(r.u32())]
    c["trailing"] = b[r.p:].hex()
    return c

def write_carbin(c):
    w = W(); v = c["version"]; w.u16(v)
    if v >= 3: w.raw(c["guid"])
    if v >= 5: w.raw(c["u5"])
    w.u32(c["ordinal"]); w.s(c["media_name"]); w.s(c["skeleton_path"])
    if v >= 2: w.raw(c["u2"])
    w.u32(len(c["parts"]))
    for p in c["parts"]:
        if v >= 4: w.u8(p["slot_type"])
        wr_part(w, p["part"])
    w.u32(len(c["upgradable_parts"]))
    for p in c["upgradable_parts"]: wr_upart(w, p)
    w.raw(c["trailing"])
    return w.bytes()


if __name__ == "__main__":
    src = open(sys.argv[1], "rb").read()
    c = read_carbin(src)
    out = write_carbin(c)
    print("trailing bytes after parse:", len(c["trailing"]) // 2)
    print("round trip identical:", out == src, f"({len(out)} vs {len(src)} bytes)")
    if len(sys.argv) > 2: json.dump(c, open(sys.argv[2], "w"), indent=1)
