"""Any built car zip -> textured .glb (body, glass, wheels, steering wheel at their carbin transforms).

python3 fh2re/carpreview.py car.zip out.glb [--paint RRGGBB]
Generalised from f1/preview_str1.py: textures are found by the swatchbin file name each material references, so it
works for any media name. 'carpaint' materials get the --paint colour (the game paints them at runtime); glass
materials ('gls'/'glass') are exported dark and translucent.
"""
import sys, os, zipfile, struct, re, argparse
import numpy as np, trimesh
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'tex'))
from geometry import Part
from body_swap import material_names
from gltf_bridge import decode_group
from carbin import read_carbin
import swatch


def skel_world(p):
    sk = [b for b in p.b.blobs if b['tag'] == 'Skel'][0]; d = bytes(sk['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2
    M, par = [], []
    for _ in range(n):
        L = struct.unpack_from('<I', d, o)[0]; o += 4; pa = struct.unpack_from('<h', d, o + L)[0]; o += L + 6
        M.append(np.frombuffer(d[o:o + 64], '<f4').reshape(4, 4).astype(float)); par.append(pa); o += 64
    W = []
    for i in range(n): W.append(M[i] @ W[par[i]] if par[i] >= 0 else M[i])
    return W


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('zip'); ap.add_argument('out'); ap.add_argument('--paint', default='b0b0b4')
    a = ap.parse_args()
    paint = [int(a.paint[i:i + 2], 16) for i in (0, 2, 4)] + [255]
    z = zipfile.ZipFile(a.zip); base = {n.lower().rsplit('/', 1)[-1]: n for n in z.namelist()}
    names = {n.lower(): n for n in z.namelist()}
    c = read_carbin(z.read([n for n in z.namelist() if n.endswith('.carbin')][0]))
    cache = {}

    def tex_of(mat_blob):
        s = bytes(mat_blob['data']).lower()
        for m in re.finditer(rb'game:\\media\\cars\\[ -~]+?\\([^\\]+?\.swatchbin)', s):
            fn = m.group(1).decode()
            if any(k in fn for k in ('_nrm', '_norm', '_glos', '_ao', '_lite', '_spec', '_mask')): continue
            if fn not in base: continue
            if fn not in cache:
                d = z.read(base[fn]); w, h = struct.unpack_from('<HH', d, 0x40)
                try: cache[fn] = Image.fromarray(swatch.decode_level(d, swatch.DATA, w, h, '2d')[..., :4])
                except Exception: cache[fn] = None
            if cache[fn] is not None: return cache[fn]
        return None

    s = trimesh.Scene(); n = 0
    for p_ in c['parts']:
        for m in p_['part']['models']:
            path = re.sub(r'^game:\\media\\cars\\[^\\]+\\', '', m['path'].lower()).replace('\\', '/')
            if path not in names: continue
            if any(k in path for k in ('interior', 'driver', 'collision', 'shadow', 'damage')) and 'steering' not in path: continue
            p = Part(z.read(names[path])); nm = material_names(p)
            mats = {struct.unpack('<i', p.b.meta(bl, 'Id  '))[0]: bl for bl in p.b.blobs if bl['tag'] == 'MatI'}
            try: W = skel_world(p)
            except Exception: W = None
            T = np.array(m['transform'], float).reshape(4, 4)
            lod_seen = None
            for r in p.render:
                if not struct.unpack_from('<H', r['blob']['data'], 4)[0] & 1 or len(set(r['indices'])) < 4: continue
                d, _ = decode_group(p, r['group'])
                P = d['POSITION'][:, :3].astype(float); b = struct.unpack_from('<h', r['blob']['data'], 2)[0]
                if W is not None and b > 1 and 'steering' in path: P = P @ W[b][:3, :3] + W[b][3, :3]
                P = P @ T[:3, :3] + T[3, :3]
                mm = trimesh.Trimesh(P * [-1, 1, 1], np.array(r['indices']).reshape(-1, 3)[:, ::-1], process=False)
                mname = (nm.get(id(r['blob'])) or '').lower()
                img = tex_of(mats[struct.unpack_from('<h', r['blob']['data'], 0)[0]])
                if 'carpaint' in mname:
                    mm.visual.face_colors = paint
                elif 'gls' in mname or 'glass' in mname or 'windsh' in mname:
                    mm.visual.face_colors = [25, 30, 35, 150]
                elif img is not None and 'TEXCOORD0' in d:
                    uv = d['TEXCOORD0'][:, :2].copy(); uv[:, 1] = 1 - uv[:, 1]
                    mm.visual = trimesh.visual.TextureVisuals(uv=uv, image=img)
                elif 'chrome' in mname or 'frame' in mname or 'alum' in mname or 'rim' in mname:
                    mm.visual.face_colors = [185, 188, 192, 255]
                elif 'tire' in mname or 'tyre' in mname or 'rubber' in mname:
                    mm.visual.face_colors = [28, 28, 30, 255]
                else:
                    mm.visual.face_colors = [22, 22, 24, 255] if 'black' in mname or 'blk' in mname else [70, 70, 76, 255]
                s.add_geometry(mm, node_name=f'{path}|{mname}|{n}'); n += 1
    s.export(a.out); print('exported', n, 'meshes')


if __name__ == '__main__':
    main()
