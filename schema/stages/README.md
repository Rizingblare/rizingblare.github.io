# 휘발성 작업 공간 — OPTIONAL

작업 단위가 한 세션 안에 들어오면 이 계층 전체를 생략한다. 이 계층이
없어도 하네스는 완전하다. 증거 사슬만으로도 전체 workflow를 수행하며,
이 계층은 미결 설계 질문과 실행 가능한 task가 뒤섞인 채 여러 세션에
걸쳐 이어지는 작업 단위라는 한 가지 작업 형태를 위한 관리 최적화다.

이 보충성 원칙은 의도적으로 명시했다. 이 계층이 없을 때 system이 어떻게
작동하는지를 밝히지 않은 선택적 계층은 다음 독자에게 필수 계층으로
취급되기 때문이다.

대규모 작업 단위마다 작업 공간 하나를 두고 그 안에 다음을 보관한다. 목표와
재개 절차를 담은 manifest, 반출 원장, 미결 질문마다 파일 하나, 확정된
결정마다 그 근거를 원문 그대로 담은 파일 하나, 작업 항목마다 파일 하나,
그리고 draft다.

다음 세 가지 규칙이 핵심을 이룬다.

**상태 정본은 파일 위치와 frontmatter의 조합이며, 이를 manifest에 중복
기재하지 않는다.** 작업 공간을 *떠나는* 항목만 ledger row를 갖는다. 작업
공간에 남아 있는 항목은 디렉터리 자체로 추적한다.

**local id는 global event sequence와 구조적으로 분리하며**, 영구 참조가
될 수 없다. 승격할 때 작업 공간의 결정은 전역에서 발급한 번호를 가진 실제
event로 *다시 생성*하며, 기존 결정의 이름만 바꾸어 event로 만들지 않는다.
이 규칙이 방지하는 실패는 실제로 관찰되었다. local id가 영구 문서로
유출되어 작업 공간이 존재하는 동안에는 올바르게 해석되었지만, 애초에
존재하지 않도록 설계된 작업 공간이 삭제되는 순간 dangling reference가
되었다.

**이 charter를 제외하면 이 디렉터리의 top level에는 어떤 파일도 두지
않는다.** Bootstrap 계획은 `bootstrap/` 아래에 두고, 작업 단위의 작업
공간은 자체 하위 디렉터리를 사용한다. 선언되지 않은 경로를 쓰는 관행이
스스로 재생산되는 것을 이렇게 막는다.

닫을 때는 고정 mapping을 따른다. contract에 영향을 주는 결정은 영구
event가 되고, 미해결 질문은 queue item이 되며, 채택한 설계는 canonical
home으로 옮긴다. 실행 추적 정보는 closing receipt에 요약하되 승격하지
않는다. close gate는 local id에서 승격 위치로 이어지는 map을 만들고,
**현재 사용 중인 규범 문서에 남은 참조가 0개**일 것을 요구한다. 이 검사는
작업 공간만이 아니라 저장소 전체를 scan한다.

## English brief

This optional volatile-workspace layer supports multi-session units that mix unresolved design questions with executable tasks; the evidence chain remains complete without it. State lives in file location and frontmatter, local ids must be regenerated as globally numbered events on promotion, and only departing items enter the ledger. Bootstrap plans belong under `bootstrap/`, unit workspaces use their own subdirectories, and closure scans the entire repository for zero remaining live normative references.
