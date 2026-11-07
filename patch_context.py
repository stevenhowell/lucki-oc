"""Real deals on their sites (St. Ann's, Wellington), the reasoning behind conversion counts,
and developer-vs-family math in 'Does it pencil?'."""
from pathlib import Path
S = Path(__file__).parent/"site"
REAL = r"""const REAL={
 '64403405':{name:'Neighborhood Congregational Church, 340 St. Ann’s Dr',tag:'Real SB 4 project',t:'This is a real SB 4 project. Neighborhood Congregational Church is leasing this parking lot for 29 affordable rental homes in a three-story building (developer: Related California). Laguna Beach committed about $6.71M: $2.5M from the state (HCD), a $2.5M city match and up to $740,000 in fee waivers. Three issues it ran into: neighbors objected, the plan was cut from 44 homes to 29, and the design-review exemptions for the church’s replacement buildings drew criticism. Lucki estimated about 9 ownership townhomes here; the real project fits about three times that as rentals, so Lucki’s numbers are on the low side.',src:'https://www.lagunabeachindy.com/news/city-commits-6-71m-in-funding-for-affordable-housing-project/article_f60c6735-3a80-42e6-a47d-164c19c713c1.html'},
 '39802812':{name:'425 E. Wellington Ave',tag:'Habitat OC’s own deal',t:'This is Habitat OC’s own 2025 deal: an existing 9-unit apartment building becoming 9 ownership condos. Santa Ana reserved $920,000: $720,000 as down-payment help ($80,000 per home) and up to $200,000 for tenant relocation. Current tenants under 120% of median income get the first right to buy.',src:'City of Santa Ana pre-commitment letter A-2025-094, 2025-07-01'}
};
"""
reps = [
 ("// ---------- data ----------", REAL + "// ---------- data ----------"),
 # names
 ("function name(c){return c.worship&&c.worship.name?", "function name(c){return REAL[c.apn]?REAL[c.apn].name:c.worship&&c.worship.name?"),
 # card badge (replace the old Wellington-only tag)
 ("${c.apn==='39802812'?'<div class=\"tag stage\" style=\"justify-self:start\">Habitat OC’s own 2025 deal</div>':''}",
  "${REAL[c.apn]?`<div class=\"tag stage\" style=\"justify-self:start\">${REAL[c.apn].tag}</div>`:''}"),
 # drawer: a real-deal box above the review box
 ("    ${(()=>{const rv=reviews(c);", "    ${REAL[c.apn]?`<div class=\"track\" style=\"background:#e8f3ea;color:#123a1b\"><div style=\"font-weight:700\">${REAL[c.apn].tag}</div><div>${REAL[c.apn].t}</div><div class=\"src\" style=\"color:inherit;opacity:.75\">${/^https?:/.test(REAL[c.apn].src)?`<a href=\"${REAL[c.apn].src}\" target=\"_blank\" rel=\"noopener\" style=\"color:inherit\">Source: Laguna Beach Independent</a>`:'Source: '+REAL[c.apn].src}</div></div>`:''}\n    ${(()=>{const rv=reviews(c);"),
 # conversion reasoning in the summary
 ("const room=c.sources.includes('conversion')?`About ${c.homes} apartments (estimated from lot size). `",
  "const room=c.sources.includes('conversion')?`About ${c.homes} apartments: a ${(c.acres||0).toFixed(2)}-acre lot × 43 apartments per acre, the density of Habitat OC’s Wellington Ave building (9 apartments on 0.21 acres). Confirm the real count with the County Assessor. `"),
 # developer vs family rows in the pro forma
 ("      <span>Family can pay</span><span>− ${fmt(p.pay)}</span>",
  "      <span class=\"src\" style=\"grid-column:1/-1;margin-top:4px\">A builder selling at market vs. a family on a low income:</span>\n      <span>Market price for this home</span><span>${fmt(PRO.market_psf*PRO.unit_sqft)}</span><span>Builder’s margin at market</span><span class=\"ans ${PRO.market_psf*PRO.unit_sqft-p.cost>=0?'pass':'fail'}\">${fmt(PRO.market_psf*PRO.unit_sqft-p.cost)}</span>\n      <span>Family can pay</span><span>− ${fmt(p.pay)}</span>"),
 ("const PRO={unit_sqft:1000,", "const PRO={market_psf:749,unit_sqft:1000,"),
 ("Prototype, not financial advice.</div>`;", "Market price $749/sq ft: same Terner report, LA townhome sales price (2023). The difference between the market price and what a family can pay is why builders don’t make these homes without help. Prototype, not financial advice.</div>`;"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
