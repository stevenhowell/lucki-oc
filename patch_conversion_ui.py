"""Add 'Apartments to convert' (the 425 E. Wellington model) as a fifth kind of land on the page."""
from pathlib import Path
S = Path(__file__).parent / "site"
reps = [
 ('<label><input type="checkbox" data-kind="surplus_land_notice" checked> <i class="sw" style="background:#8a5bc9"></i>Public land <span class="note">Surplus Land Act</span></label>',
  '<label><input type="checkbox" data-kind="surplus_land_notice" checked> <i class="sw" style="background:#8a5bc9"></i>Public land <span class="note">Surplus Land Act</span></label>\n      <label><input type="checkbox" data-kind="conversion" checked> <i class="sw" style="background:#0f8a8a"></i>Apartments to convert <span class="note">like 425 E. Wellington</span></label>'),
 ("const COLORS={religious_use:'#3a8a49',housing_element_site:'#2b7bd0',vacant:'#c98a1a',surplus_land_notice:'#8a5bc9'};",
  "const COLORS={religious_use:'#3a8a49',housing_element_site:'#2b7bd0',vacant:'#c98a1a',surplus_land_notice:'#8a5bc9',conversion:'#0f8a8a'};"),
 ("const KIND={religious_use:'Church land',housing_element_site:'City-approved site',vacant:'Empty lot',surplus_land_notice:'Public land'};",
  "const KIND={religious_use:'Church land',housing_element_site:'City-approved site',vacant:'Empty lot',surplus_land_notice:'Public land',conversion:'Apartments to convert'};"),
 ("  surplus_land_notice:{name:'Surplus Land Act (Gov. Code 54220)'",
  "  conversion:{name:'Condo conversion of an existing building',url:'https://www.hcd.ca.gov/sites/default/files/docs/planning-and-community/housing-law-fact-sheets.pdf',note:'No single state law opens this: a condo conversion needs a subdivision map under the Subdivision Map Act and the city’s own conversion rules. Habitat OC is doing exactly this at 425 E. Wellington Ave in Santa Ana (9 units, 2025). Tenants come first: there, current renters under 120% of median income get the first right to buy, and $200,000 was set aside for relocation (City of Santa Ana letter A-2025-094).'},\n  surplus_land_notice:{name:'Surplus Land Act (Gov. Code 54220)'"),
 ("if(c.sources.includes('surplus_land_notice')) out.push(LAW.surplus_land_notice); return out;}",
  "if(c.sources.includes('surplus_land_notice')) out.push(LAW.surplus_land_notice); if(c.sources.includes('conversion')) out.push(LAW.conversion); return out;}"),
 ("const a=c.sources.includes('housing_element_site')?",
  "const a=c.sources.includes('conversion')?(c.apn==='39802812'?'This is the building Habitat OC is already converting: 9 apartments becoming ownership condos, with $80,000 per unit from the City of Santa Ana.':'An existing low-rise apartment building on a lot the size of Habitat OC’s Wellington Ave deal. Buying and converting it to condos skips land and construction. Confirm it is a rental, not condos, and plan for the tenants.'):c.sources.includes('housing_element_site')?"),
 ("const room=c.homes==null?'':c.homes>0?`Room for about ${c.homes} home",
  "const room=c.sources.includes('conversion')?`About ${c.homes} apartments (estimated from lot size). `:c.homes==null?'':c.homes>0?`Room for about ${c.homes} home"),
 ("{religious_use:'Maybe · SB 4',housing_element_site:'Yes · city listed it',vacant:'Maybe · SB 9 / 684',surplus_land_notice:'Maybe · public land'}[kindKey(c)]",
  "{religious_use:'Maybe · SB 4',housing_element_site:'Yes · city listed it',vacant:'Maybe · SB 9 / 684',surplus_land_notice:'Maybe · public land',conversion:'Maybe · condo map'}[kindKey(c)]"),
 ("<div class=\"homes\">${c.homes==null?'Homes: unknown':c.homes>0?'≈ '+c.homes+' home'+(c.homes===1?'':'s'):'No room found'}</div>",
  "<div class=\"homes\">${c.homes==null?'Homes: unknown':c.sources.includes('conversion')?'≈ '+c.homes+' apartments to convert':c.homes>0?'≈ '+c.homes+' home'+(c.homes===1?'':'s'):'No room found'}</div>${c.apn==='39802812'?'<div class=\"tag stage\" style=\"justify-self:start\">Habitat OC’s own 2025 deal</div>':''}"),
 ("<div class=\"cline\">${c.open_acres!=null?c.open_acres.toFixed(1)+' open acres':(c.acres?c.acres.toFixed(1)+' acres':'')} · ${esc(c.city)}</div>",
  "<div class=\"cline\">${c.sources.includes('conversion')?(c.acres?c.acres.toFixed(2)+' acre lot':''):c.open_acres!=null?c.open_acres.toFixed(1)+' open acres':(c.acres?c.acres.toFixed(1)+' acres':'')} · ${esc(c.city)}</div>"),
 ("<div><i style=\"background:${COLORS.surplus_land_notice};border-radius:50%\"></i>Public land</div>",
  "<div><i style=\"background:${COLORS.surplus_land_notice};border-radius:50%\"></i>Public land</div><div><i style=\"background:${COLORS.conversion};border-radius:50%\"></i>Apartments to convert</div>"),
 ("const n=(ks.length<4?1:0)", "const NK=$$('[data-kind]').length; const n=(ks.length<NK?1:0)"),
 ("$('#c-kind').textContent=ks.length<4?'· '+ks.length:''; $('#c-more').textContent=(n-(ks.length<4?1:0))?'· '+(n-(ks.length<4?1:0)):'';",
  "$('#c-kind').textContent=ks.length<NK?'· '+ks.length:''; $('#c-more').textContent=(n-(ks.length<NK?1:0))?'· '+(n-(ks.length<NK?1:0)):'';"),
]
for f in ("app.src.html", "index.html"):
    s = (S / f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b)
    (S / f).write_text(s); print(f, "missing:", miss)
