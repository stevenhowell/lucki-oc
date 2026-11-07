"""Still aerial with + / − zoom and drag to pan; map layers drawn on the photo; no heavy interactive map."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ('<button id="map-toggle" class="maptoggle">Open interactive map</button>',
  '<div class="zoomctl" role="group" aria-label="Zoom"><button id="z-in" aria-label="Zoom in">+</button><button id="z-out" aria-label="Zoom out">−</button></div>'),
 (".maptoggle{", ".zoomctl{position:absolute;left:12px;top:12px;z-index:1001;display:grid;border:1px solid var(--line);border-radius:6px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.25)}\n.zoomctl button{width:44px;height:44px;min-height:44px;border:0;border-radius:0;background:#fff;color:#111;font-size:24px;padding:0}\n.zoomctl button+button{border-top:1px solid #ccc}\n.zoomctl button:disabled{color:#bbb}\n.static{cursor:grab;touch-action:none}\n.static.dragging{cursor:grabbing}\n.static .frame{transform-origin:0 0;will-change:transform}\n.maptoggle{"),
 (".static .note{position:absolute;left:12px;top:12px;", ".static .note{position:absolute;left:68px;top:12px;"),
 # zoom state + transform + pan
 ("function drawStatic(){", r"""let ZS=1, TX=0, TY=0; const STATIC_LAYERS={}; const LAYER_DATA={};
function applyZoom(){const f=$('#static .frame'); if(!f) return; const box=$('#static').getBoundingClientRect(), fr=f.getBoundingClientRect(); f.style.transform=`translate(${TX}px,${TY}px) scale(${ZS})`; $('#z-out').disabled=ZS<=1; $('#z-in').disabled=ZS>=8;
  f.querySelectorAll('circle').forEach(c=>{const r0=+c.dataset.r; if(r0) c.setAttribute('r',(r0/Math.sqrt(ZS)).toFixed(1))}); f.querySelectorAll('text').forEach(t=>{const s0=+t.dataset.s; if(s0) t.setAttribute('font-size',(s0/Math.sqrt(ZS)).toFixed(1))});}
function zoomBy(k,cx,cy){const box=$('#static').getBoundingClientRect(); const f=$('#static .frame'); if(!f) return; const fx=cx??box.width/2, fy=cy??box.height/2;
  const nz=Math.min(8,Math.max(1,ZS*k)); const ox=f.offsetLeft, oy=f.offsetTop; const px=(fx-ox-TX)/ZS, py=(fy-oy-TY)/ZS; ZS=nz; TX=fx-ox-px*ZS; TY=fy-oy-py*ZS; if(ZS===1){TX=0;TY=0} applyZoom();}
function drawStatic(){"""),
 # dots get data-r / data-s so zoom can keep them readable; outlines/layers keep stroke width
 ('<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${col}"', '<circle data-r="${r}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${col}"'),
 ('<text x="${x.toFixed(1)}" y="${(y+5).toFixed(1)}" text-anchor="middle" font-size="${zoomed?15:11}"', '<text data-s="${zoomed?15:11}" x="${x.toFixed(1)}" y="${(y+5).toFixed(1)}" text-anchor="middle" font-size="${zoomed?15:11}"'),
 # layers drawn into the still photo
 ("  box.innerHTML=`<div class=\"frame\"><img src=\"${V.img}\" alt=\"${esc(V.label)}\"><svg viewBox=\"0 0 ${V.w} ${V.h}\" role=\"img\" aria-label=\"Top sites\">${many",
  "  const P=(lon,lat)=>{const [x,y]=merc(lon,lat);return ((x-V.bbox3857[0])/(V.bbox3857[2]-V.bbox3857[0])*V.w).toFixed(1)+' '+((V.bbox3857[3]-y)/(V.bbox3857[3]-V.bbox3857[1])*V.h).toFixed(1)};\n  const lay=Object.entries(STATIC_LAYERS).filter(([n,on])=>on&&LAYER_DATA[n]).map(([n])=>`<g>${LAYER_DATA[n].features.map(f=>{const g=f.geometry; if(!g) return ''; const polys=g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[]; const st=n==='opportunity'?{fillColor:OPP[(f.properties.oppcat||'').trim()]||'#999',fillOpacity:.32,color:'#333'}:layerStyle[n]; return `<path d=\"${polys.map(p=>p.map(r=>'M'+r.map(q=>P(q[0],q[1])).join(' L ')+'Z').join(' ')).join(' ')}\" fill=\"${st.fillColor}\" fill-opacity=\"${st.fillOpacity}\" stroke=\"${st.color}\" stroke-width=\"1\" vector-effect=\"non-scaling-stroke\"><title>${esc(n==='opportunity'?(f.properties.oppcat||''):n==='flood'?'FEMA zone '+(f.properties.FLD_ZONE||''):'')}</title></path>`}).join('')}</g>`).join('');\n  box.innerHTML=`<div class=\"frame\"><img src=\"${V.img}\" alt=\"${esc(V.label)}\"><svg viewBox=\"0 0 ${V.w} ${V.h}\" role=\"img\" aria-label=\"Top sites\">${lay}${many"),
 ("  box.querySelectorAll('.dot').forEach(d=>d.onclick=()=>{const c=byApn.get(d.dataset.apn); if(c) openSite(c)});",
  "  box.querySelectorAll('.dot').forEach(d=>d.onclick=e=>{if(dragMoved) return; const c=byApn.get(d.dataset.apn); if(c) openSite(c)});\n  applyZoom();"),
 # layer toggles go to the still photo
 ("async function toggleLayer(name,on){\n  if(on&&!interactive) setInteractive(true);",
  "async function toggleLayer(name,on){\n  if(!interactive){ if(on&&!LAYER_DATA[name]) LAYER_DATA[name]=await fetch('layers/'+name+'.json').then(r=>r.json()).catch(()=>null); STATIC_LAYERS[name]=on; drawStatic(); drawLegend(); return; }"),
 # wiring: buttons, wheel, drag; reset zoom on city change
 ("$('#map-toggle').onclick=()=>setInteractive(!interactive);",
  r"""$('#z-in').onclick=()=>zoomBy(2); $('#z-out').onclick=()=>zoomBy(.5);
let dragMoved=false;
(()=>{const el=$('#static'); let sx,sy,tx0,ty0,down=false;
  el.addEventListener('pointerdown',e=>{if(ZS<=1) return; down=true; dragMoved=false; sx=e.clientX; sy=e.clientY; tx0=TX; ty0=TY; el.classList.add('dragging')});
  window.addEventListener('pointermove',e=>{if(!down) return; const dx=e.clientX-sx, dy=e.clientY-sy; if(Math.abs(dx)+Math.abs(dy)>4) dragMoved=true; TX=tx0+dx; TY=ty0+dy; applyZoom()});
  window.addEventListener('pointerup',()=>{if(down){down=false; el.classList.remove('dragging'); setTimeout(()=>dragMoved=false,0)}});
  el.addEventListener('wheel',e=>{e.preventDefault(); const r=el.getBoundingClientRect(); zoomBy(e.deltaY<0?1.25:.8,e.clientX-r.left,e.clientY-r.top)},{passive:false});
})();"""),
 ("$('#city').onchange=()=>{", "$('#city').onchange=()=>{ZS=1;TX=0;TY=0;"),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
