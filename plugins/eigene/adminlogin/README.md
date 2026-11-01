# AdminLogin 1.2.0

Admins müssen beim Betreten ein eigenes Passwort eingeben.

Jeder Admin (OP) gibt beim Betreten des Servers ein Admin-Passwort ein, bevor er in die Welt kommt. Normale Spieler merken davon nichts. Ein SuperOP (Chef-Admin) kann ein eigenes Passwort haben, damit sich kein normaler Admin als SuperOP anmelden kann.

> Status: Dokumentation verfügbar. Quellcode und `.jar`-Download folgen.

## Funktionen

- Admin-Anmeldung per Fenster beim Betreten, Passwörter werden verschlüsselt gespeichert
- Nach 3 falschen Versuchen 15 Minuten gesperrt (einstellbar)
- Eigenes Passwort pro Admin möglich, z. B. für den SuperOP
- Passwort merken: nach richtiger Eingabe für eine einstellbare Zeit nicht mehr fragen, nur vom selben Gerät bzw. derselben IP
- Verbindungen über einen lokalen Tunnel (127.0.0.1, z. B. playit) werden nie gemerkt

## Befehle

| Befehl | Was er macht | Wer |
|---|---|---|
| `adminlogin reload` | Config neu laden | Konsole |
| `adminlogin entsperren <Name>` | Gesperrten Admin freigeben | Konsole |
| `adminlogin passwort <Name> <Passwort>` | Eigenes Admin-Passwort setzen | Konsole |
| `adminlogin sitzungen` | Gemerkte Anmeldungen anzeigen | Konsole |
| `adminlogin abmelden <Name\|alle>` | Gemerkte Anmeldungen löschen | Konsole |

## Einstellungen (`config.yml`)

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `merken-stunden` | `12` | Wie lange ein richtig eingegebenes Passwort gemerkt wird, 0 = jedes Mal fragen |
| `merken-stunden-eigenes-passwort` | `-1` | Gleiche Einstellung für Admins mit eigenem Passwort, -1 = wie oben |

## Änderungen

### 1.2.0 (27.10.2026)

- Admin-Passwort merken (pro Gerät/IP, einstellbar)
- Befehle sitzungen und abmelden

### 1.1.0 (18.10.2026)

- Erste Version: Admin-Anmeldung, Sperre nach Fehlversuchen, eigenes SuperOP-Passwort
