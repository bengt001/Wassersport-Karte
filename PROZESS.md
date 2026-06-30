# Wassersport-Karte Deutschland – Der gesamte Entstehungsprozess

Eine Dokumentation, wie aus einer Idee Schritt für Schritt eine mobile,
gemeinsam nutzbare Web-App für Wassersport wurde – inklusive der Probleme,
die unterwegs auftauchten, und wie sie gelöst wurden.

**Live:** https://bengt001.github.io/Wassersport-Karte/

---

## Inhaltsverzeichnis

1. [Die Ausgangsidee](#1-die-ausgangsidee)
2. [Von „live abfragen" zu „vorab recherchieren"](#2-von-live-abfragen-zu-vorab-recherchieren)
3. [Kilometermarken der Flüsse](#3-kilometermarken-der-flüsse)
4. [Wasserski-Strecken einzeichnen](#4-wasserski-strecken-einzeichnen)
5. [Windsurf- und SUP-Verleih](#5-windsurf--und-sup-verleih)
6. [Schilder selbst eintragen](#6-schilder-selbst-eintragen)
7. [Echte Piktogramme & vollständiger Katalog](#7-echte-piktogramme--vollständiger-katalog)
8. [Kostenlos online & gemeinsam nutzbar](#8-kostenlos-online--gemeinsam-nutzbar)
9. [Mobile-Optimierung](#9-mobile-optimierung)
10. [Die großen Bugs & ihre Lösungen](#10-die-großen-bugs--ihre-lösungen)
11. [Architektur-Überblick](#11-architektur-überblick)
12. [Ehrliche Grenzen der Daten](#12-ehrliche-grenzen-der-daten)
13. [Datenquellen](#13-datenquellen)

---

## 1. Die Ausgangsidee

**Ziel:** Eine App/Karte, mit der man in Deutschland schnell Stellen zum
Wasserskifahren findet. Drei Dinge sollten sichtbar sein:

- **Alle Schifffahrtszeichen** (Schifffahrtssymbole) Deutschlands
- **Wasserski- und Jetski-Bereiche**
- **Slipstellen** (Bootsrampen) zum Einsetzen der Boote

Technische Grundentscheidung: eine **einzelne HTML-Datei** mit
[Leaflet](https://leafletjs.com/) als Kartenbibliothek und
OpenStreetMap als Kartenhintergrund. Kein Server nötig, läuft überall.

---

## 2. Von „live abfragen" zu „vorab recherchieren"

**Problem:** Die erste Version fragte beim Reinzoomen live die
[Overpass-API](https://overpass-api.de/) (OpenStreetMap-Datenbank) ab.
Das dauerte **viel zu lange** und es fehlten Bereiche.

**Lösung – Vorab-Recherche statt Live-Abfrage:**
Wir bauten **Python-Build-Skripte** (`tools/build_*.py`), die einmalig alle
Daten sammeln und in fertige JavaScript-Dateien schreiben. Die App lädt diese
vorberechneten Dateien blitzschnell, statt bei jedem Zoom neu zu fragen.

```
data/
 ├─ spots.js            ← Slipstellen, Häfen, Schifffahrtszeichen (~6200 Einträge)
 ├─ wasserski_strecken.js  ← 83 Wasserski-Regionen/Strecken
 ├─ strecken_lines.js   ← eingezeichnete Streckenlinien
 ├─ kmmarks.js          ← 713 Flusskilometer-Marken
 ├─ windsurf.js         ← Windsurf-Verleih (202)
 └─ sup.js              ← SUP-Verleih an Badeseen (458)
```

Geladen werden sie per `<script src="data/…">`, das die Daten an
`window.SPOTS`, `window.KMMARKS` usw. hängt – ein bewusster Trick, um das
CORS-Problem beim lokalen Öffnen (`file://`) zu umgehen.

**Hürde:** Die Overpass-API hat uns **ständig mit „429 Too Many Requests"**
blockiert. Gelöst durch: mehrere Endpunkte abwechselnd nutzen
(overpass-api.de + kumi.systems), exponentielles Zurückwarten (Backoff),
längere Pausen und kategorieweises Abarbeiten im Hintergrund.

---

## 3. Kilometermarken der Flüsse

**Wunsch:** Wasserski-Bereiche sind oft als **Flusskilometer** angegeben
(„Elbe km 580–585"). Damit man das abgleichen kann, sollten die
**Kilometermarken der Flüsse** auf der Karte erscheinen.

**Umsetzung:** 713 Kilometermarken aus OpenStreetMap extrahiert und als
eigene, ein-/ausschaltbare Ebene auf die Karte gelegt.

---

## 4. Wasserski-Strecken einzeichnen

**Wunsch:** Erlaubte Strecken sollten als **Linie dem echten Flusslauf
folgend** eingezeichnet werden – auch solche, die nur auf Papierkarten
existieren (z. B. die **Strecke bei Geesthacht auf der Elbe** bei Hamburg).

**Was wir machten:**
- 83 Wasserski-Regionen recherchiert und geocodiert (Ortsnamen → Koordinaten
  via [Nominatim](https://nominatim.org/), Limit 1 Abfrage/Sekunde).
- Ungenaue Strecken kommen in ein **separates Fenster mit Recherche-Hinweisen**,
  statt sie falsch präzise auf die Karte zu malen.

**Ehrliche Hürde:** Die saubere Linienführung entlang des Flusses erwies sich
als fragil – das Zusammenstückeln verlief sich in Nebenflüsse. Wir stellten
auf **kilometermarken-basiertes** Zeichnen um. Dabei zeigte sich: OpenStreetMap
hat verlässliche km-Marken nur für **Main km 0–110** → daher nur 7 saubere
Linien möglich. Das wurde offen kommuniziert, statt unsichere Linien zu malen.

---

## 5. Windsurf- und SUP-Verleih

**Wunsch:** Zusätzlich Orte zeigen, wo man **Windsurf-Ausrüstung leihen** kann –
und **SUP-Boards**, aber **nur dort, wo man auch schwimmen** kann (an einem
**Badesee**).

**Umsetzung:**
- Windsurf-Verleih: 202 Orte aus OSM-Tags.
- SUP-Verleih: 458 Orte – gefiltert auf Stellen mit Bademöglichkeit
  (Badesee/Strandbad in der Nähe).

---

## 6. Schilder selbst eintragen

**Wunsch:** Man soll **selbst aktiv Schilder eintragen** können:
auf die Karte tippen → aus einer Liste **aller möglichen
Wasserstraßenschilder** auswählen → die **häufigsten oben**, seltene unten.

**Umsetzung:**
- Modus „➕ Schild an Stelle eintragen" → roter Hinweis-Banner → Karte antippen.
- Auswahl-Dialog mit allen Schildern, sortiert nach Häufigkeit.
- **Personalisierung:** Die App merkt sich (per `localStorage`), welche Schilder
  *du* oft benutzt, und zieht sie weiter nach oben.
- **Abbrechen:** sichtbarer „✖ Abbrechen"-Button im Banner; auf dem Handy lässt
  der Banner links Platz, damit das Menü erreichbar bleibt.

---

## 7. Echte Piktogramme & vollständiger Katalog

**Wunsch:** Die Symbole sollen **exakt so aussehen wie im echten Bootsverkehr** –
besonders Wasserski/Jetski – und es sollen **wirklich alle** Zeichen dabei sein,
sowohl **Binnen-** als auch **Seeschifffahrtszeichen**.

**Was wir taten:**
- **88 Schilder** im Katalog, Binnen + See, mit **offiziellen Pictogrammen**
  (heruntergeladen von Wikimedia Commons, 103 PNG-Dateien in `data/signs/`).
- Codes gegen die **BinSchStrO Anlage 7** und die deutschsprachige Wikipedia-
  „Bildtafel der Binnenschifffahrtszeichen" geprüft.
- See-Zeichen nach **IALA Region A**.

**Korrigierte Fehler unterwegs:**
- „Baden verboten" ist **nicht** A.5.1/A.20 (existiert in Anlage 7 nicht);
  A.5.1 = Stillliegeverbot.
- Geschwindigkeitsbegrenzung = **B.6**.
- A.17 = Segelsurfen (war fälschlich A.20).
- Verbotszeichen: Diagonalstrich von **oben-links nach unten-rechts**.

**Hürde:** Wikimedia blockierte Downloads (429). Gelöst über die Route
`Special:FilePath/<Datei>?width=320`, die zuverlässig lieferte.

Außerdem behoben: **Text lief über den Rand** der Auswahl-Kacheln – per CSS mit
`word-break`/`hyphens`/`overflow-wrap` und breiteren Kacheln gefixt.

---

## 8. Kostenlos online & gemeinsam nutzbar

**Wunsch:** Die App soll **kostenlos online** stehen, damit **Freunde auch
Schilder eintragen** können und alle dieselben Einträge sehen.

**Lösung – zwei kostenlose Bausteine:**

| Baustein | Wofür |
|---|---|
| **GitHub Pages** | Hostet die Seite gratis unter einer öffentlichen Adresse |
| **Supabase** | Gemeinsame Datenbank für eingetragene Schilder (geteilt) |

- Schilder werden per **Supabase REST-API** gespeichert und alle 30 Sekunden
  (bzw. per „🔄"-Button) synchronisiert.
- **Fallback:** Ohne Supabase speichert die App lokal auf dem Gerät – die Karte
  funktioniert trotzdem.
- Beim ersten Eintragen fragt die App nach **Name/Kürzel**; Löschen geht nur bei
  **eigenen** Schildern.
- Die genaue Schritt-für-Schritt-Anleitung steht in **[SETUP.md](SETUP.md)**
  (inkl. SQL für die Datenbank-Tabelle).

Die Supabase-Zugangsdaten des Nutzers wurden in `index.html` eingetragen, und
alle Dateien wurden per `gh` CLI nach GitHub hochgeladen und über GitHub Pages
veröffentlicht.

---

## 9. Mobile-Optimierung

Die App ist als **PWA** („zum Startbildschirm hinzufügen") aufgebaut:

- `manifest.json` + App-Icon (`icon.svg`) → startet im Vollbild wie eine App.
- Viewport mit `viewport-fit=cover`, Beachtung der **Safe-Area** (Notch).
- Seitenmenü als 86 %-breite Schublade, Dialoge als **Bottom-Sheets**.
- Eingabefelder mit 16 px Schrift, damit iOS nicht automatisch zoomt.

---

## 10. Die großen Bugs & ihre Lösungen

**🐞 Karte eingefroren, keine Icons (kritisch).**
Auf dem Computer ließ sich die Karte nicht mehr zoomen/bewegen, keine Symbole;
auf dem Handy ging Bewegen, aber auch ohne Symbole.
*Ursache:* `document.querySelector('#ly-mine .lab b')` lieferte `null`, weil
`#ly-mine` die Checkbox ist und `.lab` ein **Geschwister-Element** – das warf
einen `TypeError`, **bevor** die Daten geladen wurden, und stoppte das ganze Script.
*Fix:* `.closest('.layer').querySelector('.lab b')`, das Ganze in `try/catch`
gekapselt, und die **Daten-Lader zuerst** ausgeführt. Seitdem stabil.

**🐞 `git push` hing immer wieder.**
Festhängende Prozesse (`git push` / `git-remote-https`) beendet und im
Vordergrund neu gepusht – jedes Mal erfolgreich.

**🐞 Banner verdeckte den Menü-Knopf.**
Der rote Hinweis-Banner lag über dem ☰-Menü. Gelöst durch sichtbaren
„✖ Abbrechen"-Button **und** linken Freiraum auf dem Handy.

---

## 11. Architektur-Überblick

```
Browser (Leaflet + Marker-Cluster)
        │
        ├─ lädt  data/*.js   (vorberechnete Daten – schnell)
        │
        └─ Schilder eintragen
               ├─ Supabase REST  ──►  gemeinsame DB (geteilt mit Freunden)
               └─ localStorage   ──►  Fallback (nur eigenes Gerät)

Build-Zeit (einmalig, Python):
   tools/build_*.py
        ├─ Overpass-API   (OSM-Daten)
        ├─ Nominatim      (Geocoding)
        └─ Wikimedia      (Schild-Bilder)
```

- **Frontend:** Leaflet 1.9.4 + Leaflet.markercluster 1.5.3 (per CDN).
- **Daten-Build:** Python 3 mit `urllib`, PDF-Auslesen via `pdfminer.six`.
- **Backend (optional):** Supabase (PostgREST + Row-Level-Security).
- **Hosting:** GitHub Pages.

---

## 12. Ehrliche Grenzen der Daten

Damit die Karte ehrlich bleibt, hier die bekannten Schwächen:

- **Jetski-Bereiche** stehen kaum in offenen Geodaten – die WasMotRV-Verordnung
  veröffentlicht Koordinaten nur im Verkehrsblatt, nicht maschinenlesbar.
  In OSM gab es nur **einen einzigen** Jetski-Eintrag.
- **Flusslauf-Linien** sind durch dünne OSM-Kilometermarken begrenzt
  (nur Main → 7 Linien).
- **Windsurf-/SUP-„Verleih"** ist aus OSM-Tags abgeleitet – nicht perfekt präzise.
- **See-Zeichen** mischen zwei Grafikquellen (INT-Serie + IALA-PNGs).

Diese Punkte wurden bewusst offen benannt, statt falsche Genauigkeit vorzutäuschen.

---

## 13. Datenquellen

- **OpenStreetMap / Overpass-API** – Slipstellen, Häfen, km-Marken, Verleihe.
- **Nominatim** – Geocoding der Ortsnamen.
- **Wikimedia Commons** – offizielle Schild-Pictogramme.
- **BinSchStrO Anlage 7** & deutschsprachige Wikipedia-Bildtafel – Schild-Codes.
- **IALA Region A** – Seeschifffahrtszeichen.

---

*Erstellt mit Claude Code. Live unter
https://bengt001.github.io/Wassersport-Karte/ – viel Spaß auf dem Wasser! ⚓*
