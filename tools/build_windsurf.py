#!/usr/bin/env python3
"""
Holt Windsurf-bezogene Orte (Schulen, Verleih, Surfshops, Spots) bundesweit
aus OSM und speichert data/windsurf.js -> window.WINDSURF.
OSM trennt „Verleih" nicht sauber; wir sammeln daher Windsurf-Schulen/-Spots/
-Shops und markieren, wo Verleih wahrscheinlich ist (Name/Tags).
"""
import json, re, os, time, urllib.request, urllib.parse, sys

EP = ["https://overpass-api.de/api/interpreter",
      "https://overpass.kumi.systems/api/interpreter"]

QUERY = ('[out:json][timeout:240];area["ISO3166-1"="DE"][admin_level=2]->.de;('
         'nwr["sport"~"windsurf"](area.de);'
         'nwr["leisure"="sports_centre"]["sport"="surfing"](area.de);'
         'nwr["shop"="watersports"](area.de);'
         'nwr["club"="watersports"](area.de);'
         'nwr["name"~"[Ww]indsurf"](area.de);'
         'nwr["name"~"[Ss]urfschule|[Ss]urfshop|[Ss]urf-?[Cc]enter|[Ww]assersportschule"](area.de);'
         ');out center tags;')

RENT_RE = re.compile(r"verleih|rental|vermiet|surfschule|surf school|wassersportschule|surf-?center|surfshop|surf shop", re.I)

def fetch():
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    last = None
    for ep in EP:
        for _ in range(3):
            try:
                req = urllib.request.Request(ep, data=data, headers={"User-Agent": "wassersport-karte/1.0"})
                with urllib.request.urlopen(req, timeout=260) as r:
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
        name = t.get("name", "")
        blob = " ".join([name, t.get("shop", ""), t.get("leisure", ""), t.get("sport", "")])
        rental = bool(RENT_RE.search(blob)) or t.get("shop") == "watersports" or "verleih" in name.lower()
        keep = {k: t[k] for k in ("name", "website", "phone", "opening_hours", "operator", "sport", "shop") if t.get(k)}
        keep["rental"] = rental
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                      "properties": keep})
    rentals = sum(1 for f in feats if f["properties"]["rental"])
    fc = {"type": "FeatureCollection",
          "metadata": {"title": "Windsurf – Schulen, Verleih, Shops, Spots",
                       "source": "OpenStreetMap (Overpass)", "license": "ODbL",
                       "generated": time.strftime("%Y-%m-%d %H:%M"),
                       "total": len(feats), "rental_likely": rentals},
          "features": feats}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "windsurf.js"), "w", encoding="utf-8") as f:
        f.write("window.WINDSURF="); json.dump(fc, f, ensure_ascii=False, separators=(",", ":")); f.write(";")
    print(f"✅ {len(feats)} Windsurf-Orte ({rentals} mit wahrscheinl. Verleih) -> data/windsurf.js")

if __name__ == "__main__":
    main()
