import numpy as np, trimesh, sys
W = np.load(sys.argv[1]); s = trimesh.Scene()
cols = dict(paint=[150, 165, 185, 255], trim=[30, 30, 30, 255], glass=[50, 60, 80, 255], head=[220, 220, 220, 255], lens=[200, 220, 255, 255], tail=[200, 0, 0, 255])
for k, c in cols.items():
    m = trimesh.Trimesh(W[k + '_P'] * [-1, 1, 1], W[k + '_I'].reshape(-1, 3), process=False); m.visual.face_colors = c; s.add_geometry(m, k)
s.export(sys.argv[2])
