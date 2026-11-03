"""Restore reflective front trim and clear headlamp covers after source preparation.

Run after prepare_source.py and darken_arches.py. Does not alter lamp emitters.
"""
from pathlib import Path
import pickle, sys, zipfile, re
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

p = Path(__file__).resolve().parent
sys.path[:0] = [str(p.parents[1]/'fh2re'), str(p.parents[1]/'f1')]
from geometry import Part
from body_swap import material_names
import fhmat

g = pickle.loads((p/'geo.pkl').read_bytes())
keep = []
for f in g['parts']['c1_exttrim.skin_exttrim.exttrimyes']:
    if f['node'].startswith(('c1_headlight_L107_', 'c1_headlight_R107_')):
        g['parts'].setdefault('FRONT_REFLECTOR', []).append(dict(f, mat='FRONT_REFLECTOR'))
    elif f['node'].startswith('c1_hoodr107_'):
        # The badge contains two separate islands: raised lion and shield backing.
        m = trimesh.Trimesh(vertices=f['V'], faces=np.arange(len(f['V'])).reshape(-1,3), process=True)
        a = m.face_adjacency
        count, labels = connected_components(coo_matrix((np.ones(len(a)),a.T),shape=(len(m.faces),)*2),directed=False)
        assert count == 2
        # Recover the component labels for original triangle corners after welding.
        from scipy.spatial import cKDTree
        _, match = cKDTree(m.triangles_center).query(f['V'].reshape(-1,3,3).mean(1))
        for i in range(count):
            mask = labels[match] == i
            width = np.ptp(f['V'].reshape(-1,3,3)[mask,: ,0])
            mat = 'BADGE_LION' if width < .15 else 'BADGE_BACKING'
            frag = dict(f, mat=mat)
            for key, size in [('V',3),('N',3),('UV',2)]:
                frag[key] = f[key].reshape(-1,3,size)[mask].reshape(-1,size)
            g['parts'].setdefault(mat,[]).append(frag)
    else:
        keep.append(f)
g['parts']['c1_exttrim.skin_exttrim.exttrimyes'] = keep
# The badge's inner panel shares an alpha-textured material with the grille.
# RGB conversion loses its cutout and exposes a white rectangle behind the lion.
# Separate only that bonnet inset; the main bumper grille keeps its texture.
keep = []
for f in g['parts'].get('grille', []):
    if f['node'].startswith('c1_hoodr107_'):
        g['parts'].setdefault('BADGE_INSET', []).append(dict(f, mat='BADGE_INSET'))
    else:
        keep.append(f)
g['parts']['grille'] = keep
g['materials'] = sorted(g['parts'])
(p/'geo.pkl').write_bytes(pickle.dumps(g))

# Reuse the game's reflective chrome and transparent projector-glass shaders.
# Keep the original donor intact; this derived donor carries two extra materials.
with zipfile.ZipFile(p/'donor_PEU_107Urban_2006_.zip') as src:
    names = {n.lower():n for n in src.namelist()}
    lamp = Part(src.read(names['scene/exterior/primarylights/headlightl_a.modelbin']))
    def template(name):
        return next(bl['data'] for bl in lamp.b.blobs if bl['tag']=='MatI' and lamp.b.meta(bl,'Name').decode()==name)
    changes = {}
    for path, old, new, shader in [
        ('scene/exterior/platform/body_a.modelbin','frame','front_chrome','chrome'),
        ('scene/exterior/windows/glassf_a.modelbin','gls_windsheild','headlamp_clear','gls_projector'),
    ]:
        part = Part(src.read(names[path])); nm = material_names(part)
        data = template(shader)
        paths = [v.decode('latin1') for v in re.findall(rb'[Gg]ame:\\[ -~]+?\.swatchbin',data)]
        mid = fhmat.add_material(part,new,data,paths)
        for render in list(part.render):
            if nm[id(render['blob'])]==old:
                fhmat.add_mesh(part,render,mid)
        changes[names[path]] = part.build()
    with zipfile.ZipFile(p/'donor_front_PEU_107Urban_2006_.zip','w',zipfile.ZIP_DEFLATED) as out:
        for name in src.namelist():
            out.writestr(name,changes.get(name,src.read(name)))
print('Front trim separated; chrome and clear lens materials staged')
