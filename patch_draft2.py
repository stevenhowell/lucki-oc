"""Drafts never disappear: always write into the panel on screen, keep them in the shared list, show what they were personalized with.
Also: a contact block (office phone / email / website) for sites in data contacts."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 # always resolve the live element
 ("function showDrafts(out,r){\n  out.innerHTML=", "function showDrafts(_out,r){\n  const out=$('#drafts'); if(!out) return;\n  out.innerHTML=(r.why?`<div class=\"src\" style=\"background:var(--soft);border-radius:8px;padding:8px\"><b>Personalized for this site:</b> ${esc(r.why)}</div>`:'')+"),
 ("  if(DRAFTS[c.apn]){ showDrafts(out,DRAFTS[c.apn]); btn.textContent='Draft again'; }",
  "  const saved=(PIPE[c.apn]||{}).drafts; if(!DRAFTS[c.apn]&&saved) DRAFTS[c.apn]=saved;\n  if(DRAFTS[c.apn]){ showDrafts(out,DRAFTS[c.apn]); btn.textContent='Draft again'; }"),
 ("onText:({text})=>{out.innerHTML='<div class=\"fine\">Writing…</div><div class=\"draft\">'+esc(text)+'</div>'}});",
  "onText:({text})=>{const o=$('#drafts'); if(o) o.innerHTML='<div class=\"fine\">Writing…</div><div class=\"draft\">'+esc(text)+'</div>'}});"),
 ("      DRAFTS[c.apn]=r; showDrafts(out,r); btn.textContent='Draft again';\n      if(!(PIPE[c.apn]||{}).stage) setPipe(c.apn,{stage:'research'}).then(()=>refreshDrawerState(c));",
  "      r.why=[name(c), c.homes?('about '+c.homes+(c.sources.includes('conversion')?' apartments':' homes')):null, laws(c)[0]?laws(c)[0].name.split(':')[0]:null, c.hqta!=='no'?'near frequent transit':null, Object.values(c.hazards).every(v=>v==='none found')?'no hazard zones':null, c.fund.city_program!=='unknown'?('city help '+fmt(c.fund.city_program.per_unit)+'/home'):null, REAL[c.apn]?'what happened at this real project':null, (PIPE[c.apn]||{}).note?'your notes':null].filter(Boolean).join(' · ');\n      DRAFTS[c.apn]=r; showDrafts(null,r); const b2=$('#draft'); if(b2) b2.textContent='Draft again';\n      setPipe(c.apn,{stage:(PIPE[c.apn]||{}).stage||'research',drafts:r}).then(()=>refreshDrawerState(c));"),
 ("    }catch(e){out.innerHTML=`<div class=\"fine\">", "    }catch(e){const out=$('#drafts')||document.createElement('div'); out.innerHTML=`<div class=\"fine\">"),
 ("    finally{btn.disabled=false;stop.hidden=true}};", "    finally{const b=$('#draft'), s2=$('#stop'); if(b) b.disabled=false; if(s2) s2.hidden=true}};"),
 ("btn.onclick=async()=>{ctl=new AbortController();btn.disabled=true;stop.hidden=false;out.innerHTML=", "btn.onclick=async()=>{ctl=new AbortController();btn.disabled=true;stop.hidden=false;const out=$('#drafts');out.innerHTML="),
 # contacts
 ("const C=D.candidates; const byApn=new Map(C.map(c=>[c.apn,c]));",
  "const C=D.candidates; const byApn=new Map(C.map(c=>[c.apn,c]));\nlet CONTACTS={}; fetch('contacts.json').then(r=>r.ok?r.json():{}).then(j=>{CONTACTS=j||{}; if(tab==='explore'&&!open) renderExplore(); if(open) renderDrawer(open);}).catch(()=>{});"),
 ("  const whoBody=c.worship?", "  const ct=CONTACTS[c.apn]; const ctHtml=ct?`<div><b>${esc(ct.organization||'')}</b></div>${ct.address?`<div>${esc(ct.address)}</div>`:''}${ct.phone?`<div>Office: <span style=\"user-select:all\">${esc(ct.phone)}</span></div>`:''}${ct.email?`<div>Email: <span style=\"user-select:all\">${esc(ct.email)}</span></div>`:''}${ct.contact_form?`<div><a href=\"${esc(ct.contact_form)}\" target=\"_blank\" rel=\"noopener\">Contact form</a></div>`:''}${ct.website?`<div><a href=\"${esc(ct.website)}\" target=\"_blank\" rel=\"noopener\">Website</a></div>`:''}<div class=\"src\">Public office contact from ${ct.source_url?`<a href=\"${esc(ct.source_url)}\" target=\"_blank\" rel=\"noopener\">the organization’s page</a>`:'a public listing'} (${esc(ct.confidence||'')} confidence). No individuals’ details.</div>`:'';\n  const whoBody=ct?ctHtml:c.worship?"),
 ("  const who=c.worship?{a:esc(c.worship.name||'Known'),k:'pass'}", "  const who=CONTACTS[c.apn]?{a:esc(CONTACTS[c.apn].organization||'Contact found'),k:'pass'}:c.worship?{a:esc(c.worship.name||'Known'),k:'pass'}"),
 ("function name(c){return REAL[c.apn]?REAL[c.apn].name:", "function name(c){return REAL[c.apn]?REAL[c.apn].name:(typeof CONTACTS!=='undefined'&&CONTACTS[c.apn]&&CONTACTS[c.apn].organization)?CONTACTS[c.apn].organization:"),
 ("${(COUNCIL.byApn[c.apn]||[]).length?'<div class=\"tag\" style=\"justify-self:start;background:#e6eefc;color:#1f4e9c\">Council record</div>':''}",
  "${(COUNCIL.byApn[c.apn]||[]).length?'<div class=\"tag\" style=\"justify-self:start;background:#e6eefc;color:#1f4e9c\">Council record</div>':''}${CONTACTS[c.apn]&&(CONTACTS[c.apn].phone||CONTACTS[c.apn].email)?'<div class=\"tag pass\" style=\"justify-self:start\">Office contact</div>':''}"),
 # drafts can use the contact
 ("agency:c.noa_agency||null,city_help_per_home:", "agency:c.noa_agency||null,office_contact:CONTACTS[c.apn]?{organization:CONTACTS[c.apn].organization}:null,city_help_per_home:"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
