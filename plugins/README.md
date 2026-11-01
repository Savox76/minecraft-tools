# Plugins

Getrennt nach **eigenen Plugins** (von Savox entwickelt) und **fremden Plugins**, die es schon gibt und die auf dem Server laufen oder empfohlen werden.

## Eigene Plugins (`eigene/`)

Jeder Ordner enthält:

- `plugin.json`: Daten für die Website (Version, Funktionen, Befehle, Einstellungen, Änderungen)
- `README.md`: dieselben Infos zum Lesen auf GitHub

| Plugin | Version | Kurz |
|---|---|---|
| [AdminLogin](eigene/adminlogin/) | 1.2.0 | Admin-Passwort beim Betreten, SuperOP, Sperre nach Fehlversuchen |
| [Arbeiter](eigene/arbeiter/) | 2.0.1 | Dorfbewohner-Arbeiter mit 11 Berufen und Händlern |
| [InfiniteLager](eigene/infinitelager/) | 3.2.0 | Gemeinsames und privates Lager mit Einlagern-Truhen |
| [ProvokedMobs](eigene/provokedmobs/) | 1.2.0 | Creeper-Schutz, umschaltbar |
| [ServerEinstellungen](eigene/servereinstellungen/) | 1.2.0 | Server-Einstellungen per Chatbefehl, SuperOP-Rechte |
| [ServerHilfe](eigene/serverhilfe/) | 1.0.0 | Hilfe-Buch und `/hilfe`-Menü |
| [ServerShop](eigene/servershop/) | 1.4.0 | Coin-Shop, Spieler-Shops, Tageslimits |

**Status:** Die Dokumentation ist vollständig. Quellcode und `.jar`-Downloads folgen (siehe [Masterplan](../MASTERPLAN.md), Phase 4). Der Quellcode kommt pro Plugin nach `src/` mit eigenem Gradle-Build. Fertige `.jar`-Dateien werden nicht ins Repo gelegt, sondern von GitHub Actions gebaut und an ein Release gehängt.

## Fremde Plugins (`fremd/plugins.json`)

Plugins anderer Entwickler. Hier liegen nur Beschreibung, Einsatz auf dem Server und Link zur offiziellen Download-Seite, keine Dateien.

| Feld | Bedeutung |
|---|---|
| `name`, `autor` | Name und Entwickler |
| `zweck` | wofür es da ist |
| `einsatz` | wie es auf dem Server eingestellt ist (optional) |
| `link` | offizielle Download-Seite (optional) |
| `anleitung` | ID einer Anleitung in `docs/` (optional) |
| `status` | `im-einsatz` oder `empfohlen` |

Die Liste ist vorläufig, aus den Server-Notizen übernommen, und wird mit der vollständigen Plugin-Liste ergänzt.
