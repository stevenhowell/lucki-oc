"""Lucky — score candidate parcels across Orange County.

Reads the cached public layers in cache/ and writes site/candidates.json.
Pure Python (no shapely): point-in-polygon by ray casting on centroids.
Every score component is kept on the record so the page can show its work.
"""
import json, math, csv, collections, sys, urllib.request, urllib.parse, time
from pathlib import Path

C = Path(__file__).parent / "cache"
OUT = Path(__file__).parent / "site"
OUT.mkdir(exist_ok=True)
DATA = Path(__file__).parent.parent / "data"

def load(name):
    return json.load(open(C / name))

# ---------- geometry helpers ----------
def rings(geom):
    if not geom: return []
    t = geom["type"]
    if t == "Polygon": return [geom["coordinates"]]
    if t == "MultiPolygon": return geom["coordinates"]
    return []

def centroid(geom):
    pts = [p for poly in rings(geom) for p in poly[0]]
    if not pts: return None
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))

def bbox(geom):
    pts = [p for poly in rings(geom) for ring in poly for p in ring]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return (min(xs),min(ys),max(xs),max(ys))

def pip(pt, ring):
    x,y=pt; inside=False; n=len(ring)
    for i in range(n):
        x1,y1=ring[i]; x2,y2=ring[(i+1)%n]
        if (y1>y)!=(y2>y):
            xi=(x2-x1)*(y-y1)/((y2-y1) or 1e-12)+x1
            if x<xi: inside=not inside
    return inside

def in_geom(pt, geom):
    for poly in rings(geom):
        if pip(pt, poly[0]) and not any(pip(pt, h) for h in poly[1:]): return True
    return False

class Index:
    """bbox-prefiltered polygon lookup"""
    def __init__(self, feats, keyfn):
        self.items=[(bbox(f["geometry"]), f["geometry"], keyfn(f["properties"])) for f in feats if f.get("geometry")]
    def find(self, pt):
        x,y=pt
        for (x0,y0,x1,y1),g,k in self.items:
            if x0<=x<=x1 and y0<=y<=y1 and in_geom(pt,g): return k
        return None

def dist_m(a,b):
    dx=(a[0]-b[0])*math.cos(math.radians((a[1]+b[1])/2))*111320; dy=(a[1]-b[1])*110540
    return math.hypot(dx,dy)

# ---------- layers ----------
religious = load("oc_elu_religious.geojson")["features"]
vacant = load("oc_elu_vacant.geojson")["features"]
he = load("oc_he_sites.geojson")["features"]
zoning = load("oc_zoning_by_apn.json")
noa = load("oc_noa.json")
flood = Index([f for f in load("oc_flood.geojson")["features"] if (f["properties"].get("FLD_ZONE") or "").strip().upper() not in ("X","")], lambda p: "FEMA zone " + (p.get("FLD_ZONE") or "?"))
liq = Index(load("oc_liquefaction.geojson")["features"], lambda p: "liquefaction zone")
fire = Index(load("oc_fire_lra.geojson")["features"], lambda p: p.get("HAZ_CLASS") or p.get("FHSZ") or "fire hazard zone")
tcac_feats = load("oc_tcac2021.geojson")["features"] if (C/"oc_tcac2021.geojson").exists() else []
tcac = Index(tcac_feats, lambda p: p.get("oppcat"))
hqta = Index(load("oc_hqta.geojson")["features"], lambda p: p.get("hqta_type"))
try:
    osm = load("osm_worship_oc.json")["elements"]
except Exception:
    osm = []
osm_pts = []
for e in osm:
    lat = e.get("lat") or (e.get("center") or {}).get("lat"); lon = e.get("lon") or (e.get("center") or {}).get("lon")
    if lat and lon: osm_pts.append(((lon,lat), e.get("tags",{})))

# city-level market + ACS numbers (from data/)
zhvi = {r["city"]: r for r in csv.DictReader(open(DATA/"zillow_zhvi_oc_cities.csv"))}
condo = {r["city"]: r for r in csv.DictReader(open(DATA/"zillow_oc_condo_rent.csv"))}
acs = {r["city"]: r for r in csv.DictReader(open(DATA/"acs_oc_cities.csv"))}
hcd = json.load(open(DATA/"hcd_income_limits_oc_2026.json"))
LOW4 = hcd["limits_by_household_1_to_8"]["low"][3]      # 148,850 top of low
VLOW4 = hcd["limits_by_household_1_to_8"]["very_low"][3] # 93,050 top of very-low = bottom of low
RATE_FHA = 0.06625  # CalHFA FHA 2026-11-06
def pmt_to_principal(p, r, n=360):
    m=r/12; return p*n if m==0 else p*(1-(1+m)**-n)/m
def affordable_price(income, rate, tax=0.011, hoa=350, ins=120, share=0.30):
    monthly = income*share/12
    # iterate: price such that P&I(price) + tax/12*price + hoa + ins = monthly
    lo,hi=0,3_000_000
    for _ in range(40):
        mid=(lo+hi)/2
        m=rate/12; pi = mid*m/(1-(1+m)**-360) if m else mid/360
        if pi + mid*tax/12 + hoa + ins > monthly: hi=mid
        else: lo=mid
    return round(lo,-3)
AFF = {"fha_6625": affordable_price(VLOW4, RATE_FHA), "rate_3": affordable_price(VLOW4, 0.03), "rate_0": affordable_price(VLOW4, 0.0)}

# city programs we could verify (everything else: unknown)
CITY_PROGRAMS = {
    "Santa Ana": {"program": "Inclusionary Housing Fund down-payment silent seconds", "per_unit": 80000,
                  "source": "City of Santa Ana pre-commitment letter A-2025-094 (2025-07-01), 425 E. Wellington Ave: $720,000 for 9 units"},
}

def city_name(p):
    c = (p.get("CITY") or p.get("Jurisdiction") or "").title().replace("Of ", "of ")
    return {"Unincorporated": "Orange County (unincorporated)", "Orange County": "Orange County (unincorporated)"}.get(c, c)

# ---------- candidates ----------
cands = {}
def add(f, source, extra=None):
    p = f["properties"]; g = f.get("geometry")
    apn = p.get("APN24") or p.get("Assessor_Parcel_Number") or extra.get("apn") if extra else p.get("APN24")
    if not apn: return
    c = cands.get(apn)
    if not c:
        ct = centroid(g) if g else (extra or {}).get("pt")
        if not ct: return
        c = cands[apn] = {"apn": apn, "city": city_name(p) or (extra or {}).get("city",""), "sources": [], "centroid": [round(ct[0],6), round(ct[1],6)],
                          "acres": round(float(p.get("ACRES") or 0),3), "geometry": g, "lu24": p.get("LU24"), "slope": p.get("SLOPE")}
    if source not in c["sources"]: c["sources"].append(source)
    if extra: c.update({k:v for k,v in extra.items() if k not in ("apn","pt","city")})

for f in religious: add(f, "religious_use")
for f in vacant: add(f, "vacant")
for f in he:
    p=f["properties"]
    add(f, "housing_element_site", {"he_capacity": int(p.get("Total_HE_Capacity") or 0), "he_low": int(p.get("Low_Income_HE_Capacity") or 0), "he_year": p.get("YEAR")})

# surplus-land notices: match by APN (normalize) else add as point candidates
def norm_apn(a): return (a or "").replace("-","").replace(" ","")[:8]
by_norm = {norm_apn(a): a for a in cands}
for r in noa:
    a = norm_apn(r.get("APN")); key = by_norm.get(a)
    extra = {"noa_status": r.get("NOA Status"), "noa_issued": r.get("Date Notice Issued"), "noa_agency": r.get("Local Agency"),
             "noa_contact": r.get("Notice Contact Information- Concatenated"), "noa_use": r.get("Existing Use/Vacancy"), "noa_address": r.get("Address"),
             "noa_size": r.get("Parcel Size (Gross Acres)"), "noa_link": r.get("Notice Website Link")}
    if key:
        cands[key]["sources"].append("surplus_land_notice"); cands[key].update(extra)
    else:
        try: pt=(float(r["x"]), float(r["y"]))
        except: continue
        apn = r.get("APN") or f"noa-{r.get('Parent Case')}-{r.get('Address')}"
        cands[apn] = {"apn": apn, "city": (r.get("City") or r.get("Local Agency") or "").title(), "sources": ["surplus_land_notice"],
                      "centroid": [round(pt[0],6), round(pt[1],6)], "acres": 0, "geometry": None, **extra}

# ---------- enrich ----------
for apn, c in cands.items():
    pt = tuple(c["centroid"])
    z = zoning.get(apn, {})
    c["zoning_city_code"] = z.get("ZN24_CITY"); c["zoning_scag"] = z.get("ZN24_SCAG")
    if not c.get("city") and z.get("CITY"): c["city"] = z["CITY"].title()
    c["hazards"] = {"flood": flood.find(pt) or "none found", "liquefaction": liq.find(pt) or "none found", "fire_lra": fire.find(pt) or "none found"}
    c["tcac_2021"] = tcac.find(pt) or "unknown"
    c["hqta"] = hqta.find(pt) or "no"
    # worship name within 80 m (proxy for the institution's public name)
    best=None
    for (p2, tags) in osm_pts:
        d=dist_m(pt,p2)
        if d<80 and (best is None or d<best[0]): best=(d,tags)
    if best:
        t=best[1]; c["worship"] = {"name": t.get("name"), "religion": t.get("religion"), "denomination": t.get("denomination"), "website": t.get("website") or t.get("contact:website"), "phone": t.get("phone") or t.get("contact:phone"), "distance_m": round(best[0])}
    # fund line
    city = c.get("city") or ""
    cz = zhvi.get(city) or {}; cc = condo.get(city) or {}
    typical_condo = int(float(cc.get(next((k for k in cc if k.startswith("condo_zhvi")), ""), 0) or 0)) if cc else 0
    typical_home = int(float(cz.get(next((k for k in cz if k.startswith("zhvi_") and "2026" in k), ""), 0) or 0)) if cz else 0
    prog = CITY_PROGRAMS.get(city)
    c["fund"] = {"typical_condo_value": typical_condo or None, "typical_home_value": typical_home or None,
                 "affordable_price_low_income_4p": AFF, "city_program": prog or "unknown",
                 "gap_condo_at_fha": (typical_condo - AFF["fha_6625"] - (prog or {}).get("per_unit",0)) if typical_condo else None,
                 "gap_condo_at_0pct": (typical_condo - AFF["rate_0"] - (prog or {}).get("per_unit",0)) if typical_condo else None}

# ---------- score ----------
RES_SCAG = {"1100","1110","1111","1112","1113","1120","1121","1122","1123","1600"}  # residential / mixed (SCAG zoning categories)
def score(c):
    s = {}
    src = c["sources"]
    s["pathway"] = 30 if "housing_element_site" in src else 25 if "religious_use" in src else 20 if "surplus_land_notice" in src else 10
    a = c.get("acres") or 0
    s["size"] = 20 if a >= 1 else 15 if a >= 0.5 else 10 if a >= 0.25 else 5 if a >= 0.1 else 0
    zs = c.get("zoning_scag") or ""
    s["zoning"] = 15 if zs in RES_SCAG else 8 if zs else 0
    h = c["hazards"]
    bad = sum(1 for v in h.values() if v != "none found")
    s["hazards"] = 15 if bad == 0 else 5 if bad == 1 else 0
    s["transit"] = 10 if c["hqta"] != "no" else 0
    t = c.get("tcac_2021") or ""
    s["opportunity"] = 10 if "High" in t and "Segregation" not in t else 6 if "Moderate" in t else 3 if "Low" in t else 0
    s["fund"] = 10 if c["fund"]["city_program"] != "unknown" else 0
    if c.get("slope") and float(c["slope"] or 0) > 15: s["slope_penalty"] = -15
    c["score_parts"] = s; c["score"] = sum(s.values())
    return c["score"]

ranked = sorted(cands.values(), key=score, reverse=True)
# keep geometry only for top 400 to keep the file small
for i,c in enumerate(ranked):
    c["rank"] = i+1
    if i >= 400: c.pop("geometry", None)
by_city = collections.Counter(c["city"] for c in ranked)
meta = {"generated": time.strftime("%Y-%m-%d %H:%M"), "n_candidates": len(ranked), "by_city": by_city.most_common(),
        "sources": {"religious_use": "SCAG Existing Land Use 2024, LU24=1245 Religious Facilities (code list: SCAG 2016 legend; 2024 list not re-verified)",
                    "vacant": "SCAG Existing Land Use 2024, LU24=3100 Vacant", "housing_element_site": "SCAG HousingElementSite_poly_scag, COUNTY='Orange'",
                    "surplus_land_notice": "HCD Surplus Land Act Notices of Availability (data.ca.gov, modified 2026-10-30); all OC rows are status Archive",
                    "zoning": "SCAG Zoning_poly_OR 2024 (ZN24_CITY local code, ZN24_SCAG regional category)",
                    "flood": "OC Public Works Floodplains", "liquefaction": "OC Public Works Liquefaction (CGS zones)", "fire": "OC Fire Hazard Severity Zones LRA",
                    "tcac": "SCAG TCAC 2021 Opportunity Areas (2026 map not loaded)", "hqta": "Caltrans CA HQ Transit Areas",
                    "worship_names": "OpenStreetMap amenity=place_of_worship within 80 m (ODbL)", "values": "Zillow ZHVI Sep 2026", "income": "HCD 2026 State Income Limits, Orange County",
                    "rate": "CalHFA FHA 6.625% (2026-11-06)", "aerials": "OC Public Works Aerial_Imagery_Countywide 22_OC_3IN_SP6 (2022, 3-inch)"},
        "assumptions": {"affordability": "4-person household at $93,050 (bottom of HCD low band); 30% of income; 1.1% property tax; HOA $350/mo; insurance $120/mo — ASSUMPTION",
                        "scoring_weights": "pathway 30 / size 20 / zoning 15 / hazards 15 / transit 10 / opportunity 10 / city program 10; slope >15% −15 — ASSUMPTION",
                        "ownership": "religious-use parcels are a proxy for SB 4 eligibility; ownership not verified"}}
json.dump({"meta": meta, "candidates": ranked}, open(OUT/"candidates.json","w"))
print("candidates", len(ranked), "top cities", by_city.most_common(8))
print("top 10:", [(c["rank"], c["city"], c["apn"], c["sources"], c["score"]) for c in ranked[:10]])
print("file MB", round((OUT/"candidates.json").stat().st_size/1e6,1))
