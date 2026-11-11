"""Mediterrane Villa – Ausbau-Version (verfeinert wie ein Creator).

Leitbild: warm und etwas gealtert. Putz mit Farbverläufen, Terrakotta, Pergola mit Wein, Fensterläden mit Tiefe,
Zypressen und Olivenbäume. Leichte Gebrauchsspuren passen (Moos am Sockel, rissige Steine).

Die Grundidee bleibt: vier Flügel um einen Innenhof mit Brunnen und Säulengang, Fensterläden, Walmdach aus Ziegeln,
Zypressen am Eingang. Gleicher Ursprung wie die Grundversion (Haus x2..28 z2..28), das Grundstück wächst nach
Osten (Pergola, Olivenbäume) und Süden (Vorplatz mit Zypressen-Allee).

Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Boden.
Aufruf: python tools/ausbau_villa_mediterran.py builds/villa-mediterran/ausbau [zaehlung.json]
"""
import json
import os
import random
import sys

ZIEL = sys.argv[1]
X, Y, Z = 37, 18, 38

P = []
ZEICHEN = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&*+-/:;<=>?@^_~' +
               ''.join(chr(c) for c in range(0xC0, 0x100) if c not in (0xD7, 0xF7)))
RICHT = {'north': 'Norden', 'south': 'Süden', 'east': 'Osten', 'west': 'Westen'}
VIER = ('north', 'east', 'south', 'west')
GEGEN = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
SCHRITT = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}


def block(name, mc, farbe, flags=None):
    e = {'key': next(ZEICHEN), 'name': name, 'block': mc, 'color': farbe}
    if flags:
        e['flags'] = flags
    P.append(e)
    return e['key']


GRAS = block('Gras (vorhanden)', 'minecraft:grass_block', '#7c9a4c', ['vorhanden'])
# Putz in drei Tönen, Stein für Sockel und Ecken
PUTZ = block('Weiße Terrakotta', 'minecraft:white_terracotta', '#d4b6a6')
PUTZ2 = block('Glatter Sandstein', 'minecraft:smooth_sandstone', '#e0d3a3')
PUTZ3 = block('Sandstein', 'minecraft:sandstone', '#d8c88e')
STEIN = block('Steinziegel', 'minecraft:stone_bricks', '#8a8a86')
MOOSSTEIN = block('Bemooste Steinziegel', 'minecraft:mossy_stone_bricks', '#76835e')
RISS = block('Rissige Steinziegel', 'minecraft:cracked_stone_bricks', '#7e7d78')
GEMEISSELT = block('Gemeißelter Sandstein', 'minecraft:chiseled_sandstone', '#d9c78c')
COTTO = block('Terrakotta', 'minecraft:terracotta', '#a35f45')
ZIEGEL = block('Ziegelblock', 'minecraft:bricks', '#9a5444')
ZDACH = {r: block('Ziegeltreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:brick_stairs[facing=%s]' % r, '#a85a46') for r in VIER}
ZSTUFE = block('Ziegelstufe (unten)', 'minecraft:brick_slab[type=bottom]', '#9a5444')
GESIMS = {r: block('Sandsteintreppe (verkehrt, hohe Seite nach %s)' % RICHT[r], 'minecraft:sandstone_stairs[facing=%s,half=top]' % r, '#d8c88e')
          for r in VIER}
SSOBEN = block('Glatte-Sandstein-Stufe (oben)', 'minecraft:smooth_sandstone_slab[type=top]', '#e0d3a3')
SSUNTEN = block('Glatte-Sandstein-Stufe (unten)', 'minecraft:smooth_sandstone_slab[type=bottom]', '#e0d3a3')
SMAUER = block('Sandsteinmauer', 'minecraft:sandstone_wall', '#d8c88e')
SCHEIBE = block('Glasscheibe', 'minecraft:glass_pane', '#bfe6f2')
LADEN = {r: block('Wirrholzfalltür (Fensterladen, offen nach %s)' % RICHT[r], 'minecraft:warped_trapdoor[open=true,facing=%s]' % r, '#3a8e86')
         for r in VIER}
EICHE = block('Eichenholzbretter', 'minecraft:oak_planks', '#a7834f')
KIES = block('Kies', 'minecraft:gravel', '#8f8984')
WASSER = block('Wasser', 'minecraft:water', '#3f86f0')
LATERNE = block('Laterne', 'minecraft:lantern', '#f2b33d')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
TUER = {r: (block('Dunkle Eichentür (unten, Tür nach %s)' % RICHT[r], 'minecraft:dark_oak_door[half=lower,facing=%s]' % r, '#4a3221'),
            block('Dunkle Eichentür (oben, Tür nach %s)' % RICHT[r], 'minecraft:dark_oak_door[half=upper,facing=%s]' % r, '#4a3221', ['zweiter-teil']))
        for r in VIER}
TREPPE = {r: block('Dunkle Eichentreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:dark_oak_stairs[facing=%s]' % r, '#4a3221') for r in VIER}
STUHL = {r: block('Fichtentreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:spruce_stairs[facing=%s]' % r, '#7a5a36') for r in VIER}
TPLATTE = block('Dunkle-Eichen-Stufe (oben)', 'minecraft:dark_oak_slab[type=top]', '#4a3221')
BALKEN_X = block('Dunkler Eichenstamm (liegend, Ost-West)', 'minecraft:dark_oak_log[axis=x]', '#3e2c1c')
BALKEN_Z = block('Dunkler Eichenstamm (liegend, Nord-Süd)', 'minecraft:dark_oak_log[axis=z]', '#3e2c1c')
GELAENDER = block('Fichtenzaun', 'minecraft:spruce_fence', '#7a5a36')
FASS = block('Fass', 'minecraft:barrel[facing=up]', '#8a6438')
REGAL = block('Bücherregal', 'minecraft:bookshelf', '#9a7a4a')
RAEUCHER = block('Räucherofen (nach Osten)', 'minecraft:smoker[facing=east]', '#5d5a55')
KESSEL = block('Kessel mit Wasser', 'minecraft:water_cauldron[level=3]', '#4a4a50')
FEUER = block('Lagerfeuer', 'minecraft:campfire[lit=true]', '#e0782a')
TEPPICH = block('Roter Teppich', 'minecraft:red_carpet', '#9c3a2e')
TEPPICH2 = block('Oranger Teppich', 'minecraft:orange_carpet', '#d8782e')
WOLLE_W = block('Weiße Wolle', 'minecraft:white_wool', '#e9ecec')
LESEPULT = block('Lesepult', 'minecraft:lectern[facing=south]', '#8a6438')
BETT = {r: (block('Rotes Bett (Fußende, Kopf nach %s)' % RICHT[r], 'minecraft:red_bed[part=foot,facing=%s]' % r, '#9c3a2e'),
            block('Rotes Bett (Kopfende, Kopf nach %s)' % RICHT[r], 'minecraft:red_bed[part=head,facing=%s]' % r, '#9c3a2e', ['zweiter-teil']))
        for r in VIER}
# Pflanzen
KUEBEL = block('Orange Terrakotta', 'minecraft:orange_terracotta', '#a5542a')
ZITRONE = block('Blühendes Azaleenlaub', 'minecraft:flowering_azalea_leaves[persistent=true]', '#6c8f3a')
OLIVE_LAUB = block('Azaleenlaub', 'minecraft:azalea_leaves[persistent=true]', '#7d9a5a')
OLIVE_STAMM = block('Eichenstamm', 'minecraft:oak_log', '#6b5a3e')
STAEMMCHEN = block('Eichenzaun', 'minecraft:oak_fence', '#a7834f')
ZYP_STAMM = block('Fichtenstamm', 'minecraft:spruce_log', '#4f3b26')
ZYP_LAUB = block('Fichtenlaub', 'minecraft:spruce_leaves[persistent=true]', '#3f6340')
WEIN = block('Eichenlaub', 'minecraft:oak_leaves[persistent=true]', '#5f8a38')
BEEREN = block('Höhlenranken mit Leuchtbeeren', 'minecraft:cave_vines[berries=true]', '#e6a23c')
LAVENDEL = block('Zierlauch', 'minecraft:allium', '#9a6ad0')
ROSE = block('Mohn', 'minecraft:poppy', '#d23a2a')
T_ROSE = block('Topf mit Mohn', 'minecraft:potted_poppy', '#c4402e')
T_FARN = block('Topf mit Farn', 'minecraft:potted_fern', '#5c8c3a')
MOOS = block('Moosteppich', 'minecraft:moss_carpet', '#5a7a2e')
GRAESER = block('Kurzes Gras', 'minecraft:short_grass', '#6c9a40')

G = {}
NAME = {e['key']: e['name'] for e in P}
zufall = random.Random(11)


def put(x, y, z, k, ueber=False):
    if not (0 <= x < X and 0 <= y < Y and 0 <= z < Z):
        raise SystemExit('außerhalb: %s %s' % ((x, y, z), NAME[k]))
    alt = G.get((x, y, z))
    if alt is not None and alt != k and not ueber:
        raise SystemExit('Konflikt bei %s: %s gegen %s' % ((x, y, z), NAME[alt], NAME[k]))
    G[(x, y, z)] = k


def leer(x, y, z):
    return (x, y, z) not in G


def fuell(x0, x1, y0, y1, z0, z1, k, ueber=False):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(x, y, z, k, ueber)


def tuer(x, y, z, r):
    put(x, y, z, TUER[r][0], True)
    put(x, y + 1, z, TUER[r][1], True)


def bett(x, y, z, r):
    """x,y,z = Fußende, r = Richtung des Kopfendes"""
    dx, dz = SCHRITT[r]
    put(x, y, z, BETT[r][0])
    put(x + dx, y, z + dz, BETT[r][1])


def putz(x, y, z):
    """Putz mit leichtem Farbverlauf: unten mehr Sandstein, oben heller."""
    h = (x * 73856093 ^ y * 19349663 ^ z * 83492791) % 100
    if y <= 3:
        return PUTZ3 if h < 14 else PUTZ2 if h < 30 else PUTZ
    return PUTZ2 if h < 18 else PUTZ


def sockelstein(x, y, z):
    h = (x * 92821 ^ y * 68917 ^ z * 30011) % 100
    return MOOSSTEIN if h < 28 else RISS if h < 42 else STEIN


# =====================================================================
# Ebene 0
# =====================================================================
AUSSEN = lambda x, z: x in (2, 28) or z in (2, 28)
for x in range(2, 29):
    for z in range(2, 29):
        if AUSSEN(x, z):
            put(x, 0, z, sockelstein(x, 0, z))
        elif 11 <= x <= 19 and 11 <= z <= 19:
            put(x, 0, z, COTTO if (x + z) % 2 == 0 else PUTZ2)          # Innenhof im Schachbrett
        elif 9 <= x <= 21 and 9 <= z <= 21:
            put(x, 0, z, PUTZ2)                                            # Säulengang
        else:
            put(x, 0, z, COTTO)                                            # Cotto-Böden
# Moos in den Ecken des Innenhofs
for x, z in ((11, 11), (12, 11), (11, 12), (19, 19), (18, 19), (19, 18)):
    put(x, 1, z, MOOS)
# Vorplatz im Süden: Kies, Weg aus glattem Sandstein
for x in range(8, 23):
    for z in range(29, 38):
        put(x, 0, z, PUTZ2 if 14 <= x <= 16 else KIES)
# Terrasse im Osten unter der Pergola: Cotto
for x in range(29, 36):
    for z in range(8, 23):
        put(x, 0, z, COTTO if (x + z) % 3 else ZIEGEL)
for x in range(X):
    for z in range(Z):
        if leer(x, 0, z):
            put(x, 0, z, GRAS)

# =====================================================================
# Außenwände y1..y9 mit Sockel, Eckquadern, Gesims, Fenstern und Läden
# =====================================================================
FENSTER = (5, 9, 13, 17, 21, 25)
for y in range(1, 10):
    for x in range(2, 29):
        for z in range(2, 29):
            if not AUSSEN(x, z):
                continue
            ecke = x in (2, 28) and z in (2, 28)
            neben_ecke = (x in (3, 27) and z in (2, 28)) or (z in (3, 27) and x in (2, 28))
            if y == 1:
                k = sockelstein(x, y, z)
            elif y == 5:
                k = PUTZ2                                       # Geschossband
            elif ecke or (neben_ecke and y % 2 == 0):
                k = PUTZ2                                       # Eckquader
            else:
                k = putz(x, y, z)
            put(x, y, z, k)
# Fenster, Stürze, Sohlbänke, Läden
SEITEN = (('north', lambda p: (p, 2)), ('south', lambda p: (p, 28)), ('west', lambda p: (2, p)), ('east', lambda p: (28, p)))
for seite, pos in SEITEN:
    dx, dz = SCHRITT[seite]
    for p in FENSTER:
        for (y0, y1) in ((2, 3), (7, 8)):
            x, z = pos(p)
            if seite == 'south' and y0 == 2 and 9 <= p <= 21:
                continue                                    # dort ist die Loggia
            if seite == 'east' and y0 == 2 and p in (13, 17):
                continue                                    # Terrassentür
            for y in (y0, y1):
                put(x, y, z, SCHEIBE, True)
            put(x, y1 + 1, z, PUTZ2, True)                  # Sturz
            put(x + dx, y0 - 1, z + dz, SSOBEN)             # Sohlbank
            # Läden links und rechts, aufgeklappt an der Wand
            qx, qz = (1, 0) if seite in ('north', 'south') else (0, 1)
            for s in (-1, 1):
                for y in (y0, y1):
                    put(x + dx + s * qx, y, z + dz + s * qz, LADEN[seite])
            if y0 == 7 and (p + (0 if seite in ('north', 'south') else 2)) % 8 == 1:
                put(x + dx, y0, z + dz, T_ROSE)             # Blumen auf jeder zweiten Sohlbank oben
# Gesims über dem Erdgeschoss (ragt einen Block heraus)
for x in range(1, 30):
    for z in range(1, 30):
        if x in (1, 29) or z in (1, 29):
            if x in (1, 29) and z in (1, 29):
                put(x, 5, z, SSOBEN)
            elif z == 1:
                put(x, 5, z, GESIMS['south'])
            elif z == 29:
                put(x, 5, z, GESIMS['north'])
            elif x == 1:
                put(x, 5, z, GESIMS['east'])
            else:
                put(x, 5, z, GESIMS['west'])

# ---- Loggia im Süden: Bogengang x9..21, dahinter Wand z25 mit Haustür ----
for x in range(9, 22):
    for y in range(1, 5):
        G.pop((x, y, 28), None)
for x in (9, 13, 17, 21):
    for y in (1, 2, 3):
        put(x, y, 28, PUTZ2)
    put(x, 4, 28, GEMEISSELT)
for a in (9, 13, 17):
    put(a + 1, 4, 28, GESIMS['west'])
    put(a + 2, 4, 28, SSOBEN)
    put(a + 3, 4, 28, GESIMS['east'])
for x in range(9, 22):
    for y in range(1, 5):
        put(x, y, 25, putz(x, y, 25))
    put(x, 0, 26, COTTO, True)
    put(x, 0, 27, COTTO, True)
    put(x, 0, 28, PUTZ2, True)
tuer(15, 1, 25, 'north')
for x in (11, 19):
    put(x, 2, 25, SCHEIBE, True)
    put(x, 3, 25, SCHEIBE, True)
for x in (11, 15, 19):
    put(x, 4, 27, HAENGE)
for x in (10, 20):
    put(x, 1, 26, KUEBEL)
    put(x, 2, 26, STAEMMCHEN)
    put(x, 3, 26, ZITRONE)
put(13, 1, 26, STUHL['south'])
put(17, 1, 26, STUHL['south'])
# Terrassentür nach Osten (Doppeltür) mit Sturz
tuer(28, 1, 15, 'west')
tuer(28, 1, 14, 'west')
tuer(28, 1, 16, 'west')
put(28, 4, 15, GEMEISSELT, True)

# =====================================================================
# Innenhof: Säulengang mit Bögen, Brunnen
# =====================================================================
# Innenwand Erdgeschoss x8/x22, z8/z22 (wie Grundversion), Türen in der Mitte, Fenster
for y in range(1, 5):
    for x in range(8, 23):
        for z in range(8, 23):
            if x in (8, 22) or z in (8, 22):
                put(x, y, z, putz(x, y, z))
for (x, z), r in (((15, 8), 'south'), ((15, 22), 'north'), ((8, 15), 'east'), ((22, 15), 'west')):
    tuer(x, 1, z, r)
for x, z in ((11, 8), (19, 8), (11, 22), (19, 22), (8, 11), (8, 19), (22, 11), (22, 19)):
    put(x, 2, z, SCHEIBE, True)
    put(x, 3, z, SCHEIBE, True)
# Säulen und Bögen auf dem Ring x10/x20, z10/z20
for a in (10, 20):
    for b in (10, 15, 20):
        for (x, z) in ((a, b), (b, a)):
            for y in (1, 2, 3):
                put(x, y, z, PUTZ2)
            put(x, 4, z, GEMEISSELT)
for a in (10, 20):
    for b0 in (10, 15):
        # Bogen von b0 bis b0+5: Treppe, Stufe, Stufe, Treppe
        for (x, z, r) in ((a, b0 + 1, 'north'), (a, b0 + 4, 'south'), (b0 + 1, a, 'west'), (b0 + 4, a, 'east')):
            put(x, 4, z, GESIMS[r])
        for c in (b0 + 2, b0 + 3):
            put(a, 4, c, SSOBEN)
            put(c, 4, a, SSOBEN)
for x, z in ((9, 12), (9, 18), (21, 12), (21, 18), (12, 9), (18, 9), (12, 21), (18, 21)):
    put(x, 4, z, HAENGE)
# Brunnen: achteckiges Becken, Säule, Schale; das Wasser oben fließt über die Schale ins Becken
for x in range(12, 19):
    for z in range(12, 19):
        if x in (12, 18) and z in (12, 18):
            continue
        innen = 13 <= x <= 17 and 13 <= z <= 17 and not (x in (13, 17) and z in (13, 17))
        put(x, 1, z, WASSER if innen else PUTZ2)
G[(15, 1, 15)] = PUTZ2
put(15, 2, 15, PUTZ2)
put(15, 3, 15, GEMEISSELT)
for x in (14, 15, 16):
    for z in (14, 15, 16):
        if (x, z) != (15, 15):
            put(x, 3, z, SSUNTEN)
put(15, 4, 15, WASSER)
# Bänke und Kübel im Hof
for x in (13, 17):
    put(x, 1, 11, STUHL['north'])
    put(x, 1, 19, STUHL['south'])
for x, z in ((11, 15), (19, 15)):
    put(x, 1, z, KUEBEL)
    put(x, 2, z, STAEMMCHEN)
    put(x, 3, z, ZITRONE)

# =====================================================================
# Decke y5 und Obergeschoss y6..y9
# =====================================================================
TREPPENAUGE = {(11, 4), (12, 4), (13, 4)}
for x in range(2, 29):
    for z in range(2, 29):
        if AUSSEN(x, z):
            continue                                          # schon gesetzt (Geschossband)
        if 11 <= x <= 19 and 11 <= z <= 19:
            continue                                          # offener Hof
        if (x, z) in TREPPENAUGE or (x, z) == (14, 4):
            continue
        rand = x in (10, 20) and 10 <= z <= 20 or z in (10, 20) and 10 <= x <= 20
        put(x, 5, z, PUTZ2 if rand else EICHE)
# Innenwand des Obergeschosses zum Hof (Ring x10/x20, z10/z20) mit Fenstern und Läden
for y in range(6, 10):
    for x in range(10, 21):
        for z in range(10, 21):
            if x in (10, 20) or z in (10, 20):
                put(x, y, z, putz(x, y, z))
for p in (13, 17):
    for (x, z, r) in ((p, 10, 'south'), (p, 20, 'north'), (10, p, 'east'), (20, p, 'west')):
        put(x, 7, z, SCHEIBE, True)
        put(x, 8, z, SCHEIBE, True)
        dx, dz = SCHRITT[r]
        qx, qz = (1, 0) if r in ('north', 'south') else (0, 1)
        for s in (-1, 1):
            for y in (7, 8):
                put(x + dx + s * qx, y, z + dz + s * qz, LADEN[r])
        put(x + dx, 6, z + dz, SSOBEN)
        put(x + dx, 7, z + dz, T_ROSE)

# ---- Innenwände ----
def wand(x0, x1, y0, y1, z0, z1):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(x, y, z, PUTZ)


# Erdgeschoss
wand(3, 7, 1, 4, 8, 8)
wand(3, 7, 1, 4, 14, 14)
wand(3, 7, 1, 4, 22, 22)
wand(8, 8, 1, 4, 3, 7)
wand(22, 22, 1, 4, 3, 7)
wand(8, 8, 1, 4, 23, 27)
wand(22, 22, 1, 4, 23, 27)
wand(23, 27, 1, 4, 8, 8)
wand(23, 27, 1, 4, 22, 22)
for (x, z), r in (((5, 8), 'south'), ((5, 14), 'south'), ((7, 22), 'south'), ((8, 5), 'east'), ((22, 5), 'west'),
                  ((8, 24), 'east'), ((22, 24), 'west'), ((25, 8), 'south'), ((25, 22), 'north')):
    tuer(x, 1, z, r)
# Obergeschoss: Flur rund um den Hof (x9 / x21 / z9 / z21), Zimmer außen herum wie unten
for y in range(6, 10):
    for x in range(8, 23):
        for z in range(8, 23):
            if (x in (8, 22) or z in (8, 22)) and not (10 <= x <= 20 and 10 <= z <= 20):
                put(x, y, z, PUTZ)
wand(3, 7, 6, 9, 8, 8)
wand(3, 7, 6, 9, 22, 22)
wand(23, 27, 6, 9, 8, 8)
wand(23, 27, 6, 9, 22, 22)
wand(3, 7, 6, 9, 15, 15)
wand(8, 8, 6, 9, 3, 7)
wand(22, 22, 6, 9, 3, 7)
wand(8, 8, 6, 9, 23, 27)
wand(22, 22, 6, 9, 23, 27)
for (x, z), r in (((15, 8), 'south'), ((8, 5), 'west'), ((22, 5), 'east'), ((8, 12), 'west'), ((8, 18), 'west'),
                  ((22, 15), 'east'), ((15, 22), 'north'), ((8, 25), 'west'), ((22, 25), 'east')):
    tuer(x, 6, z, r)

# =====================================================================
# Einrichtung Erdgeschoss
# =====================================================================
# Treppe im Nordflügel x10..14 entlang z4, steigt nach Osten; darunter Fässer
for i, x in enumerate(range(10, 15)):
    put(x, 1 + i, 4, TREPPE['east'])
    for y in range(1, 1 + i):
        put(x, y, 4, FASS)
for x in (11, 12, 13):
    put(x, 6, 5, GELAENDER)
put(10, 6, 4, GELAENDER)
put(12, 4, 6, HAENGE)
put(17, 1, 3, T_FARN)
put(20, 1, 6, REGAL)
put(20, 2, 6, REGAL)
put(19, 1, 3, STUHL['north'])
# Küche x3..7 z9..13: Zeile an der Westwand, Herd, Spüle, Tisch
for z, k in ((9, RAEUCHER), (10, FASS), (11, KESSEL), (12, FASS), (13, FASS)):
    put(3, 1, z, k)
for z in (10, 11, 12):
    put(5, 1, z, TPLATTE)
put(6, 1, 10, STUHL['east'])
put(6, 1, 12, STUHL['east'])
put(5, 4, 11, HAENGE)
put(7, 1, 13, KUEBEL)
put(7, 2, 13, T_FARN)
# Speisekammer x3..7 z3..7
for z in (3, 4, 5, 6, 7):
    put(3, 1, z, FASS)
    put(3, 2, z, FASS)
# Esszimmer x3..7 z15..21: langer Tisch, Stühle, Leuchter
for z in range(16, 21):
    put(5, 1, z, TPLATTE)
    put(4, 1, z, STUHL['west'])
    put(6, 1, z, STUHL['east'])
put(5, 4, 17, HAENGE)
put(5, 4, 19, HAENGE)
put(3, 1, 21, REGAL)
put(7, 1, 15, KUEBEL)
put(7, 2, 15, T_ROSE)
# Salon x3..7 z23..27: Kamin an der Innenwand, Sofa, Sessel, Teppich
for x in (4, 5, 6):
    for y in (1, 2, 3, 4):
        put(x, y, 23, ZIEGEL)
G[(5, 1, 23)] = FEUER
for x in (4, 5, 6):
    put(x, 1, 26, STUHL['south'])
put(3, 1, 25, STUHL['west'])
put(7, 1, 25, STUHL['east'])
for x, z in ((4, 24), (5, 24), (6, 24), (4, 25), (6, 25)):
    put(x, 1, z, TEPPICH)
put(5, 1, 25, TPLATTE)
put(7, 1, 27, KUEBEL)
put(7, 2, 27, STAEMMCHEN)
put(7, 3, 27, ZITRONE)
put(5, 4, 25, HAENGE)
# Diele x9..21 z23..24
for x in (10, 20):
    put(x, 1, 23, KUEBEL)
    put(x, 2, 23, T_FARN)
put(12, 1, 23, STUHL['north'])
put(18, 1, 23, STUHL['north'])
for x in range(13, 18):
    put(x, 1, 24, TEPPICH)
put(15, 4, 23, HAENGE)
# Arbeitszimmer x23..27 z23..27
for z in (25, 26, 27):
    for y in (1, 2, 3):
        put(23, y, z, REGAL)
put(26, 1, 24, TPLATTE)
put(26, 1, 25, TPLATTE)
put(25, 1, 25, STUHL['west'])
put(26, 2, 24, LATERNE)
put(24, 1, 23, LESEPULT)
put(27, 1, 27, KUEBEL)
put(27, 2, 27, T_FARN)
# Bibliothek/Salone im Ostflügel x23..27 z9..21: Kamin, Sessel, Bücher
for z in range(9, 14):
    for y in (1, 2, 3):
        put(23, y, z, REGAL)
for z in range(17, 22):
    for y in (1, 2, 3):
        put(23, y, z, REGAL)
for x in (24, 25, 26):
    for y in (1, 2, 3, 4):
        put(x, y, 9, ZIEGEL)
G[(25, 1, 9)] = FEUER
for x in (24, 26):
    put(x, 1, 12, STUHL['south'])
put(25, 1, 11, TPLATTE)
for x, z in ((24, 10), (25, 10), (26, 10), (24, 11), (26, 11)):
    put(x, 1, z, TEPPICH2)
put(25, 4, 11, HAENGE)
put(25, 4, 18, HAENGE)
put(26, 1, 19, STUHL['east'])
put(26, 1, 18, LATERNE)
# Waschküche/WC x23..27 z3..7
put(27, 1, 3, KESSEL)
put(27, 1, 4, FASS)
put(25, 1, 3, KESSEL)

# =====================================================================
# Einrichtung Obergeschoss
# =====================================================================
# Galerie im Nordflügel x9..21 z3..7: Treppe kommt bei x14 an, Leseecke
for x in (18, 19, 20, 21):
    put(x, 6, 3, REGAL)
    put(x, 7, 3, REGAL)
put(19, 6, 6, STUHL['south'])
put(20, 6, 6, STUHL['south'])
put(20, 6, 5, TPLATTE)
put(20, 7, 5, LATERNE)
put(9, 6, 7, KUEBEL)
put(9, 7, 7, T_FARN)
# Bad Nordwest x3..7 z3..7
put(4, 6, 3, KESSEL)
put(5, 6, 3, KESSEL)
put(7, 6, 7, KESSEL)
put(3, 6, 7, T_FARN)
for x in (4, 5):
    put(x, 6, 5, TEPPICH2)
# Arbeitszimmer Nordost x23..27 z3..7
for z in (3, 4):
    for y in (6, 7):
        put(27, y, z, REGAL)
put(24, 6, 3, TPLATTE)
put(25, 6, 3, TPLATTE)
put(24, 6, 4, STUHL['south'])
put(25, 7, 3, LATERNE)
put(26, 6, 7, STUHL['east'])
# Kinderzimmer Westflügel x3..7 z9..14
bett(5, 6, 10, 'west')
bett(5, 6, 13, 'west')
put(3, 6, 11, FASS)
put(3, 7, 11, LATERNE)
put(7, 6, 14, REGAL)
for x, z in ((5, 11), (6, 11), (5, 12), (6, 12)):
    put(x, 6, z, TEPPICH2)
# Gästezimmer Westflügel x3..7 z16..21
bett(5, 6, 18, 'west')
bett(5, 6, 19, 'west')
put(3, 6, 17, FASS)
put(3, 7, 17, LATERNE)
put(3, 6, 20, FASS)
put(7, 6, 21, KUEBEL)
put(7, 7, 21, T_ROSE)
# Wohnzimmer oben im Ostflügel x23..27 z9..21
for z in (13, 14, 15, 16, 17):
    put(27, 6, z, STUHL['east'])
put(25, 6, 15, TPLATTE)
put(25, 7, 15, T_ROSE)
for x, z in ((24, 14), (24, 15), (24, 16), (25, 14), (25, 16), (26, 14), (26, 15), (26, 16)):
    put(x, 6, z, TEPPICH)
for z in (10, 11):
    for y in (6, 7):
        put(23, y, z, REGAL)
put(23, 6, 20, KUEBEL)
put(23, 7, 20, T_FARN)
# Hauptschlafzimmer Südflügel x9..21 z23..27: Doppelbett, Nachttische, Sitzecke, Schrank
bett(14, 6, 26, 'south')
bett(15, 6, 26, 'south')
for x in (13, 16):
    put(x, 6, 27, FASS)
    put(x, 7, 27, LATERNE)
for x in (13, 15, 16):
    put(x, 6, 25, TEPPICH)
put(10, 6, 23, STUHL['west'])
put(10, 6, 24, STUHL['west'])
put(11, 6, 23, TPLATTE)
for z in (23, 24, 25, 26, 27):
    put(21, 6, z, FASS)
put(19, 6, 23, KUEBEL)
put(19, 7, 23, T_FARN)
# Bad Südwest x3..7 z23..27 und Bad Südost x23..27 z23..27
put(3, 6, 26, KESSEL)
put(3, 6, 27, KESSEL)
put(7, 6, 23, KESSEL)
put(26, 6, 26, KESSEL)
put(26, 6, 27, KESSEL)
put(23, 6, 23, KESSEL)
put(27, 6, 23, T_FARN)

# =====================================================================
# Dach: flaches toskanisches Walmdach aus Ziegelstufen (halbe Neigung), Überstand 1 Block,
# darüber ein kleiner Aussichtsturm (Belvedere) über der Loggia
# =====================================================================
ZOBEN = block('Ziegelstufe (oben)', 'minecraft:brick_slab[type=top]', '#a85a46')
LEITER = block('Leiter (an der Nordseite)', 'minecraft:ladder[facing=south]', '#9a7a4a')
NAME = {e['key']: e['name'] for e in P}
TURM = (13, 17, 24, 28)


def dach_h(x, z):
    if not (1 <= x <= 29 and 1 <= z <= 29):
        return None
    if 12 <= x <= 18 and 12 <= z <= 18:
        return None
    aussen = min(x - 1, 29 - x, z - 1, 29 - z)
    innen = max(12 - x, x - 18, 12 - z, z - 18) - 1
    return min(aussen, innen)


def im_turm(x, z):
    return TURM[0] <= x <= TURM[1] and TURM[2] <= z <= TURM[3]


for x in range(1, 30):
    for z in range(1, 30):
        h = dach_h(x, z)
        if h is None or im_turm(x, z):
            continue
        put(x, 10 + h // 2, z, ZOBEN if h % 2 else ZSTUFE, True)
# Zwei Schornsteine auf dem First
for (x, z) in ((6, 18), (20, 6)):
    for y in range(11, 15):
        put(x, y, z, ZIEGEL, True)
    put(x, 15, z, ZSTUFE)

# Belvedere x13..17 z24..28: Ecken mit Quadern, auf jeder Seite ein Bogen mit Brüstung
for y in range(10, 15):
    for x in range(TURM[0], TURM[1] + 1):
        for z in range(TURM[2], TURM[3] + 1):
            rand = x in (TURM[0], TURM[1]) or z in (TURM[2], TURM[3])
            if y == 10:
                put(x, y, z, PUTZ2 if rand else EICHE, True)
            elif rand:
                ecke = x in (TURM[0], TURM[1]) and z in (TURM[2], TURM[3])
                put(x, y, z, PUTZ2 if (ecke or y == 14) else putz(x, y, z), True)
for seite in VIER:
    for i, c in enumerate((14, 15, 16)):
        x, z = {'north': (c, 24), 'south': (c, 28), 'west': (13, c + 12), 'east': (17, c + 12)}[seite]
        G[(x, 11, z)] = SMAUER
        G.pop((x, 12, z), None)
        quer = 'west' if seite in ('north', 'south') else 'north'
        G[(x, 13, z)] = (GESIMS[quer] if i == 0 else SSOBEN if i == 1 else GESIMS[GEGEN[quer]])
# Dach des Belvedere
for x in range(12, 19):
    for z in range(23, 30):
        h = min(x - 12, 18 - x, z - 23, 29 - z)
        put(x, 15 + h // 2, z, ZOBEN if h % 2 else ZSTUFE, True)
put(15, 11, 26, STUHL['north'])
put(16, 11, 27, LATERNE)
# Leiter vom Schlafzimmer hinauf, an einem Pfeiler
for y in range(6, 10):
    put(14, y, 24, PUTZ, True)
for y in range(6, 11):
    G[(14, y, 25)] = LEITER
# Ranken am Haus (leichte Gebrauchsspuren)
RANKE_W = block('Ranken (an der Ostseite)', 'minecraft:vine[east=true]', '#4f7a2e')
RANKE_N = block('Ranken (an der Südseite)', 'minecraft:vine[south=true]', '#4f7a2e')
RANKE_S = block('Ranken (an der Nordseite)', 'minecraft:vine[north=true]', '#4f7a2e')
NAME = {e['key']: e['name'] for e in P}
for y in range(1, 7):
    if leer(1, y, 3):
        put(1, y, 3, RANKE_W)
    if leer(3, y, 1):
        put(3, y, 1, RANKE_N)
for y in range(1, 5):
    for x in (27,):
        if leer(x, y, 29):
            put(x, y, 29, RANKE_S)

# =====================================================================
# Pergola mit Wein im Osten, Olivenbäume, Zypressen-Allee, Lavendel
# =====================================================================
for z in (9, 13, 17, 21):
    for x in (30, 35):
        for y in (1, 2, 3):
            put(x, y, z, SMAUER)
    for x in range(29, 36):
        put(x, 4, z, BALKEN_X)
for x in (30, 35):
    for z in range(9, 22):
        if leer(x, 4, z):
            put(x, 4, z, BALKEN_Z)
for x in range(30, 36):
    for z in range(9, 22):
        if zufall.random() < .5:
            put(x, 5, z, WEIN)
            if G.get((x, 4, z)) is None and zufall.random() < .35 and 31 <= x <= 34:
                put(x, 4, z, WEIN)
for x in range(31, 35):
    for z in range(10, 21):
        if G.get((x, 4, z)) is not None and leer(x, 3, z) and zufall.random() < .3 and x in (31, 34):
            put(x, 3, z, BEEREN)
# Langer Tisch unter der Pergola
for z in range(12, 19):
    put(32, 1, z, TPLATTE)
    put(33, 1, z, TPLATTE)
    put(31, 1, z, STUHL['west'])
    put(34, 1, z, STUHL['east'])
for z in (10, 20):
    put(32, 1, z, KUEBEL)
    put(32, 2, z, STAEMMCHEN)
    put(32, 3, z, ZITRONE)
put(32, 2, 15, LATERNE)


def olive(x, z):
    put(x, 1, z, OLIVE_STAMM)
    put(x, 2, z, OLIVE_STAMM)
    put(x + 1, 3, z, OLIVE_STAMM)
    put(x - 1, 3, z + 1, OLIVE_STAMM)
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            for y in (4, 5):
                if abs(dx) + abs(dz) <= (3 if y == 4 else 2) and leer(x + dx, y, z + dz):
                    if (dx * 7 + dz * 3 + y) % 5:
                        put(x + dx, y, z + dz, OLIVE_LAUB)
    put(x, 6, z, OLIVE_LAUB)


def zypresse(x, z, h=7):
    put(x, 1, z, ZYP_STAMM)
    for y in range(2, h + 1):
        put(x, y, z, ZYP_LAUB)
        if 3 <= y <= h - 2:
            for r in VIER:
                dx, dz = SCHRITT[r]
                if leer(x + dx, y, z + dz):
                    put(x + dx, y, z + dz, ZYP_LAUB)
    put(x, h + 1, z, ZYP_LAUB)


olive(32, 28)
olive(33, 34)
olive(32, 3)
for x, z, h in ((3, 31, 7), (7, 31, 8), (23, 31, 8), (27, 31, 7)):
    zypresse(x, z, h)
for z in (30, 33, 36):
    zypresse(11, z, 6)
    zypresse(19, z, 6)
# Tor mit Pfeilern und Laternen
for x in (13, 17):
    for y in (1, 2):
        put(x, y, 37, SMAUER)
    put(x, 3, 37, LATERNE)
# Lavendel vor dem Haus und am Vorplatz
for x in list(range(3, 9)) + list(range(22, 28)):
    put(x, 1, 30, LAVENDEL)
for z in range(30, 37):
    put(9, 1, z, LAVENDEL if z % 2 else ROSE)
    put(21, 1, z, LAVENDEL if z % 2 else ROSE)
for x, z in ((1, 6), (1, 12), (1, 20), (0, 26), (30, 25), (29, 31), (35, 30), (34, 6), (30, 1)):
    if leer(x, 1, z):
        put(x, 1, z, GRAESER)

# =====================================================================
model = {'format': 1, 'size': {'x': X, 'y': Y, 'z': Z}, 'palette': P,
         'layers': [[''.join(G.get((x, y, z), '.') for x in range(X)) for z in range(Z)] for y in range(Y)]}
NAME = {e['key']: e['name'] for e in P}
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
