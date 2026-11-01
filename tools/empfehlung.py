"""Regel für „Als Nächstes“ auf der Geplant-Seite (Masterplan Abschnitt 15).

Es stehen immer ANZAHL offene Bauplan-Ideen unter „Als Nächstes“ (Feld "empfohlen": true).
Ist eine davon fertig (status "verfuegbar"), rückt per Zufall eine andere offene Bauplan-Idee nach.
Anleitungen (Kategorie "anleitungen") werden dabei nicht gezogen.
"""
import random

ANZAHL = 3

NACHRUECKEN = {
    'de': 'Ist eine davon fertig, rückt per Zufall eine neue nach.',
    'en': 'When one of them is finished, a new one moves up at random.',
}
ALLGEMEIN = {
    'de': 'Diese Ideen kommen als Nächstes dran. ' + NACHRUECKEN['de'],
    'en': 'These ideas come next. ' + NACHRUECKEN['en'],
}


def offen(i):
    return i['status'] != 'verfuegbar'


def nachruecken(daten, zufall=None):
    """Füllt „Als Nächstes“ auf ANZAHL auf. Gibt die neu gezogenen Ideen zurück."""
    zufall = zufall or random.Random()
    ideen = daten['ideen']
    aktuell = [i for i in ideen if offen(i) and i.get('empfohlen')]
    kandidaten = sorted((i for i in ideen if offen(i) and not i.get('empfohlen') and i['kategorie'] != 'anleitungen'),
                        key=lambda i: str(i['nr']))
    neu = []
    while len(aktuell) + len(neu) < ANZAHL and kandidaten:
        wahl = kandidaten.pop(zufall.randrange(len(kandidaten)))
        wahl['empfohlen'] = True
        neu.append(wahl)
    return neu


def text(daten, lang):
    """Eigener Text, solange alle Ideen, auf die er sich bezieht, noch unter „Als Nächstes“ stehen; sonst der allgemeine."""
    nrs = {i['nr'] for i in daten['ideen'] if offen(i) and i.get('empfohlen')}
    eigen = daten.get('empfohlen_text') or {}
    if eigen.get(lang) and set(eigen.get('fuer', [])) <= nrs and eigen.get('fuer'):
        return eigen[lang] + ' ' + NACHRUECKEN[lang]
    return ALLGEMEIN[lang]
