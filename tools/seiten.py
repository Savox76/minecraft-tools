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
           'anleitungen': 'anleitungen', 'anleitung': 'anleitung', 'wuensche': 'wuensche'},
    'en': {'liste': 'builds', 'bau': 'build', 'plugins': 'plugins', 'plugin': 'plugin',
           'anleitungen': 'guides', 'anleitung': 'guide', 'wuensche': 'wishes'},
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

FORM = [
    ('mob', r'Dorfbewohner'), ('flat', r'Redstonestaub|Seerosenblatt'), ('low', r'Komparator|Verstärker'),
    ('crop', r'Karotten|Kartoffeln'), ('slab', r'Bett'),
    ('thin', r'Falltür|Zauntor|Tür|Zaun|Mauer|Eisengitter|Blitzableiter|Laterne|Leiter|fackel|Glasscheibe'),
    ('slab', r'Stufe'), ('glass', r'^Glas$'), ('water', r'Wasser|Meer'),
]


def form(name):
    for f, rx in FORM:
        if re.search(rx, name):
            return f
    return 'full'


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def zeichne_modell(model, breite, hoehe, schnitt=False, fuellung=.88):
    """Isometrisches Bild des fertigen Bauwerks: transparenter Hintergrund, weicher Bodenschatten,
    feine Kanten. Dreifache Auflösung für saubere Kanten."""
    from PIL import Image, ImageDraw, ImageFilter
    S = 3
    W, Hh = breite * S, hoehe * S
    X, Y, Z = model['size']['x'], model['size']['y'], model['size']['z']
    pal = model['palette']
    idx = {p['key']: i for i, p in enumerate(pal)}
    formen = [form(p['name']) for p in pal]
    farben = [hexrgb(p['color']) for p in pal]
    grid = {}
    for y, ebene in enumerate(model['layers']):
        for z, reihe in enumerate(ebene):
            for x, ch in enumerate(reihe):
                if ch == '.':
                    continue
                n = pal[idx[ch]]['name']
                if schnitt and ('(Decke)' in n or ('(Wand)' in n and (x == X - 1 or z == Z - 1))):
                    continue
                grid[(x, y, z)] = idx[ch]
    bild = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    if not grid:
        return bild.resize((breite, hoehe))
    K = 1.15
    xs = [x - z for (x, y, z) in grid]
    ys = [(x + z) / 2 - (y + 1) * K for (x, y, z) in grid] + [(x + z) / 2 + 1 for (x, y, z) in grid]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys), max(ys) + .6
    a = min(W * fuellung / (x1 - x0), Hh * fuellung / (y1 - y0))
    ox = W / 2 - (x0 + x1) / 2 * a
    oy = Hh / 2 - (y0 + y1) / 2 * a
    c = a * K

    def P(u, v, y):
        return (ox + (u - v) * a, oy + (u + v) * a / 2 - y * c)

    # Bodenschatten
    boden = [P(x + du, z + dv, 0) for (x, y, z) in grid if y <= 1 for du in (0, 1) for dv in (0, 1)]
    schatten = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    if boden:
        bx0, bx1 = min(p[0] for p in boden), max(p[0] for p in boden)
        by0, by1 = min(p[1] for p in boden), max(p[1] for p in boden)
        sg = ImageDraw.Draw(schatten)
        mx, my = (bx0 + bx1) / 2, by1 - (by1 - by0) * .35
        rx, ry = (bx1 - bx0) * .5, max((by1 - by0) * .4, a * 1.5)
        sg.ellipse([mx - rx, my - ry, mx + rx, my + ry], fill=(20, 30, 40, 70))
        schatten = schatten.filter(ImageFilter.GaussianBlur(max(6, a * 1.2)))
    bild.alpha_composite(schatten)

    g = ImageDraw.Draw(bild)
    kanten = a >= 4 * S
    kb = max(1, int(a * .05))

    def ton(col, f, misch=0.0, gegen=(225, 236, 244)):
        col = tuple(int(col[i] + (gegen[i] - col[i]) * misch) for i in range(3))
        return tuple(max(0, min(255, int(v * f))) for v in col) + (255,)

    voll = lambda k: k is not None and formen[k] == 'full'
    for (x, y, z) in sorted(grid, key=lambda p: (p[0] + p[1] + p[2], p[1])):
        k = grid[(x, y, z)]
        f, col = formen[k], farben[k]
        u0, u1, v0, v1, y0_, y1_ = x, x + 1, z, z + 1, y, y + 1
        misch = 0.0
        if f == 'thin':
            u0 += .32; u1 -= .32; v0 += .32; v1 -= .32
        elif f == 'slab':
            y1_ = y + .5
        elif f == 'flat':
            y1_ = y + .07
        elif f == 'low':
            y1_ = y + .14
        elif f == 'crop':
            y1_ = y + .45; u0 += .12; u1 -= .12; v0 += .12; v1 -= .12
        elif f == 'mob':
            y1_ = y + 1.85; u0 += .26; u1 -= .26; v0 += .26; v1 -= .26
        elif f == 'glass':
            misch = .5
        elif f == 'water':
            misch = .2; y1_ = y + .88
        oben = not (f == 'full' and voll(grid.get((x, y + 1, z))))
        rechts = not (f in ('full', 'glass') and voll(grid.get((x + 1, y, z))))
        links = not (f in ('full', 'glass') and voll(grid.get((x, y, z + 1))))
        flaechen = []
        if links:
            flaechen.append(([P(u0, v1, y1_), P(u1, v1, y1_), P(u1, v1, y0_), P(u0, v1, y0_)], .66))
        if rechts:
            flaechen.append(([P(u1, v0, y1_), P(u1, v1, y1_), P(u1, v1, y0_), P(u1, v0, y0_)], .82))
        if oben:
            flaechen.append(([P(u0, v0, y1_), P(u1, v0, y1_), P(u1, v1, y1_), P(u0, v1, y1_)], 1.04))
        for pts, licht in flaechen:
            fuell = ton(col, licht, misch)
            if kanten and f in ('full', 'glass', 'slab'):
                g.polygon(pts, fill=fuell, outline=ton(col, licht * .8, misch), width=kb)
            else:
                g.polygon(pts, fill=fuell)
    return bild.resize((breite, hoehe), Image.LANCZOS)


def schrift(groesse, fett=True):
    from PIL import ImageFont
    for p in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if fett else []) + \
             ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.isfile(p):
            return ImageFont.truetype(p, groesse)
    return None


def og_bild(ziel, titel, unterzeile, modell_bild=None):
    """Link-Vorschau 1200 × 630: Verlauf, Marke, Titel links, Bauwerk rechts."""
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (1200, 630))
    g = ImageDraw.Draw(img)
    for yy in range(630):
        t = yy / 629
        g.line([(0, yy), (1200, yy)], fill=tuple(int(a + (b - a) * t) for a, b in zip((246, 248, 250), (222, 230, 238))))
    if modell_bild is not None:
        img.paste(modell_bild, (520, 10), modell_bild)
    g.polygon([(70, 66), (100, 83), (100, 109), (70, 126), (40, 109), (40, 83)], fill=(27, 35, 44))
    g.polygon([(70, 66), (100, 83), (70, 100), (40, 83)], fill=(244, 180, 0))
    g.polygon([(70, 100), (70, 126), (40, 109), (40, 83)], fill=(74, 88, 102))
    f1, f2, f3 = schrift(30), schrift(64 if len(titel) < 18 else 52), schrift(28, False)
    if not f1:
        img.save(ziel, optimize=True); return
    g.text((118, 78), 'Savox Bauwerkstatt', font=f1, fill=(27, 35, 44))
    zeilen, zeile = [], ''
    for wort in titel.split():
        probe = (zeile + ' ' + wort).strip()
        if g.textlength(probe, font=f2) > 500 and zeile:
            zeilen.append(zeile); zeile = wort
        else:
            zeile = probe
    zeilen.append(zeile)
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
  skip='Zum Inhalt', start='Savox Bauwerkstatt, Startseite', bauplaene='Baupläne', plugins='Plugins',
  anleitungen='Anleitungen', wuensche='Wünsche', sprache='Sprache', thema='Darstellung',
  auto='Automatisch', hell='Hell', dunkel='Dunkel', fuss='Minecraft-Baupläne und Plugins kostenlos für alle Kreativen.',
  github='Quellcode auf GitHub', disclaimer='Kein offizielles Minecraft-Produkt. Nicht von Mojang oder Microsoft genehmigt oder mit ihnen verbunden. Blöcke werden mit eigenen Farben dargestellt, nicht mit Minecraft-Texturen.',
  bloecke='Blöcke', schritte='Schritte', entwurf='Entwurf', alle_seiten='Alle Seiten'),
 'en': dict(
  skip='Skip to content', start='Savox Bauwerkstatt, home', bauplaene='Builds', plugins='Plugins',
  anleitungen='Guides', wuensche='Wishes', sprache='Language', thema='Appearance',
  auto='Automatic', hell='Light', dunkel='Dark', fuss='Minecraft build plans and plugins, free for all creators.',
  github='Source code on GitHub', disclaimer='Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft. Blocks are shown in our own colours, not with Minecraft textures.',
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
    def __init__(self, out, root, cfg, katalog, builds, docs_html, bloecke_en):
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
                      (('liste', 'bauplaene'), ('plugins', 'plugins'), ('anleitungen', 'anleitungen'), ('wuensche', 'wuensche')))
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
            'TXT_SKIP': L['skip'], 'TXT_START': L['start'], 'TXT_FUSS': L['fuss'], 'TXT_GITHUB': L['github'],
            'TXT_DISCLAIMER': L['disclaimer'], 'TXT_ALLE_SEITEN': L['alle_seiten'], 'START': self.link(),
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

    def bau_karte(self, b):
        L = T[self.lang]
        titel = lok(b, 'titel', self.lang)
        return ('<a class="karte" href="%s"><div class="bild" data-kat="%s"><img src="%s" alt="%s" width="800" height="600" loading="lazy"></div>'
                '<div class="text"><div class="chips">%s%s</div><h3>%s</h3><p>%s</p>'
                '<div class="fakten">%s<span><b>%s</b> %s</span><span><b>%d</b> %s</span></div></div></a>') % (
            self.link('bau', b['id']), b['kategorie'], self.base + 'bilder/%s.png' % b['id'],
            H(self.t('Minecraft-Bauplan %s, fertiges Bauwerk', 'Minecraft build %s, finished') % titel), edition(b['edition']),
            '<span class="marker entwurf">%s</span>' % L['entwurf'] if b['status'] == 'entwurf' else '',
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
        eb = '<span class="eyebrow">%s</span>' % H(eyebrow) if eyebrow else ''
        return '<section class="detail-kopf"><div class="wrap">%s%s<h1>%s</h1><p class="lede">%s</p></div></section>' % (
            kr, eb, H(titel), H(lede))

    # ---------- Ablauf
    def alles(self):
        os.makedirs(os.path.join(self.out, 'bilder'), exist_ok=True)
        self.karten_bilder()
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
        self.lang = 'de'
        self.fehlerseite()
        self.sitemap()

    def karten_bilder(self):
        self.modellbilder = {}
        for b in self.builds:
            schnitt = bool(b.get('ansicht', {}).get('schnitt'))
            img = zeichne_modell(b['model'], 800, 600, schnitt=schnitt)
            img.save(os.path.join(self.out, 'bilder', '%s.png' % b['id']), optimize=True)
            self.modellbilder[b['id']] = zeichne_modell(b['model'], 660, 610, schnitt=schnitt, fuellung=.9)

    def og_bilder(self):
        for b in self.builds:
            kb = next(x for x in self.k['builds'] if x['id'] == b['id'])
            og_bild(os.path.join(self.out, self.og(b['id'] + '-og')), lok(b, 'titel', self.lang),
                    self.t('Minecraft-Bauplan · %d Schritte\n%s Blöcke · Litematica & WorldEdit',
                           'Minecraft build · %d steps\n%s blocks · Litematica & WorldEdit') % (kb['schritte'], fmt(kb['bloecke'], self.lang)),
                    self.modellbilder[b['id']])
        og_bild(os.path.join(self.out, self.og('og-start')), self.t('Bauen wie mit LEGO', 'Build like LEGO'),
                self.t('Minecraft-Baupläne Schritt für Schritt\nund Plugins für Paper-Server',
                       'Minecraft build plans step by step\nand plugins for Paper servers'), self.modellbilder.get('villa-am-wasser'))
        og_bild(os.path.join(self.out, self.og('og-plugins')), self.t('Paper-Plugins', 'Paper plugins'),
                self.t('Shop, Lager, Arbeiter und mehr\nfür deinen Minecraft-Server', 'Shop, storage, workers and more\nfor your Minecraft server'))

    # ---------- Seiten
    def start(self):
        k = self.k
        summe = sum(b['bloecke'] for b in k['builds'])
        t = self.t
        inhalt = (
            '<section class="held"><div class="wrap"><div><span class="eyebrow">%s</span>'
            '<h1>%s</h1><p class="lede">%s</p>'
            '<div class="knoepfe"><a class="btn" href="%s">%s</a><a class="btn zwei" href="%s">%s</a></div>'
            '<div class="zahlen"><div><b>%d</b><span>%s</span></div><div><b>%s</b><span>%s</span></div>'
            '<div><b>%d</b><span>Plugins</span></div><div><b>%d</b><span>%s</span></div></div></div>'
            '<figure class="held-bild" style="margin:0"><img src="%s" alt="%s" width="800" height="600">'
            '<figcaption class="unter"><span>%s</span><a href="%s">%s →</a></figcaption></figure></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>%s</h2><div class="raster" style="margin-top:18px">%s</div></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>%s</h2><div class="raster" style="margin-top:18px">%s</div></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>%s</h2><div style="margin-top:18px">%s</div></div></section>'
        ) % (t('Minecraft-Baupläne · Paper-Plugins', 'Minecraft builds · Paper plugins'),
             t('Bauen wie mit LEGO. Schritt für Schritt.', 'Build like LEGO. Step by step.'),
             t('Minecraft-Baupläne, die pro Schritt genau zeigen, welche Blöcke du brauchst und wo sie hinkommen. Dazu Plugins für deinen eigenen Paper-Server. Alles kostenlos und einzeln zum Herunterladen.',
               'Minecraft build plans that show for every step exactly which blocks you need and where they go. Plus plugins for your own Paper server. All free and downloadable one by one.'),
             self.link('liste'), t('Baupläne ansehen', 'Browse builds'), self.link('wuensche'), t('Bauplan wünschen', 'Request a build'),
             len(k['builds']), t('Baupläne', 'Builds'), fmt(summe, self.lang), t('Blöcke geplant', 'Blocks planned'),
             len(k['plugins']), len(k['docs']), t('Anleitungen', 'Guides'),
             self.base + 'bilder/villa-am-wasser.png', t('Minecraft-Bauplan Villa am Wasser', 'Minecraft build Villa by the Water'),
             t('Villa am Wasser', 'Villa by the Water'), self.link('bau', 'villa-am-wasser'), t('Zum Bauplan', 'View build'),
             t('Minecraft-Baupläne', 'Minecraft build plans'), ''.join(self.bau_karte(b) for b in k['builds']),
             t('Eigene Plugins für Paper', 'Our plugins for Paper'), ''.join(self.plugin_karte(p) for p in k['plugins']),
             t('Anleitungen', 'Guides'), ''.join(self.doc_link(d) for d in k['docs']))
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'WebSite', 'name': 'Savox Bauwerkstatt', 'url': self.voll(pfad(self.lang)), 'inLanguage': self.lang,
             'description': t('Minecraft-Baupläne im LEGO-Stil und Plugins für Paper-Server, kostenlos.',
                              'LEGO-style Minecraft build plans and plugins for Paper servers, free.'),
             'publisher': {'@type': 'Person', 'name': 'Savox'}},
            {'@type': 'ItemList', 'name': t('Minecraft-Baupläne', 'Minecraft build plans'), 'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1, 'url': self.voll(pfad(self.lang, 'bau', b['id'])), 'name': lok(b, 'titel', self.lang)}
                for i, b in enumerate(k['builds'])]}]}
        self.schreibe('start', None,
                      t('Savox Bauwerkstatt – Minecraft-Baupläne im LEGO-Stil & Paper-Plugins',
                        'Savox Bauwerkstatt – LEGO-style Minecraft build plans & Paper plugins'),
                      t('Kostenlose Minecraft-Baupläne Schritt für Schritt wie bei LEGO: Villen, Leuchtturm, Eiffelturm und Farmen mit Teileliste und Download für Litematica und WorldEdit. Dazu Plugins für Paper-Server.',
                        'Free step-by-step Minecraft build plans like LEGO instructions: villas, lighthouse, Eiffel Tower and farms with parts list and downloads for Litematica and WorldEdit. Plus plugins for Paper servers.'),
                      inhalt, ld, og_titel=t('Savox Bauwerkstatt: Minecraft-Baupläne wie mit LEGO', 'Savox Bauwerkstatt: Minecraft builds like LEGO'))

    def liste_bauplaene(self):
        k, t = self.k, self.t
        kats = k['kategorien'] if self.lang == 'de' else k['kategorien_en']
        teile = []
        for kat, name in kats.items():
            bs = [b for b in k['builds'] if b['kategorie'] == kat]
            if bs:
                teile.append('<h2 style="margin:26px 0 14px">%s</h2><div class="raster">%s</div>' % (H(name), ''.join(self.bau_karte(b) for b in bs)))
        inhalt = self.kopf(t('Sammlung', 'Collection'), t('Minecraft-Baupläne', 'Minecraft build plans'),
                           t('Jeden Bauplan gibt es als LEGO-Anleitung im Browser, als Litematica- und WorldEdit-Datei und als Teileliste.',
                             'Every build comes as LEGO-style instructions in the browser, as a Litematica and WorldEdit file and as a parts list.')) + \
            '<section class="abschnitt" style="padding-top:8px"><div class="wrap">%s</div></section>' % ''.join(teile)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Minecraft-Baupläne', 'Minecraft build plans'), 'url': self.voll(pfad(self.lang, 'liste')), 'inLanguage': self.lang},
            self.krumen_ld([('Start', 'start', None), (t('Baupläne', 'Builds'), 'liste', None)])]}
        self.schreibe('liste', None,
                      t('Minecraft-Baupläne: Villen, Türme und Farmen Schritt für Schritt | Savox Bauwerkstatt',
                        'Minecraft build plans: villas, towers and farms step by step | Savox Bauwerkstatt'),
                      t('Alle Minecraft-Baupläne: Villa am Wasser, moderne, mediterrane und Gründerzeit-Villa, Leuchtturm, Eiffelturm, Gewächshaus-Farm und Kellerlager mit Sortieranlage. Mit LEGO-Schritten und Downloads.',
                        'All Minecraft build plans: villa by the water, modern, Mediterranean and Victorian-era villa, lighthouse, Eiffel Tower, greenhouse farm and cellar storage with item sorter. With LEGO-style steps and downloads.'),
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
                 ('Edition', ' · '.join('Java' if e == 'java' else 'Bedrock' for e in b.get('edition', [])))]
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
            '<img class="vor-bild" src="%s" alt="%s" width="800" height="600">'
            '<h2 style="margin:26px 0 10px">%s</h2><ol class="vor-liste">%s</ol><p style="margin-top:10px">%s</p>'
            '<div class="zwei-spalten" style="margin-top:26px"><div><h2 style="margin-bottom:12px">%s</h2><div class="tabelle-huelle"><table>'
            '<thead><tr><th>%s</th><th class="zahl">%s</th><th class="zahl">Stacks</th></tr></thead><tbody>%s</tbody></table></div></div>'
            '<div><h2 style="margin-bottom:12px">%s</h2><div class="tabelle-huelle"><table>'
            '<thead><tr><th>%s</th><th class="zahl">%s</th></tr></thead><tbody>%s</tbody></table></div>'
            '<h2 style="margin:26px 0 10px">Downloads</h2><ul class="vor-liste">%s</ul></div></div>%s</div></section>'
        ) % (self.link('liste'), t('Baupläne', 'Builds'), H(kats.get(b['kategorie'], '')), H(titel), H(lok(b, 'beschreibung', lang)),
             ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % s for s in specs),
             '<div class="hinweis"><span><b>%s:</b> %s</span></div>' % (T[lang]['entwurf'], H(lok(b, 'hinweis', lang) or '')) if b.get('status') == 'entwurf' else '',
             self.base + 'bilder/%s.png' % b['id'], H(t('Minecraft %s, fertig gebaut', 'Minecraft %s, finished build') % titel),
             t('Bauabschnitte', 'Build sections'), ab_html,
             t('Die Anleitung führt dich in %d LEGO-Schritten durch den Bau, mit höchstens 60 neuen Blöcken pro Schritt.',
               'The instructions guide you through the build in %d LEGO-style steps, with at most 60 new blocks per step.') % kb['schritte'],
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
                      t('%s in Minecraft bauen – Bauplan in %d Schritten | Savox Bauwerkstatt',
                        'Build the %s in Minecraft – %d-step build plan | Savox Bauwerkstatt') % (titel, kb['schritte']),
                      t('%s: Minecraft-Bauplan mit %d LEGO-Schritten, Teileliste (%s Blöcke) und Download für Litematica und WorldEdit. %s',
                        '%s: Minecraft build plan with %d LEGO-style steps, parts list (%s blocks) and downloads for Litematica and WorldEdit. %s') % (
                          titel, kb['schritte'], fmt(kb['bloecke'], lang), lok(b, 'beschreibung', lang)),
                      inhalt, ld, bild=self.og(b['id'] + '-og'), bild_alt=t('Minecraft-Bauplan %s', 'Minecraft build %s') % titel,
                      og_typ='article', og_titel=t('%s – Minecraft-Bauplan', '%s – Minecraft build plan') % titel)

    def liste_plugins(self):
        k, t = self.k, self.t
        fremd = ''.join('<li><b>%s</b>%s: %s%s</li>' % (
            H(p['name']), (t(' (von %s)', ' (by %s)') % H(p['autor'])) if p.get('autor') else '', H(lok(p, 'zweck', self.lang)),
            ' <a href="%s" rel="noopener">%s</a>' % (H(p['link']), t('Download-Seite', 'Download page')) if p.get('link') else '')
            for p in k.get('fremd', []))
        inhalt = self.kopf(t('Für Paper-Server', 'For Paper servers'), t('Plugins für Minecraft-Server', 'Plugins for Minecraft servers'),
                           t('Eigene Plugins für einen fairen Server mit Coins, Lager und Arbeitern, dazu bewährte Plugins anderer Entwickler.',
                             'Our own plugins for a fair server with coins, storage and workers, plus proven plugins by other developers.')) + \
            ('<section class="abschnitt" style="padding-top:8px"><div class="wrap"><h2>%s</h2>'
             '<div class="raster" style="margin-top:14px">%s</div><h2 style="margin-top:30px">%s</h2>'
             '<ul class="vor-liste">%s</ul></div></section>') % (
                t('Eigene Plugins', 'Our plugins'), ''.join(self.plugin_karte(p) for p in k['plugins']),
                t('Plugins anderer Entwickler', 'Plugins by other developers'), fremd)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Plugins für Minecraft-Server', 'Plugins for Minecraft servers'), 'url': self.voll(pfad(self.lang, 'plugins')), 'inLanguage': self.lang},
            self.krumen_ld([('Start', 'start', None), ('Plugins', 'plugins', None)])]}
        self.schreibe('plugins', None, t('Paper-Plugins für deinen Minecraft-Server | Savox Bauwerkstatt', 'Paper plugins for your Minecraft server | Savox Bauwerkstatt'),
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
            '%s</div></section>') % (
            t('Funktionen', 'Features'), ''.join('<li>%s</li>' % H(f) for f in lok(p, 'funktionen', lang)),
            t('Änderungen', 'Changelog'), aend_html, t('Befehle', 'Commands'), t('Befehl', 'Command'), t('Was er macht', 'What it does'), t('Wer', 'Who'), befehle,
            ('<h2 style="margin:28px 0 12px">%s</h2><div class="tabelle-huelle"><table><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>' % (
                t('Einstellungen in der config.yml', 'Settings in config.yml'), t('Schlüssel', 'Key'), t('Standard', 'Default'), t('Bedeutung', 'Meaning'), config)) if config else '')
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'SoftwareApplication', 'name': p['name'], 'softwareVersion': p['version'], 'description': lok(p, 'beschreibung', lang),
             'applicationCategory': 'GameApplication', 'operatingSystem': 'Paper (Minecraft Java Server)', 'inLanguage': lang,
             'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'author': {'@type': 'Person', 'name': p.get('autor', 'Savox')}},
            self.krumen_ld([('Start', 'start', None), ('Plugins', 'plugins', None), (p['name'], 'plugin', p['id'])])]}
        self.schreibe('plugin', p['id'], t('%s – Minecraft-Plugin für Paper | Savox Bauwerkstatt', '%s – Minecraft plugin for Paper | Savox Bauwerkstatt') % p['name'],
                      t('%s %s für Paper-Server: %s Mit allen Befehlen und Einstellungen.', '%s %s for Paper servers: %s With all commands and settings.') % (
                          p['name'], p['version'], lok(p, 'kurz', lang)),
                      inhalt, ld, bild=self.og('og-plugins'), og_titel=t('%s – Paper-Plugin', '%s – Paper plugin') % p['name'])

    def liste_anleitungen(self):
        t = self.t
        inhalt = self.kopf(t('Wissen', 'Knowledge'), t('Anleitungen', 'Guides'),
                           t('Hilfen rund um deinen Minecraft-Server: Farmen ohne Spieler laufen lassen, Aktionen nachvollziehen und mehr.',
                             'Help for your Minecraft server: keep farms running without players, trace player actions and more.')) + \
            '<section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px">%s</div></section>' % ''.join(self.doc_link(d) for d in self.k['docs'])
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': t('Anleitungen', 'Guides'), 'url': self.voll(pfad(self.lang, 'anleitungen')), 'inLanguage': self.lang},
            self.krumen_ld([('Start', 'start', None), (t('Anleitungen', 'Guides'), 'anleitungen', None)])]}
        self.schreibe('anleitungen', None, t('Anleitungen für Minecraft-Server | Savox Bauwerkstatt', 'Guides for Minecraft servers | Savox Bauwerkstatt'),
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
        self.schreibe('anleitung', d['id'], t('%s – Minecraft-Server-Anleitung | Savox Bauwerkstatt', '%s – Minecraft server guide | Savox Bauwerkstatt') % titel,
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
        self.schreibe('wuensche', None, t('Minecraft-Bauplan wünschen | Savox Bauwerkstatt', 'Request a Minecraft build | Savox Bauwerkstatt'),
                      t('Wünsch dir einen Minecraft-Bauplan oder ein Plugin. Die meistgewünschten Bauwerke werden zuerst als LEGO-Anleitung gebaut.',
                        'Request a Minecraft build plan or a plugin. The most requested builds are made into LEGO-style instructions first.'), inhalt, ld)

    def fehlerseite(self):
        inhalt = self.kopf(None, 'Seite nicht gefunden · Page not found', 'Diese Seite gibt es nicht (mehr). · This page does not exist.')
        self.schreibe('start', None, 'Seite nicht gefunden | Savox Bauwerkstatt', 'Diese Seite gibt es nicht.', inhalt,
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
