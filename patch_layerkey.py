"""Small map layers: no outlines, lighter fills, and a key for the layers that are on."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ('fill="${st.fillColor}" fill-opacity="${st.fillOpacity}" stroke="${st.color}" stroke-width="1" vector-effect="non-scaling-stroke">',
  'fill="${st.fillColor}" fill-opacity="${({flood:.38,liquefaction:.22,fire:.32,transit:.24,opportunity:.2,housing_element:.3})[n]??.25}" stroke="none">'),
 ("""`<div><i style="background:#fff;border:2px solid #d4482a"></i>On my list</div>`;\n}""",
  """`<div><i style="background:#fff;border:2px solid #d4482a"></i>On my list</div>`+LAYERKEY();\n}
function LAYERKEY(){const on=Object.entries(STATIC_LAYERS).filter(([n,v])=>v&&LAYER_DATA[n]).map(([n])=>n); if(!on.length) return '';
  const sw=c=>`<i style="background:${c};border-radius:3px;opacity:.85"></i>`;
  const lab={flood:'Flood zone',liquefaction:'Liquefaction zone',fire:'Wildfire zone',transit:'Near frequent transit',housing_element:'City-approved area'};
  return `<div style="border-top:1px solid var(--line);margin-top:4px;padding-top:6px;font-weight:600">Layers</div>`+on.map(n=>n==='opportunity'?`<div>${sw('#2e8b57')}${sw('#f0c24e')}${sw('#e07a5f')}Opportunity: high to low</div>`:`<div>${sw(layerStyle[n].fillColor)}${lab[n]||n}</div>`).join('');}"""),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:60] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
