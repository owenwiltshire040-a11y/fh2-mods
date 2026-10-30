"""Track width from the model's wheel arches (spec PHYSICS body track_front / track_rear = 'auto').

Rule found on the 208 and V70 in game (NOTES: track rule of thumb): the game draws the wheel ~5 cm per side inboard
of ModelTrackOuter/1.012/2, so the track is set to put the database tyre's outer face `LIP_GAP` beyond the body's arch
lip:  track = 2 * (lip + LIP_GAP - tyre_width / 2).  The lip is the widest body point within 15 cm (fore/aft) of the
axle and up to 50 cm above the wheel centre. Reproduces the hand-measured 208 lips (0.838 / 0.851).
"""
import pickle
import numpy as np

LIP_GAP = 0.04


def lips(S):
    G = pickle.load(open(S.GEO, 'rb')); parts, W = G['parts'], G['wheels']
    body = [m for m, pl in S.MATERIALS.items() if pl and pl[1] in S.BODY_PLAIN and S.BODY_PLAIN[pl[1]][1] == 'carpaint' and m in parts]
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
            B[key] = round(2 * (L[ax] + gap - T[wkey] / 2000), 3)
            print(f'auto track {ax}: arch lip {L[ax]:.3f}, tyre {T[wkey]} mm -> {B[key]}')
