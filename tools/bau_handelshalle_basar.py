"""Unterirdischer Basar – quadratische Handelshalle für 16 Dorfbewohner (Idee Nr. 117).

Leitbild: ein Basar unter der Erde. Quadratischer Saal unter einem Klostergewölbe aus Schlammziegeln mit
Rippen aus Sandstein, warmes Licht aus Pilzlicht und Laternen, bunte Markisen über jedem Stand, Teppiche und ein
Brunnen in der Mitte. Auf jeder Seite vier Stände, dazwischen in der Mitte jeder Seite etwas Besonderes:
Süden der Eingang mit Treppe zur Oberfläche, Norden die Heilstation, Osten die Smaragd-Kasse, Westen eine
Sitzecke.

Technik (Java und Bedrock):
- Jeder Dorfbewohner steht in einer 1 × 1 Zelle an der Außenwand. Davor sein Arbeitsblock als Ladentheke,
  darüber ein Spalt zum Handeln und ein Sturz, damit niemand auf die Theke klettert.
- Alle 13 Berufe, dazu drei weitere Bibliothekare (4 insgesamt).
- Heilstation: Heilzelle und Zombiezelle, dazwischen eine Eisentür mit Hebel.

Koordinaten: x nach Osten, z nach Süden, y nach oben. Ebene 0 = Hallenboden. Mitte der Halle x11 z11.
Aufruf: python tools/bau_handelshalle_basar.py builds/handelshalle-basar [zaehlung.json]
"""
import json
import math
import os
import sys

ZIEL = sys.argv[1]
X, Y, Z = 23, 13, 31
M = 11                       # Mitte
A, B = 1, 21                 # Außenwände

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
TRUHE_S = block('Truhe (nach Süden)', 'minecraft:chest[facing=south]', '#a5793f')
DORF = block('Dorfbewohner (kein Block)', None, '#8b6b4a', ['kein-block'])
ZOMBIE = block('Zombie mit Namensschild (kein Block)', None, '#4f7a4a', ['kein-block'])
EISENTUER_U = block('Eisentür (unten)', 'minecraft:iron_door[half=lower,facing=east]', '#c9c9c9')
EISENTUER_O = block('Eisentür (oben)', 'minecraft:iron_door[half=upper,facing=east]', '#c9c9c9', ['zweiter-teil'])
HEBEL = block('Hebel (an der Wand, nach Süden)', 'minecraft:lever[face=wall,facing=south]', '#7a6a50')
STUFEN_EINGANG = block('Sandsteintreppe (Eingang, hohe Seite nach Süden)', 'minecraft:sandstone_stairs[facing=south]', '#d8c88e')
BRAU = block('Braustand', 'minecraft:brewing_stand', '#6a6a6a')
TISCH = block('Glatte-Sandstein-Stufe (Tisch)', 'minecraft:smooth_sandstone_slab[type=top]', '#e0d3a3')

# Arbeitsblöcke je Seite, Theke zeigt jeweils in die Halle
LESE = {r: block('Lesepult (Bibliothekar, nach %s)' % RICHT[r], 'minecraft:lectern[facing=%s]' % r, '#8a6438') for r in ('east', 'west')}
SEITEN = {
    'west': ['L', 'L', block('Kartentisch (Kartograf)', 'minecraft:cartography_table', '#7a5a36'),
             block('Braustand (Kleriker)', 'minecraft:brewing_stand', '#6a6a6a')],
    'north': [block('Komposter (Bauer)', 'minecraft:composter', '#7a5a36'),
              block('Fass (Fischer)', 'minecraft:barrel[facing=south]', '#8a6438'),
              block('Bognertisch (Pfeilmacher)', 'minecraft:fletching_table', '#b39a6a'),
              block('Kessel (Gerber)', 'minecraft:cauldron', '#4a4a50')],
    'east': ['L', 'L', block('Schmelzofen (Rüstungsschmied)', 'minecraft:blast_furnace[facing=west]', '#5d5d62'),
             block('Räucherofen (Fleischer)', 'minecraft:smoker[facing=west]', '#5d5a55')],
    'south': [block('Steinsäge (Steinmetz)', 'minecraft:stonecutter[facing=north]', '#7d7d7d'),
              block('Webstuhl (Schäfer)', 'minecraft:loom[facing=north]', '#b39a6a'),
              block('Schmiedetisch (Werkzeugschmied)', 'minecraft:smithing_table', '#3a3a44'),
              block('Schleifstein (Waffenschmied)', 'minecraft:grindstone[face=floor,facing=north]', '#7d7d7d')],
}
SEITEN['west'] = [LESE['east'] if k == 'L' else k for k in SEITEN['west']]
SEITEN['east'] = [LESE['west'] if k == 'L' else k for k in SEITEN['east']]

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


def seite_pos(seite, s, tiefe):
    """Koordinate (x, z) auf einer Seite: s läuft an der Wand entlang, tiefe = Abstand zur Außenwand (1 = Zelle)."""
    if seite == 'west':
        return (A + tiefe, s)
    if seite == 'east':
        return (B - tiefe, s)
    if seite == 'north':
        return (s, A + tiefe)
    return (s, B - tiefe)


# =====================================================================
# Klostergewölbe: Höhe hängt vom Abstand zur Mitte ab (max von dx, dz), Rippen auf den Diagonalen und Achsen
# =====================================================================
def hoehe(x, z):
    m = max(abs(x - M), abs(z - M))
    return 5 + int(round(6 * math.cos(math.pi * m / 20)))


for x in range(A, B + 1):
    for z in range(A, B + 1):
        h = hoehe(x, z)
        dx, dz = abs(x - M), abs(z - M)
        rippe = dx == dz or dx == 0 or dz == 0
        k = SANDST if rippe else SCHLAMM
        # Lücken zum Nachbarn schließen, damit die Schale dicht ist
        tief = min([h] + [hoehe(x + a, z + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))
                          if A <= x + a <= B and A <= z + b <= B])
        for y in range(tief, h + 1):
            put(x, y, z, k, True)
# Oculus aus Pilzlicht im Scheitel
for x in (M - 1, M, M + 1):
    for z in (M - 1, M, M + 1):
        put(x, hoehe(x, z), z, PILZ, True)
# Laternen an Ketten über den vier Ecken des Gangs
for (x, z) in ((M - 4, M - 4), (M + 4, M - 4), (M - 4, M + 4), (M + 4, M + 4)):
    h = min(y for y in range(5, Y) if (x, y, z) in G)
    for y in (h - 2, h - 1):
        put(x, y, z, KETTE)
    put(x, h - 3, z, HAENGE)
# Außenwände bis zum Gewölbeansatz
for x in range(A, B + 1):
    for z in range(A, B + 1):
        if x in (A, B) or z in (A, B):
            for y in range(1, hoehe(x, z)):
                ecke = x in (A, B) and z in (A, B)
                put(x, y, z, SANDST if (ecke or y == 1 or (x == M or z == M)) else SCHLAMM)
# Boden
for x in range(A, B + 1):
    for z in range(A, B + 1):
        innen = A + 3 <= x <= B - 3 and A + 3 <= z <= B - 3
        if innen:
            rand = x in (A + 3, B - 3) or z in (A + 3, B - 3)
            put(x, 0, z, SANDST if rand else (COTTO if (x + z) % 2 == 0 else WEISSE_T))
        else:
            put(x, 0, z, SANDST)

# =====================================================================
# 16 Stände: je Seite vier, zwei links und zwei rechts der Mitte
# =====================================================================
STAENDE = (4, 6, 16, 18)
POSTEN = (3, 5, 7, 15, 17, 19)
farbe_nr = 0
for seite in ('west', 'north', 'east', 'south'):
    for i, s in enumerate(STAENDE):
        farbe = WOLLE[farbe_nr % len(WOLLE)]
        farbe_nr += 1
        zx, zz = seite_pos(seite, s, 1)       # Zelle
        tx, tz = seite_pos(seite, s, 2)       # Theke
        ax, az = seite_pos(seite, s, 3)       # erste Reihe im Gang
        put(zx, 1, zz, DORF)
        put(zx, 3, zz, SCHLAMM)
        put(tx, 1, tz, SEITEN[seite][i])
        put(tx, 3, tz, farbe)
        for (x, z) in ((zx, zz), (tx, tz), (ax, az)):
            put(x, 4, z, farbe, True)
        put(ax, 3, az, HAENGE)
    for s in POSTEN:
        for tiefe, k in ((1, SCHLAMM), (2, SANDST)):
            x, z = seite_pos(seite, s, tiefe)
            for y in range(1, 4):
                put(x, y, z, k, True)
        for tiefe in (1, 2, 3):
            x, z = seite_pos(seite, s, tiefe)
            put(x, 4, z, SANDST, True)

# =====================================================================
# Brunnen in der Mitte mit vier Bänken
# =====================================================================
for x in range(M - 2, M + 3):
    for z in range(M - 2, M + 3):
        rand = abs(x - M) == 2 or abs(z - M) == 2
        if rand:
            put(x, 1, z, SS_UNTEN if (abs(x - M) == 2 and abs(z - M) == 2) else SANDST)
        else:
            put(x, 0, z, WASSER, True)
put(M, 0, M, SANDST, True)
put(M, 1, M, SANDST)
put(M, 2, M, SANDST)
put(M, 3, M, GEMEISSELT)
put(M, 4, M, WASSER)
for (x, z, r) in ((M, M - 4, 'north'), (M, M + 4, 'south'), (M - 4, M, 'west'), (M + 4, M, 'east')):
    put(x, 1, z, SITZ[r])
# Teppiche: Läufer vom Eingang, Ring um den Brunnen
for z in range(M + 3, B):
    for x in (M - 1, M + 1):
        if leer(x, 1, z) and z != M + 4:
            put(x, 1, z, TEPPICH)
    if leer(M, 1, z):
        put(M, 1, z, TEPPICH3 if z % 2 else TEPPICH2)
for x in range(M - 3, M + 4):
    for z in range(M - 3, M + 4):
        if (abs(x - M) == 3 or abs(z - M) == 3) and leer(x, 1, z):
            put(x, 1, z, TEPPICH2)

# =====================================================================
# Mitte jeder Seite: Süden Eingang, Norden Heilstation, Osten Kasse, Westen Sitzecke
# =====================================================================
# Süden: Eingang (x10..12) mit Bogen, Säulen links und rechts
for x in (M - 1, M, M + 1):
    for y in range(1, 5):
        G.pop((x, y, B), None)
put(M - 1, 4, B, SS_OBEN, True)
put(M + 1, 4, B, SS_OBEN, True)
put(M, 5, B, GEMEISSELT, True)
for x in (M - 3, M + 3):
    for y in (1, 2, 3):
        put(x, y, B - 1, SANDST)
    put(x, 4, B - 1, LATERNE)
for x in (9, 13):
    put(x, 1, B - 2, FASS)
    put(x, 2, B - 2, TOEPFE[x % 3])

# Norden: Heilstation – Heilzelle (x10), Eisentür (x11), Zombiezelle (x12)
for x in (9, 13):
    for y in range(1, 4):
        put(x, y, A + 1, SCHLAMM)
        put(x, y, A + 2, SANDST)
for x in (10, 11, 12):
    put(x, 3, A + 1, SCHLAMM)
put(10, 1, A + 1, DORF)
put(10, 1, A + 2, SANDST)                    # Theke (zum Umziehen abbauen)
put(10, 3, A + 2, GEMEISSELT)
put(11, 1, A + 1, EISENTUER_U)
put(11, 2, A + 1, EISENTUER_O)
for y in (1, 2, 3):
    put(11, y, A + 2, SANDST)
put(11, 2, A + 3, HEBEL)
put(12, 1, A + 1, ZOMBIE)
put(12, 1, A + 2, GLAS)
put(12, 2, A + 2, GLAS)
put(12, 3, A + 2, SANDST)
for x in range(9, 14):
    for z in (A + 1, A + 2, A + 3):
        put(x, 4, z, WOLLE[6] if x in (10, 11, 12) else SANDST, True)
put(8, 1, A + 2, BRAU)
put(14, 1, A + 2, TRUHE_S)
put(11, 3, A + 3, HAENGE)

# Osten: Smaragd-Kasse – Theke mit Truhe, Fässer an der Wand
for z in range(9, 14):
    put(B - 1, 1, z, FASS)
for z in (10, 11, 12):
    put(B - 3, 1, z, SS_OBEN if z != M else TRUHE)
put(B - 1, 2, M, LATERNE)
for z in (10, 12):
    put(B - 3, 2, z, TOEPFE[z % 3])
put(B - 2, 1, 9, SITZ['north'])

# Westen: Sitzecke mit Tisch und Pflanzen
for z in (10, 11, 12):
    put(A + 1, 1, z, SITZ['west'])
put(A + 2, 1, 9, SITZ['north'])
put(A + 2, 1, 13, SITZ['south'])
put(A + 3, 1, M, TISCH)
put(A + 3, 2, M, LATERNE)
for z in (9, 13):
    put(A + 1, 1, z, FASS)
    put(A + 1, 2, z, TOEPFE[z % 3])

# =====================================================================
# Treppe zur Oberfläche im Süden (z22..30), Tunnel mit Gewölbe
# =====================================================================
for z in range(B + 1, Z):
    yb = min(z - B, 8)
    for x in (M - 1, M, M + 1):
        if z == Z - 1:
            put(x, 8, z, SANDST)
        else:
            put(x, yb, z, STUFEN_EINGANG)
        for y in range(0, yb):
            put(x, y, z, SCHLAMM)
    for x in (M - 2, M + 2):
        for y in range(0, yb + 4):
            put(x, y, z, SANDST if z % 3 == 0 else SCHLAMM)
    for x in (M - 1, M, M + 1):
        put(x, yb + 4, z, SANDST if x == M else SCHLAMM)
    if z % 3 == 1:
        put(M, yb + 3, z, HAENGE)
for x in range(M - 2, M + 3):
    put(x, 12, Z - 1, GEMEISSELT if x == M else SANDST, True)

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
