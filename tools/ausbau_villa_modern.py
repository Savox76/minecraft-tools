"""Moderne Villa – Ausbau-Version (verfeinert wie ein Creator).

Leitbild: hell und reduziert, aber eigenständig neben der Villa am Wasser. Betonsockel, viel helles Holz (auch als
Fensterpfosten), schwarz nur als Akzent (Kamin, Poller), Garten mit Rasen, Birken und Pool, eingerichtete Räume. Ohne Steg und ohne Palmen.

Grundidee der Grundversion bleibt: verglastes Erdgeschoss, Obergeschoss ragt 8 Blöcke nach Osten über die
Terrasse, Dachterrasse über dem Erdgeschoss mit Glasgeländer, Pool im Südosten, Birken im Südwesten.
Gleicher Ursprung und gleiche Ebenen wie die Grundversion (Erdgeschoss x2..18 z5..16, Obergeschoss x8..26 z3..14).

Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Boden.
Aufruf: python tools/ausbau_villa_modern.py builds/villa-modern/ausbau [zaehlung.json]
"""
import json
import os
import sys

ZIEL = sys.argv[1]
X, Y, Z = 31, 13, 31

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


# ---------- Gelände ----------
GRAS = block('Gras (vorhanden)', 'minecraft:grass_block', '#6f9e48', ['vorhanden'])
# ---------- Rohbau ----------
BETON = block('Weißer Beton', 'minecraft:white_concrete', '#e3e6e6')
SOCKEL = block('Hellgrauer Beton', 'minecraft:light_gray_concrete', '#8e8e86')
SCHWARZ = block('Polierter Schwarzstein', 'minecraft:polished_blackstone', '#35303a')
HOLZ = block('Entrindeter Eichenstamm', 'minecraft:stripped_oak_log[axis=y]', '#b8945a')
BALKEN_X = block('Entrindeter Eichenstamm (liegend, Ost-West)', 'minecraft:stripped_oak_log[axis=x]', '#b8945a')
BALKEN_Z = block('Entrindeter Eichenstamm (liegend, Nord-Süd)', 'minecraft:stripped_oak_log[axis=z]', '#b8945a')
EICHE = block('Eichenholzbretter', 'minecraft:oak_planks', '#a7834f')
FICHTE = block('Fichtenholzbretter', 'minecraft:spruce_planks', '#7a5a36')
GSTEIN = block('Glatter Stein', 'minecraft:smooth_stone', '#a3a6a8')
SOBEN = block('Glatte-Stein-Stufe (oben)', 'minecraft:smooth_stone_slab[type=top]', '#a9acae')
SCHEIBE = block('Glasscheibe', 'minecraft:glass_pane', '#bfe6f2')
MATT = block('Weiße Buntglasscheibe', 'minecraft:white_stained_glass_pane', '#f2f4f4')
GLAS = block('Glas', 'minecraft:glass', '#a9dcec')
WASSER = block('Wasser', 'minecraft:water', '#3f86f0')
SEELAT = block('Seelaterne', 'minecraft:sea_lantern', '#cfe8e0')
LATERNE = block('Laterne', 'minecraft:lantern', '#f2b33d')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
POLLER = block('Polierte-Schwarzstein-Mauer', 'minecraft:polished_blackstone_wall', '#35303a')
FEUER = block('Lagerfeuer', 'minecraft:campfire[lit=true]', '#e0782a')
# ---------- Türen und Treppen ----------
TUER = {r: (block('Eichentür (unten, Tür nach %s)' % RICHT[r], 'minecraft:oak_door[half=lower,facing=%s]' % r, '#a7834f'),
            block('Eichentür (oben, Tür nach %s)' % RICHT[r], 'minecraft:oak_door[half=upper,facing=%s]' % r, '#a7834f', ['zweiter-teil']))
        for r in ('north', 'east', 'west')}
TREPPE = {r: block('Eichentreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:oak_stairs[facing=%s]' % r, '#a7834f') for r in VIER}
SOFA = {r: block('Polierte-Diorit-Treppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:polished_diorite_stairs[facing=%s]' % r, '#d6d6d4')
        for r in VIER}
# ---------- Möbel ----------
TPLATTE = block('Eichenstufe (oben)', 'minecraft:oak_slab[type=top]', '#a7834f')
EUNTEN = block('Eichenstufe (unten)', 'minecraft:oak_slab[type=bottom]', '#a7834f')
TISCH = block('Eichenfalltür (unten)', 'minecraft:oak_trapdoor[half=bottom]', '#a7834f')
HOCKER = block('Eichenzaun', 'minecraft:oak_fence', '#a7834f')
SITZ = block('Eichen-Druckplatte', 'minecraft:oak_pressure_plate', '#a7834f')
TEPPICH = block('Hellgrauer Teppich', 'minecraft:light_gray_carpet', '#9d9d97')
WTEPPICH = block('Weißer Teppich', 'minecraft:white_carpet', '#eaeded')
WOLLE = block('Weiße Wolle', 'minecraft:white_wool', '#e9ecec')
FASS = block('Fass', 'minecraft:barrel[facing=up]', '#8a6438')
RAEUCHER = block('Räucherofen', 'minecraft:smoker[facing=south]', '#5d5a55')
GRILL = block('Räucherofen (Grill, nach Osten)', 'minecraft:smoker[facing=east]', '#5d5a55')
KESSEL = block('Kessel mit Wasser', 'minecraft:water_cauldron[level=3]', '#4a4a50')
REGAL = block('Bücherregal', 'minecraft:bookshelf', '#9a7a4a')
TV = block('Schwarzer Beton', 'minecraft:black_concrete', '#16171b')
BETT = {'east': (block('Hellgraues Bett (Fußende, Kopf nach Osten)', 'minecraft:light_gray_bed[part=foot,facing=east]', '#9d9d97'),
                 block('Hellgraues Bett (Kopfende, Kopf nach Osten)', 'minecraft:light_gray_bed[part=head,facing=east]', '#9d9d97', ['zweiter-teil'])),
        'north': (block('Weißes Bett (Fußende)', 'minecraft:white_bed[part=foot,facing=north]', '#e9ecec'),
                  block('Weißes Bett (Kopfende)', 'minecraft:white_bed[part=head,facing=north]', '#e9ecec', ['zweiter-teil']))}
# ---------- Pflanzen ----------
MOOS = block('Moosblock', 'minecraft:moss_block', '#5a7a2e')
LAUB = block('Birkenlaub', 'minecraft:birch_leaves[persistent=true]', '#7fa04e')
STAMM = block('Birkenstamm', 'minecraft:birch_log', '#d9d6c6')
AZALEE = block('Blühendes Azaleenlaub', 'minecraft:flowering_azalea_leaves[persistent=true]', '#6c8f3a')
GRAESER = block('Kurzes Gras', 'minecraft:short_grass', '#6c9a40')
FARN = block('Farn', 'minecraft:fern', '#5c8c3a')
MARGERITE = block('Margerite', 'minecraft:oxeye_daisy', '#f0efe0')
KORNBLUME = block('Kornblume', 'minecraft:cornflower', '#4f73d6')
ALLIUM = block('Zierlauch', 'minecraft:allium', '#b77ad8')
TULPE = block('Weiße Tulpe', 'minecraft:white_tulip', '#f1f1ea')
T_BAMBUS = block('Topf mit Bambus', 'minecraft:potted_bamboo', '#7fae3a')
T_FARN = block('Topf mit Farn', 'minecraft:potted_fern', '#5c8c3a')
T_AZALEE = block('Topf mit blühender Azalee', 'minecraft:potted_flowering_azalea_bush', '#7a9a3a')

G = {}
NAME = {e['key']: e['name'] for e in P}


def put(x, y, z, k, ueber=False):
    if not (0 <= x < X and 0 <= y < Y and 0 <= z < Z):
        raise SystemExit('außerhalb: %s' % ((x, y, z),))
    alt = G.get((x, y, z))
    if alt is not None and alt != k and not ueber:
        raise SystemExit('Konflikt bei %s: %s gegen %s' % ((x, y, z), NAME[alt], NAME[k]))
    G[(x, y, z)] = k


def fuell(x0, x1, y0, y1, z0, z1, k, ueber=False):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(x, y, z, k, ueber)


def leer(x, y, z):
    return (x, y, z) not in G


def tuer(x, y, z, r):
    put(x, y, z, TUER[r][0], True)
    put(x, y + 1, z, TUER[r][1], True)


def bett(x, y, z, r):
    fuss, kopf = BETT[r]
    dx, dz = {'east': (1, 0), 'north': (0, -1)}[r]
    put(x, y, z, fuss)
    put(x + dx, y, z + dz, kopf)


# =====================================================================
# Ebene 0: Rasen, Böden, Terrassen, Pool, Wege
# =====================================================================
# Erdgeschoss: Sockel aus hellgrauem Beton unter den Wänden, innen Eichenboden
for x in range(2, 19):
    for z in range(5, 17):
        put(x, 0, z, SOCKEL if x in (2, 18) or z in (5, 16) else EICHE)
# Eingangsnische x4..6 z16: Boden aus glattem Stein
for x in (4, 5, 6):
    put(x, 0, 16, GSTEIN, True)
# Südterrasse vor dem Haus x2..17 z17..19 aus glattem Stein
fuell(2, 17, 0, 0, 17, 19, GSTEIN)
# Überdachte Terrasse unter der Auskragung: Holzdeck x19..27 z4..16, Rand aus glattem Stein
for x in range(19, 28):
    for z in range(4, 17):
        put(x, 0, z, GSTEIN if x == 27 or z in (4, 16) else FICHTE)
# Pool wie in der Grundversion: Rand aus weißem Beton, Licht in den Ecken und in der Mitte der Längsseiten
for x in range(18, 29):
    for z in range(17, 24):
        rand = x in (18, 28) or z in (17, 23)
        licht = (x, z) in ((18, 17), (28, 17), (18, 23), (28, 23), (23, 17), (23, 23))
        put(x, 0, z, SEELAT if licht else BETON if rand else WASSER)
# Pooldeck im Süden x17..28 z24..26
fuell(17, 28, 0, 0, 24, 26, FICHTE)
# Trittsteine zum Eingang x4..6, im Rasen jede zweite Reihe
for z in (21, 23, 25, 27, 29):
    for x in (4, 5, 6):
        put(x, 0, z, GSTEIN)
for x in (4, 5, 6):
    put(x, 0, 30, GSTEIN)
# Rest: Rasen
for x in range(X):
    for z in range(Z):
        if leer(x, 0, z):
            put(x, 0, z, GRAS)

# =====================================================================
# Erdgeschoss y1..y4: Betonsockel, große Glasflächen mit Holzpfosten, Holz am Eingang
# =====================================================================
for y in range(1, 5):
    # Westwand x2: Beton, unten Sockelreihe, Fensterschlitz y2..3 bei z9..12
    for z in range(5, 17):
        fenster = 2 <= y <= 3 and 9 <= z <= 12
        put(2, y, z, SCHEIBE if fenster else SOCKEL if y == 1 else BETON)
    # Nordwand z5: Beton, Fensterband über der Küche (y2, x4..7) und am Wohnzimmer (y2..3, x13..16 hinter dem Kamin bleibt zu)
    for x in range(3, 18):
        fenster = (y == 2 and 4 <= x <= 7) or (2 <= y <= 3 and x in (10, 11))
        put(x, y, 5, SCHEIBE if fenster else SOCKEL if y == 1 else BETON)
    # Ostwand x18 zur überdachten Terrasse: Glas bis unter die Decke, Holzpfosten
    for z in range(5, 17):
        if z in (5, 16):
            put(18, y, z, BETON)
        elif z in (8, 13):
            put(18, y, z, HOLZ)
        else:
            put(18, y, z, SCHEIBE)
    # Südwand z16: Holz am Eingang (x2..7), dann Glas mit Holzpfosten
    for x in range(3, 18):
        if x in (4, 5, 6) and y <= 3:
            continue                     # Nische
        if x <= 7:
            put(x, y, 16, HOLZ)
        elif x in (8, 12):
            put(x, y, 16, HOLZ)
        else:
            put(x, y, 16, SCHEIBE)
    # Nische: Seitenwände eine Reihe zurück
    if y <= 3:
        put(4, y, 15, HOLZ)
        put(6, y, 15, HOLZ)
# Haustür in der Nische, Terrassentüren nach Süden und Osten
tuer(5, 1, 15, 'north')
tuer(14, 1, 16, 'north')
tuer(18, 1, 10, 'west')
# Licht in der Nische
put(5, 3, 16, HAENGE)

# ---- Innen: offener Wohnbereich ----
# Küche im Nordwesten: Zeile an der Nordwand, Insel mit Hockern
for x, k in ((3, RAEUCHER), (4, BETON), (5, KESSEL), (6, BETON), (7, BETON), (8, FASS)):
    put(x, 1, 6, k)
put(3, 2, 6, T_FARN)
for x in (4, 5, 6, 7):
    put(x, 1, 8, BETON)
for x in (5, 6):
    put(x, 1, 9, HOCKER)
    put(x, 2, 9, SITZ)
put(5, 4, 8, HAENGE)
put(6, 4, 8, HAENGE)
# Essplatz x10..12 z8..9: Tisch aus Eichenstufen, Stühle aus Eichentreppen
for x in (10, 11, 12):
    put(x, 1, 8, TPLATTE)
    put(x, 1, 9, TPLATTE)
    put(x, 1, 7, TREPPE['north'])
    put(x, 1, 10, TREPPE['south'])
put(11, 4, 8, HAENGE)
put(11, 4, 9, HAENGE)
# Wohnen im Osten: Kamin an der Nordwand, Sofa in L-Form, Couchtisch, Teppich
for x in range(13, 18):
    for y in range(1, 5):
        put(x, y, 6, SCHWARZ)
put(15, 1, 6, FEUER, True)
put(15, 2, 6, TV, True)
for x in (13, 14, 15, 16):
    put(x, 1, 10, SOFA['south'])
put(17, 1, 9, SOFA['east'])
put(17, 1, 10, SOFA['east'])
put(14, 1, 8, TISCH)
put(15, 1, 8, TISCH)
for x, z in ((13, 7), (14, 7), (15, 7), (16, 7), (13, 8), (16, 8), (13, 9), (14, 9), (15, 9), (16, 9)):
    put(x, 1, z, TEPPICH)
put(17, 1, 7, T_BAMBUS)
put(15, 4, 8, HAENGE)
# Treppe ins Obergeschoss entlang z13, steigt nach Osten (wie Grundversion), darunter Bücherwand
for i, x in enumerate(range(10, 15)):
    put(x, 1 + i, 13, TREPPE['east'])
    for y in range(1, 1 + i):
        put(x, y, 13, REGAL)
# Diele: Garderobe aus Fässern, Bank, Pflanze
for z in (12, 13, 14):
    put(3, 1, z, FASS)
put(3, 2, 14, T_AZALEE)
put(7, 1, 14, TREPPE['east'])
put(5, 4, 13, HAENGE)
# Pflanzen an der Glasfront
put(9, 1, 15, T_BAMBUS)
put(17, 1, 15, T_FARN)

# =====================================================================
# Decke y5: Boden des Obergeschosses und Dachterrasse über dem Erdgeschoss
# =====================================================================
UNTEN = {(x, z) for x in range(2, 19) for z in range(5, 17)}
OBEN = {(x, z) for x in range(8, 27) for z in range(3, 15)}
TREPPENAUGE = {(11, 13), (12, 13), (13, 13)}
LICHTER = {(20, 5), (24, 5), (20, 9), (24, 9), (20, 13), (24, 13)}   # Einbauleuchten in der Untersicht der Auskragung
for x, z in UNTEN | OBEN:
    if (x, z) in TREPPENAUGE or (x, z) == (14, 13):
        continue
    if (x, z) in OBEN:
        innen = 9 <= x <= 25 and 4 <= z <= 13
        put(x, 5, z, SEELAT if (x, z) in LICHTER else EICHE if innen else BETON)
    else:
        rand = x == 2 or z in (5, 16) or x == 18
        put(x, 5, z, BETON if rand else FICHTE)
# Vordach über dem Eingang
fuell(3, 7, 5, 5, 17, 18, BETON)
put(5, 4, 17, HAENGE)
# Holz-Sturz über der Nische
for x in (4, 5, 6):
    put(x, 4, 16, HOLZ)

# =====================================================================
# Obergeschoss y6..y9: Holzbox in weißem Rahmen, große Fenster
# =====================================================================
for y in range(6, 10):
    for x in range(8, 27):
        for z in (3, 14):
            put(x, y, z, BETON if x in (8, 26) else HOLZ)
    for z in range(4, 14):
        put(8, y, z, HOLZ)
        put(26, y, z, HOLZ)
# Südseite z14
for x in range(9, 26):
    for y in range(6, 10):
        if 13 <= x <= 17 and y <= 8:
            put(x, y, 14, SCHEIBE, True)
        elif 19 <= x <= 25 and y <= 8:
            put(x, y, 14, HOLZ if x == 22 else SCHEIBE, True)
        elif x in (10, 11) and 7 <= y <= 8:
            put(x, y, 14, SCHEIBE, True)
    put(18, 6, 14, BETON, True)
    put(18, 7, 14, BETON, True)
    put(18, 8, 14, BETON, True)
    put(18, 9, 14, BETON, True)
# Ostseite x26: komplett Glas, ein Holzpfosten
for z in range(4, 14):
    for y in range(6, 10):
        put(26, y, z, HOLZ if z == 8 else SCHEIBE, True)
# Nordseite z3: Fensterschlitze, Bad mit Milchglas
for y in (7, 8):
    for x in (10, 11, 12):
        put(x, y, 3, SCHEIBE, True)
for x in range(15, 19):
    put(x, 7, 3, MATT, True)
for x in range(20, 25):
    put(x, 7, 3, SCHEIBE, True)
# Westseite x8 zur Dachterrasse: Fenster und Tür
for z in (5, 6, 7):
    for y in (6, 7, 8):
        put(8, y, z, SCHEIBE, True)
tuer(8, 6, 10, 'east')

# ---- Innenwände ----
def wand(x, y, z, oben_matt=False):
    put(x, y, z, MATT if (oben_matt and y >= 8) else BETON)


for y in range(6, 10):
    for z in range(4, 9):
        wand(14, y, z)                     # Kinderzimmer | Bad
    for x in range(9, 14):
        wand(x, y, 9)                      # Kinderzimmer | Flur
    for x in range(15, 19):
        wand(x, y, 9, oben_matt=True)      # Bad | Flur, oben Milchglas
    for z in range(4, 14):
        wand(19, y, z)                     # Schlafzimmer
tuer(11, 6, 9, 'north')
tuer(16, 6, 9, 'north')
tuer(19, 6, 11, 'west')

# Kinderzimmer/Arbeitszimmer x9..13 z4..8
for y in (6, 7, 8):
    put(9, y, 4, REGAL)
    put(9, y, 5, REGAL)
for x in (10, 11, 12):
    put(x, 6, 4, TPLATTE)
put(11, 6, 5, TREPPE['south'])
bett(12, 6, 7, 'east')
for x, z in ((10, 6), (11, 6), (10, 7), (11, 7), (10, 8), (11, 8)):
    put(x, 6, z, WTEPPICH)
put(13, 6, 5, T_FARN)
put(11, 9, 6, HAENGE)
# Bad x15..18 z4..8: Wanne, Waschtisch, Dusche hinter Glas
put(16, 6, 4, KESSEL)
put(17, 6, 4, KESSEL)
put(15, 6, 7, KESSEL)
put(15, 6, 8, BETON)
for y in (6, 7, 8):
    put(17, y, 7, SCHEIBE)
put(18, 6, 4, T_BAMBUS)
put(16, 9, 6, HAENGE)
# Schlafzimmer x20..25 z4..13: Doppelbett mit Blick nach Süden und Osten
bett(22, 6, 5, 'north')
bett(23, 6, 5, 'north')
for x in (21, 24):
    put(x, 6, 4, FASS)
    put(x, 7, 4, LATERNE)
for x in range(21, 25):
    for z in (6, 7, 8):
        put(x, 6, z, WTEPPICH)
for z in (10, 11, 12):
    put(20, 6, z, FASS)                    # Schrank an der Trennwand
put(24, 6, 12, SOFA['south'])
put(25, 6, 11, SOFA['east'])
put(25, 6, 13, T_AZALEE)
put(22, 9, 8, HAENGE)
# Flur und Galerie x9..18 z10..13: Glasgeländer am Treppenauge, Leseecke
for x in (11, 12, 13):
    put(x, 6, 12, SCHEIBE)
put(10, 6, 13, SCHEIBE)
put(16, 6, 13, SOFA['south'])
put(17, 6, 13, SOFA['south'])
put(18, 6, 12, SOFA['east'])
put(9, 6, 13, T_BAMBUS)
put(13, 9, 11, HAENGE)
put(17, 9, 11, HAENGE)

# Einbauleuchten der Auskragung liegen im Schlafzimmerboden: mit Teppich abdecken
for x, z in LICHTER:
    if leer(x, 6, z):
        put(x, 6, z, WTEPPICH)

# =====================================================================
# Dach y10 mit dünner Kante, Gründach y11..12, Oberlicht über dem Flur
# =====================================================================
for x in range(7, 28):
    for z in range(2, 16):
        if x in (7, 27) or z in (2, 15):
            put(x, 10, z, SOBEN)
        elif (x, z) in ((12, 11), (13, 11), (14, 11), (15, 11)):
            put(x, 10, z, GLAS)
        else:
            put(x, 10, z, BETON)
for x in range(8, 27):
    for z in range(3, 15):
        if x in (8, 26) or z in (3, 14):
            put(x, 11, z, GSTEIN)
        elif not (11 <= x <= 16 and 10 <= z <= 12):
            put(x, 11, z, MOOS)
for x in range(11, 17):
    for z in (10, 12):
        put(x, 11, z, GSTEIN)
for x in (11, 16):
    put(x, 11, 11, GSTEIN)
# Gräser und Blüten im Gründach
import random
zufall = random.Random(7)
for x in range(9, 26):
    for z in range(4, 14):
        if G.get((x, 11, z)) == MOOS:
            r = zufall.random()
            if r < .12:
                put(x, 12, z, GRAESER)
            elif r < .16:
                put(x, 12, z, MARGERITE)
            elif r < .19:
                put(x, 12, z, ALLIUM)

# =====================================================================
# Dachterrasse über dem Erdgeschoss (Ebene 6): Glasgeländer wie Grundversion, Holz-Pergola, Liegen, Pflanzkästen
# =====================================================================
for z in range(5, 17):
    put(2, 6, z, SCHEIBE)
for x in range(3, 19):
    put(x, 6, 16, SCHEIBE)
put(18, 6, 15, SCHEIBE)
for x in range(3, 8):
    put(x, 6, 5, SCHEIBE)
# Pergola: Pfosten und Balken aus entrindeter Eiche
for x, z in ((3, 7), (7, 7), (3, 15), (7, 15)):
    for y in (6, 7, 8):
        put(x, y, z, HOLZ)
for z in range(7, 16):
    put(3, 9, z, BALKEN_Z)
    put(7, 9, z, BALKEN_Z)
for z in (7, 9, 11, 13, 15):
    for x in (4, 5, 6):
        put(x, 9, z, BALKEN_X)
# Liegen und Tisch
for x in (4, 6):
    put(x, 6, 10, TREPPE['north'])
    put(x, 6, 11, EUNTEN)
    put(x, 6, 12, EUNTEN)
put(5, 6, 11, T_AZALEE)
# Pflanzkästen an den Ecken
for x, z in ((3, 6), (7, 6), (17, 15), (3, 14)):
    put(x, 6, z, MOOS)
    put(x, 7, z, AZALEE)
put(5, 8, 11, HAENGE)

# =====================================================================
# Überdachte Terrasse unter der Auskragung: Lounge mit Feuerstelle, Essplatz, Grill
# =====================================================================
for x in (22, 23, 24, 25):
    put(x, 1, 5, SOFA['north'])
put(25, 1, 6, SOFA['east'])
put(25, 1, 7, SOFA['east'])
put(22, 1, 7, SOFA['west'])
put(23, 1, 7, FEUER)
put(24, 1, 7, TISCH)
for x in (21, 22, 23, 24):
    put(x, 1, 11, TPLATTE)
    put(x, 1, 12, TPLATTE)
    put(x, 1, 10, TREPPE['north'])
    put(x, 1, 13, TREPPE['south'])
for z, k in ((5, GRILL), (6, BETON), (7, KESSEL)):
    put(19, 1, z, k)
put(19, 2, 6, T_FARN)

# =====================================================================
# Garten: Hecke, Mauer mit Pforte, Poller, Birken, Beete, Pooldeck
# =====================================================================
for y in (1, 2):
    for x in range(1, 30):
        put(x, y, 2, LAUB)
    for z in range(3, 30):
        put(1, y, z, LAUB)
    for z in range(3, 17):
        put(29, y, z, LAUB)
for x in range(1, 30):
    if x not in (4, 5, 6):
        put(x, 1, 30, BETON)
for x in (3, 7):
    put(x, 1, 30, POLLER, True)
    put(x, 2, 30, LATERNE)
for x, z in ((3, 22), (7, 22), (3, 26), (7, 26)):
    put(x, 1, z, POLLER)
    put(x, 2, z, LATERNE)
# Liegen am Pool, Sonnenschirm
for x in (19, 21, 23):
    put(x, 1, 26, TREPPE['south'])
    put(x, 1, 25, EUNTEN)
put(26, 1, 25, HOCKER)
put(26, 2, 25, HOCKER)
fuell(25, 27, 3, 3, 24, 26, WOLLE)
# Beet entlang der Südterrasse
blumen = [ALLIUM, TULPE, KORNBLUME, MARGERITE, FARN, TULPE, ALLIUM, GRAESER, KORNBLUME]
for i, x in enumerate(range(8, 17)):
    put(x, 1, 20, blumen[i % len(blumen)])
    if i % 2 == 0:
        put(x, 1, 21, blumen[(i + 4) % len(blumen)])
for x, z in ((2, 4), (6, 4), (10, 4), (14, 4)):
    put(x, 1, z, AZALEE)


# Birken: weißer Stamm, lockere Krone
def birke(x, z, h):
    for y in range(1, h + 1):
        put(x, y, z, STAMM)
    for y in range(h - 2, h + 2):
        r = 2 if y < h else 1
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) == r and abs(dz) == r:
                    continue
                if leer(x + dx, y, z + dz):
                    put(x + dx, y, z + dz, LAUB)
    put(x, h + 2, z, LAUB)


birke(10, 24, 6)
birke(13, 27, 5)
birke(25, 28, 6)
for x, z, k in ((9, 26, GRAESER), (12, 25, FARN), (14, 25, GRAESER), (24, 27, FARN), (27, 28, GRAESER)):
    if leer(x, 1, z):
        put(x, 1, z, k)

# =====================================================================
model = {'format': 1, 'size': {'x': X, 'y': Y, 'z': Z}, 'palette': P,
         'layers': [[''.join(G.get((x, y, z), '.') for x in range(X)) for z in range(Z)] for y in range(Y)]}
n = {}
for k in G.values():
    n[k] = n.get(k, 0) + 1
vorh = {e['key'] for e in P if 'vorhanden' in (e.get('flags') or [])}
print('Blöcke', sum(v for k, v in n.items() if k not in vorh), 'Blockarten', len([k for k in n if k not in vorh]))
P[:] = [e for e in P if e['key'] in n]   # nicht benutzte Blöcke nicht in die Palette
os.makedirs(ZIEL, exist_ok=True)
with open(os.path.join(ZIEL, 'model.json'), 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False)
    f.write('\n')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump({NAME[k]: v for k, v in sorted(n.items(), key=lambda t: -t[1])}, f, ensure_ascii=False, indent=0)
