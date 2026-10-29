import sys, zipfile, struct, numpy as np, trimesh
sys.path.insert(0, 'fh2re')
from geometry import Part
from body_swap import material_names
from carbin import read_carbin
z = zipfile.ZipFile(sys.argv[1]); names = {n.lower(): n for n in z.namelist()}
c = read_carbin(z.read([n for n in z.namelist() if n.endswith('.carbin')][0]))
ROOT = 'game:\\media\\cars\\peu_207sehdi_08\\'
def skel(p):
    sk = [b for b in p.b.blobs if b['tag'] == 'Skel'][0]; d = bytes(sk['data']); n = struct.unpack_from('<H', d, 0)[0]; o = 2; M = []
    for _ in range(n):
        L = struct.unpack_from('<I', d, o)[0]; o += 4 + L + 6; M.append(np.frombuffer(d[o:o + 64], '<f4').reshape(4, 4)); o += 64
    return M
s = trimesh.Scene()
COL = {'carpaint': [70, 80, 90, 255], 'fabric': [120, 120, 125, 255], 'chrome': [210, 210, 215, 255], 'gls': [60, 70, 90, 120], 'leather': [55, 55, 60, 255]}
for p_ in c['parts']:
    for m in p_['part']['models']:
        path = m['path'].lower().replace(ROOT, '').replace('\\', '/')
        if path not in names: continue
        interior = path.startswith('scene/interior')
        if not interior and 'body_a' not in path: continue
        p = Part(z.read(names[path])); nm = material_names(p)
        try: M = skel(p)
        except Exception: M = None
        for r in p.render:
            if not struct.unpack_from('<H', r['blob']['data'], 4)[0] & 1 or len(r['indices']) < 6: continue
            mat = nm[id(r['blob'])]
            if 'body_a' in path and 'carpaint' not in mat: continue
            P = np.array(p.groups[r['group']]['positions']); b = struct.unpack_from('<h', r['blob']['data'], 2)[0]
            if M is not None and b > 1: P = P @ M[b][:3, :3] + M[b][3, :3]
            col = next((v for k, v in COL.items() if k in mat.lower()), [40, 40, 44, 255])
            if 'body_a' in path: col = [150, 160, 175, 255]
            mm = trimesh.Trimesh(P * [-1, 1, 1], np.array(r['indices']).reshape(-1, 3), process=False); mm.visual.face_colors = col
            s.add_geometry(mm)
s.export(sys.argv[2])
