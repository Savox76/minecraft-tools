"""Eiffelturm – Ausbau-Version (verfeinert wie ein Creator).

Leitbild: filigraner. Fachwerk statt voller Zaunringe, große Bögen zwischen den Beinen, Abendbeleuchtung.
Form, Höhe und Plattformen bleiben wie in der Grundversion (gleicher Ursprung, 45 × 45, 112 Ebenen).

- Gitterwerk: In jeder zweiten Ebene bleibt der Zaunring ganz, dazwischen nur Eckstiele und ein Mittelpfosten.
  So entstehen offene Felder wie beim echten Fachwerk.
- Bögen: Auf allen vier Seiten ein Parabelbogen aus dunklen Eichenbrettern unter der ersten Plattform,
  darüber senkrechte Zaunstäbe in den Zwickeln.
- Abendbeleuchtung: Ockerfarbene Froschlichter in den Eckstielen, Lichterketten aus Hängelaternen unter den
  Plattformen, Bodenstrahler an den Füßen.
- Platz: Kieswege, Brunnen unter dem Turm, Beete, Bänke und Laternen.

Das Skript liest den Turm aus builds/eiffelturm/model.json.
Aufruf: python tools/ausbau_eiffelturm.py builds/eiffelturm/ausbau [zaehlung.json]
"""
import json
import math
import os
import sys

ZIEL = sys.argv[1]
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = json.load(open(os.path.join(WURZEL, 'builds', 'eiffelturm', 'model.json'), encoding='utf-8'))
X, Y, Z = BASIS['size']['x'], BASIS['size']['y'], BASIS['size']['z']
MX = MZ = 22

P = []
ZEICHEN = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&*+-/:;<=>?@^_~')


def block(name, mc, farbe, flags=None):
    e = {'key': next(ZEICHEN), 'name': name, 'block': mc, 'color': farbe}
    if flags:
        e['flags'] = flags
    P.append(e)
    return e['key']


uebernahme = {p['key']: block(p['name'], p.get('block'), p['color'], p.get('flags')) for p in BASIS['palette']}
N = {p['name']: uebernahme[p['key']] for p in BASIS['palette']}
BRETT = N['Dunkle Eichenholzbretter']
ZAUN = N['Dunkle-Eichen-Zaun']
STUFE = N['Dunkle-Eichen-Stufe (unten)']
STEIN = N['Steinziegel']
GITTER = N['Eisengitter']
LATERNE = N['Laterne']

LICHT = block('Ockerfarbenes Froschlicht', 'minecraft:ochre_froglight', '#f3d27a')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
GRAS = block('Gras (vorhanden)', 'minecraft:grass_block', '#7c9a4c', ['vorhanden'])
KIES = block('Kies', 'minecraft:gravel', '#8f8984')
WEG = block('Glatter Stein', 'minecraft:smooth_stone', '#a3a6a8')
WASSER = block('Wasser', 'minecraft:water', '#3f86f0')
RAND = block('Glatte-Stein-Stufe (unten)', 'minecraft:smooth_stone_slab[type=bottom]', '#a9acae')
BANK = {r: block('Dunkle Eichentreppe (hohe Seite nach %s)' % n, 'minecraft:dark_oak_stairs[facing=%s]' % r, '#4a3221')
        for r, n in (('north', 'Norden'), ('south', 'Süden'), ('east', 'Osten'), ('west', 'Westen'))}
HECKE = block('Eichenlaub (Buchs)', 'minecraft:oak_leaves[persistent=true]', '#4f7a32')
BLUMEN = [block(n, mc, c) for n, mc, c in (('Rote Tulpe', 'minecraft:red_tulip', '#d23a2a'),
                                           ('Weiße Tulpe', 'minecraft:white_tulip', '#f1f1ea'),
                                           ('Kornblume', 'minecraft:cornflower', '#4f73d6'))]

NAME = {e['key']: e['name'] for e in P}
G = {}
for y, ebene in enumerate(BASIS['layers']):
    for z, reihe in enumerate(ebene):
        for x, ch in enumerate(reihe):
            if ch != '.':
                G[(x, y, z)] = uebernahme[ch]


def put(x, y, z, k, ueber=False):
    if not (0 <= x < X and 0 <= y < Y and 0 <= z < Z):
        raise SystemExit('außerhalb: %s %s' % ((x, y, z), NAME[k]))
    alt = G.get((x, y, z))
    if alt is not None and alt != k and not ueber:
        raise SystemExit('Konflikt bei %s: %s gegen %s' % ((x, y, z), NAME[alt], NAME[k]))
    G[(x, y, z)] = k


def leer(x, y, z):
    return (x, y, z) not in G


PLATTFORMEN = set(range(15, 21)) | {38, 39} | set(range(92, 98))

# =====================================================================
# Gitterwerk: Ringe pro Ebene finden, in ungeraden Ebenen nur Ecken und Mittelpfosten behalten
# =====================================================================
for y in range(2, 92):
    if y in PLATTFORMEN:
        continue
    zellen = {(x, z) for (x, yy, z), k in G.items() if yy == y and k in (BRETT, ZAUN)}
    gesehen = set()
    for start in list(zellen):
        if start in gesehen:
            continue
        teil, stapel = [], [start]
        gesehen.add(start)
        while stapel:
            c = stapel.pop()
            teil.append(c)
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dz)
                if n in zellen and n not in gesehen:
                    gesehen.add(n)
                    stapel.append(n)
        x0, x1 = min(c[0] for c in teil), max(c[0] for c in teil)
        z0, z1 = min(c[1] for c in teil), max(c[1] for c in teil)
        for (x, z) in teil:
            ecke = x in (x0, x1) and z in (z0, z1)
            if ecke:
                if y % 6 == 4:
                    G[(x, y, z)] = LICHT                       # Abendbeleuchtung in den Eckstielen
                continue
            if G[(x, y, z)] != ZAUN or y % 2 == 0:
                continue
            if z in (z0, z1):
                t, L = x - x0, x1 - x0
            else:
                t, L = z - z0, z1 - z0
            if t != L // 2:
                del G[(x, y, z)]                               # offenes Feld

# =====================================================================
# Bögen zwischen den Beinen (alle vier Seiten), Zwickel mit senkrechten Stäben
# =====================================================================
EBENEN = [('z', 8), ('z', 36), ('x', 8), ('x', 36)]
for achse, f in EBENEN:
    pos = (lambda a, y: (a, y, f)) if achse == 'z' else (lambda a, y: (f, y, a))
    # alten Bogen der Grundversion entfernen
    for a in range(15, 30):
        for y in (15, 16):
            if G.get(pos(a, y)) == BRETT:
                del G[pos(a, y)]
    vorher = None
    for a in range(13, 32):
        ya = int(round(14 - 6 * ((a - 22) / 9.0) ** 2))
        for y in ([ya] if vorher is None else range(min(ya, vorher), max(ya, vorher) + 1)):
            if leer(*pos(a, y)):
                put(*pos(a, y), BRETT)
        vorher = ya
        if a % 2 == 0:
            for y in range(ya + 1, 17):
                if leer(*pos(a, y)):
                    put(*pos(a, y), ZAUN)
                else:
                    break

# =====================================================================
# Lichterketten unter den Plattformen
# =====================================================================
for (y_unter, lo, hi) in ((16, 9, 35), (37, 15, 29), (91, 17, 27)):
    for a in range(lo + 2, hi - 1, 3):
        for (x, z) in ((a, lo), (a, hi), (lo, a), (hi, a)):
            if leer(x, y_unter, z) and not leer(x, y_unter + 1, z):
                put(x, y_unter, z, HAENGE)

# =====================================================================
# Platz: Kieswege, Brunnen, Beete, Bänke, Laternen, Bodenstrahler
# =====================================================================
for x in range(X):
    for z in range(Z):
        if not leer(x, 0, z):
            continue
        d = math.hypot(x - MX, z - MZ)
        if d <= 3.6:
            put(x, 0, z, WASSER)
        elif d <= 4.6:
            put(x, 0, z, WEG)
            put(x, 1, z, RAND)
        elif abs(x - MX) <= 1 or abs(z - MZ) <= 1:
            put(x, 0, z, KIES)
        elif 6.5 <= d <= 7.5:
            put(x, 0, z, KIES)
        else:
            put(x, 0, z, GRAS)
# Fontäne in der Mitte
put(MX, 1, MZ, RAND, True)
put(MX, 2, MZ, WASSER)
# Beete mit Buchs um den Brunnen
for x in range(X):
    for z in range(Z):
        d = math.hypot(x - MX, z - MZ)
        if 5.0 <= d < 6.4 and G.get((x, 0, z)) == GRAS and leer(x, 1, z):
            put(x, 1, z, HECKE if d >= 5.8 else BLUMEN[(x + z) % 3])
# Bänke und Laternen an den Wegen
for s in (-1, 1):
    for d in (10, 16):
        for (x, z, r) in ((MX + s * d, MZ - 2, 'north'), (MX + s * d, MZ + 2, 'south'),
                          (MX - 2, MZ + s * d, 'west'), (MX + 2, MZ + s * d, 'east')):
            if leer(x, 1, z) and G.get((x, 0, z)) == GRAS:
                put(x, 1, z, BANK[r])
        for (x, z) in ((MX + s * (d + 2), MZ - 2), (MX + s * (d + 2), MZ + 2), (MX - 2, MZ + s * (d + 2)), (MX + 2, MZ + s * (d + 2))):
            if leer(x, 1, z) and G.get((x, 0, z)) == GRAS:
                for y in (1, 2):
                    put(x, y, z, ZAUN)
                put(x, 3, z, LATERNE)
# Bodenstrahler an den Innenecken der Füße
for (x, z) in ((10, 10), (34, 10), (10, 34), (34, 34)):
    put(x, 0, z, LICHT, True)
    G.pop((x, 1, z), None)

# =====================================================================
model = {'format': 1, 'size': {'x': X, 'y': Y, 'z': Z}, 'palette': P,
         'layers': [[''.join(G.get((x, y, z), '.') for x in range(X)) for z in range(Z)] for y in range(Y)]}
n = {}
for k in G.values():
    n[k] = n.get(k, 0) + 1
vorh = {e['key'] for e in P if set(e.get('flags') or []) & {'vorhanden', 'kein-block'}}
print('Blöcke', sum(v for k, v in n.items() if k not in vorh), 'Blockarten', len([k for k in n if k not in vorh]))
P[:] = [e for e in P if e['key'] in n]
os.makedirs(ZIEL, exist_ok=True)
with open(os.path.join(ZIEL, 'model.json'), 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False)
    f.write('\n')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump({NAME[k]: v for k, v in sorted(n.items(), key=lambda t: -t[1])}, f, ensure_ascii=False, indent=0)
