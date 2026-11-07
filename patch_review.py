"""'Needs review': Lucki flags sites whose data is shaky, and the team can flag any site with a reason.
Auto reasons: county roof map looks incomplete; empty lot not checked for buildings; homes not measured;
surplus notice archived. Team flags live in the shared list (pipeline/<apn>: review, review_note)."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 # model
 ("function pencils(c){", r"""function reviews(c){const r=[]; const p=PIPE[c.apn]||{};
  if(p.review) r.push({who:'team',t:'Flagged by your team'+(p.review_note?': '+p.review_note:'')});
  if(c.roof_check==='thin') r.push({who:'lucki',t:`The county’s building map shows only ${c.n_buildings} building${c.n_buildings===1?'':'s'} on this lot; open land and homes may be too high`});
  if(c.sources.length===1&&c.sources[0]==='vacant'&&c.n_buildings==null) r.push({who:'lucki',t:'Tagged empty in land-use data but not checked for buildings (county server stopped answering)'});
  if(c.homes==null) r.push({who:'lucki',t:'Open land not measured, so homes are unknown'});
  if(c.sources.includes('surplus_land_notice')&&/archive/i.test(c.noa_status||'')) r.push({who:'lucki',t:'The surplus-land notice is archived; the agency may no longer offer it'});
  return r;}
function pencils(c){"""),
 # filter control
 ("<label><input type=\"checkbox\" id=\"f-room\" checked> Hide sites with no room for a home</label>",
  "<label><input type=\"checkbox\" id=\"f-room\" checked> Hide sites with no room for a home</label>\n      <label><input type=\"checkbox\" id=\"f-review\"> Hide sites that need review</label>"),
 ("&&(!$('#f-room').checked||c.homes==null||c.homes>0));", "&&(!$('#f-room').checked||c.homes==null||c.homes>0)&&(!$('#f-review').checked||!reviews(c).length));"),
 ("['#f-safe','#f-transit','#f-pencil','#f-size','#sort','#f-move','#f-room']", "['#f-safe','#f-transit','#f-pencil','#f-size','#sort','#f-move','#f-room','#f-review']"),
 # card tag
 ("${c.hqta!=='no'?'<span class=\"tag pass\">Transit</span>':''}", "${c.hqta!=='no'?'<span class=\"tag pass\">Transit</span>':''}${reviews(c).length?`<span class=\"tag review\" title=\"${esc(reviews(c).map(x=>x.t).join(' · '))}\">${reviews(c).some(x=>x.who==='team')?'Flagged':'Needs review'}</span>`:''}"),
 (".tag.pass{", ".tag.review{background:#fde8cf;color:#8a4b00}\n.tag.pass{"),
 # drawer: review box under the verdict
 ("    <div class=\"track\"><div style=\"font-weight:700\">My list</div>",
  "    ${(()=>{const rv=reviews(c);return `<div class=\"track\" style=\"background:${rv.length?'#fff4e5':'var(--soft)'};color:${rv.length?'#3d2a00':'inherit'}\"><div style=\"font-weight:700\">${rv.length?'Needs review':'Data checks look complete'}</div>${rv.map(x=>`<div>• ${esc(x.t)} <span class=\"src\" style=\"color:inherit;opacity:.7\">(${x.who==='team'?'team':'Lucki'})</span></div>`).join('')}<div class=\"stages\"><button id=\"rv-btn\" aria-pressed=\"${!!p.review}\">${p.review?'Clear my flag':'Flag for review'}</button></div><label for=\"rv-note\" class=\"src\" ${p.review?'':'hidden'} id=\"rv-l\">What looks wrong?</label><textarea id=\"rv-note\" ${p.review?'':'hidden'} placeholder=\"e.g. the photo shows a school building the map missed\">${esc(p.review_note||'')}</textarea></div>`})()}\n    <div class=\"track\"><div style=\"font-weight:700\">My list</div>"),
 ("  let t; $('#note').oninput=", "  $('#rv-btn').onclick=()=>{const on=!(PIPE[c.apn]||{}).review; setPipe(c.apn,{stage:(PIPE[c.apn]||{}).stage||'saved',review:on,review_note:on?((PIPE[c.apn]||{}).review_note||''):''}).then(()=>{renderDrawer(c); if(tab==='list')renderList(); if(on) setTimeout(()=>$('#rv-note')&&$('#rv-note').focus(),50)});};\n  let rt; $('#rv-note').oninput=()=>{clearTimeout(rt); rt=setTimeout(()=>setPipe(c.apn,{stage:(PIPE[c.apn]||{}).stage||'saved',review:true,review_note:$('#rv-note').value}),700)};\n  let t; $('#note').oninput="),
 # My list: a 'Flagged for review' group first
 ("  STAGES.forEach(([k,label])=>{const these=items.filter(p=>(p.stage||'saved')===k);",
  "  const fl=items.filter(p=>p.review); if(fl.length){const sec=document.createElement('section'); sec.innerHTML=`<h3>Flagged for review <span class=\"n\">${fl.length}</span></h3>`; const g=document.createElement('div'); g.className='grid'; fl.forEach(p=>g.append(card(byApn.get(p.apn)))); sec.append(g); b.append(sec);}\n  STAGES.forEach(([k,label])=>{const these=items.filter(p=>(p.stage||'saved')===k);"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
