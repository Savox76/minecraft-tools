"""Vorgerenderte Seiten für Suchmaschinen, auf Deutsch und Englisch.

Pro Adresse entsteht eigenes HTML mit vollständigem Text, Meta-Daten, hreflang und JSON-LD.
Dazu Vorschaubilder, Sitemap, robots.txt, 404-Seite und IndexNow-Schlüssel.
Im Browser ersetzt site/js/app.js den Inhalt danach durch die interaktive Ansicht.
"""
import html, json, os, re
from datetime import date
from urllib.parse import urlparse

H = html.escape
SPRACHEN = ('de', 'en')
SEG = {
    'de': {'liste': 'bauplaene', 'bau': 'bau', 'plugins': 'plugins', 'plugin': 'plugin',
           'anleitungen': 'anleitungen', 'anleitung': 'anleitung', 'wuensche': 'wuensche', 'geplant': 'geplant'},
    'en': {'liste': 'builds', 'bau': 'build', 'plugins': 'plugins', 'plugin': 'plugin',
           'anleitungen': 'guides', 'anleitung': 'guide', 'wuensche': 'wishes', 'geplant': 'planned'},
}


def pfad(lang, art='start', id=None):
    vor = '' if lang == 'de' else 'en/'
    if art == 'start':
        return vor
    return vor + SEG[lang][art] + '/' + (id + '/' if id else '')


def kurz(text, n=158):
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) <= n else text[:n - 1].rsplit(' ', 1)[0] + '…'


def fmt(n, lang='de'):
    return f'{n:,}'.replace(',', '.' if lang == 'de' else ',')


def stacks(n, lang='de'):
    s, r = divmod(n, 64)
    st = 'St.' if lang == 'de' else 'st.'
    return f'{s} {st} + {r}' if s and r else (f'{s} {st}' if s else str(r))


# ---------------------------------------------------------------- Bilder

def form(n):
    """Gleiche Formen wie shapeOf() in site/js/render.js."""
    for f, rx in (('mob', r'Dorfbewohner'), ('flat', r'Redstonestaub|Seerosenblatt|Teppich|Blütenblätter'), ('low', r'Komparator|Verstärker'),
                  ('crop', r'Karotten|Kartoffeln'), ('bed', r'Bett'), ('plate', r'Falltür'), ('panel', r'(?i)zauntor|tür'),
                  ('thin', r'(?i)zaun|mauer|eisengitter|blitzableiter|laterne|leiter|fackel|bambus'), ('pane', r'Glasscheibe'),
                  ('slab', r'Stufe'), ('glass', r'^Glas$'), ('water', r'Wasser|Meer')):
        if re.search(rx, n):
            return f
    return 'full'


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def zeichne_modell(model, breite, hoehe, schnitt=False, fuellung=.92, schatten=False):
    """Isometrisches Bild des fertigen Bauwerks mit transparentem Hintergrund.
    Nutzt tools/vorschau.py (echte Blockformen aus den Zuständen), genau wie site/js/render.js im Browser.
    schnitt: Decke und vordere Wände ausblenden (Keller)."""
    import copy
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from vorschau import zeichne
    if schnitt:
        model = copy.deepcopy(model)
        X, Z = model['size']['x'], model['size']['z']
        weg = {p['key'] for p in model['palette'] if '(Decke)' in p['name']}
        wand = {p['key'] for p in model['palette'] if '(Wand)' in p['name']}
        model['layers'] = [[''.join('.' if ch in weg or (ch in wand and (x == X - 1 or z == Z - 1)) else ch
                                    for x, ch in enumerate(r)) for z, r in enumerate(e)] for e in model['layers']]
    return zeichne(model, breite, hoehe, fuellung=fuellung, schatten=schatten)


def landschaft(nacht=False, spalten=240, zeilen=22, B=8):
    """Blockige Landschaft im Minecraft-Stil (eigene Farben, keine Texturen von Mojang).

    Von links nach rechts: Meer, Strand mit Leuchtturm, Wiese mit Haus und Feld, Wald, Berge mit Schnee,
    am rechten Rand wieder hinunter zum Wasser, damit sich das Bild nahtlos wiederholen lässt.
    Ein Block ist B Pixel groß; die Website zeigt das Bild pixelgenau (image-rendering: pixelated).
    """
    import math, random
    from PIL import Image, ImageDraw
    W, H = spalten * B, zeilen * B
    img = Image.new('RGB', (W, H))
    g = ImageDraw.Draw(img, 'RGBA')      # RGBA-Farben werden auf dem RGB-Bild überblendet
    rnd = random.Random(11)

    def ton(c, f):
        return tuple(max(0, min(255, int(v * f))) for v in c[:3])

    def nf(c):
        """Farbe bei Nacht: dunkler und bläulich."""
        if not nacht:
            return tuple(c[:3])
        r, gg, b = c[:3]
        return (int(r * .42 + 8), int(gg * .46 + 12), int(b * .56 + 34))

    # ---- Himmel
    oben, unten = ((10, 20, 44), (36, 58, 98)) if nacht else ((118, 176, 236), (204, 230, 250))
    for y in range(H):
        t = y / (H - 1)
        g.line([(0, y), (W, y)], fill=tuple(int(oben[i] + (unten[i] - oben[i]) * t) for i in range(3)))
    if nacht:
        for _ in range(220):
            x, y = rnd.randrange(W), rnd.randrange(int(H * .7))
            gross = rnd.random() < .18
            hell = rnd.choice((170, 210, 245))
            g.rectangle([x, y, x + (1 if gross else 0), y + (1 if gross else 0)], fill=(hell, hell, min(255, hell + 10)))
        mx, my = 92 * B, 1 * B + 4
        g.rectangle([mx - 3, my - 3, mx + 3 * B + 2, my + 3 * B + 2], fill=(230, 232, 210, 40))
        g.rectangle([mx, my, mx + 3 * B - 1, my + 3 * B - 1], fill=(228, 230, 212))
        for dx, dy in ((4, 5), (14, 12), (7, 16)):
            g.rectangle([mx + dx, my + dy, mx + dx + 3, my + dy + 3], fill=(198, 200, 184))
    else:
        sx, sy = 92 * B, 1 * B + 4
        g.rectangle([sx - 4, sy - 4, sx + 3 * B + 3, sy + 3 * B + 3], fill=(255, 238, 160, 110))
        g.rectangle([sx, sy, sx + 3 * B - 1, sy + 3 * B - 1], fill=(255, 247, 200))

    for cx, cy, cb, ch in ((8, 4, 10, 1), (44, 2, 12, 1), (110, 3, 9, 1), (156, 1, 14, 2), (208, 3, 11, 1)):
        farbe = (210, 220, 240, 45) if nacht else (255, 255, 255, 240)
        unten_ = (190, 200, 222, 45) if nacht else (222, 233, 245, 255)
        g.rectangle([cx * B, cy * B, (cx + cb) * B - 1, (cy + ch) * B - 1], fill=farbe)
        g.rectangle([(cx + 2) * B, cy * B - B // 2, (cx + cb - 3) * B - 1, cy * B - 1], fill=farbe)
        g.rectangle([cx * B, (cy + ch) * B - 2, (cx + cb) * B - 1, (cy + ch) * B - 1], fill=unten_)

    # ---- Höhen in Blöcken vom unteren Rand
    WASSER = 8
    def hoehe(c):
        if c < 40:                       # Meer (hier steht auf der Website der Name)
            return 3 + (1 if math.sin(c * .9) > .5 else 0)
        if c < 58:                       # Strand steigt an
            return min(9, 4 + (c - 40) // 3)
        if c < 104:                      # Wiese
            return int(round(9.4 + 1.0 * math.sin(c / 7.5) + .6 * math.sin(c / 2.9)))
        if c < 150:                      # Wald, leicht hügelig
            return int(round(10 + 1.6 * math.sin(c / 9) + .8 * math.sin(c / 3.7)))
        if c < 218:                      # Berg
            t = (c - 150) / 68          # zwei Gipfel, der linke höher
            spitze = max(19.5 - abs(t - .36) * 42, 16.5 - abs(t - .72) * 36)
            return int(round(max(10, spitze + .9 * math.sin(c / 2.3))))
        return max(3, int(round(10 - (c - 218) / 22 * 7)))   # hinab zum Wasser (Übergang zum Bildanfang)

    def ferne(c):                        # Bergkette im Dunst
        u = 2 * math.pi * c / spalten          # periodisch, damit die Naht beim Wiederholen nicht auffällt
        v = 11 + 4.5 * abs(math.sin(u * 3)) + 2.2 * math.sin(u * 8)
        return int(round(max(0, min(16, v))))

    def pixelblock(c, r, farbe, alpha=255, rausch=.07, oben=None, rand=None):
        x0, y0 = c * B, H - (r + 1) * B
        for i in range(0, B, 2):
            for j in range(0, B, 2):
                fc = farbe
                if oben is not None and (j < 2 or (j < 4 and rnd.random() < (rand or .45))):
                    fc = oben
                f = 1 + rnd.uniform(-rausch, rausch)
                g.rectangle([x0 + i, y0 + j, x0 + i + 1, y0 + j + 1], fill=nf(ton(fc, f)) + (alpha,))

    hoehen = [hoehe(c) for c in range(spalten)]

    # ---- ferne Berge
    for c in range(spalten):
        hb = ferne(c)
        for r in range(hb):
            dunst = (176, 196, 218) if not nacht else (150, 160, 180)
            fc = (242, 246, 252) if r >= 14 else (140, 146, 156)
            mix = tuple(int(fc[i] * .45 + dunst[i] * .55) for i in range(3))
            x0, y0 = c * B, H - (r + 1) * B
            g.rectangle([x0, y0, x0 + B - 1, y0 + B - 1], fill=nf(mix))

    # ---- Vordergrund
    GRAS, ERDE, STEIN, SAND, SANDST, FELS = (96, 160, 54), (134, 96, 67), (128, 130, 135), (220, 208, 164), (190, 176, 134), (96, 98, 104)
    for c, h in enumerate(hoehen):
        steil = abs(h - hoehen[c - 1]) >= 2 or abs(h - hoehen[(c + 1) % spalten]) >= 2
        for r in range(h):
            if r == 0:
                pixelblock(c, r, FELS)
            elif (c < 58 or c >= 230) and r >= h - 2:
                pixelblock(c, r, SAND)
            elif c < 58 or c >= 230:
                pixelblock(c, r, SANDST)
            elif r == h - 1 and h >= 15:
                pixelblock(c, r, STEIN, oben=(242, 247, 253), rand=.6)          # Schnee
            elif r == h - 2 and h >= 17:
                pixelblock(c, r, (232, 238, 246))                                # Schneeschicht
            elif r == h - 1 and steil and h >= 12:
                pixelblock(c, r, STEIN)                                          # nackter Fels an steilen Stellen
            elif r == h - 1:
                pixelblock(c, r, ERDE, oben=GRAS)
            elif r >= h - 3 and h < 13:
                pixelblock(c, r, ERDE)
            else:
                fc = STEIN
                if r < h - 4 and rnd.random() < .022:
                    fc = rnd.choice(((58, 58, 62), (200, 164, 124)))             # Kohle, Eisen
                pixelblock(c, r, fc)

    # ---- Wasser (links Meer, rechts der Übergang)
    for c in range(spalten):
        for r in range(hoehen[c], WASSER):
            x0, y0 = c * B, H - (r + 1) * B
            g.rectangle([x0, y0, x0 + B - 1, y0 + B - 1], fill=(30, 60, 130, 175) if nacht else (52, 108, 222, 170))
            if r == WASSER - 1:
                g.rectangle([x0, y0, x0 + B - 1, y0 + 1], fill=(120, 160, 230, 200) if nacht else (170, 210, 250, 230))

    def setze(c, r, fc, alpha=255, rausch=.08):
        if 0 <= c < spalten:
            pixelblock(c, r, fc, alpha=alpha, rausch=rausch)

    # ---- Leuchtturm am Strand
    lc, lb = 52, hoehen[52]
    for k in range(8):
        for dc in (0, 1):
            setze(lc + dc, lb + k, (200, 42, 42) if k % 2 == 0 else (238, 238, 232))
    for dc in (-1, 0, 1, 2):
        setze(lc + dc, lb + 8, (110, 114, 120))
    for dc in (0, 1):
        x0, y0 = (lc + dc) * B, H - (lb + 10) * B
        g.rectangle([x0, y0, x0 + B - 1, y0 + B - 1], fill=(255, 216, 96) if nacht else (238, 232, 196))
        g.rectangle([x0 + 1, y0 + 1, x0 + B - 2, y0 + B - 2], outline=(80, 80, 86) if not nacht else (255, 236, 160))
        setze(lc + dc, lb + 10, (160, 34, 34))
    if nacht:
        ly = H - (lb + 9.5) * B
        # Lichtkegel nach links übers Meer, läuft weich aus (keine Kante an der Bildnaht)
        enden = [lc - 10, lc - 20, lc - 30, lc - 40]
        for k, ende in enumerate(enden):
            t = (lc - ende) / 46
            g.polygon([(lc * B, ly - 3), (ende * B, ly - 3 - t * 4.5 * B), (ende * B, ly + 4 + t * 3 * B), (lc * B, ly + 4)], fill=(255, 222, 130, 16))
        g.polygon([((lc + 2) * B, ly - 3), ((lc + 26) * B, ly - 2.2 * B), ((lc + 26) * B, ly + 1.2 * B), ((lc + 2) * B, ly + 4)], fill=(255, 222, 130, 18))

    # ---- Haus mit Feld auf der Wiese
    hc = 72
    hb = hoehen[hc]
    for c in range(hc - 3, hc + 4):        # Boden einebnen
        hoehen[c] = hb
    for k in range(3):
        for dc in range(-3, 4):
            if abs(dc) == 3:
                setze(hc + dc, hb + k, (104, 78, 46))                           # Eckpfosten
            elif k == 1 and dc in (-2, 2):
                x0, y0 = (hc + dc) * B, H - (hb + k + 1) * B
                g.rectangle([x0, y0, x0 + B - 1, y0 + B - 1], fill=(255, 210, 110) if nacht else (170, 210, 236))
                g.rectangle([x0, y0, x0 + B - 1, y0 + B - 1], outline=nf((104, 78, 46)))
            elif dc == 0 and k < 2:
                setze(hc, hb + k, (90, 64, 38))                                  # Tür
            else:
                setze(hc + dc, hb + k, (184, 148, 96))                           # Bretter
    for k, breite in ((3, 4), (4, 3), (5, 2), (6, 1)):
        for dc in range(-breite, breite + 1):
            setze(hc + dc, hb + k, (150, 62, 50))                                # Dach
    setze(hc + 2, hb + 6, (120, 120, 126)); setze(hc + 2, hb + 7, (120, 120, 126))   # Schornstein
    if not nacht:
        for k, (dx, dy) in enumerate(((2, 0), (3, -1), (2, -2))):
            x0, y0 = (hc + 2) * B + dx * 3, H - (hb + 9) * B + dy * 6
            g.rectangle([x0, y0, x0 + 4, y0 + 4], fill=(235, 238, 242, 170 - k * 40))
    fb = hoehen[83]
    for c in range(79, 90):
        hoehen[c] = fb
        x0, y0 = c * B, H - fb * B
        g.rectangle([x0, y0 - 2, x0 + B - 1, y0 + 1], fill=nf((110, 78, 50)))           # Ackerboden
        if c == 84:
            g.rectangle([x0, y0 - 2, x0 + B - 1, y0 + 1], fill=(70, 120, 210) if not nacht else (40, 70, 130))
            continue
        for i in range(0, B, 2):
            hh = rnd.randrange(4, 8)
            g.rectangle([x0 + i, y0 - 2 - hh, x0 + i, y0 - 3], fill=nf((200, 178, 70) if c % 3 else (150, 170, 60)))

    # ---- Bäume
    def eiche(c, birke=False):
        h0 = hoehen[c]
        stamm = (230, 226, 212) if birke else (104, 78, 46)
        laub = (118, 166, 70) if birke else (66, 124, 42)
        hoch = 4 + rnd.randrange(2)
        for k in range(hoch):
            setze(c, h0 + k, stamm)
            if birke and k % 2:
                x0, y0 = c * B, H - (h0 + k + 1) * B
                g.rectangle([x0 + 2, y0 + 3, x0 + 4, y0 + 4], fill=nf((60, 60, 60)))
        for dr, breite in ((hoch - 2, 2), (hoch - 1, 2), (hoch, 1), (hoch + 1, 1)):
            for dc in range(-breite, breite + 1):
                if dr >= hoch and abs(dc) == breite and rnd.random() < .4:
                    continue
                setze(c + dc, h0 + dr, laub, rausch=.12)

    def fichte(c):
        h0 = hoehen[c]
        for k in range(7):
            setze(c, h0 + k, (78, 58, 36))
        for k, breite in ((2, 2), (3, 1), (4, 2), (5, 1), (6, 1), (7, 0), (8, 0)):
            for dc in range(-breite, breite + 1):
                setze(c + dc, h0 + k, (38, 82, 52), rausch=.12)

    for c in (63, 94, 99):
        eiche(c, birke=(c == 94))
    c = 106
    while c < 150:
        fichte(c) if rnd.random() < .7 else eiche(c, birke=rnd.random() < .3)
        c += rnd.randrange(4, 7)
    for c in (156, 162, 208, 214):
        if hoehen[c] < 15:
            fichte(c)

    # ---- Blumen und Gras auf der Wiese
    for c in list(range(59, 76)) + list(range(91, 150)):
        if 79 <= c < 90:
            continue
        x0, y0 = c * B, H - (hoehen[c] + 1) * B
        z = rnd.random()
        if z < .25 and c < 104:
            farbe = rnd.choice(((228, 58, 58), (250, 208, 58), (242, 242, 242), (118, 148, 238), (228, 118, 200)))
            x = x0 + rnd.randrange(1, 5)
            g.rectangle([x + 1, y0 + 4, x + 1, y0 + 7], fill=nf((60, 120, 40)))
            g.rectangle([x, y0 + 2, x + 2, y0 + 4], fill=nf(farbe))
        elif z < .5:
            for k in range(3):
                x = x0 + rnd.randrange(0, 7)
                g.rectangle([x, y0 + 4 + rnd.randrange(2), x, y0 + 7], fill=nf((88, 150, 50)))
    return img


def schrift(groesse, fett=True):
    from PIL import ImageFont
    for p in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if fett else []) + \
             ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.isfile(p):
            return ImageFont.truetype(p, groesse)
    return None


def og_bild(ziel, titel, unterzeile, modell_bild=None, zusatz='Baupläne und Plugins für Minecraft'):
    """Link-Vorschau 1200 × 630: Verlauf, Marke, Titel links, Bauwerk rechts."""
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (1200, 630))
    g = ImageDraw.Draw(img)
    for yy in range(630):
        t = yy / 629
        g.line([(0, yy), (1200, yy)], fill=tuple(int(a + (b - a) * t) for a, b in zip((246, 248, 250), (222, 230, 238))))
    if modell_bild is not None:
        img.paste(modell_bild, (590, 20), modell_bild)
    g.polygon([(70, 66), (100, 83), (100, 109), (70, 126), (40, 109), (40, 83)], fill=(27, 35, 44))
    g.polygon([(70, 66), (100, 83), (70, 100), (40, 83)], fill=(244, 180, 0))
    g.polygon([(70, 100), (70, 126), (40, 109), (40, 83)], fill=(74, 88, 102))
    f1, f3 = schrift(30), schrift(28, False)
    if not f1:
        img.save(ziel, optimize=True); return
    g.text((118, 70), 'Bauwerkstatt', font=f1, fill=(27, 35, 44))
    g.text((118, 106), zusatz, font=schrift(18, False), fill=(74, 88, 102))
    # Titel umbrechen und so weit verkleinern, dass er links vom Bauwerk bleibt (höchstens 520 px breit)
    for groesse in (64, 58, 52, 46, 42):
        f2 = schrift(groesse)
        zeilen, zeile = [], ''
        for wort in titel.split():
            probe = (zeile + ' ' + wort).strip()
            if g.textlength(probe, font=f2) > 520 and zeile:
                zeilen.append(zeile); zeile = wort
            else:
                zeile = probe
        zeilen.append(zeile)
        if max(g.textlength(z, font=f2) for z in zeilen) <= 520 and len(zeilen) <= 3:
            break
    yy = 250 - 36 * (len(zeilen) - 1)
    for z in zeilen[:3]:
        g.text((40, yy), z, font=f2, fill=(27, 35, 44)); yy += f2.size + 10
    g.rectangle([40, yy + 14, 120, yy + 22], fill=(244, 180, 0))
    yy += 44
    for z in unterzeile.split('\n'):
        g.text((40, yy), z, font=f3, fill=(74, 88, 102)); yy += 40
    img.save(ziel, optimize=True)


# ---------------------------------------------------------------- Texte der Oberfläche

T = {
 'de': dict(
  skip='Zum Inhalt', start='Bauwerkstatt, Startseite', zusatz='Baupläne und Plugins für Minecraft', bauplaene='Baupläne', plugins='Plugins',
  anleitungen='Anleitungen', wuensche='Wünsche', geplant='Geplant', sprache='Sprache', thema='Darstellung',
  auto='Automatisch', hell='Hell', dunkel='Dunkel', fuss='Minecraft-Baupläne und Plugins kostenlos für alle Kreativen.',
  disclaimer='Kein offizielles Minecraft-Produkt. Nicht von Mojang oder Microsoft genehmigt oder mit ihnen verbunden. Blöcke werden mit eigenen Farben dargestellt, nicht mit Minecraft-Texturen.',
  bloecke='Blöcke', schritte='Schritte', entwurf='Entwurf', alle_seiten='Alle Seiten'),
 'en': dict(
  skip='Skip to content', start='Bauwerkstatt, home', zusatz='Build plans and plugins for Minecraft', bauplaene='Builds', plugins='Plugins',
  anleitungen='Guides', wuensche='Wishes', geplant='Planned', sprache='Language', thema='Appearance',
  auto='Automatic', hell='Light', dunkel='Dark', fuss='Minecraft build plans and plugins, free for all creators.',
  disclaimer='Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft. Blocks are shown in our own colours, not with Minecraft textures.',
  bloecke='blocks', schritte='steps', entwurf='Draft', alle_seiten='All pages'),
}


def punkte(n, lang):
    lab = ('Schwierigkeit %d von 5' if lang == 'de' else 'Difficulty %d of 5') % n
    return '<span class="punkte" aria-label="%s">%s</span>' % (lab, ''.join(
        '<i class="%s"></i>' % ('an' if i <= n else '') for i in range(1, 6)))


def edition(e):
    return ''.join('<span class="marker %s">%s</span>' % (x, 'Java' if x == 'java' else 'Bedrock') for x in e or [])


def lok(obj, key, lang):
    """Übersetzten Wert holen, sonst Deutsch."""
    if lang != 'de' and isinstance(obj.get(lang), dict) and obj[lang].get(key) is not None:
        return obj[lang][key]
    return obj.get(key)


class Seiten:
    def __init__(self, out, root, cfg, katalog, builds, docs_html, bloecke_en, ideen=None):
        self.ideen = ideen or {'kategorien': [], 'ideen': []}
        self.out, self.root, self.cfg = out, root, cfg
        self.url = cfg['site_url'].rstrip('/') + '/'
        self.base = urlparse(self.url).path or '/'
        self.k, self.builds, self.docs_html, self.bloecke_en = katalog, builds, docs_html, bloecke_en
        with open(os.path.join(root, 'site', 'index.html'), encoding='utf-8') as f:
            self.vorlage = f.read()
        self.adressen = []      # (pfad_de, pfad_en) für die Sitemap
        self.lang = 'de'

    # ---------- Hilfen
    def t(self, de, en):
        return de if self.lang == 'de' else en

    def link(self, art='start', id=None, lang=None):
        return self.base + pfad(lang or self.lang, art, id)

    def voll(self, p):
        return self.url + p

    def blockname(self, p):
        n = p['name'] if self.lang == 'de' else self.bloecke_en.get(p['name'], p['name'])
        return re.sub(r' \((unten|bottom|lower)\)', '', n)

    def kopfleiste(self, art, id):
        L = T[self.lang]
        nav = ''.join('<a href="%s" data-nav="%s">%s</a>' % (self.link(a), a, L[n]) for a, n in
                      (('liste', 'bauplaene'), ('plugins', 'plugins'), ('anleitungen', 'anleitungen'), ('geplant', 'geplant'), ('wuensche', 'wuensche')))
        anders = 'en' if self.lang == 'de' else 'de'
        sprache = ('<div class="sprache" role="group" aria-label="%s">%s</div>' % (L['sprache'], ''.join(
            '<a href="%s" hreflang="%s" lang="%s" data-lang="%s"%s>%s</a>' % (
                self.base + pfad(l, art, id), l, l, l, ' aria-current="true"' if l == self.lang else '', l.upper())
            for l in SPRACHEN)))
        icons = {
            'auto': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor"/></svg>',
            'hell': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="4.5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></g></svg>',
            'dunkel': '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" fill="currentColor"/></svg>',
        }
        thema = '<div class="thema-wahl" role="radiogroup" aria-label="%s">%s</div>' % (L['thema'], ''.join(
            '<button type="button" role="radio" data-thema="%s" aria-checked="%s" title="%s" aria-label="%s">%s</button>' % (
                k, 'true' if k == 'auto' else 'false', L[k], L[k], icons[k]) for k in ('auto', 'hell', 'dunkel')))
        return nav, sprache, thema

    def fuss_links(self):
        teile = ['<a href="%s">%s</a>' % (self.link('bau', b['id']), H(lok(b, 'titel', self.lang))) for b in self.k['builds']]
        teile += ['<a href="%s">%s</a>' % (self.link('plugin', p['id']), H(p['name'])) for p in self.k['plugins']]
        teile += ['<a href="%s">%s</a>' % (self.link('anleitung', d['id']), H(lok(d, 'titel', self.lang))) for d in self.k['docs']]
        return ' '.join(teile)

    def schreibe(self, art, id, titel, beschreibung, inhalt, jsonld, bild=None, bild_alt='', og_typ='website',
                 og_titel=None, index=True, datei=None):
        L = T[self.lang]
        p_de, p_en = pfad('de', art, id), pfad('en', art, id)
        p = p_de if self.lang == 'de' else p_en
        verif = []
        if self.cfg.get('google_site_verification'):
            verif.append('<meta name="google-site-verification" content="%s">' % H(self.cfg['google_site_verification']))
        if self.cfg.get('bing_site_verification'):
            verif.append('<meta name="msvalidate.01" content="%s">' % H(self.cfg['bing_site_verification']))
        alt = '' if datei else '\n'.join([
            '<link rel="alternate" hreflang="de" href="%s">' % self.voll(p_de),
            '<link rel="alternate" hreflang="en" href="%s">' % self.voll(p_en),
            '<link rel="alternate" hreflang="x-default" href="%s">' % self.voll(p_de)])
        nav, sprache, thema = self.kopfleiste(art, id)
        felder = {
            'LANG': self.lang, 'OG_LOCALE': 'de_DE' if self.lang == 'de' else 'en_US',
            'OG_LOCALE_ALT': 'en_US' if self.lang == 'de' else 'de_DE',
            'TITEL': H(titel), 'BESCHREIBUNG': H(kurz(beschreibung)), 'BASE': self.base, 'URL': self.voll(p),
            'ALTERNATES': alt,
            'ROBOTS': 'index, follow, max-image-preview:large' if index else 'noindex, follow',
            'OG_TYP': og_typ, 'OG_TITEL': H(og_titel or titel),
            'BILD': self.voll(bild or self.og('og-start')), 'BILD_ALT': H(bild_alt or titel),
            'VERIFIKATION': '\n'.join(verif), 'JSONLD': json.dumps(jsonld, ensure_ascii=False).replace('</', '<\\/'),
            'INHALT': inhalt, 'FUSS_LINKS': self.fuss_links(), 'NAV': nav, 'SPRACHE': sprache, 'THEMA': thema,
            'TXT_SKIP': L['skip'], 'TXT_ZUSATZ': L['zusatz'], 'TXT_START': L['start'], 'TXT_FUSS': L['fuss'],
            'TXT_DISCLAIMER': L['disclaimer'], 'V': self.cfg.get('version', '1'), 'TXT_ALLE_SEITEN': L['alle_seiten'], 'START': self.link(),
        }
        text = self.vorlage
        for k, v in felder.items():
            text = text.replace('{{%s}}' % k, v)
        ziel = os.path.join(self.out, datei) if datei else os.path.join(self.out, p, 'index.html')
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        with open(ziel, 'w', encoding='utf-8') as f:
            f.write(text)
        if index and not datei and self.lang == 'de':
            self.adressen.append((p_de, p_en, art, id))

    def og(self, name):
        return 'bilder/%s%s.png' % (name, '' if self.lang == 'de' else '-en')

    def krumen_ld(self, teile):
        return {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': self.voll(pfad(self.lang, a, id))}
            for i, (n, a, id) in enumerate(teile)]}

    def stufe(self, st):
        return {'benoetigt': self.t('Benötigt', 'Required'), 'empfohlen': self.t('Empfohlen', 'Recommended'),
                'optional': self.t('Optional', 'Optional')}[st]

    def plugin_ref(self, pid):
        e = next((p for p in self.k['plugins'] if p['id'] == pid), None)
        if e:
            return e['name'], self.link('plugin', pid), True
        f = next((p for p in self.k.get('fremd', []) if p['id'] == pid), None)
        return (f['name'], f.get('link'), False) if f else (pid, None, False)

    def plugin_a(self, pid):
        name, href, eigen = self.plugin_ref(pid)
        return '<a href="%s"%s>%s</a>' % (H(href), '' if eigen else ' rel="noopener"', H(name)) if href else H(name)

    def plugin_kasten(self, liste):
        t = self.t
        if not liste:
            return '<div class="plugin-bedarf leer-plugin"><h3>Plugins</h3><p>%s</p></div>' % t(
                'Kein Plugin nötig. Läuft in reinem Minecraft (Vanilla), im Einzelspieler und auf jedem Server.',
                'No plugin needed. Works in plain Minecraft (vanilla), in singleplayer and on any server.')
        return '<div class="plugin-bedarf"><h3>%s</h3>%s</div>' % (t('Plugins für diesen Bauplan', 'Plugins for this build'), ''.join(
            '<div class="pb-eintrag"><div class="pb-kopf"><span class="marker stufe-%s">%s</span><b>%s</b></div>%s</div>' % (
                x['stufe'], self.stufe(x['stufe']), self.plugin_a(x['id']),
                '<p>%s</p>' % H(lok(x, 'grund', self.lang)) if x.get('grund') else '') for x in liste))

    def bau_karte(self, b):
        L = T[self.lang]
        titel = lok(b, 'titel', self.lang)
        return ('<a class="karte" href="%s"><div class="bild"><img src="%s" alt="%s" width="800" height="600" loading="lazy"></div>'
                '<div class="text"><div class="chips">%s%s</div><h3>%s</h3><p>%s</p>'
                '<div class="fakten">%s<span><b>%s</b> %s</span><span><b>%d</b> %s</span></div></div></a>') % (
            self.link("bau", b["id"]), self.base + 'bilder/%s.png?v=%s' % (b['id'], self.cfg.get('version', '1')),
            H(self.t('Minecraft-Bauplan %s, fertiges Bauwerk', 'Minecraft build %s, finished') % titel), edition(b['edition']),
            ('<span class="marker stufe-benoetigt">%s</span>' % self.t('Plugin nötig', 'Plugin needed') if any(x['stufe'] == 'benoetigt' for x in b.get('plugins', [])) else '') +
            ('<span class="marker entwurf">%s</span>' % L['entwurf'] if b['status'] == 'entwurf' else '') +
            ('<span class="marker ausbau">%s</span>' % self.t('+ Ausbau', '+ Extended') if b.get('varianten') else ''),
            H(titel), H(lok(b, 'beschreibung', self.lang)), punkte(b['schwierigkeit'], self.lang),
            fmt(b['bloecke'], self.lang), L['bloecke'], b['schritte'], L['schritte'])

    def plugin_karte(self, p):
        return ('<a class="karte plugin-karte" href="%s"><div class="text"><h3>%s <span class="marker">v%s</span></h3>'
                '<p>%s</p></div></a>') % (self.link('plugin', p['id']), H(p['name']), H(p['version']), H(lok(p, 'kurz', self.lang)))

    def doc_link(self, d):
        return ('<a class="liste-link" href="%s"><div><h3>%s</h3><p>%s</p></div><span class="pfeil" aria-hidden="true">→</span></a>'
                % (self.link('anleitung', d['id']), H(lok(d, 'titel', self.lang)), H(lok(d, 'kurz', self.lang))))

    def kopf(self, eyebrow, titel, lede, krumen=None):
        kr = ''
        if krumen:
            kr = '<div class="krumen">%s</div>' % ' / '.join(
                '<a href="%s">%s</a>' % (self.link(a), H(n)) if a else H(n) for n, a in krumen)
        eb = ''   # keine Etiketten über Überschriften
        return '<section class="detail-kopf"><div class="wrap">%s%s<h1>%s</h1><p class="lede">%s</p></div></section>' % (
            kr, eb, H(titel), H(lede))

    # ---------- Ablauf
    def alles(self):
        os.makedirs(os.path.join(self.out, 'bilder'), exist_ok=True)
        self.karten_bilder()
        self.banner()
        for lang in SPRACHEN:
            self.lang = lang
            self.og_bilder()
            self.start(); self.liste_bauplaene()
            for b in self.builds:
                self.bau(b)
            self.liste_plugins()
            for p in self.k['plugins']:
                self.plugin(p)
            self.liste_anleitungen()
            for d in self.k['docs']:
                self.anleitung(d)
            self.wuensche()
            self.geplant()
        self.lang = 'de'
        self.fehlerseite()
        self.sitemap()

    def karten_bilder(self):
        self.modellbilder = {}
        for b in self.builds:
            schnitt = bool(b.get('ansicht', {}).get('schnitt'))
            img = zeichne_modell(b['model'], 800, 600, schnitt=schnitt)
            img.save(os.path.join(self.out, 'bilder', '%s.png' % b['id']), optimize=True)
            self.modellbilder[b['id']] = zeichne_modell(b['model'], 590, 590, schnitt=schnitt, fuellung=.9, schatten=True)
        for (bid, var), m in getattr(self, 'varianten_modelle', {}).items():
            zeichne_modell(m, 800, 600).save(os.path.join(self.out, 'bilder', '%s--%s.png' % (bid, var)), optimize=True)

    def banner(self):
        """Minecraft-Landschaft für den Kopfbereich, als Tag- und Nachtbild."""
        for nacht, name in ((False, 'banner-tag.png'), (True, 'banner-nacht.png')):
            landschaft(nacht).save(os.path.join(self.out, 'bilder', name), optimize=True)

    def og_bilder(self):
        z = T[self.lang]['zusatz']
        for b in self.builds:
            kb = next(x for x in self.k['builds'] if x['id'] == b['id'])
            og_bild(os.path.join(self.out, self.og(b['id'] + '-og')), lok(b, 'titel', self.lang),
                    self.t('Minecraft-Bauplan · %d Schritte\n%s Blöcke · Litematica & WorldEdit',
                           'Minecraft build · %d steps\n%s blocks · Litematica & WorldEdit') % (kb['schritte'], fmt(kb['bloecke'], self.lang)),
                    self.modellbilder[b['id']], zusatz=z)
        og_bild(os.path.join(self.out, self.og('og-start')), self.t('Block für Block', 'Block by block'),
                self.t('Minecraft-Baupläne Schritt für Schritt\nund Plugins für Paper-Server',
                       'Minecraft build plans step by step\nand plugins for Paper servers'), self.modellbilder.get('villa-am-wasser'), zusatz=z)
        og_bild(os.path.join(self.out, self.og('og-plugins')), self.t('Paper-Plugins', 'Paper plugins'),
                self.t('Shop, Lager, Arbeiter und mehr\nfür deinen Minecraft-Server', 'Shop, storage, workers and more\nfor your Minecraft server'), zusatz=z)

    # ---------- Seiten
    def start(self):
        k = self.k
        summe = sum(b['bloecke'] for b in k['builds'])
        t = self.t
        bestand = t('Schon da: <b>%d Baupläne</b> mit %s Blöcken, <b>%d Plugins</b> und <b>%d Anleitungen</b>. In Planung: %d weitere Ideen.',
                    'Available now: <b>%d builds</b> with %s blocks, <b>%d plugins</b> and <b>%d guides</b>. Planned: %d more ideas.') % (
            len(k['builds']), fmt(summe, self.lang), len(k['plugins']), len(k['docs']), len(self.ideen['ideen']))
        inhalt = (
            '<section class="held"><div class="wrap"><div>'
            '<h1>%s</h1><p class="lede">%s</p>'
            '<div class="knoepfe"><a class="btn" href="%s">%s</a><a class="btn zwei" href="%s">%s</a></div>'
            '<p class="bestand">%s</p></div>'
            '<figure class="heft bauplan" style="margin:0"><img src="%s" alt="%s" width="800" height="600">'
            '<figcaption class="heft-fuss"><span>%s</span><a href="%s">%s</a></figcaption></figure></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>%s</h2><div class="raster" style="margin-top:18px">%s</div></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>%s</h2><div class="raster" style="margin-top:18px">%s</div></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>%s</h2><div style="margin-top:18px">%s</div></div></section>'
        ) % (t('Block für Block. Schritt für Schritt.', 'Block by block. Step by step.'),
             t('Minecraft-Baupläne, die pro Schritt genau zeigen, welche Blöcke du brauchst und wo sie hinkommen. Dazu Plugins für deinen eigenen Paper-Server. Alles kostenlos und einzeln zum Herunterladen.',
               'Minecraft build plans that show for every step exactly which blocks you need and where they go. Plus plugins for your own Paper server. All free and downloadable one by one.'),
             self.link('liste'), t('Baupläne ansehen', 'Browse builds'), self.link('geplant'), t('Was als Nächstes kommt', 'What comes next'),
             bestand,
             self.base + 'bilder/villa-am-wasser.png', t('Minecraft-Bauplan Villa am Wasser', 'Minecraft build Villa by the Water'),
             t('Villa am Wasser', 'Villa by the Water'), self.link('bau', 'villa-am-wasser'), t('Diesen Bauplan öffnen', 'Open this build'),
             t('Minecraft-Baupläne', 'Minecraft build plans'), ''.join(self.bau_karte(b) for b in k['builds']),
             t('Eigene Plugins für Paper', 'Our plugins for Paper'), ''.join(self.plugin_karte(p) for p in k['plugins']),
             t('Anleitungen', 'Guides'), ''.join(self.doc_link(d) for d in k['docs']))
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'WebSite', 'name': 'Bauwerkstatt', 'alternateName': t('Bauwerkstatt – Baupläne und Plugins für Minecraft', 'Bauwerkstatt – build plans and plugins for Minecraft'), 'url': self.voll(pfad(self.lang)), 'inLanguage': self.lang,
             'description': t('Minecraft-Baupläne Schritt für Schritt und Plugins für Paper-Server, kostenlos.',
                              'Step-by-step Minecraft build plans and plugins for Paper servers, free.'),
             'publisher': {'@type': 'Person', 'name': 'Savox'}},
            {'@type': 'ItemList', 'name': t('Minecraft-Baupläne', 'Minecraft build plans'), 'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1, 'url': self.voll(pfad(self.lang, 'bau', b['id'])), 'name': lok(b, 'titel', self.lang)}
                for i, b in enumerate(k['builds'])]}]}
        self.schreibe('start', None,
                      t('Bauwerkstatt – Minecraft-Baupläne Schritt für Schritt & Paper-Plugins',
                        'Bauwerkstatt – step-by-step Minecraft build plans & Paper plugins'),
                      t('Kostenlose Minecraft-Baupläne Schritt für Schritt, mit den Blöcken für jeden Schritt: Villen, Leuchtturm, Eiffelturm und Farmen mit Teileliste und Download für Litematica und WorldEdit. Dazu Plugins für Paper-Server.',
                        'Free step-by-step Minecraft build plans showing the blocks for every step: villas, lighthouse, Eiffel Tower and farms with parts list and downloads for Litematica and WorldEdit. Plus plugins for Paper servers.'),
                      inhalt, ld, og_titel=t('Bauwerkstatt: Minecraft-Baupläne Schritt für Schritt', 'Bauwerkstatt: step-by-step Minecraft builds'))

    def liste_bauplaene(self):
        k, t = self.k, self.t
        kats = k['kategorien'] if self.lang == 'de' else k['kategorien_en']
        teile = []
        for kat, name in kats.items():
            bs = [b for b in k['builds'] if b['kategorie'] == kat]
            if bs:
                teile.append('<h2 style="margin:26px 0 14px">%s</h2><div class="raster">%s</div>' % (H(name), ''.join(self.bau_karte(b) for b in bs)))
        inhalt = self.kopf(t('Sammlung', 'Collection'), t('Minecraft-Baupläne', 'Minecraft build plans'),
                           t('Jeden Bauplan gibt es als Schritt-für-Schritt-Anleitung im Browser, als Litematica- und WorldEdit-Datei und als Teileliste.',
                             'Every build comes as step-by-step instructions in the browser, as a Litematica and WorldEdit file and as a parts list.')) + \
            '<section class="abschnitt" style="padding-top:8px"><div class="wrap">%s</div></section>' % ''.join(teile)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Minecraft-Baupläne', 'Minecraft build plans'), 'url': self.voll(pfad(self.lang, 'liste')), 'inLanguage': self.lang},
            self.krumen_ld([('Start', 'start', None), (t('Baupläne', 'Builds'), 'liste', None)])]}
        self.schreibe('liste', None,
                      t('Minecraft-Baupläne: Villen, Türme und Farmen Schritt für Schritt | Bauwerkstatt',
                        'Minecraft build plans: villas, towers and farms step by step | Bauwerkstatt'),
                      t('Alle Minecraft-Baupläne: Villa am Wasser, moderne, mediterrane und Gründerzeit-Villa, Leuchtturm, Eiffelturm, Gewächshaus-Farm und Kellerlager mit Sortieranlage. Mit Bauschritten und Downloads.',
                        'All Minecraft build plans: villa by the water, modern, Mediterranean and Victorian-era villa, lighthouse, Eiffel Tower, greenhouse farm and cellar storage with item sorter. With build steps and downloads.'),
                      inhalt, ld)

    def bau(self, b):
        k, t, lang = self.k, self.t, self.lang
        kb = next(x for x in k['builds'] if x['id'] == b['id'])
        pal = b['model']['palette']
        kats = k['kategorien'] if lang == 'de' else k['kategorien_en']
        titel = lok(b, 'titel', lang)
        std = b.get('bauzeit_stunden') or [0, 0]
        specs = [(t('Schwierigkeit', 'Difficulty'), punkte(b['schwierigkeit'], lang)), (t('Blöcke', 'Blocks'), fmt(kb['bloecke'], lang)),
                 (t('Schritte', 'Steps'), str(kb['schritte'])), (t('Grundfläche', 'Footprint'), H(lok(b, 'grundflaeche', lang) or '')),
                 (t('Höhe', 'Height'), t('%d Ebenen', '%d layers') % b['model']['size']['y']),
                 (t('Bauzeit', 'Build time'), t('%d–%d Std.', '%d–%d h') % tuple(std)),
                 ('Edition', ' · '.join('Java' if e == 'java' else 'Bedrock' for e in b.get('edition', []))),
                 ('Plugins', ', '.join('%s <small>(%s)</small>' % (H(self.plugin_ref(x['id'])[0]), self.stufe(x['stufe']).lower()) for x in b.get('plugins', []))
                  or t('keine nötig', 'none needed'))]
        teile_rows = ''.join('<tr><td>%s<br><small>%s</small></td><td class="zahl">%s</td><td class="zahl">%s</td></tr>' % (
            H(self.blockname(pal[x['i']])), H((pal[x['i']].get('block') or '').split('[')[0]), fmt(x['n'], lang), stacks(x['n'], lang))
            for x in b['teileliste'])
        roh_de, roh = b.get('rohstoffe', []), lok(b, 'rohstoffe', lang) or []
        roh_rows = ''.join('<tr><td><b>%s</b><br><small>%s · %s</small></td><td class="zahl">%s</td></tr>' % (
            H(r['name']), H(r['quelle']), H(r['hinweis']), fmt(roh_de[i]['menge'], lang)) for i, r in enumerate(roh))
        ebene = lambda a: (t('Ebene %d', 'layer %d') % a['von']) if a['von'] == a['bis'] else (t('Ebenen %d bis %d', 'layers %d to %d') % (a['von'], a['bis']))
        abschnitte_de = b.get('abschnitte', [])
        abschnitte = lok(b, 'abschnitte', lang) or []
        ab_html = ''.join('<li><b>%s</b> (%s): %s</li>' % (H(a['name']), ebene(abschnitte_de[i]), H(a['text'])) for i, a in enumerate(abschnitte))
        tipps = ''.join('<div class="tipp"><b>%s</b>%s</div>' % (H(x['titel']), H(x['text'])) for x in (lok(b, 'tipps', lang) or []))
        dl = ''.join('<li><a href="%s">%s</a></li>' % (self.base + 'downloads/%s/%s' % (b['id'], d['datei']), H(d['datei'])) for d in b.get('downloads', []))
        inhalt = (
            '<section class="detail-kopf"><div class="wrap"><div class="krumen"><a href="%s">%s</a> / %s</div>'
            '<h1>%s</h1><p class="lede">%s</p><dl class="specs">%s</dl>%s</div></section>'
            '<section class="tafel"><div class="wrap">'
            '<img class="vor-bild" src="%s" alt="%s" width="800" height="600">%s'
            '<h2 style="margin:26px 0 10px">%s</h2><ol class="vor-liste">%s</ol><p style="margin-top:10px">%s</p>'
            '<div class="zwei-spalten" style="margin-top:26px"><div><h2 style="margin-bottom:12px">%s</h2><div class="tabelle-huelle"><table>'
            '<thead><tr><th>%s</th><th class="zahl">%s</th><th class="zahl">Stacks</th></tr></thead><tbody>%s</tbody></table></div></div>'
            '<div><h2 style="margin-bottom:12px">%s</h2><div class="tabelle-huelle"><table>'
            '<thead><tr><th>%s</th><th class="zahl">%s</th></tr></thead><tbody>%s</tbody></table></div>'
            '<h2 style="margin:26px 0 10px">Downloads</h2><ul class="vor-liste">%s</ul></div></div>%s</div></section>'
        ) % (self.link('liste'), t('Baupläne', 'Builds'), H(kats.get(b['kategorie'], '')), H(titel), H(lok(b, 'beschreibung', lang)),
             ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % s for s in specs),
             ('<div class="hinweis"><span><b>%s:</b> %s</span></div>' % (T[lang]['entwurf'], H(lok(b, 'hinweis', lang) or '')) if b.get('status') == 'entwurf' else '') + self.plugin_kasten(b.get('plugins', [])),
             self.base + 'bilder/%s.png' % b['id'], H(t('Minecraft %s, fertig gebaut', 'Minecraft %s, finished build') % titel),
             self.ausbau_kasten(b),
             t('Bauabschnitte', 'Build sections'), ab_html,
             t('Die Anleitung führt dich in %d Bauschritten Ebene für Ebene von unten nach oben durch den Bau, mit höchstens 60 neuen Blöcken pro Schritt. Jeder Schritt zeigt eine drehbare 3D-Ansicht und die Draufsicht der Ebene.',
               'The instructions guide you through the build in %d build steps, layer by layer from the bottom up, with at most 60 new blocks per step. Every step shows a rotatable 3D view and a top view of the layer.') % kb['schritte'],
             t('Teileliste', 'Parts list'), 'Block', t('Anzahl', 'Count'), teile_rows,
             t('Rohstoffe aus Farmen', 'Raw materials from farms'), t('Rohstoff', 'Material'), t('Menge', 'Amount'), roh_rows, dl,
             '<h2 style="margin:30px 0 12px">%s</h2><div class="raster">%s</div>' % (t('Tipps', 'Tips'), tipps) if tipps else '')
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'HowTo', 'name': t('%s in Minecraft bauen', 'Build the %s in Minecraft') % titel,
             'description': lok(b, 'beschreibung', lang), 'image': self.voll(self.og(b['id'] + '-og')), 'inLanguage': lang,
             'totalTime': 'PT%dH' % max(1, std[0]),
             'supply': [{'@type': 'HowToSupply', 'name': self.blockname(pal[x['i']]), 'requiredQuantity': x['n']} for x in b['teileliste'][:12]],
             'step': [{'@type': 'HowToSection', 'name': a['name'], 'position': i + 1,
                       'itemListElement': [{'@type': 'HowToStep', 'text': a['text']}]} for i, a in enumerate(abschnitte)],
             'author': {'@type': 'Person', 'name': b.get('autor', 'Savox')}},
            self.krumen_ld([('Start', 'start', None), (t('Baupläne', 'Builds'), 'liste', None), (titel, 'bau', b['id'])])]}
        self.schreibe('bau', b['id'],
                      t('%s in Minecraft bauen – Bauplan in %d Schritten | Bauwerkstatt',
                        'Build the %s in Minecraft – %d-step build plan | Bauwerkstatt') % (titel, kb['schritte']),
                      t('%s: Minecraft-Bauplan mit %d Bauschritten, Teileliste (%s Blöcke) und Download für Litematica und WorldEdit. %s',
                        '%s: Minecraft build plan with %d build steps, parts list (%s blocks) and downloads for Litematica and WorldEdit. %s') % (
                          titel, kb['schritte'], fmt(kb['bloecke'], lang), lok(b, 'beschreibung', lang)),
                      inhalt, ld, bild=self.og(b['id'] + '-og'), bild_alt=t('Minecraft-Bauplan %s', 'Minecraft build %s') % titel,
                      og_typ='article', og_titel=t('%s – Minecraft-Bauplan', '%s – Minecraft build plan') % titel)

    def ausbau_kasten(self, b):
        """Hinweis auf die Ausbau-Version (wird im Browser durch den Fassungs-Schalter ersetzt)."""
        v = next((x for x in b.get('varianten', []) if x['id'] != 'umbau'), None)
        if not v:
            return ''
        t = self.t
        ziel = self.link('bau', b['id']) + '?fassung=' + v['id']
        return ('<div class="ausbau-hinweis"><img src="%s" alt="%s" width="800" height="600" loading="lazy"><div>'
                '<span class="eyebrow">%s</span><h2>%s</h2><p>%s</p><a class="btn" href="%s">%s</a></div></div>') % (
            self.base + 'bilder/%s--%s.png' % (b['id'], v['id']),
            H(t('Minecraft %s, Ausbau-Version', 'Minecraft %s, extended version') % lok(b, 'titel', self.lang)),
            t('Auch als Ausbau-Version', 'Also as an extended version'), H(lok(v, 'titel', self.lang)),
            t('Dasselbe Bauwerk, verfeinert: mehr Tiefe, Details, Einrichtung und Umgebung. %s Blöcke in %d Schritten. '
              'Wer die Grundversion schon gebaut hat, kann sie Schritt für Schritt umbauen.',
              'The same build, refined: more depth, details, furnishing and surroundings. %s blocks in %d steps. '
              'If you already built the base version, you can rebuild it step by step.') % (fmt(v['bloecke'], self.lang), v['schritte']),
            ziel, t('Ausbau-Version ansehen', 'View the extended version'))

    def konzept(self, i):
        l = (i.get('konzept') or {}).get(self.lang) or (i.get('konzept') or {}).get('de')
        if not l:
            return ''
        return '<details class="konzept"><summary>%s</summary><ul>%s</ul></details>' % (
            self.t('Geplante Funktionen', 'Planned features'), ''.join('<li>%s</li>' % H(x) for x in l))

    def geplantes_plugin(self, i):
        t = self.t
        from urllib.parse import quote
        repo = 'https://github.com/Savox76/minecraft-tools'
        ziel = ('%s/issues/%s' % (repo, i['wunsch'])) if i.get('wunsch') else \
            '%s/issues/new?template=plugin-wunsch.yml&title=%s' % (repo, quote('Plugin-Wunsch: Idee #%s %s' % (i['nr'], i['titel'])))
        name = i.get('name') or lok(i, 'titel', self.lang)
        return ('<div class="karte plugin-karte geplant-plugin"><div class="text"><div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">%s</span>'
                '<div><h3>%s</h3><span class="marker status-%s">%s</span></div></div><p>%s</p>%s'
                '<div class="fakten"><a class="btn zwei klein" href="%s" rel="noopener">👍 %s</a> <a class="marker" href="%s#idee-%s">Nr. %s</a></div></div></div>') % (
            H(''.join(re.findall('[A-ZÄÖÜ]', name)[:2]) or name[0]), H(name), i['status'],
            t('In Arbeit', 'In progress') if i['status'] == 'in-arbeit' else t('In Planung', 'Planned'),
            H(lok(i, 'text', self.lang)), self.konzept(i), H(ziel), t('Mitstimmen', 'Vote too') if i.get('wunsch') else t('Wünschen', 'Vote'),
            self.link('geplant'), i['nr'], i['nr'])

    def liste_plugins(self):
        k, t = self.k, self.t
        geplant = [i for i in self.ideen['ideen'] if i['kategorie'] == 'plugins' and i['status'] != 'verfuegbar']
        fremd = ''.join('<li><b>%s</b>%s: %s%s</li>' % (
            H(p['name']), (t(' (von %s)', ' (by %s)') % H(p['autor'])) if p.get('autor') else '', H(lok(p, 'zweck', self.lang)),
            ' <a href="%s" rel="noopener">%s</a>' % (H(p['link']), t('Download-Seite', 'Download page')) if p.get('link') else '')
            for p in k.get('fremd', []))
        inhalt = self.kopf(t('Für Paper-Server', 'For Paper servers'), t('Plugins für Minecraft-Server', 'Plugins for Minecraft servers'),
                           t('Eigene Plugins für einen fairen Server mit Coins, Lager und Arbeitern, dazu bewährte Plugins anderer Entwickler.',
                             'Our own plugins for a fair server with coins, storage and workers, plus proven plugins by other developers.')) + \
            ('<section class="abschnitt" style="padding-top:8px"><div class="wrap"><h2>%s</h2>'
             '<div class="raster" style="margin-top:14px">%s</div>%s<h2 style="margin-top:30px">%s</h2>'
             '<ul class="vor-liste">%s</ul></div></section>') % (
                t('Eigene Plugins', 'Our plugins'), ''.join(self.plugin_karte(p) for p in k['plugins']),
                ('<h2 style="margin-top:30px">%s</h2><div class="raster" style="margin-top:14px">%s</div>' % (
                    t('In Planung', 'Planned'), ''.join(self.geplantes_plugin(i) for i in geplant))) if geplant else '',
                t('Plugins anderer Entwickler', 'Plugins by other developers'), fremd)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Plugins für Minecraft-Server', 'Plugins for Minecraft servers'), 'url': self.voll(pfad(self.lang, 'plugins')), 'inLanguage': self.lang},
            self.krumen_ld([('Start', 'start', None), ('Plugins', 'plugins', None)])]}
        self.schreibe('plugins', None, t('Paper-Plugins für deinen Minecraft-Server | Bauwerkstatt', 'Paper plugins for your Minecraft server | Bauwerkstatt'),
                      t('Plugins für Paper-Server: Coin-Shop, unbegrenztes Lager, Dorfbewohner-Arbeiter, Admin-Login, Creeper-Schutz, Server-Einstellungen per Chat und ein Hilfe-Buch. Dazu empfohlene Plugins anderer Entwickler.',
                        'Plugins for Paper servers: coin shop, unlimited storage, villager workers, admin login, creeper protection, server settings by chat and a help book. Plus recommended plugins by other developers.'),
                      inhalt, ld, bild=self.og('og-plugins'))

    def plugin(self, p):
        t, lang = self.t, self.lang
        wer = {'spieler': t('Spieler', 'Player'), 'admin': 'Admin', 'konsole': t('Konsole', 'Console')}
        en = p.get('en', {}) if lang == 'en' else {}
        btexte = en.get('befehle') or [b['text'] for b in p['befehle']]
        ctexte = en.get('config') or [c['text'] for c in p['config']]
        aend = en.get('changelog') or [c['punkte'] for c in p['changelog']]
        befehle = ''.join('<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>' % (H(b['befehl']), H(btexte[i]), wer.get(b['wer'], b['wer'])) for i, b in enumerate(p['befehle']))
        config = ''.join('<tr><td><code>%s</code></td><td><code>%s</code></td><td>%s</td></tr>' % (H(c['schluessel']), H(c['standard']), H(ctexte[i])) for i, c in enumerate(p['config']))
        aend_html = ''.join('<h3 style="margin-top:14px">%s (%s)</h3><ul class="vor-liste">%s</ul>' % (H(c['version']), H(c['datum']), ''.join('<li>%s</li>' % H(x) for x in aend[i])) for i, c in enumerate(p['changelog']))
        inhalt = self.kopf(None, p['name'], lok(p, 'beschreibung', lang), [('Plugins', 'plugins')]) + (
            '<section class="tafel"><div class="wrap"><div class="zwei-spalten"><div class="feld"><h2>%s</h2><ul class="funktionen">%s</ul></div>'
            '<div class="feld"><h2>%s</h2>%s</div></div>'
            '<h2 style="margin:28px 0 12px">%s</h2><div class="tabelle-huelle"><table><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>'
            '%s%s</div></section>') % (
            t('Funktionen', 'Features'), ''.join('<li>%s</li>' % H(f) for f in lok(p, 'funktionen', lang)),
            t('Änderungen', 'Changelog'), aend_html, t('Befehle', 'Commands'), t('Befehl', 'Command'), t('Was er macht', 'What it does'), t('Wer', 'Who'), befehle,
            ('<h2 style="margin:28px 0 12px">%s</h2><div class="tabelle-huelle"><table><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>' % (
                t('Einstellungen in der config.yml', 'Settings in config.yml'), t('Schlüssel', 'Key'), t('Standard', 'Default'), t('Bedeutung', 'Meaning'), config)) if config else '', self.verwendet_in(p['id']))
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'SoftwareApplication', 'name': p['name'], 'softwareVersion': p['version'], 'description': lok(p, 'beschreibung', lang),
             'applicationCategory': 'GameApplication', 'operatingSystem': 'Paper (Minecraft Java Server)', 'inLanguage': lang,
             'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'author': {'@type': 'Person', 'name': p.get('autor', 'Savox')}},
            self.krumen_ld([('Start', 'start', None), ('Plugins', 'plugins', None), (p['name'], 'plugin', p['id'])])]}
        self.schreibe('plugin', p['id'], t('%s – Minecraft-Plugin für Paper | Bauwerkstatt', '%s – Minecraft plugin for Paper | Bauwerkstatt') % p['name'],
                      t('%s %s für Paper-Server: %s Mit allen Befehlen und Einstellungen.', '%s %s for Paper servers: %s With all commands and settings.') % (
                          p['name'], p['version'], lok(p, 'kurz', lang)),
                      inhalt, ld, bild=self.og('og-plugins'), og_titel=t('%s – Paper-Plugin', '%s – Paper plugin') % p['name'])

    def verwendet_in(self, pid):
        t = self.t
        bs = [b for b in self.k['builds'] if any(x['id'] == pid for x in b.get('plugins', []))]
        ids = [i for i in self.ideen['ideen'] if any(x['id'] == pid for x in i.get('plugins', []))]
        if not bs and not ids:
            return ''
        st = lambda l: self.stufe(next(x for x in l if x['id'] == pid)['stufe']).lower()
        zeilen = ['<li><a href="%s">%s</a> <span class="eyebrow">%s · %s</span></li>' % (
            self.link('bau', b['id']), H(lok(b, 'titel', self.lang)), t('Bauplan', 'build'), st(b['plugins'])) for b in bs]
        zeilen += ['<li><a href="%s#idee-%s">%s</a> <span class="eyebrow">%s · Nr. %s · %s</span></li>' % (
            self.link('geplant'), i['nr'], H(lok(i, 'titel', self.lang)), t('geplant', 'planned'), i['nr'], st(i['plugins'])) for i in ids]
        return '<h2 style="margin:28px 0 12px">%s</h2><ul class="verwendet">%s</ul>' % (t('Wird verwendet in', 'Used in'), ''.join(zeilen))

    def liste_anleitungen(self):
        t = self.t
        inhalt = self.kopf(t('Wissen', 'Knowledge'), t('Anleitungen', 'Guides'),
                           t('Hilfen rund um deinen Minecraft-Server: Farmen ohne Spieler laufen lassen, Aktionen nachvollziehen und mehr.',
                             'Help for your Minecraft server: keep farms running without players, trace player actions and more.')) + \
            '<section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px">%s</div></section>' % ''.join(self.doc_link(d) for d in self.k['docs'])
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Anleitungen', 'Guides'), 'url': self.voll(pfad(self.lang, 'anleitungen')), 'inLanguage': self.lang},
            self.krumen_ld([('Start', 'start', None), (t('Anleitungen', 'Guides'), 'anleitungen', None)])]}
        self.schreibe('anleitungen', None, t('Anleitungen für Minecraft-Server | Bauwerkstatt', 'Guides for Minecraft servers | Bauwerkstatt'),
                      t('Anleitungen für Paper-Server: Farm-Bot, damit Farmen ohne Spieler weiterlaufen, und Spieler-Aktionen mit CoreProtect protokollieren.',
                        'Guides for Paper servers: a farm bot to keep farms running without players, and logging player actions with CoreProtect.'), inhalt, ld)

    def anleitung(self, d):
        t, lang = self.t, self.lang
        html_text = self.docs_html[(d['id'], lang)] if (d['id'], lang) in self.docs_html else self.docs_html[(d['id'], 'de')]
        titel, kurztext = lok(d, 'titel', lang), lok(d, 'kurz', lang)
        inhalt = self.kopf(None, titel, kurztext, [(t('Anleitungen', 'Guides'), 'anleitungen')]) + \
            '<section class="tafel"><div class="wrap"><article class="prosa">%s</article></div></section>' % html_text
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'TechArticle', 'headline': titel, 'description': kurztext, 'inLanguage': lang,
             'url': self.voll(pfad(lang, 'anleitung', d['id'])), 'author': {'@type': 'Person', 'name': 'Savox'}},
            self.krumen_ld([('Start', 'start', None), (t('Anleitungen', 'Guides'), 'anleitungen', None), (titel, 'anleitung', d['id'])])]}
        self.schreibe('anleitung', d['id'], t('%s – Minecraft-Server-Anleitung | Bauwerkstatt', '%s – Minecraft server guide | Bauwerkstatt') % titel,
                      '%s %s' % (kurztext, re.sub(r'<[^>]+>', ' ', html_text)), inhalt, ld, og_typ='article')

    def wuensche(self):
        t = self.t
        repo = 'https://github.com/Savox76/minecraft-tools'
        inhalt = self.kopf(t('Mitmachen', 'Get involved'), t('Bauplan wünschen', 'Request a build'),
                           t('Welches Bauwerk oder Plugin fehlt dir? Reich deinen Wunsch ein und stimm mit 👍 für die Wünsche anderer ab.',
                             'Which build or plugin are you missing? Submit your wish and vote for others’ wishes with 👍.')) + \
            ('<section class="abschnitt" style="padding-top:8px"><div class="wrap"><a class="btn" href="%s/issues/new?template=bauwunsch.yml">%s</a> '
             '<a class="btn zwei" href="%s/issues/new?template=plugin-wunsch.yml">%s</a></div></section>') % (
                repo, t('Bauplan wünschen', 'Request a build'), repo, t('Plugin wünschen', 'Request a plugin'))
        ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': t('Bauplan wünschen', 'Request a build'), 'url': self.voll(pfad(self.lang, 'wuensche')), 'inLanguage': self.lang}
        self.schreibe('wuensche', None, t('Minecraft-Bauplan wünschen | Bauwerkstatt', 'Request a Minecraft build | Bauwerkstatt'),
                      t('Wünsch dir einen Minecraft-Bauplan oder ein Plugin. Die meistgewünschten Bauwerke werden zuerst als Schritt-für-Schritt-Anleitung gebaut.',
                        'Request a Minecraft build plan or a plugin. The most requested builds are made into step-by-step instructions first.'), inhalt, ld)

    def geplant(self):
        t, lang = self.t, self.lang
        IDS = self.ideen['ideen']
        GR = {'klein': t('klein', 'small'), 'mittel': t('mittel', 'medium'), 'groß': t('groß', 'large')}
        ST = {'idee': t('Idee', 'Idea'), 'in-arbeit': t('In Arbeit', 'In progress'), 'verfuegbar': t('Verfügbar', 'Available')}
        repo = 'https://github.com/Savox76/minecraft-tools'
        from urllib.parse import quote

        def karte(i, mit_id=True):
            titel = lok(i, 'titel', lang)
            gr = GR.get(i.get('groesse'), t('Plugin', 'Plugin') if i['kategorie'] == 'plugins' else t('Anleitung', 'Guide'))
            if i['status'] == 'verfuegbar' and i.get('bauplan'):
                aktion = '<a class="btn klein" href="%s">%s</a>' % (self.link('bau', i['bauplan']), t('Zum Bauplan', 'View build'))
            elif i.get('wunsch'):       # Idee stammt aus einem Wunsch: dort mitstimmen
                aktion = '<a class="btn zwei klein" href="%s/issues/%s" rel="noopener">👍 %s</a>' % (repo, i['wunsch'], t('Mitstimmen', 'Vote too'))
            elif i['kategorie'] == 'plugins':
                ziel = '%s/issues/new?template=plugin-wunsch.yml&title=%s' % (repo, quote('Plugin-Wunsch: Idee #%s %s' % (i['nr'], i['titel'])))
                aktion = '<a class="btn zwei klein" href="%s" rel="noopener">👍 %s</a>' % (H(ziel), t('Wünschen', 'Vote'))
            else:
                ziel = '%s/issues/new?template=bauwunsch.yml&title=%s&bauwerk=%s' % (
                    repo, quote('Bauwunsch: Idee #%s %s' % (i['nr'], i['titel'])), quote(i['titel']))
                aktion = '<a class="btn zwei klein" href="%s" rel="noopener">👍 %s</a>' % (H(ziel), t('Wünschen', 'Vote'))
            plg = ''
            if i.get('plugins'):
                plg = '<p class="idee-plugins">Plugin: %s</p>' % ', '.join(
                    '%s <span>(%s)</span>' % (self.plugin_a(x['id']), self.stufe(x['stufe']).lower()) for x in i['plugins'])
            return ('<article class="idee" data-kat="%s"%s><div class="idee-kopf"><span class="idee-nr">Nr. %s</span>'
                    '<span class="marker">%s</span><span class="marker status-%s">%s</span></div><h3>%s</h3><p>%s</p>%s%s'
                    '<div class="idee-fuss">%s</div></article>') % (
                i['kategorie'], (' id="idee-%s"' % i['nr']) if mit_id else '', i['nr'], H(gr), i['status'], ST[i['status']], H(titel), H(lok(i, 'text', lang)), self.konzept(i), plg, aktion)

        teile = []
        empf = [i for i in IDS if i.get('empfohlen')]
        if empf:
            teile.append('<section class="ideen-gruppe empfohlen"><h2>%s</h2><p>%s</p><div class="ideen-raster">%s</div></section>' % (
                t('Als Nächstes', 'Up next'), H(self.ideen.get('empfohlen_text', {}).get(lang, '')),
                ''.join(karte(i, False) for i in empf)))
        for k in self.ideen['kategorien']:
            liste = [i for i in IDS if i['kategorie'] == k['id']]
            if liste:
                teile.append('<section class="ideen-gruppe" id="kat-%s"><h2>%s <span class="anzahl">%d</span></h2><p>%s</p><div class="ideen-raster">%s</div></section>' % (
                    k['id'], H(lok(k, 'name', lang)), len(liste), H(lok(k, 'text', lang)), ''.join(karte(i) for i in liste)))
        zahl = {st: sum(1 for i in IDS if i['status'] == st) for st in ST}
        inhalt = self.kopf(t('Was kommt', 'What is coming'), t('Geplant', 'Planned'),
                           t('Alle Ideen für neue Baupläne und Anleitungen: Farmen, Fabriken, Gebäude und Monumente. Stimm mit „Wünschen“ ab, was zuerst gebaut wird.',
                             'All ideas for new builds and guides: farms, factories, buildings and monuments. Vote with “Vote” for what gets built first.')) + \
            ('<section class="abschnitt" style="padding-top:8px"><div class="wrap"><div class="ideen-zahlen">%s</div>%s</div></section>') % (
                ''.join('<div><b>%d</b><span>%s</span></div>' % (n, l) for n, l in (
                    (sum(1 for i in IDS if i['kategorie'] not in ('anleitungen', 'plugins')), t('Bauplan-Ideen', 'build ideas')),
                    (sum(1 for i in IDS if i['kategorie'] == 'anleitungen'), t('Anleitungen', 'guides')),
                    (sum(1 for i in IDS if i['kategorie'] == 'plugins'), t('Plugin-Ideen', 'plugin ideas')),
                    (zahl['in-arbeit'], ST['in-arbeit']), (self.ideen.get('umgesetzt', 0), t('schon als Bauplan fertig', 'already finished as builds')))),
                ''.join(teile))
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Geplante Minecraft-Baupläne', 'Planned Minecraft builds'), 'url': self.voll(pfad(lang, 'geplant')), 'inLanguage': lang},
            {'@type': 'ItemList', 'numberOfItems': len(IDS), 'itemListElement': [
                {'@type': 'ListItem', 'position': n + 1, 'name': lok(i, 'titel', lang)} for n, i in enumerate(IDS)]},
            self.krumen_ld([('Start', 'start', None), (t('Geplant', 'Planned'), 'geplant', None)])]}
        self.schreibe('geplant', None,
                      t('Geplante Minecraft-Baupläne: %d Ideen für Farmen, Gebäude und Monumente | Bauwerkstatt',
                        'Planned Minecraft builds: %d ideas for farms, buildings and monuments | Bauwerkstatt') % len(IDS),
                      t('Was als Nächstes kommt: XP-Farmen, Bambusfarm, Fabriken mit dem Crafter, Burg, Kölner Dom, Taj Mahal und mehr. Stimm ab, welcher Minecraft-Bauplan zuerst entsteht.',
                        'What comes next: XP farms, bamboo farm, Crafter factories, castle, Cologne Cathedral, Taj Mahal and more. Vote on which Minecraft build is made first.'),
                      inhalt, ld)

    def fehlerseite(self):
        inhalt = self.kopf(None, 'Seite nicht gefunden · Page not found', 'Diese Seite gibt es nicht (mehr). · This page does not exist.')
        self.schreibe('start', None, 'Seite nicht gefunden | Bauwerkstatt', 'Diese Seite gibt es nicht.', inhalt,
                      {'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Seite nicht gefunden'}, index=False, datei='404.html')

    def sitemap(self):
        heute = date.today().isoformat()
        prio = lambda art: '1.0' if art == 'start' else ('0.8' if art in ('bau', 'liste') else '0.6')
        z = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
        urls = []
        for p_de, p_en, art, id in self.adressen:
            alt = ('<xhtml:link rel="alternate" hreflang="de" href="%s"/><xhtml:link rel="alternate" hreflang="en" href="%s"/>'
                   '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>') % (self.voll(p_de), self.voll(p_en), self.voll(p_de))
            bild = '<image:image><image:loc>%s</image:loc></image:image>' % self.voll('bilder/%s.png' % id) if art == 'bau' else ''
            for p in (p_de, p_en):
                z.append('<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority>%s%s</url>' % (self.voll(p), heute, prio(art), alt, bild))
                urls.append(self.voll(p))
        z.append('</urlset>')
        with open(os.path.join(self.out, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(z) + '\n')
        with open(os.path.join(self.out, 'robots.txt'), 'w', encoding='utf-8') as f:
            f.write('User-agent: *\nAllow: /\n\nSitemap: %s\n' % self.voll('sitemap.xml'))
        key = self.cfg.get('indexnow_key')
        if key:
            with open(os.path.join(self.out, '%s.txt' % key), 'w') as f:
                f.write(key)
        with open(os.path.join(self.out, 'urls.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls) + '\n')
        self.anzahl = len(urls)
