# Baupläne

Jeder Ordner hier ist ein Bauplan. Die Website, die LEGO-Schritte und alle Downloads entstehen automatisch daraus, sobald ein Ordner auf `main` landet.

## Aufbau eines Bauplans

```
builds/<id>/
├─ build.json   Name, Beschreibung, Kategorie, Abschnitte, Tipps, Rohstoffe
└─ model.json   die Blöcke, Ebene für Ebene
```

### `build.json`

| Feld | Bedeutung |
|---|---|
| `id` | gleich dem Ordnernamen, nur Kleinbuchstaben und Bindestriche |
| `titel`, `beschreibung` | Anzeige auf der Website |
| `kategorie` | `tuerme`, `villen` oder `technik` |
| `tags` | Stichworte |
| `edition` | `java` und/oder `bedrock` |
| `schwierigkeit` | 1 (leicht) bis 5 (Profi) |
| `bauzeit_stunden` | `[von, bis]` |
| `grundflaeche`, `massstab` | Text für die Kenndaten |
| `status` | `entwurf` (Blockrichtungen ungeprüft) oder `geprueft` |
| `hinweis` | wird bei Entwürfen angezeigt |
| `ansicht.schnitt` | `true` blendet in der 3D-Ansicht Decke und vordere Wände aus (für Keller) |
| `abschnitte` | Bauabschnitte mit `name`, `von`, `bis` (Ebenen) und `text`. Die LEGO-Schritte werden innerhalb der Abschnitte gebildet |
| `tipps` | Liste aus `titel` und `text` |
| `rohstoffe` | was die Farmen liefern müssen: `name`, `menge`, `quelle`, `hinweis` |
| `schmelzvorgaenge` | Anzahl Ofen-Vorgänge |
| `version`, `autor` | Versionsnummer und Name |

### `model.json`

- `size`: Breite `x` (Osten), Höhe `y`, Tiefe `z` (Süden)
- `palette`: ein Eintrag pro Blocksorte
  - `key`: ein Buchstabe, der in den Ebenen benutzt wird
  - `name`: deutscher Name auf der Website
  - `block`: Minecraft-ID mit Zustand, z. B. `minecraft:oak_door[half=upper]`
  - `color`: Farbe in der Darstellung
  - `flags` (optional): `vorhanden` (Gelände, wird nicht gebaut), `kein-block` (z. B. Dorfbewohner), `zweiter-teil` (obere Türhälfte, Kopfteil vom Bett: zählt nicht in der Teileliste)
- `layers`: Ebene 0 zuerst. Jede Ebene ist eine Liste von Zeilen von Norden nach Süden, jede Zeile ein Text von Westen nach Osten. `.` steht für Luft.

## Was automatisch entsteht

- LEGO-Schritte mit höchstens 60 neuen Blöcken pro Schritt
- Teileliste mit Stacks
- Downloads: `.litematic` (Litematica), `.schem` (WorldEdit), `teileliste.csv`

## Neuen Bauplan hinzufügen

1. Ordner `builds/<id>/` mit `build.json` und `model.json` anlegen.
2. Lokal prüfen: `pip install -r tools/requirements.txt` und dann `python tools/build_site.py`. Die Ausgabe nennt Blöcke und Schritte.
3. Auf `main` pushen. Die Website wird automatisch neu gebaut.
