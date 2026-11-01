#!/usr/bin/env python3
"""Baut die Website aus den Quellen im Repo.

Liest  builds/*/build.json + model.json, plugins/eigene/*/plugin.json, plugins/fremd/plugins.json, docs/*.md
und optional tools/cache/wuensche.json (wird vom Workflow aus GitHub-Issues erzeugt).

Schreibt nach  _site/ :
  index.html, Styles, Skripte (aus site/)
  data/katalog.json            Übersicht aller Einträge
  data/builds/<id>.json        Modell, LEGO-Schritte, Teileliste
  data/seiten/<id>.html        Anleitungs-Texte als HTML
  <pfad>/index.html            vorgerenderte Seiten mit Meta-Daten (tools/seiten.py)
  bilder/, sitemap.xml, robots.txt, 404.html
  downloads/<id>/...           .litematic, .schem, teileliste.csv

Aufruf:  python tools/build_site.py [--ohne-exporte]
"""
import csv, gzip, io, json, math, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site')
MAX_TEILE = 60          # höchstens so viele neue Blöcke pro LEGO-Schritt
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


def lego_schritte(build, model):
    """Teilt das Modell in LEGO-Schritte mit höchstens MAX_TEILE neuen Blöcken."""
    pal = model['palette']
    pro_ebene = {}
    for x, y, z, i in zellen(model):
        if 'vorhanden' in pal[i].get('flags', []):
            continue
        pro_ebene.setdefault(y, []).append((x, y, z, i))

    abschnitte = build.get('abschnitte') or [{'name': 'Bau', 'von': 0, 'bis': model['size']['y'] - 1}]
    schritte = []
    vergeben = set()
    for ai, ab in enumerate(abschnitte):
        offen = []          # gesammelte kleine Ebenen
        offen_y = []

        def abschliessen():
            if offen:
                schritte.append({'a': ai, 'y': [offen_y[0], offen_y[-1]], 'c': list(offen)})
                offen.clear(); offen_y.clear()

        for y in range(ab['von'], ab['bis'] + 1):
            if y in vergeben:
                continue
            vergeben.add(y)
            neu = pro_ebene.get(y, [])
            if not neu:
                continue
            if len(neu) <= MAX_TEILE:
                if len(offen) + len(neu) > MAX_TEILE:
                    abschliessen()
                offen.extend(neu); offen_y.append(y)
                continue
            abschliessen()
            # große Ebene: in Kacheln von 8 × 8 aufteilen, Schlangenlinie, gleich große Stücke
            def ordnung(c):
                tz, tx = c[2] // 8, c[0] // 8
                return (tz, tx if tz % 2 == 0 else -tx, c[2], c[0])
            neu.sort(key=ordnung)
            n = math.ceil(len(neu) / MAX_TEILE)
            groesse = math.ceil(len(neu) / n)
            for k in range(0, len(neu), groesse):
                schritte.append({'a': ai, 'y': [y, y], 'c': neu[k:k + groesse]})
        abschliessen()
    # Ebenen, die in keinem Abschnitt stehen
    rest = sorted(y for y in pro_ebene if y not in vergeben)
    for y in rest:
        schritte.append({'a': len(abschnitte) - 1, 'y': [y, y], 'c': pro_ebene[y]})
    for s in schritte:
        s['c'] = [v for zelle in s['c'] for v in zelle]   # flach: x,y,z,i,x,y,z,i,...
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

    katalog = {'builds': [], 'plugins': [], 'fremd': [], 'docs': [], 'wuensche': [], 'kategorien': KATEGORIEN,
               'plugin_kategorien': PLUGIN_KATEGORIEN}
    cfg = lies_json(os.path.join(ROOT, 'tools', 'site_config.json'))
    if os.environ.get('SITE_URL'):
        cfg['site_url'] = os.environ['SITE_URL']
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
        liste = teileliste(model)
        schritte = lego_schritte(build, model)
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
        } | {'bloecke': gesamt, 'schritte': len(schritte), 'hoehe': model['size']['y'],
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

    for name in sorted(os.listdir(os.path.join(ROOT, 'docs'))):
        if not name.endswith('.md'):
            continue
        did = name[:-3]
        with open(os.path.join(ROOT, 'docs', name), encoding='utf-8') as f:
            meta, text = front_matter(f.read())
        os.makedirs(os.path.join(OUT, 'data', 'seiten'), exist_ok=True)
        inhalt = re.sub(r'href="#/([^"]+)"', lambda m: 'href="%s%s/"' % (base, m.group(1).rstrip('/')), md_html(text))
        docs_html[did] = inhalt
        with open(os.path.join(OUT, 'data', 'seiten', f'doc-{did}.html'), 'w', encoding='utf-8') as f:
            f.write(inhalt)
        katalog['docs'].append({'id': did, 'titel': meta.get('titel', did), 'kurz': meta.get('kurz', ''),
                                'reihenfolge': int(meta.get('reihenfolge', 99))})
        print(f'Anleitung {did}')
    katalog['docs'].sort(key=lambda d: d['reihenfolge'])

    wpfad = os.path.join(ROOT, 'tools', 'cache', 'wuensche.json')
    if os.path.isfile(wpfad):
        katalog['wuensche'] = lies_json(wpfad)

    schreib_json(os.path.join(OUT, 'data', 'katalog.json'), katalog)
    with open(os.path.join(OUT, '.nojekyll'), 'w') as f:
        f.write('')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from seiten import Seiten
    s = Seiten(OUT, ROOT, cfg, katalog, alle_builds, docs_html)
    s.alles()
    print(f'Seiten: {len(s.adressen)} Adressen in sitemap.xml · Basis {cfg["site_url"]}')
    print('Fertig:', OUT)


if __name__ == '__main__':
    main()
