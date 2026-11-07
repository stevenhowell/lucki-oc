"""Simplify the cached public layers into small GeoJSON overlays for the page (site/layers/*.json),
and give every candidate a simplified parcel outline."""
import json, math
from pathlib import Path
B = Path(__file__).parent; C = B / "cache"; S = B / "site"; L = S / "layers"; L.mkdir(exist_ok=True)

def rdp(pts, eps):
    if len(pts) < 4: return pts
    a, b = pts[0], pts[-1]; dmax, idx = 0, 0
    ax, ay = a; bx, by = b; dx, dy = bx-ax, by-ay; n = math.hypot(dx, dy) or 1e-12
    for i in range(1, len(pts)-1):
        px, py = pts[i]; d = abs(dy*px - dx*py + bx*ay - by*ax)/n
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return rdp(pts[:idx+1], eps)[:-1] + rdp(pts[idx:], eps)
    return [a, b]

def simp_geom(g, eps, nd=5):
    if not g: return None
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"] if g["type"] == "MultiPolygon" else None
    if polys is None:
        if g["type"] == "Point": return {"type":"Point","coordinates":[round(v,nd) for v in g["coordinates"]]}
        return None
    out = []
    for poly in polys:
        rings = []
        for ring in poly:
            pts = [(round(x,nd), round(y,nd)) for x, y in ring]
            h = len(pts)//2
            r = rdp(pts[:h+1], eps)[:-1] + rdp(pts[h:], eps) if len(pts) > 8 else pts
            if len(r) >= 4: rings.append([list(p) for p in r])
        if rings: out.append(rings)
    if not out: return None
    return {"type":"MultiPolygon","coordinates":out} if len(out) > 1 else {"type":"Polygon","coordinates":out[0]}

def layer(src, name, keep, eps, filt=lambda p: True):
    fs = json.load(open(C/src))["features"]; out = []
    for f in fs:
        p = f.get("properties") or {}
        if not filt(p): continue
        g = simp_geom(f.get("geometry"), eps)
        if g: out.append({"type":"Feature","properties":{k: p.get(k) for k in keep},"geometry":g})
    json.dump({"type":"FeatureCollection","features":out}, open(L/f"{name}.json","w"), separators=(",",":"))
    print(name, len(out), round((L/f"{name}.json").stat().st_size/1e6, 2), "MB")

layer("oc_flood.geojson", "flood", ["FLD_ZONE"], 0.0004, lambda p: (p.get("FLD_ZONE") or "").strip().upper() not in ("X", ""))
layer("oc_liquefaction.geojson", "liquefaction", [], 0.0004)
layer("oc_fire_lra.geojson", "fire", ["HAZ_CLASS", "FHSZ"], 0.0004)
layer("oc_hqta.geojson", "transit", ["hqta_type"], 0.0003)
layer("oc_tcac2021.geojson", "opportunity", ["oppcat"], 0.0003)
layer("oc_he_sites.geojson", "housing_element", ["Jurisdiction", "Total_HE_Capacity"], 0.00002)

# candidate parcel outlines for every candidate (small eps keeps lot shape)
src = {}
for name in ("oc_elu_religious.geojson", "oc_elu_vacant.geojson", "oc_he_sites.geojson"):
    for f in json.load(open(C/name))["features"]:
        a = (f.get("properties") or {}).get("APN24")
        if a and f.get("geometry") and a not in src: src[a] = f["geometry"]
D = json.load(open(S/"candidates.json"))
for c in D["candidates"]:
    g = src.get(c["apn"])
    c["geometry"] = simp_geom(g, 0.000005, 6) if g else None
json.dump(D, open(S/"candidates.json","w"), separators=(",",":"))
print("candidates.json", round((S/"candidates.json").stat().st_size/1e6, 2), "MB")
