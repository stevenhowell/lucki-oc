"""County base: 4x4 grid of 2025 1-ft aerials, each 3600x3600 px (~5 m/px). Writes site/base/r{r}c{c}.jpg + site/base.json."""
import math, json, urllib.request, urllib.parse, time
from pathlib import Path
S=Path(__file__).parent/"site"; B=S/"base"; B.mkdir(exist_ok=True)
R=20037508.34
def merc(lon,lat): return lon*R/180, math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)*R/180
x0,y0=merc(-118.13,33.38); x1,y1=merc(-117.41,33.95)
N=4; dx=(x1-x0)/N; dy=(y1-y0)/N
URL="https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage"
meta=[]
for r in range(N):
    for c in range(N):
        bb=[x0+c*dx, y1-(r+1)*dy, x0+(c+1)*dx, y1-r*dy]
        q=urllib.parse.urlencode({"bbox":",".join(f"{v:.1f}" for v in bb),"bboxSR":3857,"imageSR":3857,"size":"3600,3600","format":"jpg","compressionQuality":70,"f":"image"})
        for t in range(4):
            try:
                d=urllib.request.urlopen(URL+"?"+q,timeout=300).read()
                if d[:2]==b"\xff\xd8": (B/f"r{r}c{c}.jpg").write_bytes(d); meta.append({"file":f"base/r{r}c{c}.jpg","bbox3857":bb}); print(r,c,len(d)//1024,"KB",flush=True); break
            except Exception as e: print("retry",r,c,str(e)[:60],flush=True); time.sleep(4)
json.dump(meta,open(S/"base.json","w")); print("done",len(meta))
