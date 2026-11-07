"""Replace the 'Does it pencil?' section with a per-site pro forma people can change:
homes on the lot, land deal (market / donated), mortgage rate, family incomes. Sources: Terner Center June 2024
'Making Missing Middle Pencil' (LA: $334/sq ft fourplex-condo hard cost, $40k/unit fees, $125/sq ft land),
HCD 2026 OC income limits, CalHFA FHA 6.625% (2026-11-06). Soft costs 20% of hard = ASSUMPTION."""
from pathlib import Path
S = Path(__file__).parent/"site"
JS_MODEL = r"""
// ---------- pro forma (Terner Center 2024 + HCD 2026 + CalHFA; ASSUMPTIONS labelled) ----------
const PRO={unit_sqft:1000,hard_psf:334,fees:40000,soft_pct:.20,land_psf:125,tax:.011,hoa:350,ins:120,share:.30};
const INCOME={low:93050,moderate:148850,mix:(93050+148850)/2};
function canPay(income,rate){const monthly=income*PRO.share/12; let lo=0,hi=3e6; for(let i=0;i<40;i++){const p=(lo+hi)/2,m=rate/12,pi=m?p*m/(1-Math.pow(1+m,-360)):p/360; if(pi+p*PRO.tax/12+PRO.hoa+PRO.ins>monthly) hi=p; else lo=p;} return Math.round(lo/1000)*1000;}
function landDefault(c){return (c.sources.includes('religious_use')||c.sources.includes('surplus_land_notice'))?'donated':'market'}
function siteSqft(c){return Math.round(((c.open_acres??c.acres)||0)*43560)}
function pro(c,o={}){
  const homes=Math.max(1,o.homes??c.homes??1), land=o.land??landDefault(c), rate=o.rate??0, fam=o.fam??'low';
  const build=PRO.unit_sqft*PRO.hard_psf, soft=build*PRO.soft_pct, fees=PRO.fees;
  const landTotal=land==='market'?siteSqft(c)*PRO.land_psf:0, landPer=landTotal/homes;
  const cost=build+soft+fees+landPer, pay=canPay(INCOME[fam],rate);
  const prog=c.fund.city_program, help=prog==='unknown'?0:prog.per_unit;
  const gap=Math.round(cost-pay-help);
  return {homes,land,rate,fam,build,soft,fees,landTotal,landPer,cost,pay,help,gap,total:gap*homes};
}
"""
reps = [
 ("// ---------- data ----------", JS_MODEL + "\n// ---------- data ----------"),
 # card tag + filter + sort use the pro forma for new-build sites
 ("function gap(c){const f=c.fund;", "function gap(c){ if(!c.sources.includes('conversion')){const p=pro(c); return p.gap<=0?{t:'Pencils at 0%'+(p.land==='donated'?' · land donated':''),k:'pass'}:{t:fmt(p.gap)+' short/home at 0%',k:p.gap<100000?'warn':'fail'}} const f=c.fund;"),
 ("function pencils(c){return c.fund.gap_condo_at_0pct!=null&&c.fund.gap_condo_at_0pct<=0}", "function pencils(c){return c.sources.includes('conversion')?(c.fund.gap_condo_at_0pct!=null&&c.fund.gap_condo_at_0pct<=0):pro(c).gap<=0}"),
 ("if(s==='gap') r=[...r].sort((a,b)=>(a.fund.gap_condo_at_0pct??1e9)-(b.fund.gap_condo_at_0pct??1e9));", "if(s==='gap') r=[...r].sort((a,b)=>(a.sources.includes('conversion')?(a.fund.gap_condo_at_0pct??1e9):pro(a).gap)-(b.sources.includes('conversion')?(b.fund.gap_condo_at_0pct??1e9):pro(b).gap));"),
 ("<option value=\"gap\">Smallest gap</option>", "<option value=\"gap\">Smallest gap per home</option>"),
 ("<label><input type=\"checkbox\" id=\"f-pencil\"> Only where a home pencils at 0%</label>", "<label><input type=\"checkbox\" id=\"f-pencil\"> Only where a home pencils at 0% (land donated for church and public land)</label>"),
 # drawer: replace fundBody for new-build sites with the interactive pro forma
 ("${q('Does it pencil?',g.t,g.k,fundBody)}", "${c.sources.includes('conversion')?q('Does it pencil?',g.t,g.k,fundBody):`<details class=\"q\" id=\"penq\"><summary><span class=\"qq\">Does it pencil?</span><span class=\"ans ${g.k}\" id=\"pen-ans\">${g.t}</span></summary><div class=\"body\" id=\"pen\"></div></details>`}"),
 ("  wireDraft(c); drawMarkers();\n}", "  if(!c.sources.includes('conversion')) wirePencil(c);\n  wireDraft(c); drawMarkers();\n}\n" + r"""function wirePencil(c){
  const box=$('#pen'); const st={homes:Math.max(1,c.homes||1),land:landDefault(c),rate:0,fam:'low'};
  const maxH=Math.max(60,Math.ceil((c.open_acres??c.acres??1)*60));
  const seg=(name,opts)=>`<div class="stages" role="group" aria-label="${name}">${opts.map(([v,l])=>`<button data-k="${name}" data-v="${v}" aria-pressed="${String(st[name])===String(v)}">${l}</button>`).join('')}</div>`;
  function draw(){ const p=pro(c,st); const pc=(n)=>Math.round(100*n/Math.max(p.cost,1));
    box.innerHTML=`<div><b>Homes on this site</b> <span class="src">(Lucki’s estimate: ${c.homes??'unknown'})</span></div>
    <div style="display:flex;gap:10px;align-items:center"><input id="pen-h" type="range" min="1" max="${maxH}" value="${st.homes}" style="flex:1"><b style="min-width:3ch;text-align:right">${st.homes}</b></div>
    <div><b>Land</b></div>${seg('land',[['donated','Donated or $1 lease'],['market','Bought at market']])}
    <div><b>Mortgage rate</b></div>${seg('rate',[['0','0% (Habitat-style)'],['0.03','3%'],['0.06625','Today 6.6%']])}
    <div><b>Families</b></div>${seg('fam',[['low','Low income $93k'],['mix','Mix'],['moderate','Moderate $149k']])}
    <div style="display:grid;grid-template-columns:1fr auto;gap:4px 12px;font-variant-numeric:tabular-nums;margin-top:6px">
      <span>Build a home</span><span>${fmt(p.build)}</span><span>Design, permits, finance</span><span>${fmt(p.soft)}</span><span>City fees</span><span>${fmt(p.fees)}</span>
      <span>Land, per home</span><span>${p.land==='donated'?'$0':fmt(p.landPer)}</span><span><b>Cost per home</b></span><span><b>${fmt(p.cost)}</b></span>
      <span>Family can pay</span><span>− ${fmt(p.pay)}</span><span>City help</span><span>− ${fmt(p.help)}</span>
      <span><b>${p.gap<=0?'Left over per home':'Gap per home'}</b></span><span class="ans ${p.gap<=0?'pass':p.gap<100000?'warn':'fail'}">${fmt(Math.abs(p.gap))}</span>
      <span>${p.gap<=0?'Left over, whole site':'Gap, whole site'}</span><span>${fmt(Math.abs(p.total))}</span></div>
    <div class="bar" style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin-top:4px" aria-hidden="true"><i style="width:${pc(p.build)}%;background:var(--accent)"></i><i style="width:${pc(p.soft+p.fees)}%;background:var(--warn)"></i><i style="width:${pc(p.landPer)}%;background:var(--fail)"></i></div>
    <div class="fine">${p.land==='market'?`Land: ${siteSqft(c).toLocaleString()} sq ft of ${c.open_acres!=null?'open ':''}land × $125/sq ft = ${fmt(p.landTotal)}, split across ${p.homes} home${p.homes===1?'':'s'}. More homes shrink this line.`:'With the land donated or leased for $1, more homes don’t change the cost per home; they change how many families it helps.'}</div>
    <div class="src">Building $334/sq ft and fees $40,000/home: Terner Center, “Making Missing Middle Pencil”, June 2024 (Los Angeles, 2023 dollars). Land $125/sq ft: same report, LA; no Orange County figure found, ASSUMPTION. Design, permits and financing at 20% of building cost: ASSUMPTION. 1,000 sq ft home. What a family can pay: 30% of income covers the loan, 1.1% tax, $350 HOA and $120 insurance; incomes from HCD’s 2026 Orange County limits. Prototype, not financial advice.</div>`;
    $('#pen-ans').textContent=p.gap<=0?'Pencils':fmt(p.gap)+' short/home'; $('#pen-ans').className='ans '+(p.gap<=0?'pass':p.gap<100000?'warn':'fail');
    $('#pen-h').oninput=e=>{st.homes=+e.target.value;draw()};
    box.querySelectorAll('[data-k]').forEach(b=>b.onclick=()=>{st[b.dataset.k]=b.dataset.k==='rate'?+b.dataset.v:b.dataset.v;draw()});
  }
  draw();
}"""),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
