(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const $ = (id) => document.getElementById(id);
  const el = (name, attrs = {}, text = '') => {
    const node = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, String(v)));
    if (text) node.textContent = text;
    return node;
  };
  const clear = (svg) => { if (!svg) return; [...svg.children].forEach(node => { if (!['title','desc'].includes(node.tagName.toLowerCase())) node.remove(); }); };
  const pathFrom = (points) => points.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(2)} ${p[1].toFixed(2)}`).join(' ');
  const text = (svg, x, y, value, cls = 'plot-muted', anchor = 'start') => svg.append(el('text', { x, y, class: cls, 'text-anchor': anchor }, value));
  const line = (svg, x1, y1, x2, y2, cls = 'plot-grid', extra = {}) => svg.append(el('line', { x1, y1, x2, y2, class: cls, ...extra }));
  const grid = (svg, x, y, w, h, cols = 10, rows = 4) => {
    for (let i = 0; i <= cols; i++) line(svg, x + w * i / cols, y, x + w * i / cols, y + h);
    for (let i = 0; i <= rows; i++) line(svg, x, y + h * i / rows, x + w, y + h * i / rows);
    line(svg, x, y + h / 2, x + w, y + h / 2, 'plot-axis');
  };
  const addLegend = (svg, items, y = 22) => {
    let x = 36;
    items.forEach(([label, color]) => {
      svg.append(el('line', { x1:x, y1:y, x2:x+24, y2:y, stroke:color, 'stroke-width':3, 'stroke-linecap':'round' }));
      text(svg, x+31, y+4, label, 'plot-small');
      x += 31 + label.length * 10 + 24;
    });
  };

  function renderSampling() {
    const svg = $('pcm-sampling-svg'); if (!svg) return;
    const f = Number($('pcm-signal-frequency').value);
    const fs = Number($('pcm-sample-rate').value);
    $('pcm-signal-frequency-out').textContent = `${Number.isInteger(f) ? f.toFixed(0) : f.toFixed(1)} Hz`;
    $('pcm-sample-rate-out').textContent = `${fs} Hz`;
    clear(svg);
    const x0=55, y0=55, w=820, h=285, mid=y0+h/2, amp=105, duration=1;
    grid(svg,x0,y0,w,h,10,6);
    addLegend(svg,[['원래 연속 신호','#8dabff'],['표본점','#73e0bd'],['표본열과 같은 저주파 후보','#ff9d73']]);
    const orig=[];
    for(let i=0;i<=900;i++){
      const t=duration*i/900;
      orig.push([x0+w*t/duration,mid-amp*Math.sin(2*Math.PI*f*t)]);
    }
    svg.append(el('path',{d:pathFrom(orig),class:'wave-path',stroke:'#8dabff','stroke-width':3}));
    const count=Math.floor(fs*duration)+1;
    const samples=[];
    for(let n=0;n<count;n++){
      const t=n/fs, val=Math.sin(2*Math.PI*f*t), x=x0+w*t, y=mid-amp*val;
      samples.push([x,y]);
      line(svg,x,mid,x,y,'plot-axis',{stroke:'#466f66','stroke-width':1.2});
      svg.append(el('circle',{cx:x,cy:y,r:5.2,fill:'#73e0bd',stroke:'#0d1817','stroke-width':2}));
    }
    const alias=Math.abs((((f+fs/2)%fs)+fs)%fs-fs/2);
    const aliasPts=[];
    for(let i=0;i<=900;i++){
      const t=duration*i/900;
      aliasPts.push([x0+w*t,mid-amp*Math.sin(2*Math.PI*alias*t)]);
    }
    if(alias!==f || fs<=2*f) svg.append(el('path',{d:pathFrom(aliasPts),class:'wave-path',stroke:'#ff9d73','stroke-width':2.2,'stroke-dasharray':'8 7',opacity:.95}));
    text(svg,x0,y0+h+30,'시간 (1초)', 'plot-muted');
    text(svg,x0+w,y0+h+30,`표본 ${count}개`, 'plot-muted','end');
    const safe=fs>2*f;
    $('pcm-alias-readout').textContent = safe
      ? `fₛ=${fs} Hz > 2f=${2*f} Hz · 조건 충족 · 기본 대역 관찰값 ${alias.toFixed(1)} Hz`
      : `fₛ=${fs} Hz ≤ 2f=${2*f} Hz · 에일리어싱 가능 · ${f} Hz가 ${alias.toFixed(1)} Hz처럼 보임`;
    const badge=el('g');
    badge.append(el('rect',{x:24,y:34,width:220,height:38,rx:10,fill:safe?'#123c32':'#4a2428',stroke:safe?'#3aa889':'#cf6674'}));
    badge.append(el('text',{x:134,y:59,'text-anchor':'middle',fill:'#f5f7fb','font-size':13,'font-weight':800},safe?'표본화 조건 충족':'에일리어싱 영역'));
    svg.append(badge);
  }

  function renderQuantization() {
    const svg=$('pcm-quant-svg'); if(!svg)return;
    const bits=Number($('pcm-bit-depth').value);
    const signalAmplitude=Number($('pcm-amplitude').value);
    $('pcm-bit-depth-out').textContent=`${bits} bit · ${2**bits} levels`;
    $('pcm-amplitude-out').textContent=signalAmplitude.toFixed(2);
    clear(svg);
    const levels=2**bits, min=-1,max=1,delta=(max-min)/levels;
    const x0=55,w=820,top=50,h=210,mid=top+h/2,amp=h*.43;
    grid(svg,x0,top,w,h,12,8);
    addLegend(svg,[['원래 표본값','#8dabff'],['양자화 출력','#ffb466'],['오차','#73e0bd']],24);
    const original=[], quant=[], err=[];
    const quantize=(v)=>{
      const idx=Math.min(levels-1,Math.max(0,Math.floor((v-min)/delta)));
      return min+(idx+.5)*delta;
    };
    for(let i=0;i<=600;i++){
      const t=i/600;
      const v=signalAmplitude*(.9*Math.sin(2*Math.PI*(1.6*t+.08))+.1*Math.sin(2*Math.PI*5*t));
      const q=quantize(v);
      original.push([x0+w*t,mid-amp*v]);
      quant.push([x0+w*t,mid-amp*q]);
      err.push([x0+w*t,355-72*(q-v)/(delta/2)]);
    }
    svg.append(el('path',{d:pathFrom(original),class:'wave-path',stroke:'#8dabff','stroke-width':2.5}));
    svg.append(el('path',{d:pathFrom(quant),class:'wave-path',stroke:'#ffb466','stroke-width':2.2}));
    line(svg,x0,355,x0+w,355,'plot-axis');
    line(svg,x0,300,x0+w,300,'plot-grid'); line(svg,x0,410,x0+w,410,'plot-grid');
    svg.append(el('path',{d:pathFrom(err),class:'wave-path',stroke:'#73e0bd','stroke-width':2}));
    text(svg,x0,286,'양자화 오차 e[n] = Q(x[n]) − x[n]','plot-label');
    text(svg,x0+w,286,`오차 범위 ≈ ±${(delta/2).toFixed(4)}`,'plot-muted','end');
    $('pcm-quant-readout').textContent=`${bits}비트 → ${levels.toLocaleString()}개 코드 · Δ≈${delta.toFixed(4)} · 반올림 오차 최대 약 ${(delta/2).toFixed(4)}`;
  }

  function renderPipeline() {
    const svg=$('pcm-pipeline-svg'); if(!svg)return;
    const fs=Number($('pcm-rate-select').value), bits=Number($('pcm-bits-select').value), channels=Number($('pcm-channel-select').value), duration=Number($('pcm-duration').value);
    $('pcm-duration-out').textContent=`${duration} s`;
    clear(svg);
    const rate=fs*bits*channels, bytes=rate*duration/8;
    const blocks=[
      ['아날로그 입력','x(t)','연속 시간·크기'],['표본화',`${(fs/1000).toFixed(fs%1000?1:0)} kHz`,'시간을 번호로'],['양자화',`${bits} bit` ,`${2**Math.min(bits,20)}${bits>20?'+':''} 레벨`],['부호화','0과 1','표본마다 코드'],['PCM 비트열',`${(rate/1000).toFixed(1)} kbit/s`,`${channels}채널`]
    ];
    blocks.forEach((b,i)=>{
      const x=25+i*178,y=88,w=150,h=132;
      svg.append(el('rect',{x,y,width:w,height:h,rx:16,fill:i===4?'#243558':'#171e2a',stroke:i===4?'#8dabff':'#354052','stroke-width':1.5}));
      text(svg,x+w/2,y+35,b[0],'plot-label','middle'); text(svg,x+w/2,y+70,b[1],'plot-label','middle'); text(svg,x+w/2,y+101,b[2],'plot-small','middle');
      if(i<blocks.length-1){line(svg,x+w+5,y+66,x+w+23,y+66,'plot-axis',{stroke:'#8dabff','stroke-width':2});svg.append(el('path',{d:`M${x+w+23} ${y+61}L${x+w+31} ${y+66}L${x+w+23} ${y+71}Z`,fill:'#8dabff'}));}
    });
    const sampleVals=[.75,.25,-.5,-.8,.1,.6], maxCode=2**Math.min(bits,16)-1;
    const codes=sampleVals.map(v=>Math.round((v+1)/2*maxCode).toString(2).padStart(Math.min(bits,16),'0'));
    svg.append(el('rect',{x:55,y:260,width:810,height:98,rx:14,fill:'#0f141d',stroke:'#2f3948'}));
    text(svg,75,287,'예시 표본 코드','plot-small');
    const shown=codes.slice(0,4).map(c=>{
      if(bits<=8)return c;
      return `${c.slice(0,8)}…`;
    }).join('  ·  ');
    text(svg,75,326,shown,'plot-label');
    text(svg,75,347,`앞 4개 표본 · 각 코드 ${bits}비트`, 'plot-small');
    text(svg,865,287,`${duration}초 데이터`, 'plot-small','end');
    const decimalMB=bytes/1e6, mib=bytes/1048576;
    text(svg,865,326,`${decimalMB.toFixed(decimalMB<10?3:2)} MB`,'plot-label','end');
    text(svg,865,347,`${mib.toFixed(mib<10?3:2)} MiB`,'plot-small','end');
    $('pcm-bitrate-readout').textContent=`R=${fs.toLocaleString()}×${bits}×${channels}=${rate.toLocaleString()} bit/s · ${duration}초 = ${bytes.toLocaleString()} byte`;
  }

  [['pcm-signal-frequency','input',renderSampling],['pcm-sample-rate','input',renderSampling],['pcm-bit-depth','input',renderQuantization],['pcm-amplitude','input',renderQuantization],['pcm-rate-select','change',renderPipeline],['pcm-bits-select','change',renderPipeline],['pcm-channel-select','change',renderPipeline],['pcm-duration','input',renderPipeline]].forEach(([id,event,fn])=>$(id)?.addEventListener(event,fn));
  renderSampling(); renderQuantization(); renderPipeline();
  document.dispatchEvent(new CustomEvent('knowledge:lab-ready'));
})();
