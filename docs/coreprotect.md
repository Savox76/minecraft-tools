---
titel: Spieler-Aktionen protokollieren
kurz: Mit CoreProtect nachvollziehen, wer was gebaut, abgebaut oder aus Kisten genommen hat.
reihenfolge: 2
---

# Spieler-Aktionen protokollieren mit CoreProtect

CoreProtect ist das Standard-Plugin auf Paper, um nachzuvollziehen, wer wann was gemacht hat. Gebaute oder zerstörte Blöcke lassen sich damit auch zurücksetzen.

## Was aufgezeichnet wird

- Blöcke setzen und abbauen
- Kisten: wer was hineingelegt oder herausgenommen hat
- Items fallen lassen und aufheben, Türen, Hebel und Knöpfe
- Getötete Mobs, Ein- und Ausloggen
- Chat, Befehle, Schildtexte

## Installation

1. **Backup** machen.
2. Die `.jar` von Modrinth holen: <https://modrinth.com/plugin/coreprotect> (unter „Plugins“).
3. In den Ordner `plugins` legen und den Server neu starten.

Die stabile Version unterstützt Minecraft bis 26.1.2. Für neuere Versionen gibt es Entwicklungs-Builds auf GitHub.

## Befehle

| Befehl | Was er macht |
|---|---|
| `/co i` | Inspektor an/aus: Block anklicken zeigt, wer ihn gesetzt oder abgebaut hat |
| `/co lookup u:Name t:1d` | Alles, was dieser Spieler am letzten Tag getan hat |
| `/co lookup u:Name t:3d a:container` | Seine Kisten-Aktivität der letzten 3 Tage |
| `/co lookup u:Name a:session` | Wann er online war |
| `/co lookup t:2h r:20` | Alles im Umkreis von 20 Blöcken in den letzten 2 Stunden |
| `/co rollback u:Name t:2h r:#global #preview` | Vorschau, was zurückgesetzt würde |
| `/co rollback u:Name t:2h r:#global` | Änderungen tatsächlich zurücksetzen |
| `/co undo` | Letzten Rollback rückgängig machen |
| `/co purge t:30d` | Daten älter als 30 Tage löschen |

Bei einem Rollback immer `r:` angeben, sonst wirkt er nur im Umkreis von 10 Blöcken.

## Ohne Plugin

`logs/latest.log` im Server-Ordner enthält Logins, Chat und Befehle. Ältere Tage liegen als `.log.gz` daneben. Blöcke und Kisten stehen dort nicht drin.

Für das gemeinsame Lager gibt es zusätzlich `/lager protokoll` aus dem Plugin [InfiniteLager](#/plugin/infinitelager).

**Fair bleiben:** Sag den Spielern auf deinem Server, dass ihr Handeln aufgezeichnet wird.

## Quellen

- [GameServerKings: CoreProtect](https://www.gameserverkings.com/knowledge-base/minecraft/coreprotect-rollback/)
- [Mineguard: Grief rückgängig machen](https://mineguard.pro/de/blog/coreprotect-rollback-grief-recovery)
