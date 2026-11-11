"""Leuchtturm – Ausbau-Version (verfeinert wie ein Creator, kleiner Ausbau).

Leitbild: rauer Küstenfels statt glattem Sockel, ein Wärterhaus, ein Steg mit Booten, Felsen im Wasser.
Der Turm selbst bekommt nur feinere Streifen, Gesimse mit Überstand, Konsolen unter dem Umgang und ein leichteres
Geländer. Form, Höhe und Abschnitte des Turms bleiben wie in der Grundversion (Mitte x8 z8).

Das Skript liest den Turm aus builds/leuchtturm/model.json und verfeinert ihn.
Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Wasserspiegel.
Aufruf: python tools/ausbau_leuchtturm.py builds/leuchtturm/ausbau [zaehlung.json]
"""
import json
import os
import sys

ZIEL = sys.argv[1]
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = json.load(open(os.path.join(WURZEL, 'builds', 'leuchtturm', 'model.json'), encoding='utf-8'))
X, Y, Z = 34, 65, 34
MX, MZ = 8, 8

P = []
ZEICHEN = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&*+-/:;<=>?@^_~' +
               ''.join(chr(c) for c in range(0xC0, 0x100) if c not in (0xD7, 0xF7)))
RICHT = {'north': 'Norden', 'south': 'Süden', 'east': 'Osten', 'west': 'Westen'}
VIER = ('north', 'east', 'south', 'west')
SCHRITT = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}


def block(name, mc, farbe, flags=None):
    e = {'key': next(ZEICHEN), 'name': name, 'block': mc, 'color': farbe}
    if flags:
        e['flags'] = flags
    P.append(e)
    return e['key']


def je_richtung(name, mc, farbe):
    return {r: block(name % RICHT[r], mc % r, farbe) for r in VIER}


MEER = block('Wasser (Meer, vorhanden)', 'minecraft:water', '#3f86f0', ['vorhanden'])
# Fels
FSTEIN = block('Stein', 'minecraft:stone', '#7d7d7d')
ANDESIT = block('Andesit', 'minecraft:andesite', '#88898a')
BRUCH = block('Bruchstein', 'minecraft:cobblestone', '#7a7a7a')
MBRUCH = block('Bemooster Bruchstein', 'minecraft:mossy_cobblestone', '#6e7a5a')
TUFF = block('Tuffstein', 'minecraft:tuff', '#6c6d66')
GRASBLOCK = block('Grasblock', 'minecraft:grass_block', '#7c9a4c')
KIES = block('Kies', 'minecraft:gravel', '#8f8984')
# Turm (aus der Grundversion übernommen)
STEINZ = block('Steinziegel', 'minecraft:stone_bricks', '#8a8a86')
MOOSZ = block('Bemooste Steinziegel', 'minecraft:mossy_stone_bricks', '#76835e')
RISSZ = block('Rissige Steinziegel', 'minecraft:cracked_stone_bricks', '#7e7d78')
WEISS = block('Weißer Beton', 'minecraft:white_concrete', '#e3e6e6')
ROT = block('Roter Beton', 'minecraft:red_concrete', '#8e2020')
GLAS = block('Glas', 'minecraft:glass', '#a9dcec')
GITTER = block('Eisengitter', 'minecraft:iron_bars', '#8d9196')
LEITER = block('Leiter', 'minecraft:ladder[facing=north]', '#9a7a4a')
LEUCHT = block('Leuchtstein', 'minecraft:glowstone', '#e8c66a')
TUER_U = block('Eichentür (unten, Tür nach Norden)', 'minecraft:oak_door[half=lower,facing=north]', '#a7834f')
TUER_O = block('Eichentür (oben, Tür nach Norden)', 'minecraft:oak_door[half=upper,facing=north]', '#a7834f', ['zweiter-teil'])
BLITZ = block('Blitzableiter', 'minecraft:lightning_rod', '#c47a4a')
SMAUER = block('Steinziegelmauer', 'minecraft:stone_brick_wall', '#8a8a86')
KONSOLE = je_richtung('Steinziegeltreppe (verkehrt, hohe Seite nach %s)', 'minecraft:stone_brick_stairs[facing=%s,half=top]', '#8a8a86')
STUFE = je_richtung('Steinziegeltreppe (hohe Seite nach %s)', 'minecraft:stone_brick_stairs[facing=%s]', '#8a8a86')
# Wärterhaus
FICHTE = block('Fichtenholzbretter', 'minecraft:spruce_planks', '#7a5a36')
FSTAMM = block('Fichtenstamm', 'minecraft:spruce_log', '#4f3b26')
DACH = je_richtung('Rote-Netherziegel-Treppe (hohe Seite nach %s)', 'minecraft:red_nether_brick_stairs[facing=%s]', '#6e2422')
FIRST = block('Rote Netherziegel', 'minecraft:red_nether_bricks', '#6e2422')
SCHEIBE = block('Glasscheibe', 'minecraft:glass_pane', '#bfe6f2')
LADEN = je_richtung('Fichtenfalltür (Fensterladen, offen nach %s)', 'minecraft:spruce_trapdoor[open=true,facing=%s]', '#6b4a2a')
FTUER = {r: (block('Fichtentür (unten, Tür nach %s)' % RICHT[r], 'minecraft:spruce_door[half=lower,facing=%s]' % r, '#6b4a2a'),
             block('Fichtentür (oben, Tür nach %s)' % RICHT[r], 'minecraft:spruce_door[half=upper,facing=%s]' % r, '#6b4a2a', ['zweiter-teil']))
         for r in ('west', 'south')}
STUHL = je_richtung('Fichtentreppe (hohe Seite nach %s)', 'minecraft:spruce_stairs[facing=%s]', '#7a5a36')
FSTUFE = block('Fichtenstufe (unten)', 'minecraft:spruce_slab[type=bottom]', '#7a5a36')
FSTUFE_O = block('Fichtenstufe (oben)', 'minecraft:spruce_slab[type=top]', '#7a5a36')
ZAUN = block('Fichtenzaun', 'minecraft:spruce_fence', '#7a5a36')
LATERNE = block('Laterne', 'minecraft:lantern', '#f2b33d')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
FASS = block('Fass', 'minecraft:barrel[facing=up]', '#8a6438')
BETT_F = block('Blaues Bett (Fußende, Kopf nach Norden)', 'minecraft:blue_bed[part=foot,facing=north]', '#3c4f9c')
BETT_K = block('Blaues Bett (Kopfende, Kopf nach Norden)', 'minecraft:blue_bed[part=head,facing=north]', '#3c4f9c', ['zweiter-teil'])
OFEN = block('Ofen (nach Osten)', 'minecraft:furnace[facing=east]', '#6a6a6a')
KESSEL = block('Kessel mit Wasser', 'minecraft:water_cauldron[level=3]', '#4a4a50')
REGAL = block('Bücherregal', 'minecraft:bookshelf', '#9a7a4a')
LESEPULT = block('Lesepult (Logbuch)', 'minecraft:lectern[facing=west]', '#8a6438')
KARTE = block('Kartentisch', 'minecraft:cartography_table', '#7a5a36')
NETZ = block('Spinnennetz (Fischernetz)', 'minecraft:cobweb', '#e8e8e8')
TEPPICH = block('Blauer Teppich', 'minecraft:blue_carpet', '#3c4f9c')
SCHORN = block('Ziegel', 'minecraft:bricks', '#9a5444')
BOJE_R = block('Roter Beton (Boje)', 'minecraft:red_concrete', '#8e2020')
BOJE_W = block('Weißer Beton (Boje)', 'minecraft:white_concrete', '#e3e6e6')
GRAESER = block('Kurzes Gras', 'minecraft:short_grass', '#6c9a40')
STRAUCH = block('Toter Busch', 'minecraft:dead_bush', '#8a6a3a')
STRANDHAFER = block('Farn', 'minecraft:fern', '#5c8c3a')
SEEGRAS = block('Seegras', 'minecraft:seagrass', '#3f8a4a')

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


def rausch(x, y, z, n=100):
    return (x * 73856093 ^ y * 19349663 ^ z * 83492791 ^ 0x5bd1e995) % n


def fels(x, y, z):
    h = rausch(x, y, z)
    return FSTEIN if h < 34 else ANDESIT if h < 54 else BRUCH if h < 72 else MBRUCH if h < 86 else TUFF


# =====================================================================
# Turm aus der Grundversion übernehmen
# =====================================================================
ALT = {'Steinziegel': STEINZ, 'Bemooste Steinziegel': MOOSZ, 'Rissige Steinziegel': RISSZ, 'Steinziegelmauer': SMAUER,
       'Weißer Beton': WEISS, 'Roter Beton': ROT, 'Glas': GLAS, 'Eisengitter': GITTER, 'Leiter': LEITER, 'Leuchtstein': LEUCHT,
       'Eichentür (unten)': TUER_U, 'Eichentür (oben)': TUER_O, 'Blitzableiter': BLITZ}
bpal = {p['key']: p['name'] for p in BASIS['palette']}
for y, ebene in enumerate(BASIS['layers']):
    for z, reihe in enumerate(ebene):
        for x, ch in enumerate(reihe):
            if ch != '.':
                put(x, y, z, ALT[bpal[ch]])


def r2(x, z):
    return (x - MX) ** 2 + (z - MZ) ** 2


# ---- Sockel wird rauer Fels (Wand y0..4); innen bleibt der Lagerraum ----
for y in range(0, 5):
    for x in range(17):
        for z in range(17):
            k = G.get((x, y, z))
            if k in (STEINZ, MOOSZ, RISSZ) and not (y > 0 and r2(x, z) < 49):
                put(x, y, z, fels(x, y, z), True)
# Fels füllt die Ecken des Sockels unregelmäßig auf
for x in range(17):
    for z in range(17):
        if r2(x, z) <= 72:
            continue
        aus = (r2(x, z) - 72) ** .5
        top = int(4 - aus * .9 + rausch(x, 0, z, 3) - 1)
        for y in range(0, max(top, 0) + 1):
            if leer(x, y, z):
                put(x, y, z, fels(x, y, z))

# ---- Feinere Streifen: 4 Blöcke hoch im Wechsel ----
for (x, y, z), k in list(G.items()):
    if k in (WEISS, ROT) and 6 <= y <= 51:
        G[(x, y, z)] = ROT if ((y - 6) // 4) % 2 else WEISS

# ---- Gesimse mit Überstand unter den Zwischenböden y22 und y38, Konsolen unter dem Umgang y52 ----
for yb in (22, 38, 52):
    ring = [(x, z) for x in range(17) for z in range(17) if G.get((x, yb, z)) == STEINZ]
    for x, z in ring:
        for r in VIER:
            dx, dz = SCHRITT[r]
            nx, nz = x + dx, z + dz
            if (nx, nz) in ring:
                continue
            if yb == 52:
                # Konsole direkt unter der Kante des Umgangs, hohe Seite zur Turmmitte
                if leer(x, yb - 1, z):
                    gegen = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}[r]
                    put(x, yb - 1, z, KONSOLE[gegen])
            elif leer(nx, yb, nz):
                gegen = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}[r]
                put(nx, yb, nz, KONSOLE[gegen])

# ---- Leichteres Geländer auf der Terrasse: Eisengitter zwischen Steinpfosten, Öffnung nach Osten ----
for (x, y, z), k in list(G.items()):
    if k == SMAUER and y == 6:
        pfosten = (x, z) in ((8, 0), (8, 16), (0, 8), (16, 8), (2, 3), (14, 3), (2, 13), (14, 13))
        G[(x, y, z)] = SMAUER if pfosten else GITTER
for z in (7, 9):
    G.pop((16, 6, z), None)
G.pop((16, 6, 8), None)
for (x, z) in ((16, 6), (16, 10)):
    if (x, 6, z) in G:
        G[(x, 6, z)] = SMAUER
    put(x, 7, z, LATERNE, True)
# Laternen auf den Pfosten
for (x, z) in ((8, 0), (8, 16), (0, 8)):
    put(x, 7, z, LATERNE, True)

# =====================================================================
# Felsplateau mit Wärterhaus im Osten
# =====================================================================
def plateau_top(x, z):
    """Oberkante des Felsens östlich und südlich vom Turm (None = Wasser)."""
    if 18 <= x <= 27 and 3 <= z <= 12:
        return 4
    dx = max(18 - x, 0, x - 27)
    dz = max(3 - z, 0, z - 12)
    d = (dx * dx + dz * dz) ** .5
    if x < 17 and z < 17:
        return None
    top = 4 - d * 1.1 + (rausch(x, 0, z, 5) - 2) * .5
    return int(round(top)) if top >= 0 else None


for x in range(14, X):
    for z in range(0, 21):
        if x < 17 and z < 17:
            continue
        t = plateau_top(x, z)
        if t is None:
            continue
        for y in range(0, t + 1):
            if leer(x, y, z):
                oben = y == t
                k = (GRASBLOCK if rausch(x, 1, z) < 55 else KIES if rausch(x, 1, z) < 70 else fels(x, y, z)) if oben and t >= 3 else fels(x, y, z)
                put(x, y, z, k)
# Stufe von der Terrasse zum Plateau
put(17, 5, 8, STUFE['west'], True)

# ---- Wärterhaus x19..26 z4..11: weiß, Fichtenecken, rotes Satteldach ----
HX0, HX1, HZ0, HZ1 = 19, 26, 4, 11
for x in range(HX0, HX1 + 1):
    for z in range(HZ0, HZ1 + 1):
        put(x, 4, z, FICHTE if HX0 < x < HX1 and HZ0 < z < HZ1 else STEINZ, True)
        if x in (HX0, HX1) or z in (HZ0, HZ1):
            for y in range(5, 9):
                ecke = x in (HX0, HX1) and z in (HZ0, HZ1)
                put(x, y, z, FSTAMM if ecke else BRUCH if y == 5 else WEISS, True)
        for y in range(5, 15):
            if HX0 < x < HX1 and HZ0 < z < HZ1:
                G.pop((x, y, z), None)
# Fenster mit Läden
FENSTER = (('north', [(21, 4), (24, 4)]), ('south', [(21, 11), (24, 11)]), ('east', [(26, 7), (26, 8)]), ('west', [(19, 5)]))
for seite, liste in FENSTER:
    dx, dz = SCHRITT[seite]
    for x, z in liste:
        for y in (6, 7):
            put(x, y, z, SCHEIBE, True)
            qx, qz = (1, 0) if seite in ('north', 'south') else (0, 1)
            for s in (-1, 1):
                ox, oz = x + dx + s * qx, z + dz + s * qz
                if leer(ox, y, oz):
                    put(ox, y, oz, LADEN[seite])
# Tür nach Westen (zum Turm) und nach Süden (zum Steg)
put(19, 5, 8, FTUER['west'][0], True)
put(19, 6, 8, FTUER['west'][1], True)
put(23, 5, 11, FTUER['south'][0], True)
put(23, 6, 11, FTUER['south'][1], True)
# Dach: First in Ost-West-Richtung, Überstand 1
for x in range(HX0 - 1, HX1 + 2):
    for z in range(HZ0 - 1, HZ1 + 2):
        d = min(z - (HZ0 - 1), (HZ1 + 1) - z)
        y = 8 + d
        if z in (7, 8):
            put(x, y, z, FIRST, True)
        else:
            put(x, y, z, DACH['south' if z < 7 else 'north'], True)
        # Giebel schließen
        if x in (HX0, HX1) and HZ0 <= z <= HZ1:
            for yy in range(9, y):
                put(x, yy, z, WEISS, True)
for x in (HX0, HX1):
    put(x, 10, 7, SCHEIBE, True)
    put(x, 10, 8, SCHEIBE, True)
# Schornstein
for y in range(9, 15):
    put(24, y, 5, SCHORN, True)
# Einrichtung
put(20, 5, 6, BETT_F)
put(20, 5, 5, BETT_K)
put(21, 5, 5, FASS)
put(21, 6, 5, LATERNE)
put(25, 5, 5, OFEN)
put(25, 5, 6, KESSEL)
put(25, 5, 7, FASS)
put(25, 6, 7, LATERNE)
put(23, 5, 7, FSTUFE_O)
put(23, 5, 8, FSTUFE_O)
put(22, 5, 7, STUHL['west'])
put(24, 5, 8, STUHL['east'])
put(23, 6, 7, LATERNE)
put(20, 5, 10, REGAL)
put(21, 5, 10, KARTE)
put(25, 5, 10, LESEPULT)
for x in (21, 22, 23):
    put(x, 5, 9, TEPPICH)
# Bank vor dem Haus, Laternen an der Tür
put(18, 5, 6, STUHL['west'])
put(18, 5, 10, FASS)
put(18, 6, 10, LATERNE)
put(21, 5, 12, ZAUN)
put(21, 6, 12, LATERNE)

# =====================================================================
# Anleger: Felsabsatz am Sockeleingang, Steg nach Süden, zwei Boote, Netz, Bojen, Felsen im Meer
# =====================================================================
for x in range(5, 12):
    for z in (17, 18):
        if leer(x, 0, z):
            put(x, 0, z, fels(x, 0, z))
for x in (4, 12):
    for y in (0, 1):
        if leer(x, y, 17):
            put(x, y, 17, fels(x, y, 17))
# Steg x7..9 z19..30 auf Pfählen
for z in range(19, 31):
    for x in (7, 8, 9):
        put(x, 1, z, FSTUFE)
for z in (19, 22, 25, 28, 30):
    for x in (6, 10):
        put(x, 0, z, FSTAMM)
        put(x, 1, z, FSTAMM)
        if z in (22, 28):
            put(x, 2, z, ZAUN)
            put(x, 3, z, LATERNE)
for x in (7, 8, 9):
    put(x, 0, 30, FSTAMM)
# Fischernetz zum Trocknen, Kisten
put(10, 2, 25, ZAUN)
put(10, 3, 25, NETZ)
put(9, 2, 20, FASS)
put(7, 2, 21, FASS)
put(7, 3, 21, FASS)


def boot(a, b):
    """Ruderboot aus Blöcken, 2 breit, 5 lang (Bug im Norden)."""
    for x in (a, a + 1):
        put(x, 1, b, STUHL['north'])
        put(x, 1, b + 4, STUHL['south'])
        for z in range(b + 1, b + 4):
            put(x, 1, z, FSTUFE)
    put(a, 1, b + 2, FSTUFE_O, True)
    put(a + 1, 1, b + 2, FSTUFE_O, True)
    put(a - 1, 1, b + 2, ZAUN)


boot(4, 22)
boot(12, 24)
# Bojen und Felsen im Wasser
for (x, z, k) in ((15, 30, BOJE_R), (2, 31, BOJE_W), (28, 25, BOJE_R)):
    put(x, 0, z, k)
    put(x, 1, z, LATERNE if k == BOJE_R else BOJE_R)
for (x, z, h) in ((20, 26, 2), (21, 26, 1), (20, 27, 1), (30, 18, 2), (31, 18, 1), (30, 17, 1), (24, 31, 1), (25, 31, 0),
                  (1, 24, 1), (2, 25, 0), (14, 33, 0), (31, 6, 1), (32, 7, 0), (16, 21, 0)):
    for y in range(0, h + 1):
        if leer(x, y, z):
            put(x, y, z, fels(x, y, z))
# Pflanzen auf dem Plateau
for x in range(15, X):
    for z in range(0, 21):
        t = plateau_top(x, z) if not (x < 17 and z < 17) else None
        if t is not None and t >= 2 and G.get((x, t, z)) == GRASBLOCK and leer(x, t + 1, z):
            r = rausch(x, 7, z)
            if r < 30:
                put(x, t + 1, z, GRAESER)
            elif r < 38:
                put(x, t + 1, z, STRANDHAFER)
            elif r < 42:
                put(x, t + 1, z, STRAUCH)
# Meer
for x in range(X):
    for z in range(Z):
        if leer(x, 0, z):
            put(x, 0, z, MEER)

# =====================================================================
model = {'format': 1, 'size': {'x': X, 'y': Y, 'z': Z}, 'palette': P,
         'layers': [[''.join(G.get((x, y, z), '.') for x in range(X)) for z in range(Z)] for y in range(Y)]}
n = {}
for k in G.values():
    n[k] = n.get(k, 0) + 1
vorh = {e['key'] for e in P if 'vorhanden' in (e.get('flags') or [])}
print('Blöcke', sum(v for k, v in n.items() if k not in vorh), 'Blockarten', len([k for k in n if k not in vorh]))
P[:] = [e for e in P if e['key'] in n]
os.makedirs(ZIEL, exist_ok=True)
with open(os.path.join(ZIEL, 'model.json'), 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False)
    f.write('\n')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump({NAME[k]: v for k, v in sorted(n.items(), key=lambda t: -t[1])}, f, ensure_ascii=False, indent=0)
