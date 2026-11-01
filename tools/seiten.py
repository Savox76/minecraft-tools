"""Vorgerenderte Seiten für Suchmaschinen: eigenes HTML pro Adresse, Vorschaubilder,
Sitemap, robots.txt, 404-Seite und IndexNow-Schlüssel.

Die Seiten enthalten den vollständigen Text ohne JavaScript. Im Browser ersetzt
site/js/app.js den Inhalt danach durch die interaktive Ansicht.
"""
import html, json, os, re
from datetime import date
from urllib.parse import urlparse

H = html.escape


def kurz(text, n=158):
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) <= n else text[:n - 1].rsplit(' ', 1)[0] + '…'


def fmt(n):
    return f'{n:,}'.replace(',', '.')


def stacks(n):
    s, r = divmod(n, 64)
    return f'{s} St. + {r}' if s and r else (f'{s} St.' if s else str(r))


# ---------------------------------------------------------------- Bilder

FORM = [
    ('mob', r'Dorfbewohner'), ('flat', r'Redstonestaub|Seerosenblatt'), ('low', r'Komparator|Verstärker'),
    ('crop', r'Karotten|Kartoffeln'), ('slab', r'Bett'), ('thin', r'Falltür|Zauntor|Tür|Zaun|Mauer|Eisengitter|Blitzableiter|Laterne|Leiter|fackel|Glasscheibe'),
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


def zeichne_modell(model, breite, hoehe, hintergrund=None, schnitt=False):
    """Isometrisches Bild des fertigen Bauwerks (Pillow)."""
    from PIL import Image, ImageDraw
    S = 2  # Kantenglättung durch doppelte Auflösung
    W, Hh = breite * S, hoehe * S
    img = Image.new('RGBA', (W, Hh), hintergrund + (255,) if hintergrund else (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
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
    if not grid:
        return img.resize((breite, hoehe))
    K = 1.15
    xs = [x - z for (x, y, z) in grid]
    ys = [(x + z) / 2 - (y + 1) * K for (x, y, z) in grid] + [(x + z) / 2 + 1 for (x, y, z) in grid]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys), max(ys)
    a = min(W * .9 / (x1 - x0), Hh * .9 / (y1 - y0))
    ox = W / 2 - (x0 + x1) / 2 * a
    oy = Hh / 2 - (y0 + y1) / 2 * a
    c = a * K

    def P(u, v, y):
        return (ox + (u - v) * a, oy + (u + v) * a / 2 - y * c)

    bg = hintergrund or (238, 241, 244)

    def ton(col, f, misch=0.0):
        col = tuple(int(col[i] + (bg[i] - col[i]) * misch) for i in range(3))
        return tuple(int(v * f) for v in col)

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
            misch = .55
        elif f == 'water':
            misch = .25; y1_ = y + .88
        oben = not (f == 'full' and voll(grid.get((x, y + 1, z))))
        rechts = not (f in ('full', 'glass') and voll(grid.get((x + 1, y, z))))
        links = not (f in ('full', 'glass') and voll(grid.get((x, y, z + 1))))
        if links:
            g.polygon([P(u0, v1, y1_), P(u1, v1, y1_), P(u1, v1, y0_), P(u0, v1, y0_)], fill=ton(col, .64, misch))
        if rechts:
            g.polygon([P(u1, v0, y1_), P(u1, v1, y1_), P(u1, v1, y0_), P(u1, v0, y0_)], fill=ton(col, .8, misch))
        if oben:
            g.polygon([P(u0, v0, y1_), P(u1, v0, y1_), P(u1, v1, y1_), P(u0, v1, y1_)], fill=ton(col, 1, misch))
    return img.resize((breite, hoehe), Image.LANCZOS)


def schrift(groesse, fett=True):
    from PIL import ImageFont
    for pfad in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if fett else []) + \
                ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.isfile(pfad):
            return ImageFont.truetype(pfad, groesse)
    return None


def og_bild(pfad, titel, unterzeile, modell=None, schnitt=False):
    """Vorschaubild 1200 × 630 für Links in Chats und sozialen Netzwerken."""
    from PIL import Image, ImageDraw
    bg = (238, 241, 244)
    img = Image.new('RGB', (1200, 630), bg)
    if modell:
        m = zeichne_modell(modell, 640, 600, schnitt=schnitt)
        img.paste(m, (540, 15), m)
    g = ImageDraw.Draw(img)
    # Marke
    g.polygon([(70, 70), (100, 87), (100, 113), (70, 130), (40, 113), (40, 87)], fill=(27, 35, 44))
    g.polygon([(70, 70), (100, 87), (70, 104), (40, 87)], fill=(244, 180, 0))
    g.polygon([(70, 104), (70, 130), (40, 113), (40, 87)], fill=(74, 88, 102))
    f1, f2, f3 = schrift(30), schrift(64 if len(titel) < 18 else 50), schrift(28, False)
    if f1:
        g.text((118, 82), 'Savox Bauwerkstatt', font=f1, fill=(27, 35, 44))
        # Titel umbrechen
        zeilen, zeile = [], ''
        for wort in titel.split():
            probe = (zeile + ' ' + wort).strip()
            if g.textlength(probe, font=f2) > 520 and zeile:
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
    img.save(pfad, optimize=True)


# ---------------------------------------------------------------- HTML-Bausteine

def punkte(n):
    return '<span class="punkte" aria-label="Schwierigkeit %d von 5">%s</span>' % (
        n, ''.join('<i class="%s"></i>' % ('an' if i <= n else '') for i in range(1, 6)))


def edition(e):
    return ''.join('<span class="marker %s">%s</span>' % (x, 'Java' if x == 'java' else 'Bedrock') for x in e or [])


class Seiten:
    def __init__(self, out, root, cfg, katalog, builds, docs_html):
        self.out, self.root, self.cfg = out, root, cfg
        self.url = cfg['site_url'].rstrip('/') + '/'
        self.base = urlparse(self.url).path or '/'
        self.k, self.builds, self.docs_html = katalog, builds, docs_html
        with open(os.path.join(root, 'site', 'index.html'), encoding='utf-8') as f:
            self.vorlage = f.read()
        self.adressen = []

    # ---------- Hilfen
    def link(self, pfad=''):
        return self.base + pfad

    def voll(self, pfad=''):
        return self.url + pfad

    def schreibe(self, pfad, titel, beschreibung, inhalt, jsonld, bild=None, bild_alt='', og_typ='website',
                 og_titel=None, index=True, datei=None):
        verif = []
        if self.cfg.get('google_site_verification'):
            verif.append('<meta name="google-site-verification" content="%s">' % H(self.cfg['google_site_verification']))
        if self.cfg.get('bing_site_verification'):
            verif.append('<meta name="msvalidate.01" content="%s">' % H(self.cfg['bing_site_verification']))
        felder = {
            'TITEL': H(titel), 'BESCHREIBUNG': H(kurz(beschreibung)), 'BASE': self.base, 'URL': self.voll(pfad),
            'ROBOTS': 'index, follow, max-image-preview:large' if index else 'noindex, follow',
            'OG_TYP': og_typ, 'OG_TITEL': H(og_titel or titel),
            'BILD': self.voll(bild or 'bilder/og-start.png'), 'BILD_ALT': H(bild_alt or titel),
            'VERIFIKATION': '\n'.join(verif), 'JSONLD': json.dumps(jsonld, ensure_ascii=False).replace('</', '<\\/'),
            'INHALT': inhalt, 'FUSS_LINKS': self.fuss_links(),
        }
        text = self.vorlage
        for k, v in felder.items():
            text = text.replace('{{%s}}' % k, v)
        ziel = os.path.join(self.out, datei) if datei else os.path.join(self.out, pfad, 'index.html')
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        with open(ziel, 'w', encoding='utf-8') as f:
            f.write(text)
        if index and not datei:
            self.adressen.append(pfad)

    def fuss_links(self):
        if not hasattr(self, '_fuss'):
            teile = ['<a href="%s">%s</a>' % (self.link('bau/%s/' % b['id']), H(b['titel'])) for b in self.k['builds']]
            teile += ['<a href="%s">%s</a>' % (self.link('plugin/%s/' % p['id']), H(p['name'])) for p in self.k['plugins']]
            teile += ['<a href="%s">%s</a>' % (self.link('anleitung/%s/' % d['id']), H(d['titel'])) for d in self.k['docs']]
            self._fuss = ' '.join(teile)
        return self._fuss

    def krumen_ld(self, teile):
        return {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': self.voll(p)} for i, (n, p) in enumerate(teile)]}

    def bau_karte(self, b):
        return ('<a class="karte" href="%s"><div class="bild"><img src="%s" alt="%s" width="800" height="600" loading="lazy"></div>'
                '<div class="text"><div class="chips">%s%s</div><h3>%s</h3><p>%s</p>'
                '<div class="fakten">%s<span><b>%s</b> Blöcke</span><span><b>%d</b> Schritte</span></div></div></a>') % (
            self.link('bau/%s/' % b['id']), self.link('bilder/%s.png' % b['id']),
            H('Minecraft-Bauplan %s, fertiges Bauwerk' % b['titel']), edition(b['edition']),
            '<span class="marker entwurf">Entwurf</span>' if b['status'] == 'entwurf' else '',
            H(b['titel']), H(b['beschreibung']), punkte(b['schwierigkeit']), fmt(b['bloecke']), b['schritte'])

    def plugin_karte(self, p):
        return ('<a class="karte plugin-karte" href="%s"><div class="text"><h3>%s <span class="marker">v%s</span></h3>'
                '<p>%s</p></div></a>') % (self.link('plugin/%s/' % p['id']), H(p['name']), H(p['version']), H(p['kurz']))

    def doc_link(self, d):
        return ('<a class="liste-link" href="%s"><div><h3>%s</h3><p>%s</p></div><span class="pfeil" aria-hidden="true">→</span></a>'
                % (self.link('anleitung/%s/' % d['id']), H(d['titel']), H(d['kurz'])))

    def kopf(self, eyebrow, titel, lede, krumen=None):
        kr = ''
        if krumen:
            kr = '<div class="krumen">%s</div>' % ' / '.join(
                '<a href="%s">%s</a>' % (self.link(p), H(n)) if p is not None else H(n) for n, p in krumen)
        eb = '<span class="eyebrow">%s</span>' % H(eyebrow) if eyebrow else ''
        return '<section class="detail-kopf"><div class="wrap">%s%s<h1>%s</h1><p class="lede">%s</p></div></section>' % (
            kr, eb, H(titel), H(lede))

    # ---------- Seiten
    def alles(self):
        os.makedirs(os.path.join(self.out, 'bilder'), exist_ok=True)
        self.bilder()
        self.start()
        self.liste_bauplaene()
        for b in self.builds:
            self.bau(b)
        self.liste_plugins()
        for p in self.k['plugins']:
            self.plugin(p)
        self.liste_anleitungen()
        for d in self.k['docs']:
            self.anleitung(d)
        self.wuensche()
        self.fehlerseite()
        self.sitemap()

    def bilder(self):
        for b in self.builds:
            schnitt = bool(b.get('ansicht', {}).get('schnitt'))
            zeichne_modell(b['model'], 800, 600, schnitt=schnitt).save(
                os.path.join(self.out, 'bilder', '%s.png' % b['id']), optimize=True)
            kb = next(x for x in self.k['builds'] if x['id'] == b['id'])
            og_bild(os.path.join(self.out, 'bilder', '%s-og.png' % b['id']), b['titel'],
                    'Minecraft-Bauplan · %d Schritte\n%s Blöcke · Litematica & WorldEdit' % (kb['schritte'], fmt(kb['bloecke'])),
                    b['model'], schnitt)
        vorzeige = next((b for b in self.builds if b['id'] == 'villa-am-wasser'), self.builds[0] if self.builds else None)
        og_bild(os.path.join(self.out, 'bilder', 'og-start.png'), 'Bauen wie mit LEGO',
                'Minecraft-Baupläne Schritt für Schritt\nund Plugins für Paper-Server', vorzeige['model'] if vorzeige else None)
        og_bild(os.path.join(self.out, 'bilder', 'og-plugins.png'), 'Paper-Plugins',
                'Shop, Lager, Arbeiter und mehr\nfür deinen Minecraft-Server')

    def start(self):
        k = self.k
        summe = sum(b['bloecke'] for b in k['builds'])
        inhalt = (
            '<section class="held"><div class="wrap"><div><span class="eyebrow">Minecraft-Baupläne · Paper-Plugins</span>'
            '<h1>Bauen wie mit LEGO. Schritt für Schritt.</h1>'
            '<p class="lede">Minecraft-Baupläne, die pro Schritt genau zeigen, welche Blöcke du brauchst und wo sie hinkommen. '
            'Dazu Plugins für deinen eigenen Paper-Server. Alles kostenlos und einzeln zum Herunterladen.</p>'
            '<div class="knoepfe"><a class="btn" href="%s">Baupläne ansehen</a><a class="btn zwei" href="%s">Bauplan wünschen</a></div>'
            '<div class="zahlen"><div><b>%d</b><span>Baupläne</span></div><div><b>%s</b><span>Blöcke geplant</span></div>'
            '<div><b>%d</b><span>Plugins</span></div><div><b>%d</b><span>Anleitungen</span></div></div></div>'
            '<figure class="held-bild" style="margin:0"><img src="%s" alt="Minecraft-Bauplan Villa am Wasser" width="800" height="600">'
            '<figcaption class="unter"><span>Villa am Wasser</span><a href="%s">Zum Bauplan →</a></figcaption></figure></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>Minecraft-Baupläne</h2><div class="raster" style="margin-top:18px">%s</div></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>Eigene Plugins für Paper</h2><div class="raster" style="margin-top:18px">%s</div></div></section>'
            '<section class="abschnitt"><div class="wrap"><h2>Anleitungen</h2><div style="margin-top:18px">%s</div></div></section>'
        ) % (self.link('bauplaene/'), self.link('wuensche/'), len(k['builds']), fmt(summe), len(k['plugins']), len(k['docs']),
             self.link('bilder/villa-am-wasser.png'), self.link('bau/villa-am-wasser/'),
             ''.join(self.bau_karte(b) for b in k['builds']), ''.join(self.plugin_karte(p) for p in k['plugins']),
             ''.join(self.doc_link(d) for d in k['docs']))
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'WebSite', 'name': 'Savox Bauwerkstatt', 'url': self.voll(), 'inLanguage': 'de',
             'description': 'Minecraft-Baupläne im LEGO-Stil und Plugins für Paper-Server, kostenlos.',
             'publisher': {'@type': 'Person', 'name': 'Savox'}},
            {'@type': 'ItemList', 'name': 'Minecraft-Baupläne', 'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1, 'url': self.voll('bau/%s/' % b['id']), 'name': b['titel']}
                for i, b in enumerate(k['builds'])]}]}
        self.schreibe('', 'Savox Bauwerkstatt – Minecraft-Baupläne im LEGO-Stil & Paper-Plugins',
                      'Kostenlose Minecraft-Baupläne Schritt für Schritt wie bei LEGO: Villen, Leuchtturm, Eiffelturm und Farmen '
                      'mit Teileliste und Download für Litematica und WorldEdit. Dazu Plugins für Paper-Server.',
                      inhalt, ld, og_titel='Savox Bauwerkstatt: Minecraft-Baupläne wie mit LEGO')

    def liste_bauplaene(self):
        k = self.k
        teile = []
        for kat, name in k['kategorien'].items():
            bs = [b for b in k['builds'] if b['kategorie'] == kat]
            if bs:
                teile.append('<h2 style="margin:26px 0 14px">%s</h2><div class="raster">%s</div>' % (H(name), ''.join(self.bau_karte(b) for b in bs)))
        inhalt = self.kopf('Sammlung', 'Minecraft-Baupläne',
                           'Jeden Bauplan gibt es als LEGO-Anleitung im Browser, als Litematica- und WorldEdit-Datei und als Teileliste.') + \
            '<section class="abschnitt" style="padding-top:8px"><div class="wrap">%s</div></section>' % ''.join(teile)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': 'Minecraft-Baupläne', 'url': self.voll('bauplaene/'), 'inLanguage': 'de'},
            self.krumen_ld([('Start', ''), ('Baupläne', 'bauplaene/')])]}
        self.schreibe('bauplaene/', 'Minecraft-Baupläne: Villen, Türme und Farmen Schritt für Schritt | Savox Bauwerkstatt',
                      'Alle Minecraft-Baupläne: Villa am Wasser, moderne, mediterrane und Gründerzeit-Villa, Leuchtturm, Eiffelturm, '
                      'Gewächshaus-Farm und Kellerlager mit Sortieranlage. Mit LEGO-Schritten und Downloads.', inhalt, ld)

    def bau(self, b):
        k = self.k
        kb = next(x for x in k['builds'] if x['id'] == b['id'])
        pal = b['model']['palette']
        kat = k['kategorien'].get(b['kategorie'], '')
        std = b.get('bauzeit_stunden') or [0, 0]
        specs = [('Schwierigkeit', punkte(b['schwierigkeit'])), ('Blöcke', fmt(kb['bloecke'])), ('Schritte', str(kb['schritte'])),
                 ('Grundfläche', H(b.get('grundflaeche', ''))), ('Höhe', '%d Ebenen' % b['model']['size']['y']),
                 ('Bauzeit', '%d–%d Std.' % tuple(std)),
                 ('Edition', ' · '.join('Java' if e == 'java' else 'Bedrock' for e in b.get('edition', [])))]
        teile_rows = ''.join('<tr><td>%s<br><small>%s</small></td><td class="zahl">%s</td><td class="zahl">%s</td></tr>' % (
            H(pal[t['i']]['name'].replace(' (unten)', '')), H((pal[t['i']].get('block') or '').split('[')[0]), fmt(t['n']), stacks(t['n']))
            for t in b['teileliste'])
        roh = ''.join('<tr><td><b>%s</b><br><small>%s · %s</small></td><td class="zahl">%s</td></tr>' % (
            H(r['name']), H(r['quelle']), H(r['hinweis']), fmt(r['menge'])) for r in b.get('rohstoffe', []))
        abschnitte = ''.join('<li><b>%s</b> (%s): %s</li>' % (
            H(a['name']), 'Ebene %d' % a['von'] if a['von'] == a['bis'] else 'Ebenen %d bis %d' % (a['von'], a['bis']), H(a['text']))
            for a in b.get('abschnitte', []))
        tipps = ''.join('<div class="tipp"><b>%s</b>%s</div>' % (H(t['titel']), H(t['text'])) for t in b.get('tipps', []))
        dl = ''.join('<li><a href="%s">%s</a></li>' % (self.link('downloads/%s/%s' % (b['id'], d['datei'])), H(d['datei']))
                     for d in b.get('downloads', []))
        inhalt = (
            '<section class="detail-kopf"><div class="wrap"><div class="krumen"><a href="%s">Baupläne</a> / %s</div>'
            '<h1>%s</h1><p class="lede">%s</p><dl class="specs">%s</dl>%s</div></section>'
            '<section class="tafel"><div class="wrap">'
            '<img class="vor-bild" src="%s" alt="%s" width="800" height="600">'
            '<h2 style="margin:26px 0 10px">Bauabschnitte</h2><ol class="vor-liste">%s</ol>'
            '<p style="margin-top:10px">Die Anleitung führt dich in %d LEGO-Schritten durch den Bau, mit höchstens 60 neuen Blöcken pro Schritt.</p>'
            '<div class="zwei-spalten" style="margin-top:26px"><div><h2 style="margin-bottom:12px">Teileliste</h2><div class="tabelle-huelle"><table>'
            '<thead><tr><th>Block</th><th class="zahl">Anzahl</th><th class="zahl">Stacks</th></tr></thead><tbody>%s</tbody></table></div></div>'
            '<div><h2 style="margin-bottom:12px">Rohstoffe aus Farmen</h2><div class="tabelle-huelle"><table>'
            '<thead><tr><th>Rohstoff</th><th class="zahl">Menge</th></tr></thead><tbody>%s</tbody></table></div>'
            '<h2 style="margin:26px 0 10px">Downloads</h2><ul class="vor-liste">%s</ul></div></div>'
            '%s</div></section>'
        ) % (self.link('bauplaene/'), H(kat), H(b['titel']), H(b['beschreibung']),
             ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % s for s in specs),
             '<div class="hinweis"><span><b>Entwurf:</b> %s</span></div>' % H(b.get('hinweis', '')) if b.get('status') == 'entwurf' else '',
             self.link('bilder/%s.png' % b['id']), H('Minecraft %s, fertig gebaut' % b['titel']),
             abschnitte, kb['schritte'], teile_rows, roh, dl,
             '<h2 style="margin:30px 0 12px">Tipps</h2><div class="raster">%s</div>' % tipps if tipps else '')
        haupt = [t for t in b['teileliste'][:12]]
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'HowTo', 'name': '%s in Minecraft bauen' % b['titel'], 'description': b['beschreibung'],
             'image': self.voll('bilder/%s-og.png' % b['id']), 'inLanguage': 'de',
             'totalTime': 'PT%dH' % max(1, std[0]),
             'supply': [{'@type': 'HowToSupply', 'name': pal[t['i']]['name'].replace(' (unten)', ''), 'requiredQuantity': t['n']} for t in haupt],
             'step': [{'@type': 'HowToSection', 'name': a['name'], 'position': i + 1,
                       'itemListElement': [{'@type': 'HowToStep', 'text': a['text']}]} for i, a in enumerate(b.get('abschnitte', []))],
             'author': {'@type': 'Person', 'name': b.get('autor', 'Savox')}},
            self.krumen_ld([('Start', ''), ('Baupläne', 'bauplaene/'), (b['titel'], 'bau/%s/' % b['id'])])]}
        self.schreibe('bau/%s/' % b['id'],
                      '%s in Minecraft bauen – Bauplan in %d Schritten | Savox Bauwerkstatt' % (b['titel'], kb['schritte']),
                      '%s: Minecraft-Bauplan mit %d LEGO-Schritten, Teileliste (%s Blöcke) und Download für Litematica und WorldEdit. %s' % (
                          b['titel'], kb['schritte'], fmt(kb['bloecke']), b['beschreibung']),
                      inhalt, ld, bild='bilder/%s-og.png' % b['id'], bild_alt='Minecraft-Bauplan %s' % b['titel'],
                      og_typ='article', og_titel='%s – Minecraft-Bauplan' % b['titel'])

    def liste_plugins(self):
        k = self.k
        fremd = ''.join('<li><b>%s</b>%s: %s%s</li>' % (
            H(p['name']), ' (von %s)' % H(p['autor']) if p.get('autor') else '', H(p['zweck']),
            ' <a href="%s" rel="noopener">Download-Seite</a>' % H(p['link']) if p.get('link') else '') for p in k.get('fremd', []))
        inhalt = self.kopf('Für Paper-Server', 'Plugins für Minecraft-Server',
                           'Eigene Plugins für einen fairen Server mit Coins, Lager und Arbeitern, dazu bewährte Plugins anderer Entwickler.') + \
            ('<section class="abschnitt" style="padding-top:8px"><div class="wrap"><h2>Eigene Plugins</h2>'
             '<div class="raster" style="margin-top:14px">%s</div><h2 style="margin-top:30px">Plugins anderer Entwickler</h2>'
             '<ul class="vor-liste">%s</ul></div></section>') % (''.join(self.plugin_karte(p) for p in k['plugins']), fremd)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': 'Plugins für Minecraft-Server', 'url': self.voll('plugins/'), 'inLanguage': 'de'},
            self.krumen_ld([('Start', ''), ('Plugins', 'plugins/')])]}
        self.schreibe('plugins/', 'Paper-Plugins für deinen Minecraft-Server | Savox Bauwerkstatt',
                      'Plugins für Paper-Server: Coin-Shop, unbegrenztes Lager, Dorfbewohner-Arbeiter, Admin-Login, Creeper-Schutz, '
                      'Server-Einstellungen per Chat und ein Hilfe-Buch. Dazu empfohlene Plugins anderer Entwickler.',
                      inhalt, ld, bild='bilder/og-plugins.png')

    def plugin(self, p):
        wer = {'spieler': 'Spieler', 'admin': 'Admin', 'konsole': 'Konsole'}
        befehle = ''.join('<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>' % (H(b['befehl']), H(b['text']), wer.get(b['wer'], b['wer'])) for b in p['befehle'])
        config = ''.join('<tr><td><code>%s</code></td><td><code>%s</code></td><td>%s</td></tr>' % (H(c['schluessel']), H(c['standard']), H(c['text'])) for c in p['config'])
        aend = ''.join('<h3 style="margin-top:14px">%s (%s)</h3><ul class="vor-liste">%s</ul>' % (H(c['version']), H(c['datum']), ''.join('<li>%s</li>' % H(x) for x in c['punkte'])) for c in p['changelog'])
        inhalt = self.kopf(None, p['name'], p['beschreibung'], [('Plugins', 'plugins/')]) + (
            '<section class="tafel"><div class="wrap"><div class="zwei-spalten"><div class="feld"><h2>Funktionen</h2><ul class="funktionen">%s</ul></div>'
            '<div class="feld"><h2>Änderungen</h2>%s</div></div>'
            '<h2 style="margin:28px 0 12px">Befehle</h2><div class="tabelle-huelle"><table><thead><tr><th>Befehl</th><th>Was er macht</th><th>Wer</th></tr></thead><tbody>%s</tbody></table></div>'
            '%s</div></section>') % (
            ''.join('<li>%s</li>' % H(f) for f in p['funktionen']), aend, befehle,
            '<h2 style="margin:28px 0 12px">Einstellungen in der config.yml</h2><div class="tabelle-huelle"><table><thead><tr><th>Schlüssel</th><th>Standard</th><th>Bedeutung</th></tr></thead><tbody>%s</tbody></table></div>' % config if config else '')
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'SoftwareApplication', 'name': p['name'], 'softwareVersion': p['version'], 'description': p['beschreibung'],
             'applicationCategory': 'GameApplication', 'operatingSystem': 'Paper (Minecraft Java Server)', 'inLanguage': 'de',
             'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'author': {'@type': 'Person', 'name': p.get('autor', 'Savox')}},
            self.krumen_ld([('Start', ''), ('Plugins', 'plugins/'), (p['name'], 'plugin/%s/' % p['id'])])]}
        self.schreibe('plugin/%s/' % p['id'], '%s – Minecraft-Plugin für Paper | Savox Bauwerkstatt' % p['name'],
                      '%s %s für Paper-Server: %s Mit allen Befehlen und Einstellungen.' % (p['name'], p['version'], p['kurz']),
                      inhalt, ld, bild='bilder/og-plugins.png', og_titel='%s – Paper-Plugin' % p['name'])

    def liste_anleitungen(self):
        inhalt = self.kopf('Wissen', 'Anleitungen', 'Hilfen rund um deinen Minecraft-Server: Farmen ohne Spieler laufen lassen, Aktionen nachvollziehen und mehr.') + \
            '<section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px">%s</div></section>' % ''.join(self.doc_link(d) for d in self.k['docs'])
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', 'name': 'Anleitungen', 'url': self.voll('anleitungen/'), 'inLanguage': 'de'},
            self.krumen_ld([('Start', ''), ('Anleitungen', 'anleitungen/')])]}
        self.schreibe('anleitungen/', 'Anleitungen für Minecraft-Server | Savox Bauwerkstatt',
                      'Anleitungen für Paper-Server: Farm-Bot, damit Farmen ohne Spieler weiterlaufen, und Spieler-Aktionen mit CoreProtect protokollieren.',
                      inhalt, ld)

    def anleitung(self, d):
        html_text = self.docs_html[d['id']]
        inhalt = self.kopf(None, d['titel'], d['kurz'], [('Anleitungen', 'anleitungen/')]) + \
            '<section class="tafel"><div class="wrap"><article class="prosa">%s</article></div></section>' % html_text
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'TechArticle', 'headline': d['titel'], 'description': d['kurz'], 'inLanguage': 'de',
             'url': self.voll('anleitung/%s/' % d['id']), 'author': {'@type': 'Person', 'name': 'Savox'}},
            self.krumen_ld([('Start', ''), ('Anleitungen', 'anleitungen/'), (d['titel'], 'anleitung/%s/' % d['id'])])]}
        text = re.sub(r'<[^>]+>', ' ', html_text)
        self.schreibe('anleitung/%s/' % d['id'], '%s – Minecraft-Server-Anleitung | Savox Bauwerkstatt' % d['titel'],
                      '%s %s' % (d['kurz'], text), inhalt, ld, og_typ='article')

    def wuensche(self):
        repo = 'https://github.com/Savox76/minecraft-tools'
        inhalt = self.kopf('Mitmachen', 'Bauplan wünschen',
                           'Welches Bauwerk oder Plugin fehlt dir? Reich deinen Wunsch ein und stimm mit 👍 für die Wünsche anderer ab.') + \
            ('<section class="abschnitt" style="padding-top:8px"><div class="wrap"><a class="btn" href="%s/issues/new?template=bauwunsch.yml">Bauplan wünschen</a> '
             '<a class="btn zwei" href="%s/issues/new?template=plugin-wunsch.yml">Plugin wünschen</a></div></section>') % (repo, repo)
        ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Bauplan wünschen', 'url': self.voll('wuensche/'), 'inLanguage': 'de'}
        self.schreibe('wuensche/', 'Minecraft-Bauplan wünschen | Savox Bauwerkstatt',
                      'Wünsch dir einen Minecraft-Bauplan oder ein Plugin. Die meistgewünschten Bauwerke werden zuerst als LEGO-Anleitung gebaut.',
                      inhalt, ld)

    def fehlerseite(self):
        inhalt = self.kopf(None, 'Seite nicht gefunden', 'Diese Seite gibt es nicht (mehr). Schau bei den Bauplänen vorbei.')
        self.schreibe('', 'Seite nicht gefunden | Savox Bauwerkstatt', 'Diese Seite gibt es nicht.', inhalt,
                      {'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Seite nicht gefunden'}, index=False, datei='404.html')

    def sitemap(self):
        heute = date.today().isoformat()
        prio = lambda p: '1.0' if p == '' else ('0.8' if p.startswith('bau/') or p == 'bauplaene/' else '0.6')
        zeilen = ['<?xml version="1.0" encoding="UTF-8"?>',
                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
        for p in self.adressen:
            bild = ''
            if p.startswith('bau/'):
                bid = p.split('/')[1]
                bild = '<image:image><image:loc>%s</image:loc></image:image>' % self.voll('bilder/%s.png' % bid)
            zeilen.append('<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority>%s</url>' % (self.voll(p), heute, prio(p), bild))
        zeilen.append('</urlset>')
        with open(os.path.join(self.out, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(zeilen) + '\n')
        with open(os.path.join(self.out, 'robots.txt'), 'w', encoding='utf-8') as f:
            f.write('User-agent: *\nAllow: /\n\nSitemap: %s\n' % self.voll('sitemap.xml'))
        key = self.cfg.get('indexnow_key')
        if key:
            with open(os.path.join(self.out, '%s.txt' % key), 'w') as f:
                f.write(key)
        with open(os.path.join(self.out, 'urls.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.voll(p) for p in self.adressen) + '\n')
