# Plugins

Getrennt nach **eigenen Plugins** (von Savox entwickelt) und **fremden Plugins**, die es schon gibt und die auf dem Server laufen oder empfohlen werden.

## Eigene Plugins (`eigene/`)

Jeder Ordner enthält:

- `plugin.json`: Daten für die Website (Version, Funktionen, Befehle, Einstellungen, Änderungen)
- `README.md`: dieselben Infos zum Lesen auf GitHub

Englische Texte stehen in `plugin.json` unter `"en"`: `kurz`, `beschreibung`, `funktionen`, `status_text` sowie `befehle`, `config` und `changelog` als Listen in derselben Reihenfolge wie auf Deutsch.

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

**Bauen und veröffentlichen** (`.github/workflows/plugins.yml`): Jede Änderung am Quellcode wird gebaut und auf einem Paper-Testserver gestartet. Ein Release mit der `.jar` entsteht über *Actions → Plugins → Run workflow* mit der Plugin-ID (z. B. `bossraid`) oder über einen Tag `<id>-v<version>`.

**In Arbeit:** [BossRaid](eigene/bossraid/) 0.1.0 (Testversion, Idee P1): Boss-Kämpfe mit Arena, Beschwörung und Raids. Erscheint auf der Website unter „Plugins → In Planung“, bis es im Spiel getestet ist.

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
| `en` | englische Fassung von `zweck` und `einsatz` |

Die Liste ist vorläufig, aus den Server-Notizen übernommen, und wird mit der vollständigen Plugin-Liste ergänzt.
