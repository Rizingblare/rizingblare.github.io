(() => {
  'use strict';
  const TAU = Math.PI * 2;
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const fmt = (v, n=3) => (Math.abs(v) < 0.0005 ? 0 : v).toFixed(n).replace('-', '−');
  const sinc = z => Math.abs(z) < 1e-9 ? 1 : Math.sin(z) / z;
  const $ = id => document.getElementById(id);

  document.querySelectorAll('.lab > svg').forEach(svg => {
    const wrapper = document.createElement('div');
    wrapper.className = 'svg-scroll';
    wrapper.setAttribute('tabindex', '0');
    wrapper.setAttribute('aria-label', '대화형 그래프. 작은 화면에서는 좌우로 스크롤할 수 있습니다.');
    svg.parentNode.insertBefore(wrapper, svg);
    wrapper.appendChild(svg);
  });

  function linePath(fn, x0, x1, yBase, yScale, samples=600) {
    let d = '';
    for (let i=0; i<=samples; i++) {
      const u = i / samples, x = x0 + (x1-x0)*u, y = yBase - yScale*fn(u);
      d += (i ? 'L' : 'M') + x.toFixed(2) + ' ' + y.toFixed(2);
    }
    return d;
  }

  // 01 · Superposition
  const superDefaults = {a1:1,f1:1,p1:0,a2:.65,f2:3,p2:25,a3:.35,f3:5,p3:-40};
  const superIds = Object.keys(superDefaults);
  let superPhaseTime = 0, superCursorU = .5, superRunning = false, superRaf = 0, superLast = 0;
  function superParams() {
    return [1,2,3].map(n => ({
      a:+$('a'+n).value, f:+$('f'+n).value, p:+$('p'+n).value * Math.PI/180
    }));
  }
  function compValue(c, u) { return c.a * Math.sin(TAU * c.f * (2*u + superPhaseTime) + c.p); }
  function updateSuperposition() {
    const cs = superParams(), x0=150, x1=940, scale=34;
    const bases=[105,225,345];
    cs.forEach((c,i) => $(['waveA','waveB','waveC'][i]).setAttribute('d', linePath(u => compValue(c,u), x0,x1,bases[i],scale,700)));
    $('waveSum').setAttribute('d', linePath(u => cs.reduce((s,c)=>s+compValue(c,u),0), x0,x1,485,scale,700));
    [1,2,3].forEach((n,i) => {
      $('a'+n+'Out').textContent=(+$('a'+n).value).toFixed(2);
      $('f'+n+'Out').textContent=(+$('f'+n).value).toFixed(1)+' Hz';
      const pv=+$('p'+n).value; $('p'+n+'Out').textContent=(pv<0?'−':'')+Math.abs(pv)+'°';
      const sign=pv<0?'−':'+'; $('eq'+['A','B','C'][i]).textContent=`${(+$('a'+n).value).toFixed(2)}·sin(2π·${(+$('f'+n).value).toFixed(1)}t ${sign} ${Math.abs(pv)}°)`;
    });
    updateSuperCursor(superCursorU);
  }
  function updateSuperCursor(u) {
    superCursorU=clamp(u,0,1); const cs=superParams(), x=150+790*superCursorU, scale=34;
    const vals=cs.map(c=>compValue(c,superCursorU)), sum=vals.reduce((a,b)=>a+b,0), bases=[105,225,345];
    $('superCursor').setAttribute('x1',x); $('superCursor').setAttribute('x2',x);
    ['dotA','dotB','dotC'].forEach((id,i)=>{ $(id).setAttribute('cx',x); $(id).setAttribute('cy',bases[i]-scale*vals[i]); });
    $('dotSum').setAttribute('cx',x); $('dotSum').setAttribute('cy',485-scale*sum);
    const displayT = 2*superCursorU + superPhaseTime;
    $('superReadout').textContent=`t = ${fmt(displayT,2)} s · ${fmt(vals[0],2)} + ${fmt(vals[1],2)} + ${fmt(vals[2],2)} = ${fmt(sum,2)}`;
  }
  superIds.forEach(id => $(id).addEventListener('input', updateSuperposition));
  $('superSvg').addEventListener('pointermove', e => { const r=e.currentTarget.getBoundingClientRect(); const x=(e.clientX-r.left)/r.width*980; updateSuperCursor((x-150)/790); });
  $('superReset').addEventListener('click',()=>{ Object.entries(superDefaults).forEach(([k,v])=>$(k).value=v); superPhaseTime=0; updateSuperposition(); });
  $('superPlay').addEventListener('click',()=>{
    superRunning=!superRunning; $('superPlay').setAttribute('aria-pressed',String(superRunning)); $('superPlay').textContent=superRunning?'❚❚ 일시정지':'▶ 시간 이동';
    if(superRunning){superLast=performance.now(); superRaf=requestAnimationFrame(superTick);} else cancelAnimationFrame(superRaf);
  });
  function superTick(now){ if(!superRunning)return; const dt=(now-superLast)/1000; superLast=now; superPhaseTime=(superPhaseTime+dt*.18)%10; updateSuperposition(); superRaf=requestAnimationFrame(superTick); }
  updateSuperposition();

  // 02 · Fourier series
  function updateSeries() {
    const N=+$('terms').value, x0=70,x1=940,base=185,scale=82;
    const approx = u => { const x=-Math.PI+TAU*u; let s=0; for(let k=1;k<=N;k++){const n=2*k-1;s+=Math.sin(n*x)/n;} return 4/Math.PI*s; };
    $('squareApprox').setAttribute('d',linePath(approx,x0,x1,base,scale,1000));
    const yTop=base-scale, yBot=base+scale;
    $('squareTarget').setAttribute('d',`M${x0} ${yBot}H${(x0+x1)/2}V${yTop}H${x1}`);
    const bars=$('harmonicBars'); bars.innerHTML='';
    const maxN=49, chartX0=90, chartX1=930, chartBase=450, maxH=75;
    for(let n=1;n<=maxN;n+=2){
      const x=chartX0+(n-1)/(maxN-1)*(chartX1-chartX0), used=n<=2*N-1;
      const h=maxH*(1/n); const line=document.createElementNS('http://www.w3.org/2000/svg','line');
      line.setAttribute('x1',x);line.setAttribute('x2',x);line.setAttribute('y1',chartBase);line.setAttribute('y2',chartBase-h);
      line.setAttribute('stroke',used?'#8dabff':'#394354');line.setAttribute('stroke-width',used?'7':'3');line.setAttribute('stroke-linecap','round');bars.appendChild(line);
      if(n<=9){const text=document.createElementNS('http://www.w3.org/2000/svg','text');text.setAttribute('x',x);text.setAttribute('y',477);text.setAttribute('text-anchor','middle');text.setAttribute('class','plot-small');text.textContent=n;bars.appendChild(text);}
    }
    $('termsOut').textContent=N+'개';
    const list=[];for(let k=1;k<=Math.min(N,6);k++)list.push(2*k-1); const suffix=N>6?', …':'';
    $('seriesReadout').textContent=`${list.join(', ')}${suffix}번째 고조파 사용 · 최고 ${2*N-1}차`;
  }
  $('terms').addEventListener('input',updateSeries); $('termsReset').addEventListener('click',()=>{$('terms').value=1;updateSeries();}); updateSeries();

  // 03 · Euler
  let eulerRunning=false,eulerRaf=0,eulerLast=0;
  function updateEuler() {
    const deg=+$('angle').value, th=deg*Math.PI/180, cx=245,cy=235,r=132;
    const px=cx+r*Math.cos(th), py=cy-r*Math.sin(th);
    $('phasor').setAttribute('x2',px);$('phasor').setAttribute('y2',py);$('phasorPoint').setAttribute('cx',px);$('phasorPoint').setAttribute('cy',py);
    $('projX').setAttribute('x1',px);$('projX').setAttribute('y1',py);$('projX').setAttribute('x2',px);$('projX').setAttribute('y2',cy);
    $('projY').setAttribute('x1',px);$('projY').setAttribute('y1',py);$('projY').setAttribute('x2',cx);$('projY').setAttribute('y2',py);
    const arcR=42, endX=cx+arcR*Math.cos(th), endY=cy-arcR*Math.sin(th), large=deg>180?1:0;
    $('angleArc').setAttribute('d',deg===0?'':`M${cx+arcR} ${cy}A${arcR} ${arcR} 0 ${large} 0 ${endX} ${endY}`);
    $('thetaLabel').setAttribute('x',cx+52*Math.cos(th/2));$('thetaLabel').setAttribute('y',cy-52*Math.sin(th/2));
    const x0=505,x1=940, amp=55;
    $('cosPath').setAttribute('d',linePath(u=>Math.cos(TAU*u),x0,x1,170,amp,500));
    $('sinPath').setAttribute('d',linePath(u=>Math.sin(TAU*u),x0,x1,330,amp,500));
    const mx=x0+(x1-x0)*deg/360; $('angleMarker').setAttribute('x1',mx);$('angleMarker').setAttribute('x2',mx);
    $('cosDot').setAttribute('cx',mx);$('cosDot').setAttribute('cy',170-amp*Math.cos(th)); $('sinDot').setAttribute('cx',mx);$('sinDot').setAttribute('cy',330-amp*Math.sin(th));
    $('angleOut').textContent=deg+'°';$('eulerReadout').textContent=`cos θ = ${fmt(Math.cos(th))} · sin θ = ${fmt(Math.sin(th))}`;
  }
  $('angle').addEventListener('input',updateEuler);$('eulerReset').addEventListener('click',()=>{$('angle').value=0;updateEuler();});
  $('eulerPlay').addEventListener('click',()=>{eulerRunning=!eulerRunning;$('eulerPlay').setAttribute('aria-pressed',String(eulerRunning));$('eulerPlay').textContent=eulerRunning?'❚❚ 일시정지':'▶ 회전';if(eulerRunning){eulerLast=performance.now();eulerRaf=requestAnimationFrame(eulerTick)}else cancelAnimationFrame(eulerRaf);});
  function eulerTick(now){if(!eulerRunning)return;const dt=(now-eulerLast)/1000;eulerLast=now;$('angle').value=(+$('angle').value+dt*55)%360;updateEuler();eulerRaf=requestAnimationFrame(eulerTick)}
  updateEuler();

  // 04 · Orthogonality
  const orthSignalFn = t => Math.sin(TAU*t)+.65*Math.sin(TAU*3*t)+.35*Math.sin(TAU*5*t);
  function areaSegments(fn,x0,x1,base,scale,samples,positive){
    const values=[];for(let i=0;i<=samples;i++){const u=i/samples;values.push({x:x0+(x1-x0)*u,v:fn(u)});} const segs=[];let pts=[];
    function flush(){if(pts.length>1){let d=`M${pts[0].x.toFixed(2)} ${base}`;pts.forEach(p=>d+=`L${p.x.toFixed(2)} ${(base-scale*p.v).toFixed(2)}`);d+=`L${pts[pts.length-1].x.toFixed(2)} ${base}Z`;segs.push(d);}pts=[];}
    for(let i=0;i<values.length;i++){const p=values[i],match=positive?p.v>=0:p.v<=0;if(match){if(!pts.length&&i>0){const prev=values[i-1];const a=Math.abs(prev.v)/(Math.abs(prev.v)+Math.abs(p.v));pts.push({x:prev.x+(p.x-prev.x)*a,v:0});}pts.push(p);}else if(pts.length){const prev=values[i-1];const a=Math.abs(prev.v)/(Math.abs(prev.v)+Math.abs(p.v));pts.push({x:prev.x+(p.x-prev.x)*a,v:0});flush();}}
    flush(); return segs;
  }
  function detectorScore(n){const N=6000;let s=0;for(let i=0;i<N;i++){const t=(i+.5)/N;s+=orthSignalFn(t)*Math.sin(TAU*n*t);}return 2*s/N;}
  let scanTimer=0;
  function updateOrth(){
    const n=+$('candidate').value,x0=90,x1=930;
    $('orthSignal').setAttribute('d',linePath(orthSignalFn,x0,x1,105,30,800));
    const basis=t=>Math.sin(TAU*n*t),product=t=>orthSignalFn(t)*basis(t);
    $('orthBasis').setAttribute('d',linePath(basis,x0,x1,230,32,800));$('orthProduct').setAttribute('d',linePath(product,x0,x1,360,26,800));
    const pos=$('productPositive'),neg=$('productNegative');pos.innerHTML='';neg.innerHTML='';
    areaSegments(product,x0,x1,360,26,700,true).forEach(d=>{const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',d);p.setAttribute('fill','#3bbf93');p.setAttribute('opacity','.35');pos.appendChild(p);});
    areaSegments(product,x0,x1,360,26,700,false).forEach(d=>{const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',d);p.setAttribute('fill','#e46f82');p.setAttribute('opacity','.35');neg.appendChild(p);});
    const bars=$('detectorBars');bars.innerHTML='';const scores=[];for(let k=1;k<=8;k++)scores.push(detectorScore(k));
    const base=535,maxH=95,barW=48,gap=48,start=150;
    scores.forEach((score,i)=>{const k=i+1,x=start+i*(barW+gap),h=Math.abs(score)*maxH;
      const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');rect.setAttribute('x',x);rect.setAttribute('y',base-h);rect.setAttribute('width',barW);rect.setAttribute('height',h);rect.setAttribute('rx',6);rect.setAttribute('fill',k===n?'#f4c66a':'#7ba4ff');rect.setAttribute('opacity',k===n?'1':'.72');if(k===n){rect.setAttribute('stroke','#fff');rect.setAttribute('stroke-width','2');}bars.appendChild(rect);
      const txt=document.createElementNS('http://www.w3.org/2000/svg','text');txt.setAttribute('x',x+barW/2);txt.setAttribute('y',558);txt.setAttribute('text-anchor','middle');txt.setAttribute('class','plot-small');txt.textContent=k+' Hz';bars.appendChild(txt);
    });
    const score=scores[n-1];$('candidateOut').textContent=n+' Hz';$('basisLabel').textContent=`sin(2π·${n}t)`;$('orthReadout').textContent=`검출값 ${fmt(score)} · ${Math.abs(score)>.08?n+' Hz 성분이 존재합니다':'거의 0 · 해당 성분이 없습니다'}`;
  }
  $('candidate').addEventListener('input',updateOrth);$('candidateScan').addEventListener('click',()=>{clearInterval(scanTimer);let n=1;$('candidate').value=n;updateOrth();scanTimer=setInterval(()=>{n++;if(n>8){clearInterval(scanTimer);return;}$('candidate').value=n;updateOrth();},650);});updateOrth();

  // 05 · Series to transform
  function updateLimit(){
    const T=+$('virtualPeriod').value, tau=1, boxCenter=500, pxPerSec=640/T, boxW=640;
    $('periodBox').setAttribute('x',boxCenter-boxW/2);$('periodBox').setAttribute('width',boxW);$('periodLeft').setAttribute('x',boxCenter-boxW/2);$('periodRight').setAttribute('x',boxCenter+boxW/2-28);
    const pulseHalf=tau*pxPerSec/2;$('pulsePath').setAttribute('d',`M70 190H${boxCenter-pulseHalf}V95H${boxCenter+pulseHalf}V190H930`);
    const x0=70,x1=930,base=430,amp=110,fMin=-6,fMax=6;
    const fx=u=>fMin+(fMax-fMin)*u;
    $('sincEnvelope').setAttribute('d',linePath(u=>Math.abs(tau*sinc(Math.PI*tau*fx(u))),x0,x1,base,amp,1200));
    const group=$('spectrumLines');group.innerHTML='';const df=1/T,nMin=Math.ceil(fMin/df),nMax=Math.floor(fMax/df);
    for(let n=nMin;n<=nMax;n++){const f=n*df,x=x0+(f-fMin)/(fMax-fMin)*(x1-x0),h=amp*Math.abs(tau*sinc(Math.PI*tau*f));const line=document.createElementNS('http://www.w3.org/2000/svg','line');line.setAttribute('x1',x);line.setAttribute('x2',x);line.setAttribute('y1',base);line.setAttribute('y2',base-h);line.setAttribute('stroke','#7ba4ff');line.setAttribute('stroke-width',Math.max(1.2,Math.min(4,18/T)));line.setAttribute('opacity','.75');group.appendChild(line);}
    $('periodOut').textContent=T.toFixed(2).replace(/\.00$/,'.0')+' s';$('limitReadout').textContent=`Δf = ${(1/T).toFixed(3)} Hz · ${nMax-nMin+1}개의 표본선이 −6~6 Hz 구간을 채웁니다`;
  }
  $('virtualPeriod').addEventListener('input',updateLimit);updateLimit();

  // 06 · Magnitude and phase
  function updatePhase(){
    const deg=+$('phaseSlider').value,phi=deg*Math.PI/180,x0=60,x1=640;
    const fn0=u=>Math.sin(TAU*2*u)+.65*Math.sin(TAU*6*u);
    const fn=u=>Math.sin(TAU*2*u)+.65*Math.sin(TAU*6*u+phi);
    $('phaseReference').setAttribute('d',linePath(fn0,x0,x1,220,55,800));$('phaseWave').setAttribute('d',linePath(fn,x0,x1,220,55,800));
    const cx=865,cy=115,r=48;$('phaseDial').setAttribute('x2',cx+r*Math.cos(phi));$('phaseDial').setAttribute('y2',cy-r*Math.sin(phi));
    $('phaseOut').textContent=(deg<0?'−':'')+Math.abs(deg)+'°';$('phaseDialLabel').textContent=(deg<0?'−':'')+Math.abs(deg)+'°';$('phaseReadout').textContent=`크기: 1 Hz = 1.00, 3 Hz = 0.65 · 위상만 ${(deg<0?'−':'')+Math.abs(deg)}°`;
  }
  $('phaseSlider').addEventListener('input',updatePhase);$('phaseRandom').addEventListener('click',()=>{$('phaseSlider').value=Math.round(Math.random()*360-180);updatePhase();});updatePhase();

  // 07 · Pulse pair
  function updatePulse(){
    const tau=+$('pulseWidth').value,x0=70,x1=930,center=500,timeSpan=4,pxPerSec=(x1-x0)/timeSpan,half=tau*pxPerSec/2,left=center-half,right=center+half;
    $('rectPulse').setAttribute('d',`M${x0} 205H${left}V95H${right}V205H${x1}`);['widthMarkerL','widthMarkerR'].forEach((id,i)=>{const x=i?right:left;$(id).setAttribute('x1',x);$(id).setAttribute('x2',x);});$('widthLabel').setAttribute('x',center-30);$('widthLabel').textContent=`τ = ${tau.toFixed(2)} s`;
    const fMin=-6,fMax=6,base=455,amp=125;$('pulseSpectrum').setAttribute('d',linePath(u=>Math.abs(sinc(Math.PI*tau*(fMin+(fMax-fMin)*u))),x0,x1,base,amp,1400));
    const zero=1/tau;const zxL=x0+(-zero-fMin)/(fMax-fMin)*(x1-x0),zxR=x0+(zero-fMin)/(fMax-fMin)*(x1-x0);
    ['zeroMarkerL','zeroLabelL'].forEach(id=>$(id).setAttribute('x1',zxL));$('zeroMarkerL').setAttribute('x2',zxL);$('zeroLabelL').setAttribute('x',zxL-18);
    $('zeroMarkerR').setAttribute('x1',zxR);$('zeroMarkerR').setAttribute('x2',zxR);$('zeroLabelR').setAttribute('x',zxR-15);
    $('widthOut').textContent=tau.toFixed(2)+' s';$('pulseReadout').textContent=`첫 영점: ±${(1/tau).toFixed(2)} Hz · ${tau<.6?'짧은 펄스이므로 넓은 대역':'폭이 넓어질수록 중심 대역이 좁아집니다'}`;
  }
  $('pulseWidth').addEventListener('input',updatePulse);updatePulse();

  // Stop animations when page is hidden.
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){superRunning=false;eulerRunning=false;cancelAnimationFrame(superRaf);cancelAnimationFrame(eulerRaf);$('superPlay').textContent='▶ 시간 이동';$('eulerPlay').textContent='▶ 회전';}
  });

  document.dispatchEvent(new CustomEvent('knowledge:lab-ready'));
})();
