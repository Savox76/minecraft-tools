"""Unterirdischer Basar – große Handelshalle für 16 Dorfbewohner (Idee Nr. 117).

Leitbild: ein Basar unter der Erde. Gewölbe aus Schlammziegeln mit Gurtbögen aus Sandstein, warmes Licht aus
Laternen und Pilzlicht, bunte Markisen über jedem Stand, Teppiche, ein Brunnen in der Mitte.

Technik (Java und Bedrock):
- Jeder Dorfbewohner steht in einer 1 × 1 Zelle. Davor sein Arbeitsblock als Ladentheke. Darüber ein Spalt
  zum Handeln und ein Sturz, damit niemand auf die Theke klettern und herauslaufen kann.
- Alle 13 Berufe sind vertreten, dazu drei weitere Bibliothekare (4 insgesamt).
- Heilstation am Nordende: Heilzelle, Zombiezelle, dazwischen eine Eisentür mit Hebel. Ein geheilter
  Dorfbewohner behält seine niedrigen Preise auch nach dem Umzug in seinen Stand.

Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Hallenboden.
Aufruf: python tools/bau_handelshalle_basar.py builds/handelshalle-basar [zaehlung.json]
"""
import json
import math
import os
import sys

ZIEL = sys.argv[1]
X, Y, Z = 17, 13, 38

P = []
ZEICHEN = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&*+-/:;<=>?@^_~' +
               ''.join(chr(c) for c in range(0xC0, 0x100) if c not in (0xD7, 0xF7)))
RICHT = {'north': 'Norden', 'south': 'Süden', 'east': 'Osten', 'west': 'Westen'}
VIER = ('north', 'east', 'south', 'west')


def block(name, mc, farbe, flags=None):
    e = {'key': next(ZEICHEN), 'name': name, 'block': mc, 'color': farbe}
    if flags:
        e['flags'] = flags
    P.append(e)
    return e['key']


SCHLAMM = block('Schlammziegel', 'minecraft:mud_bricks', '#8c6a50')
SANDST = block('Glatter Sandstein', 'minecraft:smooth_sandstone', '#e0d3a3')
GEMEISSELT = block('Gemeißelter Sandstein', 'minecraft:chiseled_sandstone', '#d9c78c')
SS_OBEN = block('Glatte-Sandstein-Stufe (oben)', 'minecraft:smooth_sandstone_slab[type=top]', '#e0d3a3')
SS_UNTEN = block('Glatte-Sandstein-Stufe (unten)', 'minecraft:smooth_sandstone_slab[type=bottom]', '#e0d3a3')
COTTO = block('Terrakotta', 'minecraft:terracotta', '#a35f45')
WEISSE_T = block('Weiße Terrakotta', 'minecraft:white_terracotta', '#d4b6a6')
PILZ = block('Pilzlicht', 'minecraft:shroomlight', '#f0a04b')
KETTE = block('Kette', 'minecraft:chain[axis=y]', '#4a4f57')
HAENGE = block('Laterne (hängend)', 'minecraft:lantern[hanging=true]', '#f2b33d')
LATERNE = block('Laterne', 'minecraft:lantern', '#f2b33d')
WASSER = block('Wasser', 'minecraft:water', '#3f86f0')
GLAS = block('Glas', 'minecraft:glass', '#a9dcec')
TREPPE = {r: block('Schlammziegeltreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:mud_brick_stairs[facing=%s]' % r, '#8c6a50') for r in VIER}
SITZ = {r: block('Sandsteintreppe (hohe Seite nach %s)' % RICHT[r], 'minecraft:sandstone_stairs[facing=%s]' % r, '#d8c88e') for r in VIER}
TEPPICH = block('Roter Teppich', 'minecraft:red_carpet', '#9c3a2e')
TEPPICH2 = block('Oranger Teppich', 'minecraft:orange_carpet', '#d8782e')
TEPPICH3 = block('Gelber Teppich', 'minecraft:yellow_carpet', '#e6c13a')
WOLLE = [block('%s Wolle' % n, 'minecraft:%s_wool' % mc, c) for n, mc, c in (
    ('Rote', 'red', '#9c3a2e'), ('Weiße', 'white', '#e9ecec'), ('Gelbe', 'yellow', '#e6c13a'), ('Blaue', 'blue', '#3c4f9c'),
    ('Orange', 'orange', '#d8782e'), ('Türkise', 'cyan', '#2e8a8f'), ('Magenta', 'magenta', '#b04aa8'), ('Grüne', 'green', '#4f6b2a'))]
TOEPFE = [block(n, mc, c) for n, mc, c in (('Topf mit Kaktus', 'minecraft:potted_cactus', '#5a8a3a'),
                                           ('Topf mit Farn', 'minecraft:potted_fern', '#5c8c3a'),
                                           ('Topf mit Bambus', 'minecraft:potted_bamboo', '#7fae3a'))]
FASS = block('Fass', 'minecraft:barrel[facing=up]', '#8a6438')
TRUHE = block('Truhe (nach Westen)', 'minecraft:chest[facing=west]', '#a5793f')
BRAU = block('Braustand', 'minecraft:brewing_stand', '#6a6a6a')
DORF = block('Dorfbewohner (kein Block)', None, '#8b6b4a', ['kein-block'])
ZOMBIE = block('Zombie mit Namensschild (kein Block)', None, '#4f7a4a', ['kein-block'])
EISENTUER_U = block('Eisentür (unten)', 'minecraft:iron_door[half=lower,facing=north]', '#c9c9c9')
EISENTUER_O = block('Eisentür (oben)', 'minecraft:iron_door[half=upper,facing=north]', '#c9c9c9', ['zweiter-teil'])
HEBEL = block('Hebel (an der Wand, nach Osten)', 'minecraft:lever[face=wall,facing=east]', '#7a6a50')
STUFEN_EINGANG = block('Sandsteintreppe (Eingang, hohe Seite nach Süden)', 'minecraft:sandstone_stairs[facing=south]', '#d8c88e')

# Arbeitsblöcke: (Name, Block, Farbe, Beruf)
def ab(name, mc, farbe):
    return block(name, mc, farbe)


WEST = [  # Theke zeigt nach Osten in den Gang
    ab('Lesepult (Bibliothekar)', 'minecraft:lectern[facing=east]', '#8a6438'),
    ab('Kartentisch (Kartograf)', 'minecraft:cartography_table', '#7a5a36'),
    BRAU,
    ab('Komposter (Bauer)', 'minecraft:composter', '#7a5a36'),
    ab('Fass (Fischer)', 'minecraft:barrel[facing=east]', '#8a6438'),
    ab('Bognertisch (Pfeilmacher)', 'minecraft:fletching_table', '#b39a6a'),
    ab('Kessel (Gerber)', 'minecraft:cauldron', '#4a4a50'),
    None,  # zweiter Bibliothekar
]
WEST[7] = WEST[0]
OST = [  # Theke zeigt nach Westen in den Gang
    ab('Lesepult (Bibliothekar, nach Westen)', 'minecraft:lectern[facing=west]', '#8a6438'),
    ab('Schmelzofen (Rüstungsschmied)', 'minecraft:blast_furnace[facing=west]', '#5d5d62'),
    ab('Räucherofen (Fleischer)', 'minecraft:smoker[facing=west]', '#5d5a55'),
    ab('Steinsäge (Steinmetz)', 'minecraft:stonecutter[facing=west]', '#7d7d7d'),
    ab('Webstuhl (Schäfer)', 'minecraft:loom[facing=west]', '#b39a6a'),
    ab('Schmiedetisch (Werkzeugschmied)', 'minecraft:smithing_table', '#3a3a44'),
    ab('Schleifstein (Waffenschmied)', 'minecraft:grindstone[face=floor,facing=west]', '#7d7d7d'),
    None,
]
OST[7] = OST[0]

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


Z0, Z1 = 9, 36          # Halle von der Südwand bis zur Nordwand
ZELLEN = list(range(14, 29, 2))   # 8 Stände je Seite


# =====================================================================
# Gewölbe und Wände
# =====================================================================
def gew(x):
    """Höhe des Gewölbes über Spalte x (Wand bei x1 und x15)."""
    return 5 + int(round(5 * math.sin(math.pi * (x - 1) / 14)))


RIPPEN = {Z0, 13, 17, 21, 25, 29, Z1}
for z in range(Z0, Z1 + 1):
    rippe = z in RIPPEN
    vorher = None
    for x in range(1, 16):
        y = gew(x)
        k = SANDST if rippe else SCHLAMM
        for yy in ([y] if vorher is None else range(min(y, vorher), max(y, vorher) + 1)):
            put(x, yy, z, k, True)
        vorher = y
    for x in (1, 15):
        for y in range(1, 5):
            put(x, y, z, SANDST if rippe else SCHLAMM, True)
# Pilzlicht im Scheitel, Laternen an Ketten
for z in range(Z0 + 2, Z1, 4):
    put(8, gew(8), z, PILZ, True)
for z in (11, 15, 19, 23, 27, 33):
    for y in range(gew(8) - 2, gew(8)):
        put(8, y, z, KETTE)
    put(8, gew(8) - 3, z, HAENGE)
# Stirnwände
for z in (Z0, Z1):
    for x in range(2, 15):
        for y in range(1, gew(x)):
            if z == Z0 and 7 <= x <= 9 and y <= 4:
                continue                    # Eingang
            if leer(x, y, z):
                put(x, y, z, SANDST if (y in (1, 5) or x in (2, 14)) else SCHLAMM)
put(8, 5, Z0, GEMEISSELT, True)
for x in (7, 9):
    put(x, 4, Z0, SS_OBEN, True)
# Boden
for x in range(1, 16):
    for z in range(Z0, Z1 + 1):
        gang = 4 <= x <= 12
        if gang:
            muster = COTTO if (x + z) % 2 == 0 else WEISSE_T
            put(x, 0, z, SANDST if x in (4, 12) else muster)
        else:
            put(x, 0, z, SANDST)

# =====================================================================
# Stände: Zelle, Theke, Handelsspalt, Sturz, Markise, Licht
# =====================================================================
for seite, (xz, xt, xa, liste) in (('west', (2, 3, 4, WEST)), ('ost', (14, 13, 12, OST))):
    for i, z in enumerate(ZELLEN):
        farbe = WOLLE[i % len(WOLLE)]
        # Zelle
        put(xz, 1, z, DORF)
        put(xz, 3, z, SCHLAMM)
        # Theke = Arbeitsblock, darüber Spalt, darüber Sturz aus Wolle
        put(xt, 1, z, liste[i])
        put(xt, 3, z, farbe)
        # Markise ragt in den Gang
        for x in (xz, xt, xa):
            put(x, 4, z, farbe, True)
        put(xa, 3, z, HAENGE)
    # Trennwände zwischen den Ständen (Pfosten an der Theke)
    for z in range(13, 30, 2):
        for y in range(1, 4):
            put(xz, y, z, SCHLAMM)
            put(xt, y, z, SANDST)
        for x in (xz, xt, xa):
            put(x, 4, z, SANDST, True)

# =====================================================================
# Brunnen in der Mitte des Gangs mit Sitzstufen
# =====================================================================
BX, BZ = 8, 21
for x in range(BX - 2, BX + 3):
    for z in range(BZ - 2, BZ + 3):
        rand = abs(x - BX) == 2 or abs(z - BZ) == 2
        if rand:
            put(x, 1, z, SS_UNTEN if (abs(x - BX) == 2 and abs(z - BZ) == 2) else SANDST)
        else:
            put(x, 0, z, WASSER, True)
put(BX, 0, BZ, SANDST, True)
put(BX, 1, BZ, SANDST)
put(BX, 2, BZ, GEMEISSELT)
put(BX, 3, BZ, WASSER)
for (x, z, r) in ((BX, BZ - 3, 'north'), (BX, BZ + 3, 'south')):
    put(x, 1, z, SITZ[r])

# =====================================================================
# Teppichläufer, Pflanzen, Vorhalle
# =====================================================================
for z in range(Z0 + 1, Z1):
    for x in (7, 9):
        if leer(x, 1, z) and not (BZ - 3 <= z <= BZ + 3):
            put(x, 1, z, TEPPICH)
    if leer(8, 1, z) and not (BZ - 3 <= z <= BZ + 3):
        put(8, 1, z, TEPPICH3 if z % 4 == 0 else TEPPICH2)
for (x, z) in ((2, 10), (14, 10), (2, 12), (14, 12), (4, 30), (12, 30)):
    put(x, 1, z, FASS)
    put(x, 2, z, TOEPFE[(x + z) % 3])
for (x, z) in ((5, 11), (11, 11)):
    for y in (1, 2, 3):
        put(x, y, z, SANDST)
    put(x, 4, z, GEMEISSELT)
    put(x, 5, z, LATERNE)

# =====================================================================
# Nordende: Heilstation (West) und Smaragd-Kasse (Ost)
# =====================================================================
# Heilzelle z31, Eisentür z32, Zombiezelle z33
for z in (30, 34):
    for x in (2, 3):
        for y in range(1, 4):
            put(x, y, z, SCHLAMM)
for z in (31, 32, 33):
    put(2, 3, z, SCHLAMM)
put(2, 1, 31, DORF)
put(3, 1, 31, SANDST)                       # Theke (zum Umziehen abbauen)
put(3, 3, 31, GEMEISSELT)
put(2, 1, 32, EISENTUER_U)
put(2, 2, 32, EISENTUER_O)
for y in (1, 2, 3):
    put(3, y, 32, SANDST)
put(4, 2, 32, HEBEL)
put(2, 1, 33, ZOMBIE)
put(3, 1, 33, GLAS)
put(3, 2, 33, GLAS)
put(3, 3, 33, SANDST)
for x in (2, 3):
    put(x, 4, 31, WOLLE[6], True)
    put(x, 4, 32, WOLLE[6], True)
    put(x, 4, 33, WOLLE[6], True)
put(4, 1, 35, BRAU)
put(5, 1, 35, TRUHE)
# Smaragd-Kasse im Osten
for z in (31, 32, 33):
    put(14, 1, z, FASS)
    put(13, 1, z, SS_OBEN if z != 32 else TRUHE)
put(14, 2, 32, LATERNE)
for z in (31, 33):
    put(13, 2, z, TOEPFE[z % 3])
put(11, 1, 35, SITZ['north'])
put(12, 1, 35, SITZ['north'])

# =====================================================================
# Treppe zur Oberfläche (Süden): Stufen z1..z8 steigen nach Süden an, Tunnel mit Gewölbe
# =====================================================================
for z in range(0, Z0):
    stufe = Z0 - z               # 9 .. 1
    yb = min(stufe, 8)
    for x in (7, 8, 9):
        if z == 0:
            put(x, 8, z, SANDST)
        else:
            put(x, yb, z, STUFEN_EINGANG)
            for y in range(0, yb):
                put(x, y, z, SCHLAMM)
    for x in (6, 10):
        for y in range(0, yb + 4):
            put(x, y, z, SANDST if z % 3 == 0 else SCHLAMM)
    for x in (7, 8, 9):
        put(x, yb + 4, z, SCHLAMM if x != 8 else SANDST)
    if z % 3 == 1:
        put(8, yb + 3, z, HAENGE)
# Portal oben
for x in range(6, 11):
    put(x, 12, 0, GEMEISSELT if x == 8 else SANDST, True)

# =====================================================================
model = {'format': 1, 'size': {'x': X, 'y': Y, 'z': Z}, 'palette': P,
         'layers': [[''.join(G.get((x, y, z), '.') for x in range(X)) for z in range(Z)] for y in range(Y)]}
n = {}
for k in G.values():
    n[k] = n.get(k, 0) + 1
weg = {e['key'] for e in P if set(e.get('flags') or []) & {'vorhanden', 'kein-block', 'zweiter-teil'}}
print('Blöcke', sum(v for k, v in n.items() if k not in weg), 'Blockarten', len([k for k in n if k not in weg]))
P[:] = [e for e in P if e['key'] in n]
os.makedirs(ZIEL, exist_ok=True)
with open(os.path.join(ZIEL, 'model.json'), 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False)
    f.write('\n')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump({NAME[k]: v for k, v in sorted(n.items(), key=lambda t: -t[1])}, f, ensure_ascii=False, indent=0)
