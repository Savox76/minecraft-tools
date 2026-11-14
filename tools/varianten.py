"""Ausbau-Versionen von Bauplänen (Masterplan Abschnitt 4.2).

Eine Ausbau-Version liegt in builds/<id>/ausbau/ mit eigener build.json und model.json. Die Grundversion bleibt
unverändert. Die build.json der Ausbau-Version enthält nur, was sich ändert; alles andere (Kategorie, Tags,
Edition, Plugins ...) kommt aus der Grundversion.

Zusätzlich entsteht die Fassung „Umbau“: Wer die Grundversion schon gebaut hat, baut zuerst ab, was sich ändert
(von oben nach unten), und setzt dann nur die neuen Blöcke (von unten nach oben). Dafür legt umbau() beide
Modelle übereinander (gleicher Ursprung, Ecke Nordwest unten).
"""
import copy
import math

VARIANTEN = ('ausbau',)
TITEL = {'ausbau': ('Ausbau-Version', 'Extended version'), 'umbau': ('Umbau von der Grundversion', 'Rebuild from the base version')}


def zusammen(basis, var):
    """Variante = Grundversion + Abweichungen. 'en' wird feldweise ergänzt."""
    neu = {k: v for k, v in basis.items() if k not in ('model', 'schritte', 'teileliste', 'downloads', 'varianten')}
    for k, v in var.items():
        if k == 'en':
            neu['en'] = {**basis.get('en', {}), **v}
        else:
            neu[k] = v
    return neu


def spec(p):
    return p.get('block') or p['name']


def _gitter(model):
    idx = {p['key']: i for i, p in enumerate(model['palette'])}
    g = {}
    for y, ebene in enumerate(model['layers']):
        for z, reihe in enumerate(ebene):
            for x, ch in enumerate(reihe):
                if ch != '.':
                    g[(x, y, z)] = idx[ch]
    return g


def auffuellen(model, X, Y, Z):
    """Modell auf X × Y × Z vergrößern (leere Zellen dazu), Ursprung bleibt."""
    m = copy.deepcopy(model)
    lay = [[r.ljust(X, '.') for r in e] + ['.' * X] * (Z - len(e)) for e in m['layers']]
    lay += [['.' * X] * Z for _ in range(Y - len(lay))]
    m['layers'], m['size'] = lay, {'x': X, 'y': Y, 'z': Z}
    return m


def _schluessel():
    n = 0
    while True:
        c = chr(0xC0 + n)
        n += 1
        if c not in '×÷':
            yield c


def umbau(basis_model, aus_model):
    """Liefert (neu_model, vorher_model, weg_zellen).

    neu_model:    Ausbau-Modell, Blöcke die schon so in der Grundversion stehen sind als 'vorhanden' markiert
    vorher_model: Grundversion, auf dieselbe Größe gebracht
    weg_zellen:   [(x, y, z, palettenindex in vorher_model)] was abgebaut werden muss
    """
    X = max(basis_model['size']['x'], aus_model['size']['x'])
    Y = max(basis_model['size']['y'], aus_model['size']['y'])
    Z = max(basis_model['size']['z'], aus_model['size']['z'])
    vor = auffuellen(basis_model, X, Y, Z)
    neu = auffuellen(aus_model, X, Y, Z)
    gv, gn = _gitter(vor), _gitter(neu)
    pv, pn = vor['palette'], neu['palette']
    kontext = lambda p: bool(set(p.get('flags', [])) & {'vorhanden', 'kein-block'})

    # Paletten-Einträge für „steht schon da“
    keys = _schluessel()
    benutzt = {p['key'] for p in pn}
    bleibt = {}

    def bleibt_key(i):
        if i not in bleibt:
            k = next(keys)
            while k in benutzt:
                k = next(keys)
            q = dict(pn[i], key=k, flags=sorted(set(pn[i].get('flags', [])) | {'vorhanden'}))
            pn.append(q)
            bleibt[i] = k
        return bleibt[i]

    zeilen = [[list(r) for r in e] for e in neu['layers']]
    weg = []
    for pos in set(gv) | set(gn):
        x, y, z = pos
        iv, i_n = gv.get(pos), gn.get(pos)
        gleich = iv is not None and i_n is not None and spec(pv[iv]) == spec(pn[i_n])
        if gleich:
            if not kontext(pn[i_n]):
                zeilen[y][z][x] = bleibt_key(i_n)
            continue
        if iv is not None and not kontext(pv[iv]):
            weg.append((x, y, z, iv))
    neu['layers'] = [[''.join(r) for r in e] for e in zeilen]
    return neu, vor, weg


def weg_schritte(weg, abschnitt=0):
    """Abbau von oben nach unten, eine ganze Ebene pro Schritt."""
    pro = {}
    for c in weg:
        pro.setdefault(c[1], []).append(c)
    return [{'a': abschnitt, 'y': [y, y], 'weg': True,
             'c': [v for z in sorted(pro[y], key=lambda c: (c[2], c[0])) for v in z]}
            for y in sorted(pro, reverse=True)]


RUECKBAU = {
    'de': {'name': 'Rückbau', 'text': 'Zuerst baust du ab, was sich ändert: die rot umrandeten Blöcke, von oben nach unten. '
                                      'Alles, was bleibt, ist normal zu sehen. Danach folgen nur noch die neuen Blöcke.'},
    'en': {'name': 'Taking down', 'text': 'First take down what changes: the blocks outlined in red, from the top down. '
                                          'Everything that stays is shown normally. After that come only the new blocks.'},
}
