#!/usr/bin/env python3
"""
Baut eine lokale Datenbank (GeoJSON) für die Wassersport-Karte.
Fragt OpenStreetMap (Overpass) für GANZ Deutschland ab und speichert das
Ergebnis als data/spots.geojson, damit die Webseite nicht mehr live laden muss.

Aufruf:  python3 build_data.py
"""
import json, time, urllib.request, urllib.parse, os, sys

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Jede Kategorie wird einzeln abgefragt (vermeidet Timeouts bei landesweiter Suche).
# area DE = Deutschland.
HEADER = '[out:json][timeout:180];area["ISO3166-1"="DE"][admin_level=2]->.de;'

CATEGORIES = {
    "slip": [
        'nwr["leisure"="slipway"](area.de);',
    ],
    "ski": [
        'nwr["sport"="water_ski"](area.de);',
        'nwr["sport"="waterski"](area.de);',
        'nwr["leisure"="water_park"]["water_ski"](area.de);',
        'nwr["sport"="wakeboarding"](area.de);',
    ],
    "jet": [
        'nwr["sport"="jet_ski"](area.de);',
        'nwr["sport"="jetski"](area.de);',
        'nwr["sport"="personal_watercraft"](area.de);',
    ],
    "harbor": [
        'nwr["leisure"="marina"](area.de);',
    ],
}

def run_query(body):
    q = HEADER + "(" + "".join(body) + ");out center tags;"
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for ep in ENDPOINTS:
        for attempt in range(3):
            try:
                req = urllib.request.Request(ep, data=data,
                    headers={"User-Agent": "wassersport-karte/1.0 (build_data.py)"})
                with urllib.request.urlopen(req, timeout=200) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                last = e
                sys.stderr.write(f"  Versuch fehlgeschlagen ({ep}): {e}\n")
                time.sleep(5 + attempt * 5)
    raise RuntimeError(f"Abfrage endgültig fehlgeschlagen: {last}")

def to_features(kind, osm):
    feats = []
    seen = set()
    for el in osm.get("elements", []):
        tags = el.get("tags") or {}
        lat = el.get("lat", (el.get("center") or {}).get("lat"))
        lon = el.get("lon", (el.get("center") or {}).get("lon"))
        if lat is None or lon is None:
            continue
        key = (round(lat, 6), round(lon, 6))
        if key in seen:
            continue
        seen.add(key)
        # nur relevante Tags behalten -> Datei klein halten
        keep = {}
        for k in ("name", "fee", "surface", "access", "operator",
                  "website", "opening_hours", "phone", "ref"):
            if tags.get(k):
                keep[k] = tags[k]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {"kind": kind, **keep},
        })
    return feats

def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    all_feats = []
    stats = {}
    for kind, body in CATEGORIES.items():
        print(f"▶ Lade Kategorie '{kind}' …", flush=True)
        osm = run_query(body)
        feats = to_features(kind, osm)
        stats[kind] = len(feats)
        all_feats.extend(feats)
        print(f"  → {len(feats)} Einträge", flush=True)
        time.sleep(3)  # freundlich zum Server

    fc = {
        "type": "FeatureCollection",
        "metadata": {
            "source": "OpenStreetMap (Overpass API)",
            "license": "ODbL – © OpenStreetMap-Mitwirkende",
            "generated": time.strftime("%Y-%m-%d %H:%M"),
            "counts": stats,
            "total": len(all_feats),
        },
        "features": all_feats,
    }
    out = os.path.join(out_dir, "spots.geojson")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = os.path.getsize(out) / 1024
    print(f"\n✅ Gespeichert: {out}  ({size_kb:.0f} KB, {len(all_feats)} Orte)")
    print("   Aufschlüsselung:", stats)

if __name__ == "__main__":
    main()
