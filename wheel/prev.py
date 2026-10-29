import sys, struct, numpy as np, trimesh
sys.path.insert(0, '../fh2re')
from geometry import Part
from body_swap import material_names
p = Part(open(sys.argv[1], 'rb').read()); names = material_names(p)
col = dict(rim=[200, 200, 205, 255], inner_rim=[120, 120, 125, 255], outer_rim=[215, 215, 220, 255], lug=[230, 230, 230, 255],
           valve_cap=[30, 30, 30, 255], black=[20, 20, 20, 255], wheel_badge=[160, 160, 170, 255], hub=[90, 60, 40, 255])
s = trimesh.Scene()
for r in p.render:
    m = names[id(r['blob'])]
    if m not in col or struct.unpack_from('<H', r['blob']['data'], 4)[0] != 0b11: continue
    P = np.array(p.groups[r['group']]['positions']); T = np.array(r['indices']).reshape(-1, 3)
    P = P.copy(); P[:, 0] = np.minimum(P[:, 0], 0.08)      # fold the barrel back so it doesn't fill the view
    mm = trimesh.Trimesh(P * [-1, 1, 1], T, process=False); mm.visual.face_colors = col[m]; s.add_geometry(mm, m + str(len(s.geometry)))
s.export(sys.argv[2])
