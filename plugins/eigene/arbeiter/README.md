# Arbeiter 2.0.1

Dorfbewohner arbeiten für dich: 11 Berufe, bezahlt mit Coins.

Kaufbare Dorfbewohner, die für ihren Besitzer arbeiten: ernten, Holz fällen, graben, angeln, schmelzen und mehr. Jeder Spieler darf 25 Arbeiter haben. Arbeiter nutzen nur, was ihrem Besitzer gehört, und sind unverwundbar.

> Status: Dokumentation verfügbar. Quellcode und `.jar`-Download folgen.

## Funktionen

- 11 Berufe plus kostenlose Dorfbewohner ohne Beruf (Preise in Coins): Bauer 500, Holzfäller 750, Bergarbeiter 1000, Gräber 400, Wächter 600, Hirte 600, Fischer 400, Sammler 300, Schmelzer 500, Imker 400, Lichtwart 200
- Menü per Rechtsklick: Pause, Truhe festlegen, Lieferung ins private Lager, Arbeitsbereich ändern und anzeigen, Arbeitsplatz verlegen, Beruf wechseln, entlassen (50 % zurück)
- Faire Regeln: nur eigene Felder, Öfen, Bienenstöcke und Truhen; fremde Bäume, Tiere mit Namen, zahme oder angeleinte Tiere sind tabu
- Arbeitsbereiche verschiedener Spieler überschneiden sich nicht; mindestens 32 Blöcke Abstand zu fremden Homes; Sperrzonen einstellbar (z. B. Spawn)
- Holzfäller pflanzt 2×2-Bäume wieder als 2×2 nach (Dunkle Eiche, Blasse Eiche, Riesen-Fichte, großer Tropenbaum)
- Händler für Admins: öffnen den Shop für eine Kategorie
- Arbeiter arbeiten nur in geladenen Chunks (Spieler, Farm-Bot oder Chunk-Loader in der Nähe)

## Befehle

| Befehl | Was er macht | Wer |
|---|---|---|
| `/arbeiter preise` | Alle Berufe, Preise und Bereiche | Spieler |
| `/arbeiter kaufen <beruf>` | Arbeiter kaufen: ohne \| bauer \| holzfaeller \| bergarbeiter \| graeber \| waechter \| hirte \| fischer \| sammler \| schmelzer \| imker \| lichtwart | Spieler |
| `/arbeiter liste` | Eigene Arbeiter und was sie gerade tun | Spieler |
| `/arbeiter menue <Nr>` | Menü öffnen (oder Arbeiter rechtsklicken) | Spieler |
| `/arbeiter ersetzen <Nr>` | Verschwundenen Arbeiter ersetzen | Spieler |
| `/arbeiter admin liste \| entfernen <Nr> \| reload` | Verwaltung | Admin |
| `/arbeiter admin haendler <all\|wood\|stone\|ores\|tiere\|resources\|entfernen>` | Händler aufstellen oder entfernen | Admin |

## Einstellungen (`config.yml`)

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `arbeitsbereich.sperrzonen` | `- "world,0,0,100"` | Bereiche, in denen keine Arbeiter arbeiten (Welt, X, Z, Radius) |

## Änderungen

### 2.0.1 (31.10.2026)

- Holzfäller pflanzt 2×2-Bäume als 2×2 nach

### 2.0.0 (18.10.2026)

- Erste Version mit 11 Berufen, Menü, Händlern und fairen Regeln
