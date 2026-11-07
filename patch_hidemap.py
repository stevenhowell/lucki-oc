"""A button on the divider hides the map so the list fills the window; the same button brings it back."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ('  <section class="side">', '  <section class="side"><button id="map-hide" class="maphide" aria-pressed="false" aria-label="Hide map" title="Hide map">‹</button>'),
 (".maptoggle{", ".maphide{position:absolute;left:-22px;top:50%;transform:translateY(-50%);z-index:1002;width:44px;height:44px;min-height:44px;border-radius:50%;padding:0;font-size:24px;line-height:1;display:grid;place-items:center;background:var(--panel,#fff);border:1px solid var(--line);box-shadow:0 2px 8px rgba(0,0,0,.25);cursor:pointer}\n.maphide:active{transform:translateY(-50%) scale(.94)}\nbody.nomap .main{grid-template-columns:minmax(0,1fr)}\nbody.nomap .mapwrap{display:none}\nbody.nomap .maphide{left:8px}\n.maptoggle{"),
 ("$('#z-in').onclick=()=>zoomBy(2);", "$('#map-hide').onclick=()=>{const off=document.body.classList.toggle('nomap'); const b=$('#map-hide'); b.textContent=off?'›':'‹'; b.setAttribute('aria-pressed',off); b.setAttribute('aria-label',off?'Show map':'Hide map'); b.title=off?'Show map':'Hide map'; if(!off) drawStatic();};\n$('#z-in').onclick=()=>zoomBy(2);"),
 ("@media (max-width:900px){", "@media (max-width:900px){.maphide{display:none}"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
