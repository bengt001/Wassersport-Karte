#!/usr/bin/env python3
"""
Holt SUP-/Bootsverleih-Stellen, die NAHE AN EINEM BADEPLATZ liegen
(Badesee, Strand, Schwimmstelle), bundesweit aus OSM.
Ausgabe: data/sup.js -> window.SUP

Filter: Verleih-Kandidat AND im Umkreis von ~350 m einer Badestelle
(leisure=swimming_area / natural=beach / sport=swimming).
"""
import json, re, os, time, urllib.request, urllib.parse, sys

EP = ["https://overpass-api.de/api/interpreter",
      "https://overpass.kumi.systems/api/interpreter"]

# 1) Badestellen  2) Verleih-Kandidaten  3) Kandidaten im Umkreis der Badestellen
QUERY = ('[out:json][timeout:300];area["ISO3166-1"="DE"][admin_level=2]->.de;'
         '('
         '  nwr["leisure"="swimming_area"](area.de);'
         '  nwr["natural"="beach"](area.de);'
         '  nwr["sport"="swimming"]["access"!="private"](area.de);'
         ')->.swim;'
         '('
         '  nwr["amenity"="boat_rental"](area.de);'
         '  nwr["shop"="watersports"](area.de);'
         '  nwr["sport"~"sup|stand_up"](area.de);'
         '  nwr["name"~"SUP|[Ss]tand.?[Uu]p|[Pp]addel|[Pp]addle"](area.de);'
         ')->.cand;'
         'nwr.cand(around.swim:350);'
         'out center tags;')

SUP_RE = re.compile(r"\bSUP\b|stand.?up|paddel|paddle|stand_up", re.I)
RENT_RE = re.compile(r"verleih|rental|vermiet|boat_rental", re.I)

def fetch():
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    last = None
    for ep in EP:
        for _ in range(3):
            try:
                req = urllib.request.Request(ep, data=data, headers={"User-Agent": "wassersport-karte/1.0"})
                with urllib.request.urlopen(req, timeout=320) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                last = e; sys.stderr.write(f"  retry: {e}\n"); time.sleep(20)
    raise RuntimeError(last)

def main():
    osm = fetch()
    feats, seen = [], set()
    for el in osm.get("elements", []):
        t = el.get("tags") or {}
        lat = el.get("lat", (el.get("center") or {}).get("lat"))
        lon = el.get("lon", (el.get("center") or {}).get("lon"))
        if lat is None or lon is None:
            continue
        key = (round(lat, 5), round(lon, 5), t.get("name", ""))
        if key in seen:
            continue
        seen.add(key)
        blob = " ".join([t.get("name", ""), t.get("sport", ""), t.get("amenity", ""), t.get("shop", "")])
        is_sup = bool(SUP_RE.search(blob))           # explizit SUP genannt
        rental = bool(RENT_RE.search(blob)) or t.get("amenity") == "boat_rental" or t.get("shop") == "watersports"
        keep = {k: t[k] for k in ("name", "website", "phone", "opening_hours", "operator", "sport", "shop", "amenity") if t.get(k)}
        keep["sup"] = is_sup
        keep["rental"] = rental
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                      "properties": keep})
    sup_n = sum(1 for f in feats if f["properties"]["sup"])
    fc = {"type": "FeatureCollection",
          "metadata": {"title": "SUP-/Bootsverleih an Badestellen",
                       "source": "OpenStreetMap (Overpass) – Verleih im Umkreis von 350 m einer Badestelle",
                       "license": "ODbL", "generated": time.strftime("%Y-%m-%d %H:%M"),
                       "total": len(feats), "sup_explicit": sup_n},
          "features": feats}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "sup.js"), "w", encoding="utf-8") as f:
        f.write("window.SUP="); json.dump(fc, f, ensure_ascii=False, separators=(",", ":")); f.write(";")
    print(f"✅ {len(feats)} Verleih-Stellen an Badeplätzen ({sup_n} explizit SUP) -> data/sup.js")

if __name__ == "__main__":
    main()
