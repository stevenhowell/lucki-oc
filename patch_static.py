"""Default to one still aerial (county or city) with numbered dots; the interactive map loads only on request."""
from pathlib import Path
S = Path(__file__).parent/"site"
reps = [
 ('  <div id="map" aria-label="Map of candidate sites"></div>',
  '  <div class="mapwrap"><div id="static" class="static" aria-label="Aerial photo with the top sites"></div><div id="map" hidden aria-label="Interactive map of candidate sites"></div><button id="map-toggle" class="maptoggle">Open interactive map</button><div class="slegend" id="slegend"></div></div>'),
 ("#map{min-height:300px;height:100%;background:#2a2d29}",
  "#map{min-height:300px;height:100%;background:#2a2d29}\n.mapwrap{position:relative;min-height:300px;background:#2a2d29;overflow:hidden}\n.mapwrap #map{position:absolute;inset:0}\n.static{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}\n.static .frame{position:relative;width:100%;max-height:100%;aspect-ratio:1600/1000}\n.static img{display:block;width:100%;height:100%;object-fit:contain}\n.static svg{position:absolute;inset:0;width:100%;height:100%}\n.static .dot{cursor:pointer}\n.maptoggle{position:absolute;right:12px;top:12px;z-index:1001;box-shadow:0 2px 8px rgba(0,0,0,.25)}\n.slegend{position:absolute;left:12px;bottom:12px;z-index:1000;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-size:12px;display:grid;gap:4px}\n.slegend i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;vertical-align:-2px}\n.static .note{position:absolute;left:12px;top:12px;background:rgba(0,0,0,.6);color:#fff;font-size:12px;padding:4px 10px;border-radius:999px}"),
 # data: overview + city stills
 ("let D,AER,BASE;", "let D,AER,BASE; const OV=await fetch('overview.json').then(r=>r.ok?r.json():null).catch(()=>null); const CITYV=await fetch('cities.json').then(r=>r.ok?r.json():{}).catch(()=>({}));"),
 # lazy base imagery
 ("BASE.forEach(t=>L.imageOverlay(t.file,bnd(t.bbox3857),{interactive:false}).addTo(map));",
  "let interactive=false, baseLoaded=false;\nfunction loadBase(){ if(baseLoaded) return; baseLoaded=true; BASE.forEach(t=>L.imageOverlay(t.file,bnd(t.bbox3857),{interactive:false}).addTo(map)); }"),
 ("let sized=false; new ResizeObserver(()=>{const z=map.getSize(); map.invalidateSize(); if(!sized&&$('#map').clientHeight>50){sized=true; fitCity(); update();}}).observe(document.getElementById('map'));",
  "new ResizeObserver(()=>{ if(interactive) map.invalidateSize(); else drawStatic(); }).observe(document.querySelector('.mapwrap'));"),
 # markers: static when not interactive
 ("function drawMarkers(){\n  dots.clearLayers(); outlines.clearLayers();",
  "function drawMarkers(){\n  if(!interactive){ drawStatic(); return; }\n  dots.clearLayers(); outlines.clearLayers();"),
 ("function inView(r){const sz=map.getSize(); if(!$('#f-move').checked||sz.x<50||sz.y<50) return r;",
  "function inView(r){const sz=map.getSize(); if(!interactive||!$('#f-move').checked||sz.x<50||sz.y<50) return r;"),
 ("function openSite(c){open=c; renderDrawer(c); const z=Math.max(map.getZoom(),17); map.flyTo([c.centroid[1],c.centroid[0]],z,{duration:.6});",
  "function openSite(c){open=c; renderDrawer(c); if(interactive){const z=Math.max(map.getZoom(),17); map.flyTo([c.centroid[1],c.centroid[0]],z,{duration:.6});} else drawStatic();"),
 ("async function toggleLayer(name,on){", "async function toggleLayer(name,on){\n  if(on&&!interactive) setInteractive(true);"),
 # the static view + toggle
 ("// ---------- filters ----------", r"""// ---------- still aerial (default) ----------
const merc=(lon,lat)=>[lon*R/180, Math.log(Math.tan((90+lat)*Math.PI/360))/(Math.PI/180)*R/180];
function drawStatic(){
  const box=$('#static'); if(!box||interactive) return;
  const city=$('#city').value; const V=(city&&CITYV[city])?{...CITYV[city],img:CITYV[city].file,label:city+', 2025 aerial'}:OV?{...OV,img:'overview.jpg',label:'Orange County, 2025 aerial'}:null;
  if(!V){box.innerHTML='<div class="note">Photo not available. Use the interactive map.</div>';return}
  const rows=(typeof filtered==='function')?filtered():C; const top=rows.slice(0,10);
  const px=c=>{const [x,y]=merc(c.centroid[0],c.centroid[1]);return [(x-V.bbox3857[0])/(V.bbox3857[2]-V.bbox3857[0])*V.w,(V.bbox3857[3]-y)/(V.bbox3857[3]-V.bbox3857[1])*V.h]};
  const inside=([x,y])=>x>=0&&y>=0&&x<=V.w&&y<=V.h; const zoomed=!!(city&&CITYV[city]);
  const many=rows.slice(0,zoomed?300:600).map(c=>[c,px(c)]).filter(([c,p])=>inside(p)&&!top.includes(c));
  const sel=open&&inside(px(open))?open:null;
  const dot=(c,[x,y],i)=>{const t=i>=0, col=COLORS[kindKey(c)]||'#666', r=t?(zoomed?15:10):(zoomed?6:4);
    return `<g class="dot" data-apn="${esc(c.apn)}"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${col}" fill-opacity="${t?1:.7}" stroke="${PIPE[c.apn]?'#d4482a':'#fff'}" stroke-width="${PIPE[c.apn]?3:t?2:1}"><title>${esc(name(c))}</title></circle>${t?`<text x="${x.toFixed(1)}" y="${(y+5).toFixed(1)}" text-anchor="middle" font-size="${zoomed?15:11}" font-weight="700" fill="#fff" style="pointer-events:none">${i+1}</text>`:''}</g>`};
  const selMark=sel?(()=>{const [x,y]=px(sel);return `<circle cx="${x}" cy="${y}" r="${zoomed?26:18}" fill="none" stroke="#ff8a5b" stroke-width="4"/>`})():'';
  box.innerHTML=`<div class="frame"><img src="${V.img}" alt="${esc(V.label)}"><svg viewBox="0 0 ${V.w} ${V.h}" role="img" aria-label="Top sites">${many.map(([c,p])=>dot(c,p,-1)).join('')}${top.map((c,i)=>inside(px(c))?dot(c,px(c),i):'').join('')}${selMark}</svg></div><div class="note">${esc(V.label)} · numbers match the list</div>`;
  box.querySelectorAll('.dot').forEach(d=>d.onclick=()=>{const c=byApn.get(d.dataset.apn); if(c) openSite(c)});
  $('#slegend').innerHTML=Object.entries(KIND).map(([k,l])=>`<div><i style="background:${COLORS[k]}"></i>${l}</div>`).join('')+`<div><i style="background:#fff;border:2px solid #d4482a"></i>On my list</div>`;
}
function setInteractive(on){
  interactive=on; $('#static').hidden=on; $('#slegend').hidden=on; $('#map').hidden=!on;
  $('#map-toggle').textContent=on?'Back to photo':'Open interactive map';
  $('#move-wrap')&&($('#move-wrap').hidden=!on);
  if(on){ loadBase(); setTimeout(()=>{map.invalidateSize(); if(open) map.setView([open.centroid[1],open.centroid[0]],17); else fitCity(); drawMarkers(); if(tab==='explore'&&!open) renderExplore();},60); }
  else { drawStatic(); if(tab==='explore'&&!open) renderExplore(); }
}
$('#map-toggle').onclick=()=>setInteractive(!interactive);

// ---------- filters ----------"""),
 ('<label class="move"><input type="checkbox" id="f-move"> Only what\'s on the map</label>', '<label class="move" id="move-wrap" hidden><input type="checkbox" id="f-move"> Only what\'s on the map</label>'),
]
for f in ("app.src.html", "index.html"):
    s = (S/f).read_text(); miss = [a[:70] for a, b in reps if a not in s]
    for a, b in reps: s = s.replace(a, b, 1)
    (S/f).write_text(s); print(f, "missing:", miss)
