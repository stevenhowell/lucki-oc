"""Draft the first call: keep drafts across redraws, stream readable text, faster model; shared-list updates
no longer redraw the open site (which wiped drafts and reset notes while typing)."""
from pathlib import Path
S = Path(__file__).parent/"site"
OLD_SNAP = "db.collection('pipeline').onSnapshot(snap=>{PIPE={};snap.docs.forEach(d=>{PIPE[d.id]=d.data()});refreshCounts();if(tab==='list')renderList();drawMarkers();if(open)renderDrawer(open)},err=>{store='local';});"
NEW_SNAP = "db.collection('pipeline').onSnapshot(snap=>{PIPE={};snap.docs.forEach(d=>{PIPE[d.id]=d.data()});refreshCounts();if(tab==='list'&&!open)renderList();drawMarkers();if(open)refreshDrawerState(open)},err=>{store='local';});"
start = "async function wireDraft(c){"
NEW_WIRE = r"""const DRAFTS={};
function refreshDrawerState(c){ const p=PIPE[c.apn]||{};
  $$('[data-stage]').forEach(b=>b.setAttribute('aria-pressed',p.stage===b.dataset.stage));
  const h=$('#dheart'); if(h){h.setAttribute('aria-pressed',!!p.stage); h.textContent=p.stage?'♥':'♡'; h.style.color=p.stage?'var(--heart)':'var(--ink)';}
  const n=$('#note'); if(n&&document.activeElement!==n&&(p.note||'')!==n.value) n.value=p.note||'';
  const m=$('#savedmsg'); if(m&&p.updated) m.textContent='Last change '+new Date(p.updated).toLocaleString()+(store==='shared'?' · shared list':' · this browser only');
}
function parseDraft(t){const sec=(k,next)=>{const re=new RegExp('^\\s*'+k+'\\s*:?\\s*$([\\s\\S]*?)(?=^\\s*(?:'+next+')\\s*:?\\s*$|$(?![\\s\\S]))','mi'); const m=t.match(re); return m?m[1].trim():''};
  return {call:sec('CALL SCRIPT','TEXT MESSAGE|EMAIL'),text:sec('TEXT MESSAGE','EMAIL|CALL SCRIPT'),email:sec('EMAIL','CALL SCRIPT|TEXT MESSAGE')};}
function showDrafts(out,r){
  out.innerHTML='<div class="badge">Drafts · not sent</div>'+['call','text','email'].map(k=>`<div><div class="src" style="display:flex;justify-content:space-between;align-items:center">${{call:'Call script',text:'Text message',email:'Email'}[k]} <button data-copy="${k}" style="min-height:36px">Copy</button></div><div class="draft" id="d-${k}">${esc(String(r[k]||'(none)'))}</div></div>`).join('');
  out.querySelectorAll('[data-copy]').forEach(b=>b.onclick=async()=>{const el=$('#d-'+b.dataset.copy);try{await navigator.clipboard.writeText(el.textContent);b.textContent='Copied'}catch(e){const s=getSelection(),rg=document.createRange();rg.selectNodeContents(el);s.removeAllRanges();s.addRange(rg);b.textContent='Selected'}});
}
async function wireDraft(c){
  const btn=$('#draft'), stop=$('#stop'), out=$('#drafts');
  if(DRAFTS[c.apn]){ showDrafts(out,DRAFTS[c.apn]); btn.textContent='Draft again'; }
  const sample=(window.claude&&window.claude.use)?await window.claude.use('sample').catch(()=>null):null;
  if(!sample){btn.disabled=true;btn.textContent='Open in Claude to draft';return}
  let ctl; stop.onclick=()=>ctl&&ctl.abort();
  btn.onclick=async()=>{ctl=new AbortController();btn.disabled=true;stop.hidden=false;out.innerHTML='<div class="fine">Writing… (first time, Claude asks you to allow it)</div>';
    const facts={site:name(c),city:c.city,parcel:c.apn,acres:c.acres,open_acres:c.open_acres,homes_estimate:c.homes,kind:KIND[kindKey(c)],laws:laws(c).map(l=>l.name),zoning:c.zoning_city_code,hazards:c.hazards,near_frequent_transit:c.hqta!=='no',real_deal:REAL[c.apn]?REAL[c.apn].t:null,institution:c.worship?{name:c.worship.name,denomination:c.worship.denomination}:null,agency:c.noa_agency||null,city_help_per_home:c.fund.city_program==='unknown'?null:c.fund.city_program.per_unit,my_notes:(PIPE[c.apn]||{}).note||null};
    const prompt=`You write first-contact outreach for a one-person acquisitions lead at Habitat for Humanity of Orange County, a nonprofit that builds affordable homes families buy. Write to the ORGANIZATION'S OFFICE (a congregation's office, a public agency, or "the owner of record"), never to a named person. Use only these facts; if something is missing, leave it out or say it is unknown. Do not invent numbers, people, dates or promises. Mention the law that may apply in one plain sentence and say it still needs to be confirmed. Warm, short, plain words; the goal is a 20-minute conversation, not a deal.
Facts: ${JSON.stringify(facts)}
Write exactly three sections with these headings on their own lines and nothing before the first heading:
CALL SCRIPT
(5 to 7 short lines: who you are, why you're calling about this property, one sentence on the law, the ask for a short meeting, and what to say if they're not interested)
TEXT MESSAGE
(one message under 300 characters)
EMAIL
(Subject: line first, then under 150 words, signed "[Your name], Habitat for Humanity of Orange County")`;
    try{const {text}=await sample(prompt,{signal:ctl.signal,modelTier:'quick',onText:({text})=>{out.innerHTML='<div class="fine">Writing…</div><div class="draft">'+esc(text)+'</div>'}});
      const r=parseDraft(text); if(!r.call&&!r.text&&!r.email){r.call=text;}
      DRAFTS[c.apn]=r; showDrafts(out,r); btn.textContent='Draft again';
      if(!(PIPE[c.apn]||{}).stage) setPipe(c.apn,{stage:'research'}).then(()=>refreshDrawerState(c));
    }catch(e){out.innerHTML=`<div class="fine">${e.code==='cancelled'?'Stopped.':e.code==='not_granted'?'Claude isn’t allowed for this page. Allow it from the page’s permissions and try again.':e.code==='rate_limited'?'Too many requests right now. Try again in a minute.':'Could not draft ('+esc(e.code||'error')+'). Try again.'}</div>`; if(e.text) out.innerHTML+='<div class="draft">'+esc(e.text)+'</div>';}
    finally{btn.disabled=false;stop.hidden=true}};
}
"""
for f in ("app.src.html", "index.html"):
    p = S/f; s = p.read_text()
    assert OLD_SNAP in s, f + " snap"
    s = s.replace(OLD_SNAP, NEW_SNAP)
    a = s.index(start); b = s.index("\n}\n", a) + 3
    s = s[:a] + NEW_WIRE + s[b:]
    # stage clicks: update in place instead of a full redraw (keeps drafts and the note box)
    s = s.replace("$$('[data-stage]').forEach(b=>b.onclick=()=>{setPipe(c.apn,{stage:p.stage===b.dataset.stage?'none':b.dataset.stage,note:$('#note').value}).then(()=>{renderDrawer(c); tab==='list'?renderList():null});});",
                  "$$('[data-stage]').forEach(b=>b.onclick=()=>{const cur=(PIPE[c.apn]||{}).stage; setPipe(c.apn,{stage:cur===b.dataset.stage?'none':b.dataset.stage,note:$('#note').value}).then(()=>refreshDrawerState(c));});")
    p.write_text(s); print(f, "ok")
