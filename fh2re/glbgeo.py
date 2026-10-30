"""glTF/GLB model -> per-material triangle soups in FH2 car space (the glb counterpart of objgeo.py).

Sketchfab exports can put the body and the wheel nodes in different frames, so the body frame is given explicitly
(--frame: which model axes become FH2 x, y, z, with signs), the wheel centres are given in model units (--wheels,
measured from the body's arches) and the rim comes from the wheel nodes' own local coordinates (--rim-node, --rim-mats),
re-centred on the FH2 left-front wheel so fh2re/rimbuild.py can take it as it is.

usage: glbgeo.py model.glb out.pkl --frame "-x,z,y" --scale S --wheels ZF,ZR,YC,XHALF --tyre-radius R_model
                 --ground G_fh2 --axle-mid Z [--rim-node PREFIX --rim-mats a,b] [--skip-mats a,b]
"""
import sys, pickle, argparse
import numpy as np, trimesh

def parse_frame(spec):
    """'-x,z,y' -> (permutation, signs): FH2 axis i = sign * model axis"""
    perm, sign = [], []
    for tok in spec.split(','):
        tok = tok.strip(); s = -1.0 if tok.startswith('-') else 1.0; ax = 'xyz'.index(tok.lstrip('+-')); perm.append(ax); sign.append(s)
    return perm, np.array(sign)

def load(fn, frame, scale, skip_mats, rim_node=None, rim_mats=(), skip_nodes=(), tag_nodes=()):
    sc = trimesh.load(fn, force='scene'); g = sc.graph; perm, sign = parse_frame(frame)
    mirror = np.prod(sign) * np.linalg.det(np.eye(3)[perm]) < 0            # does the axis map flip handedness?
    body, rim = {}, {}
    for node in g.nodes_geometry:
        T, geom = g[node]; m = sc.geometry[geom]; mat = getattr(getattr(m.visual, 'material', None), 'name', None)
        F = m.faces
        for pre, tag in tag_nodes:                   # e.g. hub_=RIM_: wheels baked into the body keep a material of their own
            if node.startswith(pre): mat = f'{tag}{mat}'
        if rim_node and node.startswith(rim_node) and mat in rim_mats:
            V = m.vertices * scale; N = m.vertex_normals                     # local: x depth (face at min x), y/z wheel plane
            rim.setdefault(mat, []).append(dict(node=node, mat=mat, V=V[F].reshape(-1, 3), N=N[F].reshape(-1, 3), UV=np.zeros((len(F) * 3, 2))))
            continue
        if mat in skip_mats or (rim_node and node.startswith(rim_node)) or any(node.startswith(p) for p in skip_nodes): continue
        V = trimesh.transform_points(m.vertices, T); R = T[:3, :3]; N = m.vertex_normals @ R.T
        N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
        V = V[:, perm] * sign * scale; N = N[:, perm] * sign
        uv = getattr(m.visual, 'uv', None); UV = uv[F].reshape(-1, 2) if uv is not None else np.zeros((len(F) * 3, 2))
        Vf, Nf = V[F].reshape(-1, 3), N[F].reshape(-1, 3)
        if mirror: Vf = Vf.reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3); Nf = Nf.reshape(-1, 3, 3)[:, ::-1].reshape(-1, 3); UV = UV.reshape(-1, 3, 2)[:, ::-1].reshape(-1, 2)
        body.setdefault(mat, []).append(dict(node=node, mat=mat, V=Vf, N=Nf, UV=UV))
    return body, rim

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('glb'); ap.add_argument('out')
    ap.add_argument('--frame', required=True); ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--wheels', required=True, help='model units, body frame: front z, rear z, centre height, half track (after --frame, before scale)')
    ap.add_argument('--tyre-radius', type=float, required=True, help='model units')
    ap.add_argument('--ground', type=float, required=True, help='FH2 y of the tyre contact patch'); ap.add_argument('--axle-mid', type=float, default=0.0)
    ap.add_argument('--rim-node', default=None); ap.add_argument('--rim-mats', default=''); ap.add_argument('--skip-mats', default='')
    ap.add_argument('--skip-nodes', default='', help='node name prefixes to leave out of the body (e.g. the other wheels)')
    ap.add_argument('--tag-nodes', default='', help='prefix=TAG,...: materials of nodes starting with prefix become TAG+material (wheels baked into the body: hub_=RIM_)')
    A = ap.parse_args()
    body, rim = load(A.glb, A.frame, A.scale, set(A.skip_mats.split(',')) - {''}, A.rim_node, set(A.rim_mats.split(',')) - {''}, [p for p in A.skip_nodes.split(',') if p],
                      [tuple(t.split('=', 1)) for t in A.tag_nodes.split(',') if '=' in t])
    zf, zr, yc, xh = [float(x) for x in A.wheels.split(',')]; s = A.scale; r = A.tyre_radius * s
    W = {'HUB_LF': np.array([-xh, yc, zf]) * s, 'HUB_RF': np.array([xh, yc, zf]) * s, 'HUB_LR': np.array([-xh, yc, zr]) * s, 'HUB_RR': np.array([xh, yc, zr]) * s}
    off = np.array([0.0, A.ground - (yc * s - r), A.axle_mid - (zf + zr) / 2 * s])
    for lst in body.values():
        for p in lst: p['V'] = p['V'] + off
    wheels = {k: dict(centre=c + off, radius=r) for k, c in W.items()}
    parts = dict(body)
    for mat, lst in rim.items():           # the rim, re-centred on the FH2 left-front wheel (outward = -x, as in the wheel part)
        parts[mat] = [dict(p, V=p['V'] + wheels['HUB_LF']['centre']) for p in lst]
    V = np.concatenate([p['V'] for l in body.values() for p in l])
    print(f'body x {V[:,0].min():.2f}..{V[:,0].max():.2f} y {V[:,1].min():.2f}..{V[:,1].max():.2f} z {V[:,2].min():.2f}..{V[:,2].max():.2f}; '
          f'wheelbase {(zf - zr) * s:.3f} track {2 * xh * s:.3f} tyre radius {r:.3f}; rim materials {list(rim)}')
    for k, w in wheels.items(): print(k, 'FH2 centre', w['centre'].round(3))
    pickle.dump(dict(parts=parts, wheels=wheels, ground=A.ground, wheelbase=float((zf - zr) * s), materials=sorted(parts)), open(A.out, 'wb'))
    print('wrote', A.out)
