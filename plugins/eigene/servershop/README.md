# ServerShop 1.4.0

Coin-Shop mit 181 Items, Spieler-Shops und Tageslimits.

Ein Server-Shop mit Coins als Währung und Spieler-Shops an eigenen Truhen. Die Preise sind so abgestimmt, dass Kaufen, Verarbeiten und Verkaufen keinen Gewinn bringt: Coins verdient man nur mit echter Arbeit oder Arbeitern.

> Status: Dokumentation verfügbar. Quellcode und `.jar`-Download folgen.

## Funktionen

- 181 Items in Kategorien, darunter alles, was die Arbeiter liefern
- Verkaufen an den Server bringt 50 % vom Kaufpreis, gerechnet auf die ganze Menge
- Erzblöcke und antiker Schutt sind nicht kaufbar
- Spieler-Shops an selbst aufgestellten Truhen, geschützt gegen fremdes Öffnen, Trichter und Explosionen
- Kaufmenü an fremden Shop-Truhen: 1, 8, 16, 32, 64 Stück oder „So viel wie möglich“
- Tageslimit 10.000 Coins pro Spieler (Verkäufe an den Server und Einnahmen aus dem eigenen Shop), max. 256 Stück pro Item und Tag beim Kaufen
- Händler (aus dem Arbeiter-Plugin) öffnen den Shop für ihre Kategorie

## Befehle

| Befehl | Was er macht | Wer |
|---|---|---|
| `/shop` | Server-Shop öffnen | Spieler |
| `/coins` | Guthaben und heutiges Verkaufslimit | Spieler |
| `/playershop create <Preis>` | Eigene Shop-Truhe einrichten (Truhe anschauen, Ware in der Hand) | Spieler |
| `/playershop remove \| info \| liste` | Eigene Shops verwalten | Spieler |
| `/shopadmin reload` | Config neu laden | Admin |
| `/shopadmin money <Spieler> <Betrag>` | Coins gutschreiben | Admin |

## Einstellungen (`config.yml`)

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `tageslimit-verkauf-coins` | `10000` | Maximaler Verkaufserlös pro Spieler und Tag |
| `spieler-shops.einnahmen-zaehlen-zum-tageslimit` | `true` | false = Einnahmen aus dem eigenen Shop sind unbegrenzt |

## Änderungen

### 1.4.0 (31.10.2026)

- Kaufmenü an Spieler-Shops
- Tageslimit 10.000 Coins, Shop-Einnahmen zählen mit

### 1.3.0 (18.10.2026)

- 50 % Verkaufspreis auf die ganze Menge
- 181 Items, Kategorie „Tiere, Fisch & Nahrung“
- Preise gegen Gewinnschleifen geprüft (48 Rezepte)
- Händler-Anbindung
