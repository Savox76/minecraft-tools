"""Schreibt die automatisch erzeugten Tabellen in den Masterplan:
Abschnitt 15 (Ideen aus ideen/ideen.json) und 16.6 (welcher Bauplan und welche Idee welches Plugin braucht).

Aufruf nach jeder Änderung an ideen/ideen.json:
    python tools/ideen_masterplan.py
Mit --pruefen wird nur geprüft, ob der Masterplan aktuell ist (wird von build_site.py genutzt).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, ENDE = '<!-- ideen:start -->', '<!-- ideen:ende -->'
A_START, A_ENDE = '<!-- abhaengigkeiten:start -->', '<!-- abhaengigkeiten:ende -->'
STUFE_TXT = {'benoetigt': 'benötigt', 'empfohlen': 'empfohlen', 'optional': 'optional'}
STATUS = {'idee': '💡 Idee', 'in-arbeit': '🔨 in Arbeit', 'verfuegbar': '✅ verfügbar'}


def tabellen(daten):
    zeilen = []
    ideen = daten['ideen']
    zaehl = {s: sum(1 for i in ideen if i['status'] == s) for s in STATUS}
    zeilen.append('%d Einträge: %s.' % (len(ideen), ', '.join('%d %s' % (zaehl[s], STATUS[s]) for s in STATUS)))
    empf = [i for i in ideen if i.get('empfohlen')]
    if empf:
        zeilen.append('')
        zeilen.append('**Als Nächstes empfohlen:** ' + ', '.join('Nr. %s %s' % (i['nr'], i['titel']) for i in empf) + '.')
    for k in daten['kategorien']:
        liste = [i for i in ideen if i['kategorie'] == k['id']]
        if not liste:
            continue
        zeilen += ['', '### %s (%d)' % (k['name'], len(liste)), '', k['text'], '']
        if k['id'] == 'anleitungen':
            zeilen += ['| Nr. | Anleitung | Inhalt | Status |', '|---|---|---|---|']
            zeilen += ['| %s | %s | %s | %s |' % (i['nr'], i['titel'], (i['text'] + ''.join(' Plugin: %s (%s).' % (x['id'], STUFE_TXT[x['stufe']]) for x in i.get('plugins', []))).replace('|', '\\|'), STATUS[i['status']]) for i in liste]
        else:
            zeilen += ['| Nr. | Vorschlag | Größe | Beschreibung | Status |', '|---|---|---|---|---|']
            for i in sorted(liste, key=lambda x: x['nr']):
                st = STATUS[i['status']] + (' ([Bauplan](builds/%s/))' % i['bauplan'] if i.get('bauplan') else '')
                plg = ''.join(' Plugin: %s (%s).' % (x['id'], STUFE_TXT[x['stufe']]) for x in i.get('plugins', []))
                zeilen.append('| %s | %s | %s | %s | %s |' % (i['nr'], i['titel'], i.get('groesse', ''), (i['text'] + plg).replace('|', '\\|'), st))
    return '\n'.join(zeilen)


def abhaengigkeiten(daten):
    """Tabelle: Plugin → Baupläne und Ideen, die es benötigen, empfehlen oder optional nutzen."""
    builds = []
    for bid in sorted(os.listdir(os.path.join(ROOT, 'builds'))):
        pfad = os.path.join(ROOT, 'builds', bid, 'build.json')
        if os.path.isfile(pfad):
            with open(pfad, encoding='utf-8') as f:
                builds.append(json.load(f))
    namen = {}
    for pid in os.listdir(os.path.join(ROOT, 'plugins', 'eigene')):
        pfad = os.path.join(ROOT, 'plugins', 'eigene', pid, 'plugin.json')
        if os.path.isfile(pfad):
            with open(pfad, encoding='utf-8') as f:
                namen[pid] = json.load(f)['name'] + ' (eigenes)'
    with open(os.path.join(ROOT, 'plugins', 'fremd', 'plugins.json'), encoding='utf-8') as f:
        for x in json.load(f):
            namen[x['id']] = x['name'] + ' (fremdes)'
    nutzung = {}
    for b in builds:
        for x in b.get('plugins', []):
            nutzung.setdefault(x['id'], []).append((x['stufe'], 'Bauplan %s' % b['titel']))
    for i in daten['ideen']:
        for x in i.get('plugins', []):
            nutzung.setdefault(x['id'], []).append((x['stufe'], 'Idee Nr. %s %s' % (i['nr'], i['titel'])))
    ohne = [b['titel'] for b in builds if not b.get('plugins')]
    z = ['| Plugin | Benötigt von | Empfohlen für | Optional bei |', '|---|---|---|---|']
    for pid in sorted(nutzung, key=lambda k: namen.get(k, k).lower()):
        l = nutzung[pid]
        sp = lambda st: ', '.join(n for s_, n in l if s_ == st) or '–'
        z.append('| %s | %s | %s | %s |' % (namen.get(pid, pid), sp('benoetigt'), sp('empfohlen'), sp('optional')))
    z += ['', 'Ohne Plugin (reines Minecraft): %s.' % (', '.join(ohne) if ohne else 'keiner')]
    return '\n'.join(z)


def ersetze(text, a_mark, e_mark, inhalt):
    if a_mark not in text or e_mark not in text:
        sys.exit('Markierungen %s / %s fehlen im Masterplan' % (a_mark, e_mark))
    a, b = text.index(a_mark) + len(a_mark), text.index(e_mark)
    return text[:a] + '\n' + inhalt + '\n' + text[b:]


def main():
    with open(os.path.join(ROOT, 'ideen', 'ideen.json'), encoding='utf-8') as f:
        daten = json.load(f)
    pfad = os.path.join(ROOT, 'MASTERPLAN.md')
    with open(pfad, encoding='utf-8') as f:
        text = f.read()
    neu = ersetze(text, START, ENDE, tabellen(daten))
    neu = ersetze(neu, A_START, A_ENDE, abhaengigkeiten(daten))
    if '--pruefen' in sys.argv:
        if neu != text:
            print('Hinweis: Masterplan Abschnitt 15 oder 16.6 ist nicht aktuell. Bitte python tools/ideen_masterplan.py ausführen.')
        return
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write(neu)
    print('Masterplan aktualisiert: %d Ideen' % len(daten['ideen']))


if __name__ == '__main__':
    main()
