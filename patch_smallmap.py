"""Small map: a quarter-size panel at the top left, legend under it, no viewer zoom (picking a city still swaps to that city's aerial)."""
from pathlib import Path
S = Path(__file__).parent/"site"
CSS = """
@media (min-width:901px){
.main{grid-template-columns:minmax(300px,34vw) minmax(0,1fr)}
.mapwrap{align-self:start;min-height:0;aspect-ratio:1.45;margin:12px 0 0 12px;border-radius:12px;overflow:visible;background:transparent}
.mapwrap .static{border-radius:12px;overflow:hidden;background:#2a2d29}
.slegend{top:calc(100% + 10px);bottom:auto;left:0;font-size:12px}
.maptoggle{top:8px;right:8px;min-height:36px;padding:6px 12px;font-size:14px}
}
.zoomctl{display:none!important}
.static,.static.dragging{cursor:default}
"""
reps = [
 ("function zoomBy(k,cx,cy){", "function zoomBy(k,cx,cy){return;"),
 (".maphide{position:absolute;", CSS + ".maphide{position:absolute;"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
