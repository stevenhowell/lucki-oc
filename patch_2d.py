"""One button top right: Satellite <-> 2D map (county grey street basemap). Search box. Page scrolls on narrow windows."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 # one button, top right of the photo
 ('<div class="slegend" id="slegend"></div>', '<div class="slegend" id="slegend"></div><button id="view-btn" class="maptoggle" aria-pressed="false">2D map</button>'),
 # pick image by mode
 ("  const city=$('#city').value; const V=(city&&CITYV[city])?{...CITYV[city],img:CITYV[city].file,label:city+', 2025 aerial'}:OV?{...OV,img:'overview.jpg',label:'Orange County, 2025 aerial'}:null;",
  "  const city=$('#city').value; const slug=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); const two=VIEW==='2d';\n  const V=(city&&CITYV[city])?{...CITYV[city],img:two?'map2d/'+slug(city)+'.png':CITYV[city].file,label:city+(two?', street map':', 2025 aerial')}:OV?{...OV,img:two?'map2d/overview.png':'overview.jpg',label:'Orange County'+(two?', street map':', 2025 aerial')}:null;"),
 ("let ZS=1, TX=0, TY=0;", "let VIEW='sat'; let ZS=1, TX=0, TY=0;"),
 # search box in the bar
 ('<select id="city" class="search" aria-label="City">', '<input id="q" class="search" type="search" placeholder="Search a name, street or parcel" aria-label="Search sites" style="min-width:220px">\n  <select id="city" class="search" aria-label="City">'),
 ("&&(!$('#f-review').checked||!reviews(c).length));", "&&(!$('#f-review').checked||!reviews(c).length)&&(!QS||((name(c)+' '+(c.noa_address||'')+' '+c.apn+' '+c.city+' '+((c.worship||{}).name||'')).toLowerCase().includes(QS))));"),
 ("let tab='explore', open=null, shown=0, rows=[];", "let tab='explore', open=null, shown=0, rows=[]; let QS='';"),
 ("$('#z-in').onclick=()=>zoomBy(2);", "let qt; $('#q').oninput=e=>{clearTimeout(qt); qt=setTimeout(()=>{QS=e.target.value.trim().toLowerCase(); closeSite(); update();},250)};\n$('#view-btn').onclick=()=>{VIEW=VIEW==='sat'?'2d':'sat'; $('#view-btn').textContent=VIEW==='sat'?'2D map':'Satellite'; $('#view-btn').setAttribute('aria-pressed',VIEW==='2d'); drawStatic();};\n$('#z-in').onclick=()=>zoomBy(2);"),
 # scrolling on narrow windows: let the page grow and scroll
 ("@media (max-width:900px){body{overflow:auto}", "@media (max-width:900px){html,body{height:auto}body{overflow:auto}.main{flex:none}.cards{overflow:visible}.drawer{position:static}"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
