#!/usr/bin/env python3
"""Baut die Website aus den Quellen im Repo.

Liest  builds/*/build.json + model.json, plugins/eigene/*/plugin.json, plugins/fremd/plugins.json, docs/*.md
und optional tools/cache/wuensche.json (wird vom Workflow aus GitHub-Issues erzeugt).

Schreibt nach  _site/ :
  index.html, Styles, Skripte (aus site/)
  data/katalog.json            Übersicht aller Einträge
  data/builds/<id>.json        Modell, Bauschritte, Teileliste
  data/seiten/<id>.html        Anleitungs-Texte als HTML
  <pfad>/index.html            vorgerenderte Seiten mit Meta-Daten (tools/seiten.py)
  bilder/, sitemap.xml, robots.txt, 404.html
  downloads/<id>/...           .litematic, .schem, teileliste.csv

Aufruf:  python tools/build_site.py [--ohne-exporte]
"""
import csv, gzip, io, json, math, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site')
MAX_TEILE = 60          # höchstens so viele neue Blöcke pro Bauschritt
DATA_VERSION = 3953     # Minecraft Java 1.21, ältere Versionen werden beim Laden automatisch umgewandelt

KATEGORIEN = {
    'tuerme': 'Türme & Wahrzeichen',
    'villen': 'Villen',
    'technik': 'Farmen & Technik',
}
PLUGIN_KATEGORIEN = {
    'sicherheit': 'Sicherheit', 'wirtschaft': 'Wirtschaft', 'lager': 'Lager',
    'schutz': 'Schutz', 'verwaltung': 'Verwaltung',
}
KATEGORIEN_EN = {'tuerme': 'Towers & landmarks', 'villen': 'Villas', 'technik': 'Farms & technology'}
PLUGIN_KATEGORIEN_EN = {'sicherheit': 'Security', 'wirtschaft': 'Economy', 'lager': 'Storage',
                        'schutz': 'Protection', 'verwaltung': 'Administration'}
# Englische Adress-Teile für Links in den Anleitungen (#/plugin/x -> en/plugin/x/)
SEG_EN = {'bauplaene': 'builds', 'bau': 'build', 'anleitungen': 'guides', 'anleitung': 'guide', 'wuensche': 'wishes'}


def lies_json(pfad):
    with open(pfad, encoding='utf-8') as f:
        return json.load(f)


def schreib_json(pfad, daten):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(daten, f, ensure_ascii=False, separators=(',', ':'))


def block_id(spec):
    """'minecraft:oak_door[half=upper]' -> ('minecraft:oak_door', {'half': 'upper'})"""
    m = re.match(r'^([^\[]+)(?:\[(.*)\])?$', spec)
    props = {}
    if m.group(2):
        for teil in m.group(2).split(','):
            k, v = teil.split('=')
            props[k.strip()] = v.strip()
    return m.group(1), props


# ---------------------------------------------------------------- Baupläne

def zaehlt(p):
    return not set(p.get('flags', [])) & {'vorhanden', 'kein-block', 'zweiter-teil'}


def exportierbar(p):
    return p.get('block') and not set(p.get('flags', [])) & {'vorhanden', 'kein-block'}


def zellen(model):
    """Alle Blöcke als (x, y, z, palettenindex)."""
    idx = {p['key']: i for i, p in enumerate(model['palette'])}
    for y, ebene in enumerate(model['layers']):
        for z, reihe in enumerate(ebene):
            for x, ch in enumerate(reihe):
                if ch != '.':
                    yield x, y, z, idx[ch]


def bau_schritte(build, model):
    """Teilt das Modell in Bauschritte: Ebene für Ebene von unten nach oben.

    Jeder Schritt gehört zu genau einer Ebene. Ebenen mit mehr als MAX_TEILE neuen Blöcken
    werden in gleich große Teile zerlegt (Kacheln von 8 × 8 in Schlangenlinie), damit man
    beim Bauen nicht kreuz und quer laufen muss. 't' = [Teil, Anzahl Teile] der Ebene.
    """
    pal = model['palette']
    pro_ebene, zweite = {}, []
    for x, y, z, i in zellen(model):
        flags = pal[i].get('flags', [])
        if 'vorhanden' in flags:
            continue
        if 'zweiter-teil' in flags:      # obere Türhälfte, Kopfteil vom Bett: entsteht mit dem ersten Teil
            zweite.append((x, y, z, i))
            continue
        pro_ebene.setdefault(y, []).append((x, y, z, i))

    abschnitte = build.get('abschnitte') or [{'name': 'Bau', 'von': 0, 'bis': model['size']['y'] - 1}]

    def abschnitt(y):
        for ai, ab in enumerate(abschnitte):
            if ab['von'] <= y <= ab['bis']:
                return ai
        return len(abschnitte) - 1

    def ordnung(c):
        tz, tx = c[2] // 8, c[0] // 8
        return (tz, tx if tz % 2 == 0 else -tx, c[2], c[0])

    schritte = []
    for y in sorted(pro_ebene):
        neu = sorted(pro_ebene[y], key=ordnung)
        n = math.ceil(len(neu) / MAX_TEILE)
        groesse = math.ceil(len(neu) / n)
        for k in range(n):
            teil = neu[k * groesse:(k + 1) * groesse]
            if teil:
                schritte.append({'a': abschnitt(y), 'y': [y, y], 't': [k + 1, n], 'c': list(teil)})
    # zweite Teile in den Schritt ihres ersten Teils (darunter oder daneben)
    wo = {(c[0], c[1], c[2]): k for k, st in enumerate(schritte) for c in st['c']}
    for x, y, z, i in zweite:
        k = next((wo[q] for q in ((x, y - 1, z), (x + 1, y, z), (x - 1, y, z), (x, y, z + 1), (x, y, z - 1)) if q in wo), None)
        if k is None:
            k = max((j for j, st in enumerate(schritte) if st['y'][0] <= y), default=0)
        schritte[k]['c'].append((x, y, z, i))
    for st in schritte:
        st['c'] = [v for zelle in st['c'] for v in zelle]   # flach: x,y,z,i,x,y,z,i,...
    return schritte


def teileliste(model):
    menge = {}
    for _, _, _, i in zellen(model):
        if zaehlt(model['palette'][i]):
            menge[i] = menge.get(i, 0) + 1
    return sorted(menge.items(), key=lambda kv: -kv[1])


def export_litematic(build, model, pfad):
    from litemapy import Region, BlockState
    s = model['size']
    reg = Region(0, 0, 0, s['x'], s['y'], s['z'])
    cache = {}
    for x, y, z, i in zellen(model):
        p = model['palette'][i]
        if not exportierbar(p):
            continue
        if i not in cache:
            bid, props = block_id(p['block'])
            cache[i] = BlockState(bid, **props)
        reg[x, y, z] = cache[i]
    schem = reg.as_schematic(name=build['titel'], author=build.get('autor', ''),
                             description=build.get('beschreibung', '')[:200], mc_version=DATA_VERSION)
    schem.save(pfad)


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return out


def export_schem(build, model, pfad):
    """Sponge-Schematic Version 2 (WorldEdit / FAWE)."""
    import nbtlib
    from nbtlib import tag
    s = model['size']
    W, H, L = s['x'], s['y'], s['z']
    palette = {'minecraft:air': 0}
    ids = [0] * (W * H * L)
    for x, y, z, i in zellen(model):
        p = model['palette'][i]
        if not exportierbar(p):
            continue
        spec = p['block']
        if spec not in palette:
            palette[spec] = len(palette)
        ids[x + z * W + y * W * L] = palette[spec]
    data = bytearray()
    for v in ids:
        data += varint(v)
    root = nbtlib.Compound({
        'Version': tag.Int(2),
        'DataVersion': tag.Int(DATA_VERSION),
        'Width': tag.Short(W), 'Height': tag.Short(H), 'Length': tag.Short(L),
        'PaletteMax': tag.Int(len(palette)),
        'Palette': nbtlib.Compound({k: tag.Int(v) for k, v in palette.items()}),
        'BlockData': tag.ByteArray([b if b < 128 else b - 256 for b in data]),
        'Offset': tag.IntArray([0, 0, 0]),
        'Metadata': nbtlib.Compound({'Name': tag.String(build['titel']), 'Author': tag.String(build.get('autor', ''))}),
    })
    nbtlib.File({'Schematic': root}, gzipped=True).save(pfad)


def export_csv(build, model, liste, pfad):
    with open(pfad, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['Block', 'Minecraft-ID', 'Anzahl', 'Stacks (64)'])
        for i, n in liste:
            p = model['palette'][i]
            w.writerow([p['name'], p.get('block') or '', n, f'{n // 64} + {n % 64}'])


# ---------------------------------------------------------------- Texte

def front_matter(text):
    meta = {}
    if text.startswith('---'):
        ende = text.index('\n---', 3)
        for zeile in text[3:ende].strip().splitlines():
            if ':' in zeile:
                k, v = zeile.split(':', 1)
                meta[k.strip()] = v.strip()
        text = text[ende + 4:]
    return meta, text


def md_html(text):
    import markdown
    text = re.sub(r'^# .*\n', '', text.lstrip(), count=1)   # Titel zeigt die Seite selbst
    return markdown.markdown(text, extensions=['tables', 'fenced_code'])


# ---------------------------------------------------------------- Hauptablauf

def main():
    exporte = '--ohne-exporte' not in sys.argv
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, 'site'), OUT)
    # Versionsnummer gegen veraltete Dateien im Browser-Zwischenspeicher (GitHub Pages speichert 10 Minuten)
    import time
    version = (os.environ.get('GITHUB_SHA') or '')[:8] or time.strftime('%Y%m%d%H%M%S')
    pfad_js = os.path.join(OUT, 'js', 'app.js')
    with open(pfad_js, encoding='utf-8') as f:
        js = f.read()
    js = js.replace('__VERSION__', version).replace("from './render.js'", "from './render.js?v=%s'" % version)
    with open(pfad_js, 'w', encoding='utf-8') as f:
        f.write(js)
    pfad_css = os.path.join(OUT, 'style.css')
    with open(pfad_css, encoding='utf-8') as f:
        css = f.read()
    with open(pfad_css, 'w', encoding='utf-8') as f:
        f.write(css.replace('__VERSION__', version))

    katalog = {'builds': [], 'plugins': [], 'fremd': [], 'docs': [], 'wuensche': [], 'kategorien': KATEGORIEN,
               'plugin_kategorien': PLUGIN_KATEGORIEN, 'kategorien_en': KATEGORIEN_EN,
               'plugin_kategorien_en': PLUGIN_KATEGORIEN_EN}
    bloecke_en = lies_json(os.path.join(ROOT, 'tools', 'i18n', 'bloecke_en.json'))
    cfg = lies_json(os.path.join(ROOT, 'tools', 'site_config.json'))
    if os.environ.get('SITE_URL'):
        cfg['site_url'] = os.environ['SITE_URL']
    cfg['version'] = version
    from urllib.parse import urlparse
    base = urlparse(cfg['site_url']).path or '/'
    alle_builds, docs_html = [], {}

    for bid in sorted(os.listdir(os.path.join(ROOT, 'builds'))):
        ordner = os.path.join(ROOT, 'builds', bid)
        if not os.path.isfile(os.path.join(ordner, 'build.json')):
            continue
        build = lies_json(os.path.join(ordner, 'build.json'))
        model = lies_json(os.path.join(ordner, 'model.json'))
        assert build['id'] == bid, f'{bid}: id in build.json passt nicht zum Ordnernamen'
        for p in model['palette']:
            if p['name'] not in bloecke_en:
                print(f'  Hinweis: keine englische Bezeichnung für „{p["name"]}“ (tools/i18n/bloecke_en.json)')
            p['name_en'] = bloecke_en.get(p['name'], p['name'])
        liste = teileliste(model)
        schritte = bau_schritte(build, model)
        downloads = []
        if exporte:
            ziel = os.path.join(OUT, 'downloads', bid)
            os.makedirs(ziel, exist_ok=True)
            export_litematic(build, model, os.path.join(ziel, f'{bid}.litematic'))
            downloads.append({'datei': f'{bid}.litematic', 'art': 'litematic'})
            export_schem(build, model, os.path.join(ziel, f'{bid}.schem'))
            downloads.append({'datei': f'{bid}.schem', 'art': 'schem'})
            export_csv(build, model, liste, os.path.join(ziel, f'{bid}-teileliste.csv'))
            downloads.append({'datei': f'{bid}-teileliste.csv', 'art': 'csv'})
            for d in downloads:
                d['groesse'] = os.path.getsize(os.path.join(ziel, d['datei']))
        gesamt = sum(n for _, n in liste)
        daten = {**build, 'model': model, 'schritte': schritte,
                 'teileliste': [{'i': i, 'n': n} for i, n in liste], 'downloads': downloads}
        schreib_json(os.path.join(OUT, 'data', 'builds', f'{bid}.json'), daten)
        alle_builds.append(daten)
        katalog['builds'].append({
            k: build.get(k) for k in ('id', 'titel', 'beschreibung', 'kategorie', 'tags', 'edition',
                                      'schwierigkeit', 'bauzeit_stunden', 'grundflaeche', 'status')
        } | {'plugins': [{'id': x['id'], 'stufe': x['stufe']} for x in build.get('plugins', [])],
             'en': {k: build.get('en', {}).get(k) for k in ('titel', 'beschreibung', 'grundflaeche')},
             'bloecke': gesamt, 'schritte': len(schritte), 'hoehe': model['size']['y'],
             'blocksorten': len(liste)})
        print(f'Bauplan  {bid:22} {gesamt:6} Blöcke  {len(schritte):4} Schritte')

    for pid in sorted(os.listdir(os.path.join(ROOT, 'plugins', 'eigene'))):
        ordner = os.path.join(ROOT, 'plugins', 'eigene', pid)
        if not os.path.isfile(os.path.join(ordner, 'plugin.json')):
            continue
        p = lies_json(os.path.join(ordner, 'plugin.json'))
        katalog['plugins'].append(p)
        print(f'Plugin   {pid}')

    fremd = os.path.join(ROOT, 'plugins', 'fremd', 'plugins.json')
    if os.path.isfile(fremd):
        katalog['fremd'] = lies_json(fremd)
        print(f'Fremde Plugins: {len(katalog["fremd"])}')

    def link_de(m):
        return 'href="%s%s/"' % (base, m.group(1).rstrip('/'))

    def link_en(m):
        teile = m.group(1).rstrip('/').split('/')
        teile[0] = SEG_EN.get(teile[0], teile[0])
        return 'href="%sen/%s/"' % (base, '/'.join(teile))

    os.makedirs(os.path.join(OUT, 'data', 'seiten'), exist_ok=True)
    for name in sorted(os.listdir(os.path.join(ROOT, 'docs'))):
        if not name.endswith('.md'):
            continue
        did = name[:-3]
        with open(os.path.join(ROOT, 'docs', name), encoding='utf-8') as f:
            meta, text = front_matter(f.read())
        eintrag = {'id': did, 'titel': meta.get('titel', did), 'kurz': meta.get('kurz', ''),
                   'reihenfolge': int(meta.get('reihenfolge', 99))}
        sprachen = [('de', meta, text, link_de, '')]
        en_pfad = os.path.join(ROOT, 'docs', 'en', name)
        if os.path.isfile(en_pfad):
            with open(en_pfad, encoding='utf-8') as f:
                meta_en, text_en = front_matter(f.read())
            eintrag['en'] = {'titel': meta_en.get('titel', eintrag['titel']), 'kurz': meta_en.get('kurz', eintrag['kurz'])}
            sprachen.append(('en', meta_en, text_en, link_en, '.en'))
        else:
            print(f'  Hinweis: keine englische Fassung docs/en/{name}')
        for lang, _, txt, umschreiben, endung in sprachen:
            inhalt = re.sub(r'href="#/([^"]+)"', umschreiben, md_html(txt))
            docs_html[(did, lang)] = inhalt
            with open(os.path.join(OUT, 'data', 'seiten', f'doc-{did}{endung}.html'), 'w', encoding='utf-8') as f:
                f.write(inhalt)
        katalog['docs'].append(eintrag)
        print(f'Anleitung {did} ({", ".join(x[0] for x in sprachen)})')
    katalog['docs'].sort(key=lambda d: d['reihenfolge'])

    wpfad = os.path.join(ROOT, 'tools', 'cache', 'wuensche.json')
    if os.path.isfile(wpfad):
        katalog['wuensche'] = lies_json(wpfad)

    # Plugin-Angaben in Bauplänen und Ideen prüfen: jede ID muss ein eigenes oder fremdes Plugin sein
    bekannte = {x['id'] for x in katalog['plugins']} | {x['id'] for x in katalog['fremd']}
    STUFEN = {'benoetigt', 'empfohlen', 'optional'}

    def pruefe_plugins(wo, liste):
        for x in liste or []:
            if x.get('id') not in bekannte:
                sys.exit(f'{wo}: unbekanntes Plugin „{x.get("id")}“ (erlaubt: {", ".join(sorted(bekannte))})')
            if x.get('stufe') not in STUFEN:
                sys.exit(f'{wo}: Stufe muss benoetigt, empfohlen oder optional sein, nicht „{x.get("stufe")}“')

    for b in alle_builds:
        pruefe_plugins(f'builds/{b["id"]}/build.json', b.get('plugins'))

    # Ideen für die Seite „Geplant“ (Quelle: ideen/ideen.json, siehe Masterplan Abschnitt 15)
    ideen = lies_json(os.path.join(ROOT, 'ideen', 'ideen.json'))
    ideen.pop('_hinweis', None)
    gebaut = {b['id'] for b in katalog['builds']}
    for i in ideen['ideen']:
        pruefe_plugins(f'ideen/ideen.json Nr. {i["nr"]}', i.get('plugins'))
        if i.get('bauplan') and i['bauplan'] not in gebaut:
            print(f'  Hinweis: Idee {i["nr"]} verweist auf unbekannten Bauplan {i["bauplan"]}')
    # Fertige Ideen (status verfuegbar) sind jetzt Baupläne: sie stehen nur noch im Masterplan unter „Umgesetzt“
    umgesetzt = [i for i in ideen['ideen'] if i['status'] == 'verfuegbar']
    ideen['ideen'] = [i for i in ideen['ideen'] if i['status'] != 'verfuegbar']
    ideen['umgesetzt'] = len(umgesetzt)
    schreib_json(os.path.join(OUT, 'data', 'ideen.json'), ideen)
    katalog['ideen_anzahl'] = len(ideen['ideen'])
    katalog['ideen_umgesetzt'] = len(umgesetzt)
    print(f'Ideen    {len(ideen["ideen"])} offen, {len(umgesetzt)} umgesetzt')
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'ideen_masterplan.py'), '--pruefen'])

    schreib_json(os.path.join(OUT, 'data', 'katalog.json'), katalog)
    with open(os.path.join(OUT, '.nojekyll'), 'w') as f:
        f.write('')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from seiten import Seiten
    s = Seiten(OUT, ROOT, cfg, katalog, alle_builds, docs_html, bloecke_en, ideen)
    s.alles()
    print(f'Seiten: {s.anzahl} Adressen (Deutsch und Englisch) in sitemap.xml · Basis {cfg["site_url"]}')
    print('Fertig:', OUT)


if __name__ == '__main__':
    main()
