"""Gründerzeit-Villa – Ausbau-Version (verfeinert wie ein Creator).

Leitbild: reich verziert. Gesimse, Erker, Stuck aus Stufen und Treppen, Gauben mit Dachrinnen, schmiedeeiserner
Zaun, Vorgarten. Tiefe durch Vor- und Rücksprünge.

Die Grundidee bleibt: Backstein mit weißen Gesimsen, steiles Dach mit Gauben und Kaminen, Veranda im Süden und ein
achteckiger Eckturm mit spitzem Helm. Gleicher Ursprung und dieselben Geschosshöhen wie die Grundversion
(Haus x2..22 z4..18, Turm um x21 z18, Erdgeschoss y1..5, Decke y6, Obergeschoss y7..11).
Neu: Zwerchhaus im Norden, zweigeschossiger Erker im Westen, Fensterrahmungen mit Verdachungen, Zahnschnitt,
Schieferdach mit Dachrinnen und Fallrohren, Zierfachwerk in den Giebeln, Balkon über der Veranda,
geschwungener Turmhelm, eingerichtete Räume, Vorgarten mit Eisenzaun.

Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Boden.
Aufruf: python tools/ausbau_villa_gruenderzeit.py builds/villa-gruenderzeit/ausbau [zaehlung.json]
"""
import json
import os
import sys

ZIEL = sys.argv[1]
X, Y, Z = 30, 39, 32

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


def je_richtung(name, mc, farbe, flags=None):
    return {r: block(name % RICHT[r], mc % r, farbe, flags) for r in VIER}


GRAS = block('Gras (vorhanden)', 'minecraft:grass_block', '#7c9a4c', ['vorhanden'])
ZIEGEL = block('Ziegel', 'minecraft:bricks', '#9a5444')
STEIN = block('Steinziegel', 'minecraft:stone_bricks', '#8a8a86')
SOCKEL_T = je_richtung('Steinziegeltreppe (hohe Seite nach %s)', 'minecraft:stone_brick_stairs[facing=%s]', '#8a8a86')
SSTUFE = block('Steinziegelstufe (oben)', 'minecraft:stone_brick_slab[type=top]', '#8a8a86')
DIORIT = block('Polierter Diorit', 'minecraft:polished_diorite', '#d8d8d6')
D_TREPPE = je_richtung('Polierte-Diorit-Treppe (verkehrt, hohe Seite nach %s)', 'minecraft:polished_diorite_stairs[facing=%s,half=top]', '#d8d8d6')
D_OBEN = block('Polierte-Diorit-Stufe (oben)', 'minecraft:polished_diorite_slab[type=top]', '#d8d8d6')
D_UNTEN = block('Polierte-Diorit-Stufe (unten)', 'minecraft:polished_diorite_slab[type=bottom]', '#d8d8d6')
KALZIT = block('Kalzit', 'minecraft:calcite', '#e3e4df')
SCHIEFER = block('Tiefenschiefer-Ziegel', 'minecraft:deepslate_tiles', '#3c3c44')
S_TREPPE = je_richtung('Tiefenschiefer-Ziegeltreppe (hohe Seite nach %s)', 'minecraft:deepslate_tile_stairs[facing=%s]', '#45454e')
S_STUFE = block('Tiefenschiefer-Ziegelstufe', 'minecraft:deepslate_tile_slab[type=bottom]', '#45454e')
RINNE = block('Eisenfalltür (Dachrinne)', 'minecraft:iron_trapdoor[half=top]', '#c9c9c9')
ROHR = block('Kette (Fallrohr)', 'minecraft:chain[axis=y]', '#4a4f57')
SCHEIBE = block('Glasscheibe', 'minecraft:glass_pane', '#bfe6f2')
GITTER = block('Eisengitter', 'minecraft:iron_bars', '#8d9196')
BALKEN_Y = block('Dunkler Eichenstamm', 'minecraft:dark_oak_log[axis=y]', '#3e2c1c')
BALKEN_X = block('Dunkler Eichenstamm (liegend, Ost-West)', 'minecraft:dark_oak_log[axis=x]', '#3e2c1c')
BALKEN_Z = block('Dunkler Eichenstamm (liegend, Nord-Süd)', 'minecraft:dark_oak_log[axis=z]', '#3e2c1c')
DEICHE = block('Dunkle Eichenholzbretter', 'minecraft:dark_oak_planks', '#4a3221')
FICHTE = block('Fichtenholzbretter', 'minecraft:spruce_planks', '#7a5a36')
DZAUN = block('Dunkler Eichenzaun', 'minecraft:dark_oak_fence', '#4a3221')
KONSOLE = je_richtung('Dunkle Eichentreppe (verkehrt, hohe Seite nach %s)', 'minecraft:dark_oak_stairs[facing=%s,half=top]', '#4a3221')
TREPPE = je_richtung('Dunkle Eichentreppe (hohe Seite nach %s)', 'minecraft:dark_oak_stairs[facing=%s]', '#4a3221')
DSTUFE_O = block('Dunkle-Eichen-Stufe (oben)', 'minecraft:dark_oak_slab[type=top]', '#4a3221')
TUER = {r: (block('Dunkle Eichentür (unten, Tür nach %s)' % RICHT[r], 'minecraft:dark_oak_door[half=lower,facing=%s]' % r, '#4a3221'),
            block('Dunkle Eichentür (oben, Tür nach %s)' % RICHT[r], 'minecraft:dark_oak_door[half=upper,facing=%s]' % r, '#4a3221', ['zweiter-teil']))
        for r in VIER}
TOR = block('Dunkles Eichenzauntor (nach Süden)', 'minecraft:dark_oak_fence_gate[facing=south]', '#4a3221')
LATERNE = block('Laterne', 'minecraft:lantern', '#f2b33d')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
MAST = block('Polierte-Schwarzstein-Mauer', 'minecraft:polished_blackstone_wall', '#35303a')
BLITZ = block('Blitzableiter', 'minecraft:lightning_rod', '#c47a4a')
WEG = block('Glatter Stein', 'minecraft:smooth_stone', '#a3a6a8')
KIES = block('Kies', 'minecraft:gravel', '#8f8984')
# Einrichtung
FEUER = block('Lagerfeuer', 'minecraft:campfire[lit=true]', '#e0782a')
REGAL = block('Bücherregal', 'minecraft:bookshelf', '#9a7a4a')
FASS = block('Fass', 'minecraft:barrel[facing=up]', '#8a6438')
RAEUCHER = block('Räucherofen (nach Süden)', 'minecraft:smoker[facing=south]', '#5d5a55')
KESSEL = block('Kessel mit Wasser', 'minecraft:water_cauldron[level=3]', '#4a4a50')
ROT = block('Roter Teppich', 'minecraft:red_carpet', '#9c3a2e')
GRUEN = block('Grüner Teppich', 'minecraft:green_carpet', '#4f6b2a')
STUHL = je_richtung('Fichtentreppe (hohe Seite nach %s)', 'minecraft:spruce_stairs[facing=%s]', '#7a5a36')
SESSEL = je_richtung('Rote-Netherziegel-Treppe (hohe Seite nach %s)', 'minecraft:red_nether_brick_stairs[facing=%s]', '#5e1f1c')
TPLATTE = DSTUFE_O
LESEPULT = block('Lesepult', 'minecraft:lectern[facing=south]', '#8a6438')
KLAVIER = block('Notenblock', 'minecraft:note_block', '#6b4a32')
UHR = block('Standuhr (Dunkler Eichenstamm)', 'minecraft:dark_oak_wood', '#3e2c1c')
BETT = {r: (block('Rotes Bett (Fußende, Kopf nach %s)' % RICHT[r], 'minecraft:red_bed[part=foot,facing=%s]' % r, '#9c3a2e'),
            block('Rotes Bett (Kopfende, Kopf nach %s)' % RICHT[r], 'minecraft:red_bed[part=head,facing=%s]' % r, '#9c3a2e', ['zweiter-teil']))
        for r in ('north', 'east', 'west')}
# Garten
HECKE = block('Eichenlaub (Buchs)', 'minecraft:oak_leaves[persistent=true]', '#4f7a32')
LINDE_L = block('Dunkles Eichenlaub', 'minecraft:dark_oak_leaves[persistent=true]', '#3f6a2a')
LINDE_S = block('Dunkler Eichenstamm (Baum)', 'minecraft:dark_oak_log', '#3e2c1c')
ROSE_U = block('Rosenstrauch (unten)', 'minecraft:rose_bush[half=lower]', '#b8323a')
ROSE_O = block('Rosenstrauch (oben)', 'minecraft:rose_bush[half=upper]', '#b8323a', ['zweiter-teil'])
PFINGST_U = block('Pfingstrose (unten)', 'minecraft:peony[half=lower]', '#e0a2c4')
PFINGST_O = block('Pfingstrose (oben)', 'minecraft:peony[half=upper]', '#e0a2c4', ['zweiter-teil'])
TULPE = block('Weiße Tulpe', 'minecraft:white_tulip', '#f1f1ea')
T_FARN = block('Topf mit Farn', 'minecraft:potted_fern', '#5c8c3a')
T_ROSE = block('Topf mit Mohn', 'minecraft:potted_poppy', '#c4402e')

G = {}


def name_von(k):
    return next(e['name'] for e in P if e['key'] == k)


def put(x, y, z, k, ueber=False):
    if not (0 <= x < X and 0 <= y < Y and 0 <= z < Z):
        raise SystemExit('außerhalb: %s %s' % ((x, y, z), name_von(k)))
    alt = G.get((x, y, z))
    if alt is not None and alt != k and not ueber:
        raise SystemExit('Konflikt bei %s: %s gegen %s' % ((x, y, z), name_von(alt), name_von(k)))
    G[(x, y, z)] = k


def leer(x, y, z):
    return (x, y, z) not in G


def weg(x, y, z):
    G.pop((x, y, z), None)


def tuer(x, y, z, r):
    put(x, y, z, TUER[r][0], True)
    put(x, y + 1, z, TUER[r][1], True)


def bett(x, y, z, r):
    dx, dz = SCHRITT[r]
    put(x, y, z, BETT[r][0])
    put(x + dx, y, z + dz, BETT[r][1])


def turm_innen(x, z, r=3):
    dx, dz = abs(x - 21), abs(z - 18)
    return max(dx, dz) <= r and dx + dz <= r + 1


def turm_ring(x, z):
    return turm_innen(x, z) and not turm_innen(x, z, 2)


def im_haus(x, z):
    return 2 <= x <= 22 and 4 <= z <= 18


def haus_rand(x, z):
    return im_haus(x, z) and (x in (2, 22) or z in (4, 18))


# =====================================================================
# Wände: Sockel y0..1 Stein, Backstein, Gurtgesims y6, Fries y11
# =====================================================================
ERKER = [(23, z) for z in range(6, 11)] + [(24, z) for z in range(7, 10)]
ERKER_WAND = ((23, 6), (23, 10), (24, 7), (24, 8), (24, 9))
for x in range(X):
    for z in range(Z):
        if im_haus(x, z) or turm_innen(x, z) or (x, z) in ERKER:
            put(x, 0, z, STEIN)
WANDZELLEN = [(x, z) for x in range(X) for z in range(Z)
              if (haus_rand(x, z) and not (turm_innen(x, z, 2))) or turm_ring(x, z)
              or (x, z) in ERKER_WAND]
for x, z in WANDZELLEN:
    for y in range(1, 12):
        if (x, z) in ERKER_WAND and y > 10:
            continue
        k = STEIN if y == 1 else DIORIT if y in (6, 11) else ZIEGEL
        put(x, y, z, k)
# Turm über dem Hausdach weiter bis y24, Bänder bei y12, y18, y24
for x in range(17, 26):
    for z in range(14, 23):
        if turm_ring(x, z):
            for y in range(12, 25):
                put(x, y, z, DIORIT if y in (12, 18, 24) else ZIEGEL)
# Die Erkerwand zum Haus öffnen (Salon und Schlafzimmer sehen in den Erker)
for z in (7, 8, 9):
    for y in list(range(1, 6)) + list(range(7, 11)):
        weg(22, y, z)


# ---- Fenster mit Rahmung: Sturz weiß, Verdachung und Sohlbank außen ----
def fenster(x, z, aussen, y0, y1, verdachung=True):
    dx, dz = SCHRITT[aussen]
    for y in range(y0, y1 + 1):
        put(x, y, z, SCHEIBE, True)
    put(x, y1 + 1, z, DIORIT, True)
    put(x + dx, y0 - 1, z + dz, D_OBEN, True)
    if verdachung:
        put(x + dx, y1 + 1, z + dz, D_TREPPE[GEGEN[aussen]], True)
    # seitliche Faschen aus Diorit
    qx, qz = (1, 0) if aussen in ('north', 'south') else (0, 1)
    for s in (-1, 1):
        if G.get((x + s * qx, y1 + 1, z + s * qz)) == ZIEGEL:
            put(x + s * qx, y1 + 1, z + s * qz, DIORIT, True)


GESCHOSSE = ((2, 4), (7, 9))
for (y0, y1) in GESCHOSSE:
    for x in (4, 7, 10, 12, 14, 17, 20):
        fenster(x, 4, 'north', y0, y1)
    for x in (4, 7, 13, 16):
        fenster(x, 18, 'south', y0, y1)
    for z in (6, 16):
        fenster(2, z, 'west', y0, y1)
    fenster(22, 12, 'east', y0, y1)
    # Erker: drei Fenster vorne, je eins an den Schrägen
    for z in (7, 8, 9):
        fenster(24, z, 'east', y0, y1, verdachung=False)
    fenster(23, 6, 'north', y0, y1, verdachung=False)
    fenster(23, 10, 'south', y0, y1, verdachung=False)
    # Turm: Fenster nach Süden, Osten und Westen
    for (x, z, r) in ((21, 21, 'south'), (24, 18, 'east'), (18, 19, 'west')):
        fenster(x, z, r, y0, y1)
for (x, z, r) in ((21, 21, 'south'), (24, 18, 'east'), (18, 18, 'west')):
    fenster(x, z, r, 14, 16)
for (x, z, r) in ((21, 21, 'south'), (24, 18, 'east'), (18, 18, 'west'), (21, 15, 'north')):
    fenster(x, z, r, 20, 22)
# Haustür mit Oberlicht und Balkontür darüber
tuer(10, 1, 18, 'north')
put(10, 3, 18, SCHEIBE, True)
put(10, 4, 18, SCHEIBE, True)
put(10, 5, 18, DIORIT, True)
tuer(10, 7, 18, 'north')
put(10, 9, 18, SCHEIBE, True)
put(10, 10, 18, DIORIT, True)

# ---- Gurtgesims y6 und Sockelschräge y1, außen umlaufend ----
def aussen_ring(y, k_fn, nur_haus=True):
    for x in range(X):
        for z in range(Z):
            if not leer(x, y, z):
                continue
            if im_haus(x, z) or turm_innen(x, z) or (x, z) in ERKER:
                continue
            if 4 <= x <= 16 and 19 <= z <= 22:
                continue                          # Veranda
            for r in VIER:
                dx, dz = SCHRITT[r]
                nx, nz = x - dx, z - dz          # Nachbar in Richtung Haus
                if (nx, nz) in WANDZELLEN and not leer(nx, y, nz):
                    k = k_fn(r)
                    if k:
                        put(x, y, z, k)
                    break


aussen_ring(6, lambda r: D_TREPPE[GEGEN[r]])
aussen_ring(1, lambda r: SOCKEL_T[GEGEN[r]])

# =====================================================================
# Decken y6 innen
# =====================================================================
TREPPENLOCH = {(8, z) for z in range(10, 14)}
for x in range(X):
    for z in range(Z):
        innen = (im_haus(x, z) and not haus_rand(x, z)) or turm_innen(x, z, 2) or (x, z) in ((23, 7), (23, 8), (23, 9), (22, 7), (22, 8), (22, 9))
        if innen and leer(x, 6, z) and (x, z) not in TREPPENLOCH and (x, z) != (8, 9):
            put(x, 6, z, FICHTE)
# Turmböden y12 und y18
for x in range(17, 26):
    for z in range(14, 23):
        if turm_innen(x, z, 2):
            put(x, 12, z, FICHTE)
            put(x, 18, z, FICHTE)

# =====================================================================
# Schieferdach: Satteldach, First in Ost-West-Richtung bei z11, Überstand 1, Zierfachwerk in den Giebeln
# =====================================================================
def dach_y(z):
    return 11 + min(z - 3, 19 - z)


for x in range(1, 24):
    for z in range(3, 20):
        if turm_innen(x, z):
            continue
        y = dach_y(z)
        k = SCHIEFER if z == 11 else S_TREPPE['south' if z < 11 else 'north']
        put(x, y, z, k, True)
    put(x, 20, 11, S_STUFE)
# Giebelwände x2 / x22 unter dem Dach: Kalzit mit Fachwerk aus dunkler Eiche
for x in (2, 22):
    for z in range(4, 19):
        if turm_innen(x, z):
            continue
        for y in range(12, dach_y(z)):
            if y == 12 or z in (5, 8, 11, 14, 17) or y == 16:
                k = BALKEN_Z if y in (12, 16) else BALKEN_Y
            else:
                k = KALZIT
            put(x, y, z, k)
    for z in (10, 11, 12):
        for y in (14, 15):
            put(x, y, z, SCHEIBE, True)
# Ortgang-Brett: Diorit-Stufen auf der Giebelkante
for z in range(3, 20):
    for x in (1, 23):
        if not turm_innen(x, z) and leer(x, dach_y(z) - 1, z) and dach_y(z) - 1 >= 11:
            put(x, dach_y(z) - 1, z, D_OBEN)

# ---- Zwerchhaus im Norden: Giebel x9..15 steigt aus der Wand, eigenes Dach, Fachwerk ----
def zw_y(x):
    return 11 + min(x - 8, 16 - x)


for x in range(8, 17):
    yc = zw_y(x)
    zmax = 3
    while dach_y(zmax + 1) < yc:
        zmax += 1
    for z in range(3, zmax + 1):
        for y in range(dach_y(z), yc):
            weg(x, y, z)                      # Hausdach unter dem Zwerchhaus entfernen
        k = SCHIEFER if x == 12 else S_TREPPE['east' if x < 12 else 'west']
        put(x, yc, z, k, True)
    if 9 <= x <= 15:
        for y in range(12, yc):
            k = BALKEN_X if y in (12, 15) else BALKEN_Y if x in (9, 15) else KALZIT
            put(x, y, 4, k, True)
for x in (11, 12, 13):
    put(x, 12, 4, SCHEIBE, True)
    put(x, 13, 4, SCHEIBE, True)
put(12, 16, 3, BLITZ)
# Seitenwände des Zwerchhauses
for z in range(5, 8):
    for x in (9, 15):
        for y in range(dach_y(z) + 1, zw_y(x)):
            put(x, y, z, KALZIT, True)


# ---- Gauben im Süden und Norden: Fenster, Wangen, eigenes Satteldach ----
def gaube(a, seite):
    f = 16 if seite == 'south' else 6            # Vorderwand
    innen = -1 if seite == 'south' else 1        # Richtung zum First
    yb = dach_y(f)                               # Fensterunterkante
    for z in (f, f + innen, f + 2 * innen):
        for x in (a, a + 1, a + 2):
            for y in range(yb, yb + 3):
                weg(x, y, z)
    for y in (yb, yb + 1):
        put(a, y, f, DIORIT)
        put(a + 2, y, f, DIORIT)
        put(a + 1, y, f, SCHEIBE)
        for z in (f + innen, f + 2 * innen):
            put(a, y, z, ZIEGEL)
            put(a + 2, y, z, ZIEGEL)
    for z in (f - innen, f, f + innen, f + 2 * innen):
        put(a, yb + 2, z, S_TREPPE['east'], True)
        put(a + 2, yb + 2, z, S_TREPPE['west'], True)
        put(a + 1, yb + 2, z, SCHIEFER, True)
        put(a + 1, yb + 3, z, S_STUFE, True)
    put(a + 1, yb - 1, f - innen, D_OBEN, True)


for a in (5, 13):
    gaube(a, 'south')
for a in (3, 17):
    gaube(a, 'north')

# ---- Dachrinnen und Fallrohre ----
for x in range(1, 24):
    if leer(x, 11, 2):
        put(x, 11, 2, RINNE)
    if not turm_innen(x, 20) and leer(x, 11, 20) and x <= 17:
        put(x, 11, 20, RINNE)
for (x, z) in ((1, 4), (23, 4), (1, 18)):
    for y in range(2, 11):
        if leer(x, y, z):
            put(x, y, z, ROHR)
# Zahnschnitt unter der Traufe
for x in range(2, 23, 2):
    if leer(x, 10, 3):
        put(x, 10, 3, D_OBEN)
    if x <= 16 and leer(x, 10, 19):
        put(x, 10, 19, D_OBEN)

# ---- Schornsteine mit weißem Band und Kragen ----
for (x, z) in ((5, 10), (17, 10)):
    for y in range(dach_y(z), 22):
        put(x, y, z, DIORIT if y == 20 else ZIEGEL, True)
    for r in VIER:
        dx, dz = SCHRITT[r]
        put(x + dx, 21, z + dz, D_UNTEN, True)

# ---- Erker: kleines Schieferdach, zum Haus hin ansteigend ----
for z in range(6, 11):
    put(23, 11, z, D_OBEN if z in (6, 10) else S_TREPPE['west'], True)
for z in (7, 8, 9):
    put(24, 11, z, S_TREPPE['west'])
    put(23, 12, z, S_STUFE)

# ---- Turmhelm: geschwungen, aus Schiefer, mit Blitzableiter ----
HELM = [(25, 4), (26, 3), (27, 3), (28, 2), (29, 2), (30, 2), (31, 1), (32, 1), (33, 1), (34, 1), (35, 0), (36, 0)]
rad = dict(HELM)
for y, r in HELM:
    for x in range(16, 27):
        for z in range(13, 24):
            dx, dz = x - 21, z - 18
            if r == 0:
                if (dx, dz) == (0, 0):
                    put(x, y, z, SCHIEFER)
                continue
            if not turm_innen(x, z, r) or turm_innen(x, z, r - 1):
                continue
            weiter = rad.get(y + 1, -1) < r
            if not weiter:
                put(x, y, z, SCHIEFER)
            elif abs(dx) > abs(dz):
                put(x, y, z, S_TREPPE['west' if dx > 0 else 'east'])
            elif abs(dz) > abs(dx):
                put(x, y, z, S_TREPPE['north' if dz > 0 else 'south'])
            else:
                put(x, y, z, S_STUFE)
put(21, 37, 18, BLITZ)
# Zahnschnitt unter dem Helm
for x in range(16, 27):
    for z in range(13, 24):
        if turm_innen(x, z, 4) and not turm_innen(x, z, 3) and (x + z) % 2 == 0 and leer(x, 24, z):
            put(x, 24, z, D_OBEN)

# =====================================================================
# Veranda mit Balkon
# =====================================================================
for x in range(5, 16):
    for z in range(19, 22):
        put(x, 0, z, DEICHE)
for x in (9, 10, 11):
    put(x, 0, 22, WEG)
for x, z in ((5, 21), (15, 21), (5, 19), (15, 19), (8, 21), (12, 21)):
    for y in (1, 2, 3):
        put(x, y, z, DZAUN)
    put(x, 4, z, BALKEN_Y)
for x in (6, 7, 13, 14):
    put(x, 1, 21, DZAUN)
put(5, 1, 20, DZAUN)
put(15, 1, 20, DZAUN)
# Zierbügel unter dem Dach
for x in (6, 9, 11, 14):
    put(x, 4, 21, KONSOLE['east' if x in (6, 11) else 'west'])
# Dach der Veranda = Balkonboden, Kante aus Diorit
for x in range(5, 16):
    for z in range(19, 23):
        put(x, 5, z, D_OBEN if (x in (5, 15) or z == 22) else DEICHE, True)
for x in range(5, 16):
    put(x, 6, 22, GITTER)
for z in range(19, 22):
    put(5, 6, z, GITTER)
    put(15, 6, z, GITTER)
put(5, 6, 22, DIORIT, True)
put(15, 6, 22, DIORIT, True)
put(5, 7, 22, LATERNE)
put(15, 7, 22, LATERNE)
put(7, 6, 20, STUHL['north'])
put(13, 6, 20, STUHL['north'])
put(10, 4, 20, HAENGE)
put(8, 1, 20, STUHL['south'])
put(12, 1, 20, STUHL['south'])
put(6, 1, 19, T_FARN)
put(14, 1, 19, T_FARN)

# =====================================================================
# Innenwände und Einrichtung
# =====================================================================
def wand(x0, x1, y0, y1, z0, z1, k=ZIEGEL):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if leer(x, y, z):
                    put(x, y, z, k)


for (y0, y1) in ((1, 5), (7, 10)):
    wand(7, 7, y0, y1, 5, 17)
    wand(13, 13, y0, y1, 5, 17)
    wand(14, 21, y0, y1, 10, 10)
    wand(3, 6, y0, y1, 14, 14)
for (x, y, z, r) in ((7, 1, 8, 'west'), (7, 1, 16, 'west'), (13, 1, 7, 'east'), (13, 1, 13, 'east'), (17, 1, 10, 'south'),
                     (7, 7, 8, 'west'), (7, 7, 16, 'west'), (13, 7, 7, 'east'), (13, 7, 13, 'east'), (17, 7, 10, 'south')):
    tuer(x, y, z, r)

# ---- Diele mit großer Treppe (steigt nach Norden entlang x8) ----
for i, z in enumerate(range(14, 8, -1)):
    put(8, 1 + i, z, TREPPE['north'])
    for y in range(1, 1 + i):
        put(8, y, z, DEICHE)
for z in range(10, 14):
    put(9, 7, z, DZAUN)
put(8, 7, 14, DZAUN)
for z in range(9, 18):
    put(10, 1, z, ROT)
    put(11, 1, z, ROT)
put(12, 1, 5, UHR)
put(12, 2, 5, UHR)
put(9, 1, 5, T_FARN)
put(12, 1, 17, T_FARN)
for z in (8, 13):
    put(10, 5, z, HAENGE)
put(11, 5, 16, HAENGE)
# Esszimmer x3..6 z5..13: Kamin an der Nordwand, lange Tafel
for x in (4, 5, 6):
    for y in (1, 2, 3, 4, 5):
        if (x, y) != (5, 1):
            put(x, y, 5, ZIEGEL)
put(5, 1, 5, FEUER)
for x in (4, 5, 6):
    put(x, 3, 6, D_OBEN)
for z in range(8, 12):
    put(4, 1, z, TPLATTE)
    put(5, 1, z, TPLATTE)
    put(3, 1, z, STUHL['west'])
    put(6, 1, z, STUHL['east'])
put(4, 5, 9, HAENGE)
put(5, 5, 10, HAENGE)
put(3, 1, 13, FASS)
put(3, 2, 13, T_ROSE)
# Küche x3..6 z15..17
for z, k in ((15, RAEUCHER), (16, KESSEL), (17, FASS)):
    put(3, 1, z, k)
put(4, 1, 17, FASS)
put(5, 1, 16, TPLATTE)
put(6, 1, 16, STUHL['east'])
put(5, 5, 16, HAENGE)
# Salon x14..21 z5..9 mit Erker: Klavier, Sessel um den Tisch, Sitzplatz im Erker
put(14, 1, 5, KLAVIER)
put(14, 1, 6, STUHL['west'])
put(17, 1, 6, SESSEL['north'])
put(19, 1, 6, SESSEL['north'])
put(18, 1, 7, TPLATTE)
put(17, 1, 8, SESSEL['south'])
put(19, 1, 8, SESSEL['south'])
for x, z in ((17, 7), (19, 7), (18, 6), (18, 8)):
    put(x, 1, z, GRUEN)
put(23, 1, 8, SESSEL['east'])
put(23, 1, 7, T_FARN)
put(23, 1, 9, T_ROSE)
put(21, 1, 5, T_FARN)
put(18, 5, 7, HAENGE)
# Herrenzimmer x14..17 z11..17 mit Bibliothek im Turm
put(15, 1, 13, TPLATTE)
put(15, 1, 14, TPLATTE)
put(15, 2, 13, LATERNE)
put(14, 1, 14, STUHL['west'])
put(16, 1, 12, LESEPULT)
for z in (11, 12):
    for y in (1, 2, 3):
        put(17, y, z, REGAL) if (z, y) != (12, 1) or True else None
put(15, 5, 15, HAENGE)
for x in range(17, 26):
    for z in range(14, 23):
        if turm_innen(x, z, 2) and not turm_innen(x, z, 1):
            for y in (1, 2):
                if leer(x, y, z) and not (z == 15 or x == 18) and (x, z) != (21, 20) and (x, z) != (23, 18):
                    put(x, y, z, REGAL)
put(21, 1, 18, SESSEL['south'])
put(22, 1, 19, SESSEL['east'])
put(21, 5, 18, HAENGE)

# ---- Obergeschoss ----
# Schlafzimmer West x3..6 z5..13 mit Erker
bett(4, 7, 7, 'north')
bett(5, 7, 7, 'north')
put(3, 7, 5, FASS)
put(3, 8, 5, LATERNE)
put(6, 7, 5, FASS)
for x, z in ((3, 9), (4, 9), (5, 9), (6, 9), (4, 8), (5, 8)):
    put(x, 7, z, ROT)
put(6, 7, 11, FASS)
put(6, 7, 13, FASS)
# Bad x3..6 z15..17
put(3, 7, 16, KESSEL)
put(3, 7, 17, KESSEL)
put(6, 7, 17, KESSEL)
put(5, 7, 15, T_FARN)
# Flur oben mit Galerie
for z in range(9, 18):
    put(11, 7, z, ROT)
put(12, 7, 5, REGAL)
put(12, 8, 5, REGAL)
put(10, 7, 5, SESSEL['north'])
# Schlafzimmer Ost x14..21 z5..9
bett(17, 7, 7, 'north')
bett(18, 7, 7, 'north')
put(16, 7, 5, FASS)
put(16, 8, 5, LATERNE)
put(19, 7, 5, FASS)
put(23, 7, 8, SESSEL['east'])
put(23, 7, 7, TPLATTE)
put(23, 8, 7, LATERNE)
for x in range(16, 20):
    put(x, 7, 8, GRUEN)
# Kinderzimmer x14..17 z11..17
bett(16, 7, 12, 'east')
bett(16, 7, 15, 'east')
put(14, 7, 17, REGAL)
put(14, 7, 11, FASS)
put(14, 8, 11, LATERNE)
# Turmzimmer oben: Lesezimmer
put(21, 7, 18, SESSEL['south'])
put(22, 7, 19, TPLATTE)
put(22, 8, 19, LATERNE)
for x, z in ((20, 17), (21, 17), (22, 17), (20, 19), (20, 20)):
    put(x, 7, z, GRUEN)

# =====================================================================
# Vorgarten mit Eisenzaun, Rosen, Buchs, Linde, Laternen
# =====================================================================
for x in range(0, 30):
    for z in (31,):
        if 9 <= x <= 11:
            continue
        pfeiler = x % 4 == 0 or x in (8, 12, 29)
        put(x, 1, z, STEIN)
        put(x, 2, z, ZIEGEL if pfeiler else GITTER)
        if pfeiler:
            put(x, 3, z, ZIEGEL)
            put(x, 4, z, SSTUFE)
for z in range(22, 31):
    for x in (0, 29):
        pfeiler = z % 4 == 3
        put(x, 1, z, STEIN)
        put(x, 2, z, ZIEGEL if pfeiler else GITTER)
        if pfeiler:
            put(x, 3, z, ZIEGEL)
            put(x, 4, z, SSTUFE)
for x in (8, 12):
    put(x, 5, 31, LATERNE)
for x in (9, 10, 11):
    put(x, 1, 31, TOR) if x != 10 else None
# Weg zum Haus, Kiesrand
for z in range(23, 32):
    for x in (9, 10, 11):
        put(x, 0, z, WEG)
    put(8, 0, z, KIES)
    put(12, 0, z, KIES)
# Beete mit Buchs-Einfassung und Rosen
for (x0, x1) in ((2, 6), (14, 18)):
    for z in range(24, 30):
        for x in range(x0, x1 + 1):
            rand = x in (x0, x1) or z in (24, 29)
            if rand:
                put(x, 1, z, HECKE)
            elif (x + z) % 2 == 0:
                put(x, 1, z, ROSE_U if x0 == 2 else PFINGST_U)
                put(x, 2, z, ROSE_O if x0 == 2 else PFINGST_O)
            else:
                put(x, 1, z, TULPE)
# Linde mit Bank
for y in range(1, 6):
    put(24, y, 27, LINDE_S)
for y in range(5, 10):
    r = 3 if y in (6, 7) else 2
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r + 1 and leer(24 + dx, y, 27 + dz) and 0 <= 27 + dz < Z and 24 + dx < 29:
                put(24 + dx, y, 27 + dz, LINDE_L)
put(22, 1, 28, STUHL['east'])
put(22, 1, 27, STUHL['east'])
# Gaslaternen am Weg
for (x, z) in ((7, 23), (13, 23)):
    for y in (1, 2, 3):
        put(x, y, z, MAST)
    put(x, 4, z, LATERNE)
# Rasen
for x in range(X):
    for z in range(Z):
        if leer(x, 0, z):
            put(x, 0, z, GRAS)

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
