# Bauwerkstatt · minecraft-tools

Minecraft-Baupläne im LEGO-Stil und Plugins für Paper-Server, kostenlos und einzeln herunterladbar.

**Website:** <https://savox76.github.io/minecraft-tools/> · English: <https://savox76.github.io/minecraft-tools/en/>

| Ordner | Inhalt |
|---|---|
| [`builds/`](builds/) | Baupläne: Beschreibung und Blöcke. Website, LEGO-Schritte und Downloads entstehen daraus automatisch |
| [`plugins/eigene/`](plugins/eigene/) | Eigene Paper-Plugins mit Dokumentation |
| [`plugins/fremd/`](plugins/fremd/) | Plugins anderer Entwickler, die auf dem Server laufen oder empfohlen werden |
| [`docs/`](docs/) | Anleitungen (Farm-Bot, CoreProtect), englisch in `docs/en/` |
| [`ideen/`](ideen/) | Geplante Baupläne und Anleitungen mit Kurztext, Quelle der Seite „Geplant“ |
| [`site/`](site/) | Die Website |
| [`tools/`](tools/) | Erzeugt Website-Daten, LEGO-Schritte, `.litematic`, `.schem` und Teilelisten |

Wünsche für neue Baupläne oder Plugins: [Issue anlegen](https://github.com/Savox76/minecraft-tools/issues/new/choose).

Wie es weitergeht, steht im [Masterplan](MASTERPLAN.md).

## Lokal ansehen

```
pip install -r tools/requirements.txt
SITE_URL=http://localhost:8000/ python tools/build_site.py
python -m http.server -d _site 8000
```

Dann <http://localhost:8000> öffnen.

---

Kein offizielles Minecraft-Produkt. Nicht von Mojang oder Microsoft genehmigt oder mit ihnen verbunden.
