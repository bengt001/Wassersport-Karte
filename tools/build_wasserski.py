#!/usr/bin/env python3
"""
Baut data/wasserski_strecken.js – kuratierte Liste amtlich freigegebener
Wasserski-Strecken (Tafelzeichen E.17) in Deutschland.

Quellen:
 - BMV/WSV: "Wasserskilaufen auf Binnenschifffahrtsstraßen des Bundes –
   Südliche Wasserstraßen" (Main, Neckar, Main-Donau-Kanal, Regnitz, Donau)
 - ELWIS / GDWS Sportschifffahrts-Broschüren (Mosel/Saar/Lahn, Elbe–Oder, Nord)

Wichtig: km-Angaben stammen aus den amtlichen Listen, die Punkt-Koordinaten
werden aus den Ortsbeschreibungen per Nominatim geocodiert und sind daher
NUR UNGEFÄHR. Maßgeblich ist die Beschilderung (E.17) vor Ort + ELWIS.

Aufruf:  python3 build_wasserski.py
"""
import json, time, urllib.request, urllib.parse, os, sys

UA = "wassersport-karte/1.0 (kontakt: lokal)"

# --- Kuratierte Strecken: (Fluss, km, Beschreibung, Geocode-Suchbegriff, Bundesland, Zeiten) ---
S = []
def add(river, km, desc, geo, land, times=""):
    S.append(dict(river=river, km=km, desc=desc, geo=geo, land=land, times=times, conf="approx"))

# NECKAR (Baden-Württemberg)
add("Neckar","94,92–97,20","zwischen Heinsheim und Offenau","Offenau, Neckar","Baden-Württemberg","sonn-/feiertags ab 16:00")
add("Neckar","196,80–198,80","Oberesslingen bis Kraftwerk Altbach","Altbach, Neckar","Baden-Württemberg","sonn-/feiertags ab 13:00")

# MAIN-DONAU-KANAL / REGNITZ (Bayern)
add("Main-Donau-Kanal / Regnitz","0,00–0,20","Höhe Bischberg (Anschluss an Main-Strecke)","Bischberg","Bayern")
add("Main-Donau-Kanal / Regnitz","26,25–26,56","Wehrarm der Regnitzstaustufe Forchheim","Forchheim","Bayern","max. 30 km/h")

# DONAU (Bayern) – nur Do–So und an bayerischen Feiertagen
DT="nur Do–So & bayer. Feiertage"
add("Donau","2206,0–2221,3","Betriebshafen Grünau bis Löwenmühle","Vilshofen an der Donau","Bayern",DT)
add("Donau","2232,4–2246,0","Heining bis Windorf","Windorf, Donau","Bayern",DT)
add("Donau","2267,2–2269,2","Ruckasing bis Mühlham","Künzing","Bayern",DT)
add("Donau","2284,0–2291,2","Hafeneinfahrt Deggendorf bis Zeitldorf","Deggendorf","Bayern",DT)
add("Donau","2312,6–2317,5","oberhalb Sand (Straubing)","Sand, Straubing","Bayern",DT)
add("Donau","2358,5–2366,0","oberhalb Reibersdorf","Bogen, Donau","Bayern",DT)
add("Donau","2387,0–2397,0","Autobahnbrücke Wörth bis Sulzbach","Wörth an der Donau","Bayern",DT)
add("Donau","2402,2–2414,2","Sportboothafen Sinzing bis Kelheim","Bad Abbach","Bayern",DT)

# MAIN (Hessen + Bayern/Unterfranken) – Sa/So/Fei 9–12 & 14–19, Mo–Fr 9–12 & 14–21
MT="Sa/So/Fei 9–12 & 14–19 Uhr"
add("Main","45,16–47,60","Höhe Fechenheim","Fechenheim, Frankfurt am Main","Hessen",MT)
add("Main","57,80–59,00","Hafen Hanau bis Mainaltarm Steinheimer Bogen","Hanau","Hessen",MT)
add("Main","65,00–66,60","unterhalb Kahlmündung","Kahl am Main","Bayern",MT)
add("Main","79,60–81,50","unterhalb Autobahnbrücke Kleinostheim","Kleinostheim","Bayern",MT)
add("Main","81,50–83,20","unterhalb Hafen Aschaffenburg","Aschaffenburg","Bayern",MT)
add("Main","94,00–95,00","oberhalb Ländeplatz Obernau","Obernau, Aschaffenburg","Bayern",MT)
add("Main","106,15–107,10","unterhalb Schutzhafen Erlenbach","Erlenbach am Main","Bayern",MT)
add("Main","115,20–116,50","zwischen Röllfeld und Laudenbach","Klingenberg am Main","Bayern",MT)
add("Main","127,00–128,50","oberhalb Ländeplatz Bürgstadt","Bürgstadt","Bayern",MT)
add("Main","137,90–139,70","oberhalb Collenberg","Collenberg","Bayern",MT)
add("Main","151,30–153,00","oberhalb Hafen Wertheim","Wertheim","Baden-Württemberg",MT)
add("Main","163,80–165,91","oberhalb Urphar","Urphar, Wertheim","Baden-Württemberg",MT)
add("Main","176,20–177,20","zwischen Trennfeld und Marktheidenfeld","Marktheidenfeld","Bayern",MT)
add("Main","187,70–188,80","unterhalb Neustadt am Main","Neustadt am Main","Bayern",MT)
add("Main","190,50–195,60","Höhe Rodenbach (bei Lohr)","Lohr am Main","Bayern",MT)
add("Main","209,60–210,80","unterhalb Gemünden","Gemünden am Main","Bayern",MT)
add("Main","220,80–224,20","Karlburg bis Staustufe Harrbach","Karlstadt","Bayern",MT)
add("Main","233,80–234,80","unterhalb Straßenbrücke Zellingen","Zellingen","Bayern",MT)
add("Main","259,00–262,20","oberhalb Staustufe Randersacker","Randersacker","Bayern",MT)
add("Main","269,20–270,00","oberhalb Staustufe Goßmannsdorf","Goßmannsdorf am Main","Bayern",MT)
add("Main","278,00–279,80","zwischen Marktsteft und Segnitz","Marktsteft","Bayern",MT)
add("Main","287,91–289,78","zwischen Mainstockheim und Kitzingen","Kitzingen","Bayern",MT)
add("Main","296,40–298,50","Höhe Straßenbrücke bei Schwarzenau","Schwarzach am Main","Bayern",MT)
add("Main","306,20–307,50","oberhalb Brücke Volkach","Volkach","Bayern",MT)
add("Main","311,80–313,20","zwischen Fähre Obereisenheim und Fahr","Obereisenheim","Bayern",MT)
add("Main","316,26–316,80","im Wehrarm der Staustufe Wipfeld","Wipfeld","Bayern",MT)
add("Main","320,00–322,80","zwischen Fähre Garstadt und Hirschfeld","Bergrheinfeld","Bayern",MT)
add("Main","333,23–334,68","Höhe Schweinfurt (Höllenbachmündung)","Schweinfurt","Bayern",MT)
add("Main","348,05–350,40","zwischen Ober- und Untertheres","Theres","Bayern",MT)
add("Main","368,23–372,50","Höhe Eltmann","Eltmann","Bayern",MT)
add("Main","381,30–384,19","unterhalb Regnitzmündung (bei Bamberg)","Bischberg","Bayern",MT)

# ELBE (Quelle: GDWS-Broschüre „Wassersport zwischen Elbe und Oder")
add("Elbe","71,30–72,60","unterhalb Wildberg (linke Stromseite)","Mühlberg/Elbe","Brandenburg / Sachsen")
add("Elbe","110,50–111,50","unterhalb Riesa (linke Stromseite)","Riesa","Sachsen","9–12 & 15–18 Uhr")
add("Elbe","155,60–156,60","unterhalb Torgau","Torgau","Sachsen")
add("Elbe","168,50–169,90","oberhalb/unterhalb Elsnig","Elsnig","Sachsen")
add("Elbe","238,00–239,00","unterhalb Coswig (Anhalt)","Coswig (Anhalt)","Sachsen-Anhalt")
add("Elbe","304,00–306,00","unterhalb Glinde","Glinde bei Barby","Sachsen-Anhalt")
add("Elbe","322,20–323,00","Magdeburg-Buckau","Magdeburg-Buckau","Sachsen-Anhalt")
add("Elbe","344,50–345,80","Heinrichsberg / Niegripp","Niegripp","Sachsen-Anhalt")
add("Elbe","452,50–453,50","oberhalb Wittenberge","Wittenberge","Brandenburg","täglich 8–18 Uhr")
add("Elbe","487,20–489,20","oberhalb/unterhalb Vietze (linkes Ufer, Buhnenfelder)","Vietze","Niedersachsen")
add("Elbe","525,50–527,50","unterhalb Hitzacker","Hitzacker","Niedersachsen")
add("Elbe","533,50–535,50","oberhalb Neu-Darchau","Neu Darchau","Niedersachsen")
add("Elbe","552,30–554,00","unterhalb Bleckede","Bleckede","Niedersachsen")
add("Elbe","563,50–566,00","unterhalb Barförde","Barförde","Niedersachsen")
add("Elbe","566,50–568,85","oberhalb Lauenburg (nur rechte Stromseite)","Lauenburg/Elbe","Schleswig-Holstein")
add("Elbe","584,00–585,00","oberhalb Wehr Geesthacht (rechte Stromseite, 100 m parallel zum Deckwerk)","Geesthacht","Schleswig-Holstein","⚠️ Wehrbereich gesperrt – Lebensgefahr!")
add("Elbe","586,20–587,50","unterhalb Wehr Geesthacht","Geesthacht","Schleswig-Holstein","⚠️ Wehrbereich gesperrt – Lebensgefahr!")
add("Elbe","600,00–603,00","unterhalb Hoopte bis Fliegenberg","Hoopte, Winsen (Luhe)","Niedersachsen")

# SEEN-WASSERSTRASSEN NORD-OST (MV / Brandenburg / Berlin / Sachsen-Anhalt)
add("Tegeler See (Havel-Oder)","km 4,0","Insel Lindwerder – 400×100 m","Tegeler See, Berlin","Berlin","9–12 & 15–18 Uhr")
add("Plauer See (Müritz-Elde)","km 126,2","östl. Plauer Werder","Plauer See, Plau am See","Mecklenburg-Vorpommern","9–12 & 15–18 Uhr · ab Windst. 4 gesperrt")
add("Fleesensee (Müritz-Elde)","138,0–139,0","bei Untergöhren","Untergöhren","Mecklenburg-Vorpommern")
add("Müritz","154,3–156,3","südl. Schloss Klink bei Sembzin","Klink","Mecklenburg-Vorpommern")
add("Müritz","km 158,0","1500×500 m südlich","Sembzin","Mecklenburg-Vorpommern")
add("Müritz","164,5–165,0","zwischen Ludorfer Höbel und Plötzer Berg","Ludorf","Mecklenburg-Vorpommern")
add("Müritz-Havel-Wasserstraße","km 14,5","Diemitz","Diemitz, Mirow","Mecklenburg-Vorpommern")
add("Müritz-Havel-Wasserstraße","23,3–24,5","Mirow (Vilzsee / Mirower See)","Mirow","Mecklenburg-Vorpommern")
add("Obere Havel-Wasserstraße","55,8–57,0","unterhalb Himmelpfort (Stolpsee)","Himmelpfort","Brandenburg","9–12 & 15–18 Uhr")
add("Obere Havel-Wasserstraße","73,75–74,5","oberhalb Priepert (Priepertsee)","Priepert","Mecklenburg-Vorpommern")
add("Obere Havel-Wasserstraße","85,8–87,0","oberhalb Groß-Trebbow (Woblitzsee)","Wesenberg","Mecklenburg-Vorpommern")
add("Potsdamer Havel","8,5–9,5","Großer Zernsee, unterhalb Eisenbahnbrücke Werder","Werder (Havel)","Brandenburg","9–12 & 15–18 Uhr")
add("Potsdamer Havel","21,05–21,30","Templiner See, oberhalb Eisenbahnbrücke Potsdam","Potsdam","Brandenburg","9–12 & 15–21 Uhr")
add("Stör-Wasserstraße","28,0–28,3","Ziegelsee, unterhalb Fahrt zum Hafen Schwerin","Ziegelsee, Schwerin","Mecklenburg-Vorpommern")
add("Stör-Wasserstraße","32,5–35,0","Schweriner See, Retgendorf Richtung Rampe","Retgendorf","Mecklenburg-Vorpommern","ab Windst. 4 gesperrt")
add("Templiner Gewässer","19,1–20,0","Fährsee bei Templin","Templin","Brandenburg","9–12 & 15–18 Uhr")
add("Untere Havel-Wasserstraße","8,8–9,5","unterhalb Insel Lindwerder (Havelchaussee)","Havelchaussee, Berlin","Berlin")
add("Untere Havel-Wasserstraße","38,3–39,0","Trebelsee, unterhalb Ketzin","Ketzin","Brandenburg","9–12 & 15–21 Uhr")
add("Untere Havel-Wasserstraße","75,2–75,8","oberhalb Tieckow-West","Tieckow","Brandenburg")
add("Werbelliner Gewässer","17,1–17,8","Werbellinsee Ostufer, oberhalb Altenhof","Altenhof, Werbellinsee","Brandenburg","9–12 & 15–18 Uhr")
add("Saale","25,1–26,1","bei Nienburg","Nienburg (Saale)","Sachsen-Anhalt","1.6.–30.9. · 9–13 & 15–20 Uhr")

# --- Regionen, in denen amtliche E.17-Strecken existieren, aber hier NICHT
#     einzeln verortet sind: nur als Recherche-Hinweis (conf="region"). ---
def region(name, land, lat, lon, hint, url):
    S.append(dict(river=name, km="—", desc=hint, geo=None, land=land, times="",
                  conf="region", lat=lat, lon=lon, url=url))

region("Mosel, Saar & Lahn","RLP / Saarland / Hessen",49.79,6.64,
       "Mehrere freigegebene Wasserski-Strecken – genaue Abschnitte beim WSA Mosel-Saar-Lahn prüfen.",
       "https://www.wsa-mosel-saar-lahn.wsv.de/Webs/WSA/Mosel-Saar/DE/02_Schifffahrt/07_SportFreizeitschifffahrt/Wasserski/wasserski_node.html")
region("Weser, Aller, Leine, Fulda, Werra","Niedersachsen / Hessen / NRW",52.43,9.20,
       "Einzelne freigegebene Strecken (u. a. Aller bei Hornbostel/Frankenfeld) – beim WSA Weser prüfen.",
       "https://www.wsa-weser.wsv.de/Webs/WSA/Weser/DE/02_Schifffahrt/01_SportFreizeitschifffahrt/04_Wasserski/Wasserski_node.html")
region("Mittelweser / Mittellandkanal-Raum","Niedersachsen",52.43,9.66,
       "Freigegebene Strecken im Bereich Mittellandkanal/ESK – beim WSA Mittellandkanal-ESK prüfen.",
       "https://www.wsa-mittellandkanal-elbe-seitenkanal.wsv.de/Webs/WSA/Mittellandkanal-ESK/DE/Schifffahrt/SportFreizeitschifffahrt/sportfreizeitschifffahrt_node.html")

# ------------------------------------------------------------------
def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"format": "json", "limit": 1, "countrycodes": "de", "q": q})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
        if d:
            return float(d[0]["lat"]), float(d[0]["lon"])
    except Exception as e:
        sys.stderr.write(f"  geocode-Fehler '{q}': {e}\n")
    return None

def main():
    feats = []
    miss = []
    for i, e in enumerate(S, 1):
        if e["conf"] == "region":
            lat, lon = e["lat"], e["lon"]
        else:
            print(f"[{i}/{len(S)}] geocodiere: {e['geo']}", flush=True)
            ll = geocode(e["geo"])
            time.sleep(1.1)  # Nominatim: max 1 Anfrage/Sekunde
            if not ll:
                miss.append(e["geo"]); continue
            lat, lon = ll
        props = {k: e[k] for k in ("river", "km", "desc", "land", "times", "conf")}
        if e.get("url"):
            props["url"] = e["url"]
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                      "properties": props})

    fc = {"type": "FeatureCollection",
          "metadata": {"title": "Amtliche Wasserski-Strecken (E.17) – ungefähre Lage",
                       "source": "BMV/WSV & ELWIS Sportschifffahrt-Broschüren; Geocoding © OSM/Nominatim",
                       "note": "Koordinaten sind aus Ortsbeschreibungen abgeleitet und nur ungefähr. "
                               "Maßgeblich sind die E.17-Schilder vor Ort und ELWIS.",
                       "generated": time.strftime("%Y-%m-%d %H:%M"),
                       "total": len(feats)},
          "features": feats}

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "wasserski_strecken.geojson"), "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(out_dir, "wasserski_strecken.js"), "w", encoding="utf-8") as f:
        f.write("window.WS_STRECKEN=")
        json.dump(fc, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";")
    print(f"\n✅ {len(feats)} Strecken/Regionen gespeichert.  Nicht geocodiert: {miss}")

if __name__ == "__main__":
    main()
