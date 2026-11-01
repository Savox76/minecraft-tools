# ServerEinstellungen 1.2.0

Die wichtigsten Server-Einstellungen per Chatbefehl, mit SuperOP-Rechten.

Admins ändern die wichtigsten Server-Einstellungen im Chat. Jede Änderung wird sofort gespeichert und gilt auch nach einem Neustart. Bestimmte Einstellungen, etwa Kreativ- und Zuschauermodus, darf nur der SuperOP ändern.

> Status: Dokumentation verfügbar. Quellcode und `.jar`-Download folgen.

## Funktionen

- Einstellungen: kreativ, zuschauer, abenteuer, schwierigkeit, pvp, inventar-behalten, feuer-ausbreitung, explosions-schaden, mob-griefing, monster-spawnen, phantome, wetterwechsel, zeit, reichweite, ein-spieler-schlaf, nether, end
- Kreativ- und Zuschauermodus ab Start gesperrt, auch für Admins; nur der SuperOP schaltet frei
- Reichweite 2 bis 16 Chunks um Spieler und Farm-Bots, in denen Farmen laufen
- Ein schlafender Spieler beendet die Nacht (wichtig, weil Farm-Bots nie schlafen)
- Änderungen werden im Chat angekündigt (abschaltbar)

## Befehle

| Befehl | Was er macht | Wer |
|---|---|---|
| `/einstellungen` | Alle Einstellungen anzeigen | Admin |
| `/einstellungen <name>` | Erklärung und aktueller Wert | Admin |
| `/einstellungen <name> <wert>` | Einstellung ändern, z. B. /einstellungen zeit tag | Admin |
| `/einstellungen neu-laden` | Nach Änderungen direkt in der config.yml | Admin |
| `/einstellungen superop liste` | SuperOPs anzeigen | Admin |
| `einstellungen superop hinzufuegen \| entfernen <Name>` | SuperOP verwalten | Konsole |

## Einstellungen (`config.yml`)

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `nur-superop` | `Liste` | Welche Einstellungen nur der SuperOP ändern darf |

## Änderungen

### 1.2.0 (18.10.2026)

- SuperOP-Rechte
- Reichweite für Farmen und Farm-Bots
- Ein-Spieler-Schlaf
