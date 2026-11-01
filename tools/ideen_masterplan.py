"""Schreibt die Ideenliste aus ideen/ideen.json in den Masterplan (Abschnitt 15).

Aufruf nach jeder Änderung an ideen/ideen.json:
    python tools/ideen_masterplan.py
Mit --pruefen wird nur geprüft, ob der Masterplan aktuell ist (wird von build_site.py genutzt).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, ENDE = '<!-- ideen:start -->', '<!-- ideen:ende -->'
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
            zeilen += ['| %s | %s | %s | %s |' % (i['nr'], i['titel'], i['text'].replace('|', '\\|'), STATUS[i['status']]) for i in liste]
        else:
            zeilen += ['| Nr. | Vorschlag | Größe | Beschreibung | Status |', '|---|---|---|---|---|']
            for i in sorted(liste, key=lambda x: x['nr']):
                st = STATUS[i['status']] + (' ([Bauplan](builds/%s/))' % i['bauplan'] if i.get('bauplan') else '')
                zeilen.append('| %s | %s | %s | %s | %s |' % (i['nr'], i['titel'], i.get('groesse', ''), i['text'].replace('|', '\\|'), st))
    return '\n'.join(zeilen)


def main():
    with open(os.path.join(ROOT, 'ideen', 'ideen.json'), encoding='utf-8') as f:
        daten = json.load(f)
    pfad = os.path.join(ROOT, 'MASTERPLAN.md')
    with open(pfad, encoding='utf-8') as f:
        text = f.read()
    if START not in text or ENDE not in text:
        sys.exit('Markierungen %s / %s fehlen im Masterplan' % (START, ENDE))
    a, b = text.index(START) + len(START), text.index(ENDE)
    neu = text[:a] + '\n' + tabellen(daten) + '\n' + text[b:]
    if '--pruefen' in sys.argv:
        if neu != text:
            print('Hinweis: Masterplan Abschnitt 15 ist nicht aktuell. Bitte python tools/ideen_masterplan.py ausführen.')
        return
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write(neu)
    print('Masterplan aktualisiert: %d Ideen' % len(daten['ideen']))


if __name__ == '__main__':
    main()
