"""One 1-ft (2025) aerial per city, framed on that city's top 40 sites. Writes site/cities/<slug>.jpg + site/cities.json."""
import json, math, urllib.request, urllib.parse, collections, re, time
from pathlib import Path
S=Path(__file__).parent/"site"; O=S/"cities"; O.mkdir(exist_ok=True)
C=json.load(open(S/"candidates.json"))["candidates"]
R=20037508.34
def merc(lon,lat): return lon*R/180, math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)*R/180
by=collections.defaultdict(list)
for c in C: by[c["city"]].append(c)
meta={}
URL="https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage"
for city,rows in by.items():
    if not city: continue
    pts=[merc(*c["centroid"]) for c in rows[:40]]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    w=max(max(xs)-min(xs),1500)*1.25; h=max(max(ys)-min(ys),1000)*1.25
    if w/h<1.6: w=h*1.6
    else: h=w/1.6
    cx,cy=(max(xs)+min(xs))/2,(max(ys)+min(ys))/2; bb=[cx-w/2,cy-h/2,cx+w/2,cy+h/2]
    slug=re.sub(r'[^a-z0-9]+','-',city.lower()).strip('-')
    q=urllib.parse.urlencode({"bbox":",".join(f"{v:.1f}" for v in bb),"bboxSR":3857,"imageSR":3857,"size":"1600,1000","format":"jpg","f":"image"})
    for t in range(3):
        try:
            d=urllib.request.urlopen(URL+"?"+q,timeout=120).read()
            if d[:2]==b"\xff\xd8": (O/f"{slug}.jpg").write_bytes(d); meta[city]={"file":f"cities/{slug}.jpg","bbox3857":bb,"w":1600,"h":1000}; break
        except Exception as e: time.sleep(3)
    print(city, "ok" if city in meta else "FAIL", flush=True)
json.dump(meta,open(S/"cities.json","w")); print("cities",len(meta))
