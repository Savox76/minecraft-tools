# Masterplan: minecraft-tools

Arbeitstitel: **Savox Bauwerkstatt**. Eine Sammlung von Minecraft-Bauanleitungen und Server-Plugins für Kreative, kostenlos und einzeln herunterladbar.

Stand: 01.11.2026 · Website: <https://savox76.github.io/minecraft-tools/>

---

## 0. Aktueller Stand

| Bereich | Status | Wo |
|---|---|---|
| 8 Baupläne | ✅ **verfügbar** als Entwurf: LEGO-Schritte, Teileliste, `.litematic`, `.schem`, CSV | [`builds/`](builds/) |
| 7 eigene Plugins | 🟡 **Doku verfügbar**, Quellcode und `.jar` integrierbar, sobald der Quellcode vorliegt | [`plugins/eigene/`](plugins/eigene/) |
| Fremde Plugins | 🟡 **vorläufige Liste** (7) aus den Server-Notizen, wird mit der vollständigen Liste ergänzt | [`plugins/fremd/plugins.json`](plugins/fremd/plugins.json) |
| 2 Anleitungen | ✅ verfügbar (Farm-Bot, CoreProtect) | [`docs/`](docs/) |
| Website | ✅ automatisch per GitHub Actions auf GitHub Pages, **Deutsch und Englisch**, Hell/Dunkel/Automatisch, suchmaschinenfreundlich (siehe 14.) | [`site/`](site/), [`tools/build_site.py`](tools/build_site.py), [`tools/seiten.py`](tools/seiten.py) |
| Ideen für neue Inhalte | 💡 91 Bauplan-Vorschläge (Farmen, Gebäude, Monumente, Produktionen, Funktionales) und 10 Anleitungen | Abschnitt 15 |
| Bauwünsche | ✅ Issue-Formulare, Wunschliste täglich auf der Website | [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) |

**Entwurf** heißt: Die Richtung von Treppen, Türen und Trichtern ist in den Dateien noch nicht in einer Testwelt geprüft (siehe Phase 1).

### Feste Regeln

- **Jeder neue Bauplan kommt ins Repo** als Ordner `builds/<id>/` (Format in [`builds/README.md`](builds/README.md)). Website, LEGO-Schritte, Teileliste und Downloads entstehen daraus automatisch. Er erscheint also überall, ohne dass sonst etwas angepasst werden muss.
- **Eigene und fremde Plugins bleiben getrennt.** Eigene Plugins bekommen `plugins/eigene/<id>/plugin.json` und `README.md`, fremde einen Eintrag in `plugins/fremd/plugins.json` (nur Beschreibung, Einsatz und Link zur offiziellen Seite, keine Dateien). Die Website zeigt beides automatisch in getrennten Bereichen.
- **Änderungen gehen direkt auf `main`.**
- **Alles zweisprachig:** Neue Baupläne, Plugins und Anleitungen bekommen eine englische Fassung (`"en"` in `build.json` und `plugin.json`, `docs/en/<id>.md`, neue Blocknamen in `tools/i18n/bloecke_en.json`). Fehlt sie, zeigt die englische Seite den deutschen Text und der Build gibt einen Hinweis aus.
- **Keine erzeugten Dateien im Repo:** Website, `.litematic`, `.schem`, `.jar` und PDFs baut GitHub Actions bei jedem Push neu.

---

## 1. Ziel

- **Alle Baupläne** (Türme, Villen, Farmen, Technik) als Schritt-für-Schritt-Anleitungen im **LEGO-Stil**: Zu jedem Schritt ist sofort klar, welche Blöcke in welcher Menge gebraucht werden.
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

## 4. Das LEGO-Prinzip

So sieht eine Bauanleitung aus:

1. **Deckblatt:** Bild des fertigen Bauwerks, Name, Größe, Schwierigkeit, Bauzeit, Java/Bedrock.
2. **Gesamt-Teileliste:** alle Blöcke mit Bild und Anzahl, zusätzlich in Stacks (z. B. „12 St. + 30“). Darunter die Rohstoffe aus Farmen, zum Beispiel „1.050 Sand = Glas und Beton“.
3. **Bauschritte, nummeriert, einer pro Seite:** siehe den festen Ablauf in 4.1
4. **Unterbaugruppen** wie bei LEGO: Teile, die mehrfach vorkommen (Palme, Fenster-Modul, Laternenpfahl), werden einmal gezeigt und mit **„2 ×“** markiert.
5. **Schritt-Regeln:** Ebene für Ebene, höchstens 60 neue Blöcke pro Schritt (Einzelheiten in 4.1). Die Schritte entstehen automatisch.
6. **Ausgaben pro Bauplan:**
   - Web-Ansicht zum Durchblättern, auf dem Handy wischbar
   - druckbares **PDF-Heft** im selben Look
   - Teileliste als **CSV**
   - Bauplan-Dateien zum direkten Einfügen ins Spiel (siehe 6.)
7. **Baufortschritt:** Erledigte Schritte lassen sich abhaken. Der Stand wird im Browser gespeichert.

### 4.1 Fester Ablauf jedes Bauplans (gilt auch für alle neuen)

Jeder Bauplan wird **Ebene für Ebene von unten nach oben** gebaut. Dieser Ablauf entsteht automatisch aus `model.json` (`tools/build_site.py`, Funktion `lego_schritte`); für einen neuen Bauplan muss dafür nichts von Hand eingestellt werden.

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
| Neue Teile | Kasten wie bei LEGO: Block-Bild, „× 12“, Name |
| Abschnitt | „Ebene 1 · Teil 3 von 5“, Name und Text des Bauabschnitts |
| Steuerung | Zurück/Weiter, Schieberegler, Pfeiltasten, „Schritt erledigt“ mit Fortschrittsbalken (im Browser gespeichert) |

Dazu gibt es pro Bauplan die Reiter **Teileliste** (gesamt, mit Stacks und Rohstoffen), **Ebenen** (jede Ebene einzeln als Draufsicht) und **Downloads** (`.litematic`, `.schem`, CSV).

**Checkliste für einen neuen Bauplan**

- [ ] `builds/<id>/model.json`: Ebene 0 ist der Boden, jede weitere Ebene liegt genau einen Block höher. Gelände mit `vorhanden` markieren, obere Türhälften und Bett-Kopfteile mit `zweiter-teil`.
- [ ] `builds/<id>/build.json`: `abschnitte` mit `von`/`bis` passend zu den Ebenen, dazu Tipps, Rohstoffe und die englische Fassung unter `en`.
- [ ] Neue Blocknamen in `tools/i18n/bloecke_en.json` eintragen.
- [ ] Lokal bauen (`python tools/build_site.py`) und in der Ausgabe Blöcke und Schritte prüfen. Danach im Browser einmal alle Schritte durchklicken und die Draufsicht ansehen.
- [ ] Auf `main` pushen. Website, Schritte, Bilder und Downloads entstehen automatisch.

**Wichtige Änderung gegenüber heute:** Die bisherigen Modelle kennen keine **Blockrichtungen** (wohin eine Treppe zeigt, obere oder untere Stufe). Für echte LEGO-Genauigkeit wird jeder Bau einmal in einer Kreativ-Testwelt nachgebaut oder geprüft und als `.litematic` exportiert. Diese Datei ist ab dann die Quelle für alles andere. Dabei wird jeder Bauplan automatisch einmal real getestet.

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
- [x] Automatische Schritt-Aufteilung nach den LEGO-Regeln aus 4.
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
- [x] Bauplan-Seite: Kenndaten, Teileliste, Schritt-Ansicht im LEGO-Stil, 3D drehbar, Ebenen-Ansicht, Download-Knöpfe
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

### Phase 3 · LEGO-PDF-Hefte (1 Sitzung)
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
- **Geplant-Seite:** die Ideen aus Abschnitt 15 auf der Website zeigen, damit Besucher sehen, was kommt, und mit abstimmen können
- **Server-Setup-Assistent:** Paper, Plugins, Bot und Einstellungen in einem geführten Ablauf (Desktop-App)

---

## 12. Offene Entscheidungen

| # | Frage | Mein Vorschlag |
|---|---|---|
| 1 | Name des Projekts | „Savox Bauwerkstatt“ |
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

- [ ] **Google Search Console:** <https://search.google.com/search-console> → Property hinzufügen → **URL-Präfix** `https://savox76.github.io/minecraft-tools/` → Bestätigung per **HTML-Tag**. Den Code aus `content="…"` in [`tools/site_config.json`](tools/site_config.json) bei `google_site_verification` eintragen (oder mir schicken), pushen, ein paar Minuten warten, dann „Bestätigen“ klicken.
- [ ] Danach in der Search Console unter **Sitemaps** `sitemap.xml` einreichen.
- [ ] **Bing Webmaster Tools:** <https://www.bing.com/webmasters> → „Aus Google Search Console importieren“. Bing beliefert auch DuckDuckGo und Ecosia.
- [ ] **GitHub-Repo:** Auf der Repo-Seite rechts bei „About“ das Zahnrad → Website `https://savox76.github.io/minecraft-tools/` eintragen, Topics: `minecraft`, `minecraft-schematics`, `litematica`, `worldedit`, `paper-plugin`, `minecraft-plugin`.

### Bekannt machen (Links von außen)

Suchmaschinen bewerten eine Seite auch danach, wer auf sie verlinkt.

- **Planet Minecraft** (planetminecraft.com): die größte Seite für Baupläne. Jeden Bauplan mit Bild und `.litematic` hochladen und auf die LEGO-Anleitung verlinken.
- **Modrinth und Hangar:** sobald die Plugins als `.jar` fertig sind (Phase 4), dort veröffentlichen und die Website als Homepage angeben.
- **Reddit:** r/Minecraft, r/MinecraftBuilds, r/admincraft (für die Plugins), deutschsprachig r/minecraftDE. Am besten mit einem Bild oder GIF der Schritt-Animation.
- **Savox-Kanäle:** Zeitraffer eines Baus als Short oder TikTok mit Link zum Bauplan.
- **Discord:** Minecraft-Bau- und Server-Admin-Communities.

### Wichtig zu wissen

- Eine neue Seite braucht meist einige Tage bis wenige Wochen, bis sie bei Google erscheint. Die Search Console zeigt, welche Seiten schon aufgenommen sind.
- `robots.txt` wird von Suchmaschinen nur direkt auf `savox76.github.io/` gelesen, nicht im Unterordner. Deshalb ist das Einreichen der Sitemap in der Search Console der wichtige Weg.
- Mit einer eigenen Domain (Masterplan 12., Punkt 8) wäre die Seite unabhängig von GitHub und leichter zu merken. Dann nur `site_url` in `tools/site_config.json` ändern.

---

## 15. Ideen-Speicher: mögliche neue Baupläne

Vorschläge für künftige Baupläne. Wird einer umgesetzt, bekommt er einen Ordner `builds/<id>/` und folgt dem Ablauf aus 4.1. Status: 💡 Idee · 🔨 in Arbeit · ✅ als Bauplan verfügbar. Größe: klein (bis etwa 15 × 15), mittel, groß.

**Hinweis zu Paper:** Farmen, die Sand, TNT oder Teppiche vervielfältigen, laufen auf Paper normalerweise nicht und stehen deshalb nicht auf der Liste. Bäume fällt am besten der Holzfäller aus dem Arbeiter-Plugin. Monsterfarmen laufen nur, wenn ein Spieler oder der Farm-Bot in der Nähe ist.

### 15.1 Farmen und Technik

| Nr. | Vorschlag | Größe | Was es bringt | Status |
|---|---|---|---|---|
| 1 | Kaktus-XP-Farm mit Ofenbatterie | klein | Kaktus → grüner Farbstoff, 1 XP pro Stück, XP sammelt sich im Ofen. Ohne Monster | 💡 |
| 2 | Seetang-XP-Ofen | klein | Weniger XP, dafür getrockneter Seetang als Brennstoff | 💡 |
| 3 | Dunkelraum-Monsterfarm | mittel | XP, Knochen, Pfeile, Schießpulver, Fäden | 💡 |
| 4 | Spawner-XP-Farm (Zombie/Skelett) | klein | Viel XP, nur an einem gefundenen Spawner | 💡 |
| 5 | Lohenfarm | mittel | XP und Lohenruten, an einer Netherfestung | 💡 |
| 6 | Goldfarm auf dem Nether-Dach | groß | Sehr viel XP und Gold | 💡 |
| 7 | Endermanfarm im End | groß | Schnellste XP-Quelle, Drache muss besiegt sein | 💡 |
| 8 | Handelshalle mit Dorfbewohnern | mittel | XP, Smaragde, Verzauberungsbücher; passt zum Arbeiter-Plugin | 💡 |
| 9 | Kleine Bambusfarm | klein | 8 Pflanzen, Beobachter und Kolben, Trichter; etwa 8 × 4 | 💡 |
| 10 | Große Bambusfarm | groß | 2 × 16 Pflanzen, Trichterlore unter Glas, Fasskette | 💡 |
| 11 | Bambus-Brennstoffstation | klein | Bambus heizt die Ofenbatterie aus Nr. 1 ohne Kohle | 💡 |
| 12 | Melonen- und Kürbisfarm | klein | Beobachter und Kolben ernten automatisch | 💡 |
| 13 | Wollfarm | klein | Schafe, Werfer mit Schere; eine Farbe pro Kammer | 💡 |
| 14 | Honig- und Waben-Farm | klein | Honigblöcke, Waben für Kerzen | 💡 |
| 15 | Eisenfarm | mittel | Eisen für Trichter, Schienen, Laternen | 💡 |
| 16 | Schneefarm mit Schneegolems | klein | Schneeblöcke und Eis | 💡 |
| 17 | Lava aus Tropfstein | klein | Unendlich Lava im Kessel als Brennstoff | 💡 |
| 18 | Basalt-Generator | klein | Lava, Blaueis, Seelenerde → Basalt | 💡 |
| 19 | Bruchstein-Generator | klein | Lava und Wasser, nur noch abbauen | 💡 |
| 20 | Moosfarm | klein | Moos, Azaleen, Kompost per Knochenmehl-Werfer | 💡 |
| 21 | Kuh- und Hühnerfarm | klein | Leder für Bücher, Federn, Eier, Fleisch | 💡 |
| 22 | Schleimfarm | mittel | Schleimbälle für Klebekolben | 💡 |
| 23 | Hexenfarm | groß | Redstone, Leuchtsteinstaub, Zucker | 💡 |
| 24 | Creeperfarm | mittel | Schießpulver für Raketen | 💡 |
| 25 | Verzauberungsraum | klein | Zaubertisch mit 15 Bücherregalen, Amboss, Schleifstein | 💡 |
| 26 | Marktplatz für Spieler-Shops | mittel | Stände für die Shop-Truhen aus ServerShop | 💡 |
| 27 | Lorenbahnhof | mittel | Gleise vom Spawn zu allen Farmen | 💡 |
| 28 | Windmühle | klein | Deko-Hülle für eine Bambus- oder Melonenfarm | 💡 |
| 29 | Hafen mit Steg und Bootshaus | mittel | Passt zu Villa am Wasser und Leuchtturm | 💡 |

Empfohlener Start: Nr. 1, 9 und 11 als Kreislauf (Bambus heizt die Öfen, Kaktus liefert XP und Farbstoff).

### 15.2 Gebäude und Monumente

| Nr. | Vorschlag | Größe | Besonderheit | Status |
|---|---|---|---|---|
| 30 | Brandenburger Tor | mittel | Säulen, Quadriga aus Kupfer und Stein | 💡 |
| 31 | Big Ben (Elizabeth Tower) | groß | Uhrturm mit vier Zifferblättern, gut im Maßstab 1:2 | 💡 |
| 32 | Kölner Dom | groß | Zwei Türme, Spitzbögen, bunte Glasfenster | 💡 |
| 33 | Frauenkirche Dresden | groß | Steinerne Glockenkuppel aus Sandstein | 💡 |
| 34 | Freiheitsstatue | groß | Aus Kupfer, das von selbst grün wird | 💡 |
| 35 | Schiefer Turm von Pisa | mittel | Schräge durch versetzte Ringe, Säulengänge | 💡 |
| 36 | Kolosseum | groß | Ovale Arena mit Bögen, teilweise eingestürzt | 💡 |
| 37 | Schloss Neuschwanstein | groß | Türme, Spitzdächer, auf einem Felsen | 💡 |
| 38 | Tower Bridge | groß | Zwei Türme mit Klappbrücke (Kolben möglich) | 💡 |
| 39 | Pyramide mit Grabkammer | groß | Viel Sandstein; Sand ist auf Paper nicht farmbar | 💡 |
| 40 | Japanische Pagode | mittel | Fünf Stockwerke, geschwungene Dächer | 💡 |
| 41 | Maya-Tempel | mittel | Stufenpyramide mit Treppe, Dschungel-Deko | 💡 |
| 42 | Stonehenge | klein | Steinkreis, gut als erstes Monument | 💡 |
| 43 | Mittelalterliche Burg | groß | Ringmauer, Torhaus, Bergfried, Burghof | 💡 |
| 44 | Wachturm | klein | Steinturm mit Holzdach und Leiter | 💡 |
| 45 | Fachwerkdorf | mittel | Bäckerei, Schmiede und Gasthaus | 💡 |
| 46 | Bauernhof mit Scheune und Silo | mittel | Farmen aus 15.1 lassen sich darin verstecken | 💡 |
| 47 | Blockhütte am See | klein | Rundholz, Kamin, Steg | 💡 |
| 48 | Baumhaus im Riesen-Dschungelbaum | mittel | Mehrere Plattformen mit Hängebrücken | 💡 |
| 49 | Unterwasser-Glaskuppel | mittel | Wohnkuppel am Meeresgrund, viel Glas | 💡 |
| 50 | Japanisches Teehaus mit Garten | klein | Kirschbaumholz, Teich, Steinlaternen | 💡 |
| 51 | Zwergenhalle im Berg | groß | Große Halle mit Säulen, in den Berg gebaut statt in die Tiefe | 💡 |
| 52 | Hochhaus | groß | Moderne Glasfassade, Etagen einzeln baubar | 💡 |
| 53 | Rathaus mit Uhrturm am Spawn | mittel | Hilfe-Schilder, Treffpunkt für alle | 💡 |
| 54 | Hängebrücke | mittel | Über eine Schlucht oder einen Fluss | 💡 |
| 55 | Gartenpavillon mit Brunnen | klein | Schneller Einstieg, passt zu den Villen | 💡 |
| 56 | Große Bibliothek | mittel | Bücherregale über zwei Etagen, Lesesaal | 💡 |
| 57 | Dorfkapelle | klein | Glockenturm, Buntglas | 💡 |
| 58 | Luftschiff | mittel | Hülle aus Wolle, Gondel aus Holz | 💡 |
| 59 | Piratenschiff | mittel | Masten, Segel aus Wolle, Kanonendeck | 💡 |

Für Nachbauten echter Wahrzeichen wird der Maßstab im Bauplan angegeben (wie beim Eiffelturm 1:3), damit Höhe und Blockzahl realistisch bleiben.

### 15.3 Weitere Produktionen

| Nr. | Vorschlag | Größe | Was es bringt | Status |
|---|---|---|---|---|
| 60 | Zuckerrohrfarm | klein | Papier für Bücher, Karten und Raketen | 💡 |
| 61 | Kakaofarm | klein | Beobachter und Kolben ernten Kakaobohnen am Tropenbaumstamm: Kekse, brauner Farbstoff | 💡 |
| 62 | Blumenfarm | klein | Knochenmehl-Werfer auf Gras, alle Grundfarben für Wolle, Beton und Glas | 💡 |
| 63 | Komposter-Kette | klein | Überschuss aus Bambus, Kaktus und Seetang wird zu Knochenmehl | 💡 |
| 64 | Tonfarm | mittel | Werfer mit Wasserflaschen machen Erde zu Schlamm, Tropfstein darunter macht daraus Ton: Terrakotta, Ziegel | 💡 |
| 65 | Froschlicht-Farm | groß | Frösche fressen kleine Magmawürfel: Leuchtblöcke in drei Farben | 💡 |
| 66 | Amethyst-Farm | mittel | An einer gefundenen Geode, Beobachter und Kolben: Amethyst für Fernrohr und getöntes Glas | 💡 |
| 67 | Chorusfrucht-Farm im End | mittel | Halbautomatisch: Purpurblöcke zum Bauen | 💡 |
| 68 | Pilzfarm | klein | Dunkler Raum: Pilze für Suppen und Riesenpilz-Deko | 💡 |
| 69 | Holzkohle-Station | klein | Stämme vom Holzfäller-Arbeiter werden zu Holzkohle | 💡 |
| 70 | Erz-Schmelzstation | mittel | Einwurftruhe, viele Öfen gleichzeitig, sortierte Ausgabe | 💡 |
| 71 | Automatische Werkbank (Crafter) | mittel | Seit 1.21: stellt z. B. Brot, Papier oder Eisenblöcke selbst her | 💡 |
| 72 | Raketen-Fabrik | mittel | Papier und Schießpulver per Crafter: Raketen für Elytra-Flüge | 💡 |
| 73 | Automatische Brauerei | mittel | Braustände mit Trichtern, Tränke in Serie | 💡 |
| 74 | Automatische Küche | klein | Räucheröfen mit Trichtern, gefüttert aus Kuh- und Hühnerfarm | 💡 |
| 75 | Buch-Station | mittel | Zuckerrohr und Leder werden zu Büchern und Bücherregalen | 💡 |

### 15.4 Funktionale Bauten

| Nr. | Vorschlag | Größe | Wozu | Status |
|---|---|---|---|---|
| 76 | Blasen-Aufzug | klein | Seelensand hoch, Magmablock runter, als eigener Bauplan zum Einbauen | 💡 |
| 77 | Item-Aufzug | klein | Blasensäule hebt Gegenstände vom Keller ins Lager | 💡 |
| 78 | Versteckte Kolbentür 2 × 2 | klein | Öffnet per Knopf oder Druckplatte, verschwindet in der Wand | 💡 |
| 79 | Geheimgang hinter Bücherregal | klein | Klassischer Geheimeingang zum Lager | 💡 |
| 80 | Tresor mit Zahlenschloss | mittel | Redstone-Kombinationsschloss mit Hebeln | 💡 |
| 81 | Automatisches Licht | klein | Tageslichtsensor schaltet Redstone-Lampen ab Abend ein | 💡 |
| 82 | Zugbrücke | mittel | Kolben fahren die Brücke ein, passt zur Burg | 💡 |
| 83 | Leuchtfeuer-Pyramide | mittel | Eisenblöcke aus der Eisenfarm, Effekte wie Eile beim Abbauen | 💡 |
| 84 | Aquisitor-Rahmen | klein | Atmen unter Wasser rund um die Glaskuppel | 💡 |
| 85 | Nether-Knotenpunkt | groß | Portale zu allen Basen, Eisstraße für schnelle Bootsfahrten | 💡 |
| 86 | Kartenraum | mittel | Karten in Rahmen ergeben eine Wandkarte der Welt | 💡 |
| 87 | Farm-Bot-Zentrale | klein | Sicherer, beleuchteter Raum für den Bot mitten zwischen den Farmen | 💡 |
| 88 | Lagerhalle mit Einlagern-Truhen | mittel | Für das InfiniteLager-Plugin, gemeinsam und privat getrennt | 💡 |
| 89 | Werkstatt | klein | Amboss, Schleifstein, Schmiedetisch, Webstuhl und Steinsäge an einem Ort | 💡 |
| 90 | Ausrüstungsraum | klein | Rüstungsständer, Waffen und Werkzeuge geordnet | 💡 |
| 91 | Beleuchteter Spawn | mittel | Laternen-Raster, damit am Spawn keine Monster entstehen | 💡 |

### 15.5 Ideen für Anleitungen

| Nr. | Anleitung | Inhalt | Status |
|---|---|---|---|
| A1 | Redstone-Grundlagen | Beobachter, Komparator, Verstärker und Trichter-Richtungen einfach erklärt | 💡 |
| A2 | Litematica einrichten | Mod installieren, Bauplan laden, Geisterblöcke ausrichten | 💡 |
| A3 | WorldEdit-Dateien einfügen | `.schem` auf den Server laden und an der richtigen Stelle einsetzen | 💡 |
| A4 | Paper-Server einrichten | Von der Installation bis zu den ersten Plugins | 💡 |
| A5 | Bedrock-Spieler verbinden | Geyser und Floodgate, Whitelist ohne Passwort | 💡 |
| A6 | Automatische Backups | Welt regelmäßig sichern und im Notfall zurückspielen | 💡 |
| A7 | Lag finden mit spark | Messung starten, Bericht lesen, typische Ursachen | 💡 |
| A8 | Rohstoff-Übersicht | Welche Farm liefert welches Baumaterial, und was sich nicht farmen lässt | 💡 |
| A9 | Server von außen erreichbar machen | Tunnel statt Portfreigabe, worauf man achten muss | 💡 |
| A10 | Spielerleitfaden | Regeln, wichtige Befehle und Hilfe-Buch für neue Spieler | 💡 |
