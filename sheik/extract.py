"""Pull the community-made exterior of the 207 out of the BeamNG mod's p207.dae (personal use; BeamNG's own
'vivace_' parts and other mods' parts are left out). Output: per-part, per-material triangles in the file's
own space (Z up, front at -Y), with UVs."""
import collada, numpy as np, pickle, sys
EXTERIOR = ['bodyshell_very_high.163', 'bonnet_very_high', 'boot_very_high', 'bumper_f_very_high.009', 'bumper_r_very_high',
            'door_dside_f_very_high.001', 'door_dside_r_very_high.009', 'door_pside_f_very_high.025', 'door_pside_r_very_high.002',
            'windscreen_very_high', 'windscreen_r_very_high', 'window_lf_very_high', 'window_rf_very_high', 'window_lr_very_high',
            'window_rr_very_high', 'headlight_l_very_high.001', 'headlight_l_very_high.002', 'indicators_very_high.001',
            'indicators_very_high.002', 'mirror_l_very_high', 'mirror_r_very_high', 'misc_c_very_high.002', 'misc_c_very_high.009',
            'Mesh.011', 'Mesh.024', 'Chassis_very_high.148', 'Chassis_very_high.150', 'taillights_very_high']
d = collada.Collada(sys.argv[1], ignore=[collada.common.DaeUnsupportedError, collada.common.DaeBrokenRefError])
out = {}
for bg in d.scene.objects('geometry'):
    name = bg.original.name
    if name not in EXTERIOR: continue
    parts = []
    for prim in bg.primitives():
        if not isinstance(prim, (collada.triangleset.BoundTriangleSet, collada.polylist.BoundPolylist, collada.polygons.BoundPolygons)): continue
        tri = prim.triangleset() if not isinstance(prim, collada.triangleset.BoundTriangleSet) else prim
        V = tri.vertex[tri.vertex_index].reshape(-1, 3)
        N = tri.normal[tri.normal_index].reshape(-1, 3) if tri.normal is not None else None
        UV = tri.texcoordset[0][tri.texcoord_indexset[0]].reshape(-1, 2) if len(tri.texcoordset) else None
        mat = getattr(tri.material, 'name', None) or getattr(tri.material, 'id', None)
        parts.append(dict(mat=mat, V=V, N=N, UV=UV))
    out.setdefault(name, []).extend(parts)
print({k: sum(len(p['V']) // 3 for p in v) for k, v in out.items()})
print('missing', [e for e in EXTERIOR if e not in out])
pickle.dump(out, open('exterior.pkl', 'wb'))
