"""Autoshow presentation for a packaged car mod: thumbnails, make logos and the database fields that point at them.

  python3 fh2re/presentation.py MODDIR --thumb big.png [--logo-text "TORO ROSSO" | --logo-png logo.png]
                                       [--use-make ID --make-name-ref '_&...'] [--make-icon-base Name]

* --thumb: a transparent 816x459 render (scan/viewer/thumb.js); writes media/stripped/RC0/Thumbnail_<car>_Big/_Small
  and points Data_Car.Thumbnail at game:\\Media\\Stripped\\RC0\\Thumbnail_<car>.png (the game adds _Big/_Small).
* --logo-text / --logo-png: writes Manu_Logo_<CODE> (220x184) and L_Manu_Logo_<CODE> (440x376) and points the mod's
  List_CarMake row at them. IconPathBase = the make name without spaces (vanilla style: 'AstonMartin').
* --use-make: drop the mod's own List_CarMake row and use an existing make instead (a vanilla make such as Volvo 53,
  or another mod's make); every ManufacturerID/MakeID that pointed at the old make is moved over.
UI swatchbin format: tex/uiswatch.py.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tex'))
import uiswatch

FONT = next((f for f in ('/usr/share/fonts/opentype/inter/Inter-Bold.otf', '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf',
                         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') if os.path.exists(f)), None)
MAKE_COLS = ('MakeID', 'ManufacturerID', 'ManufacturerId')


def wordmark(text, w, h):
    """white bold wordmark with a soft dark edge, transparent background, fitted to w x h"""
    S = 4; W, H = w * S, h * S
    size = H; img = None
    while size > 8:
        f = ImageFont.truetype(FONT, size)
        lines = text.split('\\n') if '\\n' in text else [text]
        boxes = [f.getbbox(l) for l in lines]
        tw = max(b[2] - b[0] for b in boxes); th = sum(b[3] - b[1] for b in boxes) + (len(lines) - 1) * size * 0.25
        if tw <= W * 0.9 and th <= H * 0.6: break
        size = int(size * 0.94)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = (H - th) / 2
    for l, b in zip(lines, boxes):
        x = (W - (b[2] - b[0])) / 2 - b[0]
        d.text((x, y - b[1]), l, font=f, fill=(255, 255, 255, 255), stroke_width=max(2, size // 22), stroke_fill=(20, 20, 24, 255))
        y += (b[3] - b[1]) + size * 0.25
    return img.resize((w, h), Image.LANCZOS)


def logo_from_png(path, w, h):
    src = Image.open(path).convert('RGBA'); src = src.crop(src.getbbox() or (0, 0, *src.size))
    k = min(w * 0.9 / src.width, h * 0.8 / src.height)
    src = src.resize((max(1, int(src.width * k)), max(1, int(src.height * k))), Image.LANCZOS)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.paste(src, ((w - src.width) // 2, (h - src.height) // 2)); return out


def write_swatch(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(uiswatch.encode(np.array(img.convert('RGBA'))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mod'); ap.add_argument('--thumb'); ap.add_argument('--logo-text'); ap.add_argument('--logo-png')
    ap.add_argument('--use-make', type=int); ap.add_argument('--make-name-ref'); ap.add_argument('--make-icon-base')
    ap.add_argument('--dependency')
    a = ap.parse_args()
    dbp = os.path.join(a.mod, 'database.json'); db = json.load(open(dbp)); T = db['tables']
    car = T['Data_Car']['insert'][0]; cid = car['Id']
    rc0 = os.path.join(a.mod, 'media', 'stripped', 'RC0')
    if a.thumb:
        im = Image.open(a.thumb).convert('RGBA')
        write_swatch(im.resize((816, 459), Image.LANCZOS), f'{rc0}/Thumbnail_{cid}_Big.swatchbin')
        write_swatch(im.resize((192, 108), Image.LANCZOS), f'{rc0}/Thumbnail_{cid}_Small.swatchbin')
        car['Thumbnail'] = f'game:\\Media\\Stripped\\RC0\\Thumbnail_{cid}.png'
    makes = T.get('List_CarMake', {}).get('insert', [])
    if a.use_make is not None:
        old = car['MakeID']; n = 0
        for tname, t in T.items():
            for r in t.get('insert', []):
                for c in MAKE_COLS:
                    if r.get(c) == old: r[c] = a.use_make; n += 1
        if a.make_name_ref: car['MakeName'] = a.make_name_ref
        T['List_CarMake']['insert'] = [r for r in makes if r['ID'] != old]
        if not T['List_CarMake']['insert']: del T['List_CarMake']
        sp = os.path.join(a.mod, 'strings.json')
        if os.path.exists(sp):
            s = json.load(open(sp))
            for lang in s['languages'].values(): lang.pop('List_CarMake', None)
            json.dump(s, open(sp, 'w'), indent=1, ensure_ascii=False)
        print(f'make {old} -> {a.use_make} ({n} references)')
    elif a.logo_text or a.logo_png:
        mk = makes[0]; code = mk['ManufacturerCode']
        for name, (w, h) in (('Manu_Logo', (220, 184)), ('L_Manu_Logo', (440, 376))):
            img = logo_from_png(a.logo_png, w, h) if a.logo_png else wordmark(a.logo_text, w, h)
            write_swatch(img, f'{rc0}/{name}_{code}.swatchbin')
        mk['IconPath'] = f'game:\\Media\\Stripped\\RC0\\Manu_Logo_{code}.swatchbin'
        mk['IconPathLarge'] = f'game:\\Media\\Stripped\\RC0\\L_Manu_Logo_{code}.swatchbin'
        if a.make_icon_base: mk['IconPathBase'] = a.make_icon_base
    json.dump(db, open(dbp, 'w'), indent=1, ensure_ascii=False)
    if a.dependency:
        mp = os.path.join(a.mod, 'mod.json'); m = json.load(open(mp))
        m['dependencies'] = sorted(set(m.get('dependencies', [])) | {a.dependency}); json.dump(m, open(mp, 'w'), indent=1)
    print('updated', a.mod)


if __name__ == '__main__':
    main()
