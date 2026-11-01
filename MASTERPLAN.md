# Masterplan: minecraft-tools

Name: **Bauwerkstatt** (Zusatz: „Baupläne und Plugins für Minecraft“). „Minecraft“ darf nach den Minecraft-Nutzungsrichtlinien nicht der Hauptname sein, nur ein Zusatz. Eine Sammlung von Minecraft-Bauanleitungen und Server-Plugins für Kreative, kostenlos und einzeln herunterladbar.

Stand: 01.11.2026 · Website: <https://savox76.github.io/minecraft-tools/>

---

## 0. Aktueller Stand

| Bereich | Status | Wo |
|---|---|---|
| 8 Baupläne | ✅ **verfügbar** als Entwurf: Bauschritte, Teileliste, `.litematic`, `.schem`, CSV | [`builds/`](builds/) |
| 7 eigene Plugins | 🟡 **Doku verfügbar**, Quellcode und `.jar` integrierbar, sobald der Quellcode vorliegt | [`plugins/eigene/`](plugins/eigene/) |
| Fremde Plugins | 🟡 **vorläufige Liste** (7) aus den Server-Notizen, wird mit der vollständigen Liste ergänzt | [`plugins/fremd/plugins.json`](plugins/fremd/plugins.json) |
| 2 Anleitungen | ✅ verfügbar (Farm-Bot, CoreProtect) | [`docs/`](docs/) |
| Website | ✅ automatisch per GitHub Actions auf GitHub Pages, **Deutsch und Englisch**, Hell/Dunkel/Automatisch, suchmaschinenfreundlich (siehe 14.) | [`site/`](site/), [`tools/build_site.py`](tools/build_site.py), [`tools/seiten.py`](tools/seiten.py) |
| Geplant | 💡 150 Ideen für Baupläne und 14 für Anleitungen, mit Kurztext, auf der Website unter „Geplant“ | [`ideen/ideen.json`](ideen/ideen.json), Abschnitt 15 |
| Abhängigkeiten | ✅ Werkzeuge, Dienste, Spiel, Server und Plugins, teils automatisch erzeugt | Abschnitt 16 |
| Bauwünsche | ✅ Issue-Formulare, Wunschliste täglich auf der Website | [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) |

**Entwurf** heißt: Die Richtung von Treppen, Türen und Trichtern ist in den Dateien noch nicht in einer Testwelt geprüft (siehe Phase 1).

### Feste Regeln

- **Jeder neue Bauplan kommt ins Repo** als Ordner `builds/<id>/` (Format in [`builds/README.md`](builds/README.md)). Website, Bauschritte, Teileliste und Downloads entstehen daraus automatisch. Er erscheint also überall, ohne dass sonst etwas angepasst werden muss.
- **Eigene und fremde Plugins bleiben getrennt.** Eigene Plugins bekommen `plugins/eigene/<id>/plugin.json` und `README.md`, fremde einen Eintrag in `plugins/fremd/plugins.json` (nur Beschreibung, Einsatz und Link zur offiziellen Seite, keine Dateien). Die Website zeigt beides automatisch in getrennten Bereichen.
- **Änderungen gehen direkt auf `main`.**
- **Alles zweisprachig:** Neue Baupläne, Plugins und Anleitungen bekommen eine englische Fassung (`"en"` in `build.json` und `plugin.json`, `docs/en/<id>.md`, neue Blocknamen in `tools/i18n/bloecke_en.json`). Fehlt sie, zeigt die englische Seite den deutschen Text und der Build gibt einen Hinweis aus.
- **Abhängigkeiten aktuell halten:** Kommt ein Werkzeug, Dienst oder Plugin dazu oder ändert sich eine Version, wird Abschnitt 16 angepasst. Welche Baupläne und Ideen welche Plugins brauchen, erzeugt `python tools/ideen_masterplan.py`.
- **Keine Links zum Quellcode auf der Website:** Die Website verlinkt nicht auf das GitHub-Repo, den Quellcode der Seite, der Plugins oder der Baupläne. Downloads (`.litematic`, `.schem`, CSV, später `.jar`) liegen direkt auf der Website. Ausnahme bisher: die Wunsch-Formulare (GitHub-Issues).
- **Kein Bezug zu LEGO:** LEGO ist die Marke eines anderen Unternehmens. Auf der Website und im Repo heißt es Bauschritte, Bauheft und Schritt-für-Schritt-Anleitung.
- **Keine erzeugten Dateien im Repo:** Website, `.litematic`, `.schem`, `.jar` und PDFs baut GitHub Actions bei jedem Push neu.

---

## 1. Ziel

- **Alle Baupläne** (Türme, Villen, Farmen, Technik) als **Schritt-für-Schritt-Anleitungen**: Zu jedem Schritt ist sofort klar, welche Blöcke in welcher Menge gebraucht werden.
- **Alle eigenen Plugins** mit Quellcode, Doku und Download.
- **Jeder Bauplan und jedes Plugin einzeln** verfügbar, ohne Gesamtpaket.
- **Gleiche Oberfläche** auf Windows, Linux und macOS.
- **Wünsche für neue Anleitungen** einreichen und abstimmen.

## 2. Empfehlung in Kürze

**Eine Codebasis, drei Ausgaben:**

| Ausgabe | Wofür | Kosten |
|---|---|---|
| **Website auf GitHub Pages** | Hauptweg. Läuft in jedem Browser auf jedem System, kein Installieren | kostenlos |
| **Offline-App (PWA)** | Dieselbe Website lässt sich mit einem Klick „installieren“ und läuft dann ohne Internet | kostenlos |
| **Desktop-App (Tauri)** | Gleiche Oberfläche plus Funktionen, die eine Website nicht kann: Baupläne direkt in den Minecraft-Ordner kopieren, Plugins mit Backup in einen Server installieren | kostenlos, Installer werden automatisch für alle 3 Systeme gebaut |

**Kann das dauerhaft auf GitHub Pages bleiben? Ja.** Das Repo ist öffentlich, und die Seite ist rein statisch, braucht also keinen eigenen Server. Die Grenzen von GitHub Pages liegen bei 1 GB Seitengröße und etwa 100 GB Datenverkehr pro Monat. Für Baupläne und Plugin-Dateien reicht das weit. Nicht erlaubt ist nur Pages als Hosting für einen Shop oder ein Geschäft. Eine kostenlose Sammlung ist in Ordnung.

**Reihenfolge:** Erst die Website mit Offline-Funktion, denn sie deckt Windows, Linux und macOS schon vollständig ab. Die Desktop-App kommt danach, sobald die lokalen Zusatzfunktionen gebraucht werden.

---

## 3. Was hinein soll (Bestand)

### Baupläne (8)

| ID | Name | Größe | Höhe | Blöcke ca. |
|---|---|---|---|---|
| `eiffelturm` | Eiffelturm (1:3) | 43 × 43 | 112 | 7.600 |
| `leuchtturm` | Leuchtturm | Ø 17 | 65 | 2.600 |
| `villa-am-wasser` | Villa am Wasser mit Pool und Wasser-Aufzug | 27 × 27 | 15 | 2.700 |
| `villa-modern` | Moderne Villa | 29 × 23 | 12 | 2.000 |
| `villa-mediterran` | Mediterrane Villa | 27 × 27 | 16 | 3.750 |
| `villa-gruenderzeit` | Gründerzeit-Villa mit Turm | 21 × 15 + Turm | 38 | 2.750 |
| `gewaechshaus-farm` | Gewächshaus mit Dorfbewohner-Farm | 15 × 15 | 14 | 870 |
| `kellerlager` | Kellerlager mit Sortieranlage (Java) | 17 × 12 | 8 | 800 |

Quelle: die bisherige Bauplan-Seite (Claude-Artifact „Spawn-Baupläne“).

### Eigene Plugins (7, Paper)

| Plugin | Version | Kurz |
|---|---|---|
| AdminLogin | 1.2.0 | Admin-Passwort beim Betreten, SuperOP, Sperre nach Fehlversuchen |
| ServerShop | 1.4.0 | Coin-Shop, Spieler-Shops, Tageslimits |
| InfiniteLager | 3.2.0 | gemeinsames und privates Lager, Einlagern-Truhen, Protokoll |
| ProvokedMobs | 1.2.0 | Creeper-Schutz, umschaltbar |
| Arbeiter | 2.0.1 | Dorfbewohner-Arbeiter mit 11 Berufen, Händler |
| ServerEinstellungen | 1.2.0 | Server-Einstellungen per Chatbefehl, SuperOP-Rechte |
| ServerHilfe | 1.0.0 | Hilfe-Buch und `/hilfe`-Menü |

Quelle: der Ordner „Quellcode“ aus dem Server-Update-Paket.

### Fremde Plugins (vorläufig)

FakePlayerPlugin, ChunkLoader, EasyCommandBlocker, Simple Voice Chat, Floodgate, spark (im Einsatz) und CoreProtect (empfohlen). Die vollständige Liste folgt.

### Anleitungen ohne Bauplan

- Farm-Bot mit FakePlayerPlugin (Paper)
- Spieler-Aktionen protokollieren mit CoreProtect

---

## 4. Das Bauheft-Prinzip

So sieht eine Bauanleitung aus:

1. **Deckblatt:** Bild des fertigen Bauwerks, Name, Größe, Schwierigkeit, Bauzeit, Java/Bedrock.
2. **Gesamt-Teileliste:** alle Blöcke mit Bild und Anzahl, zusätzlich in Stacks (z. B. „12 St. + 30“). Darunter die Rohstoffe aus Farmen, zum Beispiel „1.050 Sand = Glas und Beton“.
3. **Bauschritte, nummeriert, einer pro Seite:** siehe den festen Ablauf in 4.1
4. **Unterbaugruppen** wie in einem Bauheft: Teile, die mehrfach vorkommen (Palme, Fenster-Modul, Laternenpfahl), werden einmal gezeigt und mit **„2 ×“** markiert.
5. **Schritt-Regeln:** Ebene für Ebene, höchstens 60 neue Blöcke pro Schritt (Einzelheiten in 4.1). Die Schritte entstehen automatisch.
6. **Ausgaben pro Bauplan:**
   - Web-Ansicht zum Durchblättern, auf dem Handy wischbar
   - druckbares **PDF-Heft** im selben Look
   - Teileliste als **CSV**
   - Bauplan-Dateien zum direkten Einfügen ins Spiel (siehe 6.)
7. **Baufortschritt:** Erledigte Schritte lassen sich abhaken. Der Stand wird im Browser gespeichert.

### 4.1 Fester Ablauf jedes Bauplans (gilt auch für alle neuen)

Jeder Bauplan wird **Ebene für Ebene von unten nach oben** gebaut. Dieser Ablauf entsteht automatisch aus `model.json` (`tools/build_site.py`, Funktion `bau_schritte`); für einen neuen Bauplan muss dafür nichts von Hand eingestellt werden.

**So werden die Schritte gebildet**

1. **Ein Schritt gehört immer zu genau einer Ebene.** Es werden nie mehrere Ebenen in einem Schritt zusammengefasst, auch wenn eine Ebene nur wenige Blöcke hat.
2. **Höchstens 60 neue Blöcke pro Schritt.** Hat eine Ebene mehr, wird sie in gleich große Teile zerlegt: „Ebene 1 · Teil 3 von 5“. Die Teile folgen Kacheln von 8 × 8 Blöcken in Schlangenlinie, damit man im Spiel nicht kreuz und quer laufen muss.
3. **Zweite Teile gehören zum ersten:** Die obere Türhälfte und das Kopfteil vom Bett erscheinen im selben Schritt wie der untere Teil, weil Minecraft sie automatisch mitsetzt. Sie zählen nicht in der Teileliste.
4. **Gelände** (`vorhanden`) wird nie als Schritt gezeigt, sondern blass als Umgebung.
5. **Bauabschnitte** (`abschnitte` in `build.json`) teilen die Ebenen in sinnvolle Bereiche („Fundament“, „Erdgeschoss & Pool“). Jeder Schritt zeigt seinen Abschnitt mit Beschreibung.

**Das sieht man in jedem Schritt**

| Bereich | Inhalt |
|---|---|
| Schrittnummer | groß oben links, „13 von 52“ |
| 3D-Ansicht | neue Blöcke gelb umrandet, gebaute blass, spätere ausgeblendet. **Drehbar** in vier Richtungen (Südost, Nordost, Nordwest, Südwest): Knöpfe ⟲ ⟳, Ziehen mit der Maus, Wischen auf dem Handy oder Tasten Q und E. ◎ zeigt das ganze Bauwerk |
| Draufsicht der Ebene | Raster der aktuellen Ebene, Norden oben, Koordinaten ab der Mitte. Neue Blöcke gelb umrandet, schon gebaute blass, die Ebene darunter als Schatten. Antippen zeigt Block, Position und Minecraft-ID |
| Plugins | Oben auf der Bauplan-Seite: „Kein Plugin nötig“ oder jedes Plugin mit Stufe (benötigt, empfohlen, optional), Grund und Link. Karten zeigen „Plugin nötig“, Plugin-Seiten listen umgekehrt alle Baupläne und Ideen, die sie verwenden |
| Neue Teile | Kasten wie in einem Bauheft: Block-Bild, „× 12“, Name |
| Abschnitt | „Ebene 1 · Teil 3 von 5“, Name und Text des Bauabschnitts |
| Steuerung | Zurück/Weiter, Schieberegler, Pfeiltasten, „Schritt erledigt“ mit Fortschrittsbalken (im Browser gespeichert) |

Dazu gibt es pro Bauplan die Reiter **Teileliste** (gesamt, mit Stacks und Rohstoffen), **Ebenen** (jede Ebene einzeln als Draufsicht) und **Downloads** (`.litematic`, `.schem`, CSV).

**Checkliste für einen neuen Bauplan**

- [ ] `builds/<id>/model.json`: Ebene 0 ist der Boden, jede weitere Ebene liegt genau einen Block höher. Gelände mit `vorhanden` markieren, obere Türhälften und Bett-Kopfteile mit `zweiter-teil`.
- [ ] `builds/<id>/build.json`: `abschnitte` mit `von`/`bis` passend zu den Ebenen, dazu Tipps, Rohstoffe und die englische Fassung unter `en`.
- [ ] `plugins` in `build.json` eintragen: welches Plugin benötigt, empfohlen oder optional ist und warum, oder `[]`, wenn er in reinem Minecraft läuft.
- [ ] Neue Blocknamen in `tools/i18n/bloecke_en.json` eintragen.
- [ ] Lokal bauen (`python tools/build_site.py`) und in der Ausgabe Blöcke und Schritte prüfen. Danach im Browser einmal alle Schritte durchklicken und die Draufsicht ansehen.
- [ ] Auf `main` pushen. Website, Schritte, Bilder und Downloads entstehen automatisch.

**Wichtige Änderung gegenüber heute:** Die bisherigen Modelle kennen keine **Blockrichtungen** (wohin eine Treppe zeigt, obere oder untere Stufe). Für echte Genauigkeit wird jeder Bau einmal in einer Kreativ-Testwelt nachgebaut oder geprüft und als `.litematic` exportiert. Diese Datei ist ab dann die Quelle für alles andere. Dabei wird jeder Bauplan automatisch einmal real getestet.

---

## 5. Architektur

```mermaid
flowchart LR
  subgraph Quellen
    B[builds/*<br/>.litematic + build.yml]
    P[plugins/*<br/>Java-Quellcode]
    D[docs/*.md<br/>Anleitungen]
    W[GitHub Issues<br/>Bauwünsche]
  end
  subgraph Pipeline [GitHub Actions]
    T[tools/<br/>Teileliste, Schritte,<br/>Exporte, Vorschaubilder, PDF]
    G[Gradle<br/>Plugin-.jar bauen]
  end
  subgraph Ausgaben
    S[Website<br/>GitHub Pages + PWA]
    A[Desktop-App<br/>Windows · Linux · macOS]
    R[GitHub Releases<br/>Plugin-Downloads]
  end
  B --> T --> S
  D --> S
  W --> T
  P --> G --> R --> S
  S --> A
```

**Technik-Entscheidungen**

| Teil | Wahl | Warum |
|---|---|---|
| Website | HTML, CSS und JavaScript-Module ohne Build-Schritt | läuft sofort auf GitHub Pages, kein Node nötig, eine Oberfläche für Web und Desktop. Ein Umstieg auf Vite und Svelte bleibt möglich, falls die Seite stark wächst |
| 3D-Ansicht | eigene isometrische Canvas-Darstellung | leicht, zoomt pro Schritt auf das Gebaute, hebt neue Blöcke hervor. Three.js kommt erst dazu, wenn freies Drehen und Zoomen gebraucht wird |
| Bauplan-Pipeline | Python (`litemapy`, `nbtlib`, `Markdown`) | liest und schreibt `.litematic`, `.schem`, später auch `.nbt` und Bedrock-`.mcstructure` |
| PDF-Heft | Playwright druckt die Schritt-Seiten | PDF sieht genau aus wie die Website |
| Desktop | Tauri 2 | kleine Installer (etwa 10 MB statt 100 MB bei Electron), gleiche Oberfläche |
| Plugins | Gradle-Multiprojekt, Paper-API, Java 21 | ein Befehl baut alle 7, jedes einzeln versioniert |
| Wünsche | GitHub-Issue-Formulare | kein eigener Server nötig, Abstimmung per 👍 |
| Sprachen | Deutsch und Englisch | `"en"` in den JSON-Dateien, `docs/en/`, `tools/i18n/` |

---

### 5.1 Gestaltung

- **Leitidee:** Ein Bauplan ist eine Blaupause. Überall, wo gebaut wird (Startseite, Schritt-Ansicht), steht das Modell auf einer bauplanblauen Fläche mit Raster. Der Fußbereich nimmt das Blau wieder auf. Alles andere bleibt ruhig.
- **Farben:** Bauplatte-Grau als Seite, Weiß für Inhalte, Bauplan-Blau für Bühnen, hellblaue Teile-Kästen wie in einem Bauheft, Signalgelb nur für „neu“. Hell, Dunkel und Automatisch über Farbvariablen in `site/style.css`.
- **Schrift:** Archivo breit für Überschriften, Schrittnummern und Stückzahlen, Atkinson Hyperlegible für Text, JetBrains Mono nur für Minecraft-IDs, Befehle und Koordinaten.
- **Kopfbereich:** Banner mit einer Minecraft-Landschaft aus Blöcken (Meer, Strand mit Leuchtturm, Wiese mit Haus und Feld, Wald, Berge mit Schnee). Tagsüber hell, im Dunkelmodus Nacht mit Sternen, Mond und leuchtendem Leuchtturm. Das Bild zeichnet `tools/seiten.py` (Funktion `landschaft`) bei jedem Bauen selbst, mit eigenen Farben statt Minecraft-Texturen. Darunter eine dunkle Menüleiste, die beim Scrollen stehen bleibt.
- **Startseite:** eine lebende Seite aus dem Bauheft: Schrittnummer, Teile-Kasten mit den Blöcken des Schritts und das wachsende Modell.
- **Regeln:** keine Großbuchstaben-Etiketten über Überschriften, keine Hüpf-Effekte auf Karten, Bewegung nur in der Startseiten-Animation (und nicht bei „weniger Bewegung“).

## 6. Downloads pro Eintrag

**Pro Bauplan**

| Datei | Für wen |
|---|---|
| `.litematic` | Java mit Litematica-Mod: Bauplan als Geisterblöcke im Spiel |
| `.schem` | WorldEdit oder FastAsyncWorldEdit auf Servern |
| `.nbt` | Strukturblock in Vanilla Java (bis 48 × 48 × 48, größere werden geteilt) |
| `.mcstructure` | Bedrock (Strukturblock) |
| `anleitung.pdf` | Ausdrucken, Tablet |
| `teileliste.csv` | Excel und Co. |

**Pro Plugin**
- `.jar` aus GitHub Releases. Jedes Plugin hat eigene Tags, z. B. `arbeiter-v2.0.1`.
- `README` mit Befehlen, Rechten und `config.yml` erklärt.
- Changelog.
- Getestete Paper-Version.

Jede Detailseite hat einen eigenen, teilbaren Link, etwa `…/#/bau/leuchtturm` oder `…/#/plugin/arbeiter`.

---

## 7. Repo-Struktur

```
minecraft-tools/
├─ MASTERPLAN.md
├─ README.md                  Einstieg, Disclaimer, Links
├─ LICENSE-CODE               Lizenz für Code und Plugins
├─ LICENSE-CONTENT            Lizenz für Baupläne und Texte
├─ builds/
│  └─ leuchtturm/
│     ├─ build.yml            Name, Beschreibung, Tags, Schritte-Overrides, Tipps
│     ├─ leuchtturm.litematic Quelle der Wahrheit
│     └─ README.md            optional: Hintergrund, Varianten
├─ plugins/
│  ├─ eigene/
│  │  ├─ arbeiter/            plugin.json, README.md, später src/ und build.gradle.kts
│  │  └─ …
│  └─ fremd/plugins.json      Plugins anderer Entwickler: Zweck, Einsatz, Link
├─ docs/                      Anleitungen (Farm-Bot, CoreProtect)
├─ tools/                     build_site.py (Schritte, Teileliste, Exporte, Website-Daten), seiten.py (vorgerenderte Seiten,
│                             Vorschaubilder, Sitemap), fetch_wishes.py, site_config.json
├─ site/                      Website: index.html, style.css, js/app.js, js/render.js
├─ desktop/                   später: Tauri-Hülle um site/
└─ .github/
   ├─ workflows/              website.yml (heute), später plugins.yml, desktop.yml
   └─ ISSUE_TEMPLATE/         bauwunsch.yml, plugin-wunsch.yml, fehler.yml
```

### Format eines Bauplans

Heute besteht jeder Bauplan aus `build.json` (Beschreibung, Abschnitte, Tipps, Rohstoffe) und `model.json` (Blöcke mit Minecraft-ID, Ebene für Ebene). Alle Felder stehen in [`builds/README.md`](builds/README.md).

Ab Phase 1 kommt eine `.litematic`-Datei aus der Testwelt als Quelle dazu. `model.json` wird dann daraus erzeugt, inklusive Blockrichtungen.

---

## 8. Phasenplan

Aufwand in **Arbeitssitzungen** (eine Sitzung = ein Abend gemeinsam mit Claude).

### Phase 0 · Fundament (1 Sitzung)
- [ ] Lizenzen festlegen und Dateien anlegen (siehe 10.)
- [x] README mit Disclaimer: „Kein offizielles Minecraft-Produkt …“
- [x] Repo-Ordner wie in 7. anlegen
- [x] Issue-Formulare: Bauwunsch, Plugin-Wunsch, Fehler melden
- [x] Workflow für GitHub Pages (Quelle: GitHub Actions)

**Fertig, wenn:** Eine leere Seite unter `savox76.github.io/minecraft-tools` erreichbar ist und ein Bauwunsch als Issue eingereicht werden kann.

### Phase 1 · Bauplan-Pipeline (2–3 Sitzungen)
- [ ] `.litematic` einlesen, inklusive Blockrichtungen
- [x] Teileliste und Rohstoffe (aus den bisherigen Modellen übernommen)
- [x] Automatische Schritt-Aufteilung nach den Schritt-Regeln aus 4.
- [x] Exporte: `.litematic`, `.schem`, `teileliste.csv`
- [ ] Exporte: `.nbt`, `.mcstructure`
- [x] Vorschaubilder (werden im Browser gezeichnet)
- [x] Check: Jeder Bauplan muss im Workflow fehlerfrei durchlaufen, auch bei Pull Requests
- [x] **Migration:** die 8 bisherigen Modelle sind als Entwurf im Repo
- [ ] In der Kreativ-Testwelt richten (Treppen, Türen) und als `.litematic` zurück ins Repo, Status dann `geprueft`

**Fertig, wenn:** Der Leuchtturm vollständig mit allen Exporten durchläuft und im Spiel per Litematica korrekt erscheint.

### Phase 2 · Website (3–4 Sitzungen)
- [x] Katalog: Kacheln mit Vorschaubild, Filter nach Kategorie
- [ ] Filter nach Größe, Schwierigkeit, Edition
- [x] Bauplan-Seite: Kenndaten, Teileliste, Schritt-Ansicht wie in einem Bauheft, 3D drehbar, Ebenen-Ansicht, Download-Knöpfe
- [x] Baufortschritt abhaken, gespeichert im Browser
- [ ] Koordinaten-Helfer (wie bisher): Mitte eintragen, echte X/Y/Z pro Block
- [x] Plugin-Seiten: Beschreibung, Befehle, Rechte, Config, Änderungen
- [ ] Download der neuesten Version (nach Phase 4)
- [x] Anleitungs-Seiten aus `docs/`
- [x] Wunschliste: offene Bauwünsche, sortiert nach 👍
- [ ] PWA: installierbar und offline nutzbar (Manifest steht, Offline-Speicher fehlt noch)
- [x] Hell, Dunkel oder Automatisch (wie das Gerät), Handy-tauglich, Wischen zwischen Schritten
- [x] Deutsch und Englisch: eigene Adressen unter `/en/`, Sprachschalter im Kopf, alle Baupläne, Plugins, Anleitungen und Blocknamen übersetzt
- [x] Vorschaubilder der Karten werden im Browser gezeichnet (wie die 3D-Ansicht); das vorgerenderte Bild beim ersten Laden bleibt im Bildfeld

**Fertig, wenn:** Alle Baupläne, Plugins und Anleitungen online sind und jede Seite einen eigenen Link hat. Stand: erledigt bis auf die offenen Punkte oben.

### Phase 3 · PDF-Bauhefte (1 Sitzung)
- [ ] Druck-Layout für Deckblatt, Teileliste, Schritte (2 pro Seite bei kleinen Schritten)
- [ ] Automatisch bei jeder Änderung neu erzeugen und zum Download anbieten

### Phase 4 · Plugins ins Repo (2–3 Sitzungen)
- [ ] Quellcode der 7 Plugins übernehmen, Gradle-Multiprojekt
- [ ] **Sicherheits-Check vor dem Hochladen:** keine Passwörter, Server-IPs, playit-Adressen oder persönlichen Spielernamen im Code oder in Standard-Configs
- [ ] Texte auslagern, damit sie übersetzbar sind (Deutsch und Englisch)
- [x] Pro Plugin: README (Befehle, Rechte, Config, Änderungen)
- [ ] Workflow: Ein Tag `<plugin>-v<version>` baut die `.jar` und hängt sie an ein Release
- [ ] Optional: zusätzlich auf Modrinth und Hangar veröffentlichen

**Fertig, wenn:** Jedes Plugin einzeln über die Website als `.jar` herunterladbar ist.

### Phase 5 · Desktop-App (2 Sitzungen)
- [ ] Tauri-Hülle um dieselbe Website
- [ ] Lokale Zusatzfunktionen:
  - „In Minecraft öffnen“: kopiert `.litematic` in `.minecraft/schematics`
  - „In Server installieren“: Server-Ordner wählen, Plugin kopieren, vorher Backup (wie heute `INSTALLIEREN.bat`)
  - Offline-Gesamtpaket aller Baupläne
- [ ] Workflow: Installer für Windows (`.msi`), macOS (`.dmg`) und Linux (`.AppImage`, `.deb`) bei jedem Release
- [ ] Hinweis für Nutzer: Ohne kostenpflichtige Code-Signatur zeigen Windows („Der Computer wurde geschützt“) und macOS beim ersten Start eine Warnung

### Phase 6 · Community (1 Sitzung, danach laufend)
- [ ] `CONTRIBUTING.md`: So reicht man einen eigenen Bauplan ein (`.litematic` + `build.yml` per Pull Request)
- [ ] Automatische Prüfung eingereichter Baupläne
- [ ] Wunsch-Ablauf: Issue → Label `angenommen` → in Arbeit → fertig, dann automatisch mit dem neuen Bauplan verlinkt

---

## 9. Bauwünsche

1. Auf der Website auf **„Bauplan wünschen“** klicken. Das öffnet ein GitHub-Formular mit den Feldern Name des Bauwerks, Stil, ungefähre Größe, Java/Bedrock, Referenzbilder und gewünschte Rohstoffe.
2. Andere stimmen mit **👍** ab.
3. Einmal pro Tag holt ein Workflow die offenen Wünsche und schreibt sie als Datei in die Website. Besucher brauchen dafür kein GitHub-Konto und die Seite keine Live-Abfrage.
4. Zum Einreichen braucht man ein kostenloses GitHub-Konto. Ein Formular ohne Konto ginge nur mit einem Zusatzdienst, das ist eine spätere Option.

---

## 10. Rechtliches und Sicherheit

- **Kein Minecraft-Material verbreiten:** keine Original-Texturen, Sounds oder das Logo im Repo. Die Blöcke werden wie bisher mit eigenen Farben dargestellt. In der Desktop-App kann jeder optional sein **eigenes** Ressourcenpaket laden, das dann nur lokal genutzt wird.
- **Disclaimer** auf jeder Seite: „Kein offizielles Minecraft-Produkt. Nicht von Mojang oder Microsoft genehmigt oder mit ihnen verbunden.“ Das Tool darf nicht offiziell wirken.
- **Kostenlos:** Die Minecraft-EULA verbietet, mit Mods oder Inhalten Geld zu verdienen. Alles bleibt also gratis.
- **Lizenz-Vorschlag:**
  - Code und Plugins: **MIT** (jeder darf nutzen und ändern, Namensnennung bleibt)
  - Baupläne und Texte: **CC BY 4.0** (frei nutzbar mit Namensnennung) oder **CC BY-NC 4.0** (zusätzlich keine kommerzielle Nutzung durch andere)
- **Plugins:** Vor jeder Veröffentlichung auf Passwörter und Adressen prüfen (siehe Phase 4). AdminLogin speichert Passwörter verschlüsselt, das bleibt so.
- **Datenschutz:** Die Website setzt keine Cookies und kein Tracking. Der Baufortschritt bleibt nur im Browser des Nutzers.
- **Impressum:** Ob eine private, kostenlose Seite ein Impressum braucht, hängt davon ab, ob sie als geschäftsmäßig gilt, etwa durch eine Verbindung zur Marke Savox. Das vor dem Start kurz prüfen. Ich bin kein Anwalt.

---

## 11. Ideen für später

- **Ingame-Plugin „BauHelfer“:** zeigt den aktuellen Bauschritt als Geisterblöcke direkt auf dem Server, prüft, ob alles richtig gesetzt ist, und hakt den Schritt ab. Funktioniert ohne Mod, also auch für Bedrock-Spieler.
- **Shop-Preisrechner:** Was kostet ein Bauplan in Coins im eigenen ServerShop?
- **Farm-Planer:** Welche Farmen braucht ein Bauplan, und wie lange dauert das Sammeln?
- **Lageplan-Editor:** mehrere Baupläne plus Farm-Bot-Radius auf einer Karte anordnen
- **Zeitraffer-Animation:** jeder Bauplan als kurzes Video oder GIF, Schritt für Schritt
- **Varianten:** Größen (1:1, 1:2) und Materialvarianten (Holz- oder Steinversion) per Klick
- **Bauplan-Pakete:** zusammengehörige Pläne gebündelt, z. B. „Villa am Wasser + Kellerlager + Gewächshaus“
- **Server-Setup-Assistent:** Paper, Plugins, Bot und Einstellungen in einem geführten Ablauf (Desktop-App)

---

## 12. Offene Entscheidungen

| # | Frage | Mein Vorschlag |
|---|---|---|
| 1 | Name des Projekts | ✅ „Bauwerkstatt“ mit Zusatz „Baupläne und Plugins für Minecraft“ (vorher „Savox Bauwerkstatt“) |
| 2 | Lizenz Baupläne | CC BY-NC 4.0 |
| 3 | Lizenz Code und Plugins | MIT |
| 4 | Sprachen | ✅ Deutsch und Englisch, seit Phase 2 umgesetzt |
| 5 | Plugin-Quellcode öffentlich? | Ja, nach dem Sicherheits-Check |
| 6 | Bedrock-Export (`.mcstructure`) | Ja, weil dein Server Bedrock-Spieler hat |
| 7 | Desktop-App sofort oder später? | Später (Phase 5), die Website deckt erst einmal alles ab |
| 8 | Eigene Domain statt `savox76.github.io/minecraft-tools`? | Optional, auch später möglich (ca. 10 €/Jahr) |

---

## 13. Nächster Schritt

Entscheidungen aus Abschnitt 12 treffen (vor allem die Lizenz), dann den Plugin-Quellcode übernehmen (Phase 4). Parallel kannst du schon einmal den Leuchtturm in einer Kreativ-Testwelt bauen und als `.litematic` exportieren. Er wird der erste vollständige Bauplan in der Pipeline.

---

## 14. Gefunden werden (Suchmaschinen)

### Was die Website automatisch macht

- **Echte Adressen** pro Seite, z. B. `…/bau/leuchtturm/` statt `…/#/bau/leuchtturm`. Alte `#/`-Links werden umgeleitet.
- **Zwei Sprachen:** jede Seite gibt es auf Deutsch und auf Englisch (`…/en/build/leuchtturm/`). `hreflang`-Verweise sagen Google, welche Seite zu welcher Sprache gehört, so erscheint im Ausland die englische Fassung. Keine automatische Umleitung, der Besucher wählt selbst.
- **Vorgerenderte Seiten:** Jede Seite enthält ihren kompletten Text (Beschreibung, Bauabschnitte, Teileliste, Rohstoffe, Downloads, Befehle) schon im HTML. Suchmaschinen lesen ihn ohne JavaScript, im Browser übernimmt dann die interaktive Ansicht.
- **Pro Seite:** eigener Titel mit Suchbegriffen („Leuchtturm in Minecraft bauen – Bauplan in 58 Schritten“), Beschreibung, Canonical-Link, Open-Graph- und Twitter-Vorschau.
- **Vorschaubilder:** pro Bauplan ein Bild (800 × 600) und ein Link-Vorschaubild (1200 × 630) für WhatsApp, Discord und soziale Netzwerke.
- **Strukturierte Daten (JSON-LD):** `HowTo` für Baupläne (Material und Bauabschnitte), `SoftwareApplication` für Plugins, `TechArticle` für Anleitungen, `BreadcrumbList` überall.
- **`sitemap.xml`** mit allen Seiten und Bildern, `404.html`, interne Links im Fußbereich zu allen Seiten.
- **IndexNow:** Nach jedem Push meldet der Workflow alle Adressen an Bing, Yandex, Seznam und weitere Suchmaschinen.

### Was nur du machen kannst (einmalig)

- [x] **Google Search Console:** <https://search.google.com/search-console> → Property hinzufügen → **URL-Präfix** `https://savox76.github.io/minecraft-tools/` → Bestätigung per **HTML-Tag**. Den Code aus `content="…"` in [`tools/site_config.json`](tools/site_config.json) bei `google_site_verification` eintragen (oder mir schicken), pushen, ein paar Minuten warten, dann „Bestätigen“ klicken. ✅ Code ist in `tools/site_config.json` eingetragen (01.11.2026); in der Search Console auf „Bestätigen“ klicken.
- [ ] Danach in der Search Console unter **Sitemaps** `sitemap.xml` einreichen.
- [ ] **Bing Webmaster Tools:** <https://www.bing.com/webmasters> → „Aus Google Search Console importieren“. Bing beliefert auch DuckDuckGo und Ecosia.
- [ ] **GitHub-Repo:** Auf der Repo-Seite rechts bei „About“ das Zahnrad → Website `https://savox76.github.io/minecraft-tools/` eintragen, Topics: `minecraft`, `minecraft-schematics`, `litematica`, `worldedit`, `paper-plugin`, `minecraft-plugin`.

### Bekannt machen (Links von außen)

Suchmaschinen bewerten eine Seite auch danach, wer auf sie verlinkt.

- **Planet Minecraft** (planetminecraft.com): die größte Seite für Baupläne. Jeden Bauplan mit Bild und `.litematic` hochladen und auf die Schritt-für-Schritt-Anleitung verlinken.
- **Modrinth und Hangar:** sobald die Plugins als `.jar` fertig sind (Phase 4), dort veröffentlichen und die Website als Homepage angeben.
- **Reddit:** r/Minecraft, r/MinecraftBuilds, r/admincraft (für die Plugins), deutschsprachig r/minecraftDE. Am besten mit einem Bild oder GIF der Schritt-Animation.
- **Savox-Kanäle:** Zeitraffer eines Baus als Short oder TikTok mit Link zum Bauplan.
- **Discord:** Minecraft-Bau- und Server-Admin-Communities.

### Wichtig zu wissen

- Eine neue Seite braucht meist einige Tage bis wenige Wochen, bis sie bei Google erscheint. Die Search Console zeigt, welche Seiten schon aufgenommen sind.
- `robots.txt` wird von Suchmaschinen nur direkt auf `savox76.github.io/` gelesen, nicht im Unterordner. Deshalb ist das Einreichen der Sitemap in der Search Console der wichtige Weg.
- Mit einer eigenen Domain (Masterplan 12., Punkt 8) wäre die Seite unabhängig von GitHub und leichter zu merken. Dann nur `site_url` in `tools/site_config.json` ändern.

---

## 15. Ideen-Speicher: geplante Baupläne und Anleitungen

Alle Ideen stehen in [`ideen/ideen.json`](ideen/ideen.json), jeweils mit Nummer, Kategorie, Größe, Status und kurzem Text auf Deutsch und Englisch. Daraus entstehen automatisch die Seite **Geplant** auf der Website (`/geplant/`, englisch `/en/planned/`) und die Tabellen unten.

**Ablauf**
- Neue Idee: Eintrag in `ideen/ideen.json` mit der nächsten freien Nummer, danach `python tools/ideen_masterplan.py` ausführen. Das schreibt die Tabellen unten neu.
- Wird eine Idee umgesetzt: `status` auf `in-arbeit`, dann auf `verfuegbar` mit `"bauplan": "<id>"`. Die Geplant-Seite verlinkt dann direkt auf den Bauplan.
- Plugins: Braucht eine Idee ein Plugin, steht es unter `plugins` mit `id` und `stufe` (`benoetigt`, `empfohlen`, `optional`). Die Geplant-Seite zeigt es auf der Karte.
- Abstimmen: Auf der Geplant-Seite führt „Wünschen“ zu einem vorausgefüllten Bauwunsch („Idee #61: Kakaofarm“). Gibt es dazu schon einen offenen Wunsch, zeigt die Seite dessen 👍-Stimmen und verlinkt dorthin.
- Größe: klein (bis etwa 15 × 15), mittel, groß. Für Nachbauten echter Wahrzeichen gibt der Bauplan einen Maßstab an (wie beim Eiffelturm 1:3).

**Hinweis zu Paper:** Farmen, die Sand, TNT oder Teppiche vervielfältigen, laufen auf Paper normalerweise nicht und stehen deshalb nicht auf der Liste. Bäume fällt am besten der Holzfäller aus dem Arbeiter-Plugin. Monsterfarmen laufen nur, wenn ein Spieler oder der Farm-Bot in der Nähe ist.

<!-- ideen:start -->
164 Einträge: 164 💡 Idee, 0 🔨 in Arbeit, 0 ✅ verfügbar.

**Als Nächstes empfohlen:** Nr. 1 Kaktus-XP-Farm mit Ofenbatterie, Nr. 9 Kleine Bambusfarm, Nr. 11 Bambus-Brennstoffstation.

### Skillfarmen (XP) (10)

Erfahrung für Verzauberungen und Reparaturen.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 1 | Kaktus-XP-Farm mit Ofenbatterie | klein | Kaktus wächst von selbst, Trichter bringen ihn in eine Reihe Öfen. Jeder Kaktus wird zu grünem Farbstoff und gibt 1 XP, die im Ofen gespeichert bleibt, bis du ihn leerst. Ganz ohne Monster. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 2 | Seetang-XP-Ofen | klein | Wie die Kaktus-Farm, nur mit Seetang. Gibt weniger Erfahrung, liefert dafür getrockneten Seetang, der als Block ein guter Brennstoff ist. | 💡 Idee |
| 3 | Dunkelraum-Monsterfarm | mittel | Ein dunkler Turm, in dem Monster spawnen und in eine Kammer fallen, wo ein Schlag reicht. Nebenbei Knochen, Pfeile, Schießpulver und Fäden. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 4 | Spawner-XP-Farm | klein | Rund um einen gefundenen Zombie- oder Skelett-Spawner. Sehr ergiebig und schnell gebaut, aber nur dort möglich, wo ein Spawner liegt. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 5 | Lohenfarm | mittel | An einem Lohen-Spawner in der Netherfestung. Viel XP und Lohenruten für Braustände und Enderaugen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 6 | Goldfarm auf dem Nether-Dach | groß | Zombifizierte Piglins werden mit Schildkröteneiern angelockt und fallen in eine Kammer. Sehr viel XP und Gold. | 💡 Idee |
| 7 | Endermanfarm im End | groß | Die schnellste XP-Quelle im Spiel, dazu Enderperlen. Der Enderdrache muss vorher besiegt sein. | 💡 Idee |
| 8 | Kleine Handelshalle | klein | Sechs Dorfbewohner in einer Reihe, jeder in einer eigenen Zelle hinter seinem Arbeitsblock. Gehandelt wird über den Block hinweg, so kann niemand weglaufen. Mit zwei Bibliothekaren für Verzauberungsbücher, etwa 15 × 9 Blöcke. Plugin: arbeiter (optional). | 💡 Idee |
| 117 | Große Handelshalle | groß | 16 Zellen in zwei Reihen gegenüber, alle 13 Berufe einmal und Bibliothekare mehrfach. Mit Lore-Zufahrt zum Einbringen der Dorfbewohner und einer Heilstation für Zombie-Dorfbewohner, die dauerhaft bessere Preise bringt. Plugin: arbeiter (optional). | 💡 Idee |
| 118 | Große Handelshalle im Stil einer Zauberschule | groß | Eine hohe Halle mit Spitzbogen-Gewölbe, schwebenden Kerzen aus Lichtblöcken und langen Tafeln in der Mitte. Die Händler stehen in Nischen an den Seitenwänden, über ihnen Galerien mit Bücherregalen und Bannern. Plugin: arbeiter (optional). | 💡 Idee |

### Farmen für Baumaterial (21)

Liefern die Blöcke und Rohstoffe für die Baupläne.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 9 | Kleine Bambusfarm | klein | Eine Reihe mit 8 Bambuspflanzen. Beobachter merken das Wachsen, Kolben brechen den Bambus ab, Trichter sammeln alles ein. Etwa 8 × 4 Blöcke. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 10 | Große Bambusfarm | groß | Zwei Reihen mit je 16 Pflanzen. Eine Trichterlore unter Glas sammelt in eine Fasskette. Genug für Bambusbretter und Mosaik in großen Mengen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 12 | Melonen- und Kürbisfarm | klein | Beobachter und Kolben ernten, sobald eine Frucht wächst. Kürbisse für Laternen und Golems, Melonen als Essen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 13 | Wollfarm | klein | Schafe fressen Gras, ein Werfer mit Schere schert sie automatisch. Eine Farbe pro Kammer für bunte Bauten. | 💡 Idee |
| 14 | Honig- und Waben-Farm | klein | Bienenstöcke mit Werfern für Flaschen und Scheren. Honigblöcke, Waben für Kerzen und gewachste Kupferblöcke. | 💡 Idee |
| 15 | Eisenfarm | mittel | Dorfbewohner werden von einem Zombie erschreckt, dabei entstehen Eisengolems. Eisen für Trichter, Schienen und Laternen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 16 | Schneefarm mit Schneegolems | klein | Schneegolems hinterlassen Schnee, der automatisch abgebaut wird. Schneeblöcke und Eis zum Bauen. | 💡 Idee |
| 17 | Lava aus Tropfstein | klein | Spitzer Tropfstein unter einer Lavaquelle füllt einen Kessel. Unendlich Lava als Brennstoff, ohne in den Nether zu müssen. | 💡 Idee |
| 18 | Basalt-Generator | klein | Lava, Blaueis und Seelenerde erzeugen immer neuen Basalt. Daraus wird polierter Basalt und glatter Basalt. | 💡 Idee |
| 19 | Bruchstein-Generator | klein | Lava und Wasser erzeugen Bruchstein nach, du baust nur noch ab. Grundlage für Steinziegel, glatten Stein und Treppen. | 💡 Idee |
| 20 | Moosfarm | klein | Werfer mit Knochenmehl lassen Moos wachsen. Moos, Azaleen und Material für den Komposter. | 💡 Idee |
| 21 | Kuh- und Hühnerfarm | klein | Kleine Gehege mit Begrenzung, damit die Tiere nicht überhandnehmen. Leder für Bücher, Federn, Eier und Fleisch. | 💡 Idee |
| 60 | Zuckerrohrfarm | klein | Eine Reihe Zuckerrohr mit Beobachtern und Kolben. Papier für Bücher, Karten und Raketen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 61 | Kakaofarm | klein | Beobachter und Kolben ernten Kakaobohnen am Tropenbaumstamm. Für Kekse und braunen Farbstoff. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 62 | Blumenfarm | klein | Ein Werfer mit Knochenmehl auf Gras lässt Blumen wachsen. Alle Grundfarben für Wolle, Beton und Glas. | 💡 Idee |
| 64 | Tonfarm | mittel | Werfer mit Wasserflaschen machen Erde zu Schlamm, Tropfstein darunter macht daraus Ton. Für Terrakotta und Ziegel. | 💡 Idee |
| 65 | Froschlicht-Farm | groß | Frösche fressen kleine Magmawürfel und lassen dabei Froschlichter fallen. Leuchtblöcke in drei Farben. | 💡 Idee |
| 66 | Amethyst-Farm | mittel | An einer gefundenen Geode: Beobachter merken reife Kristalle, Kolben brechen sie ab. Für Fernrohr und getöntes Glas. | 💡 Idee |
| 67 | Chorusfrucht-Farm im End | mittel | Halbautomatisch: Chorusblumen wachsen nach, du erntest. Chorusfrüchte werden zu Purpurblöcken. | 💡 Idee |
| 68 | Pilzfarm | klein | Ein dunkler Raum, in dem sich Pilze von selbst ausbreiten. Für Suppen und Riesenpilz-Deko. | 💡 Idee |
| 150 | Große Kaktusfarm | groß | Mehrere Etagen mit Kaktus auf Sand. Wächst ein Kaktus an einen Zaun heran, bricht er ab und fällt in Wasserrinnen, die alles zu Trichtern und Fässern führen. Zusammen mit einer großen Ofenbatterie eine starke XP-Quelle und viel grüner Farbstoff. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |

### Monsterfarmen (3)

Material für Redstone und Raketen.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 22 | Schleimfarm | mittel | In einem Schleim-Chunk oder Sumpf. Schleimbälle für Klebekolben und Schleimblöcke. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 23 | Hexenfarm | groß | An einer Sumpfhütte. Redstone, Leuchtsteinstaub, Zucker und Flaschen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |
| 24 | Creeperfarm | mittel | Nur Creeper spawnen auf Spezialblöcken. Schießpulver für Raketen. Plugin: fakeplayerplugin (empfohlen). | 💡 Idee |

### Verarbeitung und Fabriken (9)

Machen aus Rohstoffen fertige Dinge, ganz von selbst.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 11 | Bambus-Brennstoffstation | klein | Koppelt die Bambusfarm an die Ofenbatterie. Die Öfen laufen dann ohne Kohle. | 💡 Idee |
| 63 | Komposter-Kette | klein | Überschuss aus Bambus, Kaktus und Seetang wird in Kompostern zu Knochenmehl. | 💡 Idee |
| 69 | Holzkohle-Station | klein | Stämme vom Holzfäller-Arbeiter werden in Öfen zu Holzkohle. Plugin: arbeiter (benötigt). | 💡 Idee |
| 70 | Erz-Schmelzstation | mittel | Eine Einwurftruhe verteilt auf viele Öfen gleichzeitig, die Ausgabe landet sortiert in Fässern. | 💡 Idee |
| 71 | Automatische Werkbank (Crafter) | mittel | Der Crafter aus 1.21 stellt Dinge selbst her, zum Beispiel Brot, Papier oder Eisenblöcke. | 💡 Idee |
| 72 | Raketen-Fabrik | mittel | Papier und Schießpulver werden per Crafter zu Raketen für Elytra-Flüge. | 💡 Idee |
| 73 | Automatische Brauerei | mittel | Braustände mit Trichtern für Zutaten und Lohenpulver. Tränke in Serie. | 💡 Idee |
| 74 | Automatische Küche | klein | Räucheröfen mit Trichtern, gefüttert aus der Kuh- und Hühnerfarm. | 💡 Idee |
| 75 | Buch-Station | mittel | Zuckerrohr und Leder werden zu Büchern und Bücherregalen. | 💡 Idee |

### Funktionale Bauten (21)

Technik und Komfort für Basis und Server.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 25 | Verzauberungsraum | klein | Zaubertisch mit 15 Bücherregalen, dazu Amboss und Schleifstein. Passt direkt zu den XP-Farmen. | 💡 Idee |
| 26 | Marktplatz für Spieler-Shops | mittel | Stände für die Shop-Truhen aus dem ServerShop-Plugin, mit Schildern und Laternen. Plugin: servershop (benötigt). | 💡 Idee |
| 27 | Lorenbahnhof | mittel | Gleise vom Spawn zu allen Farmen, mit Haltestellen und Fahrplan-Schildern. | 💡 Idee |
| 76 | Blasen-Aufzug | klein | Seelensand fährt hoch, Magmablock runter. Als eigener Bauplan zum Einbauen in jedes Haus. | 💡 Idee |
| 77 | Item-Aufzug | klein | Eine Blasensäule hebt Gegenstände vom Keller nach oben ins Lager. | 💡 Idee |
| 78 | Versteckte Kolbentür 2 × 2 | klein | Öffnet per Knopf oder Druckplatte und verschwindet in der Wand. | 💡 Idee |
| 79 | Geheimgang hinter Bücherregal | klein | Der klassische Geheimeingang, zum Beispiel zum Lager. | 💡 Idee |
| 80 | Tresor mit Zahlenschloss | mittel | Ein Redstone-Kombinationsschloss mit Hebeln. Nur wer den Code kennt, kommt rein. | 💡 Idee |
| 81 | Automatisches Licht | klein | Ein Tageslichtsensor schaltet Redstone-Lampen ab Abend ein. | 💡 Idee |
| 82 | Zugbrücke | mittel | Kolben fahren die Brücke ein und aus. Passt zur Burg. | 💡 Idee |
| 83 | Leuchtfeuer-Pyramide | mittel | Eisenblöcke aus der Eisenfarm, Effekte wie Eile beim Abbauen. | 💡 Idee |
| 84 | Aquisitor-Rahmen | klein | Gibt Atmung unter Wasser, zum Beispiel rund um die Glaskuppel. | 💡 Idee |
| 85 | Nether-Knotenpunkt | groß | Portale zu allen Basen und eine Eisstraße für schnelle Bootsfahrten. | 💡 Idee |
| 86 | Kartenraum | mittel | Karten in Rahmen ergeben eine große Wandkarte der Welt. | 💡 Idee |
| 87 | Farm-Bot-Zentrale | klein | Ein sicherer, beleuchteter Raum für den Farm-Bot, mitten zwischen den Farmen. Plugin: fakeplayerplugin (benötigt). | 💡 Idee |
| 88 | Lagerhalle mit Einlagern-Truhen | mittel | Für das InfiniteLager-Plugin, gemeinsamer und privater Bereich getrennt. Plugin: infinitelager (benötigt). | 💡 Idee |
| 89 | Werkstatt | klein | Amboss, Schleifstein, Schmiedetisch, Webstuhl und Steinsäge an einem Ort. | 💡 Idee |
| 90 | Ausrüstungsraum | klein | Rüstungsständer, Waffen und Werkzeuge geordnet an der Wand. | 💡 Idee |
| 91 | Beleuchteter Spawn | mittel | Ein Laternen-Raster, damit am Spawn keine Monster entstehen, und das sieht trotzdem gut aus. | 💡 Idee |
| 103 | Sortiermodul | klein | Eine einzelne Sortierstrecke zum Anbauen an jede Farm, ohne ganzes Kellerlager. | 💡 Idee |
| 104 | Müllschlucker | klein | Eine Truhe, deren Inhalt in Kaktus oder Lava verschwindet. Für Überschuss, den niemand braucht. | 💡 Idee |

### Tiere (5)

Gehege, Ställe und Aquarien.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 92 | Schildkröten-Brutstation | klein | Ein Strand mit Schildkröten, deren Eier geschützt schlüpfen. Für Schildkrötenpanzer und Tränke. | 💡 Idee |
| 93 | Axolotl-Aquarium | klein | Ein großes Glasbecken als Deko im Haus. Axolotl helfen später auch beim Kampf unter Wasser. | 💡 Idee |
| 94 | Pferdestall mit Koppel | mittel | Boxen, Heulager und eine Koppel zum Züchten schneller Pferde. | 💡 Idee |
| 95 | Tierheim für zahme Tiere | klein | Ein sicheres Haus für Hunde, Katzen und Papageien, geschützt vor Monstern. | 💡 Idee |
| 97 | Schnüffler-Gehege | mittel | Schnüffler graben seltene Samen aus: Fackellilien und Kannenpflanzen für besondere Gärten. | 💡 Idee |

### Spiel und Freizeit (5)

Für Events und gemeinsame Abende auf dem Server.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 98 | Arena mit Tribüne | mittel | Für Mob-Kämpfe oder Duelle, mit Zuschauerrängen und Eingangstoren. | 💡 Idee |
| 99 | Parkour-Strecke | mittel | Sprünge in Stufen von leicht bis schwer, mit Kontrollpunkten. | 💡 Idee |
| 100 | Heckenlabyrinth | mittel | Ein Irrgarten aus Laub mit Schatz in der Mitte. | 💡 Idee |
| 101 | Elytra-Startturm | mittel | Ein hoher Turm mit Startplattform und gepolstertem Landeplatz. | 💡 Idee |
| 102 | Bogenschießstand | klein | Zielblöcke geben ein Redstone-Signal, ein Lämpchen zeigt Treffer an. | 💡 Idee |

### Mystery-Bauwerke (14)

Bauwerke mit Geheimnissen: versteckte Gänge, Rätsel, Ruinen und verlassene Orte.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 136 | Spukvilla mit Geheimgängen | groß | Eine verfallene Villa mit knarrenden Dielen, verdeckten Kolbentüren hinter Bildern und Regalen und einem Gang, der in eine verborgene Gruft führt. | 💡 Idee |
| 137 | Escape-Room-Haus | mittel | Ein Haus voller Redstone-Rätsel: Hinweise auf Schildern und in Büchern, Hebel in der richtigen Reihenfolge öffnen den nächsten Raum. Ideal für Server-Events. | 💡 Idee |
| 138 | Rätselgrab in der Wüste | groß | Ein Grabmal mit Fallen, Druckplatten-Rätseln und einer Schatzkammer, die sich nur mit dem richtigen Code öffnet. | 💡 Idee |
| 139 | Versunkene Tempelstadt | groß | Ruinen einer Stadt am Meeresgrund, halb im Sand begraben, mit Säulen, eingestürzten Dächern und einem Tempel voller Prismarin. | 💡 Idee |
| 140 | Steinkreis mit Geheimkammer | mittel | Uralte Steine im Kreis. Wer die Hebel an den Steinen richtig umlegt, öffnet eine Treppe in eine Kammer darunter. | 💡 Idee |
| 141 | Verlassenes Bergwerk | mittel | Ein Stollen mit Holzstützen, rostigen Schienen, umgekippten Loren und einem eingestürzten Gang, hinter dem etwas Seltsames leuchtet. | 💡 Idee |
| 142 | Geisterschiff | mittel | Ein Wrack mit zerrissenen Segeln, schief im Nebel liegend, mit Laternen, die nachts von allein zu leuchten scheinen. | 💡 Idee |
| 143 | Bibliothek hinter dem Wasserfall | mittel | Ein Wasserfall verdeckt den Eingang zu einer Höhle mit Bücherregalen, Lesepult und einer Karte zum nächsten Geheimnis. | 💡 Idee |
| 144 | Hexenturm im Sumpf | mittel | Ein schiefer Turm auf Stelzen mit Kesseln, Braustand, Kräutergarten und einer Falltür ins Ungewisse. | 💡 Idee |
| 145 | Geisterdorf | groß | Ein verlassenes Dorf mit leeren Häusern, Spinnweben, überwucherten Wegen und einem Brunnen, der tiefer führt, als er sollte. | 💡 Idee |
| 146 | Uhrturm mit Geheimkammer | mittel | Hinter dem Ziffernblatt liegt eine Kammer mit Zahnrädern aus Blöcken. Ein versteckter Mechanismus öffnet den Weg nach oben. | 💡 Idee |
| 147 | Schwarzer Monolith | klein | Ein glatter Block aus Obsidian mitten im Nirgendwo, mit Inschriften auf Schildern und einer Kammer, die nur nachts erreichbar ist. | 💡 Idee |
| 148 | Friedhof mit Gruft | mittel | Grabsteine, alte Bäume, eine Kapelle und darunter eine Gruft mit Kerzen und einem versiegelten Raum. | 💡 Idee |
| 149 | Sternwarte der Sterndeuter | mittel | Ein Turm mit Kuppel, Sternbildern aus Lichtblöcken im Boden und einem Rätsel, das nur mit Blick in den Nachthimmel lösbar ist. | 💡 Idee |

### Monumente (29)

Nachbauten bekannter Wahrzeichen, mit passendem Maßstab.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 30 | Brandenburger Tor | mittel | Das Berliner Wahrzeichen mit Säulen und der Quadriga aus Kupfer. | 💡 Idee |
| 31 | Big Ben | groß | Der Uhrturm in London mit vier Zifferblättern, gut im Maßstab 1:2. | 💡 Idee |
| 32 | Kölner Dom | groß | Zwei Türme, Spitzbögen und bunte Glasfenster. | 💡 Idee |
| 33 | Frauenkirche Dresden | groß | Die steinerne Glockenkuppel aus hellem Sandstein. | 💡 Idee |
| 34 | Freiheitsstatue | groß | Gebaut aus Kupfer, das im Spiel mit der Zeit von selbst grün wird. | 💡 Idee |
| 35 | Schiefer Turm von Pisa | mittel | Die Schräge entsteht durch versetzte Ringe, dazu Säulengänge. | 💡 Idee |
| 36 | Kolosseum | groß | Ovale Arena mit Bögen, teilweise eingestürzt wie im Original. | 💡 Idee |
| 37 | Schloss Neuschwanstein | groß | Türme und Spitzdächer auf einem Felsen. | 💡 Idee |
| 38 | Tower Bridge | groß | Zwei Türme mit Klappbrücke, die mit Kolben funktionieren kann. | 💡 Idee |
| 39 | Pyramide mit Grabkammer | groß | Braucht viel Sandstein. Sand lässt sich auf Paper nicht farmen, also vorher sammeln. | 💡 Idee |
| 40 | Japanische Pagode | mittel | Fünf Stockwerke mit geschwungenen Dächern. | 💡 Idee |
| 41 | Maya-Tempel | mittel | Stufenpyramide mit großer Treppe und Dschungel-Deko. | 💡 Idee |
| 42 | Stonehenge | klein | Ein Steinkreis, gut als erstes Monument. | 💡 Idee |
| 111 | Parthenon | groß | Der griechische Tempel auf der Akropolis, mit umlaufenden Säulen. | 💡 Idee |
| 112 | Chinesische Mauer | mittel | Ein Abschnitt mit Wachtürmen, der sich über Hügel zieht. | 💡 Idee |
| 113 | Taj Mahal | groß | Weißer Palast mit großer Kuppel, vier Minaretten und Wasserbecken. | 💡 Idee |
| 114 | Holstentor Lübeck | mittel | Das Backsteintor mit zwei runden Türmen und Spitzhelmen. | 💡 Idee |
| 115 | Rialtobrücke | mittel | Steinbrücke mit Läden über einem Kanal, wie in Venedig. | 💡 Idee |
| 116 | Moai-Köpfe | klein | Die steinernen Köpfe der Osterinsel, schnell gebaut und gut als Deko am Strand. | 💡 Idee |
| 119 | Notre-Dame de Paris | groß | Die gotische Kathedrale mit zwei Fassadentürmen, großer Fensterrose und Strebebögen an den Seiten. | 💡 Idee |
| 120 | Hagia Sophia | groß | Riesige flache Kuppel über einem quadratischen Bau, ringsum Halbkuppeln und vier schlanke Minarette. | 💡 Idee |
| 121 | Petersdom mit Petersplatz | groß | Die große Kuppel über der Basilika, davor der ovale Platz mit Säulengängen und einem Obelisken in der Mitte. | 💡 Idee |
| 122 | Angkor Wat | groß | Tempelanlage mit fünf Türmen in Form von Lotusknospen, umgeben von einem breiten Wassergraben. | 💡 Idee |
| 123 | Mont-Saint-Michel | groß | Eine Klosterinsel im Meer: Häuser und Mauern ziehen sich spiralförmig den Felsen hoch, oben die Abtei mit Spitze. | 💡 Idee |
| 124 | Machu Picchu | groß | Steinterrassen und Ruinen auf einem Bergsattel, passt perfekt in Minecraft-Berge. | 💡 Idee |
| 125 | Golden Gate Bridge | groß | Hängebrücke mit zwei roten Pylonen und Tragseilen aus Ketten, über eine Meeresbucht gespannt. | 💡 Idee |
| 126 | Alhambra | groß | Palastanlage mit Innenhöfen, Wasserbecken, Bogengängen und fein gemusterten Wänden. | 💡 Idee |
| 127 | Koloss von Rhodos | groß | Das antike Weltwunder als riesige Bronzestatue an einer Hafeneinfahrt, die Schiffe fahren darunter durch. | 💡 Idee |
| 128 | Empire State Building | groß | Der Art-déco-Wolkenkratzer mit gestuften Absätzen und Spitze, gut im Maßstab 1:3. | 💡 Idee |

### Gebäude (33)

Eigene Entwürfe vom Wachturm bis zum Luftschiff.

| Nr. | Vorschlag | Größe | Beschreibung | Status |
|---|---|---|---|---|
| 28 | Windmühle | klein | Deko-Hülle für eine Bambus- oder Melonenfarm. Sieht aus wie ein Bauwerk, darin steckt eine Farm. | 💡 Idee |
| 29 | Hafen mit Steg und Bootshaus | mittel | Passt zur Villa am Wasser und zum Leuchtturm. | 💡 Idee |
| 43 | Mittelalterliche Burg | groß | Ringmauer, Torhaus, Bergfried und Burghof. | 💡 Idee |
| 44 | Wachturm | klein | Steinturm mit Holzdach und Leiter, gut für Grenzen und Wege. | 💡 Idee |
| 45 | Fachwerkdorf | mittel | Bäckerei, Schmiede und Gasthaus im Fachwerkstil. | 💡 Idee |
| 46 | Bauernhof mit Scheune und Silo | mittel | Farmen aus der Liste lassen sich darin unauffällig verstecken. | 💡 Idee |
| 47 | Blockhütte am See | klein | Rundholz, Kamin und ein kleiner Steg. | 💡 Idee |
| 48 | Baumhaus im Riesen-Dschungelbaum | mittel | Mehrere Plattformen, verbunden mit Hängebrücken. | 💡 Idee |
| 49 | Unterwasser-Glaskuppel | mittel | Eine Wohnkuppel am Meeresgrund mit Blick auf die Fische. | 💡 Idee |
| 50 | Japanisches Teehaus mit Garten | klein | Kirschbaumholz, Teich und Steinlaternen. | 💡 Idee |
| 51 | Zwergenhalle im Berg | groß | Eine große Halle mit Säulen, in den Berg gebaut statt in die Tiefe. | 💡 Idee |
| 52 | Hochhaus | groß | Moderne Glasfassade, jede Etage als eigener Bauabschnitt. | 💡 Idee |
| 53 | Rathaus mit Uhrturm am Spawn | mittel | Treffpunkt für alle, mit Hilfe-Schildern und Infotafeln. Plugin: serverhilfe (empfohlen). | 💡 Idee |
| 54 | Hängebrücke | mittel | Über eine Schlucht oder einen Fluss, mit Seilen aus Ketten oder Zäunen. | 💡 Idee |
| 55 | Gartenpavillon mit Brunnen | klein | Ein schneller Einstieg, passt zu den Villen. | 💡 Idee |
| 56 | Große Bibliothek | mittel | Bücherregale über zwei Etagen, Lesesaal und Galerie. | 💡 Idee |
| 57 | Dorfkapelle | klein | Kleiner Bau mit Glockenturm und Buntglas. | 💡 Idee |
| 58 | Luftschiff | mittel | Hülle aus Wolle, Gondel aus Holz, schwebt über dem Spawn. | 💡 Idee |
| 59 | Piratenschiff | mittel | Masten, Segel aus Wolle und ein Kanonendeck. | 💡 Idee |
| 96 | Fischerhütte mit Angelsteg | klein | Kleine Hütte am Wasser, Fässer für den Fang und ein Steg zum Angeln. | 💡 Idee |
| 105 | Weihnachtsmarkt | mittel | Buden, Tannenbäume mit Lichtern und ein Glühwein-Stand. Passt zur Adventszeit auf dem Server. | 💡 Idee |
| 106 | Winterdorf mit Iglus | klein | Iglus aus Schnee, Eisbahn und Lagerfeuer für ein Winter-Event. | 💡 Idee |
| 107 | U-Bahn-Station | mittel | Unterirdischer Bahnsteig für das Lorennetz, mit Treppen und Lichtern. | 💡 Idee |
| 108 | Wasserrad | klein | Ein Mühlrad am Bach als Deko, passt zu Fachwerkdorf und Bauernhof. | 💡 Idee |
| 109 | Marktbrunnen | klein | Ein verzierter Brunnen als Mittelpunkt für Marktplatz oder Spawn. | 💡 Idee |
| 110 | Sternwarte | mittel | Kuppel mit Fernrohr-Raum und Sternenkarte an der Wand. | 💡 Idee |
| 129 | Schwebende Insel mit Wasserfällen | groß | Eine Insel hoch über dem Spawn mit Wurzeln an der Unterseite, Wasserfällen über den Rand und einem kleinen Tempel obendrauf. | 💡 Idee |
| 130 | Vulkanfestung | groß | Eine dunkle Festung aus Schwarzstein und Basalt in einem Vulkankrater, mit Lavafällen und einer Brücke über den Lavasee. | 💡 Idee |
| 131 | Elfenstadt in Riesenbäumen | groß | Häuser auf mehreren Ebenen in riesigen eigenen Bäumen, verbunden durch Brücken, Wendeltreppen und Laternen. | 💡 Idee |
| 132 | Bergkloster an der Felswand | groß | Ein Kloster, das an einer steilen Felswand klebt, mit Treppen im Fels und Glockenturm über dem Abgrund. | 💡 Idee |
| 133 | Unterwasserstadt | groß | Mehrere Glaskuppeln am Meeresgrund, verbunden durch Tunnel, mit Gärten aus Korallen und Seetang. | 💡 Idee |
| 134 | Riesenrad | mittel | Ein großes Rad aus Ketten und Zäunen mit bunten Gondeln, als Blickfang für Marktplatz oder Hafen. | 💡 Idee |
| 135 | Staudamm | groß | Eine gewaltige Staumauer zwischen zwei Bergen, vorne Wasserfälle aus den Auslässen, oben eine Straße. | 💡 Idee |

### Anleitungen (14)

Wissen rund um Server, Farmen und Bauen.

| Nr. | Anleitung | Inhalt | Status |
|---|---|---|---|
| A1 | Redstone-Grundlagen | Beobachter, Komparator, Verstärker und Trichter-Richtungen einfach erklärt, mit Bildern. | 💡 Idee |
| A2 | Litematica einrichten | Mod installieren, Bauplan laden und die Geisterblöcke richtig ausrichten. | 💡 Idee |
| A3 | WorldEdit-Dateien einfügen | Eine .schem-Datei auf den Server laden und an der richtigen Stelle einsetzen. | 💡 Idee |
| A4 | Paper-Server einrichten | Von der Installation über die Einstellungen bis zu den ersten Plugins. | 💡 Idee |
| A5 | Bedrock-Spieler verbinden | Geyser und Floodgate einrichten, Whitelist ohne Passwort. Plugin: floodgate (benötigt). | 💡 Idee |
| A6 | Automatische Backups | Die Welt regelmäßig sichern und im Notfall zurückspielen. | 💡 Idee |
| A7 | Lag finden mit spark | Messung starten, Bericht lesen, typische Ursachen beheben. Plugin: spark (benötigt). | 💡 Idee |
| A8 | Rohstoff-Übersicht | Welche Farm liefert welches Baumaterial, und was sich nicht farmen lässt. | 💡 Idee |
| A9 | Server von außen erreichbar machen | Tunnel statt Portfreigabe, und worauf man dabei achten muss. | 💡 Idee |
| A10 | Spielerleitfaden | Regeln, wichtige Befehle und das Hilfe-Buch für neue Spieler. | 💡 Idee |
| A11 | Farmen klein halten | Überlauf-Stopp mit Komparator: Die Farm hält an, wenn das Fass halb voll ist. Plugin: fakeplayerplugin (optional). | 💡 Idee |
| A12 | Dorfbewohner-Handel verbessern | Arbeitsblöcke, Heilen von Zombie-Dorfbewohnern und bessere Preise. | 💡 Idee |
| A13 | Wahrzeichen in Blöcke umrechnen | Wie man aus echten Maßen einen Maßstab wählt, damit der Nachbau machbar bleibt. | 💡 Idee |
| A14 | Elytra finden und nutzen | Endstadt finden, Elytra reparieren, Raketen und sichere Landeplätze. | 💡 Idee |
<!-- ideen:ende -->

---

## 16. Abhängigkeiten

Alles, wovon das Projekt abhängt. Bei Updates (neue Minecraft-Version, neue Plugin-Version, neue Python-Version) diese Liste durchgehen. Die Tabelle 16.6 wird automatisch aus den Daten erzeugt (`python tools/ideen_masterplan.py`), alles andere wird von Hand gepflegt.

### 16.1 Website bauen (Python)

| Was | Version | Wofür | Wo festgelegt |
|---|---|---|---|
| Python | 3.12 | Erzeugt Website, Bauschritte, Bilder und Downloads | `.github/workflows/website.yml` |
| litemapy | 0.11.0b0 (fest) | Schreibt `.litematic`-Dateien | `tools/requirements.txt` |
| nbtlib | ≥ 2.0, < 3 | Schreibt `.schem`-Dateien (NBT) | `tools/requirements.txt` |
| Markdown | ≥ 3.5, < 4 | Anleitungen aus `docs/` in HTML umwandeln | `tools/requirements.txt` |
| Pillow | ≥ 10 | Vorschaubilder und Link-Vorschaubilder | `tools/requirements.txt` |
| DejaVu-Schriften | `fonts-dejavu-core` | Schrift in den Link-Vorschaubildern | Workflow installiert sie bei Bedarf |

Im Browser läuft die Website ohne fremde Bibliotheken: eigenes JavaScript (ES-Module) und Canvas für die 3D-Ansicht.

### 16.2 GitHub und Dienste

| Was | Wofür | Hinweis |
|---|---|---|
| GitHub-Repo `Savox76/minecraft-tools` | Quelle für alles | Änderungen direkt auf `main` |
| GitHub Actions: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4` | Website bei jedem Push und täglich neu bauen und veröffentlichen | `deploy-pages@v4` läuft bereits mit Hinweis auf Node 24; bei Gelegenheit auf neuere Versionen heben |
| GitHub Pages | Hosting unter `savox76.github.io/minecraft-tools/` | Muss in den Repo-Einstellungen auf „GitHub Actions“ stehen |
| GitHub Issues und Labels (`bauwunsch`, `plugin-wunsch`, `fehler`, `angenommen`) | Wünsche und Abstimmung mit 👍 | Workflow legt die Labels an, `tools/fetch_wishes.py` liest die Wünsche täglich |
| Google Fonts: Archivo, Atkinson Hyperlegible, JetBrains Mono | Schriften der Website | Werden vom Browser geladen; ohne Verbindung greift eine Systemschrift |
| IndexNow (`api.indexnow.org`) | Meldet neue Seiten an Bing und weitere Suchmaschinen | Schlüssel in `tools/site_config.json` |
| Google Search Console, Bing Webmaster Tools | Sichtbarkeit bei Google und Bing | Google-Code eingetragen (`tools/site_config.json`); Bing per Import aus der Search Console (siehe 14.) |

### 16.3 Lokal ansehen und testen

| Was | Wofür |
|---|---|
| `python -m http.server` | Website lokal ansehen (siehe README) |
| Playwright mit Chromium | Nur für Bildschirm-Tests beim Entwickeln, nicht im Repo und nicht im Workflow |

### 16.4 Spiel und Server

| Was | Version | Wofür |
|---|---|---|
| Minecraft Java | 1.21 oder neuer | Baupläne sind für Java geplant; Downloads werden mit Daten-Version 3953 (1.21) geschrieben und von neueren Versionen umgewandelt. Ideen mit dem Crafter brauchen mindestens 1.21 |
| Minecraft Bedrock | über Geyser und Floodgate | Bedrock-Spieler auf dem Java-Server; Baupläne mit Bedrock-Markierung lassen sich dort nachbauen |
| Paper | passend zur Minecraft-Version | Server-Software für alle Plugins |
| Java | 21 oder neuer | Paper und FakePlayerPlugin (AFKDummyForFarming bräuchte Java 25) |
| Litematica (Mod, Java) | aktuelle Version zur Minecraft-Version | Öffnet die `.litematic`-Downloads als Geisterblöcke |
| WorldEdit oder FastAsyncWorldEdit | aktuelle Version | Fügt die `.schem`-Downloads auf dem Server ein |

### 16.5 Plugins untereinander

Laut Dokumentation der eigenen Plugins. Ob es harte Abhängigkeiten sind (Plugin startet sonst nicht) oder weiche (Funktion fällt nur weg), wird geprüft, sobald der Quellcode im Repo ist (Phase 4).

| Plugin | Braucht oder nutzt | Wofür |
|---|---|---|
| Alle eigenen Plugins | Paper | Laufen nur auf Paper |
| Arbeiter | ServerShop | Arbeiter werden mit Coins gekauft; Händler öffnen den Shop einer Kategorie |
| Arbeiter | InfiniteLager | Arbeiter können in das private Lager ihres Besitzers liefern |
| Arbeiter | FakePlayerPlugin oder ChunkLoader (empfohlen) | Arbeiter arbeiten nur in geladenen Chunks |
| ServerHilfe | alle eigenen Plugins (nur Texte) | Das Hilfe-Buch erklärt Shop, Lager, Arbeiter und Farm-Bot; bei neuen Befehlen die Texte anpassen |
| Floodgate | Geyser | Floodgate lässt Bedrock-Spieler ohne Java-Konto herein; die Verbindung selbst stellt Geyser her. Geyser fehlt noch in der Liste der fremden Plugins |
| EasyCommandBlocker | Befehle aller Plugins | Die Liste der für Spieler sichtbaren Befehle muss bei neuen Befehlen ergänzt werden |

### 16.6 Baupläne und Ideen brauchen Plugins

Wird aus `plugins` in `builds/*/build.json` und `ideen/ideen.json` erzeugt.

<!-- abhaengigkeiten:start -->
| Plugin | Benötigt von | Empfohlen für | Optional bei |
|---|---|---|---|
| Arbeiter (eigenes) | Idee Nr. 69 Holzkohle-Station | – | Idee Nr. 8 Kleine Handelshalle, Idee Nr. 117 Große Handelshalle, Idee Nr. 118 Große Handelshalle im Stil einer Zauberschule |
| FakePlayerPlugin (fremdes) | Idee Nr. 87 Farm-Bot-Zentrale | Bauplan Gewächshaus-Farm, Idee Nr. 1 Kaktus-XP-Farm mit Ofenbatterie, Idee Nr. 3 Dunkelraum-Monsterfarm, Idee Nr. 4 Spawner-XP-Farm, Idee Nr. 5 Lohenfarm, Idee Nr. 9 Kleine Bambusfarm, Idee Nr. 10 Große Bambusfarm, Idee Nr. 150 Große Kaktusfarm, Idee Nr. 12 Melonen- und Kürbisfarm, Idee Nr. 15 Eisenfarm, Idee Nr. 60 Zuckerrohrfarm, Idee Nr. 61 Kakaofarm, Idee Nr. 22 Schleimfarm, Idee Nr. 23 Hexenfarm, Idee Nr. 24 Creeperfarm | Idee Nr. A11 Farmen klein halten |
| Floodgate (fremdes) | Idee Nr. A5 Bedrock-Spieler verbinden | – | – |
| InfiniteLager (eigenes) | Idee Nr. 88 Lagerhalle mit Einlagern-Truhen | – | Bauplan Kellerlager |
| ServerHilfe (eigenes) | – | Idee Nr. 53 Rathaus mit Uhrturm am Spawn | – |
| ServerShop (eigenes) | Idee Nr. 26 Marktplatz für Spieler-Shops | – | – |
| spark (fremdes) | Idee Nr. A7 Lag finden mit spark | – | – |

Ohne Plugin (reines Minecraft): Eiffelturm, Leuchtturm, Villa am Wasser, Gründerzeit-Villa, Mediterrane Villa, Moderne Villa.
<!-- abhaengigkeiten:ende -->
