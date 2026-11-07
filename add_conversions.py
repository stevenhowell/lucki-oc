"""Add the Wellington model: small low-rise apartment buildings (SCAG LU24 1123, 0.15-0.45 acres) that a nonprofit
could buy and convert to ownership condos. Reads cache/candidates_v1_backup.json, writes site/candidates.json with the
new sites appended (points only, no outline). Run rank.py after this."""
import json, math, urllib.request, urllib.parse, time, csv
from pathlib import Path
B = Path(__file__).parent; C_ = B/"cache"; S = B/"site"; DATA = B.parent/"data"
URL = "https://maps.scag.ca.gov/scaggis/rest/services/LDX/Existinglanduse_poly_OR/MapServer/0/query"
cache = C_/"oc_elu_lowrise_apts.geojson"
if not cache.exists():
    feats = []; off = 0
    while True:
        q = urllib.parse.urlencode({"where": "LU24='1123' AND ACRES>=0.15 AND ACRES<=0.45", "outFields": "APN24,CITY,LU24,ACRES,SLOPE",
                                    "outSR": 4326, "f": "geojson", "resultOffset": off, "resultRecordCount": 2000, "geometryPrecision": 6})
        d = json.load(urllib.request.urlopen(URL + "?" + q, timeout=240)); f = d.get("features", []); feats += f
        if len(f) < 2000: break
        off += len(f)
    json.dump({"type": "FeatureCollection", "features": feats}, open(cache, "w")); print("fetched", len(feats))
F = json.load(open(cache))["features"]
D = json.load(open(C_/"candidates_v1_backup.json")); have = {c["apn"] for c in D["candidates"]}

def rings(g): return [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"] if g["type"] == "MultiPolygon" else []
def centroid(g):
    pts = [p for poly in rings(g) for p in poly[0]]
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)) if pts else None
def bbox(g):
    pts = [p for poly in rings(g) for ring in poly for p in ring]; xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
def pip(pt, ring):
    x, y = pt; ins = False
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i+1) % len(ring)]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/((y2-y1) or 1e-12)+x1: ins = not ins
    return ins
class Index:
    def __init__(s, feats, key): s.items = [(bbox(f["geometry"]), f["geometry"], key(f["properties"])) for f in feats if f.get("geometry") and rings(f["geometry"])]
    def find(s, pt):
        for (x0, y0, x1, y1), g, k in s.items:
            if x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1 and any(pip(pt, p[0]) for p in rings(g)): return k
        return None
L = lambda n: json.load(open(C_/n))["features"]
flood = Index([f for f in L("oc_flood.geojson") if (f["properties"].get("FLD_ZONE") or "").strip().upper() not in ("X", "")], lambda p: "FEMA zone " + (p.get("FLD_ZONE") or "?"))
liq = Index(L("oc_liquefaction.geojson"), lambda p: "liquefaction zone")
fire = Index(L("oc_fire_lra.geojson"), lambda p: p.get("HAZ_CLASS") or "fire hazard zone")
tcac = Index(L("oc_tcac2021.geojson"), lambda p: p.get("oppcat"))
hqta = Index(L("oc_hqta.geojson"), lambda p: p.get("hqta_type"))
zon = json.load(open(C_/"oc_zoning_by_apn.json"))
condo = {r["city"]: r for r in csv.DictReader(open(DATA/"zillow_oc_condo_rent.csv"))}
zh = {r["city"]: r for r in csv.DictReader(open(DATA/"zillow_zhvi_oc_cities.csv"))}
tmpl = D["candidates"][0]["fund"]["affordable_price_low_income_4p"]
PROG = {"Santa Ana": {"program": "Inclusionary Housing Fund down-payment silent seconds", "per_unit": 80000,
                      "source": "City of Santa Ana pre-commitment letter A-2025-094 (2025-07-01), 425 E. Wellington Ave: $720,000 for 9 units"}}
added = 0
for f in F:
    p = f["properties"]; apn = p.get("APN24"); g = f.get("geometry")
    if not apn or apn in have or not g: continue
    ct = centroid(g)
    if not ct: continue
    city = (p.get("CITY") or "").title().replace("Unincorporated", "Orange County (unincorporated)")
    cc = condo.get(city) or {}; tv = int(float(cc.get(next((k for k in cc if k.startswith("condo_zhvi")), ""), 0) or 0)) if cc else 0
    hz = zh.get(city) or {}; th = int(float(hz.get(next((k for k in hz if k.startswith("zhvi_") and "2026" in k), ""), 0) or 0)) if hz else 0
    prog = PROG.get(city)
    c = {"apn": apn, "city": city, "sources": ["conversion"], "centroid": [round(ct[0], 6), round(ct[1], 6)], "acres": round(float(p.get("ACRES") or 0), 3),
         "geometry": None, "lu24": "1123", "slope": p.get("SLOPE"), "zoning_city_code": (zon.get(apn) or {}).get("ZN24_CITY"), "zoning_scag": (zon.get(apn) or {}).get("ZN24_SCAG"),
         "hazards": {"flood": flood.find(ct) or "none found", "liquefaction": liq.find(ct) or "none found", "fire_lra": fire.find(ct) or "none found"},
         "tcac_2021": tcac.find(ct) or "unknown", "hqta": hqta.find(ct) or "no",
         "fund": {"typical_condo_value": tv or None, "typical_home_value": th or None, "affordable_price_low_income_4p": tmpl, "city_program": prog or "unknown",
                  "gap_condo_at_fha": (tv - tmpl["fha_6625"] - (prog or {}).get("per_unit", 0)) if tv else None,
                  "gap_condo_at_0pct": (tv - tmpl["rate_0"] - (prog or {}).get("per_unit", 0)) if tv else None},
         "score_parts": {}, "score": 0}
    D["candidates"].append(c); added += 1
D["meta"]["sources"]["conversion"] = "SCAG Existing Land Use 2024, LU24=1123 (low-rise apartments, condominiums and townhouses) on 0.15-0.45 acres; model: 425 E. Wellington Ave, Santa Ana (9 units on 0.21 acres)"
json.dump(D, open(S/"candidates.json", "w"), separators=(",", ":"))
print("added", added, "conversion sites; total", len(D["candidates"]))
