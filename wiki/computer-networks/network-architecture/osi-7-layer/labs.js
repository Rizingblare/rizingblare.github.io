(() => {
  const NS='http://www.w3.org/2000/svg';
  const $=id=>document.getElementById(id);
  const el=(name,attrs={},value='')=>{const n=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(value)n.textContent=value;return n};
  const clear=svg=>{if(!svg)return;[...svg.children].forEach(node=>{if(!['title','desc'].includes(node.tagName.toLowerCase()))node.remove()})};
  const txt=(svg,x,y,value,cls='plot-muted',anchor='start')=>svg.append(el('text',{x,y,class:cls,'text-anchor':anchor},value));

  function renderEncapsulation(){
    const svg=$('osi-encapsulation-svg');if(!svg)return;
    const direction=$('osi-direction').value;
    const stage=Number($('osi-stage').value);
    const payload=Number($('osi-payload-size').value);
    clear(svg);
    const sendLabels=['응용 데이터','전송 계층','네트워크 계층','데이터 링크 계층','물리 전송'];
    const receiveLabels=[...sendLabels].reverse();
    const logicalStage=direction==='send'?stage:4-stage;
    $('osi-stage-out').textContent=(direction==='send'?sendLabels:receiveLabels)[stage];
    $('osi-payload-size-out').textContent=`${payload} B`;
    const layers=[
      {name:'응용 데이터',short:'DATA',size:payload,color:'#8dabff'},
      {name:'전송 헤더',short:'L4',size:20,color:'#b59aff'},
      {name:'IP 헤더',short:'L3',size:20,color:'#73e0bd'},
      {name:'링크 헤더·트레일러',short:'L2',size:18,color:'#ffb466'}
    ];
    const present=[0];
    if(logicalStage>=1)present.unshift(1);
    if(logicalStage>=2)present.unshift(2);
    if(logicalStage>=3)present.unshift(3);
    const total=present.reduce((s,i)=>s+layers[i].size,0);
    const x0=55,y=118,w=830,h=104;
    let x=x0;
    present.forEach((idx)=>{
      const part=layers[idx];const bw=w*part.size/total;
      svg.append(el('rect',{x,y,width:bw,height:h,rx:idx===present[0]?15:0,fill:part.color,opacity:.92,stroke:'#0f1520','stroke-width':2}));
      // 헤더 블록은 밝은 파스텔 면이므로 라벨은 어두운 잉크로 고정한다.
      // 클래스 CSS가 presentation attribute를 이기므로 style로 덮어쓴다.
      svg.append(el('text',{x:x+bw/2,y:y+44,class:'plot-label','text-anchor':'middle',style:'fill:#101620'},part.short));
      svg.append(el('text',{x:x+bw/2,y:y+70,class:'plot-small','text-anchor':'middle',style:'fill:#101620;font-size:12.5px;font-weight:700'},`${part.size} B`));
      x+=bw;
    });
    const arrowY=295;
    const names=['응용','전송','네트워크','데이터 링크','물리'];
    names.forEach((name,i)=>{
      const bx=72+i*171;
      const active=i===stage;
      svg.append(el('rect',{x:bx,y:arrowY,width:145,height:72,rx:14,fill:active?'#293e70':'#171e2a',stroke:active?'#8dabff':'#354052','stroke-width':active?2.5:1.2}));
      txt(svg,bx+72.5,arrowY+31, direction==='send'?names[i]:names[4-i], 'plot-label','middle');
      txt(svg,bx+72.5,arrowY+53,direction==='send'?(i===0?'생성':i===4?'신호화':'제어 정보 추가'):(i===0?'수신 신호':i===4?'응용 전달':'제어 정보 제거'),'plot-small','middle');
      if(i<4){
        svg.append(el('path',{d:`M${bx+149} ${arrowY+36}H${bx+166}`,stroke:'#8dabff','stroke-width':2,fill:'none'}));
        svg.append(el('path',{d:`M${bx+166} ${arrowY+31}L${bx+174} ${arrowY+36}L${bx+166} ${arrowY+41}Z`,fill:'#8dabff'}));
      }
    });
    txt(svg,55,48,direction==='send'?'송신: 안쪽 데이터에 바깥 제어 정보를 붙입니다':'수신: 바깥 제어 정보를 차례로 해석하고 제거합니다','plot-label');
    txt(svg,885,48,`현재 논리 PDU ${total} B`,'plot-label','end');
    const status=logicalStage===4?'비트/신호로 매체에 전달':logicalStage===3?'링크 프레임 완성':logicalStage===2?'IP 패킷 완성':logicalStage===1?'전송 PDU 완성':'응용 메시지';
    $('osi-encapsulation-readout').textContent=`${status} · 설명용 크기 ${total} B · 응용 데이터 비율 ${(payload/total*100).toFixed(1)}%`;
  }

  const symptoms={
    link:{focus:[1,2],title:'1·2계층부터 확인',tests:['케이블·무선 신호','인터페이스 up/down','스위치 포트·VLAN'],note:'상위 프로토콜 검사 전에 링크 자체가 형성되었는지 확인합니다.'},
    local:{focus:[2,3],title:'2·3계층 경계 확인',tests:['IP/서브넷 설정','ARP·Neighbor 상태','게이트웨이 MAC·VLAN'],note:'같은 링크의 다음 홉에 도달하지 못하므로 링크 전달과 로컬 주소 계산을 함께 봅니다.'},
    route:{focus:[3],title:'3계층 경로 우선',tests:['라우팅 테이블','기본 게이트웨이','경로 추적·ACL'],note:'로컬 다음 홉은 되므로 원격 네트워크까지의 경로와 정책을 좁혀 봅니다.'},
    dns:{focus:[7,4,3],title:'DNS 응용과 하위 전달 확인',tests:['DNS 서버 주소','UDP/TCP 53','질의·응답과 캐시'],note:'IP 접속 성공은 일부 하위 경로의 증거지만 DNS 서버까지의 별도 전달은 확인해야 합니다.'},
    port:{focus:[4,3],title:'4계층 종단 우선',tests:['SYN/SYN-ACK','서버 listen','방화벽·포트 정책'],note:'ICMP 왕복과 특정 TCP 포트는 서로 다른 서비스이므로 연결 설정을 직접 관찰합니다.'},
    tls:{focus:[6,5,7],title:'TLS·표현·세션 범위',tests:['인증서·SNI','버전·암호군','서버 이름·시간'],note:'TCP 연결이 됐다면 암호 협상과 상위 메시지 계약을 조사합니다.'},
    app:{focus:[7],title:'응용 처리 우선',tests:['HTTP 상태·본문','서버 로그','입력·권한·의존 서비스'],note:'전송과 보안 채널이 성립한 뒤 서버가 500을 냈다면 애플리케이션 처리 증거가 핵심입니다.'}
  };
  function renderTrouble(){
    const svg=$('osi-troubleshoot-svg');if(!svg)return;
    const key=$('osi-symptom').value, info=symptoms[key];clear(svg);
    const layers=[['7','응용'],['6','표현'],['5','세션'],['4','전송'],['3','네트워크'],['2','데이터 링크'],['1','물리']];
    layers.forEach((layer,i)=>{
      const y=45+i*59, num=Number(layer[0]), active=info.focus.includes(num);
      svg.append(el('rect',{x:55,y,width:360,height:46,rx:12,fill:active?'#293e70':'#171e2a',stroke:active?'#8dabff':'#354052','stroke-width':active?2.5:1.2}));
      txt(svg,80,y+29,`${layer[0]}계층`,'plot-small');txt(svg,155,y+29,layer[1],'plot-label');
      txt(svg,395,y+29,active?'우선 조사':'증거로 범위 판단','plot-small','end');
    });
    svg.append(el('rect',{x:470,y:48,width:410,height:360,rx:20,fill:'#151b25',stroke:'#354052'}));
    txt(svg,500,88,info.title,'plot-label');
    txt(svg,500,122,'다음 확인 항목','plot-small');
    info.tests.forEach((t,i)=>{
      svg.append(el('circle',{cx:510,cy:160+i*58,r:14,fill:'#243558',stroke:'#8dabff'}));
      txt(svg,510,165+i*58,String(i+1),'plot-small','middle');
      txt(svg,540,166+i*58,t,'plot-label');
    });
    const words=info.note.split(' ');let line='',lines=[];
    words.forEach(word=>{if((line+word).length>31){lines.push(line.trim());line=''}line+=word+' '});if(line)lines.push(line.trim());
    svg.append(el('rect',{x:490,y:328,width:370,height:62,rx:12,fill:'#1f2937',stroke:'#39465a'}));
    lines.slice(0,2).forEach((v,i)=>txt(svg,510,353+i*21,v,'plot-small'));
    $('osi-troubleshoot-readout').textContent=`우선 범위: ${info.focus.sort((a,b)=>b-a).map(x=>`${x}계층`).join(', ')} · 계층 번호는 가설이며 검사 결과로 확정합니다.`;
  }
  $('osi-direction')?.addEventListener('change',renderEncapsulation);
  $('osi-stage')?.addEventListener('input',renderEncapsulation);
  $('osi-payload-size')?.addEventListener('input',renderEncapsulation);
  $('osi-symptom')?.addEventListener('change',renderTrouble);
  renderEncapsulation();renderTrouble();
  document.dispatchEvent(new CustomEvent('knowledge:lab-ready'));
})();
