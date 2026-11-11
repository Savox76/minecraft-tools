"""Villa am Wasser – Ausbau-Version (verfeinert wie ein Creator).

Leitbild: modern, hell, luxuriös am Wasser. Grundidee der Grundversion bleibt:
Glasfront zum Wasser, auskragendes Obergeschoss, erhöhter Pool mit Glaskante, Dachterrasse mit Whirlpool,
Penthouse, Wasser-Aufzug. Verfeinert: Fassadentiefe (vorstehende Deckenkanten, Glas zurückgesetzt, Lisenen),
Materialmix (Quarz, Beton, Tiefenschiefer, Holzlamellen), eingerichtete Räume, Garten, Steg, Licht.

Koordinaten: x nach Osten, z nach Süden (Wasser im Süden), y nach oben. Ebene 0 = Boden.
"""
import json, os, sys

ZIEL = sys.argv[1]
X, Y, Z = 33, 16, 38

P = []
KEY = {}
ZEICHEN = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&*+-/:;<=>?@^_~')


def block(name, mc, farbe, flags=None):
    k = next(ZEICHEN)
    e = {'key': k, 'name': name, 'block': mc, 'color': farbe}
    if flags:
        e['flags'] = flags
    P.append(e)
    KEY[name] = k
    return k


RICHT = {'north': 'Norden', 'south': 'Süden', 'east': 'Osten', 'west': 'Westen'}

# ---------- Gelände ----------
GRAS = block('Gras (vorhanden)', 'minecraft:grass_block', '#6f9e48', ['vorhanden'])
SAND = block('Sand (vorhanden)', 'minecraft:sand', '#dccf9e', ['vorhanden'])
MEER = block('Meer (vorhanden)', 'minecraft:water', '#3f76e4', ['vorhanden'])
# ---------- Rohbau ----------
QUARZ = block('Glatter Quarzblock', 'minecraft:smooth_quartz', '#ece6dc')
BETON = block('Weißer Beton', 'minecraft:white_concrete', '#e3e6e6')
SOCKEL = block('Hellgrauer Beton', 'minecraft:light_gray_concrete', '#8e8e86')
DUNKEL = block('Polierter Tiefenschiefer', 'minecraft:polished_deepslate', '#4a4a4f')
SAEULE = block('Quarzsäule', 'minecraft:quartz_pillar', '#e9e3d8')
QOBEN = block('Glatte-Quarz-Stufe (oben)', 'minecraft:smooth_quartz_slab[type=top]', '#efe9df')
QUNTEN = block('Glatte-Quarz-Stufe (unten)', 'minecraft:smooth_quartz_slab[type=bottom]', '#efe9df')
SCHEIBE = block('Glasscheibe', 'minecraft:glass_pane', '#bfe6f2')
MATT = block('Weiße Buntglasscheibe', 'minecraft:white_stained_glass_pane', '#f2f4f4')
GLAS = block('Glas', 'minecraft:glass', '#a9dcec')
LAMELLE = block('Entrindeter Dunkeleichenstamm', 'minecraft:stripped_dark_oak_log', '#4a3524')
DEICHE = block('Dunkle Eichenholzbretter', 'minecraft:dark_oak_planks', '#4c3320')
BIRKE = block('Birkenholzbretter', 'minecraft:birch_planks', '#d7c98c')
FICHTE = block('Fichtenholzbretter', 'minecraft:spruce_planks', '#7a5a36')
FPFOSTEN = block('Entrindeter Fichtenstamm', 'minecraft:stripped_spruce_log', '#73593a')
GSTEIN = block('Glatter Stein', 'minecraft:smooth_stone', '#a3a6a8')
ANDESIT = block('Polierter Andesit', 'minecraft:polished_andesite', '#8e9192')
TSTUFE = block('Polierte-Tiefenschiefer-Stufe', 'minecraft:polished_deepslate_slab[type=bottom]', '#505056')
WASSER = block('Wasser', 'minecraft:water', '#3f86f0')
SEELAT = block('Seelaterne', 'minecraft:sea_lantern', '#cfe8e0')
LEUCHT = block('Leuchtstein', 'minecraft:glowstone', '#ffd75e')
ENDSTAB = block('Endstab', 'minecraft:end_rod', '#f3efe6')
ENDSTAB_U = block('Endstab (nach unten)', 'minecraft:end_rod[facing=down]', '#f3efe6')
LATERNE = block('Laterne', 'minecraft:lantern', '#f2b33d')
FEUER = block('Lagerfeuer', 'minecraft:campfire[lit=true]', '#e0782a')
SEELENSAND = block('Seelensand', 'minecraft:soul_sand', '#5b4536')
MAGMA = block('Magmablock', 'minecraft:magma_block', '#8f3a12')
SOLAR = block('Tageslichtsensor', 'minecraft:daylight_detector', '#d9cfb8')
# ---------- Türen ----------
TUER = {}
for r in ('north', 'south', 'east', 'west'):
    TUER[r] = (block('Dunkle Eichentür (unten, Tür nach %s)' % RICHT[r], 'minecraft:dark_oak_door[half=lower,facing=%s]' % r, '#4c3320'),
               block('Dunkle Eichentür (oben, Tür nach %s)' % RICHT[r], 'minecraft:dark_oak_door[half=upper,facing=%s]' % r, '#4c3320', ['zweiter-teil']))
# ---------- Treppen ----------
QTREPPE = {r: block('Glatte-Quarz-Treppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:smooth_quartz_stairs[facing=%s]' % r, '#ece6dc')
           for r in ('north', 'south', 'east', 'west')}
STUHL = {r: block('Dunkle Eichentreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:dark_oak_stairs[facing=%s]' % r, '#4c3320')
         for r in ('north', 'south', 'east', 'west')}
# ---------- Möbel ----------
SLAT_W = block('Fichtenfalltür (Lamelle, offen nach Westen)', 'minecraft:spruce_trapdoor[facing=west,open=true,half=bottom]', '#7a5a36')
SLAT_N = block('Fichtenfalltür (Lamelle, offen nach Norden)', 'minecraft:spruce_trapdoor[facing=north,open=true,half=bottom]', '#7a5a36')
TISCH = block('Dunkle-Eichen-Falltür (unten)', 'minecraft:dark_oak_trapdoor[half=bottom]', '#4c3320')
SCHRANK = block('Dunkle-Eichen-Falltür (Wandschrank)', 'minecraft:dark_oak_trapdoor[facing=south,open=true,half=top]', '#4c3320')
TPLATTE = block('Glatte-Quarz-Stufe (Tischplatte)', 'minecraft:smooth_quartz_slab[type=top]', '#efe9df')
HOCKER = block('Fichtenzaun', 'minecraft:spruce_fence', '#6e5233')
SITZ = block('Fichten-Druckplatte', 'minecraft:spruce_pressure_plate', '#7a5a36')
TEPPICH = block('Hellgrauer Teppich', 'minecraft:light_gray_carpet', '#9d9d97')
WTEPPICH = block('Weißer Teppich', 'minecraft:white_carpet', '#eaeded')
FASS = block('Fass', 'minecraft:barrel[facing=up]', '#8a6438')
RAEUCHER = block('Räucherofen', 'minecraft:smoker[facing=south]', '#5d5a55')
KESSEL = block('Kessel mit Wasser', 'minecraft:water_cauldron[level=3]', '#4a4a50')
REGAL = block('Bücherregal', 'minecraft:bookshelf', '#9a7a4a')
PULT = block('Lesepult', 'minecraft:lectern[facing=east]', '#9a7a4a')
BRAU = block('Braustand', 'minecraft:brewing_stand', '#6a6a60')
TV = block('Schwarzer Beton', 'minecraft:black_concrete', '#16171b')
BETT_FUSS = block('Weißes Bett (Fußende)', 'minecraft:white_bed[part=foot,facing=north]', '#e9ecec')
BETT_KOPF = block('Weißes Bett (Kopfende)', 'minecraft:white_bed[part=head,facing=north]', '#e9ecec', ['zweiter-teil'])
# ---------- Pflanzen ----------
MOOS = block('Moosblock', 'minecraft:moss_block', '#5a7a2e')
FARN = block('Farn', 'minecraft:fern', '#5c8c3a')
GRAESER = block('Kurzes Gras', 'minecraft:short_grass', '#6c9a40')
MARGERITE = block('Margerite', 'minecraft:oxeye_daisy', '#f0efe0')
KORNBLUME = block('Kornblume', 'minecraft:cornflower', '#4f73d6')
ALLIUM = block('Zierlauch', 'minecraft:allium', '#b77ad8')
T_BAMBUS = block('Topf mit Bambus', 'minecraft:potted_bamboo', '#7fae3a')
T_FARN = block('Topf mit Farn', 'minecraft:potted_fern', '#5c8c3a')
T_AZALEE = block('Topf mit blühender Azalee', 'minecraft:potted_flowering_azalea_bush', '#7a9a3a')
AZALEE = block('Blühendes Azaleenlaub', 'minecraft:flowering_azalea_leaves[persistent=true]', '#6c8f3a')
HECKE = block('Eichenlaub', 'minecraft:oak_leaves[persistent=true]', '#5d8a2f')
PSTAMM = block('Tropenbaumstamm', 'minecraft:jungle_log', '#8a6b3d')
PLAUB = block('Tropenbaumlaub', 'minecraft:jungle_leaves[persistent=true]', '#4f9a2a')

G = {}


def put(x, y, z, k, ueber=False):
    if not (0 <= x < X and 0 <= y < Y and 0 <= z < Z):
        raise SystemExit('außerhalb: %s' % ((x, y, z),))
    alt = G.get((x, y, z))
    if alt is not None and alt != k and not ueber:
        n = {e['key']: e['name'] for e in P}
        raise SystemExit('Konflikt bei %s: %s gegen %s' % ((x, y, z), n[alt], n[k]))
    G[(x, y, z)] = k


def fuell(x0, x1, y0, y1, z0, z1, k, ueber=False):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                put(x, y, z, k, ueber)


def leer(x, y, z):
    return (x, y, z) not in G


def tuer(x, y, z, richtung):
    u, o = TUER[richtung]
    put(x, y, z, u)
    put(x, y + 1, z, o)


# =====================================================================
# Ebene 0: Gelände, Böden, Wege, Pool-Boden, Aufzug
# =====================================================================
# Haus Erdgeschoss: Außenwände x5..23, z3..14; innen x6..22, z4..13
for x in range(5, 24):
    for z in range(3, 15):
        rand = x in (5, 23) or z in (3, 14)
        put(x, 0, z, SOCKEL if rand else BIRKE)
# Eingangsnische x13..15 z3 (Wand springt zurück), Boden Andesit
for x in (13, 14, 15):
    put(x, 0, 3, ANDESIT, ueber=True)
# Aufzug (wie Grundversion): Seelensand fährt hoch, Magmablock runter
put(6, 0, 7, SEELENSAND, ueber=True)
put(6, 0, 8, MAGMA, ueber=True)
# Weg zur Haustür: Platten mit Fuge, daneben Beete
for z in (0, 1, 2):
    put(13, 0, z, ANDESIT)
    put(14, 0, z, GSTEIN)
    put(15, 0, z, ANDESIT)
for x0, x1 in ((6, 12), (16, 22)):
    for x in range(x0, x1 + 1):
        put(x, 0, 2, MOOS)
# Terrasse x3..29, z15..27 aus Dunkler Eiche, Rand aus glattem Stein
for x in range(3, 30):
    for z in range(15, 28):
        if (x, 0, z) in G:
            continue
        rand = z == 27 or x in (3, 29) or x in (11, 12)
        put(x, 0, z, GSTEIN if rand else DEICHE)
# Pool x13..28, z20..26: Boden weißer Beton mit Seelaternen
for x in range(13, 29):
    for z in range(20, 27):
        licht = z == 23 and x in (16, 20, 24)
        put(x, 0, z, SEELAT if licht else BETON, ueber=True)
# Feuerstelle x4..10, z20..24: abgesenkte Lounge aus Tiefenschiefer
for x in range(4, 11):
    for z in range(20, 25):
        put(x, 0, z, DUNKEL, ueber=True)
# Steg ins Meer: Weg über den Strand, Steg x16..17 z30..35, Kopf x14..19 z35..37
for z in (28, 29):
    for x in (11, 12):
        put(x, 0, z, GSTEIN)
for z in range(30, 38):
    for x in (11, 12):
        put(x, 0, z, FICHTE)
for z in (35, 36, 37):
    for x in range(9, 15):
        if (x, 0, z) not in G:
            put(x, 0, z, FICHTE)
# Gelände ringsum
for x in range(X):
    for z in range(Z):
        if (x, 0, z) not in G:
            put(x, 0, z, GRAS if z < 28 else SAND if z < 30 else MEER)

# =====================================================================
# Erdgeschoss y1..y4
# =====================================================================
LAMELLEN_N = set(range(9, 13)) | set(range(16, 18))


def eg_wand(x, z, y):
    """Außenwand Erdgeschoss."""
    ecke = x in (5, 23) and z in (3, 14)
    if ecke:
        return QUARZ
    if z == 14:                                   # Südfront zum Wasser: Glas mit Lisenen
        if x in (9, 13, 17, 21):
            return SAEULE
        return SCHEIBE
    if x == 23:                                   # Ostseite: Glas mit Lisenen
        if z in (6, 10):
            return SAEULE
        return SCHEIBE
    if x == 5:                                    # Westseite: Holzlamellen, Aufzug, schmale Fenster
        if z in (6, 9):
            return GLAS
        if z in (11, 12) and y in (2, 3):
            return SCHEIBE
        return DUNKEL
    if z == 3:                                    # Nordseite: Eingang, Lamellen, Küchenfenster
        if x in LAMELLEN_N:
            return DUNKEL
        if 7 <= x <= 8 and y == 3:
            return SCHEIBE
        if 19 <= x <= 21 and y in (2, 3):
            return SCHEIBE
        return QUARZ
    return None


for y in range(1, 5):
    for x in range(5, 24):
        for z in range(3, 15):
            if x in (5, 23) or z in (3, 14):
                if z == 3 and 13 <= x <= 15:
                    continue                      # Eingangsnische
                k = eg_wand(x, z, y)
                if k:
                    put(x, y, z, k)
# Nische: Seitenwände und Haustür eine Reihe zurück
for y in range(1, 5):
    put(13, y, 4, QUARZ)
    put(15, y, 4, QUARZ)
tuer(14, 1, 4, 'south')
put(14, 3, 4, SCHEIBE)
put(14, 4, 4, QUARZ)
put(14, 4, 3, SEELAT)                             # Licht in der Nischendecke
put(13, 4, 3, QUARZ)
put(15, 4, 3, QUARZ)
# Terrassentür in der Glasfront
put(15, 1, 14, TUER['north'][0], ueber=True)
put(15, 2, 14, TUER['north'][1], ueber=True)

# Wasser-Aufzug wie in der Grundversion: zwei Schächte x6 z7/z8, Türen bei x7
for y in range(1, 5):
    put(5, y, 6, GLAS, ueber=True)
    put(6, y, 6, GLAS)
    put(5, y, 9, GLAS, ueber=True)
    put(6, y, 9, GLAS)
    put(6, y, 7, WASSER)
    put(6, y, 8, WASSER)
for z in (7, 8):
    tuer(7, 1, z, 'east')
    put(7, 3, z, GLAS)
    put(7, 4, z, GLAS)

# Treppe ins Obergeschoss: entlang der Nordwand, x17..21 z4..5, steigt nach Osten
for i, x in enumerate(range(17, 22)):
    for z in (4, 5):
        put(x, 1 + i, z, QTREPPE['east'])
for x in (17, 18):
    for z in (4, 5):
        for y in range(1, 1 + (x - 17)):
            pass
# unter der Treppe: Stauraum
for z in (4, 5):
    put(18, 1, z, FASS)
    put(19, 1, z, FASS)
    put(19, 2, z, REGAL)
    put(20, 1, z, REGAL)
    put(20, 2, z, REGAL)
    put(20, 3, z, REGAL)
    put(21, 1, z, REGAL)
    put(21, 2, z, REGAL)
    put(21, 3, z, REGAL)
    put(21, 4, z, REGAL)

# Küche im Nordwesten x7..11, z4..6
for x in range(7, 12):
    put(x, 1, 4, {7: RAEUCHER, 8: DUNKEL, 9: KESSEL, 10: DUNKEL, 11: FASS}[x])
    if x not in (7, 8):
        put(x, 3, 4, SCHRANK)
put(11, 2, 4, T_BAMBUS)
for x in (8, 9, 10):
    put(x, 1, 6, DUNKEL)                          # Kochinsel
    put(x, 1, 7, HOCKER) if x != 9 else None
    if x != 9:
        put(x, 2, 7, SITZ)
put(9, 2, 6, T_FARN)
# Essplatz x8..11, z10..12
for x in (9, 10):
    put(x, 1, 11, HOCKER)
    put(x, 2, 11, TPLATTE)
    put(x, 1, 10, STUHL['north'])
    put(x, 1, 12, STUHL['south'])
put(9, 3, 11, ENDSTAB)
# Wohnbereich x13..22, z8..13 mit Blick nach Süden
for x in range(14, 19):
    put(x, 1, 9, QTREPPE['north'])                # Sofa, Lehne im Norden
for z in (10, 11, 12):
    put(13, 1, z, QTREPPE['west'])                # Sofa-Seite, Lehne im Westen
for x in range(14, 19):
    for z in (10, 11, 12):
        if z == 11 and 15 <= x <= 17:
            put(x, 1, z, TISCH)                   # Couchtisch
        else:
            put(x, 1, z, TEPPICH)
put(16, 2, 11, T_AZALEE, ueber=False) if leer(16, 2, 11) else None
for z in (8, 9):
    put(22, 1, z, DUNKEL)                         # Sideboard an der Ostseite
    put(22, 2, z, T_BAMBUS if z == 8 else LATERNE)
put(22, 1, 12, T_AZALEE)
put(22, 1, 13, REGAL)
put(6, 1, 12, T_BAMBUS)
put(6, 1, 13, REGAL)
put(6, 2, 13, REGAL)
for y in (2, 3):                                  # Fernsehwand im Westen
    for z in (10, 11):
        put(6, y, z, TV)
# Eingangsbereich: Pflanzen und Licht
put(12, 1, 4, T_FARN)
put(16, 1, 4, T_BAMBUS)

# =====================================================================
# Decke/Obergeschoss-Boden y5: kragt nach Süden und Osten aus (x4..27, z2..17)
# =====================================================================
for x in range(4, 28):
    for z in range(2, 18):
        if 6 <= x <= 6 and z in (7, 8):
            put(x, 5, z, WASSER)
            continue
        if 19 <= x <= 20 and z in (4, 5):
            continue                              # Treppenauge
        if x == 21 and z in (4, 5):
            put(x, 5, z, QTREPPE['east'])
            continue
        innen = 5 <= x <= 25 and 3 <= z <= 15
        licht = False
        if licht:
            put(x, 5, z, LEUCHT)
        else:
            put(x, 5, z, BIRKE if innen else QUARZ)
# Lichtleiste unter der Auskragung (Erdgeschoss-Terrasse und Ostseite)
for x in range(6, 27, 4):
    put(x, 4, 17, ENDSTAB_U)
for z in range(16, 3, -4):
    put(27, 4, z, ENDSTAB_U)
# Vordach über dem Eingang
for x in range(12, 17):
    for z in (0, 1):
        put(x, 5, z, QOBEN)
put(14, 5, 1, SEELAT, ueber=True)

# =====================================================================
# Obergeschoss y6..y9: Wände x4..26, z2..16 (Glas zurückgesetzt hinter die Deckenkante)
# =====================================================================


def og_wand(x, z, y):
    ecke = x in (4, 26) and z in (2, 16)
    if ecke:
        return QUARZ
    if z == 16:
        return SAEULE if x in (8, 12, 16, 20, 24) else SCHEIBE
    if x == 26:
        return SAEULE if z in (6, 11) else SCHEIBE
    if x == 4:
        if z in (11, 12, 13) and y in (7, 8):
            return SCHEIBE
        return DUNKEL
    if z == 2:
        if y in (7, 8) and 9 <= x <= 14:
            return MATT                           # Badfenster, matt
        if y in (7, 8) and (5 <= x <= 7 or 22 <= x <= 25):
            return SCHEIBE
        if y in (7, 8) and 5 <= x <= 25:
            return DUNKEL                         # dunkles Fensterband verbindet die Fenster
        return QUARZ
    return None


for y in range(6, 10):
    for x in range(4, 27):
        for z in range(2, 17):
            if x in (4, 26) or z in (2, 16):
                put(x, y, z, og_wand(x, z, y))
# Aufzug im OG (wie Grundversion)
for y in range(6, 10):
    put(5, y, 7, GLAS)
    put(5, y, 8, GLAS)
    put(6, y, 6, GLAS)
    put(6, y, 9, GLAS)
    put(6, y, 7, WASSER)
    put(6, y, 8, WASSER)
for z in (7, 8):
    tuer(7, 6, z, 'east')
    put(7, 8, z, GLAS)
    put(7, 9, z, GLAS)
# Geländer am Treppenauge
for z in (4, 5):
    put(18, 6, z, SCHEIBE)
for x in (19, 20):
    put(x, 6, 6, SCHEIBE)
# Treppe zur Dachterrasse: einläufig an der Nordwand z3, steigt nach Westen x20..16
for i, x in enumerate(range(20, 15, -1)):
    put(x, 6 + i, 3, QTREPPE['west'])
# Bad x9..14, z3..5 mit Trennwand z6 und Tür
for x in range(8, 16):
    for y in range(6, 10):
        wand = BETON if y <= 7 else MATT
        if x == 8 or x == 15:
            for z in range(3, 6):
                if not (x == 15 and z == 3):
                    put(x, y, z, wand)
        if 8 <= x <= 15:
            if x == 11 and y in (6, 7):
                continue
            put(x, y, 6, wand)
tuer(11, 6, 6, 'north')
put(12, 6, 3, KESSEL)
put(13, 6, 3, KESSEL)                             # Wanne
put(9, 6, 3, KESSEL)                              # Waschbecken
put(9, 8, 3, SCHEIBE)                             # Spiegel
put(14, 6, 5, QTREPPE['east'])                    # Sitzbank
put(10, 6, 5, T_BAMBUS)
put(13, 9, 4, LEUCHT, ueber=True) if False else None
# Arbeitszimmer im Westen x5..9, z10..15
for z in range(11, 16):
    put(5, 6, z, REGAL)
    put(5, 7, z, REGAL)
    if z not in (11, 12, 13):
        put(5, 8, z, REGAL)
put(7, 6, 12, HOCKER)
put(7, 7, 12, TPLATTE)
put(8, 6, 12, HOCKER)
put(8, 7, 12, TPLATTE)
put(7, 8, 12, ENDSTAB)
put(7, 6, 13, STUHL['south'])
put(6, 6, 15, PULT)
put(9, 6, 15, T_AZALEE)
# Galerie/Lounge in der Mitte x11..17, z9..15
for x in range(12, 17):
    put(x, 6, 12, QTREPPE['north'])
for x in range(12, 17):
    for z in (13, 14):
        if z == 13 and x in (13, 14, 15):
            put(x, 6, z, TISCH)
        else:
            put(x, 6, z, TEPPICH)
put(11, 6, 12, T_BAMBUS)
put(17, 6, 12, T_FARN)
put(17, 6, 15, T_AZALEE)
# Schlafzimmer im Südosten x19..25, z9..15 mit Trennwand x18 und z8
for y in range(6, 10):
    wand = BETON if y <= 7 else MATT
    for z in range(8, 16):
        if z == 12 and y in (6, 7):
            continue
        put(18, y, z, wand)
    for x in range(19, 26):
        put(x, y, 8, wand)
tuer(18, 6, 12, 'west')
for x in (22, 23):
    put(x, 6, 10, BETT_KOPF)
    put(x, 6, 11, BETT_FUSS)
for x in (21, 24):
    put(x, 6, 10, FASS)
    put(x, 7, 10, ENDSTAB)
for x in range(20, 26):
    for z in (12, 13):
        if leer(x, 6, z):
            put(x, 6, z, TEPPICH)
for z in (9, 10, 11):
    put(19, 6, z, FASS)
    put(19, 7, z, FASS)
put(25, 6, 15, QTREPPE['north'])                 # Sessel mit Blick aufs Wasser
put(24, 6, 15, T_AZALEE)
put(20, 6, 15, T_BAMBUS)
# Flur zum Aufzug: Pflanze
put(8, 6, 9, T_FARN)

# =====================================================================
# Dach y10 (Dachterrasse), Kante als dünne Stufe, Licht in der Untersicht
# =====================================================================
for x in range(3, 29):
    for z in range(1, 19):
        if x == 6 and z in (7, 8):
            put(x, 10, z, WASSER)
            continue
        if z == 3 and x in (17, 18):
            continue                              # Treppenauge
        if z == 3 and x == 16:
            continue                              # oberste Stufe liegt schon
        rand = x in (3, 28) or z in (1, 18)
        if rand:
            put(x, 10, z, QOBEN)
        elif 23 <= x <= 25 and 14 <= z <= 16:
            put(x, 10, z, SEELAT if (x, z) == (24, 15) else QUARZ)
        elif 5 <= x <= 8 and 13 <= z <= 16:
            put(x, 10, z, DEICHE)                 # Holzdeck für die Liegen
        else:
            put(x, 10, z, QUARZ)
put(16, 10, 3, QTREPPE['west'], ueber=True)

# Pendelleuchten in den Räumen
for (x, z) in ((9, 5), (15, 7), (11, 9), (16, 10), (11, 12), (20, 8), (21, 12), (14, 6)):
    if leer(x, 4, z):
        put(x, 4, z, ENDSTAB_U)                   # Erdgeschoss
for (x, z) in ((11, 4), (7, 10), (14, 10), (14, 14), (22, 12), (22, 14), (10, 8), (21, 6)):
    if leer(x, 9, z):
        put(x, 9, z, ENDSTAB_U)                   # Obergeschoss
for (x, z) in ((13, 8), (17, 8), (15, 10)):
    put(x, 13, z, ENDSTAB_U)                      # Penthouse

# Lichtleiste unter dem Dachüberstand (Obergeschoss)
for x in range(6, 27, 4):
    put(x, 9, 18, ENDSTAB_U)
for z in range(16, 3, -4):
    put(28, 9, z, ENDSTAB_U)

# =====================================================================
# Dachterrasse y11..: Glasgeländer, Penthouse, Whirlpool, Lounge
# =====================================================================
for x in range(4, 28):
    for z in range(2, 18):
        if x in (4, 27) or z in (2, 17):
            ecke = x in (4, 27) and z in (2, 17)
            put(x, 11, z, QUARZ if ecke else SCHEIBE)
for (x, z) in ((4, 2), (27, 2), (4, 17), (27, 17)):
    put(x, 12, z, ENDSTAB)
# Aufzug oben offen, Glas ringsum (wie Grundversion)
put(5, 11, 7, SCHEIBE)
put(5, 11, 8, SCHEIBE)
put(6, 11, 6, SCHEIBE)
put(6, 11, 9, SCHEIBE)
# Geländer am Treppenauge
put(15, 11, 3, SCHEIBE)
for x in (16, 17, 18):
    put(x, 11, 4, SCHEIBE)

# Penthouse x9..21, z5..12 (Wände), y11..13
PH = (9, 21, 5, 12)


def ph_wand(x, z, y):
    x0, x1, z0, z1 = PH
    if x in (x0, x1) and z in (z0, z1):
        return QUARZ
    if z == z1:
        return SAEULE if x in (13, 17) else SCHEIBE
    if x == x1:
        return SCHEIBE if z not in (8,) else SAEULE
    if x == x0:
        return DUNKEL
    if z == z0:
        if y == 12 and 11 <= x <= 19 and x % 2:
            return SCHEIBE
        return QUARZ
    return None


for y in (11, 12, 13):
    for x in range(PH[0], PH[1] + 1):
        for z in range(PH[2], PH[3] + 1):
            if x in (PH[0], PH[1]) or z in (PH[2], PH[3]):
                if x == PH[1] and z == 10 and y in (11, 12):
                    continue
                put(x, y, z, ph_wand(x, z, y))
tuer(21, 11, 10, 'west')
# Bar an der Nordwand
for x in range(11, 17):
    put(x, 11, 6, FASS if x in (11, 16) else DUNKEL)
put(12, 12, 6, BRAU)
put(15, 12, 6, BRAU)
for x in (12, 14, 16):
    put(x, 11, 8, HOCKER)
    put(x, 12, 8, SITZ)
# Lounge im Penthouse
for x in range(12, 18):
    put(x, 11, 10, QTREPPE['north'])
for x in range(12, 18):
    put(x, 11, 11, TEPPICH if x not in (14, 15) else TISCH)
put(10, 11, 6, T_BAMBUS)
put(20, 11, 6, T_AZALEE)
put(10, 11, 11, T_FARN)
put(19, 11, 11, T_BAMBUS)
put(20, 11, 9, LATERNE)
# Penthouse-Dach y14 mit dünner Kante, Solaranlage y15
for x in range(8, 23):
    for z in range(4, 14):
        rand = x in (8, 22) or z in (4, 13)
        put(x, 14, z, QOBEN if rand else QUARZ)
for x in range(11, 20):
    for z in (6, 7, 9, 10):
        put(x, 15, z, SOLAR)
# Whirlpool x22..26, z13..17 wie Grundversion, mit Quarzrand
for x in range(22, 27):
    for z in range(13, 18):
        if z == 17:
            continue
        if 23 <= x <= 25 and 14 <= z <= 16:
            put(x, 11, z, WASSER)
        else:
            put(x, 11, z, QUARZ)
put(22, 12, 13, LATERNE)
put(26, 12, 13, LATERNE)
# Liegen auf dem Holzdeck (Lehne im Norden, Blick nach Süden)
for x in (5, 7):
    put(x, 11, 14, QTREPPE['north'])
    put(x, 11, 15, QUNTEN)
put(6, 11, 14, T_AZALEE)
put(8, 11, 16, T_BAMBUS)
# Essplatz draußen x11..15, z14..15
for x in (12, 13, 14):
    put(x, 11, 15, HOCKER)
    put(x, 12, 15, TPLATTE)
    put(x, 11, 14, STUHL['north'])
    put(x, 11, 16, STUHL['south'])
put(13, 13, 15, LATERNE)

# =====================================================================
# Holzlamellen vor den dunklen Wänden (offene Falltüren, je Block Abstand): Tiefe und Schatten
# =====================================================================
for z in (4, 8, 10, 14):
    for y in range(1, 5):
        put(4, y, z, SLAT_W)                      # Erdgeschoss Westseite
for z in (4, 6, 8, 10, 14, 16):
    for y in range(6, 10):
        if leer(3, y, z):
            put(3, y, z, SLAT_W)                  # Obergeschoss Westseite, unter dem Dachüberstand
for x in (9, 11, 16):
    for y in range(2, 5):
        put(x, y, 2, SLAT_N)                      # Erdgeschoss Nordseite über dem Beet
for z in (6, 8, 10, 12):
    for y in (11, 12, 13):
        put(8, y, z, SLAT_W)                      # Penthouse Westseite

# =====================================================================
# Terrasse und Garten y1..
# =====================================================================
# Pool x13..28, z20..26: Quarzrand, Glaskante zum Meer, Wasser innen
for x in range(13, 29):
    for z in range(20, 27):
        rand = x in (13, 28) or z in (20, 26)
        if z == 26 and 13 < x < 28:
            put(x, 1, z, GLAS)
        elif rand:
            put(x, 1, z, QUARZ)
        else:
            put(x, 1, z, WASSER)
# Liegen am Pool (Lehne im Norden, Blick zum Meer)
for x in (15, 17, 23, 25):
    put(x, 1, 17, QTREPPE['north'])
    put(x, 1, 18, QUNTEN)
for x in (16, 24):
    put(x, 1, 17, T_AZALEE)
# Feuerstelle: Bänke um ein Lagerfeuer im Tiefenschiefer-Ring
put(7, 1, 22, FEUER)
for (x, z) in ((6, 21), (7, 21), (8, 21), (6, 22), (8, 22), (6, 23), (7, 23), (8, 23)):
    put(x, 1, z, TSTUFE)
for x in range(5, 10):
    put(x, 1, 20, QTREPPE['north'])
    put(x, 1, 24, QTREPPE['south'])
for z in (21, 22, 23):
    put(4, 1, z, QTREPPE['west'])
put(10, 1, 20, T_FARN)
put(10, 1, 24, T_BAMBUS)
# Wegleuchten (Endstäbe auf Quarzsockel) am Weg, an der Treppe zum Strand
for (x, z) in ((12, 0), (16, 0), (10, 27), (13, 27)):
    put(x, 1, z, SAEULE)
    put(x, 2, z, ENDSTAB)
# Beete vor dem Haus: Farn, Gräser, Blumen
blumen = [FARN, GRAESER, MARGERITE, FARN, KORNBLUME, GRAESER, ALLIUM]
for i, x in enumerate([x for x in range(6, 23) if not 12 <= x <= 16]):
    put(x, 1, 2, blumen[i % len(blumen)])
# Hecke: Landseite, mit Lücken für Weg und Seitenweg
for x in range(3, 30):
    if 12 <= x <= 16:
        continue
    put(x, 1, 1, HECKE)
for z in range(1, 15):
    put(3, 1, z, HECKE)
    if z not in (10, 11):
        put(29, 1, z, HECKE)
for z in (1, 2, 3):
    pass
put(3, 2, 1, AZALEE)
put(29, 2, 1, AZALEE)
put(11, 2, 1, AZALEE)
put(17, 2, 1, AZALEE)
# Steg: Pfosten mit Laternen, Bank am Kopf
for (x, z) in ((10, 30), (13, 30), (10, 34), (13, 34)):
    put(x, 0, z, FPFOSTEN, ueber=True)
    put(x, 1, z, FPFOSTEN)
    put(x, 2, z, LATERNE)
for x in (9, 14):
    put(x, 1, 37, FPFOSTEN)
    put(x, 2, 37, LATERNE)
for x in (10, 11, 12, 13):
    put(x, 1, 37, STUHL['south'])


# Palmen: schlanker Stamm mit leichtem Knick, Krone mit hängenden Wedeln
def palme(x, z, hoehe, knick, arm=3):
    dx, dz = knick
    for y in range(1, hoehe + 1):
        ox = dx if y > hoehe // 2 else 0
        oz = dz if y > hoehe // 2 else 0
        put(x + ox, y, z + oz, PSTAMM)
    cx, cz, top = x + dx, z + dz, hoehe + 1
    put(cx, top, cz, PLAUB)
    for ax, az in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        lang = arm if ax == 0 or az == 0 else arm - 1
        for i in range(1, lang + 1):
            y = top if i < lang else top - 1
            p = (cx + ax * i, y, cz + az * i)
            if leer(*p):
                put(*p, PLAUB)
        p = (cx + ax * lang, top - 2, cz + az * lang)
        if lang == arm and arm >= 3 and leer(*p):
            put(*p, PLAUB)


palme(3, 19, 7, (0, 0))
palme(29, 21, 8, (0, 0))
palme(30, 5, 6, (0, 0), arm=2)

# =====================================================================
model = {'format': 1, 'size': {'x': X, 'y': Y, 'z': Z}, 'palette': P,
         'layers': [[''.join(G.get((x, y, z), '.') for x in range(X)) for z in range(Z)] for y in range(Y)]}
n = {}
for k in G.values():
    n[k] = n.get(k, 0) + 1
name = {e['key']: e['name'] for e in P}
vorh = {e['key'] for e in P if 'vorhanden' in (e.get('flags') or [])}
print('Blöcke', sum(v for k, v in n.items() if k not in vorh), 'Blockarten', len([k for k in n if k not in vorh]))
os.makedirs(ZIEL, exist_ok=True)
with open(os.path.join(ZIEL, 'model.json'), 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False)
    f.write('\n')
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'villa_ausbau_zaehlung.json'), 'w', encoding='utf-8') as f:
    json.dump({name[k]: v for k, v in sorted(n.items(), key=lambda t: -t[1])}, f, ensure_ascii=False, indent=0)
