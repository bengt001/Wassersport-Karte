# Wassersport-Karte – Online stellen & gemeinsam nutzen

Diese Anleitung bringt die App **kostenlos online** (GitHub Pages) und macht das
**Eintragen von Schildern gemeinsam nutzbar** (Supabase). Beides ist gratis.

> Ohne Schritt A funktioniert die App trotzdem – dann werden Schilder nur lokal
> auf dem jeweiligen Gerät gespeichert (nicht geteilt).

---

## A) Gemeinsame Datenbank einrichten (Supabase) – ca. 10 Min

1. Auf **https://supabase.com** kostenlos registrieren → **New project** anlegen
   (Name frei wählen, Region „Central EU" / Frankfurt, Passwort vergeben).
2. Links im Menü **SQL Editor** öffnen, folgendes einfügen und **Run** drücken:

   ```sql
   create table public.signs (
     id     bigint generated always as identity primary key,
     lat    double precision not null,
     lon    double precision not null,
     code   text not null,
     author text,
     ts     bigint not null
   );
   alter table public.signs enable row level security;
   create policy "read"   on public.signs for select using (true);
   create policy "insert" on public.signs for insert with check (true);
   create policy "delete" on public.signs for delete using (true);
   ```

   (Damit darf jeder in deiner Freundesgruppe lesen, eintragen und löschen.
   Die App selbst lässt das Löschen nur bei den **eigenen** Einträgen zu.)

2b. **Für geteilte Orte, Strecken & Kommentare** zusätzlich diese zweite
   Tabelle anlegen (SQL Editor → einfügen → **Run**):

   ```sql
   create table public.entries (
     id     bigint generated always as identity primary key,
     kind   text not null,            -- 'poi' | 'strk' | 'note'
     data   jsonb not null,
     author text,
     ts     bigint not null
   );
   alter table public.entries enable row level security;
   create policy "read"   on public.entries for select using (true);
   create policy "insert" on public.entries for insert with check (true);
   create policy "delete" on public.entries for delete using (true);
   ```

   Ohne diese Tabelle läuft die App weiter – eigene Orte/Strecken/Kommentare
   werden dann nur lokal gespeichert (nicht geteilt). Beim ersten Start mit
   vorhandener Tabelle bietet die App an, bisher lokal gespeicherte Einträge
   hochzuladen.

3. Links **Project Settings → API** öffnen und zwei Werte kopieren:
   - **Project URL** (z. B. `https://abcdxyz.supabase.co`)
   - **anon public**-Key (langer Schlüssel unter „Project API keys")

4. In der Datei **`index.html`** ganz oben im `<script>`-Bereich diese zwei
   Zeilen ausfüllen (mit dem Editor deiner Wahl):

   ```js
   const SUPABASE_URL = 'https://abcdxyz.supabase.co';
   const SUPABASE_KEY = 'dein-anon-public-key';
   ```

   Fertig – ab jetzt landen eingetragene Schilder in der gemeinsamen Datenbank.
   Der anon-Key darf öffentlich sein (er ist nur durch die obigen Regeln freigegeben).

---

## B) Kostenlos online stellen (GitHub Pages) – ca. 10 Min

1. Auf **https://github.com** kostenlos registrieren.
2. **New repository** → Name z. B. `wassersport-karte`, **Public**, anlegen.
3. **Alle Dateien hochladen**: im Repo auf **Add file → Upload files**, dann
   den **kompletten Ordnerinhalt** hineinziehen – wichtig:
   - `index.html`
   - `manifest.json`, `icon.svg`
   - der ganze Ordner **`data/`** (enthält Karten- und Schilder-Daten)

   → unten **Commit changes**.
4. **Settings → Pages**: bei *Source* **Deploy from a branch**, Branch **main**,
   Ordner **/ (root)** → **Save**.
5. Nach ~1 Minute erscheint oben die Adresse:
   **`https://DEIN-NAME.github.io/wassersport-karte/`**
   Diesen Link kannst du an deine Freunde schicken.

> Änderst du später etwas an `index.html`, einfach die Datei im Repo erneut
> hochladen – die Seite aktualisiert sich automatisch.

---

## C) Auf dem Smartphone wie eine App nutzen

Öffne den Link im Handy-Browser und füge ihn zum Startbildschirm hinzu:

- **iPhone (Safari):** Teilen-Symbol → **„Zum Home-Bildschirm"**
- **Android (Chrome):** Menü ⋮ → **„App installieren"** / „Zum Startbildschirm"

Dann startet die Karte im Vollbild wie eine echte App (Icon inklusive).

---

## Bedienung (gemeinsames Eintragen)

1. Beim ersten Eintragen fragt die App nach deinem **Namen/Kürzel** – das steht
   dann bei deinen Schildern.
2. **➕ Schild an Stelle eintragen** → auf die Karte tippen → Schild auswählen.
3. Alle sehen die Schilder der Gruppe; mit **🔄 Geteilte Schilder aktualisieren**
   (oder automatisch alle 30 Sek.) kommen neue Einträge der Freunde herein.
4. Löschen geht nur bei **eigenen** Schildern.

Viel Spaß auf dem Wasser! ⚓
