"""A three-step 'how to use' line above the list, and a review flag for very large parcels."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ("    <div class=\"cards\" id=\"cards\"></div>",
  "    <div class=\"howto\" id=\"howto\"><b>How Lucki works</b><ol><li>Pick a city at the top.</li><li>Tap a site: read the summary, look at the photo, open “Does it pencil?”.</li><li>Tap ♡ to save it, then move it from Saved to Contacted on the site page.</li></ol><button id=\"howto-x\" aria-label=\"Hide these tips\">Got it</button></div>\n    <div class=\"cards\" id=\"cards\"></div>"),
 (".more{grid-column:1/-1;", ".howto{margin:0 16px 8px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel);display:grid;grid-template-columns:1fr auto;gap:4px 12px;align-items:start;font-size:13px}\n.howto ol{margin:4px 0 0;padding-left:18px;grid-column:1}\n.howto button{grid-column:2;grid-row:1/3;min-height:36px}\n.more{grid-column:1/-1;"),
 ("  if(c.homes==null) r.push({who:'lucki',t:'Open land not measured, so homes are unknown'});",
  "  if(c.homes==null) r.push({who:'lucki',t:'Open land not measured, so homes are unknown'});\n  if(c.very_large) r.push({who:'lucki',t:'Very large parcel: it may be a campus, a park or a parcel that crosses a road; check the photo'});"),
 ("try{const s=localStorage.getItem('lucki.city'); if(s&&cities.includes(s)) $('#city').value=s;}catch(e){}",
  "try{const s=localStorage.getItem('lucki.city'); if(s&&cities.includes(s)) $('#city').value=s; if(localStorage.getItem('lucki.howto')==='hide') $('#howto').hidden=true;}catch(e){}\n$('#howto-x').onclick=()=>{$('#howto').hidden=true; try{localStorage.setItem('lucki.howto','hide')}catch(e){}};"),
 ("<option value=\"best\">Most homes</option>", "<option value=\"best\">Best fit for a small nonprofit</option><option value=\"homes\">Most homes</option>"),
 ("if(s==='size') r=", "if(s==='homes') r=[...r].sort((a,b)=>(b.homes||0)-(a.homes||0));\n  if(s==='size') r="),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
