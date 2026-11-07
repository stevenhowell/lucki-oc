"""Show city council / community development records: on matching sites, and per city above the list."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ("const C=D.candidates; const byApn=new Map(C.map(c=>[c.apn,c]));",
  "const C=D.candidates; const byApn=new Map(C.map(c=>[c.apn,c]));\nlet COUNCIL={byCity:{},byApn:{}}; fetch('council.json').then(r=>r.ok?r.json():null).then(j=>{if(j){COUNCIL=j; if(tab==='explore'&&!open) renderExplore(); if(open) renderDrawer(open);}}).catch(()=>{});\nconst recHtml=r=>`<div style=\"border-top:1px solid var(--line);padding-top:6px\"><div><b>${esc(r.project||r.address||'Council item')}</b>${r.units?` · ${r.units} homes`:''}${r.tenure?` · ${esc(r.tenure)}`:''}</div><div class=\"src\">${esc(r.date||'date unknown')} · ${esc(r.body||'')}${r.decision?' · '+esc(r.decision):''}${r.money?' · '+esc(r.money):''}</div>${r.summary?`<div>${esc(r.summary)}</div>`:''}${r.issues&&r.issues.length?`<div class=\"src\">Issues raised: ${esc(r.issues.join(', '))}</div>`:''}${r.url?`<div class=\"src\"><a href=\"${esc(r.url)}\" target=\"_blank\" rel=\"noopener\">Read the record</a></div>`:''}</div>`;"),
 # per-city panel above the cards
 ("  more();\n}", "  const cr=(COUNCIL.byCity[$('#city').value]||[]); if($('#city').value&&cr.length){const d=document.createElement('details'); d.className='council'; d.style.gridColumn='1/-1'; d.innerHTML=`<summary><b>City council &amp; community development record</b> · ${cr.length} item${cr.length===1?'':'s'}</summary><div style=\"display:grid;gap:8px;margin-top:8px\">${cr.map(recHtml).join('')}</div>`; box.prepend(d);}\n  more();\n}"),
 (".howto{", ".council{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:10px 12px;font-size:13px}\n.council summary{cursor:pointer;min-height:32px}\n.howto{"),
 # on the site page
 ("    ${REAL[c.apn]?`<div class=\"track\" style=\"background:#e8f3ea;", "    ${(COUNCIL.byApn[c.apn]||[]).length?`<div class=\"track\"><div style=\"font-weight:700\">City council record</div>${COUNCIL.byApn[c.apn].map(recHtml).join('')}</div>`:''}\n    ${REAL[c.apn]?`<div class=\"track\" style=\"background:#e8f3ea;"),
 # card tag
 ("${REAL[c.apn]?`<div class=\"tag stage\" style=\"justify-self:start\">${REAL[c.apn].tag}</div>`:''}",
  "${REAL[c.apn]?`<div class=\"tag stage\" style=\"justify-self:start\">${REAL[c.apn].tag}</div>`:''}${(COUNCIL.byApn[c.apn]||[]).length?'<div class=\"tag\" style=\"justify-self:start;background:#e6eefc;color:#1f4e9c\">Council record</div>':''}"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
