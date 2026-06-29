#!/usr/bin/env python3
"""
Zeichnet die amtlichen Wasserski-Strecken als LINIEN entlang des Flusslaufs.

Robuster Ansatz ohne Zusammensetzen der Flussgeometrie:
Die Fluss-km-Marken (waterway=milestone) liegen selbst auf dem Fluss und
tragen ihren km-Wert. Für eine Strecke km_von–km_bis werden die Marken in
diesem Bereich nach km sortiert verbunden; die Endpunkte werden zwischen den
benachbarten Marken interpoliert. So folgt die Linie dem realen Flusslauf.

Ausgabe: data/strecken_lines.js  ->  window.WS_LINES (GeoJSON LineStrings)
Aufruf:  python3 build_strecken_lines.py
"""
import json, re, os, time, urllib.request, urllib.parse, sys

EP = ["https://overpass-api.de/api/interpreter",
      "https://overpass.kumi.systems/api/interpreter"]
UA = "wassersport-karte/1.0"

RIVER_OSM = {
    "Main": ["Main"],
    "Neckar": ["Neckar"],
    "Donau": ["Donau"],
    "Main-Donau-Kanal / Regnitz": ["Main-Donau-Kanal", "Regnitz"],
}

def overpass(q):
    data = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(6):
        ep = EP[attempt % len(EP)]
        try:
            req = urllib.request.Request(ep, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=200) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            wait = 12 + attempt * 12
            sys.stderr.write(f"  overpass retry (warte {wait}s): {e}\n"); time.sleep(wait)
    raise RuntimeError("overpass failed")

def fetch_marks(name):
    """Nur die km-Marken im Umkreis des Flusses (leichtgewichtig)."""
    q = (f'[out:json][timeout:180];area["ISO3166-1"="DE"][admin_level=2]->.de;'
         f'way["waterway"]["name"="{name}"](area.de)->.r;'
         f'node(around.r:250)["waterway"="milestone"]'
         f'["seamark:distance_mark:units"="kilometres"]->.m;'
         f'.m out;')
    out = []
    for el in overpass(q).get("elements", []):
        if el.get("lat") is None: continue
        try:
            km = float(el["tags"]["seamark:distance_mark:distance"])
        except Exception:
            continue
        out.append((km, el["lat"], el["lon"]))
    return out

def dedupe(marks):
    """Marken mit gleichem km mitteln (linke/rechte Ufermarke)."""
    by = {}
    for km, la, lo in marks:
        by.setdefault(km, []).append((la, lo))
    res = []
    for km, pts in by.items():
        la = sum(p[0] for p in pts)/len(pts); lo = sum(p[1] for p in pts)/len(pts)
        res.append((km, la, lo))
    res.sort()
    return res

def lerp(p, q, t): return (p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t)

def point_at(marks, km):
    """Koordinate für einen km-Wert zwischen den Nachbarmarken interpolieren."""
    if km <= marks[0][0] or km >= marks[-1][0]:
        return None
    for i in range(len(marks)-1):
        k0, la0, lo0 = marks[i]; k1, la1, lo1 = marks[i+1]
        if k0 <= km <= k1 and k1 > k0:
            t = (km-k0)/(k1-k0)
            return lerp((la0, lo0), (la1, lo1), t)
    return None

def build_line(marks, a, b):
    """LineString-Koordinaten [lon,lat] für km a..b, oder None."""
    lo, hi = min(a, b), max(a, b)
    pA, pB = point_at(marks, lo), point_at(marks, hi)
    if pA is None or pB is None:
        return None
    inner = [(la, lo_) for (km, la, lo_) in marks if lo < km < hi]
    pts = [pA] + inner + [pB]
    coords = []
    for la, lo_ in pts:
        c = [round(lo_, 6), round(la, 6)]
        if not coords or coords[-1] != c:
            coords.append(c)
    return coords if len(coords) >= 2 else None

def parse_km(s):
    s = s.replace("–", "-").replace(",", ".")
    m = re.findall(r"\d+\.\d+", s)
    return (float(m[0]), float(m[1])) if len(m) >= 2 else None

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    strecken = json.load(open(os.path.join(base, "data", "wasserski_strecken.geojson"), encoding="utf-8"))
    by_river = {}
    for f in strecken["features"]:
        p = f["properties"]
        if p.get("conf") != "approx": continue
        by_river.setdefault(p["river"], []).append(p)

    out_feats, stats = [], {}
    for river in ["Main", "Donau", "Neckar", "Main-Donau-Kanal / Regnitz"]:
        if river not in by_river: continue
        names = RIVER_OSM.get(river, [])
        print(f"\n▶ {river}: lade km-Marken …", flush=True)
        try:
            marks = []
            for nm in names:
                marks += fetch_marks(nm); time.sleep(6)
            marks = dedupe(marks)
            print(f"  km-Marken: {len(marks)}" + (f"  (km {marks[0][0]:.0f}–{marks[-1][0]:.0f})" if marks else ""))
            if len(marks) < 2:
                print("  ⚠️ keine km-Marken – Strecken bleiben Punkte"); stats[river] = f"0/{len(by_river[river])}"; continue
            done = 0
            for p in by_river[river]:
                rng = parse_km(p["km"])
                if not rng: continue
                line = build_line(marks, *rng)
                if not line: continue
                out_feats.append({"type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": line},
                    "properties": {"river": river, "km": p["km"], "desc": p["desc"],
                                   "land": p["land"], "times": p.get("times", "")}})
                done += 1
            stats[river] = f"{done}/{len(by_river[river])}"
            print(f"  ✅ {done}/{len(by_river[river])} Strecken als Linie")
        except Exception as e:
            print(f"  ⚠️ Fehler bei {river}: {e}")
        time.sleep(4)

    fc = {"type": "FeatureCollection",
          "metadata": {"title": "Amtliche Wasserski-Strecken als Linien (E.17)",
                       "source": "Strecken: BMV/WSV & ELWIS · km-Marken/Flusslauf: OSM (ODbL)",
                       "note": "Linien verbinden die OSM-Fluss-km-Marken im jeweiligen Abschnitt. "
                               "Anfang/Ende auf wenige hundert Meter genau – maßgeblich ist E.17 vor Ort.",
                       "generated": time.strftime("%Y-%m-%d %H:%M"),
                       "stats": stats, "total": len(out_feats)},
          "features": out_feats}
    with open(os.path.join(base, "data", "strecken_lines.js"), "w", encoding="utf-8") as f:
        f.write("window.WS_LINES="); json.dump(fc, f, ensure_ascii=False, separators=(",", ":")); f.write(";")
    print(f"\n=== Gesamt: {len(out_feats)} Linien · {stats} ===")

if __name__ == "__main__":
    main()
