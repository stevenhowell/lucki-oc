"""Make first paint independent of the big data: a visible loading state, a clear error if data fails,
and lot outlines loaded after the list appears."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ("const [D,AER,BASE]=await Promise.all([fetch('candidates.json').then(r=>r.json()),fetch('aerials.json').then(r=>r.json()).catch(()=>({})),fetch('base.json').then(r=>r.json()).catch(()=>[])]);",
  """$('#cards').innerHTML='<div class="empty"><b>Loading sites…</b><span>About 11,000 sites across Orange County.</span></div>';
let D,AER,BASE;
try{ [D,AER,BASE]=await Promise.all([fetch('candidates.json').then(r=>{if(!r.ok) throw new Error('candidates.json '+r.status); return r.json()}),fetch('aerials.json').then(r=>r.json()).catch(()=>({})),fetch('base.json').then(r=>r.json()).catch(()=>[])]); }
catch(e){ $('#cards').innerHTML=`<div class="empty"><b>Sites didn’t load.</b><span>${String(e&&e.message||e)}. Reload the page; if it keeps happening, the data file may still be publishing.</span><button onclick="location.reload()">Reload</button></div>`; return; }"""),
 ("const C=D.candidates; const byApn=new Map(C.map(c=>[c.apn,c]));",
  "const C=D.candidates; const byApn=new Map(C.map(c=>[c.apn,c]));\nfetch('outlines.json').then(r=>r.ok?r.json():{}).then(o=>{for(const [a,g] of Object.entries(o)){const c=byApn.get(a); if(c) c.geometry=g;} if(typeof drawMarkers==='function') drawMarkers(); if(open) renderDrawer(open);}).catch(()=>{});"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
