"""After a rerank: make sure the sites people will see first have a close-up photo.
Picks = top 40 county-wide + top 4 per city + 425 E. Wellington. Renders missing ones one at a time (gentle on the county server).
Old photos of sites ranked below 1500 and not picked are dropped from aerials.json and listed in cache/aerials_dropped.json
(so the publish can remove them). Total stays under MAX."""
import json, math, urllib.request, urllib.parse, time, collections
from pathlib import Path
B = Path(__file__).parent; S = B/"site"; A = S/"aerials"
MAX = 470
C = json.load(open(S/"candidates.json"))["candidates"]; byapn = {c["apn"]: c for c in C}
AER = json.load(open(S/"aerials.json"))
R = 20037508.34
def merc(lon, lat): return lon*R/180, math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)*R/180
def bbox_for(c):
    g = c.get("geometry"); P = []
    if g:
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        P = [merc(*p) for poly in polys for ring in poly for p in ring]
    if P:
        xs = [p[0] for p in P]; ys = [p[1] for p in P]; x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    else:
        x, y = merc(*c["centroid"]); pad = 35 if c["sources"] == ["conversion"] else 60; x0, x1, y0, y1 = x-pad, x+pad, y-pad, y+pad
    w = max(x1-x0, 60)*1.7; h = max(y1-y0, 40)*1.7
    if w/h < 800/560: w = h*800/560
    else: h = w*560/800
    cx, cy = (x0+x1)/2, (y0+y1)/2
    return [cx-w/2, cy-h/2, cx+w/2, cy+h/2]
live = [c for c in C if (c.get("homes") or 0) > 0]
picks = [c["apn"] for c in live[:40]]
by = collections.defaultdict(list)
for c in live: by[c["city"]].append(c["apn"])
for city, apns in by.items(): picks += apns[:4]
picks.append("39802812")
picks = list(dict.fromkeys(a for a in picks if a in byapn))
keep_old = [a for a in AER if a in byapn and (byapn[a]["rank"] <= 1500 or a in picks)]
dropped = [a for a in AER if a not in keep_old]
need = [a for a in picks if a not in AER]
room = MAX - len(keep_old)
if room < len(need):  # drop the lowest-ranked old photos that are not picks
    extra = sorted([a for a in keep_old if a not in picks], key=lambda a: -byapn[a]["rank"])[:len(need)-room]
    keep_old = [a for a in keep_old if a not in extra]; dropped += extra
print("picks", len(picks), "have", len(picks)-len(need), "to render", len(need), "dropping", len(dropped), flush=True)
NEW = {a: AER[a] for a in keep_old}
URL = "https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/22_OC_3IN_SP6/ImageServer/exportImage"
fails = 0
for i, a in enumerate(need):
    c = byapn[a]; bb = bbox_for(c)
    q = urllib.parse.urlencode({"bbox": ",".join(f"{v:.2f}" for v in bb), "bboxSR": 3857, "imageSR": 3857, "size": "800,560", "format": "jpg", "f": "image"})
    try:
        d = urllib.request.urlopen(URL+"?"+q, timeout=60).read()
        if d[:2] == b"\xff\xd8": (A/f"{a}.jpg").write_bytes(d); NEW[a] = {"bbox3857": [round(v, 2) for v in bb], "w": 800, "h": 560}
        else: fails += 1
    except Exception as e:
        fails += 1; print("fail", a, str(e)[:60], flush=True)
        if fails >= 5: print("county server failing; stopping", flush=True); break
    time.sleep(0.3)
    if i % 20 == 0: print(i, "rendered", flush=True)
json.dump(NEW, open(S/"aerials.json", "w")); json.dump(dropped, open(B/"cache"/"aerials_dropped.json", "w"))
print("aerials now", len(NEW), "dropped", len(dropped), "fails", fails, flush=True)
