"""Estimate a car's FH2 stats from its real specs, the way the stock cars are rated.

    from estimates import estimates, torque_curve
    estimates(dict(mass=1230, hp=134, cd=0.32, tyre_fw=195, tyre_rw=195, t60=None, top_mph=None), frontal_area_m2)

Fits (least squares over every stock car in vanilla.slt, 30 Oct): PerformanceIndex and the five Autoshow ratings
from [1, ln(hp/kg), ln(top mph), ln(0-60 s), (front+rear tyre mm)/kg]; rms error PI 0.058, ratings 0.27-0.72.
Class from PI with the game's CarClasses limits. 0-60 / top speed are estimated when not given.
"""
import numpy as np

CLASS_PI = [(0, 0.4345), (1, 0.525628), (2, 0.6179), (3, 0.748432), (4, 0.846368), (5, 0.997086), (6, 9.0)]
CLASS_NAMES = ['D', 'C', 'B', 'A', 'S1', 'S2', 'X']
# least-squares fits over every stock car: [1, ln(hp/kg), ln(top mph), ln(0-60 s), (front+rear tyre mm)/kg]
FITS = {'pi': [1.0387, 0.1761, 0.0442, -0.2309, -0.0725], 'speed': [-14.984, 0.5069, 4.2821, 0.0272, -0.041],
        'handling': [10.5776, 0.3878, -0.3372, -1.4139, 1.4142], 'accel': [11.6317, 1.6582, 0.0086, -0.9898, -0.5416],
        'braking': [13.5845, 0.4864, -0.5456, -1.8521, 1.7228], 'launch': [20.0577, 0.2493, -1.268, -3.1845, -0.956]}


def safe(s): return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_') or 'x'


def torque_curve(hp, nm, rpm_t, rpm_p, redline, aspiration):
    """a plausible curve through the quoted figures: peak torque at rpm_t (held to ~0.75 rpm_p on turbo engines),
    peak power at rpm_p, tailing off to the limiter"""
    Tp = hp * 7120.9 / rpm_p                       # torque at the power peak (Nm)
    T = max(nm, Tp)
    hold = max(rpm_t, 0.75 * rpm_p) if aspiration in ('turbo', 'twin') else rpm_t
    pts = {0: 0.45 * T, int(rpm_t * 0.5): 0.78 * T, int(rpm_t): T}
    if hold > rpm_t + 200: pts[int(hold)] = T * 0.99
    pts[int(rpm_p)] = min(Tp, T); pts[int(redline)] = min(Tp, T) * 0.88
    return sorted(pts.items())


def estimates(c, A):
    """0-60, 0-100, top speed, PI, ratings, class from the specs (fits over the stock cars)"""
    kg, hp = c['mass'], c['hp']
    t60 = c.get('t60') or round(1.18 * (kg / hp) ** 0.95, 1)
    t100 = round(t60 * (2.4 + 0.07 * kg / hp), 1)
    top = c.get('top_mph') or round(19.8 * (hp / (c['cd'] * A)) ** (1 / 3))
    x = np.array([1, np.log(hp / kg), np.log(top), np.log(t60), (c['tyre_fw'] + c['tyre_rw']) / kg])
    f = {k: float(np.dot(v, x)) for k, v in FITS.items()}
    pi = float(np.clip(f['pi'], 0.05, 0.99))
    cls = next(i for i, lim in CLASS_PI if pi <= lim)
    ratings = tuple(round(float(np.clip(f[k], 1.0, 10.0)), 1) for k in ('speed', 'handling', 'accel', 'braking', 'launch'))
    return dict(t60=t60, t100=t100, top_mph=top, pi=round(pi, 3), cls=cls, cls_name=CLASS_NAMES[cls], ratings=ratings)


