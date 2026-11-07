"""Pre-render county 3-inch aerials for the ranked sites (the artifact viewer cannot load them live).
Writes site/aerials/<apn>.jpg and site/aerials.json {apn: {bbox3857:[x0,y0,x1,y1], w, h}} plus site/overview.jpg.
"""
import json, math, urllib.request, urllib.parse, time, sys, collections
from pathlib import Path
S = Path(__file__).parent / "site"; A = S / "aerials"; A.mkdir(exist_ok=True)
D = json.load(open(S / "candidates.json")); C = D["candidates"]
def merc(lon, lat):
    x = lon * 20037508.34 / 180; y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180) * 20037508.34 / 180
    return x, y
def pts(geom):
    if not geom: return []
    polys = geom["coordinates"] if geom["type"] == "Polygon" else [p for mp in geom["coordinates"] for p in mp]
    return [p for ring in polys for p in ring]
def bbox_for(c):
    P = pts(c.get("geometry"))
    if P:
        xs = [merc(*p)[0] for p in P]; ys = [merc(*p)[1] for p in P]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    else:
        x, y = merc(*c["centroid"]); x0 = x1 = x; y0 = y1 = y
    w = max(x1 - x0, 60) * 1.7; h = max(y1 - y0, 40) * 1.7
    # keep 800x560 aspect
    if w / h < 800 / 560: w = h * 800 / 560
    else: h = w * 560 / 800
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
# pick sites: top 10 overall, top 10 per city, top 3 per city per pathway
want = []
want += C[:10]
by_city = collections.defaultdict(list)
for c in C: by_city[c["city"]].append(c)
for city, rows in by_city.items():
    want += rows[:10]
    for src in ("religious_use", "housing_element_site", "vacant", "surplus_land_notice"):
        want += [r for r in rows if src in r["sources"]][:3]
seen = set(); picks = [c for c in want if not (c["apn"] in seen or seen.add(c["apn"]))]
print("rendering", len(picks), flush=True)
meta = json.load(open(S / "aerials.json")) if (S / "aerials.json").exists() else {}
URL = "https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/22_OC_3IN_SP6/ImageServer/exportImage"
for i, c in enumerate(picks):
    out = A / f"{c['apn']}.jpg"
    if out.exists() and c["apn"] in meta: continue
    bb = bbox_for(c)
    q = urllib.parse.urlencode({"bbox": ",".join(f"{v:.2f}" for v in bb), "bboxSR": 3857, "imageSR": 3857, "size": "800,560", "format": "jpg", "f": "image"})
    for t in range(3):
        try:
            data = urllib.request.urlopen(URL + "?" + q, timeout=90).read()
            if data[:2] == b"\xff\xd8":
                out.write_bytes(data); meta[c["apn"]] = {"bbox3857": [round(v, 2) for v in bb], "w": 800, "h": 560}; break
            else: print("not jpeg", c["apn"], data[:80]); time.sleep(2)
        except Exception as e: print("retry", c["apn"], str(e)[:60], flush=True); time.sleep(3)
    if i % 25 == 0:
        json.dump(meta, open(S / "aerials.json", "w")); print(i, "done", flush=True)
json.dump(meta, open(S / "aerials.json", "w"))
# county overview (1-ft 2025 layer, whole county)
x0, y0 = merc(-118.13, 33.38); x1, y1 = merc(-117.41, 33.95)
w = x1 - x0; h = w * 1000 / 1600; cy = (y0 + y1) / 2; y0, y1 = cy - h / 2, cy + h / 2
OV = "https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage"
q = urllib.parse.urlencode({"bbox": f"{x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f}", "bboxSR": 3857, "imageSR": 3857, "size": "1600,1000", "format": "jpg", "f": "image"})
data = urllib.request.urlopen(OV + "?" + q, timeout=180).read()
(S / "overview.jpg").write_bytes(data)
json.dump({"bbox3857": [x0, y0, x1, y1], "w": 1600, "h": 1000}, open(S / "overview.json", "w"))
print("overview bytes", len(data), "sites rendered", len(meta), flush=True)
