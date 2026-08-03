(() => {
  const NS='http://www.w3.org/2000/svg';const $=id=>document.getElementById(id);
  const el=(name,attrs={},value='')=>{const n=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(value)n.textContent=value;return n};
  const clear=svg=>{if(!svg)return;[...svg.children].forEach(node=>{if(!['title','desc'].includes(node.tagName.toLowerCase()))node.remove()})};
  const txt=(svg,x,y,value,cls='plot-muted',anchor='start')=>svg.append(el('text',{x,y,class:cls,'text-anchor':anchor},value));
  const wrap=(value,max=34)=>{const words=value.split(' '),lines=[];let line='';for(const word of words){if((line+word).length>max){lines.push(line.trim());line=''}line+=word+' '}if(line)lines.push(line.trim());return lines};
  const scenario={
    dirty:{title:'더티 리드',initial:'balance = 100',t1:['BEGIN','UPDATE balance=0','ROLLBACK'],t2:['BEGIN','SELECT balance → ?','알림 판단','COMMIT'],bad:'T2가 미커밋 0을 보고 행동',allowed:{ru:true,rc:false,rr:false,ser:false}},
    nonrepeatable:{title:'반복 불가능 읽기',initial:'price = 10,000',t1:['BEGIN','SELECT → 10,000','SELECT → ?','COMMIT'],t2:['BEGIN','UPDATE price=12,000','COMMIT'],bad:'T1의 같은 조회가 10,000 → 12,000',allowed:{ru:true,rc:true,rr:false,ser:false}},
    lost:{title:'갱신 분실',initial:'counter = 10',t1:['READ 10','CALC 11','WRITE 11','COMMIT'],t2:['READ 10','CALC 11','WRITE 11','COMMIT'],bad:'두 증가 중 하나가 사라져 최종 11',allowed:{ru:true,rc:true,rr:'depends',ser:false}},
    skew:{title:'쓰기 스큐',initial:'A=on, B=on; 최소 1명',t1:['READ B=on','WRITE A=off','COMMIT'],t2:['READ A=on','WRITE B=off','COMMIT'],bad:'서로 다른 행을 써 최종 A=off,B=off',allowed:{ru:true,rc:true,rr:'depends',ser:false}}
  };
  const levelLabel={ru:'Read Uncommitted',rc:'Read Committed',rr:'Repeatable Read',ser:'Serializable'};
  function event(svg,x,y,w,label,type='read'){
    const fill=type==='write'?'#4b3126':type==='commit'?'#183d34':type==='bad'?'#4a2428':'#243558';
    const stroke=type==='write'?'#ffb466':type==='commit'?'#73e0bd':type==='bad'?'#ff7f8f':'#8dabff';
    svg.append(el('rect',{x,y,width:w,height:42,rx:10,fill,stroke,'stroke-width':1.4}));txt(svg,x+w/2,y+26,label,'plot-small','middle');
  }
  function renderAnomaly(){
    const svg=$('isolation-anomaly-svg');if(!svg)return;const key=$('isolation-anomaly').value,level=$('isolation-level').value,s=scenario[key];clear(svg);
    txt(svg,55,43,s.title,'plot-label');txt(svg,885,43,levelLabel[level],'plot-label','end');
    svg.append(el('rect',{x:55,y:62,width:830,height:50,rx:12,fill:'#151b25',stroke:'#354052'}));txt(svg,75,93,`초기 상태 · ${s.initial}`,'plot-label');
    const y1=170,y2=310;txt(svg,55,y1+26,'T1','plot-label');txt(svg,55,y2+26,'T2','plot-label');
    svg.append(el('line',{x1:105,y1:y1+22,x2:880,y2:y1+22,stroke:'#495568'}));svg.append(el('line',{x1:105,y1:y2+22,x2:880,y2:y2+22,stroke:'#495568'}));
    const max=Math.max(s.t1.length,s.t2.length),gap=720/max;
    s.t1.forEach((v,i)=>event(svg,125+i*gap,y1,gap-18,v,/WRITE|UPDATE/.test(v)?'write':/COMMIT|ROLLBACK/.test(v)?'commit':'read'));
    s.t2.forEach((v,i)=>event(svg,125+i*gap+(i%2?gap*.12:0),y2,gap-18,v,/WRITE|UPDATE/.test(v)?'write':/COMMIT/.test(v)?'commit':'read'));
    const allow=s.allowed[level];let status,color,explain;
    if(allow===true){status='이 패턴이 나타날 수 있음';color='#ff7f8f';explain=s.bad;}
    else if(allow==='depends'){status='구현·문장에 따라 충돌 또는 허용';color='#ffb466';explain='Repeatable Read의 정확한 쓰기 충돌·스냅샷 보장은 DBMS 문서를 확인해야 합니다.';}
    else{status='해당 수준의 보장 또는 중단으로 방지';color='#73e0bd';explain=level==='ser'?'직렬 순서를 만들 수 없으면 하나를 중단하고 전체 트랜잭션을 재시도합니다.':'미커밋·변경 가시성 규칙이 이 읽기 이상을 차단합니다.';}
    svg.append(el('rect',{x:55,y:435,width:830,height:86,rx:16,fill:'#151b25',stroke:color,'stroke-width':2}));
    txt(svg,78,468,status,'plot-label');wrap(explain,58).slice(0,2).forEach((v,i)=>txt(svg,78,494+i*20,v,'plot-small'));
    $('isolation-anomaly-readout').textContent=`${s.title} · ${levelLabel[level]} · ${status}`;
  }

  function renderSnapshot(){
    const svg=$('snapshot-svg');if(!svg)return;const level=$('snapshot-level').value,next=Number($('snapshot-update').value);$('snapshot-update-out').textContent=String(next);clear(svg);
    txt(svg,55,40,level==='rc'?'Read Committed · 문장별 스냅샷':'Repeatable Read · 트랜잭션 스냅샷','plot-label');
    const y1=92,y2=245;txt(svg,55,y1+28,'T1','plot-label');txt(svg,55,y2+28,'T2','plot-label');
    const events1=[['BEGIN',115],['SELECT #1 → 100',235],['SELECT #2 → '+(level==='rc'?next:100),620],['COMMIT',790]];
    const events2=[['BEGIN',300],['UPDATE → '+next,420],['COMMIT',535]];
    for(const [v,x] of events1)event(svg,x,y1,145,v,/COMMIT/.test(v)?'commit':'read');
    for(const [v,x] of events2)event(svg,x,y2,135,v,/UPDATE/.test(v)?'write':/COMMIT/.test(v)?'commit':'read');
    svg.append(el('line',{x1:105,y1:y1+21,x2:895,y2:y1+21,stroke:'#4e5b70'}));svg.append(el('line',{x1:105,y1:y2+21,x2:895,y2:y2+21,stroke:'#4e5b70'}));
    const versions=[{v:100,x:155,from:'초기 커밋'},{v:next,x:500,from:'T2 커밋'}];
    txt(svg,55,375,'행 버전과 가시성','plot-label');
    versions.forEach((o,i)=>{svg.append(el('rect',{x:o.x,y:400,width:250,height:65,rx:14,fill:i?'#173d35':'#243558',stroke:i?'#73e0bd':'#8dabff'}));txt(svg,o.x+125,428,`value = ${o.v}`,'plot-label','middle');txt(svg,o.x+125,451,o.from,'plot-small','middle')});
    const result=level==='rc'?`두 번째 SELECT는 T2가 커밋한 ${next}을 볼 수 있음`:`T1은 처음 스냅샷의 100을 계속 봄`;
    svg.append(el('path',{d:`M${level==='rc'?625:280} 393L${level==='rc'?625:280} 365`,stroke:'#ffb466','stroke-width':2}));
    txt(svg,885,375,result,'plot-muted','end');
    $('snapshot-readout').textContent=`초기 100 · T2가 ${next} 커밋 · ${result}`;
  }
  $('isolation-anomaly')?.addEventListener('change',renderAnomaly);$('isolation-level')?.addEventListener('change',renderAnomaly);$('snapshot-level')?.addEventListener('change',renderSnapshot);$('snapshot-update')?.addEventListener('input',renderSnapshot);
  renderAnomaly();renderSnapshot();document.dispatchEvent(new CustomEvent('knowledge:lab-ready'));
})();
