"""207 (pre-facelift, UK diesel) instrument faces drawn onto the Fiesta's gauge texture layout.
The game turns the needles by the Fiesta's calibration (measured from its faces: tacho -115 deg + 29.2 deg per
1000 rpm about (256, 260); speedo -116.6 deg + 1.435 deg per mph about (777, 261); angles clockwise from up),
so the 207 scales are drawn at those angles: they read true wherever the needle points."""
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont
S = 2                                   # draw at 2x, downsample
W, H = 1024 * S, 512 * S
F = '/usr/share/fonts/truetype/dejavu/'
font = lambda size, bold=True: ImageFont.truetype(F + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), size * S)
CREAM, DARK, RED_BROWN, INK, RED = (236, 230, 210), (28, 28, 30), (120, 28, 20), (25, 22, 22), (190, 30, 25)
TACHO, SPEEDO = (256, 260), (777, 261)
t_ang = lambda k: -115 + 29.2 * k
s_ang = lambda mph: -116.6 + 1.435 * mph

def pol(c, r, a):
    a = math.radians(a); return (c[0] * S + math.sin(a) * r * S, c[1] * S - math.cos(a) * r * S)

def face(d, lite, c, r_face):
    if lite: return
    d.ellipse([c[0] * S - r_face * S, c[1] * S - r_face * S, c[0] * S + r_face * S, c[1] * S + r_face * S], fill=CREAM)
    # the 207's dark lower sector under the scale
    d.chord([c[0] * S - r_face * S, c[1] * S - r_face * S, c[0] * S + r_face * S, c[1] * S + r_face * S], 45, 135, fill=DARK)

def tick(d, c, a, r0, r1, w, col):
    d.line([pol(c, r0, a), pol(c, r1, a)], fill=col, width=int(w * S))

def label(d, c, a, r, text, f, col):
    x, y = pol(c, r, a); d.text((x, y), text, font=f, fill=col, anchor='mm')

def draw(lite):
    img = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    ink = (255, 236, 200) if lite else INK; num = (255, 120, 80) if lite else RED_BROWN
    # ---- rev counter: 0-6 x1000, red from 5 (1.6 HDi 90)
    face(d, lite, TACHO, 222)
    if not lite:
        d.arc([TACHO[0] * S - 196 * S, TACHO[1] * S - 196 * S, TACHO[0] * S + 196 * S, TACHO[1] * S + 196 * S],
              t_ang(5) - 90, t_ang(6) - 90, fill=RED, width=16 * S)
    for k in np.arange(0, 6.01, 0.5):
        major = abs(k - round(k)) < 1e-6
        tick(d, TACHO, t_ang(k), 178 if major else 188, 204, 5 if major else 3, ink)
        if major: label(d, TACHO, t_ang(k), 148, str(int(k)), font(40), num)
    for k in np.arange(0, 6.01, 0.1):
        tick(d, TACHO, t_ang(k), 198, 204, 1.5, ink)
    label(d, TACHO, 0, 70, 'x1000', font(16, False), ink); label(d, TACHO, 0, 48, 'r/min', font(16, False), ink)
    # ---- speedometer: mph 0-140 outside, km/h inside (UK car)
    face(d, lite, SPEEDO, 222)
    for v in range(0, 141, 5):
        major = v % 10 == 0
        tick(d, SPEEDO, s_ang(v), 180 if major else 190, 204, 5 if major else 3, ink)
        if v % 20 == 0 and v: label(d, SPEEDO, s_ang(v), 150, str(v), font(34), num)
    label(d, SPEEDO, s_ang(0), 155, '0', font(34), num)
    for kmh in range(20, 221, 20):
        a = s_ang(kmh / 1.609344)
        tick(d, SPEEDO, a, 112, 124, 2.5, num)
        if kmh % 40 == 0: label(d, SPEEDO, a, 96, str(kmh), font(17), num)
    label(d, SPEEDO, 0, 60, 'mph', font(20), ink); label(d, SPEEDO, 0, 36, 'km/h', font(15, False), num)
    return img

def fuel_from_fiesta(base, lite):
    """the small fuel dial: the Fiesta's own markings (it sets the needle's travel), recoloured to the 207's style"""
    a = np.array(base)[..., :3].astype(float); y, x = np.mgrid[0:512, 0:1024]
    reg = ((x - 525) ** 2 + (y - 470) ** 2 < 95 ** 2) & (y > 380)
    mark = a.max(2) / 255.0
    out = np.zeros((512, 1024, 3))
    if lite: out[reg] = (mark[reg][:, None] * np.array([255, 236, 200]))
    else:    out[reg] = (1 - mark[reg][:, None]) * np.array(CREAM) + mark[reg][:, None] * np.array(INK)
    return out, reg

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../../tex'); import swatch
    for kind, path in (('DIFF', '../../tex/PEU_207SEHDi_08_gauges_DIFF_367d7a9f-0096-42de-9166-37f6185bbe8e.swatchbin'),
                       ('LITE', '../../tex/PEU_207SEHDi_08_gauges_LITE_70befc2f-93c5-4e84-b1df-418e28c4bd7f.swatchbin')):
        T = open(path, 'rb').read()
        base = swatch.decode_level(T[0x53:], 0, 1024, 512, '2d')
        img = np.array(draw(kind == 'LITE').resize((1024, 512), Image.LANCZOS)).astype(float)
        fu, reg = fuel_from_fiesta(base, kind == 'LITE'); img[reg] = fu[reg]
        rgba = np.dstack([img.clip(0, 255).astype(np.uint8), np.full((512, 1024), 255, np.uint8)])
        Image.fromarray(rgba[..., :3]).save(f'gauges_207_{kind}.png')
        open(f'gauges_{kind}.swatchbin', 'wb').write(swatch.write_like(T, rgba))
        print(kind, 'written')
