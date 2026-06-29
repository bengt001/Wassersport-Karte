#!/usr/bin/env python3
"""
Holt die Flusskilometer-Marken (waterway=milestone) bundesweit aus OSM
und speichert sie als data/kmmarks.js -> window.KMMARKS.
So lassen sich die km-Angaben der Wasserski-Strecken auf der Karte abgleichen.
"""
import json, urllib.request, urllib.parse, os, time

EP = ["https://overpass-api.de/api/interpreter",
      "https://overpass.kumi.systems/api/interpreter"]

QUERY = ('[out:json][timeout:180];area["ISO3166-1"="DE"][admin_level=2]->.de;'
         'node["waterway"="milestone"]'
         '["seamark:distance_mark:units"="kilometres"](area.de);'
         'out qt;')

def fetch():
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    last = None
    for ep in EP:
        for _ in range(3):
            try:
                req = urllib.request.Request(ep, data=data, headers={"User-Agent": "wassersport-karte/1.0"})
                with urllib.request.urlopen(req, timeout=200) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                last = e; time.sleep(8)
    raise RuntimeError(last)

def main():
    osm = fetch()
    feats = []
    for el in osm.get("elements", []):
        if el.get("lat") is None: continue
        t = el.get("tags", {})
        try:
            km = float(t.get("seamark:distance_mark:distance"))
        except (TypeError, ValueError):
            continue
        name = t.get("seamark:name") or t.get("name") or ""
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(el["lon"], 6), round(el["lat"], 6)]},
                      "properties": {"km": km, "name": name}})
    fc = {"type": "FeatureCollection",
          "metadata": {"source": "OpenStreetMap (waterway=milestone)", "license": "ODbL",
                       "generated": time.strftime("%Y-%m-%d %H:%M"), "total": len(feats)},
          "features": feats}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "kmmarks.js"), "w", encoding="utf-8") as f:
        f.write("window.KMMARKS="); json.dump(fc, f, ensure_ascii=False, separators=(",", ":")); f.write(";")
    print(f"✅ {len(feats)} km-Marken gespeichert -> data/kmmarks.js")

if __name__ == "__main__":
    main()
