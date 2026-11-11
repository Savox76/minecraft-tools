"""Gewächshaus-Farm – Ausbau-Version (kleiner Ausbau, verfeinert wie ein Creator).

Leitbild: Die Farm bleibt genau wie sie ist. Dazu kommen ein Rahmen aus dunklem Holz (mehr Pfosten und Sparren,
umlaufender Rähm, Zierkamm auf dem First), ein niedriger Sockel aus Steinziegeln, Pflanzkästen innen und außen,
Wege und Laternen.

Feld, Wasser, Trichter, Truhe, Komposter, Bett, Nische und Dorfbewohner bleiben unverändert. Korrigiert wird ein
Fehler der Grundversion: Vor der Nische stand ein Holzpfosten, durch den der Bauer den zweiten Dorfbewohner nicht
sehen konnte. Dort ist jetzt Glas.

Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Boden.
Aufruf: python tools/ausbau_gewaechshaus.py builds/gewaechshaus-farm/ausbau [zaehlung.json]
"""
import json
import os
import sys

ZIEL = sys.argv[1]
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = json.load(open(os.path.join(WURZEL, 'builds', 'gewaechshaus-farm', 'model.json'), encoding='utf-8'))
X, Y, Z = 19, 15, 25

P = []
ZEICHEN = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&*+-/:;<=>?@^_~')
RICHT = {'north': 'Norden', 'south': 'Süden', 'east': 'Osten', 'west': 'Westen'}
VIER = ('north', 'east', 'south', 'west')


def block(name, mc, farbe, flags=None):
    e = {'key': next(ZEICHEN), 'name': name, 'block': mc, 'color': farbe}
    if flags:
        e['flags'] = flags
    P.append(e)
    return e['key']


# Übernommen aus der Grundversion (gleiche Namen und Blöcke, damit der Umbau sie als „bleibt“ erkennt)
uebernahme = {}
for p in BASIS['palette']:
    uebernahme[p['key']] = block(p['name'], p.get('block'), p['color'], p.get('flags'))
NAMEN = {p['name']: uebernahme[p['key']] for p in BASIS['palette']}
STEINZ = NAMEN['Steinziegel']
GLAS = NAMEN['Glas']
STAMM = NAMEN['Dunkle-Eichen-Stamm']
LATERNE = NAMEN['Laterne']

GRAS = block('Gras (vorhanden)', 'minecraft:grass_block', '#7c9a4c', ['vorhanden'])
SPARREN = {r: block('Dunkle Eichentreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:dark_oak_stairs[facing=%s]' % r, '#4a3221')
           for r in ('north', 'south')}
RAEHM_X = block('Dunkler Eichenstamm (liegend, Ost-West)', 'minecraft:dark_oak_log[axis=x]', '#3e2c1c')
RAEHM_Z = block('Dunkler Eichenstamm (liegend, Nord-Süd)', 'minecraft:dark_oak_log[axis=z]', '#3e2c1c')
KAMM = block('Eisengitter', 'minecraft:iron_bars', '#8d9196')
ZAUN = block('Dunkler Eichenzaun', 'minecraft:dark_oak_fence', '#4a3221')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
TISCH = block('Dunkle-Eichen-Stufe (oben)', 'minecraft:dark_oak_slab[type=top]', '#4a3221')
PODSOL = block('Podsol', 'minecraft:podzol', '#6a4a2a')
KASTEN = {r: block('Dunkle-Eichen-Falltür (Pflanzkasten, offen nach %s)' % RICHT[r], 'minecraft:dark_oak_trapdoor[open=true,facing=%s]' % r, '#4a3221')
          for r in VIER}
WEG = block('Glatter Stein', 'minecraft:smooth_stone', '#a3a6a8')
KIES = block('Kies', 'minecraft:gravel', '#8f8984')
REGEN = block('Kessel mit Wasser', 'minecraft:water_cauldron[level=3]', '#4a4a50')
BANK = block('Fichtentreppe (hohe Seite nach Norden)', 'minecraft:spruce_stairs[facing=north]', '#7a5a36')
T = {n: block(n, mc, c) for n, mc, c in (
    ('Topf mit Farn', 'minecraft:potted_fern', '#5c8c3a'),
    ('Topf mit Mohn', 'minecraft:potted_poppy', '#c4402e'),
    ('Topf mit Kornblume', 'minecraft:potted_cornflower', '#4f73d6'),
    ('Topf mit Bambus', 'minecraft:potted_bamboo', '#7fae3a'),
    ('Topf mit Kaktus', 'minecraft:potted_cactus', '#5a8a3a'),
    ('Topf mit blühender Azalee', 'minecraft:potted_flowering_azalea_bush', '#7a9a3a'))}
B = {n: block(n, mc, c) for n, mc, c in (
    ('Zierlauch', 'minecraft:allium', '#9a6ad0'),
    ('Weiße Tulpe', 'minecraft:white_tulip', '#f1f1ea'),
    ('Rote Tulpe', 'minecraft:red_tulip', '#d23a2a'),
    ('Kornblume', 'minecraft:cornflower', '#4f73d6'),
    ('Margerite', 'minecraft:oxeye_daisy', '#f0efe0'),
    ('Farn', 'minecraft:fern', '#5c8c3a'),
    ('Kurzes Gras', 'minecraft:short_grass', '#6c9a40'))}
BLUMEN = [B['Zierlauch'], B['Weiße Tulpe'], B['Farn'], B['Rote Tulpe'], B['Kornblume'], B['Margerite']]
TOEPFE = list(T.values())

NAME = {e['key']: e['name'] for e in P}
G = {}


def put(x, y, z, k, ueber=False):
    if not (0 <= x < X and 0 <= y < Y and 0 <= z < Z):
        raise SystemExit('außerhalb: %s %s' % ((x, y, z), NAME[k]))
    alt = G.get((x, y, z))
    if alt is not None and alt != k and not ueber:
        raise SystemExit('Konflikt bei %s: %s gegen %s' % ((x, y, z), NAME[alt], NAME[k]))
    G[(x, y, z)] = k


def leer(x, y, z):
    return (x, y, z) not in G


# ---- Grundversion übernehmen ----
for y, ebene in enumerate(BASIS['layers']):
    for z, reihe in enumerate(ebene):
        for x, ch in enumerate(reihe):
            if ch != '.':
                put(x, y, z, uebernahme[ch])
TREPPE_ALT = NAMEN['Dunkle-Eichen-Treppe']
STUFE_ALT = NAMEN['Dunkle-Eichen-Stufe']

# ---- Fehler der Grundversion: Pfosten vor der Nische wird Glas (der Bauer muss den Dorfbewohner sehen) ----
for y in (1, 2):
    put(9, y, 3, GLAS, True)

# ---- Wände: Sockel aus Steinziegeln (Ebene 1), mehr Pfosten, Rähm oben ----
WAND = [(x, z) for x in range(2, 17) for z in range(3, 18) if x in (2, 16) or z in (3, 17)]
PFOSTEN = {(x, z) for x in (2, 5, 9, 13, 16) for z in (3, 17)} | {(x, z) for x in (2, 16) for z in (3, 6, 10, 14, 17)}
NISCHE = {(8, 3), (9, 3), (10, 3)}
for x, z in WAND:
    for y in range(1, 5):
        alt = G.get((x, y, z))
        if alt not in (GLAS, STAMM):
            continue                                   # Tor bleibt
        if (x, z) in NISCHE and y <= 2:
            continue                                   # Blick in die Nische frei
        if (x, z) in PFOSTEN and not ((x, z) == (9, 3) and y <= 2):
            put(x, y, z, STAMM, True)
        elif y == 1:
            put(x, y, z, STEINZ, True)
        elif y == 4:
            put(x, y, z, RAEHM_X if z in (3, 17) else RAEHM_Z, True)
        else:
            put(x, y, z, GLAS, True)

# ---- Dach: Sparren mit Richtung, zwei zusätzliche Sparren, Firstbalken, Zierkamm ----
for (x, y, z), k in list(G.items()):
    if y >= 5 and k == TREPPE_ALT:
        G[(x, y, z)] = SPARREN['south' if z < 10 else 'north'] if z != 10 else STAMM
for (x, y, z), k in list(G.items()):
    if y >= 5 and k == GLAS and x in (5, 13) and z != 10:
        G[(x, y, z)] = SPARREN['south' if z < 10 else 'north']
for x in range(2, 17):
    if G.get((x, 12, 10)) in (STUFE_ALT, SPARREN['north'], SPARREN['south'], STAMM):
        G[(x, 12, 10)] = RAEHM_X
for x in range(3, 16):
    put(x, 13, 10, KAMM)
for x in (2, 16):
    put(x, 13, 10, ZAUN)
    put(x, 14, 10, LATERNE)
# Hängelaternen unter dem First
for x in (5, 9, 13):
    put(x, 11, 10, HAENGE)

# ---- Pflanztische innen an den Längswänden ----
for x, zs in ((3, (5, 6, 7, 8, 12, 13, 14, 15)), (15, (6, 7, 8, 12, 13, 14, 15))):
    for i, z in enumerate(zs):
        if leer(x, 1, z):
            put(x, 1, z, TISCH)
            put(x, 2, z, TOEPFE[(i + x) % len(TOEPFE)])

# ---- Pflanzkästen außen: Podsol, Blumen, Front aus Falltüren ----
for z in range(4, 17):
    i = z % len(BLUMEN)
    put(1, 1, z, PODSOL)
    put(1, 2, z, BLUMEN[i])
    put(0, 1, z, KASTEN['west'])
    put(17, 1, z, PODSOL)
    put(17, 2, z, BLUMEN[(i + 3) % len(BLUMEN)])
    put(18, 1, z, KASTEN['east'])
for x, r in ((1, 'north'), (17, 'north')):
    put(x, 1, 3, KASTEN[r])
for x, r in ((1, 'south'), (17, 'south')):
    put(x, 1, 17, KASTEN[r])

# ---- Weg zum Tor, Laternenpfähle, Beete, Bank, Regentonne ----
for z in range(18, 25):
    for x in (8, 9, 10):
        put(x, 0, z, WEG if x == 9 or z % 2 == 0 else KIES)
for x in (7, 11):
    for z in (19, 23):
        put(x, 1, z, ZAUN)
        put(x, 2, z, ZAUN)
        put(x, 3, z, LATERNE)
put(7, 1, 18, REGEN)
put(12, 1, 21, BANK)
put(13, 1, 21, BANK)
for x in list(range(3, 7)) + list(range(14, 16)):
    for z in range(19, 24):
        if (x + z) % 2 == 0:
            put(x, 1, z, BLUMEN[(x * 3 + z) % len(BLUMEN)])
for x, z in ((1, 20), (16, 23), (5, 1), (13, 1), (0, 19), (18, 22)):
    if leer(x, 1, z):
        put(x, 1, z, B['Kurzes Gras'])

for x in range(X):
    for z in range(Z):
        if leer(x, 0, z):
            put(x, 0, z, GRAS)

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
