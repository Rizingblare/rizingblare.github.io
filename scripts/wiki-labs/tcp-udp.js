(() => {
  const NS='http://www.w3.org/2000/svg';const $=id=>document.getElementById(id);
  const el=(name,attrs={},value='')=>{const n=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(value)n.textContent=value;return n};
  const clear=svg=>{if(!svg)return;[...svg.children].forEach(node=>{if(!['title','desc'].includes(node.tagName.toLowerCase()))node.remove()})};
  const txt=(svg,x,y,value,cls='plot-muted',anchor='start')=>svg.append(el('text',{x,y,class:cls,'text-anchor':anchor},value));
  const arrow=(svg,x1,y1,x2,y2,label,color='#8dabff',dashed=false)=>{
    svg.append(el('line',{x1,y1,x2,y2,stroke:color,'stroke-width':2.2,'stroke-dasharray':dashed?'7 6':'none'}));
    const a=Math.atan2(y2-y1,x2-x1),len=9;
    const p1=[x2-len*Math.cos(a-.55),y2-len*Math.sin(a-.55)],p2=[x2-len*Math.cos(a+.55),y2-len*Math.sin(a+.55)];
    svg.append(el('path',{d:`M${x2} ${y2}L${p1[0]} ${p1[1]}L${p2[0]} ${p2[1]}Z`,fill:color}));
    txt(svg,(x1+x2)/2,(y1+y2)/2-8,label,'plot-small','middle');
  };
  function renderReliability(){
    const svg=$('tcp-reliability-svg');if(!svg)return;
    const loss=Number($('tcp-loss-segment').value),size=Number($('tcp-segment-size').value),base=Number($('tcp-base-seq').value);
    $('tcp-segment-size-out').textContent=`${size} B`;$('tcp-base-seq-out').textContent=base.toLocaleString();clear(svg);
    const left=180,right=760,top=74,bottom=570;
    txt(svg,left,42,'송신자','plot-label','middle');txt(svg,right,42,'수신자','plot-label','middle');
    svg.append(el('line',{x1:left,y1:top,x2:left,y2:bottom,stroke:'#556175','stroke-width':2}));
    svg.append(el('line',{x1:right,y1:top,x2:right,y2:bottom,stroke:'#556175','stroke-width':2}));
    const seqs=[base,base+size,base+size*2];let y=115;let expected=base;
    const received=[];
    for(let i=0;i<3;i++){
      const sy=y,ey=y+54;const isLost=loss===i+1;
      arrow(svg,left,sy,right,ey,`DATA seq=${seqs[i]} len=${size}`,isLost?'#ff7f8f':'#8dabff',isLost);
      if(isLost){
        svg.append(el('circle',{cx:(left+right)/2,cy:(sy+ey)/2,r:18,fill:'#4a2428',stroke:'#ff7f8f'}));txt(svg,(left+right)/2,(sy+ey)/2+5,'×','plot-label','middle');
      }else received.push(i);
      if(!isLost && seqs[i]===expected){expected+=size;while(received.includes((expected-base)/size))expected+=size;}
      const ack=expected;
      arrow(svg,right,ey+22,left,ey+64,`ACK ${ack}`,'#73e0bd');
      y+=125;
    }
    if(loss){
      const ry=495,seq=seqs[loss-1];
      arrow(svg,left,ry,right,ry+45,`RETRANSMIT seq=${seq}`,'#ffb466');
      const finalAck=base+3*size;
      arrow(svg,right,ry+67,left,ry+104,`ACK ${finalAck}`,'#73e0bd');
      txt(svg,470,602,`빈 구간 ${seq}~${seq+size-1}가 채워지면 연속 ACK가 ${finalAck}까지 진행`,'plot-muted','middle');
      $('tcp-reliability-readout').textContent=`세그먼트 ${loss} 손실 · 수신자는 빈 구간의 첫 바이트 ${seq}를 ACK로 반복 · 재전송 후 ACK ${finalAck}`;
    }else{
      txt(svg,470,540,'모든 데이터가 연속 도착하여 ACK가 세그먼트마다 진행','plot-muted','middle');
      $('tcp-reliability-readout').textContent=`손실 없음 · 최종 누적 ACK ${base+3*size} · 총 데이터 ${3*size} B`;
    }
  }

  const chunk=(s,n)=>{const out=[];for(let i=0;i<s.length;i+=n)out.push(s.slice(i,i+n));return out};
  function boxes(svg,items,y,label,colors){
    txt(svg,55,y-20,label,'plot-label');let x=55;
    items.forEach((value,i)=>{const w=Math.max(64,value.length*17+26);svg.append(el('rect',{x,y,width:w,height:60,rx:12,fill:colors[i%colors.length],stroke:'#354052'}));txt(svg,x+w/2,y+36,value,'plot-label','middle');x+=w+10});
  }
  function renderBoundary(){
    const svg=$('message-boundary-svg');if(!svg)return;
    const a=$('transport-message-a').value,b=$('transport-message-b').value,n=Number($('tcp-read-size').value);$('tcp-read-size-out').textContent=`${n} B`;clear(svg);
    boxes(svg,[a,b],62,'송신 애플리케이션의 두 번 호출',['#243558','#3a2a58']);
    txt(svg,55,158,'TCP: 두 메시지는 하나의 순서 있는 바이트 스트림이 됩니다','plot-label');
    const chars=(a+b).split('');let x=55;chars.forEach((c,i)=>{svg.append(el('rect',{x,y:182,width:42,height:48,rx:7,fill:i<a.length?'#29436d':'#49356f',stroke:'#5c6d86'}));txt(svg,x+21,213,c,'plot-label','middle');x+=43});
    const reads=chunk(a+b,n);boxes(svg,reads,285,`TCP recv(${n})의 가능한 읽기 경계`,['#173d35','#214b43']);
    boxes(svg,[a,b],405,'UDP: 두 send는 두 데이터그램 경계로 유지',['#4c3524','#4b2d35']);
    txt(svg,885,450,'도착·순서 자체는 보장되지 않음','plot-small','end');
    $('message-boundary-readout').textContent=`TCP 스트림 ${a.length+b.length} B → 읽기 ${reads.length}회 예시 (${reads.join(' | ')}) · UDP 데이터그램 2개 (${a.length} B, ${b.length} B)`;
  }
  $('tcp-loss-segment')?.addEventListener('change',renderReliability);$('tcp-segment-size')?.addEventListener('input',renderReliability);$('tcp-base-seq')?.addEventListener('input',renderReliability);
  $('transport-message-a')?.addEventListener('change',renderBoundary);$('transport-message-b')?.addEventListener('change',renderBoundary);$('tcp-read-size')?.addEventListener('input',renderBoundary);
  renderReliability();renderBoundary();document.dispatchEvent(new CustomEvent('knowledge:lab-ready'));
})();
