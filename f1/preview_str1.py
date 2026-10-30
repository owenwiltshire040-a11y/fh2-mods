"""textured preview of the built car zip: body + steering wheel (+ wheels/brakes at their carbin transforms)"""
import sys, zipfile, struct, numpy as np, trimesh, re
from PIL import Image
sys.path.insert(0, '../fh2re'); sys.path.insert(0, '../tex')
from geometry import Part
from body_swap import material_names
from gltf_bridge import decode_group
from carbin import read_carbin
from modelbin import Bundle
import swatch
MEDIA = 'STR_ToroRosso_1_06'
z = zipfile.ZipFile(sys.argv[1]); names = {n.lower(): n for n in z.namelist()}
c = read_carbin(z.read([n for n in z.namelist() if n.endswith('.carbin')][0]))
def skel_world(p):
    sk = [b for b in p.b.blobs if b['tag'] == 'Skel'][0]; d = bytes(sk['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2; M, par = [], []
    for _ in range(n):
        L = struct.unpack_from('<I', d, o)[0]; o += 4; pa = struct.unpack_from('<h', d, o + L)[0]; o += L + 6
        M.append(np.frombuffer(d[o:o + 64], '<f4').reshape(4, 4).astype(float)); par.append(pa); o += 64
    W = []
    for i in range(n): W.append(M[i] @ W[par[i]] if par[i] >= 0 else M[i])
    return W
texcache = {}
def tex_of(p, mat_blob):
    s = bytes(mat_blob['data']).lower()
    m = re.search(rb'game:\\media\\cars\\' + MEDIA.lower().encode() + rb'\\textures\\str1\\swatches\\([ -~]+?_diff|[ -~]+?)\.swatchbin', s)
    if not m: return None
    key = next((n for n in names if n.endswith(m.group(1).decode() + '.swatchbin')), None)
    if key is None: return None
    if key not in texcache:
        d = z.read(names[key]); w = struct.unpack_from('<H', d, 0x40)[0]
        texcache[key] = Image.fromarray(swatch.decode_level(d[0x53:], 0, w, w, '2d')[..., :3])
    return texcache[key]
s = trimesh.Scene()
for p_ in c['parts']:
    for m in p_['part']['models']:
        path = re.sub(r'^game:\\media\\cars\\[^\\]+\\', '', m['path'].lower()).replace('\\', '/')
        if path not in names: continue
        p = Part(z.read(names[path])); nm = material_names(p)
        mats = {struct.unpack('<i', p.b.meta(bl, 'Id  '))[0]: bl for bl in p.b.blobs if bl['tag'] == 'MatI'}
        try: W = skel_world(p)
        except Exception: W = None
        T = np.array(m['transform'], float).reshape(4, 4)
        for r in p.render:
            if not struct.unpack_from('<H', r['blob']['data'], 4)[0] & 1 or len(set(r['indices'])) < 4: continue
            d, _ = decode_group(p, r['group'])
            P = d['POSITION'][:, :3].astype(float); b = struct.unpack_from('<h', r['blob']['data'], 2)[0]
            if W is not None and b > 1 and 'steering' in path: P = P @ W[b][:3, :3] + W[b][3, :3]
            P = P @ T[:3, :3] + T[3, :3]
            mm = trimesh.Trimesh(P * [-1, 1, 1], np.array(r['indices']).reshape(-1, 3)[:, ::-1], process=False)
            img = tex_of(p, mats[struct.unpack_from('<h', r['blob']['data'], 0)[0]])
            if img is not None and 'TEXCOORD0' in d:
                uv = d['TEXCOORD0'].copy(); uv[:, 1] = 1 - uv[:, 1]
                mm.visual = trimesh.visual.TextureVisuals(uv=uv, image=img)
            else:
                mm.visual.face_colors = [60, 60, 66, 255] if 'black' not in nm[id(r['blob'])] else [20, 20, 22, 255]
            s.add_geometry(mm)
s.export(sys.argv[2]); print('exported', len(s.geometry), 'meshes')
