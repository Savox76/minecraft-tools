---
titel: Farm-Bot für Paper-Server
kurz: Farmen laufen weiter, auch Pflanzenwachstum und Spawning, wenn niemand online ist.
reihenfolge: 1
---

# Farm-Bot für Paper-Server

Ziel: Die Farmen laufen stetig weiter, auch Pflanzenwachstum und Mob-Spawning, wenn niemand online ist. Die Farmen bleiben dabei klein.

Wir nutzen das **FakePlayerPlugin**. Paper bleibt, alle anderen Plugins bleiben.

## Warum ein Bot nötig ist

- Pflanzen wachsen nur, wenn ihr Chunk geladen ist **und** ein Spieler höchstens **128 Blöcke** entfernt ist. Dasselbe gilt für Mob-Spawning.
- `/forceload` allein reicht dafür nicht. Damit laufen nur Trichter, Öfen, Redstone, Dorfbewohner und Eisenfarmen.
- Der Bot des FakePlayerPlugin ist eine vollständige Spielerfigur in der Welt. Er steht in der Tab-Liste und in der Spielerzahl wie ein echter Spieler.

## 1. Vorbereitung

1. **Server-Version prüfen:** In der Server-Konsole `version` eingeben.
2. **Java-Version prüfen:** Das Plugin braucht **Java 21** oder neuer. Prüfen mit `java -version`.
3. **Backup:** Server stoppen und den kompletten Server-Ordner kopieren.

## 2. Plugin installieren

1. Hangar öffnen: <https://hangar.papermc.io/Janky-Development/FakePlayerPlugin>
2. Im Reiter **„Versions“** die Datei wählen, die zu deiner Server-Version passt.
3. Die `.jar` in den Ordner `plugins` legen.
4. Server starten und in der Konsole prüfen, dass das Plugin ohne Fehler geladen wurde.

## 3. Bot einrichten

1. Einen **sicheren Platz** in der Mitte deiner Farmen bauen: rundum geschlossen und gut beleuchtet.
2. Dort hinstellen und den Bot erzeugen:
   ```
   /fpp spawn --name Farmbot
   ```
3. Den Bot festsetzen, damit er nicht weggeschoben wird:
   ```
   /fpp freeze Farmbot on
   ```
4. Fake-Nachrichten abschalten, sonst schreibt der Bot zufällige Chat-Nachrichten:
   ```
   /fpp chat off
   ```
5. Kontrolle: `/fpp list` zeigt alle Bots mit Ort und Laufzeit.

Der Bot bleibt nach einem Server-Neustart erhalten und kehrt an seinen Platz zurück.

| Befehl | Wirkung |
|---|---|
| `/fpp despawn Farmbot` | Bot entfernen |
| `/fpp freeze Farmbot off` | Bot wieder freigeben |
| `/fpp stats` | Bots und Server-Leistung (TPS) anzeigen |
| `/fpp reload` | Config neu laden |

## 4. Zuckerrohr-Test

Das Plugin sagt nicht ausdrücklich, dass der Bot auch das Pflanzenwachstum auslöst. Deshalb einmal testen:

1. Neben dem Bot 5 frisch gepflanzte Zuckerrohre mit Wasser daneben setzen.
2. Ausloggen und 30 bis 60 Minuten warten.
3. Wieder einloggen: Sind die Zuckerrohre gewachsen, funktioniert alles.

## 5. Server-Einstellungen

`server.properties`:

```
simulation-distance=6
pause-when-empty-seconds=0
```

- `simulation-distance=6` simuliert etwa 96 Blöcke um Spieler und Bot. Mit dem Plugin [ServerEinstellungen](#/plugin/servereinstellungen) geht das auch im Spiel: `/einstellungen reichweite 6`.
- `pause-when-empty-seconds`: Seit 1.21.2 pausiert der Server, wenn 60 Sekunden niemand online ist. Der Wert 0 soll das abschalten. Erscheint nach dem Ausloggen trotzdem „Server empty for 60 seconds, pausing“ in der Konsole, wirkt die Einstellung nicht.

Spielregel gegen Phantome, weil der Bot nie schläft:

```
/gamerule doInsomnia false
```

`randomTickSpeed` bleibt auf 3, sonst wächst alles schneller als gewollt.

Laptop als Server: Energiesparmodus und Ruhezustand auf „Nie“, „Deckel zuklappen“ auf „Nichts unternehmen“.

## 6. Standort und Größe

- Bot ins **Zentrum** stellen, alle Farmen in höchstens **80 Blöcken** Abstand.
- **Mini-Farmen:** Gewächshaus 7 × 7 oder 9 × 9, Zuckerrohr eine Reihe à 8, Seetang 6 bis 8 Säulen.
- **Lager als Grenze:** Ein volles Fass (1.728 Items) staut die Leitung, Überschuss verschwindet nach 5 Minuten.
- **Stopp-Schalter:** Komparator am Fass, Redstone-Staub zum Sammel-Trichter. Mit 8 Staub-Blöcken stoppt die Farm bei etwa halb vollem Fass.
- Alles gut **ausleuchten**: Um den Bot spawnen nachts Monster, und Zombies greifen Dorfbewohner an.

## Falls der Test scheitert

- **AFKDummyForFarming** (nur Paper 26.2, Java 25): <https://modrinth.com/plugin/afkdummyforfarming>, Befehle `/dafk add Farmbot`, `/dafk remove Farmbot`.
- **Fabric + Carpet:** erprobte Standardlösung, aber alle Paper-Plugins gehen verloren. Weltumzug laut [Paper-Doku](https://docs.papermc.io/paper/migration/).

## Quellen

- [FakePlayerPlugin (Hangar)](https://hangar.papermc.io/Janky-Development/FakePlayerPlugin) · [Doku](https://fpp.wtf)
- [Minecraft Wiki: server.properties](https://minecraft.wiki/w/Server.properties)
- [PaperMC Forum: Random Ticks im 128-Block-Radius](https://forums.papermc.io/threads/understanding-tick-updates.959)
