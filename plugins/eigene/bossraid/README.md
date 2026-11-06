# BossRaid 0.1.0 (Testversion)

Boss-Kämpfe mit Arena, Beschwörung am Altar und Raid-Vorlagen. Bosse machen echten Schaden, man kann sterben, dafür gibt es guten Loot. Idee P1, Konzept im [Masterplan, Abschnitt 17.1](../../../MASTERPLAN.md).

**Stand:** Erste Fassung mit den Bossen Nekromant, Sumpfhexe und Steingolem. Kompiliert und startet auf einem Paper-Testserver ohne Fehler, ist aber noch **nicht im Spiel getestet**. Bitte zuerst in einer Testwelt ausprobieren (Checkliste unten).

- Plattform: Paper 1.21.4 oder neuer, Java 21
- Datei: `BossRaid-0.1.0.jar` aus dem Release `bossraid-v0.1.0` in den Ordner `plugins` legen, Server neu starten

## So richtest du einen Raid ein

1. **Arena:** In die Mitte stellen, `/bossarena erstellen kolosseum`. Der Radius ist fest (30 Blöcke, nur in der `config.yml` änderbar). `/bossarena zeigen kolosseum` lässt den Rand leuchten.
2. **Boss-Spawn und Eingang:** Hinstellen, `/bossarena bossspawn kolosseum` und `/bossarena eingang kolosseum`. Am Eingang stehen alle wieder auf, die sterben.
3. **Raid-Vorlage:** `/raid erstellen golemtag steingolem kolosseum`, dann Regeln einstellen, z. B. `/raid set golemtag tod grabtruhe`, `/raid set golemtag leben 3`. Prüfen mit `/raid info golemtag`.
4. **Altar:** Auf einen Block in der Arena schauen, `/bossarena altar kolosseum golemtag`. Das Plugin stellt vier Kerzen 3 Blöcke schräg um den Altar.
5. **Tor (optional):** Tor geschlossen bauen (z. B. Eisengitter), `/bossarena tor kolosseum`, jeden Tor-Block mit dem Torstab anklicken, `/bossarena tor kolosseum speichern`. Das Tor öffnet sich und schließt sich zu jedem Kampf.

## So läuft ein Kampf

- **Beschwörung (Hauptweg):** Fragmente sammeln, an der Werkbank den Beschwörungsgegenstand herstellen (`/raid rezepte`), mit Rechtsklick auf den Altar legen, die vier Kerzen mit Feuerzeug anzünden. Nach 10 Sekunden Ritual erscheint der Boss. Wer dann in der Arena steht, ist dabei. Die verfluchte Version ruft den Boss auf „schwer“.
- **Admin-Start:** `/raid start golemtag` (60 Sekunden zum Beitreten mit `/raid beitreten`) oder `/raid start golemtag sofort` (alle, die in der Arena stehen).
- **Während des Kampfs:** Tor zu, kein Bauen in der Arena, Boss-Leiste mit Phase und Restzeit. Spezialangriffe werden angekündigt (Partikel, Ton, Chat). Wer sich eintürmt, wird heruntergezogen. Wer die Arena verlässt oder ausloggt, gilt als geflohen und bekommt keinen Loot.
- **Tod:** je nach Raid `normal` (Sachen fallen, 10 Minuten nur für dich aufhebbar), `grabtruhe` (Truhe am Todesort, nur du öffnest sie) oder `behalten` (alles bleibt, halbe Level weg). Danach Neustart am Eingang, der Boss heilt sich um 10 %. Sind alle Leben weg, ist man ausgeschieden.
- **Ende:** Sieg mit Feuerwerk, Rangliste und persönlichem Loot (ab 5 % Schaden). Gescheitert, wenn die Zeit abläuft oder eine Wartezeit lang niemand mehr lebt. Dann verschwindet der Boss.

## Befehle

| Befehl | Wirkung | Wer |
|---|---|---|
| `/raid beitreten` | Einem gestarteten Raid beitreten | Spieler |
| `/raid top <raid>` | Siege, Bestzeit, letzte Rangliste | Spieler |
| `/raid info <raid>` | Alle Regeln eines Raids | Spieler |
| `/raid liste`, `/raid bosse`, `/raid rezepte` | Übersichten | Spieler |
| `/raid erstellen <name> [boss] [arena]` | Raid-Vorlage anlegen | Admin |
| `/raid set <raid> <feld> <wert>` | Regel ändern (siehe unten) | Admin |
| `/raid start <raid> [sofort]` | Raid starten | Admin |
| `/raid stopp [raid\|arena]` | Laufende Raids abbrechen | Admin |
| `/raid gegenstand <id> [anzahl] [verflucht] [spieler]` | Gegenstände geben (zum Testen) | Admin |
| `/raid loeschen <raid>`, `/raid neuladen` | Vorlage löschen, Config neu laden | Admin |
| `/bossarena erstellen\|bossspawn\|eingang <arena>` | Arena einrichten | Admin |
| `/bossarena altar <arena> <raid>` | Altar setzen und verbinden | Admin |
| `/bossarena tor <arena> [speichern\|loeschen]` | Tor markieren | Admin |
| `/bossarena zeigen\|info\|liste\|loeschen` | Arenen ansehen und verwalten | Admin |

**Felder für `/raid set`:** `boss`, `arena`, `stufe` (leicht, normal, schwer), `tod` (normal, grabtruhe, behalten), `leben`, `zeit` (Minuten, Standard 15), `leer` (Sekunden ohne lebende Spieler, Standard 60), `spieler` (z. B. 2-8), `loot` (Faktor, z. B. 1.5), `abklingzeit` (Minuten Pause am Altar, Standard 60), `beschwoerung` (an, aus).

**Rechte:** `bossraid.admin` (Standard: OPs), `bossraid.spieler` (Standard: alle).

## Bosse in dieser Version

| Boss | Stufe | Beschwörung | Besonderheit |
|---|---|---|---|
| Nekromant | I | Seelenkristall (8 Seelensplitter von Skeletten bei Nacht + Knochenblock) | Skelett-Wellen, Teleport hinter Spieler, Seelensturm, heilende Skelette |
| Sumpfhexe | I | Hexenauge (8 Sumpfkräuter von Hexen und Schleimen + fermentiertes Spinnenauge) | weicht aus, Schleime, heilt sich in Ruhe, Kessel zerschlagen, Fluch |
| Steingolem | II | Golemkern (8 Steinsplitter von Silberfischchen und Höhlenspinnen + Eisenblock) | Felswurf, Schockwelle (springen!), Steinhaut |

Alle Werte, Fähigkeiten, Texte und der Loot stehen in `plugins/BossRaid/bosse.yml` und lassen sich ohne Programmieren ändern. Neue Bosse entstehen dort aus dem Fähigkeiten-Baukasten.

## Einstellungen (`config.yml`)

| Einstellung | Standard | Bedeutung |
|---|---|---|
| `arena.radius` | 30 | fester Radius jeder Arena |
| `stufen.*` | 0.6/1.0/1.5 Leben | Faktoren für Leben, Schaden und Loot je Stufe |
| `leben-pro-weiterem-spieler` | 0.4 | +40 % Boss-Leben pro weiterem Spieler |
| `heilung-bei-spielertod` | 0.10 | Boss heilt sich, wenn jemand stirbt |
| `loot.mindest-anteil` | 0.05 | Loot erst ab 5 % Schaden |
| `fragmente.tageslimit` | 8 | Fragmente pro Spieler und Tag |
| `tod.nie-abnehmen` | „Hilfe & Befehle“ | wird bei keiner Todesregel abgenommen |
| `ignorierte-spieler` | leer | z. B. Namen der Farm-Bots |

## Zusammenspiel mit dem Server

- **Inventar behalten** ist auf dem Server an. In der Arena gilt während eines Raids die Todesregel des Raids, überall sonst bleibt alles wie gewohnt.
- **Zuschauermodus** ist gesperrt. Wer ausgeschieden ist, steht deshalb normal wieder auf (Bett oder Spawn) und kommt bis zum Ende nicht mehr in die Arena.
- **Farm-Bots** zählen nie als Teilnehmer, wenn ihr Name unter `ignorierte-spieler` steht.
- **EasyCommandBlocker:** `/raid` für alle Spieler freigeben, damit `/raid beitreten` und `/raid rezepte` in der Tab-Liste erscheinen.

## Test-Checkliste (Testwelt)

- [ ] Server startet, in der Konsole steht „BossRaid bereit“
- [ ] Arena, Boss-Spawn, Eingang, Raid und Altar einrichten, `/raid info` zeigt alles
- [ ] `/raid gegenstand seelenkristall`, auf den Altar legen, Kerzen anzünden: Ritual und Auftritt
- [ ] Nekromant: Pfeil-Salve, Skelette, Teleport (Phase 2), Seelensturm (Phase 3)
- [ ] Sumpfhexe: weicht aus, Schleime, Heilkreis, Kessel zerschlagen, Fluch
- [ ] Steingolem: greift Spieler an, Felswurf, Schockwelle (Springen schützt), Steinhaut
- [ ] Sterben mit jeder Todesregel, Wiederbeleben am Eingang, Ausscheiden nach dem letzten Leben
- [ ] Arena verlassen = geflohen, Ausloggen = geflohen
- [ ] Zeit ablaufen lassen (`/raid set <raid> zeit 1`): Boss verschwindet, gescheitert
- [ ] Alle sterben, Wartezeit läuft ab: gescheitert
- [ ] Sieg: Feuerwerk, Rangliste, Loot, `/raid top`
- [ ] Bedrock-Spieler: Boss-Leiste, Titel und Größe der Bosse sichtbar
- [ ] Server während eines Kampfs neu starten: kein Boss bleibt übrig, Tor offen

## Änderungen

**0.1.0** (06.11.2026): Erste Fassung. Arenen, Raid-Vorlagen, Beschwörung am Altar, Admin-Start, drei Phasen, Fähigkeiten-Baukasten, Zeitlimit und Scheitern, Todesregeln, Grabtruhen, persönlicher Loot, Nekromant, Sumpfhexe, Steingolem.
