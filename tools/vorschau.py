"""Isometrische Vorschaubilder mit echten Blockformen.

Liest die Minecraft-ID samt Zuständen aus der Palette (facing, half, type, open, part ...) und zeichnet
Treppen, Stufen, Falltüren, Türen, Scheiben, Zäune, Mauern, Teppiche, Töpfe, Pflanzen usw. in ihrer Form.
Ohne Zustände (ältere Modelle) wird die Form wie bisher aus dem deutschen Namen erraten.

Aufruf zum Testen:
    python tools/vorschau.py builds/<id>/model.json bild.png [--drehung 0-3] [--bis-ebene N] [--breite 1600]
"""
import argparse
import json
import re

from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# Blöcke lesen
# ---------------------------------------------------------------------------


def lese_block(s):
    """'minecraft:oak_stairs[facing=east,half=top]' -> ('oak_stairs', {'facing': 'east', 'half': 'top'})"""
    if not s:
        return '', {}
    m = re.match(r'(?:[a-z_]+:)?([a-z0-9_]+)(?:\[(.*)\])?', s)
    if not m:
        return '', {}
    zust = {}
    if m.group(2):
        for teil in m.group(2).split(','):
            if '=' in teil:
                k, v = teil.split('=', 1)
                zust[k.strip()] = v.strip()
    return m.group(1), zust


def art(bid, name):
    """Grobe Formklasse eines Blocks."""
    if not bid:
        n = name
        for f, rx in (('mob', r'Dorfbewohner'), ('flat', r'Redstonestaub|Seerosenblatt|Teppich|Blütenblätter'),
                      ('bed', r'Bett'), ('trapdoor', r'Falltür'), ('door', r'(?i)tür'), ('fence', r'(?i)zaun'),
                      ('wall', r'(?i)mauer'), ('thin', r'(?i)eisengitter|blitzableiter|laterne|leiter|fackel|bambus'),
                      ('pane', r'Glasscheibe'), ('slab', r'Stufe'), ('glass', r'^Glas$'), ('water', r'Wasser|Meer')):
            if re.search(rx, n):
                return f
        return 'full'
    if bid in ('water', 'bubble_column'):
        return 'water'
    if bid == 'glass' or (bid.endswith('_stained_glass') and 'pane' not in bid) or bid == 'tinted_glass':
        return 'glass'
    for suff, f in (('_stairs', 'stairs'), ('_slab', 'slab'), ('_trapdoor', 'trapdoor'), ('_door', 'door'),
                    ('_pane', 'pane'), ('_fence_gate', 'gate'), ('_fence', 'fence'), ('_wall', 'wall'),
                    ('_carpet', 'flat'), ('_pressure_plate', 'plate'), ('_bed', 'bed'), ('_button', 'button')):
        if bid.endswith(suff) and not (suff == '_wall' and bid.endswith('_wall_sign')):
            return f
    if bid == 'iron_bars':
        return 'pane'
    if bid.startswith('potted_') or bid == 'flower_pot':
        return 'pot'
    if bid in ('lantern', 'soul_lantern'):
        return 'lantern'
    if bid in ('end_rod', 'lightning_rod', 'chain', 'bamboo', 'torch', 'soul_torch', 'ladder'):
        return 'rod'
    if bid in ('campfire', 'soul_campfire'):
        return 'campfire'
    if bid == 'daylight_detector':
        return 'detector'
    if bid in ('brewing_stand',):
        return 'stand'
    if bid in ('lily_pad', 'redstone_wire', 'pink_petals', 'moss_carpet', 'snow'):
        return 'flat'
    if bid in ('short_grass', 'grass', 'fern', 'dead_bush', 'poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'allium',
               'azure_bluet', 'blue_orchid', 'lily_of_the_valley', 'sweet_berry_bush', 'sapling', 'wheat', 'carrots',
               'potatoes', 'beetroots', 'kelp', 'seagrass', 'sugar_cane') or bid.endswith('_tulip') or bid.endswith('_sapling'):
        return 'plant'
    if bid in ('lectern', 'enchanting_table', 'stonecutter'):
        return 'low'
    if bid in ('comparator', 'repeater'):
        return 'thinplate'
    if bid == 'villager':
        return 'mob'
    return 'full'


VERBINDET = {'full', 'glass', 'pane', 'fence', 'wall', 'stairs', 'gate'}

# ---------------------------------------------------------------------------
# Drehung (Blick aus vier Richtungen)
# ---------------------------------------------------------------------------
DREH = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}


def drehe_richtung(r, n):
    for _ in range(n % 4):
        r = DREH.get(r, r)
    return r


# ---------------------------------------------------------------------------
# Formen als Quader (u = x, v = z, y nach oben; je 0..1 im Block)
# ---------------------------------------------------------------------------


def quader(a, zust, nb):
    """Liste von (u0, u1, y0, y1, v0, v1, farbfaktor) für eine Formklasse."""
    f = zust.get('facing', 'north')
    if a == 'full' or a == 'glass':
        return [(0, 1, 0, 1, 0, 1, 1)]
    if a == 'water':
        return [(0, 1, 0, .88, 0, 1, 1)]
    if a == 'slab':
        t = zust.get('type', 'bottom')
        if t == 'double':
            return [(0, 1, 0, 1, 0, 1, 1)]
        return [(0, 1, .5, 1, 0, 1, 1)] if t == 'top' else [(0, 1, 0, .5, 0, 1, 1)]
    if a == 'stairs':
        oben = zust.get('half', 'bottom') == 'top'
        unten = (0, 1, .5, 1, 0, 1, 1) if oben else (0, 1, 0, .5, 0, 1, 1)
        y0, y1 = (0, .5) if oben else (.5, 1)
        hinten = {'north': (0, 1, y0, y1, 0, .5, 1), 'south': (0, 1, y0, y1, .5, 1, 1),
                  'east': (.5, 1, y0, y1, 0, 1, 1), 'west': (0, .5, y0, y1, 0, 1, 1)}[f]
        return [unten, hinten]
    if a == 'trapdoor':
        d = .1875
        if zust.get('open') == 'true':
            return [{'north': (0, 1, 0, 1, 1 - d, 1, .95), 'south': (0, 1, 0, 1, 0, d, .95),
                     'east': (0, d, 0, 1, 0, 1, .95), 'west': (1 - d, 1, 0, 1, 0, 1, .95)}[f]]
        return [(0, 1, 1 - d, 1, 0, 1, .95)] if zust.get('half') == 'top' else [(0, 1, 0, d, 0, 1, .95)]
    if a == 'door':
        d = .1875
        return [{'north': (0, 1, 0, 1, 1 - d, 1, .95), 'south': (0, 1, 0, 1, 0, d, .95),
                 'east': (0, d, 0, 1, 0, 1, .95), 'west': (1 - d, 1, 0, 1, 0, 1, .95)}[f]]
    if a in ('pane', 'fence', 'wall'):
        if a == 'pane':
            p0, p1, a0, a1, h0, h1 = .4375, .5625, .4375, .5625, 0, 1
        elif a == 'fence':
            p0, p1, a0, a1, h0, h1 = .375, .625, .4375, .5625, .375, .9375
        else:
            p0, p1, a0, a1, h0, h1 = .25, .75, .3125, .6875, 0, .875
        q = [(p0, p1, 0, 1 if a != 'wall' else 1, p0, p1, 1)]
        n_, s_, o_, w_ = (nb(0, -1) in VERBINDET, nb(0, 1) in VERBINDET, nb(1, 0) in VERBINDET, nb(-1, 0) in VERBINDET)
        if n_:
            q.append((a0, a1, h0, h1, 0, p0, 1))
        if s_:
            q.append((a0, a1, h0, h1, p1, 1, 1))
        if w_:
            q.append((0, p0, h0, h1, a0, a1, 1))
        if o_:
            q.append((p1, 1, h0, h1, a0, a1, 1))
        return q
    if a == 'gate':
        return [(0, 1, .3, 1, .4375, .5625, 1)] if f in ('north', 'south') else [(.4375, .5625, .3, 1, 0, 1, 1)]
    if a == 'flat':
        return [(0, 1, 0, .0625, 0, 1, 1)]
    if a == 'plate':
        return [(.0625, .9375, 0, .0625, .0625, .9375, 1)]
    if a == 'bed':
        return [(0, 1, 0, .5625, 0, 1, 1)]
    if a == 'button':
        return [(.3125, .6875, 0, .125, .375, .625, 1)]
    if a == 'pot':
        return [(.3125, .6875, 0, .375, .3125, .6875, 1), ('pflanze', .38, .62, .375, .95, .38, .62)]
    if a == 'lantern':
        if zust.get('hanging') == 'true':
            return [(.3125, .6875, .0625, .5625, .3125, .6875, 1.15), (.47, .53, .5625, 1, .47, .53, .7)]
        return [(.3125, .6875, 0, .5625, .3125, .6875, 1.15)]
    if a == 'rod':
        return [(.4375, .5625, 0, 1, .4375, .5625, 1.1)]
    if a == 'campfire':
        return [(0, 1, 0, .4375, 0, 1, 1), ('flamme', .3, .7, .4375, .8, .3, .7)]
    if a == 'detector':
        return [(0, 1, 0, .375, 0, 1, 1)]
    if a == 'stand':
        return [(.4375, .5625, 0, .875, .4375, .5625, 1), (.125, .875, 0, .125, .125, .875, .9)]
    if a == 'plant':
        return [('pflanze', .2, .8, 0, .8, .2, .8)]
    if a == 'low':
        return [(0, 1, 0, .875, 0, 1, 1)]
    if a == 'thinplate':
        return [(0, 1, 0, .125, 0, 1, 1)]
    if a == 'mob':
        return [(.26, .74, 0, 1.85, .26, .74, 1)]
    if a == 'thin':
        return [(.32, .68, 0, 1, .32, .68, 1)]
    return [(0, 1, 0, 1, 0, 1, 1)]


PFLANZE = (92, 140, 58)
FLAMME = (255, 170, 60)

# ---------------------------------------------------------------------------
# Zeichnen
# ---------------------------------------------------------------------------


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def zeichne(model, breite, hoehe, drehung=0, bis_ebene=None, ab_ebene=0, fuellung=.92, schatten=True,
            hintergrund=None, umgebung=True):
    """Bild (RGBA) des Modells. drehung 0..3 dreht um je 90°, bis_ebene schneidet oben ab (Innenansicht)."""
    S = 3
    W, H = breite * S, hoehe * S
    X, Y, Z = model['size']['x'], model['size']['y'], model['size']['z']
    pal = model['palette']
    idx = {p['key']: i for i, p in enumerate(pal)}
    info = []
    for p in pal:
        bid, zust = lese_block(p.get('block') or '')
        info.append((art(bid, p['name']), zust, hexrgb(p['color']), 'vorhanden' in (p.get('flags') or []), bid))
    n = drehung % 4

    def dreh(x, z):
        for _ in range(n):
            x, z = (Z if _ % 2 == 0 else X) - 1 - z, x
        return x, z

    # nach Drehung: Breite in x
    grid = {}
    for y, ebene in enumerate(model['layers']):
        if y < ab_ebene or (bis_ebene is not None and y > bis_ebene):
            continue
        for z, reihe in enumerate(ebene):
            for x, ch in enumerate(reihe):
                if ch == '.':
                    continue
                k = idx[ch]
                if info[k][3] and not umgebung:
                    continue
                grid[dreh(x, z) + (y,)] = k
    bild = Image.new('RGBA', (W, H), hintergrund or (0, 0, 0, 0))
    if not grid:
        return bild.resize((breite, hoehe))
    K = 1.15
    xs = [x - z for (x, z, y) in grid]
    ys = [(x + z) / 2 - (y + 1) * K for (x, z, y) in grid] + [(x + z) / 2 + 1 for (x, z, y) in grid]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys), max(ys)
    a = min(W * fuellung / (x1 - x0), H * fuellung / (y1 - y0))
    ox, oy = W / 2 - (x0 + x1) / 2 * a, H / 2 - (y0 + y1) / 2 * a
    c = a * K

    def P(u, v, y):
        return (ox + (u - v) * a, oy + (u + v) * a / 2 - y * c)

    unterste = min(y for (x, z, y) in grid)
    if schatten:
        boden = [P(x + du, z + dv, unterste) for (x, z, y) in grid if y <= unterste + 1 for du in (0, 1) for dv in (0, 1)]
        sch = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        bx0, bx1 = min(p[0] for p in boden), max(p[0] for p in boden)
        by0, by1 = min(p[1] for p in boden), max(p[1] for p in boden)
        ImageDraw.Draw(sch).ellipse([bx0, by0 + (by1 - by0) * .2, bx1, by1 + a], fill=(20, 30, 40, 50))
        bild.alpha_composite(sch.filter(ImageFilter.GaussianBlur(max(6, a * 1.2))))
    g = ImageDraw.Draw(bild)
    kante = max(1, round(.5 * S))

    def flaeche(pts, fuell):
        if fuell[3] == 255:
            g.polygon(pts, fill=fuell)
            return
        bx0, by0 = int(min(q[0] for q in pts)), int(min(q[1] for q in pts))
        bx1, by1 = int(max(q[0] for q in pts)) + 2, int(max(q[1] for q in pts)) + 2
        if bx1 <= bx0 or by1 <= by0:
            return
        st = Image.new('RGBA', (bx1 - bx0, by1 - by0), (0, 0, 0, 0))
        ImageDraw.Draw(st).polygon([(q[0] - bx0, q[1] - by0) for q in pts], fill=fuell)
        bild.alpha_composite(st, dest=(bx0, by0))

    def art_bei(x, z, y):
        k = grid.get((x, z, y))
        return None if k is None else info[k][0]

    def farbe(col, f, al):
        return (max(0, min(255, round(col[0] * f))), max(0, min(255, round(col[1] * f))),
                max(0, min(255, round(col[2] * f))), round(255 * al))

    hell = (255, 255, 255)
    for (x, z, y) in sorted(grid, key=lambda q: (q[0] + q[1] + q[2], q[2])):
        k = grid[(x, z, y)]
        a_, zust, col, kontext, bid = info[k]
        if n and 'facing' in zust:
            zust = dict(zust, facing=drehe_richtung(zust['facing'], n))
        # leichte Farbschwankung pro Block, damit Flächen nicht wie Plastik wirken
        schw = 1 + ((x * 73856093 ^ y * 19349663 ^ z * 83492791) % 9 - 4) * .011
        al = .42 if a_ == 'glass' else .7 if a_ == 'water' else .62 if a_ == 'pane' else 1
        if kontext:
            col = tuple(round(col[i] + (hell[i] - col[i]) * .62) for i in range(3))
            if al < 1:
                al *= .6
        teile = quader(a_, zust, lambda dx, dz: art_bei(x + dx, z + dz, y))
        teile = sorted(teile, key=lambda q: ((q[1] + q[2]) if isinstance(q[0], str) else (q[0] + q[4] + q[2])))
        for q in teile:
            if isinstance(q[0], str):
                kc = PFLANZE if q[0] == 'pflanze' else FLAMME
                u0, u1, ya, yb, v0, v1, ff = q[1], q[2], q[3], q[4], q[5], q[6], 1
                fc = kc
            else:
                u0, u1, ya, yb, v0, v1, ff = q
                fc = col
            voll = (u0, u1, ya, yb, v0, v1) == (0, 1, 0, 1, 0, 1) and a_ in ('full', 'glass')
            verdeckt = lambda nb: nb is not None and (nb == 'full' or (nb == a_ and a_ in ('glass', 'water')))
            oben = not (voll and verdeckt(art_bei(x, z, y + 1)))
            rechts = not (voll and verdeckt(art_bei(x + 1, z, y)))
            links = not (voll and verdeckt(art_bei(x, z + 1, y)))
            if a_ == 'water':
                oben = not verdeckt(art_bei(x, z, y + 1))
                rechts = not verdeckt(art_bei(x + 1, z, y))
                links = not verdeckt(art_bei(x, z + 1, y))
            U0, U1, V0, V1, Y0, Y1 = x + u0, x + u1, z + v0, z + v1, y + ya, y + yb
            f = ff * schw
            if links:
                flaeche([P(U0, V1, Y1), P(U1, V1, Y1), P(U1, V1, Y0), P(U0, V1, Y0)], farbe(fc, .66 * f, al))
            if rechts:
                flaeche([P(U1, V0, Y1), P(U1, V1, Y1), P(U1, V1, Y0), P(U1, V0, Y0)], farbe(fc, .82 * f, al))
            if oben:
                deckel = [P(U0, V0, Y1), P(U1, V0, Y1), P(U1, V1, Y1), P(U0, V1, Y1)]
                flaeche(deckel, farbe(fc, 1.0 * f, al))
                if a_ == 'full' and a >= 4 * S and not kontext:
                    g.line(deckel + [deckel[0]], fill=(0, 0, 0, 30), width=kante)
    return bild.resize((breite, hoehe), Image.LANCZOS)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('modell')
    ap.add_argument('bild')
    ap.add_argument('--drehung', type=int, default=0)
    ap.add_argument('--bis-ebene', type=int, default=None)
    ap.add_argument('--ab-ebene', type=int, default=0)
    ap.add_argument('--breite', type=int, default=1600)
    ap.add_argument('--hoehe', type=int, default=1100)
    ap.add_argument('--ohne-umgebung', action='store_true')
    a = ap.parse_args()
    m = json.load(open(a.modell, encoding='utf-8'))
    b = zeichne(m, a.breite, a.hoehe, a.drehung, a.bis_ebene, a.ab_ebene, umgebung=not a.ohne_umgebung,
                hintergrund=(233, 238, 243, 255))
    b.save(a.bild)
