"""Turn data/council_records.json into site/council.json:
{byCity: {city: [record...]}, byApn: {apn: [record...]}}. Each record with an address is geocoded once
(ArcGIS World geocoder, cached in cache/geocode.json) and attached to the nearest Lucki site within 80 m."""
import json, math, urllib.request, urllib.parse, time
from pathlib import Path
B = Path(__file__).parent; S = B/"site"; DATA = B.parent/"data"
R = json.load(open(DATA/"council_records.json"))
C = json.load(open(S/"candidates.json"))["candidates"]
GC = B/"cache"/"geocode.json"; gc = json.load(open(GC)) if GC.exists() else {}
def geocode(addr, city):
    k = f"{addr}, {city}, CA"
    if k in gc: return gc[k]
    q = urllib.parse.urlencode({"SingleLine": k, "maxLocations": 1, "outFields": "Match_addr", "f": "json"})
    try:
        d = json.load(urllib.request.urlopen("https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?" + q, timeout=20))
        c = (d.get("candidates") or [None])[0]
        gc[k] = [c["location"]["x"], c["location"]["y"], c["score"]] if c and c["score"] >= 85 else None
    except Exception: gc[k] = None
    time.sleep(0.2); return gc[k]
def dist(a, b):
    return math.hypot((a[0]-b[0])*111320*math.cos(math.radians(a[1])), (a[1]-b[1])*110540)
CITYFIX = {"orange county": "Orange County (unincorporated)"}
byCity, byApn = {}, {}
for r in R:
    city = (r.get("city") or "").strip(); city = CITYFIX.get(city.lower(), city)
    rec = {k: r.get(k) for k in ("date", "body", "address", "project", "units", "tenure", "decision", "money", "issues", "summary", "url")}
    byCity.setdefault(city, []).append(rec)
    apn = (r.get("apn") or "").replace("-", "")
    hit = next((c for c in C if apn and c["apn"].replace("-", "") == apn), None)
    if not hit and r.get("address"):
        g = geocode(r["address"], city)
        if g:
            near = min(((dist(g[:2], c["centroid"]), c) for c in C if c["city"] == city), default=(1e9, None), key=lambda t: t[0])
            if near[0] <= 80: hit = near[1]; rec["match_m"] = round(near[0])
    if hit: byApn.setdefault(hit["apn"], []).append(rec)
for v in byCity.values(): v.sort(key=lambda r: r.get("date") or "", reverse=True)
json.dump(gc, open(GC, "w"))
json.dump({"byCity": byCity, "byApn": byApn}, open(S/"council.json", "w"), separators=(",", ":"))
print("records", len(R), "cities", len(byCity), "matched to sites", sum(len(v) for v in byApn.values()), list(byApn)[:10])
