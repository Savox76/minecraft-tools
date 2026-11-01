# InfiniteLager 3.2.0

Unbegrenztes gemeinsames und privates Lager mit Einlagern-Truhen.

Ein unbegrenztes Lager per Befehl: ein gemeinsames Lager für alle und ein privates Lager pro Spieler. Einlagern-Truhen leeren sich automatisch ins Lager.

> Status: Dokumentation verfügbar. Quellcode und `.jar`-Download folgen.

## Funktionen

- Gemeinsames Lager für alle Spieler
- Privates Lager pro Spieler, auf das niemand sonst zugreifen kann
- Einlagern-Truhen (gemeinsam oder privat), werden alle 5 Sekunden automatisch geleert
- Private Einlagern-Truhen kann nur der Besitzer öffnen oder abbauen
- Suche im Lager
- Protokoll: wer was aus dem gemeinsamen Lager genommen hat

## Befehle

| Befehl | Was er macht | Wer |
|---|---|---|
| `/lager` | Gemeinsames Lager öffnen | Spieler |
| `/lager in` | Ins gemeinsame Lager einlagern | Spieler |
| `/lager privat` | Privates Lager öffnen | Spieler |
| `/lager privat in` | Ins private Lager einlagern | Spieler |
| `/lager truhe` | Truhe in der Hand wird zur Einlagern-Truhe (gemeinsam) | Spieler |
| `/lager privat truhe` | Truhe in der Hand wird zur Einlagern-Truhe (privat) | Spieler |
| `/lager suche <item>` | Im Lager suchen (auch /lager privat suche <item>) | Spieler |
| `/lager protokoll` | Letzte Entnahmen aus dem gemeinsamen Lager | Spieler |

## Änderungen

### 3.2.0 (18.10.2026)

- Privates Lager pro Spieler
- Private Einlagern-Truhen
- Automatisches Leeren alle 5 Sekunden
- Protokoll für das gemeinsame Lager
