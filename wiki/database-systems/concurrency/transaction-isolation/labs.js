(() => {
  const NS='http://www.w3.org/2000/svg';const $=id=>document.getElementById(id);
  const el=(name,attrs={},value='')=>{const n=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(value)n.textContent=value;return n};
  const clear=svg=>{if(!svg)return;[...svg.children].forEach(node=>{if(!['title','desc'].includes(node.tagName.toLowerCase()))node.remove()})};
  const txt=(svg,x,y,value,cls='plot-muted',anchor='start')=>{const n=el('text',{x,y,class:cls,'text-anchor':anchor},value);svg.append(n);return n};
  const ctxt=(svg,x,y,value,color,anchor='start',cls='plot-small')=>{const n=el('text',{x,y,class:cls,'text-anchor':anchor,style:`fill:${color}`},value);svg.append(n);return n};
  const wrap=(value,max=34)=>{const words=value.split(' '),lines=[];let line='';for(const word of words){if((line+word).length>max){lines.push(line.trim());line=''}line+=word+' '}if(line)lines.push(line.trim());return lines};
  const DANGER='#ff7f8f',WARNC='#ffb466',OKC='#73e0bd';
  const BOX={read:['#243558','#8dabff'],changed:['#243558','#ffb466'],write:['#4b3126','#ffb466'],commit:['#183d34','#73e0bd'],bad:['#4a2428','#ff7f8f'],warn:['#4b3126','#ffb466'],abort:['#4a2428','#ff7f8f']};
  const DASHED=new Set(['warn','abort']);
  const addArrow=(svg,id,color)=>{const d=el('defs'),m=el('marker',{id,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto'});m.append(el('path',{d:'M0 0L10 5L0 10z',fill:color}));d.append(m);svg.append(d)};
  const stepBox=(svg,x,y,w,label,type,flash)=>{
    const g=el('g',flash?{class:'lab-flash'}:{});
    const [fill,stroke]=BOX[type]||BOX.read;
    const attrs={x,y,width:w,height:42,rx:10,fill,stroke,'stroke-width':1.4};
    if(DASHED.has(type))attrs['stroke-dasharray']='5 4';
    g.append(el('rect',attrs));
    const lines=Array.isArray(label)?label:[label];
    lines.forEach((v,i)=>g.append(el('text',{x:x+w/2,y:lines.length===1?y+26:y+18+i*15,class:'plot-small','text-anchor':'middle'},v)));
    svg.append(g);return g;
  };
  const st=(s,l,t='read')=>({s,l,t});
  const levelLabel={ru:'Read Uncommitted',rc:'Read Committed',rr:'Repeatable Read',ser:'Serializable'};

  function anomalyConfig(key,level){
    if(key==='dirty'){
      const p=level!=='ru';
      return{title:'더티 리드',initial:'balance = 100 (커밋됨)',slots:7,
        t1:[st(0,'BEGIN'),st(1,['UPDATE','balance=0'],'write'),st(5,'ROLLBACK','commit')],
        t2:[st(2,'BEGIN'),st(3,p?['SELECT','→ 100 (커밋값)']:['SELECT','→ 0 (미커밋)'],p?'read':'bad'),st(4,'알림 판단'),st(6,'COMMIT','commit')],
        verdict:p?'ok':'bad',
        status:p?'해당 수준에서 방지':'이 패턴이 나타날 수 있음',
        final:p?'T1 롤백 후에도 데이터는 계속 100 · T2 판단은 유효':'T1 롤백 → T2는 존재한 적 없는 0을 근거로 알림',
        explain:p?(level==='rc'?'각 문장은 시작 시점에 커밋된 값만 봅니다 — 미커밋 0은 스냅샷 밖입니다.':'트랜잭션 스냅샷이 미커밋 값을 숨겨 SELECT는 커밋된 100을 봅니다.'):'T2가 커밋되지 않은 0을 읽었고, 그 값은 롤백으로 사라졌습니다.',
        band:p?null:{from:1,to:5,label:'미커밋 값이 노출되는 구간'},
        arrow:p?null:{from:['t1',1],to:['t2',1],label:'미커밋 쓰기를 읽음'}};
    }
    if(key==='nonrepeatable'){
      const p=level==='rr'||level==='ser';
      return{title:'반복 불가능 읽기',initial:'price = 10,000 (커밋됨)',slots:7,
        t1:[st(0,'BEGIN'),st(1,['SELECT #1','→ 10,000']),st(5,p?['SELECT #2','→ 10,000 (유지)']:['SELECT #2','→ 12,000'],p?'read':'bad'),st(6,'COMMIT','commit')],
        t2:[st(2,'BEGIN'),st(3,['UPDATE','price=12,000'],'write'),st(4,'COMMIT','commit')],
        verdict:p?'ok':'bad',
        status:p?'해당 수준에서 방지':'이 패턴이 나타날 수 있음',
        final:p?'T1 안에서는 계속 10,000 · 새 트랜잭션부터 12,000':'같은 조회가 10,000 → 12,000으로 달라짐',
        explain:p?'T1은 트랜잭션 스냅샷을 유지해 T2의 커밋을 보지 않습니다.':(level==='ru'?'미커밋 값까지 보이는 수준이므로 커밋된 변경은 당연히 보입니다.':'문장별 스냅샷이 T2의 커밋을 두 번째 SELECT에 반영합니다.'),
        band:p?null:{from:2,to:4,label:'이 사이에 T2가 커밋 — 여기서 값이 바뀜'},
        arrow:p?null:{from:['t2',2],to:['t1',2],label:'커밋된 새 값이 보임'}};
    }
    if(key==='lost'){
      const t1=[st(0,'READ 10'),st(2,'CALC 11'),st(3,'WRITE 11','write'),st(4,'COMMIT','commit')];
      if(level==='ser')return{title:'갱신 분실',initial:'counter = 10 (커밋됨)',slots:8,t1,
        t2:[st(1,'READ 10'),st(5,['ABORT','(직렬화 실패)'],'abort'),st(6,['RETRY','READ 11']),st(7,['WRITE 12','COMMIT'],'commit')],
        verdict:'ok',status:'중단·재시도로 방지',
        final:'최종 counter = 12 · 두 증가 모두 반영',
        explain:'직렬 순서를 만들 수 없어 T2를 중단하고 전체 트랜잭션을 재시도합니다.',
        band:null,arrow:null};
      if(level==='rr')return{title:'갱신 분실',initial:'counter = 10 (커밋됨)',slots:7,t1,
        t2:[st(1,'READ 10'),st(5,['WRITE 11 ?','(충돌 감지?)'],'warn'),st(6,['COMMIT 또는','ABORT / WAIT'],'warn')],
        verdict:'warn',status:'구현·문장에 따라 중단 또는 허용',
        final:'PostgreSQL RR: 갱신 충돌로 중단 · 잠금 기반: 11로 덮일 수 있음',
        explain:'RR의 갱신 충돌 처리(첫 갱신자 승리 등)는 DBMS 문서를 확인해야 합니다.',
        band:null,arrow:null};
      return{title:'갱신 분실',initial:'counter = 10 (커밋됨)',slots:7,t1,
        t2:[st(1,'READ 10'),st(5,['WRITE 11','(10 기준)'],'bad'),st(6,'COMMIT','commit')],
        verdict:'bad',status:'이 패턴이 나타날 수 있음',
        final:'최종 counter = 11 · 증가 1회 분실',
        explain:'T2가 낡은 값 10을 기준으로 계산해 T1의 커밋된 11을 덮어씁니다.',
        band:{from:3,to:5,label:'커밋된 증가가 덮이는 구간'},
        arrow:{from:['t1',2],to:['t2',1],label:'커밋된 11을 덮어씀'}};
    }
    // skew
    const t1=[st(0,'READ B=on'),st(2,['WRITE','A=off'],'write'),st(4,'COMMIT','commit')];
    if(level==='ser')return{title:'쓰기 스큐',initial:'A=on, B=on · 최소 1명 당직',slots:8,t1,
      t2:[st(1,'READ A=on'),st(3,['WRITE','B=off'],'write'),st(5,['ABORT','(직렬화 실패)'],'abort'),st(6,['RETRY','READ A=off']),st(7,['B 유지','COMMIT'],'commit')],
      verdict:'ok',status:'중단·재시도로 방지',
      final:'최종 A=off, B=on · 불변식 유지',
      explain:'위험한 읽기-쓰기 의존성을 감지해 커밋 시점에 T2를 중단합니다.',
      band:null,arrow:null};
    if(level==='rr')return{title:'쓰기 스큐',initial:'A=on, B=on · 최소 1명 당직',slots:6,t1,
      t2:[st(1,'READ A=on'),st(3,['WRITE','B=off'],'warn'),st(5,['COMMIT 또는','ABORT / WAIT'],'warn')],
      verdict:'warn',status:'구현에 따라 허용 또는 차단',
      final:'스냅샷 RR(SI): 허용될 수 있음 · 잠금 기반 RR: 차단 가능',
      explain:'스냅샷 격리는 서로 다른 행 쓰기를 충돌로 보지 않습니다.',
      band:null,arrow:null};
    return{title:'쓰기 스큐',initial:'A=on, B=on · 최소 1명 당직',slots:6,t1,
      t2:[st(1,'READ A=on'),st(3,['WRITE','B=off'],'bad'),st(5,'COMMIT','commit')],
      verdict:'bad',status:'이 패턴이 나타날 수 있음',
      final:'최종 A=off, B=off · “최소 1명” 불변식 위반',
      explain:'행 단위 충돌 없이 각자 낡은 전제로 서로 다른 행을 바꿉니다.',
      band:{from:2,to:5,label:'서로 다른 행을 써 함께 커밋되는 구간'},
      arrow:{from:['t1',1],to:['t2',2],label:'T2의 전제 A=on은 이미 무효'}};
  }

  let prevA={};
  function renderAnomaly(){
    const svg=$('isolation-anomaly-svg');if(!svg)return;
    const key=$('isolation-anomaly').value,level=$('isolation-level').value;
    const c=anomalyConfig(key,level);clear(svg);
    addArrow(svg,'iso-causal-arrow',DANGER);
    const x0=110,x1=890,slotW=(x1-x0)/c.slots,bw=slotW-14;
    const y1=150,y2=268;
    txt(svg,55,43,`${c.title} × ${levelLabel[level]}`,'plot-label');
    svg.append(el('rect',{x:55,y:60,width:830,height:46,rx:12,fill:'#151b25',stroke:'#354052'}));
    txt(svg,75,89,`초기 상태 · ${c.initial}`,'plot-label');
    if(c.band){
      const bx=x0+c.band.from*slotW,bwd=(c.band.to-c.band.from+1)*slotW;
      svg.append(el('rect',{x:bx,y:126,width:bwd,height:210,rx:10,fill:DANGER,'fill-opacity':0.12}));
      ctxt(svg,Math.min(bx+8,560),120,c.band.label,'#ff9aa8');
    }
    txt(svg,55,y1+26,'T1','plot-label');txt(svg,55,y2+26,'T2','plot-label');
    svg.append(el('line',{x1:x0-5,y1:y1+21,x2:x1,y2:y1+21,stroke:'#495568'}));
    svg.append(el('line',{x1:x0-5,y1:y2+21,x2:x1,y2:y2+21,stroke:'#495568'}));
    const next={};
    const place=(steps,row,y)=>steps.map((s,i)=>{
      const x=x0+s.s*slotW+7;
      const sig=`${s.s}|${Array.isArray(s.l)?s.l.join('¦'):s.l}|${s.t}`;
      const k=`${row}-${i}`;next[k]=sig;
      const flash=!!prevA.__init&&prevA[k]!==sig;
      return{g:stepBox(svg,x,y,bw,s.l,s.t,flash),x,y,w:bw};
    });
    const b1=place(c.t1,'t1',y1),b2=place(c.t2,'t2',y2);
    if(c.arrow){
      const F=(c.arrow.from[0]==='t1'?b1:b2)[c.arrow.from[1]];
      const T=(c.arrow.to[0]==='t1'?b1:b2)[c.arrow.to[1]];
      const sy=F.y<T.y?F.y+42:F.y,tyRaw=T.y<F.y?T.y+42:T.y;
      const ty=tyRaw>sy?tyRaw-6:tyRaw+6;
      const sx=F.x+F.w/2,tx=T.x+T.w/2,my=(sy+ty)/2;
      svg.append(el('path',{d:`M${sx} ${sy}C${sx} ${my},${tx} ${my},${tx} ${ty}`,fill:'none',stroke:DANGER,'stroke-width':1.8,'marker-end':'url(#iso-causal-arrow)'}));
      ctxt(svg,(sx+tx)/2,my+4,c.arrow.label,'#ff9aa8','middle');
    }
    const vc=c.verdict==='bad'?DANGER:c.verdict==='warn'?WARNC:OKC;
    const vk=`${c.status}|${c.final}|${c.explain}`;next.__v=vk;
    const vg=el('g',prevA.__init&&prevA.__v!==vk?{class:'lab-flash'}:{});
    vg.append(el('rect',{x:55,y:428,width:830,height:112,rx:16,fill:'#151b25',stroke:vc,'stroke-width':2}));
    vg.append(el('text',{x:78,y:460,class:'plot-label',style:`fill:${vc}`},c.status));
    vg.append(el('text',{x:78,y:486,class:'plot-label'},c.final));
    wrap(c.explain,60).slice(0,2).forEach((v,i)=>vg.append(el('text',{x:78,y:510+i*19,class:'plot-small'},v)));
    svg.append(vg);
    prevA=Object.assign({__init:true},next);
    $('isolation-anomaly-readout').textContent=`${c.title} × ${levelLabel[level]} — ${c.status} · ${c.final}`;
  }

  let prevS={};
  function renderSnapshot(){
    const svg=$('snapshot-svg');if(!svg)return;
    const level=$('snapshot-level').value,nv=Number($('snapshot-update').value);
    $('snapshot-update-out').textContent=String(nv);clear(svg);
    const rc=level==='rc';
    addArrow(svg,'snap-causal-arrow',DANGER);
    addArrow(svg,'snap-note-arrow',WARNC);
    const x0=110,x1=890,slots=7,slotW=(x1-x0)/slots,bw=slotW-14;
    const y1=92,y2=182;
    txt(svg,55,40,rc?'Read Committed · 문장별 스냅샷':'Repeatable Read · 트랜잭션 스냅샷','plot-label');
    if(rc){
      const bx=x0+2*slotW,bwd=3*slotW;
      svg.append(el('rect',{x:bx,y:68,width:bwd,height:178,rx:10,fill:DANGER,'fill-opacity':0.12}));
      ctxt(svg,bx+bwd/2,60,'이 사이에 T2가 커밋 — 여기서 값이 바뀜','#ff9aa8','middle');
    }
    txt(svg,55,y1+26,'T1','plot-label');txt(svg,55,y2+26,'T2','plot-label');
    svg.append(el('line',{x1:x0-5,y1:y1+21,x2:x1,y2:y1+21,stroke:'#4e5b70'}));
    svg.append(el('line',{x1:x0-5,y1:y2+21,x2:x1,y2:y2+21,stroke:'#4e5b70'}));
    const t1s=[st(0,'BEGIN'),st(1,['SELECT #1','→ 100']),st(5,rc?['SELECT #2',`→ ${nv}`]:['SELECT #2','→ 100 (유지)'],rc?'changed':'read'),st(6,'COMMIT','commit')];
    const t2s=[st(2,'BEGIN'),st(3,['UPDATE',`→ ${nv}`],'write'),st(4,'COMMIT','commit')];
    const next={};
    const place=(steps,row,y)=>steps.map((s,i)=>{
      const x=x0+s.s*slotW+7;
      const sig=`${s.s}|${Array.isArray(s.l)?s.l.join('¦'):s.l}|${s.t}`;
      const k=`${row}-${i}`;next[k]=sig;
      const flash=!!prevS.__init&&prevS[k]!==sig;
      return{g:stepBox(svg,x,y,bw,s.l,s.t,flash),x,y,w:bw};
    });
    const b1=place(t1s,'t1',y1),b2=place(t2s,'t2',y2);
    if(rc){
      const F=b2[2],T=b1[2];
      const sx=F.x+F.w/2,tx=T.x+T.w/2;
      svg.append(el('path',{d:`M${sx} ${F.y}C${sx} ${(F.y+T.y+42)/2},${tx} ${(F.y+T.y+42)/2},${tx} ${T.y+48}`,fill:'none',stroke:DANGER,'stroke-width':1.8,'marker-end':'url(#snap-causal-arrow)'}));
    }
    txt(svg,55,304,'행 버전과 가시성','plot-label');
    const vbox=(x,value,from,dim,flashKey)=>{
      const sig=`${value}|${from}|${dim?1:0}`;next[flashKey]=sig;
      const g=el('g',(prevS.__init&&prevS[flashKey]!==sig?{class:'lab-flash '}:{}));
      if(dim)g.setAttribute('opacity','0.35');
      const attrs={x,y:316,width:250,height:60,rx:14,fill:dim?'#173d35':(flashKey==='v1'?'#243558':'#173d35'),stroke:flashKey==='v1'?'#8dabff':'#73e0bd','stroke-width':1.4};
      if(dim)attrs['stroke-dasharray']='6 5';
      g.append(el('rect',attrs));
      g.append(el('text',{x:x+125,y:342,class:'plot-label','text-anchor':'middle'},`value = ${value}`));
      g.append(el('text',{x:x+125,y:364,class:'plot-small','text-anchor':'middle'},from));
      svg.append(g);return g;
    };
    vbox(155,'100','초기 커밋',false,'v1');
    vbox(500,String(nv),'T2 커밋',!rc,'v2');
    if(!rc){
      const bsig='badge';next.badge=bsig;
      const bg=el('g',prevS.__init&&prevS.badge!==bsig?{class:'lab-flash'}:{});
      bg.append(el('rect',{x:615,y:302,width:150,height:26,rx:9,fill:'#4a2428',stroke:DANGER,'stroke-width':1.2}));
      bg.append(el('text',{x:690,y:319,class:'plot-small','text-anchor':'middle',style:`fill:#ff9aa8`},'T1에게 보이지 않음'));
      svg.append(bg);
    }
    const selX=b1[2].x+b1[2].w/2;
    const targetX=rc?625:280;
    svg.append(el('path',{d:`M${selX} ${y1+42}V252H${targetX}V310`,fill:'none',stroke:WARNC,'stroke-width':1.6,'stroke-dasharray':'4 4','marker-end':'url(#snap-note-arrow)'}));
    const result=rc?`두 번째 SELECT는 T2가 커밋한 ${nv}을 봄`:'T1은 처음 스냅샷의 100을 계속 봄';
    const rk=`${result}`;next.note=rk;
    const rt=el('text',{x:selX-10,y:272,class:'plot-small','text-anchor':'end',style:`fill:${WARNC}`},result);
    if(prevS.__init&&prevS.note!==rk)rt.setAttribute('class','plot-small lab-flash');
    svg.append(rt);
    prevS=Object.assign({__init:true},next);
    $('snapshot-readout').textContent=`초기 100 · T2가 ${nv} 커밋 · ${levelLabel[level]} · ${result}`;
  }
  $('isolation-anomaly')?.addEventListener('change',renderAnomaly);$('isolation-level')?.addEventListener('change',renderAnomaly);$('snapshot-level')?.addEventListener('change',renderSnapshot);$('snapshot-update')?.addEventListener('input',renderSnapshot);
  renderAnomaly();renderSnapshot();document.dispatchEvent(new CustomEvent('knowledge:lab-ready'));
})();
