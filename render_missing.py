"""Render close-up aerials for every site in the given cities that has none (same method as render_aerials.py)."""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path
import importlib.util
S = Path(__file__).parent/"site"; A = S/"aerials"
src = open(Path(__file__).parent/"render_aerials.py").read().split("# pick sites")[0]
src = src.replace('D = json.load(open(S / "candidates.json")); C = D["candidates"]', '')
ns = {"__file__": str(Path(__file__).parent/"render_aerials.py")}; exec(src, ns)
bbox_for = ns["bbox_for"]
C = json.load(open(S/"candidates.json"))["candidates"]; O = json.load(open(S/"outlines.json"))
meta = json.load(open(S/"aerials.json"))
cities = sys.argv[1:]
todo = [c for c in C if c["city"] in cities and c["apn"] not in meta]
print("todo", len(todo), flush=True)
URL = "https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/22_OC_3IN_SP6/ImageServer/exportImage"
fails = 0
for c in todo:
    c = dict(c, geometry=O.get(c["apn"]))
    bb = bbox_for(c)
    q = urllib.parse.urlencode({"bbox": ",".join(f"{v:.2f}" for v in bb), "bboxSR": 3857, "imageSR": 3857, "size": "800,560", "format": "jpg", "f": "image"})
    try:
        data = urllib.request.urlopen(URL+"?"+q, timeout=60).read()
        if data[:2] == b"\xff\xd8" and len(data) > 5000:
            (A/f"{c['apn']}.jpg").write_bytes(data); meta[c["apn"]] = {"bbox3857": [round(v,2) for v in bb], "w": 800, "h": 560}; fails = 0
        else: print("bad", c["apn"], len(data)); fails += 1
    except Exception as e:
        print("fail", c["apn"], str(e)[:60], flush=True); fails += 1
    if fails >= 3: print("server failing, stopping"); break
    time.sleep(0.4)
json.dump(meta, open(S/"aerials.json","w"))
print("done; missing now", sum(1 for c in C if c["city"] in cities and c["apn"] not in meta))
