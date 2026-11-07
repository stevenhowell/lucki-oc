"""Phone and email at the top: on every card that has an office contact, and first thing on the site page.
City-office contacts no longer rename the site."""
from pathlib import Path
S = Path(__file__).parent/"site"
HELP = r"""function ctBits(c){const ct=CONTACTS[c.apn]; if(!ct||!(ct.phone||ct.email)) return null; const tel=(ct.phone||'').replace(/[^0-9+]/g,'');
  return {ct, phone:ct.phone?`<a href="tel:${tel}" onclick="event.stopPropagation()">${esc(ct.phone)}</a>`:'', email:ct.email?`<a href="mailto:${esc(ct.email)}" onclick="event.stopPropagation()">${esc(ct.email)}</a>`:''};}
function ctCard(c){const b=ctBits(c); if(!b) return ''; return `<div class="ccontact">${b.phone?`<div>Call ${b.phone}</div>`:''}${b.email?`<div class="cmail">${b.email}</div>`:''}${/^City of|tenant/i.test(b.ct.organization||'')?`<div class="cwho">${esc(b.ct.organization.split(' (')[0])}</div>`:''}</div>`;}
function ctTop(c){const b=ctBits(c); if(!b) return ''; return `<div class="ctop"><div class="ctop-h">Who to contact</div><div><b>${esc(b.ct.organization||'')}</b></div>${b.phone?`<div>Phone: ${b.phone}</div>`:''}${b.email?`<div>Email: ${b.email}</div>`:''}<div class="src">${b.ct.confidence==='high'?'From the organization’s own page':'From a public listing'} · office contact, not a person</div></div>`;}
function name(c){"""
CSS = """.ccontact{font-size:13px;display:grid;gap:1px;margin:2px 0 2px}
.ccontact a{color:var(--accent,#1f6f3f);font-weight:600;text-decoration:none}
.ccontact .cmail{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ccontact .cwho{color:var(--muted);font-size:12px}
.ctop{background:#e8f3ea;border-radius:10px;padding:10px 12px;display:grid;gap:3px;font-size:14px}
.ctop-h{font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#1f6f3f}
.ctop a{color:#1f6f3f;font-weight:600}
.ctitle{"""
reps = [
 ("function name(c){", HELP),
 ("(typeof CONTACTS!=='undefined'&&CONTACTS[c.apn]&&CONTACTS[c.apn].organization)?CONTACTS[c.apn].organization:",
  "(typeof CONTACTS!=='undefined'&&CONTACTS[c.apn]&&CONTACTS[c.apn].organization&&!/^City of|tenant/i.test(CONTACTS[c.apn].organization))?CONTACTS[c.apn].organization:"),
 ('<div class="ctitle">${esc(name(c))}</div>', '<div class="ctitle">${esc(name(c))}</div>${ctCard(c)}'),
 ('<div class="dbody">${hero}<div class="pad">\n', '<div class="dbody">${hero}<div class="pad">\n    ${ctTop(c)}\n'),
 (".ctitle{", CSS),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
