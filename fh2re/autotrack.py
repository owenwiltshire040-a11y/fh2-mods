"""Track width from the model's wheel arches (spec PHYSICS body track_front / track_rear = 'auto').

Rule found on the 208 and V70 in game (NOTES: track rule of thumb): the game draws the wheel ~5 cm per side inboard
of ModelTrackOuter/1.012/2, so the track is set to put the database tyre's outer face `LIP_GAP` beyond the body's arch
lip:  track = 2 * (lip + LIP_GAP - tyre_width / 2).  The lip is the widest body point within 15 cm (fore/aft) of the
axle and up to 50 cm above the wheel centre. Reproduces the hand-measured 208 lips (0.838 / 0.851).
"""
import pickle
from pathlib import Path
import numpy as np

LIP_GAP = 0.04


def lips(S):
    G = pickle.loads(Path(S.GEO).read_bytes()); parts, W = G['parts'], G['wheels']
    if getattr(S, 'WHEEL_FIT', {}).get('geometry') == 'open_wheel':
        # An exposed wheel has no arch lip. Measure its actual outer rim face.
        out = {}
        for ax in ('F', 'R'):
            mats = S.OPEN_WHEEL_RIM_MATERIALS[ax]
            V = np.concatenate([p['V'] for m in mats for p in parts[m] if len(p['V'])])
            c = W['HUB_L' + ax]['centre']
            V = V[(np.abs(V[:,2]-c[2])<.4)&(np.abs(V[:,1]-c[1])<.4)]
            if not len(V) or not (np.any(V[:,0]<0) and np.any(V[:,0]>0)):
                raise ValueError('Open-wheel fit requires both source rims at each axle')
            out[ax] = float((-V[:,0].min()+V[:,0].max())/2)
        return out
    body = getattr(S, 'ARCH_MATERIALS', None) or [m for m, pl in S.MATERIALS.items() if pl and pl[1] in S.BODY_PLAIN and S.BODY_PLAIN[pl[1]][1] == 'carpaint' and m in parts]
    body = [m for m in body if m in parts]
    if not body:
        raise ValueError('No body materials available for arch measurement; specify ARCH_MATERIALS.')
    V = np.concatenate([p['V'] for m in body for p in parts[m]])
    out = {}
    for ax in ('F', 'R'):
        c = W['HUB_L' + ax]['centre']
        k = (np.abs(V[:, 2] - c[2]) < 0.15) & (V[:, 1] > c[1]) & (V[:, 1] < c[1] + 0.5)
        out[ax] = float(np.abs(V[k, 0]).max())
    return out


def apply(S):
    B = S.PHYSICS['body']; T = S.PHYSICS.get('tyres', {})
    if B.get('track_front') != 'auto' and B.get('track_rear') != 'auto': return
    L = lips(S); gap = getattr(S, 'LIP_GAP', LIP_GAP)
    for ax, key, wkey in (('F', 'track_front', 'width_front'), ('R', 'track_rear', 'width_rear')):
        if B.get(key) == 'auto':
            # Custom normalised rims use X=0 at their outer face, not their hub centre.
            if getattr(S, 'TRACK_REFERENCE', None) == 'rim_face':
                B[key] = round(2 * (L[ax] + getattr(S, 'RIM_FACE_GAP', .01)), 3)
            else:
                B[key] = round(2 * (L[ax] + gap - T[wkey] / 2000), 3)
            print(f'auto track {ax}: arch lip {L[ax]:.3f}, tyre {T[wkey]} mm -> {B[key]}')
