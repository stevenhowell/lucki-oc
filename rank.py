"""Lucki ranking v2: how many homes could go here, and would they pencil.
Reads site/candidates.json + cache/coverage.json, writes homes, open land and a plain-language reason onto each site,
re-sorts, and re-ranks. Every assumption is in ASSUMPTIONS and on the page."""
import json, math
from pathlib import Path
B = Path(__file__).parent; S = B/"site"
D = json.load(open(S/"candidates.json")); C = D["candidates"]
COV = json.load(open(B/"cache"/"coverage.json"))
SFR = {"1110", "1111", "1112", "1113"}
A = {
  "density_per_acre": 20,          # ASSUMPTION: townhome-scale ownership homes per acre of open land
  "church_share_of_open": 0.5,     # ASSUMPTION: a congregation keeps half its open land (parking, play space)
  "sb9_cap": 4,                    # SB 9: lot split + duplex on each half, up to 4 homes (HCD SB 9 fact sheet)
  "sb684_cap": 10,                 # SB 684 / SB 1123: up to 10 homes without a hearing (HCD fact sheets)
  "hazard_factor": 0.6,            # ASSUMPTION: a site in a flood, fire or liquefaction zone ranks as if it had 60% of its homes
  "no_pencil_factor": 0.7,         # ASSUMPTION: a site that does not pencil even at 0% ranks as if it had 70% of its homes
  "min_open_m2": 400,
  "conversion_units_per_acre": 43, # ASSUMPTION: 425 E. Wellington Ave, Santa Ana = 9 units on 0.21 acres (SCAG ACRES)              # ASSUMPTION: under ~400 m² of open land (about 4,300 sq ft) fits no new home
}
def lot_m2(c):
    if c["apn"] in COV: return COV[c["apn"]]["lot_m2"]
    return (c.get("acres") or 0) * 4046.86
for c in C:
    cov = COV.get(c["apn"]); src = set(c["sources"]); why = []
    if src == {"conversion"}:
        open_m2 = None; roof = None; basis = "existing apartment building (SCAG land use 2024)"
    elif "vacant" in src and not (src & {"religious_use", "housing_element_site"}):
        if cov: open_m2 = cov["open_m2"]; roof = cov["roof_m2"]; basis = "empty lot (SCAG land use); " + (f"county footprints show {cov['n_buildings']} building{'s' if cov['n_buildings']!=1 else ''} on it" if cov["n_buildings"] else "no buildings in county footprints")
        else: open_m2 = lot_m2(c); roof = 0; basis = "empty lot (SCAG land use); not checked for buildings"
    elif cov:
        open_m2 = cov["open_m2"]; roof = cov["roof_m2"]; basis = f"{cov['n_buildings']} building{'s' if cov['n_buildings']!=1 else ''} on the lot (county footprints)"
    else:
        open_m2 = None; roof = None; basis = "not measured"
    c["n_buildings"] = cov["n_buildings"] if cov else None
    c["roof_check"] = ("thin" if (cov and lot_m2(c) > 8000 and cov["n_buildings"] <= 2 and src & {"religious_use","surplus_land_notice"} and "housing_element_site" not in src) else None)
    c["open_acres"] = round(open_m2/4046.86, 2) if open_m2 is not None else None
    c["roof_share"] = round(roof/lot_m2(c), 2) if (roof is not None and lot_m2(c)) else None
    c["open_basis"] = basis
    # lead-quality checks first: a failed check means no homes, with the reason
    zs = c.get("zoning_scag") or ""; slope = float(c.get("slope") or 0); fail = None
    if zs == "1800": fail = "zoned open space, recreation or conservation (SCAG 2024)"
    elif zs == "9999": fail = "zoned for transportation or right-of-way (SCAG 2024)"
    elif slope > 15: fail = f"steep: {slope:.0f}% average slope (SCAG)"
    elif "vacant" in src and cov and lot_m2(c) and cov["roof_m2"]/lot_m2(c) > 0.3 and not (src & {"religious_use","housing_element_site"}): fail = f"tagged empty but {round(100*cov['roof_m2']/lot_m2(c))}% of it is under a roof now (county footprints)"
    c["fail"] = fail
    if fail:
        homes = 0; how = fail
    elif src == {"conversion"}:
        homes = max(1, round((c.get("acres") or 0) * A["conversion_units_per_acre"])); how = f"lot size × {A['conversion_units_per_acre']} units/acre, the density of 425 E. Wellington Ave (9 units on 0.21 acres) — ASSUMPTION; confirm the real unit count"
    elif "housing_element_site" in src and c.get("he_capacity") and open_m2 is None:
        homes = c["he_capacity"]; how = "the city's Housing Element capacity (open land not measured)"
    elif "housing_element_site" in src and c.get("he_capacity") and open_m2 >= A["min_open_m2"]:
        fit = math.floor(open_m2/4046.86 * A["density_per_acre"])
        homes = min(fit, c["he_capacity"]); how = f"open land × {A['density_per_acre']}/acre (ASSUMPTION), up to the city's planned {c['he_capacity']}"
    elif open_m2 is None:
        homes = None; how = "unknown: lot not measured"
    elif open_m2 < A["min_open_m2"]:
        homes = 0; how = "too little open land"
    else:
        ac = open_m2/4046.86
        if "religious_use" in src:
            homes = math.floor(ac * A["church_share_of_open"] * A["density_per_acre"]); how = f"half the open land × {A['density_per_acre']}/acre (ASSUMPTION)"
        elif "vacant" in src:
            raw = math.floor(ac * A["density_per_acre"])
            cap = A["sb9_cap"] if (c.get("zoning_scag") or "") in SFR else A["sb684_cap"]
            homes = min(raw, cap); how = f"open land × {A['density_per_acre']}/acre, capped at {cap} ({'SB 9' if cap==4 else 'SB 684'})"
        else:
            homes = math.floor(ac * A["density_per_acre"]); how = f"open land × {A['density_per_acre']}/acre (ASSUMPTION)"
    c["homes"] = homes; c["homes_how"] = how
    haz = sum(1 for v in c["hazards"].values() if v != "none found")
    f = c["fund"]; pencils = f.get("gap_condo_at_0pct") is not None and f["gap_condo_at_0pct"] <= 0
    k = (A["hazard_factor"] if haz else 1) * (1 if pencils or f.get("gap_condo_at_0pct") is None else A["no_pencil_factor"])
    c["rank_value"] = round((homes or 0) * k, 2)
    c["rank_reason"] = {"homes": homes, "homes_how": how, "hazard_zones": haz, "pencils_at_0pct": pencils,
                        "factor": round(k, 2), "rank_value": c["rank_value"]}
for c in C:
    if c.get("fail") or c.get("homes") == 0: c["geometry"] = None
C.sort(key=lambda c: (c["rank_value"], c.get("open_acres") or 0, c["score"]), reverse=True)
for i, c in enumerate(C): c["rank"] = i + 1
D["meta"]["ranking"] = "v2: homes that fit × hazard factor × pencil factor (see assumptions)"
D["meta"]["assumptions"]["homes"] = ("Homes that fit = the city's Housing Element capacity where listed; otherwise open (unroofed) land from the county building-footprint layer × 20 homes/acre (ASSUMPTION), "
    "church land using half its open land (ASSUMPTION), empty single-family lots capped at 4 (SB 9), other empty lots at 10 (SB 684). Under 400 m² open = 0.")
D["meta"]["assumptions"]["rank"] = "Rank = homes × 0.6 if in a flood/fire/liquefaction zone × 0.7 if it does not pencil even at 0% (ASSUMPTIONS)."
D["meta"]["assumption_values"] = A
D["meta"]["total_homes"] = sum(c["homes"] or 0 for c in C)
D["meta"]["sites_with_homes"] = sum(1 for c in C if (c["homes"] or 0) > 0)
import collections as _c
D["meta"]["dropped"] = dict(_c.Counter((c["fail"] or ("too little open land" if c["homes"]==0 else None)) for c in C if (c["homes"] or 0)==0 and c["homes"] is not None).most_common(12))
json.dump(D, open(S/"candidates.json", "w"), separators=(",", ":"))
print("sites", len(C), "with ≥1 home", D["meta"]["sites_with_homes"], "total homes", D["meta"]["total_homes"])
for c in C[:12]:
    print(c["rank"], c["city"], (c.get("worship") or {}).get("name") or c["sources"], "homes", c["homes"], "open ac", c["open_acres"], "roof", c["roof_share"], "k", c["rank_reason"]["factor"])
import collections
print("conversions in top 200/1000", sum(1 for c in C[:200] if c["sources"]==["conversion"]), sum(1 for c in C[:1000] if c["sources"]==["conversion"]))
print("top200 kinds", collections.Counter(c["sources"][0] for c in C[:200]))
print("top200 cities", collections.Counter(c["city"] for c in C[:200]).most_common(6))
