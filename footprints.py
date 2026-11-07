"""For each candidate parcel (church, city-approved, public land; empty lots are skipped), ask the county
Building_Footprints layer which buildings sit on it, and measure how much of the lot is not under a roof.
Writes cache/coverage.json {apn: {lot_m2, roof_m2, open_m2, n_buildings}}. 4 requests at a time, cached, resumable."""
import json, math, urllib.request, urllib.parse, time, concurrent.futures as cf
from pathlib import Path
B = Path(__file__).parent; OUT = B/"cache"/"coverage.json"
C = json.load(open(B/"site"/"candidates.json"))["candidates"]
done = json.load(open(OUT)) if OUT.exists() else {}
URL = "https://www.ocgis.com/arcpub/rest/services/Map_Layers/Building_Footprints/MapServer/0/query"

def rings(g): return [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
def area_m2(ring, lat0):
    k = math.cos(math.radians(lat0)); s = 0
    for i in range(len(ring)-1):
        x1, y1 = ring[i][0]*111320*k, ring[i][1]*110540; x2, y2 = ring[i+1][0]*111320*k, ring[i+1][1]*110540
        s += x1*y2 - x2*y1
    return abs(s)/2
def poly_area(g, lat0): return sum(area_m2(p[0], lat0) - sum(area_m2(h, lat0) for h in p[1:]) for p in rings(g))
def pip(pt, ring):
    x, y = pt; ins = False
    for i in range(len(ring)-1):
        x1, y1 = ring[i]; x2, y2 = ring[i+1]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/((y2-y1) or 1e-12)+x1: ins = not ins
    return ins
def inside(pt, g): return any(pip(pt, p[0]) for p in rings(g))

def work(c):
    g = c["geometry"]; pts = [p for poly in rings(g) for p in poly[0]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; lat0 = sum(ys)/len(ys)
    q = urllib.parse.urlencode({"geometry": f"{min(xs)},{min(ys)},{max(xs)},{max(ys)}", "geometryType": "esriGeometryEnvelope", "inSR": 4326,
                                "spatialRel": "esriSpatialRelIntersects", "outFields": "Height", "returnGeometry": "true", "outSR": 4326, "f": "geojson"})
    for t in range(3):
        try:
            d = json.load(urllib.request.urlopen(URL+"?"+q, timeout=60)); break
        except Exception: time.sleep(2+t*3)
    else: return c["apn"], None
    lot = poly_area(g, lat0); roof = 0; n = 0
    for f in d.get("features", []):
        fg = f.get("geometry")
        if not fg or fg["type"] not in ("Polygon", "MultiPolygon"): continue
        fp = [p for poly in rings(fg) for p in poly[0]]
        cen = (sum(p[0] for p in fp)/len(fp), sum(p[1] for p in fp)/len(fp))
        if inside(cen, g): roof += poly_area(fg, lat0); n += 1
    return c["apn"], {"lot_m2": round(lot), "roof_m2": round(roof), "open_m2": round(max(0, lot-roof)), "n_buildings": n}

import sys
extra = set(json.load(open(B/"cache"/"vacant_to_check.json"))) if "--vacant" in sys.argv else set()
todo = [c for c in C if c.get("geometry") and c["apn"] not in done and (set(c["sources"]) != {"vacant"} or c["apn"] in extra)]
print("to measure", len(todo), "already", len(done), flush=True)
with cf.ThreadPoolExecutor(4) as ex:
    for i, (apn, r) in enumerate(ex.map(work, todo)):
        if r: done[apn] = r
        if i % 200 == 0:
            json.dump(done, open(OUT, "w")); print(i, "measured", flush=True)
json.dump(done, open(OUT, "w")); print("done", len(done), flush=True)
